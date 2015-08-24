#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy
import datetime
import json
import uuid

from oslo_utils import timeutils
import six
from six.moves.urllib import parse

from heat.common import exception
from heat.common import identifier
from heat.common import template_format
from heat.engine import environment
from heat.engine.resources.aws.cfn import wait_condition_handle as aws_wch
from heat.engine import rsrc_defn
from heat.engine import scheduler
from heat.engine import stack as parser
from heat.engine import template as tmpl
from heat.objects import resource as resource_objects
from heat.tests import common
from heat.tests import utils

test_template_waitcondition = '''
{
  "AWSTemplateFormatVersion" : "2010-09-09",
  "Description" : "Just a WaitCondition.",
  "Parameters" : {},
  "Resources" : {
    "WaitHandle" : {
      "Type" : "AWS::CloudFormation::WaitConditionHandle"
    },
    "WaitForTheHandle" : {
      "Type" : "AWS::CloudFormation::WaitCondition",
      "Properties" : {
        "Handle" : {"Ref" : "WaitHandle"},
        "Timeout" : "5"
      }
    }
  }
}
'''

test_template_wc_count = '''
{
  "AWSTemplateFormatVersion" : "2010-09-09",
  "Description" : "Just a WaitCondition.",
  "Parameters" : {},
  "Resources" : {
    "WaitHandle" : {
      "Type" : "AWS::CloudFormation::WaitConditionHandle"
    },
    "WaitForTheHandle" : {
      "Type" : "AWS::CloudFormation::WaitCondition",
      "Properties" : {
        "Handle" : {"Ref" : "WaitHandle"},
        "Timeout" : "5",
        "Count" : "3"
      }
    }
  }
}
'''


class WaitConditionTest(common.HeatTestCase):

    def setUp(self):
        super(WaitConditionTest, self).setUp()

    def create_stack(self, stack_id=None,
                     template=test_template_waitcondition, params=None,
                     stub=True, stub_status=True):
        params = params or {}
        temp = template_format.parse(template)
        template = tmpl.Template(temp,
                                 env=environment.Environment(params))
        ctx = utils.dummy_context(tenant_id='test_tenant')
        stack = parser.Stack(ctx, 'test_stack', template,
                             disable_rollback=True)

        # Stub out the stack ID so we have a known value
        if stack_id is None:
            stack_id = str(uuid.uuid4())

        self.stack_id = stack_id
        with utils.UUIDStub(self.stack_id):
            stack.store()

        if stub:
            id = identifier.ResourceIdentifier('test_tenant', stack.name,
                                               stack.id, '', 'WaitHandle')
            self.m.StubOutWithMock(aws_wch.WaitConditionHandle, 'identifier')
            aws_wch.WaitConditionHandle.identifier(
            ).MultipleTimes().AndReturn(id)

        if stub_status:
            self.m.StubOutWithMock(aws_wch.WaitConditionHandle,
                                   'get_status')

        return stack

    def test_post_success_to_handle(self):
        self.stack = self.create_stack()
        aws_wch.WaitConditionHandle.get_status().AndReturn([])
        aws_wch.WaitConditionHandle.get_status().AndReturn([])
        aws_wch.WaitConditionHandle.get_status().AndReturn(['SUCCESS'])

        self.m.ReplayAll()

        self.stack.create()

        rsrc = self.stack['WaitForTheHandle']
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE),
                         rsrc.state)

        r = resource_objects.Resource.get_by_name_and_stack(
            None, 'WaitHandle', self.stack.id)
        self.assertEqual('WaitHandle', r.name)
        self.m.VerifyAll()

    def test_post_failure_to_handle(self):
        self.stack = self.create_stack()
        aws_wch.WaitConditionHandle.get_status().AndReturn([])
        aws_wch.WaitConditionHandle.get_status().AndReturn([])
        aws_wch.WaitConditionHandle.get_status().AndReturn(['FAILURE'])

        self.m.ReplayAll()

        self.stack.create()

        rsrc = self.stack['WaitForTheHandle']
        self.assertEqual((rsrc.CREATE, rsrc.FAILED), rsrc.state)
        reason = rsrc.status_reason
        self.assertTrue(reason.startswith('WaitConditionFailure:'))

        r = resource_objects.Resource.get_by_name_and_stack(
            None, 'WaitHandle', self.stack.id)
        self.assertEqual('WaitHandle', r.name)
        self.m.VerifyAll()

    def test_post_success_to_handle_count(self):
        self.stack = self.create_stack(template=test_template_wc_count)
        aws_wch.WaitConditionHandle.get_status().AndReturn([])
        aws_wch.WaitConditionHandle.get_status().AndReturn(['SUCCESS'])
        aws_wch.WaitConditionHandle.get_status().AndReturn(['SUCCESS',
                                                            'SUCCESS'])
        aws_wch.WaitConditionHandle.get_status().AndReturn(['SUCCESS',
                                                            'SUCCESS',
                                                            'SUCCESS'])

        self.m.ReplayAll()

        self.stack.create()

        rsrc = self.stack['WaitForTheHandle']
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE),
                         rsrc.state)

        r = resource_objects.Resource.get_by_name_and_stack(
            None, 'WaitHandle', self.stack.id)
        self.assertEqual('WaitHandle', r.name)
        self.m.VerifyAll()

    def test_post_failure_to_handle_count(self):
        self.stack = self.create_stack(template=test_template_wc_count)
        aws_wch.WaitConditionHandle.get_status().AndReturn([])
        aws_wch.WaitConditionHandle.get_status().AndReturn(['SUCCESS'])
        aws_wch.WaitConditionHandle.get_status().AndReturn(['SUCCESS',
                                                            'FAILURE'])

        self.m.ReplayAll()

        self.stack.create()

        rsrc = self.stack['WaitForTheHandle']
        self.assertEqual((rsrc.CREATE, rsrc.FAILED), rsrc.state)
        reason = rsrc.status_reason
        self.assertTrue(reason.startswith('WaitConditionFailure:'))

        r = resource_objects.Resource.get_by_name_and_stack(
            None, 'WaitHandle', self.stack.id)
        self.assertEqual('WaitHandle', r.name)
        self.m.VerifyAll()

    def test_timeout(self):
        self.stack = self.create_stack()

        # Avoid the stack create exercising the timeout code at the same time
        self.m.StubOutWithMock(self.stack, 'timeout_secs')
        self.stack.timeout_secs().MultipleTimes().AndReturn(None)

        now = timeutils.utcnow()
        fake_clock = [now + datetime.timedelta(0, t)
                      for t in (0, 0.001, 0.1, 4.1, 5.1)]
        timeutils.set_time_override(fake_clock)
        self.addCleanup(timeutils.clear_time_override)

        aws_wch.WaitConditionHandle.get_status(
        ).MultipleTimes().AndReturn([])

        self.m.ReplayAll()

        self.stack.create()

        rsrc = self.stack['WaitForTheHandle']

        self.assertEqual((rsrc.CREATE, rsrc.FAILED), rsrc.state)
        reason = rsrc.status_reason
        self.assertTrue(reason.startswith('WaitConditionTimeout:'))

        self.m.VerifyAll()

    def test_FnGetAtt(self):
        self.stack = self.create_stack()
        aws_wch.WaitConditionHandle.get_status().AndReturn(['SUCCESS'])

        self.m.ReplayAll()
        self.stack.create()

        rsrc = self.stack['WaitForTheHandle']
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

        wc_att = rsrc.FnGetAtt('Data')
        self.assertEqual(six.text_type({}), wc_att)

        handle = self.stack['WaitHandle']
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), handle.state)

        test_metadata = {'Data': 'foo', 'Reason': 'bar',
                         'Status': 'SUCCESS', 'UniqueId': '123'}
        ret = handle.handle_signal(test_metadata)
        wc_att = rsrc.FnGetAtt('Data')
        self.assertEqual('{"123": "foo"}', wc_att)
        self.assertEqual('status:SUCCESS reason:bar', ret)

        test_metadata = {'Data': 'dog', 'Reason': 'cat',
                         'Status': 'SUCCESS', 'UniqueId': '456'}
        ret = handle.handle_signal(test_metadata)
        wc_att = rsrc.FnGetAtt('Data')
        self.assertIsInstance(wc_att, six.string_types)
        self.assertEqual({"123": "foo", "456": "dog"}, json.loads(wc_att))
        self.assertEqual('status:SUCCESS reason:cat', ret)
        self.m.VerifyAll()

    def test_validate_handle_url_bad_stackid(self):
        self.m.ReplayAll()

        stack_id = 'STACK_HUBSID_1234'
        t = json.loads(test_template_waitcondition)
        badhandle = ("http://server.test:8000/v1/waitcondition/" +
                     "arn%3Aopenstack%3Aheat%3A%3Atest_tenant" +
                     "%3Astacks%2Ftest_stack%2F" +
                     "bad1" +
                     "%2Fresources%2FWaitHandle")
        t['Resources']['WaitForTheHandle']['Properties']['Handle'] = badhandle
        self.stack = self.create_stack(template=json.dumps(t), stub=False,
                                       stack_id=stack_id)
        self.m.ReplayAll()

        rsrc = self.stack['WaitForTheHandle']
        self.assertRaises(ValueError, rsrc.handle_create)

        self.m.VerifyAll()

    def test_validate_handle_url_bad_stackname(self):
        self.m.ReplayAll()

        stack_id = 'STACKABCD1234'
        t = json.loads(test_template_waitcondition)
        badhandle = ("http://server.test:8000/v1/waitcondition/" +
                     "arn%3Aopenstack%3Aheat%3A%3Atest_tenant" +
                     "%3Astacks%2FBAD_stack%2F" +
                     stack_id + "%2Fresources%2FWaitHandle")
        t['Resources']['WaitForTheHandle']['Properties']['Handle'] = badhandle
        self.stack = self.create_stack(template=json.dumps(t), stub=False,
                                       stack_id=stack_id)

        rsrc = self.stack['WaitForTheHandle']
        self.assertRaises(ValueError, rsrc.handle_create)

        self.m.VerifyAll()

    def test_validate_handle_url_bad_tenant(self):
        self.m.ReplayAll()

        stack_id = 'STACKABCD1234'
        t = json.loads(test_template_waitcondition)
        badhandle = ("http://server.test:8000/v1/waitcondition/" +
                     "arn%3Aopenstack%3Aheat%3A%3ABAD_tenant" +
                     "%3Astacks%2Ftest_stack%2F" +
                     stack_id + "%2Fresources%2FWaitHandle")
        t['Resources']['WaitForTheHandle']['Properties']['Handle'] = badhandle
        self.stack = self.create_stack(stack_id=stack_id,
                                       template=json.dumps(t), stub=False)

        rsrc = self.stack['WaitForTheHandle']
        self.assertRaises(ValueError, rsrc.handle_create)

        self.m.VerifyAll()

    def test_validate_handle_url_bad_resource(self):
        self.m.ReplayAll()

        stack_id = 'STACK_HUBR_1234'
        t = json.loads(test_template_waitcondition)
        badhandle = ("http://server.test:8000/v1/waitcondition/" +
                     "arn%3Aopenstack%3Aheat%3A%3Atest_tenant" +
                     "%3Astacks%2Ftest_stack%2F" +
                     stack_id + "%2Fresources%2FBADHandle")
        t['Resources']['WaitForTheHandle']['Properties']['Handle'] = badhandle
        self.stack = self.create_stack(stack_id=stack_id,
                                       template=json.dumps(t), stub=False)

        rsrc = self.stack['WaitForTheHandle']
        self.assertRaises(ValueError, rsrc.handle_create)

        self.m.VerifyAll()

    def test_validate_handle_url_bad_resource_type(self):
        self.m.ReplayAll()
        stack_id = 'STACKABCD1234'
        t = json.loads(test_template_waitcondition)
        badhandle = ("http://server.test:8000/v1/waitcondition/" +
                     "arn%3Aopenstack%3Aheat%3A%3Atest_tenant" +
                     "%3Astacks%2Ftest_stack%2F" +
                     stack_id + "%2Fresources%2FWaitForTheHandle")
        t['Resources']['WaitForTheHandle']['Properties']['Handle'] = badhandle
        self.stack = self.create_stack(stack_id=stack_id,
                                       template=json.dumps(t), stub=False)

        rsrc = self.stack['WaitForTheHandle']
        self.assertRaises(ValueError, rsrc.handle_create)

        self.m.VerifyAll()


class WaitConditionHandleTest(common.HeatTestCase):
    def setUp(self):
        super(WaitConditionHandleTest, self).setUp()

    def create_stack(self, stack_name=None, stack_id=None):
        temp = template_format.parse(test_template_waitcondition)
        template = tmpl.Template(temp)
        ctx = utils.dummy_context(tenant_id='test_tenant')
        if stack_name is None:
            stack_name = utils.random_name()
        stack = parser.Stack(ctx, stack_name, template,
                             disable_rollback=True)
        # Stub out the UUID for this test, so we can get an expected signature
        if stack_id is not None:
            with utils.UUIDStub(stack_id):
                stack.store()
        else:
            stack.store()
        self.stack_id = stack.id

        # Stub waitcondition status so all goes CREATE_COMPLETE
        self.m.StubOutWithMock(aws_wch.WaitConditionHandle, 'get_status')
        aws_wch.WaitConditionHandle.get_status().AndReturn(['SUCCESS'])

        id = identifier.ResourceIdentifier('test_tenant', stack.name,
                                           stack.id, '', 'WaitHandle')
        self.m.StubOutWithMock(aws_wch.WaitConditionHandle, 'identifier')
        aws_wch.WaitConditionHandle.identifier().MultipleTimes().AndReturn(id)
        self.m.ReplayAll()
        stack.create()
        return stack

    def test_handle(self):
        stack_id = 'STACKABCD1234'
        stack_name = 'test_stack2'
        created_time = datetime.datetime(2012, 11, 29, 13, 49, 37)
        self.stack = self.create_stack(stack_id=stack_id,
                                       stack_name=stack_name)

        self.m.StubOutWithMock(self.stack.clients.client_plugin('heat'),
                               'get_heat_cfn_url')
        self.stack.clients.client_plugin('heat').get_heat_cfn_url().AndReturn(
            'http://server.test:8000/v1')
        self.m.ReplayAll()
        rsrc = self.stack['WaitHandle']
        self.assertEqual(rsrc.resource_id, rsrc.data().get('user_id'))
        # clear the url
        rsrc.data_set('ec2_signed_url', None, False)

        rsrc.created_time = created_time
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        connection_url = "".join([
            'http://server.test:8000/v1/waitcondition/',
            'arn%3Aopenstack%3Aheat%3A%3Atest_tenant%3Astacks%2F',
            'test_stack2%2F', stack_id, '%2Fresources%2F',
            'WaitHandle?'])

        expected_url = "".join([
            connection_url,
            'Timestamp=2012-11-29T13%3A49%3A37Z&',
            'SignatureMethod=HmacSHA256&',
            'AWSAccessKeyId=4567&',
            'SignatureVersion=2&',
            'Signature=',
            'fHyt3XFnHq8%2FSwYaVcHdJka1hz6jdK5mHtgbo8OOKbQ%3D'])

        actual_url = rsrc.FnGetRefId()
        expected_params = parse.parse_qs(expected_url.split("?", 1)[1])
        actual_params = parse.parse_qs(actual_url.split("?", 1)[1])
        self.assertEqual(expected_params, actual_params)
        self.assertTrue(connection_url.startswith(connection_url))

        self.m.VerifyAll()

    def test_handle_signal(self):
        self.stack = self.create_stack()
        rsrc = self.stack['WaitHandle']
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        self.assertEqual(rsrc.resource_id, rsrc.data().get('user_id'))
        test_metadata = {'Data': 'foo', 'Reason': 'bar',
                         'Status': 'SUCCESS', 'UniqueId': '123'}
        rsrc.handle_signal(test_metadata)
        handle_metadata = {u'123': {u'Data': u'foo',
                                    u'Reason': u'bar',
                                    u'Status': u'SUCCESS'}}
        self.assertEqual(handle_metadata, rsrc.metadata_get())
        self.m.VerifyAll()

    def test_handle_signal_invalid(self):
        self.stack = self.create_stack()
        rsrc = self.stack['WaitHandle']
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        self.assertEqual(rsrc.resource_id, rsrc.data().get('user_id'))
        # handle_signal should raise a ValueError if the metadata
        # is missing any of the expected keys
        err_metadata = {'Data': 'foo', 'Status': 'SUCCESS', 'UniqueId': '123'}
        self.assertRaises(ValueError, rsrc.handle_signal,
                          err_metadata)

        err_metadata = {'Data': 'foo', 'Reason': 'bar', 'UniqueId': '1234'}
        self.assertRaises(ValueError, rsrc.handle_signal,
                          err_metadata)

        err_metadata = {'Data': 'foo', 'Reason': 'bar', 'UniqueId': '1234'}
        self.assertRaises(ValueError, rsrc.handle_signal,
                          err_metadata)

        err_metadata = {'data': 'foo', 'reason': 'bar',
                        'status': 'SUCCESS', 'uniqueid': '1234'}
        self.assertRaises(ValueError, rsrc.handle_signal,
                          err_metadata)

        # Also any Status other than SUCCESS or FAILURE should be rejected
        err_metadata = {'Data': 'foo', 'Reason': 'bar',
                        'Status': 'UCCESS', 'UniqueId': '123'}
        self.assertRaises(ValueError, rsrc.handle_signal,
                          err_metadata)
        err_metadata = {'Data': 'foo', 'Reason': 'bar',
                        'Status': 'wibble', 'UniqueId': '123'}
        self.assertRaises(ValueError, rsrc.handle_signal,
                          err_metadata)
        err_metadata = {'Data': 'foo', 'Reason': 'bar',
                        'Status': 'success', 'UniqueId': '123'}
        self.assertRaises(ValueError, rsrc.handle_signal,
                          err_metadata)
        err_metadata = {'Data': 'foo', 'Reason': 'bar',
                        'Status': 'FAIL', 'UniqueId': '123'}
        self.assertRaises(ValueError, rsrc.handle_signal,
                          err_metadata)
        self.m.VerifyAll()

    def test_get_status(self):
        self.stack = self.create_stack()
        rsrc = self.stack['WaitHandle']
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        self.assertEqual(rsrc.resource_id, rsrc.data().get('user_id'))
        # UnsetStubs, don't want get_status stubbed anymore..
        self.m.VerifyAll()
        self.m.UnsetStubs()

        self.assertEqual([], rsrc.get_status())

        test_metadata = {'Data': 'foo', 'Reason': 'bar',
                         'Status': 'SUCCESS', 'UniqueId': '123'}
        ret = rsrc.handle_signal(test_metadata)
        self.assertEqual(['SUCCESS'], rsrc.get_status())
        self.assertEqual('status:SUCCESS reason:bar', ret)

        test_metadata = {'Data': 'foo', 'Reason': 'bar2',
                         'Status': 'SUCCESS', 'UniqueId': '456'}
        ret = rsrc.handle_signal(test_metadata)
        self.assertEqual(['SUCCESS', 'SUCCESS'], rsrc.get_status())
        self.assertEqual('status:SUCCESS reason:bar2', ret)

    def test_get_status_reason(self):
        self.stack = self.create_stack()
        rsrc = self.stack['WaitHandle']
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

        test_metadata = {'Data': 'foo', 'Reason': 'bar',
                         'Status': 'SUCCESS', 'UniqueId': '123'}
        ret = rsrc.handle_signal(test_metadata)
        self.assertEqual(['bar'], rsrc.get_status_reason('SUCCESS'))
        self.assertEqual('status:SUCCESS reason:bar', ret)

        test_metadata = {'Data': 'dog', 'Reason': 'cat',
                         'Status': 'SUCCESS', 'UniqueId': '456'}
        ret = rsrc.handle_signal(test_metadata)
        self.assertEqual(
            ['bar', 'cat'], sorted(rsrc.get_status_reason('SUCCESS')))
        self.assertEqual('status:SUCCESS reason:cat', ret)

        test_metadata = {'Data': 'boo', 'Reason': 'hoo',
                         'Status': 'FAILURE', 'UniqueId': '789'}
        ret = rsrc.handle_signal(test_metadata)
        self.assertEqual(['hoo'], rsrc.get_status_reason('FAILURE'))
        self.assertEqual('status:FAILURE reason:hoo', ret)
        self.m.VerifyAll()


class WaitConditionUpdateTest(common.HeatTestCase):
    def setUp(self):
        super(WaitConditionUpdateTest, self).setUp()

    def create_stack(self, temp=None):
        if temp is None:
            temp = test_template_wc_count
        temp_fmt = template_format.parse(temp)
        template = tmpl.Template(temp_fmt)
        ctx = utils.dummy_context(tenant_id='test_tenant')
        stack = parser.Stack(ctx, 'test_stack', template,
                             disable_rollback=True)

        stack_id = str(uuid.uuid4())
        self.stack_id = stack_id
        with utils.UUIDStub(self.stack_id):
            stack.store()

        self.m.StubOutWithMock(aws_wch.WaitConditionHandle, 'get_status')
        aws_wch.WaitConditionHandle.get_status().AndReturn([])
        aws_wch.WaitConditionHandle.get_status().AndReturn(['SUCCESS'])
        aws_wch.WaitConditionHandle.get_status().AndReturn(['SUCCESS',
                                                            'SUCCESS'])
        aws_wch.WaitConditionHandle.get_status().AndReturn(['SUCCESS',
                                                            'SUCCESS',
                                                            'SUCCESS'])

        return stack

    def get_stack(self, stack_id):
        ctx = utils.dummy_context(tenant_id='test_tenant')
        stack = parser.Stack.load(ctx, stack_id)
        self.stack_id = stack_id
        return stack

    def test_update(self):
        self.stack = self.create_stack()
        self.m.ReplayAll()
        self.stack.create()

        rsrc = self.stack['WaitForTheHandle']
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

        self.m.VerifyAll()
        self.m.UnsetStubs()

        wait_condition_handle = self.stack['WaitHandle']
        test_metadata = {'Data': 'foo', 'Reason': 'bar',
                         'Status': 'SUCCESS', 'UniqueId': '1'}
        self._handle_signal(wait_condition_handle, test_metadata, 5)

        uprops = copy.copy(rsrc.properties.data)
        uprops['Count'] = '5'
        update_snippet = rsrc_defn.ResourceDefinition(rsrc.name,
                                                      rsrc.type(),
                                                      uprops)

        updater = scheduler.TaskRunner(rsrc.update, update_snippet)
        updater()

        self.assertEqual((rsrc.UPDATE, rsrc.COMPLETE), rsrc.state)

    def test_update_restored_from_db(self):
        self.stack = self.create_stack()
        self.m.ReplayAll()
        self.stack.create()

        rsrc = self.stack['WaitForTheHandle']
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

        self.m.VerifyAll()
        self.m.UnsetStubs()

        handle_stack = self.stack
        wait_condition_handle = handle_stack['WaitHandle']
        test_metadata = {'Data': 'foo', 'Reason': 'bar',
                         'Status': 'SUCCESS', 'UniqueId': '1'}
        self._handle_signal(wait_condition_handle, test_metadata, 2)

        self.stack.store()
        self.stack = self.get_stack(self.stack_id)
        rsrc = self.stack['WaitForTheHandle']

        self._handle_signal(wait_condition_handle, test_metadata, 3)

        uprops = copy.copy(rsrc.properties.data)
        uprops['Count'] = '5'
        update_snippet = rsrc_defn.ResourceDefinition(rsrc.name,
                                                      rsrc.type(),
                                                      uprops)

        updater = scheduler.TaskRunner(rsrc.update, update_snippet)
        updater()

        self.assertEqual((rsrc.UPDATE, rsrc.COMPLETE), rsrc.state)

    def _handle_signal(self, rsrc, metadata, times=1):
        for t in range(times):
            metadata['UniqueId'] = metadata['UniqueId'] * 2
            ret = rsrc.handle_signal(metadata)
            self.assertEqual("status:%s reason:%s" %
                             (metadata[rsrc.STATUS], metadata[rsrc.REASON]),
                             ret)

    def test_update_timeout(self):
        self.stack = self.create_stack()
        self.m.ReplayAll()
        self.stack.create()

        rsrc = self.stack['WaitForTheHandle']
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

        self.m.VerifyAll()
        self.m.UnsetStubs()

        now = timeutils.utcnow()
        fake_clock = [now + datetime.timedelta(0, t)
                      for t in (0, 0.001, 0.1, 4.1, 5.1)]
        timeutils.set_time_override(fake_clock)
        self.addCleanup(timeutils.clear_time_override)

        self.m.StubOutWithMock(aws_wch.WaitConditionHandle, 'get_status')
        aws_wch.WaitConditionHandle.get_status().MultipleTimes().AndReturn([])

        self.m.ReplayAll()

        uprops = copy.copy(rsrc.properties.data)
        uprops['Count'] = '5'
        update_snippet = rsrc_defn.ResourceDefinition(rsrc.name,
                                                      rsrc.type(),
                                                      uprops)

        updater = scheduler.TaskRunner(rsrc.update, update_snippet)
        ex = self.assertRaises(exception.ResourceFailure,
                               updater)
        self.assertEqual("WaitConditionTimeout: resources.WaitForTheHandle: "
                         "0 of 5 received", six.text_type(ex))
        self.assertEqual(5, rsrc.properties['Count'])
        self.m.VerifyAll()
