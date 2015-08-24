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

from oslo_config import cfg
import six

from heat.common import exception
from heat.common import short_id
from heat.common import template_format
from heat.engine.resources.aws.iam import user
from heat.engine.resources.openstack.heat import access_policy as ap
from heat.engine import scheduler
from heat.objects import resource_data as resource_data_object
from heat.tests import common
from heat.tests import fakes
from heat.tests import utils


user_template = '''
{
  "AWSTemplateFormatVersion" : "2010-09-09",
  "Description" : "Just a User",
  "Parameters" : {},
  "Resources" : {
    "CfnUser" : {
      "Type" : "AWS::IAM::User"
    }
  }
}
'''

user_template_password = '''
{
  "AWSTemplateFormatVersion" : "2010-09-09",
  "Description" : "Just a User",
  "Parameters" : {},
  "Resources" : {
    "CfnUser" : {
      "Type" : "AWS::IAM::User",
      "Properties": {
        "LoginProfile": { "Password": "myP@ssW0rd" }
      }
    }
  }
}
'''

user_accesskey_template = '''
{
  "AWSTemplateFormatVersion" : "2010-09-09",
  "Description" : "Just a User",
  "Parameters" : {},
  "Resources" : {
    "CfnUser" : {
      "Type" : "AWS::IAM::User"
    },

    "HostKeys" : {
      "Type" : "AWS::IAM::AccessKey",
      "Properties" : {
        "UserName" : {"Ref": "CfnUser"}
      }
    }
  }
}
'''


user_policy_template = '''
{
  "AWSTemplateFormatVersion" : "2010-09-09",
  "Description" : "Just a User",
  "Parameters" : {},
  "Resources" : {
    "CfnUser" : {
      "Type" : "AWS::IAM::User",
      "Properties" : {
        "Policies" : [ { "Ref": "WebServerAccessPolicy"} ]
      }
    },
    "WebServerAccessPolicy" : {
      "Type" : "OS::Heat::AccessPolicy",
      "Properties" : {
        "AllowedResources" : [ "WikiDatabase" ]
      }
    },
    "WikiDatabase" : {
      "Type" : "AWS::EC2::Instance",
    }
  }
}
'''


class UserTest(common.HeatTestCase):
    def setUp(self):
        super(UserTest, self).setUp()
        self.stack_name = 'test_user_stack_%s' % utils.random_name()
        self.username = '%s-CfnUser-aabbcc' % self.stack_name
        self.fc = fakes.FakeKeystoneClient(username=self.username)
        cfg.CONF.set_default('heat_stack_user_role', 'stack_user_role')

    def create_user(self, t, stack, resource_name,
                    project_id='stackproject', user_id='dummy_user',
                    password=None):
        self.m.StubOutWithMock(user.User, 'keystone')
        user.User.keystone().MultipleTimes().AndReturn(self.fc)

        self.m.StubOutWithMock(fakes.FakeKeystoneClient,
                               'create_stack_domain_project')
        fakes.FakeKeystoneClient.create_stack_domain_project(
            stack.id).AndReturn(project_id)

        resource_defns = stack.t.resource_definitions(stack)
        rsrc = user.User(resource_name,
                         resource_defns[resource_name],
                         stack)
        rsrc._store()

        self.m.StubOutWithMock(short_id, 'get_id')
        short_id.get_id(rsrc.uuid).MultipleTimes().AndReturn('aabbcc')

        self.m.StubOutWithMock(fakes.FakeKeystoneClient,
                               'create_stack_domain_user')
        fakes.FakeKeystoneClient.create_stack_domain_user(
            username=self.username, password=password,
            project_id=project_id).AndReturn(user_id)
        self.m.ReplayAll()
        self.assertIsNone(rsrc.validate())
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        return rsrc

    def test_user(self):
        t = template_format.parse(user_template)
        stack = utils.parse_stack(t, stack_name=self.stack_name)

        rsrc = self.create_user(t, stack, 'CfnUser')
        self.assertEqual('dummy_user', rsrc.resource_id)
        self.assertEqual(self.username, rsrc.FnGetRefId())

        self.assertRaises(exception.InvalidTemplateAttribute,
                          rsrc.FnGetAtt, 'Foo')

        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

        self.assertIsNone(rsrc.handle_suspend())
        self.assertIsNone(rsrc.handle_resume())

        rsrc.resource_id = None
        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)

        rsrc.resource_id = self.fc.access
        rsrc.state_set(rsrc.CREATE, rsrc.COMPLETE)
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)

        rsrc.state_set(rsrc.CREATE, rsrc.COMPLETE)
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_user_password(self):
        t = template_format.parse(user_template_password)
        stack = utils.parse_stack(t, stack_name=self.stack_name)

        rsrc = self.create_user(t, stack, 'CfnUser', password=u'myP@ssW0rd')
        self.assertEqual('dummy_user', rsrc.resource_id)
        self.assertEqual(self.username, rsrc.FnGetRefId())

        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_user_validate_policies(self):
        t = template_format.parse(user_policy_template)
        stack = utils.parse_stack(t, stack_name=self.stack_name)

        rsrc = self.create_user(t, stack, 'CfnUser')
        self.assertEqual('dummy_user', rsrc.resource_id)
        self.assertEqual(self.username, rsrc.FnGetRefId())
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

        self.assertEqual([u'WebServerAccessPolicy'],
                         rsrc.properties['Policies'])

        # OK
        self.assertTrue(rsrc._validate_policies([u'WebServerAccessPolicy']))

        # Resource name doesn't exist in the stack
        self.assertFalse(rsrc._validate_policies([u'NoExistAccessPolicy']))

        # Resource name is wrong Resource type
        self.assertFalse(rsrc._validate_policies([u'NoExistAccessPolicy',
                                                  u'WikiDatabase']))

        # Wrong type (AWS embedded policy format, not yet supported)
        dict_policy = {"PolicyName": "AccessForCFNInit",
                       "PolicyDocument":
                       {"Statement": [{"Effect": "Allow",
                                       "Action":
                                       "cloudformation:DescribeStackResource",
                                       "Resource": "*"}]}}

        # However we should just ignore it to avoid breaking existing templates
        self.assertTrue(rsrc._validate_policies([dict_policy]))

        self.m.VerifyAll()

    def test_user_create_bad_policies(self):
        t = template_format.parse(user_policy_template)
        t['Resources']['CfnUser']['Properties']['Policies'] = ['NoExistBad']
        stack = utils.parse_stack(t, stack_name=self.stack_name)
        resource_name = 'CfnUser'
        resource_defns = stack.t.resource_definitions(stack)
        rsrc = user.User(resource_name,
                         resource_defns[resource_name],
                         stack)
        self.assertRaises(exception.InvalidTemplateAttribute,
                          rsrc.handle_create)

    def test_user_access_allowed(self):
        self.m.StubOutWithMock(ap.AccessPolicy, 'access_allowed')
        ap.AccessPolicy.access_allowed('a_resource').AndReturn(True)
        ap.AccessPolicy.access_allowed('b_resource').AndReturn(False)

        self.m.ReplayAll()

        t = template_format.parse(user_policy_template)
        stack = utils.parse_stack(t, stack_name=self.stack_name)

        rsrc = self.create_user(t, stack, 'CfnUser')
        self.assertEqual('dummy_user', rsrc.resource_id)
        self.assertEqual(self.username, rsrc.FnGetRefId())
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

        self.assertTrue(rsrc.access_allowed('a_resource'))
        self.assertFalse(rsrc.access_allowed('b_resource'))
        self.m.VerifyAll()

    def test_user_access_allowed_ignorepolicy(self):
        self.m.StubOutWithMock(ap.AccessPolicy, 'access_allowed')
        ap.AccessPolicy.access_allowed('a_resource').AndReturn(True)
        ap.AccessPolicy.access_allowed('b_resource').AndReturn(False)

        self.m.ReplayAll()

        t = template_format.parse(user_policy_template)
        t['Resources']['CfnUser']['Properties']['Policies'] = [
            'WebServerAccessPolicy', {'an_ignored': 'policy'}]
        stack = utils.parse_stack(t, stack_name=self.stack_name)

        rsrc = self.create_user(t, stack, 'CfnUser')
        self.assertEqual('dummy_user', rsrc.resource_id)
        self.assertEqual(self.username, rsrc.FnGetRefId())
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

        self.assertTrue(rsrc.access_allowed('a_resource'))
        self.assertFalse(rsrc.access_allowed('b_resource'))
        self.m.VerifyAll()


class AccessKeyTest(common.HeatTestCase):
    def setUp(self):
        super(AccessKeyTest, self).setUp()
        self.username = utils.PhysName('test_stack', 'CfnUser')
        self.credential_id = 'acredential123'
        self.fc = fakes.FakeKeystoneClient(username=self.username,
                                           user_id='dummy_user',
                                           credential_id=self.credential_id)
        cfg.CONF.set_default('heat_stack_user_role', 'stack_user_role')

    def create_user(self, t, stack, resource_name,
                    project_id='stackproject', user_id='dummy_user',
                    password=None):
        self.m.StubOutWithMock(user.User, 'keystone')
        user.User.keystone().MultipleTimes().AndReturn(self.fc)

        self.m.ReplayAll()
        rsrc = stack[resource_name]
        self.assertIsNone(rsrc.validate())
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        return rsrc

    def create_access_key(self, t, stack, resource_name):
        resource_defns = stack.t.resource_definitions(stack)
        rsrc = user.AccessKey(resource_name,
                              resource_defns[resource_name],
                              stack)
        self.assertIsNone(rsrc.validate())
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        return rsrc

    def test_access_key(self):
        t = template_format.parse(user_accesskey_template)
        stack = utils.parse_stack(t)

        self.create_user(t, stack, 'CfnUser')
        rsrc = self.create_access_key(t, stack, 'HostKeys')

        self.m.VerifyAll()
        self.assertEqual(self.fc.access,
                         rsrc.resource_id)

        self.assertEqual(self.fc.secret,
                         rsrc._secret)

        # Ensure the resource data has been stored correctly
        rs_data = resource_data_object.ResourceData.get_all(rsrc)
        self.assertEqual(self.fc.secret, rs_data.get('secret_key'))
        self.assertEqual(self.fc.credential_id, rs_data.get('credential_id'))
        self.assertEqual(2, len(list(six.iterkeys(rs_data))))

        self.assertEqual(utils.PhysName(stack.name, 'CfnUser'),
                         rsrc.FnGetAtt('UserName'))
        rsrc._secret = None
        self.assertEqual(self.fc.secret,
                         rsrc.FnGetAtt('SecretAccessKey'))

        self.assertRaises(exception.InvalidTemplateAttribute,
                          rsrc.FnGetAtt, 'Foo')

        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_access_key_get_from_keystone(self):
        self.m.StubOutWithMock(user.AccessKey, 'keystone')
        user.AccessKey.keystone().MultipleTimes().AndReturn(self.fc)

        self.m.ReplayAll()

        t = template_format.parse(user_accesskey_template)

        stack = utils.parse_stack(t)

        self.create_user(t, stack, 'CfnUser')
        rsrc = self.create_access_key(t, stack, 'HostKeys')

        # Delete the resource data for secret_key, to test that existing
        # stacks which don't have the resource_data stored will continue
        # working via retrieving the keypair from keystone
        resource_data_object.ResourceData.delete(rsrc, 'credential_id')
        resource_data_object.ResourceData.delete(rsrc, 'secret_key')
        rs_data = resource_data_object.ResourceData.get_all(rsrc)
        self.assertEqual(0, len(list(six.iterkeys(rs_data))))

        rsrc._secret = None
        self.assertEqual(self.fc.secret,
                         rsrc.FnGetAtt('SecretAccessKey'))

        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_access_key_no_user(self):
        self.m.ReplayAll()

        t = template_format.parse(user_accesskey_template)
        # Set the resource properties UserName to an unknown user
        t['Resources']['HostKeys']['Properties']['UserName'] = 'NonExistent'
        stack = utils.parse_stack(t)
        stack['CfnUser'].resource_id = self.fc.user_id

        resource_defns = stack.t.resource_definitions(stack)
        rsrc = user.AccessKey('HostKeys',
                              resource_defns['HostKeys'],
                              stack)
        create = scheduler.TaskRunner(rsrc.create)
        self.assertRaises(exception.ResourceFailure, create)
        self.assertEqual((rsrc.CREATE, rsrc.FAILED), rsrc.state)

        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)

        self.m.VerifyAll()


class AccessPolicyTest(common.HeatTestCase):

    def test_accesspolicy_create_ok(self):
        t = template_format.parse(user_policy_template)
        stack = utils.parse_stack(t)

        resource_name = 'WebServerAccessPolicy'
        resource_defns = stack.t.resource_definitions(stack)
        rsrc = ap.AccessPolicy(resource_name,
                               resource_defns[resource_name],
                               stack)
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

    def test_accesspolicy_create_ok_empty(self):
        t = template_format.parse(user_policy_template)
        resource_name = 'WebServerAccessPolicy'
        t['Resources'][resource_name]['Properties']['AllowedResources'] = []
        stack = utils.parse_stack(t)

        resource_defns = stack.t.resource_definitions(stack)
        rsrc = ap.AccessPolicy(resource_name,
                               resource_defns[resource_name],
                               stack)
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)

    def test_accesspolicy_create_err_notfound(self):
        t = template_format.parse(user_policy_template)
        resource_name = 'WebServerAccessPolicy'
        t['Resources'][resource_name]['Properties']['AllowedResources'] = [
            'NoExistResource']
        stack = utils.parse_stack(t)

        self.assertRaises(exception.StackValidationFailed, stack.validate)

    def test_accesspolicy_access_allowed(self):
        t = template_format.parse(user_policy_template)
        resource_name = 'WebServerAccessPolicy'
        stack = utils.parse_stack(t)

        resource_defns = stack.t.resource_definitions(stack)
        rsrc = ap.AccessPolicy(resource_name,
                               resource_defns[resource_name],
                               stack)
        self.assertTrue(rsrc.access_allowed('WikiDatabase'))
        self.assertFalse(rsrc.access_allowed('NotWikiDatabase'))
        self.assertFalse(rsrc.access_allowed(None))
