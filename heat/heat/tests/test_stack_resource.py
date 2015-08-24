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

import json
import uuid

import mock
from oslo_config import cfg
from oslo_messaging import exceptions as msg_exceptions
from oslo_serialization import jsonutils
import six
import testtools

from heat.common import exception
from heat.common import template_format
from heat.engine import resource
from heat.engine.resources import stack_resource
from heat.engine import stack as parser
from heat.engine import template as templatem
from heat.tests import common
from heat.tests import generic_resource as generic_rsrc
from heat.tests import utils


ws_res_snippet = {"HeatTemplateFormatVersion": "2012-12-12",
                  "Type": "StackResourceType",
                  "metadata": {
                      "key": "value",
                      "some": "more stuff"}}

param_template = '''
{
  "AWSTemplateFormatVersion" : "2010-09-09",
  "Parameters" : {
    "KeyName" : {
      "Description" : "KeyName",
      "Type" : "String",
      "Default" : "test"
    }
  },
  "Resources" : {
    "WebServer": {
      "Type": "GenericResource",
      "Properties": {}
    }
  }
}
'''


simple_template = '''
{
  "AWSTemplateFormatVersion" : "2010-09-09",
  "Parameters" : {},
  "Resources" : {
    "WebServer": {
      "Type": "GenericResource",
      "Properties": {}
    }
  }
}
'''

main_template = '''
heat_template_version: 2013-05-23
resources:
  volume_server:
    type: nested.yaml
'''

my_wrong_nested_template = '''
heat_template_version: 2013-05-23
resources:
  server:
    type: OS::Nova::Server
    properties:
      image: F17-x86_64-gold
      flavor: m1.small
  volume:
    type: OS::Cinder::Volume
    properties:
      size: 10
      description: Volume for stack
  volume_attachment:
    type: OS::Cinder::VolumeAttachment
    properties:
      volume_id: { get_resource: volume }
      instance_uuid: { get_resource: instance }
'''

resource_group_template = '''
heat_template_version: 2013-05-23
resources:
  my_resource_group:
    type: OS::Heat::ResourceGroup
    properties:
      resource_def:
        type: idontexist
'''

heat_autoscaling_group_template = '''
heat_template_version: 2013-05-23
resources:
  my_autoscaling_group:
    type: OS::Heat::AutoScalingGroup
    properties:
      resource:
        type: idontexist
      desired_capacity: 2
      max_size: 4
      min_size: 1
'''

nova_server_template = '''
heat_template_version: 2013-05-23
resources:
  group_server:
    type: idontexist
'''


class MyImplementedStackResource(generic_rsrc.StackResourceType):
    def child_template(self):
        return self.nested_template

    def child_params(self):
        return self.nested_params


class StackResourceBaseTest(common.HeatTestCase):
    def setUp(self):
        super(StackResourceBaseTest, self).setUp()
        self.ws_resname = "provider_resource"
        self.empty_temp = templatem.Template(
            {'HeatTemplateFormatVersion': '2012-12-12',
             'Resources': {self.ws_resname: ws_res_snippet}})
        self.ctx = utils.dummy_context()
        self.parent_stack = parser.Stack(self.ctx, 'test_stack',
                                         self.empty_temp,
                                         stack_id=str(uuid.uuid4()),
                                         user_creds_id='uc123',
                                         stack_user_project_id='aprojectid')
        resource_defns = self.empty_temp.resource_definitions(
            self.parent_stack)
        self.parent_resource = generic_rsrc.StackResourceType(
            'test', resource_defns[self.ws_resname], self.parent_stack)


class StackResourceTest(StackResourceBaseTest):

    def setUp(self):
        super(StackResourceTest, self).setUp()
        self.templ = template_format.parse(param_template)
        self.simple_template = template_format.parse(simple_template)

        # to get same json string from a dict for comparison,
        # make sort_keys True
        orig_dumps = jsonutils.dumps

        def sorted_dumps(*args, **kwargs):
            kwargs.setdefault('sort_keys', True)
            return orig_dumps(*args, **kwargs)
        patched_dumps = mock.patch(
            'oslo_serialization.jsonutils.dumps', sorted_dumps)
        patched_dumps.start()
        self.addCleanup(lambda: patched_dumps.stop())

    def test_child_template_defaults_to_not_implemented(self):
        self.assertRaises(NotImplementedError,
                          self.parent_resource.child_template)

    def test_child_params_defaults_to_not_implemented(self):
        self.assertRaises(NotImplementedError,
                          self.parent_resource.child_params)

    def test_preview_defaults_to_stack_resource_itself(self):
        preview = self.parent_resource.preview()
        self.assertIsInstance(preview, stack_resource.StackResource)

    def test_nested_stack_abandon(self):
        nest = mock.MagicMock()
        self.parent_resource.nested = nest
        nest.return_value.prepare_abandon.return_value = {'X': 'Y'}
        ret = self.parent_resource.prepare_abandon()
        nest.return_value.prepare_abandon.assert_called_once_with()
        self.assertEqual({'X': 'Y'}, ret)

    def test_nested_abandon_stack_not_found(self):
        self.parent_resource.nested = mock.MagicMock(return_value=None)
        ret = self.parent_resource.prepare_abandon()
        self.assertEqual({}, ret)

    @testtools.skipIf(six.PY3, "needs a separate change")
    def test_implementation_signature(self):
        self.parent_resource.child_template = mock.Mock(
            return_value=self.simple_template)
        sig1, sig2 = self.parent_resource.implementation_signature()
        self.assertEqual('7b0eaabb5b82b9e90804d42e0bb739035588cb797'
                         '82427770646686ca2235028', sig1)
        self.assertEqual('8fa647d036b8f36909386e1e1004539dfae7a8e88'
                         'c24aac0d85399e881421301', sig2)
        self.parent_stack.t.files["foo"] = "bar"
        sig1a, sig2a = self.parent_resource.implementation_signature()
        self.assertEqual(sig1, sig1a)
        self.assertNotEqual(sig2, sig2a)

    def test_propagated_files(self):
        """Makes sure that the files map in the top level stack
        are passed on to the child stack.
        """
        self.parent_stack.t.files["foo"] = "bar"
        parsed_t = self.parent_resource._parse_child_template(self.templ, None)
        self.assertEqual({"foo": "bar"}, parsed_t.files)

    @mock.patch('heat.engine.environment.get_child_environment')
    @mock.patch.object(stack_resource.parser, 'Stack')
    def test_preview_with_implemented_child_resource(self, mock_stack_class,
                                                     mock_env_class):
        nested_stack = mock.Mock()
        mock_stack_class.return_value = nested_stack
        nested_stack.preview_resources.return_value = 'preview_nested_stack'
        mock_env_class.return_value = 'environment'
        template = templatem.Template(template_format.parse(param_template))
        parent_t = self.parent_stack.t
        resource_defns = parent_t.resource_definitions(self.parent_stack)
        parent_resource = MyImplementedStackResource(
            'test',
            resource_defns[self.ws_resname],
            self.parent_stack)
        params = {'KeyName': 'test'}
        parent_resource.set_template(template, params)
        validation_mock = mock.Mock(return_value=None)
        parent_resource._validate_nested_resources = validation_mock

        result = parent_resource.preview()
        mock_env_class.assert_called_once_with(
            self.parent_stack.env,
            params,
            child_resource_name='test',
            item_to_remove=None)
        self.assertEqual('preview_nested_stack', result)
        mock_stack_class.assert_called_once_with(
            mock.ANY,
            'test_stack-test',
            mock.ANY,
            timeout_mins=None,
            disable_rollback=True,
            parent_resource=parent_resource.name,
            owner_id=self.parent_stack.id,
            user_creds_id=self.parent_stack.user_creds_id,
            stack_user_project_id=self.parent_stack.stack_user_project_id,
            adopt_stack_data=None,
            nested_depth=1
        )

    @mock.patch('heat.engine.environment.get_child_environment')
    @mock.patch.object(stack_resource.parser, 'Stack')
    def test_preview_with_implemented_dict_child_resource(self,
                                                          mock_stack_class,
                                                          mock_env_class):
        nested_stack = mock.Mock()
        mock_stack_class.return_value = nested_stack
        nested_stack.preview_resources.return_value = 'preview_nested_stack'
        mock_env_class.return_value = 'environment'
        template_dict = template_format.parse(param_template)
        parent_t = self.parent_stack.t
        resource_defns = parent_t.resource_definitions(self.parent_stack)
        parent_resource = MyImplementedStackResource(
            'test',
            resource_defns[self.ws_resname],
            self.parent_stack)
        params = {'KeyName': 'test'}
        parent_resource.set_template(template_dict, params)
        validation_mock = mock.Mock(return_value=None)
        parent_resource._validate_nested_resources = validation_mock

        result = parent_resource.preview()
        mock_env_class.assert_called_once_with(
            self.parent_stack.env,
            params,
            child_resource_name='test',
            item_to_remove=None)
        self.assertEqual('preview_nested_stack', result)
        mock_stack_class.assert_called_once_with(
            mock.ANY,
            'test_stack-test',
            mock.ANY,
            timeout_mins=None,
            disable_rollback=True,
            parent_resource=parent_resource.name,
            owner_id=self.parent_stack.id,
            user_creds_id=self.parent_stack.user_creds_id,
            stack_user_project_id=self.parent_stack.stack_user_project_id,
            adopt_stack_data=None,
            nested_depth=1
        )

    def test_preview_propagates_files(self):
        self.parent_stack.t.files["foo"] = "bar"
        tmpl = self.parent_stack.t.t
        self.parent_resource.child_template = mock.Mock(return_value=tmpl)
        self.parent_resource.child_params = mock.Mock(return_value={})
        self.parent_resource.preview()
        self.stack = self.parent_resource.nested()
        self.assertEqual({"foo": "bar"}, self.stack.t.files)

    def test_preview_validates_nested_resources(self):
        parent_t = self.parent_stack.t
        resource_defns = parent_t.resource_definitions(self.parent_stack)
        stk_resource = MyImplementedStackResource(
            'test',
            resource_defns[self.ws_resname],
            self.parent_stack)
        stk_resource.child_params = mock.Mock(return_value={})
        stk_resource.child_template = mock.Mock(
            return_value=templatem.Template(self.simple_template,
                                            stk_resource.child_params))
        exc = exception.RequestLimitExceeded(message='Validation Failed')
        validation_mock = mock.Mock(side_effect=exc)
        stk_resource._validate_nested_resources = validation_mock

        self.assertRaises(exception.RequestLimitExceeded,
                          stk_resource.preview)

    def test_preview_dict_validates_nested_resources(self):
        parent_t = self.parent_stack.t
        resource_defns = parent_t.resource_definitions(self.parent_stack)
        stk_resource = MyImplementedStackResource(
            'test',
            resource_defns[self.ws_resname],
            self.parent_stack)
        stk_resource.child_params = mock.Mock(return_value={})
        stk_resource.child_template = mock.Mock(
            return_value=self.simple_template)
        exc = exception.RequestLimitExceeded(message='Validation Failed')
        validation_mock = mock.Mock(side_effect=exc)
        stk_resource._validate_nested_resources = validation_mock

        self.assertRaises(exception.RequestLimitExceeded,
                          stk_resource.preview)

    @mock.patch.object(stack_resource.parser, 'Stack')
    def test_preview_doesnt_validate_nested_stack(self, mock_stack_class):
        nested_stack = mock.Mock()
        mock_stack_class.return_value = nested_stack

        tmpl = self.parent_stack.t.t
        self.parent_resource.child_template = mock.Mock(return_value=tmpl)
        self.parent_resource.child_params = mock.Mock(return_value={})
        self.parent_resource.preview()

        self.assertFalse(nested_stack.validate.called)
        self.assertTrue(nested_stack.preview_resources.called)

    def test_validate_error_reference(self):
        stack_name = 'validate_error_reference'
        tmpl = template_format.parse(main_template)
        files = {'nested.yaml': my_wrong_nested_template}
        stack = parser.Stack(utils.dummy_context(), stack_name,
                             templatem.Template(tmpl, files=files))
        rsrc = stack['volume_server']
        raise_exc_msg = ('Failed to validate: resources.volume_server: '
                         'The specified reference "instance" '
                         '(in volume_attachment.Properties.instance_uuid) '
                         'is incorrect.')
        exc = self.assertRaises(exception.StackValidationFailed,
                                rsrc.validate)
        self.assertEqual(raise_exc_msg, six.text_type(exc))

    def _test_validate_unknown_resource_type(self, stack_name, tmpl,
                                             resource_name,
                                             stack_resource=True):
        raise_exc_msg = 'The Resource Type (idontexist) could not be found.'
        stack = parser.Stack(utils.dummy_context(), stack_name, tmpl)
        rsrc = stack[resource_name]
        if stack_resource:
            exc = self.assertRaises(exception.StackValidationFailed,
                                    rsrc.validate)
        else:
            exc = self.assertRaises(exception.ResourceTypeNotFound,
                                    rsrc.validate)
        self.assertIn(raise_exc_msg, six.text_type(exc))

    def test_validate_resource_group(self):
        # resource group validate without nested template is a normal
        # resource validation
        stack_name = 'validate_resource_group_template'
        t = template_format.parse(resource_group_template)
        tmpl = templatem.Template(t)
        self._test_validate_unknown_resource_type(stack_name, tmpl,
                                                  'my_resource_group',
                                                  stack_resource=False)

        # validate with nested template
        res_prop = t['resources']['my_resource_group']['properties']
        res_prop['resource_def']['type'] = 'nova_server.yaml'
        files = {'nova_server.yaml': nova_server_template}
        tmpl = templatem.Template(t, files=files)
        self._test_validate_unknown_resource_type(stack_name, tmpl,
                                                  'my_resource_group')

    def test_validate_heat_autoscaling_group(self):
        # Autoscaling validation is a nested stack validation
        stack_name = 'validate_heat_autoscaling_group_template'
        t = template_format.parse(heat_autoscaling_group_template)
        tmpl = templatem.Template(t)
        self._test_validate_unknown_resource_type(stack_name, tmpl,
                                                  'my_autoscaling_group')

        # validate with nested template
        res_prop = t['resources']['my_autoscaling_group']['properties']
        res_prop['resource']['type'] = 'nova_server.yaml'
        files = {'nova_server.yaml': nova_server_template}
        tmpl = templatem.Template(t, files=files)
        self._test_validate_unknown_resource_type(stack_name, tmpl,
                                                  'my_autoscaling_group')

    def test__validate_nested_resources_checks_num_of_resources(self):
        stack_resource.cfg.CONF.set_override('max_resources_per_stack', 2)
        tmpl = {'HeatTemplateFormatVersion': '2012-12-12',
                'Resources': [1]}
        template = stack_resource.template.Template(tmpl)
        root_resources = mock.Mock(return_value=2)
        self.parent_resource.stack.total_resources = root_resources

        self.assertRaises(exception.RequestLimitExceeded,
                          self.parent_resource._validate_nested_resources,
                          template)

    def test_load_nested_ok(self):
        self.parent_resource._nested = None
        self.parent_resource.resource_id = 319
        self.m.StubOutWithMock(parser.Stack, 'load')
        parser.Stack.load(self.parent_resource.context,
                          self.parent_resource.resource_id,
                          show_deleted=False,
                          force_reload=False).AndReturn('s')
        self.m.ReplayAll()
        self.parent_resource.nested()
        self.m.VerifyAll()

    def test_load_nested_force_reload(self):
        self.parent_resource._nested = 'write-over-me'
        self.parent_resource.resource_id = 319
        self.m.StubOutWithMock(parser.Stack, 'load')
        parser.Stack.load(self.parent_resource.context,
                          self.parent_resource.resource_id,
                          show_deleted=False,
                          force_reload=True).AndReturn('ok')
        self.m.ReplayAll()
        self.parent_resource.nested(force_reload=True)
        self.assertEqual('ok', self.parent_resource._nested)
        self.m.VerifyAll()

    def test_load_nested_non_exist(self):
        self.parent_resource._nested = None
        self.parent_resource.resource_id = '90-8'
        self.m.StubOutWithMock(parser.Stack, 'load')
        parser.Stack.load(self.parent_resource.context,
                          self.parent_resource.resource_id,
                          show_deleted=False,
                          force_reload=False).AndRaise(
            exception.NotFound)
        self.m.ReplayAll()

        self.assertIsNone(self.parent_resource.nested())
        self.m.VerifyAll()

    def test_load_nested_cached(self):
        self.parent_resource._nested = 'gotthis'
        self.assertEqual('gotthis', self.parent_resource.nested())

    def test_load_nested_force_reload_ok(self):
        self.parent_resource._nested = mock.MagicMock()
        self.parent_resource.resource_id = '90-8'
        self.m.StubOutWithMock(parser.Stack, 'load')
        parser.Stack.load(self.parent_resource.context,
                          self.parent_resource.resource_id,
                          show_deleted=False,
                          force_reload=True).AndReturn('s')
        self.m.ReplayAll()
        st = self.parent_resource.nested(force_reload=True)
        self.assertEqual('s', st)
        self.m.VerifyAll()

    def test_load_nested_force_reload_none(self):
        self.parent_resource._nested = mock.MagicMock()
        self.parent_resource.resource_id = '90-8'
        self.m.StubOutWithMock(parser.Stack, 'load')
        parser.Stack.load(self.parent_resource.context,
                          self.parent_resource.resource_id,
                          show_deleted=False,
                          force_reload=True).AndRaise(
            exception.NotFound)
        self.m.ReplayAll()
        self.assertIsNone(self.parent_resource.nested(force_reload=True))
        self.m.VerifyAll()

    def test_delete_nested_none_nested_stack(self):
        self.parent_resource._nested = None
        self.assertIsNone(self.parent_resource.delete_nested())

    def test_delete_nested_not_found_nested_stack(self):
        self.parent_resource._nested = mock.MagicMock()
        rpcc = mock.Mock()
        self.parent_resource.rpc_client = rpcc
        rpcc.return_value.delete_stack = mock.Mock(
            side_effect=exception.NotFound())
        self.assertIsNone(self.parent_resource.delete_nested())
        rpcc.return_value.delete_stack.assert_called_once_with(
            self.parent_resource.context, mock.ANY)

    def test_need_update_for_nested_resource(self):
        """
        The resource in Create or Update state and has nested stack,
        should need update.
        """
        self.parent_resource.action = self.parent_resource.CREATE
        need_update = self.parent_resource._needs_update(
            self.parent_resource.t,
            self.parent_resource.t,
            self.parent_resource.properties,
            self.parent_resource.properties,
            self.parent_resource)

        self.assertEqual(True, need_update)

    def test_need_update_in_failed_state_for_nested_resource(self):
        """
        The resource in failed state and has no nested stack,
        should need update with UpdateReplace.
        """
        self.parent_resource.state_set(self.parent_resource.INIT,
                                       self.parent_resource.FAILED)
        self.parent_resource._nested = None
        self.assertRaises(resource.UpdateReplace,
                          self.parent_resource._needs_update,
                          self.parent_resource.t,
                          self.parent_resource.t,
                          self.parent_resource.properties,
                          self.parent_resource.properties,
                          self.parent_resource)

    def test_need_update_in_init_complete_state_for_nested_resource(self):
        """
        The resource in failed state and has no nested stack,
        should need update with UpdateReplace.
        """
        self.parent_resource.state_set(self.parent_resource.INIT,
                                       self.parent_resource.COMPLETE)
        self.parent_resource._nested = None
        self.assertRaises(resource.UpdateReplace,
                          self.parent_resource._needs_update,
                          self.parent_resource.t,
                          self.parent_resource.t,
                          self.parent_resource.properties,
                          self.parent_resource.properties,
                          self.parent_resource)


class StackResourceLimitTest(StackResourceBaseTest):
    scenarios = [
        ('3_4_0', dict(root=3, templ=4, nested=0, max=10, error=False)),
        ('3_8_0', dict(root=3, templ=8, nested=0, max=10, error=True)),
        ('3_8_2', dict(root=3, templ=8, nested=2, max=10, error=True)),
        ('3_5_2', dict(root=3, templ=5, nested=2, max=10, error=False)),
        ('3_6_2', dict(root=3, templ=6, nested=2, max=10, error=True)),
        ('3_12_2', dict(root=3, templ=12, nested=2, max=10, error=True))]

    def setUp(self):
        super(StackResourceLimitTest, self).setUp()
        self.res = self.parent_resource

    def test_resource_limit(self):
        # mock root total_resources
        total_resources = self.root + self.nested
        parser.Stack.total_resources = mock.Mock(return_value=total_resources)

        # setup the config max
        cfg.CONF.set_default('max_resources_per_stack', self.max)

        # fake the template
        templ = mock.MagicMock()
        templ.__getitem__.return_value = range(self.templ)
        templ.RESOURCES = 'Resources'
        if self.error:
            self.assertRaises(exception.RequestLimitExceeded,
                              self.res._validate_nested_resources, templ)
        else:
            self.assertIsNone(self.res._validate_nested_resources(templ))


class StackResourceAttrTest(StackResourceBaseTest):
    def test_get_output_ok(self):
        nested = self.m.CreateMockAnything()
        self.m.StubOutWithMock(stack_resource.StackResource, 'nested')
        stack_resource.StackResource.nested().AndReturn(nested)
        nested.outputs = {"key": "value"}
        nested.output('key').AndReturn("value")
        self.m.ReplayAll()

        self.assertEqual("value", self.parent_resource.get_output("key"))

        self.m.VerifyAll()

    def test_get_output_key_not_found(self):
        nested = self.m.CreateMockAnything()
        self.m.StubOutWithMock(stack_resource.StackResource, 'nested')
        stack_resource.StackResource.nested().AndReturn(nested)
        nested.outputs = {}
        self.m.ReplayAll()

        self.assertRaises(exception.InvalidTemplateAttribute,
                          self.parent_resource.get_output,
                          "key")

        self.m.VerifyAll()

    def test_resolve_attribute_string(self):
        nested = self.m.CreateMockAnything()
        self.m.StubOutWithMock(stack_resource.StackResource, 'nested')
        stack_resource.StackResource.nested().AndReturn(nested)
        nested.outputs = {'key': 'value'}
        nested.output('key').AndReturn('value')
        self.m.ReplayAll()

        self.assertEqual('value',
                         self.parent_resource._resolve_attribute("key"))

        self.m.VerifyAll()

    def test_resolve_attribute_dict(self):
        nested = self.m.CreateMockAnything()
        self.m.StubOutWithMock(stack_resource.StackResource, 'nested')
        stack_resource.StackResource.nested().AndReturn(nested)
        nested.outputs = {'key': {'a': 1, 'b': 2}}
        nested.output('key').AndReturn({'a': 1, 'b': 2})
        self.m.ReplayAll()

        self.assertEqual({'a': 1, 'b': 2},
                         self.parent_resource._resolve_attribute("key"))

        self.m.VerifyAll()

    def test_resolve_attribute_list(self):
        nested = self.m.CreateMockAnything()
        self.m.StubOutWithMock(stack_resource.StackResource, 'nested')
        stack_resource.StackResource.nested().AndReturn(nested)
        nested.outputs = {"key": [1, 2, 3]}
        nested.output('key').AndReturn([1, 2, 3])
        self.m.ReplayAll()

        self.assertEqual([1, 2, 3],
                         self.parent_resource._resolve_attribute("key"))

        self.m.VerifyAll()

    def test_validate_nested_stack(self):
        self.parent_resource.child_template = mock.Mock(return_value='foo')
        self.parent_resource.child_params = mock.Mock(return_value={})
        nested = self.m.CreateMockAnything()
        nested.validate().AndReturn(True)
        self.m.StubOutWithMock(stack_resource.StackResource,
                               '_parse_nested_stack')
        name = '%s-%s' % (self.parent_stack.name, self.parent_resource.name)
        stack_resource.StackResource._parse_nested_stack(
            name, 'foo', {}).AndReturn(nested)

        self.m.ReplayAll()
        self.parent_resource.validate_nested_stack()
        self.assertFalse(nested.strict_validate)
        self.m.VerifyAll()

    def test_validate_assertion_exception_rethrow(self):
        expected_message = 'Expected Assertion Error'
        self.parent_resource.child_template = mock.Mock(return_value='foo')
        self.parent_resource.child_params = mock.Mock(return_value={})
        self.m.StubOutWithMock(stack_resource.StackResource,
                               '_parse_nested_stack')
        name = '%s-%s' % (self.parent_stack.name, self.parent_resource.name)
        stack_resource.StackResource._parse_nested_stack(
            name, 'foo', {}).AndRaise(AssertionError(expected_message))

        self.m.ReplayAll()
        exc = self.assertRaises(AssertionError,
                                self.parent_resource.validate_nested_stack)
        self.assertEqual(expected_message, six.text_type(exc))
        self.m.VerifyAll()


class StackResourceCheckCompleteTest(StackResourceBaseTest):
    scenarios = [
        ('create', dict(action='create', show_deleted=False)),
        ('update', dict(action='update', show_deleted=False)),
        ('suspend', dict(action='suspend', show_deleted=False)),
        ('resume', dict(action='resume', show_deleted=False)),
        ('delete', dict(action='delete', show_deleted=True)),
    ]

    def setUp(self):
        super(StackResourceCheckCompleteTest, self).setUp()
        self.nested = mock.MagicMock()
        self.nested.name = 'nested-stack'
        self.parent_resource.nested = mock.MagicMock(return_value=self.nested)
        self.parent_resource._nested = self.nested
        setattr(self.nested, self.action.upper(), self.action.upper())
        self.nested.action = self.action.upper()
        self.nested.COMPLETE = 'COMPLETE'

    def test_state_ok(self):
        """
        check_create_complete should return True create task is
        done and the nested stack is in (<action>,COMPLETE) state.
        """
        self.nested.status = 'COMPLETE'
        complete = getattr(self.parent_resource,
                           'check_%s_complete' % self.action)
        self.assertIs(True, complete(None))
        self.parent_resource.nested.assert_called_once_with(
            show_deleted=self.show_deleted, force_reload=True)

    def test_state_err(self):
        """
        check_create_complete should raise error when create task is
        done but the nested stack is not in (<action>,COMPLETE) state
        """
        self.nested.status = 'FAILED'
        reason = ('Resource %s failed: ValueError: '
                  'resources.%s: broken on purpose' % (
                      self.action.upper(),
                      'child_res'))
        exp_path = 'resources.test.resources.child_res'
        exp = 'ValueError: %s: broken on purpose' % exp_path
        self.nested.status_reason = reason
        complete = getattr(self.parent_resource,
                           'check_%s_complete' % self.action)
        exc = self.assertRaises(exception.ResourceFailure, complete, None)
        self.assertEqual(exp, six.text_type(exc))
        self.parent_resource.nested.assert_called_once_with(
            show_deleted=self.show_deleted, force_reload=True)

    def test_state_unknown(self):
        """
        check_create_complete should raise error when create task is
        done but the nested stack is not in (<action>,COMPLETE) state
        """
        self.nested.status = 'WTF'
        self.nested.status_reason = 'broken on purpose'
        complete = getattr(self.parent_resource,
                           'check_%s_complete' % self.action)
        self.assertRaises(resource.ResourceUnknownStatus, complete, None)
        self.parent_resource.nested.assert_called_once_with(
            show_deleted=self.show_deleted, force_reload=True)

    def test_in_progress(self):
        self.nested.status = 'IN_PROGRESS'
        complete = getattr(self.parent_resource,
                           'check_%s_complete' % self.action)
        self.assertFalse(complete(None))
        self.parent_resource.nested.assert_called_once_with(
            show_deleted=self.show_deleted, force_reload=True)

    def test_update_not_started(self):
        if self.action != 'update':
            # only valid for updates at the moment.
            return

        self.nested.status = 'COMPLETE'
        self.nested.state = ('UPDATE', 'COMPLETE')
        self.nested.updated_time = 'test'
        cookie = {'previous': {'state': ('UPDATE', 'COMPLETE'),
                               'updated_at': 'test'}}

        complete = getattr(self.parent_resource,
                           'check_%s_complete' % self.action)

        self.assertFalse(complete(cookie=cookie))
        self.parent_resource.nested.assert_called_once_with(
            show_deleted=self.show_deleted, force_reload=True)

    def test_wrong_action(self):
        self.nested.action = 'COMPLETE'
        complete = getattr(self.parent_resource,
                           'check_%s_complete' % self.action)
        self.assertFalse(complete(None))
        self.parent_resource.nested.assert_called_once_with(
            show_deleted=self.show_deleted, force_reload=True)


class WithTemplateTest(StackResourceBaseTest):

    scenarios = [
        ('basic', dict(params={}, timeout_mins=None, adopt_data=None)),
        ('params', dict(params={'foo': 'fee'},
                        timeout_mins=None, adopt_data=None)),
        ('timeout', dict(params={}, timeout_mins=53, adopt_data=None)),
        ('adopt', dict(params={}, timeout_mins=None,
                       adopt_data={'template': 'foo', 'environment': 'eee'})),
    ]

    def test_create_with_template(self):
        child_env = {'parameter_defaults': {},
                     'parameters': self.params,
                     'resource_registry': {'resources': {}},
                     'encrypted_param_names': []}
        self.parent_resource.child_params = mock.Mock(
            return_value=self.params)
        res_name = self.parent_resource.physical_resource_name()
        rpcc = mock.Mock()
        self.parent_resource.rpc_client = rpcc
        rpcc.return_value._create_stack.return_value = {'stack_id': 'pancakes'}
        self.parent_resource.create_with_template(
            self.empty_temp, user_params=self.params,
            timeout_mins=self.timeout_mins, adopt_data=self.adopt_data)
        adopt_data_str = None
        if self.adopt_data:
            adopt_data_str = json.dumps(self.adopt_data)
        rpcc.return_value._create_stack.assert_called_once_with(
            self.ctx, res_name, self.empty_temp.t, child_env, {},
            {'disable_rollback': True,
             'adopt_stack_data': adopt_data_str,
             'timeout_mins': self.timeout_mins},
            stack_user_project_id='aprojectid',
            parent_resource_name='test',
            user_creds_id='uc123',
            owner_id=self.parent_stack.id,
            nested_depth=1)

    def test_update_with_template(self):
        nested = mock.MagicMock()
        nested.updated_time = 'now_time'
        nested.state = ('CREATE', 'COMPLETE')
        nested.identifier.return_value = 'stack_identifier'
        self.parent_resource.nested = mock.MagicMock(return_value=nested)
        self.parent_resource._nested = nested

        child_env = {'parameter_defaults': {},
                     'parameters': self.params,
                     'resource_registry': {'resources': {}},
                     'encrypted_param_names': []}
        self.parent_resource.child_params = mock.Mock(
            return_value=self.params)
        rpcc = mock.Mock()
        self.parent_resource.rpc_client = rpcc
        rpcc.return_value._create_stack.return_value = {'stack_id': 'pancakes'}
        self.parent_resource.update_with_template(
            self.empty_temp, user_params=self.params,
            timeout_mins=self.timeout_mins)
        rpcc.return_value.update_stack.assert_called_once_with(
            self.ctx, 'stack_identifier', self.empty_temp.t,
            child_env, {}, {'timeout_mins': self.timeout_mins})


class RaiseLocalException(StackResourceBaseTest):

    def test_heat_exception(self):
        local = exception.InvalidResourceType(message='test')
        self.assertRaises(exception.InvalidResourceType,
                          self.parent_resource.raise_local_exception, local)

    def test_messaging_timeout(self):
        local = msg_exceptions.MessagingTimeout('took too long')
        self.assertRaises(msg_exceptions.MessagingTimeout,
                          self.parent_resource.raise_local_exception, local)

    def test_remote_heat_ex(self):
        class InvalidResourceType_Remote(exception.InvalidResourceType):
            pass

        local = InvalidResourceType_Remote(message='test')
        self.assertRaises(exception.ResourceFailure,
                          self.parent_resource.raise_local_exception, local)
