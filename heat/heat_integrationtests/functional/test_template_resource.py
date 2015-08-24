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

import yaml

from heat_integrationtests.common import test
from heat_integrationtests.functional import functional_base


class TemplateResourceTest(functional_base.FunctionalTestsBase):
    """Prove that we can use the registry in a nested provider."""

    template = '''
heat_template_version: 2013-05-23
resources:
  secret1:
    type: OS::Heat::RandomString
outputs:
  secret-out:
    value: { get_attr: [secret1, value] }
'''
    nested_templ = '''
heat_template_version: 2013-05-23
resources:
  secret2:
    type: OS::Heat::RandomString
outputs:
  value:
    value: { get_attr: [secret2, value] }
'''

    env_templ = '''
resource_registry:
  "OS::Heat::RandomString": nested.yaml
'''

    def setUp(self):
        super(TemplateResourceTest, self).setUp()

    def test_nested_env(self):
        main_templ = '''
heat_template_version: 2013-05-23
resources:
  secret1:
    type: My::NestedSecret
outputs:
  secret-out:
    value: { get_attr: [secret1, value] }
'''

        nested_templ = '''
heat_template_version: 2013-05-23
resources:
  secret2:
    type: My::Secret
outputs:
  value:
    value: { get_attr: [secret2, value] }
'''

        env_templ = '''
resource_registry:
  "My::Secret": "OS::Heat::RandomString"
  "My::NestedSecret": nested.yaml
'''

        stack_identifier = self.stack_create(
            template=main_templ,
            files={'nested.yaml': nested_templ},
            environment=env_templ)
        nested_ident = self.assert_resource_is_a_stack(stack_identifier,
                                                       'secret1')
        # prove that resource.parent_resource is populated.
        sec2 = self.client.resources.get(nested_ident, 'secret2')
        self.assertEqual('secret1', sec2.parent_resource)

    def test_no_infinite_recursion(self):
        """Prove that we can override a python resource.

        And use that resource within the template resource.
        """
        stack_identifier = self.stack_create(
            template=self.template,
            files={'nested.yaml': self.nested_templ},
            environment=self.env_templ)
        self.assert_resource_is_a_stack(stack_identifier, 'secret1')

    def test_nested_stack_delete_then_delete_parent_stack(self):
        """Check the robustness of stack deletion.

        This tests that if you manually delete a nested
        stack, the parent stack is still deletable.
        """
        # disable cleanup so we can call _stack_delete() directly.
        stack_identifier = self.stack_create(
            template=self.template,
            files={'nested.yaml': self.nested_templ},
            environment=self.env_templ,
            enable_cleanup=False)

        nested_ident = self.assert_resource_is_a_stack(stack_identifier,
                                                       'secret1')

        self._stack_delete(nested_ident)
        self._stack_delete(stack_identifier)

    def test_change_in_file_path(self):
        stack_identifier = self.stack_create(
            template=self.template,
            files={'nested.yaml': self.nested_templ},
            environment=self.env_templ)
        stack = self.client.stacks.get(stack_identifier)
        secret_out1 = self._stack_output(stack, 'secret-out')

        nested_templ_2 = '''
heat_template_version: 2013-05-23
resources:
  secret2:
    type: OS::Heat::RandomString
outputs:
  value:
    value: freddy
'''
        env_templ_2 = '''
resource_registry:
  "OS::Heat::RandomString": new/nested.yaml
'''
        self.update_stack(stack_identifier,
                          template=self.template,
                          files={'new/nested.yaml': nested_templ_2},
                          environment=env_templ_2)
        stack = self.client.stacks.get(stack_identifier)
        secret_out2 = self._stack_output(stack, 'secret-out')
        self.assertNotEqual(secret_out1, secret_out2)
        self.assertEqual('freddy', secret_out2)


class NestedAttributesTest(functional_base.FunctionalTestsBase):
    """Prove that we can use the template resource references."""

    main_templ = '''
heat_template_version: 2014-10-16
resources:
  secret2:
    type: My::NestedSecret
outputs:
  old_way:
    value: { get_attr: [secret2, nested_str]}
  test_attr1:
    value: { get_attr: [secret2, resource.secret1, value]}
  test_attr2:
    value: { get_attr: [secret2, resource.secret1.value]}
  test_ref:
    value: { get_resource: secret2 }
'''

    env_templ = '''
resource_registry:
  "My::NestedSecret": nested.yaml
'''

    def setUp(self):
        super(NestedAttributesTest, self).setUp()

    def test_stack_ref(self):
        nested_templ = '''
heat_template_version: 2014-10-16
resources:
  secret1:
    type: OS::Heat::RandomString
outputs:
  nested_str:
    value: {get_attr: [secret1, value]}
'''
        stack_identifier = self.stack_create(
            template=self.main_templ,
            files={'nested.yaml': nested_templ},
            environment=self.env_templ)
        self.assert_resource_is_a_stack(stack_identifier, 'secret2')
        stack = self.client.stacks.get(stack_identifier)
        test_ref = self._stack_output(stack, 'test_ref')
        self.assertIn('arn:openstack:heat:', test_ref)

    def test_transparent_ref(self):
        """With the addition of OS::stack_id we can now use the nested resource
        more transparently.
        """
        nested_templ = '''
heat_template_version: 2014-10-16
resources:
  secret1:
    type: OS::Heat::RandomString
outputs:
  OS::stack_id:
    value: {get_resource: secret1}
  nested_str:
    value: {get_attr: [secret1, value]}
'''
        stack_identifier = self.stack_create(
            template=self.main_templ,
            files={'nested.yaml': nested_templ},
            environment=self.env_templ)
        self.assert_resource_is_a_stack(stack_identifier, 'secret2')
        stack = self.client.stacks.get(stack_identifier)
        test_ref = self._stack_output(stack, 'test_ref')
        test_attr = self._stack_output(stack, 'old_way')

        self.assertNotIn('arn:openstack:heat', test_ref)
        self.assertEqual(test_attr, test_ref)

    def test_nested_attributes(self):
        nested_templ = '''
heat_template_version: 2014-10-16
resources:
  secret1:
    type: OS::Heat::RandomString
outputs:
  nested_str:
    value: {get_attr: [secret1, value]}
'''
        stack_identifier = self.stack_create(
            template=self.main_templ,
            files={'nested.yaml': nested_templ},
            environment=self.env_templ)
        self.assert_resource_is_a_stack(stack_identifier, 'secret2')
        stack = self.client.stacks.get(stack_identifier)
        old_way = self._stack_output(stack, 'old_way')
        test_attr1 = self._stack_output(stack, 'test_attr1')
        test_attr2 = self._stack_output(stack, 'test_attr2')

        self.assertEqual(old_way, test_attr1)
        self.assertEqual(old_way, test_attr2)


class TemplateResourceUpdateTest(functional_base.FunctionalTestsBase):
    """Prove that we can do template resource updates."""

    main_template = '''
HeatTemplateFormatVersion: '2012-12-12'
Resources:
  the_nested:
    Type: the.yaml
    Properties:
      one: my_name
      two: your_name
Outputs:
  identifier:
    Value: {Ref: the_nested}
  value:
    Value: {'Fn::GetAtt': [the_nested, the_str]}
'''

    main_template_change_prop = '''
HeatTemplateFormatVersion: '2012-12-12'
Resources:
  the_nested:
    Type: the.yaml
    Properties:
      one: updated_name
      two: your_name

Outputs:
  identifier:
    Value: {Ref: the_nested}
  value:
    Value: {'Fn::GetAtt': [the_nested, the_str]}
'''

    main_template_add_prop = '''
HeatTemplateFormatVersion: '2012-12-12'
Resources:
  the_nested:
    Type: the.yaml
    Properties:
      one: my_name
      two: your_name
      three: third_name

Outputs:
  identifier:
    Value: {Ref: the_nested}
  value:
    Value: {'Fn::GetAtt': [the_nested, the_str]}
'''

    main_template_remove_prop = '''
HeatTemplateFormatVersion: '2012-12-12'
Resources:
  the_nested:
    Type: the.yaml
    Properties:
      one: my_name

Outputs:
  identifier:
    Value: {Ref: the_nested}
  value:
    Value: {'Fn::GetAtt': [the_nested, the_str]}
'''

    initial_tmpl = '''
HeatTemplateFormatVersion: '2012-12-12'
Parameters:
  one:
    Default: foo
    Type: String
  two:
    Default: bar
    Type: String

Resources:
  NestedResource:
    Type: OS::Heat::RandomString
    Properties:
      salt: {Ref: one}
Outputs:
  the_str:
    Value: {'Fn::GetAtt': [NestedResource, value]}
'''

    prop_change_tmpl = '''
HeatTemplateFormatVersion: '2012-12-12'
Parameters:
  one:
    Default: yikes
    Type: String
  two:
    Default: foo
    Type: String
Resources:
  NestedResource:
    Type: OS::Heat::RandomString
    Properties:
      salt: {Ref: two}
Outputs:
  the_str:
    Value: {'Fn::GetAtt': [NestedResource, value]}
'''

    prop_add_tmpl = '''
HeatTemplateFormatVersion: '2012-12-12'
Parameters:
  one:
    Default: yikes
    Type: String
  two:
    Default: foo
    Type: String
  three:
    Default: bar
    Type: String

Resources:
  NestedResource:
    Type: OS::Heat::RandomString
    Properties:
      salt: {Ref: three}
Outputs:
  the_str:
    Value: {'Fn::GetAtt': [NestedResource, value]}
'''

    prop_remove_tmpl = '''
HeatTemplateFormatVersion: '2012-12-12'
Parameters:
  one:
    Default: yikes
    Type: String

Resources:
  NestedResource:
    Type: OS::Heat::RandomString
    Properties:
      salt: {Ref: one}
Outputs:
  the_str:
    Value: {'Fn::GetAtt': [NestedResource, value]}
'''

    attr_change_tmpl = '''
HeatTemplateFormatVersion: '2012-12-12'
Parameters:
  one:
    Default: foo
    Type: String
  two:
    Default: bar
    Type: String

Resources:
  NestedResource:
    Type: OS::Heat::RandomString
    Properties:
      salt: {Ref: one}
Outputs:
  the_str:
    Value: {'Fn::GetAtt': [NestedResource, value]}
  something_else:
    Value: just_a_string
'''

    content_change_tmpl = '''
HeatTemplateFormatVersion: '2012-12-12'
Parameters:
  one:
    Default: foo
    Type: String
  two:
    Default: bar
    Type: String

Resources:
  NestedResource:
    Type: OS::Heat::RandomString
    Properties:
      salt: yum
Outputs:
  the_str:
    Value: {'Fn::GetAtt': [NestedResource, value]}
'''

    EXPECTED = (UPDATE, NOCHANGE) = ('update', 'nochange')
    scenarios = [
        ('no_changes', dict(template=main_template,
                            provider=initial_tmpl,
                            expect=NOCHANGE)),
        ('main_tmpl_change', dict(template=main_template_change_prop,
                                  provider=initial_tmpl,
                                  expect=UPDATE)),
        ('provider_change', dict(template=main_template,
                                 provider=content_change_tmpl,
                                 expect=UPDATE)),
        ('provider_props_change', dict(template=main_template,
                                       provider=prop_change_tmpl,
                                       expect=UPDATE)),
        ('provider_props_add', dict(template=main_template_add_prop,
                                    provider=prop_add_tmpl,
                                    expect=UPDATE)),
        ('provider_props_remove', dict(template=main_template_remove_prop,
                                       provider=prop_remove_tmpl,
                                       expect=NOCHANGE)),
        ('provider_attr_change', dict(template=main_template,
                                      provider=attr_change_tmpl,
                                      expect=NOCHANGE)),
    ]

    def setUp(self):
        super(TemplateResourceUpdateTest, self).setUp()

    def test_template_resource_update_template_schema(self):
        stack_identifier = self.stack_create(
            template=self.main_template,
            files={'the.yaml': self.initial_tmpl})
        stack = self.client.stacks.get(stack_identifier)
        initial_id = self._stack_output(stack, 'identifier')
        initial_val = self._stack_output(stack, 'value')

        self.update_stack(stack_identifier,
                          self.template,
                          files={'the.yaml': self.provider})
        stack = self.client.stacks.get(stack_identifier)
        self.assertEqual(initial_id,
                         self._stack_output(stack, 'identifier'))
        if self.expect == self.NOCHANGE:
            self.assertEqual(initial_val,
                             self._stack_output(stack, 'value'))
        else:
            self.assertNotEqual(initial_val,
                                self._stack_output(stack, 'value'))


class TemplateResourceUpdateFailedTest(functional_base.FunctionalTestsBase):
    """Prove that we can do updates on a nested stack to fix a stack."""
    main_template = '''
HeatTemplateFormatVersion: '2012-12-12'
Resources:
  keypair:
    Type: OS::Nova::KeyPair
    Properties:
      name: replace-this
      save_private_key: false
  server:
    Type: server_fail.yaml
    DependsOn: keypair
'''
    nested_templ = '''
HeatTemplateFormatVersion: '2012-12-12'
Resources:
  RealRandom:
    Type: OS::Heat::RandomString
'''

    def setUp(self):
        super(TemplateResourceUpdateFailedTest, self).setUp()
        self.assign_keypair()

    def test_update_on_failed_create(self):
        # create a stack with "server" dependent on "keypair", but
        # keypair fails, so "server" is not created properly.
        # We then fix the template and it should succeed.
        broken_templ = self.main_template.replace('replace-this',
                                                  self.keypair_name)
        stack_identifier = self.stack_create(
            template=broken_templ,
            files={'server_fail.yaml': self.nested_templ},
            expected_status='CREATE_FAILED')

        fixed_templ = self.main_template.replace('replace-this',
                                                 test.rand_name())
        self.update_stack(stack_identifier,
                          fixed_templ,
                          files={'server_fail.yaml': self.nested_templ})


class TemplateResourceAdoptTest(functional_base.FunctionalTestsBase):
    """Prove that we can do template resource adopt/abandon."""

    main_template = '''
HeatTemplateFormatVersion: '2012-12-12'
Resources:
  the_nested:
    Type: the.yaml
    Properties:
      one: my_name
Outputs:
  identifier:
    Value: {Ref: the_nested}
  value:
    Value: {'Fn::GetAtt': [the_nested, the_str]}
'''

    nested_templ = '''
HeatTemplateFormatVersion: '2012-12-12'
Parameters:
  one:
    Default: foo
    Type: String
Resources:
  RealRandom:
    Type: OS::Heat::RandomString
    Properties:
      salt: {Ref: one}
Outputs:
  the_str:
    Value: {'Fn::GetAtt': [RealRandom, value]}
'''

    def setUp(self):
        super(TemplateResourceAdoptTest, self).setUp()

    def _yaml_to_json(self, yaml_templ):
        return yaml.load(yaml_templ)

    def test_abandon(self):
        stack_identifier = self.stack_create(
            template=self.main_template,
            files={'the.yaml': self.nested_templ},
            enable_cleanup=False
        )

        info = self.stack_abandon(stack_id=stack_identifier)
        self.assertEqual(self._yaml_to_json(self.main_template),
                         info['template'])
        self.assertEqual(self._yaml_to_json(self.nested_templ),
                         info['resources']['the_nested']['template'])

    def test_adopt(self):
        data = {
            'resources': {
                'the_nested': {
                    "type": "the.yaml",
                    "resources": {
                        "RealRandom": {
                            "type": "OS::Heat::RandomString",
                            'resource_data': {'value': 'goopie'},
                            'resource_id': 'froggy'
                        }
                    }
                }
            },
            "environment": {"parameters": {}},
            "template": yaml.load(self.main_template)
        }

        stack_identifier = self.stack_adopt(
            adopt_data=json.dumps(data),
            files={'the.yaml': self.nested_templ})

        self.assert_resource_is_a_stack(stack_identifier, 'the_nested')
        stack = self.client.stacks.get(stack_identifier)
        self.assertEqual('goopie', self._stack_output(stack, 'value'))


class TemplateResourceCheckTest(functional_base.FunctionalTestsBase):
    """Prove that we can do template resource check."""

    main_template = '''
HeatTemplateFormatVersion: '2012-12-12'
Resources:
  the_nested:
    Type: the.yaml
    Properties:
      one: my_name
Outputs:
  identifier:
    Value: {Ref: the_nested}
  value:
    Value: {'Fn::GetAtt': [the_nested, the_str]}
'''

    nested_templ = '''
HeatTemplateFormatVersion: '2012-12-12'
Parameters:
  one:
    Default: foo
    Type: String
Resources:
  RealRandom:
    Type: OS::Heat::RandomString
    Properties:
      salt: {Ref: one}
Outputs:
  the_str:
    Value: {'Fn::GetAtt': [RealRandom, value]}
'''

    def setUp(self):
        super(TemplateResourceCheckTest, self).setUp()

    def test_check(self):
        stack_identifier = self.stack_create(
            template=self.main_template,
            files={'the.yaml': self.nested_templ}
        )

        self.client.actions.check(stack_id=stack_identifier)
        self._wait_for_stack_status(stack_identifier, 'CHECK_COMPLETE')


class TemplateResourceErrorMessageTest(functional_base.FunctionalTestsBase):
    """Prove that nested stack errors don't suck."""
    template = '''
HeatTemplateFormatVersion: '2012-12-12'
Resources:
  victim:
    Type: fail.yaml
'''
    nested_templ = '''
HeatTemplateFormatVersion: '2012-12-12'
Resources:
  oops:
    Type: OS::Heat::TestResource
    Properties:
      fail: true
      wait_secs: 2
'''

    def setUp(self):
        super(TemplateResourceErrorMessageTest, self).setUp()

    def test_fail(self):
        stack_identifier = self.stack_create(
            template=self.template,
            files={'fail.yaml': self.nested_templ},
            expected_status='CREATE_FAILED')
        stack = self.client.stacks.get(stack_identifier)

        exp_path = 'resources.victim.resources.oops'
        exp_msg = 'Test Resource failed oops'
        exp = 'Resource CREATE failed: ValueError: %s: %s' % (exp_path,
                                                              exp_msg)
        self.assertEqual(exp, stack.stack_status_reason)


class TemplateResourceSuspendResumeTest(functional_base.FunctionalTestsBase):
    """Prove that we can do template resource suspend/resume."""

    main_template = '''
heat_template_version: 2014-10-16
parameters:
resources:
  the_nested:
    type: the.yaml
'''

    nested_templ = '''
heat_template_version: 2014-10-16
resources:
  test_random_string:
    type: OS::Heat::RandomString
'''

    def setUp(self):
        super(TemplateResourceSuspendResumeTest, self).setUp()

    def test_suspend_resume(self):
        """Basic test for template resource suspend resume"""
        stack_identifier = self.stack_create(
            template=self.main_template,
            files={'the.yaml': self.nested_templ}
        )

        self.stack_suspend(stack_identifier=stack_identifier)
        self.stack_resume(stack_identifier=stack_identifier)
