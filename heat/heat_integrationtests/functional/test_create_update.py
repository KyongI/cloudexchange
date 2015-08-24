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
import json

from heat_integrationtests.functional import functional_base

test_template_one_resource = {
    'heat_template_version': '2013-05-23',
    'description': 'Test template to create one instance.',
    'resources': {
        'test1': {
            'type': 'OS::Heat::TestResource',
            'properties': {
                'value': 'Test1',
                'fail': False,
                'update_replace': False,
                'wait_secs': 0
            }
        }
    }
}

test_template_two_resource = {
    'heat_template_version': '2013-05-23',
    'description': 'Test template to create two instance.',
    'resources': {
        'test1': {
            'type': 'OS::Heat::TestResource',
            'properties': {
                'value': 'Test1',
                'fail': False,
                'update_replace': False,
                'wait_secs': 0
            }
        },
        'test2': {
            'type': 'OS::Heat::TestResource',
            'properties': {
                'value': 'Test1',
                'fail': False,
                'update_replace': False,
                'wait_secs': 0
            }
        }
    }
}


def _change_rsrc_properties(template, rsrcs, values):
        modified_template = copy.deepcopy(template)
        for rsrc_name in rsrcs:
            rsrc_prop = modified_template['resources'][
                rsrc_name]['properties']
            for prop in rsrc_prop:
                if prop in values:
                    rsrc_prop[prop] = values[prop]
        return modified_template


class CreateStackTest(functional_base.FunctionalTestsBase):
    def setUp(self):
        super(CreateStackTest, self).setUp()

    def test_create_rollback(self):
        values = {'fail': True, 'value': 'test_create_rollback'}
        template = _change_rsrc_properties(test_template_one_resource,
                                           ['test1'], values)

        self.stack_create(
            template=template,
            expected_status='ROLLBACK_COMPLETE',
            disable_rollback=False)


class UpdateStackTest(functional_base.FunctionalTestsBase):

    provider_template = {
        'heat_template_version': '2013-05-23',
        'description': 'foo',
        'resources': {
            'test1': {
                'type': 'My::TestResource'
            }
        }
    }

    provider_group_template = '''
heat_template_version: 2013-05-23
resources:
  test_group:
    type: OS::Heat::ResourceGroup
    properties:
      count: 2
      resource_def:
        type: My::TestResource
'''

    update_userdata_template = '''
heat_template_version: 2014-10-16
parameters:
  flavor:
    type: string
  user_data:
    type: string
  image:
    type: string
  network:
    type: string

resources:
  server:
    type: OS::Nova::Server
    properties:
      image: {get_param: image}
      flavor: {get_param: flavor}
      networks: [{network: {get_param: network} }]
      user_data_format: SOFTWARE_CONFIG
      user_data: {get_param: user_data}
'''

    def setUp(self):
        super(UpdateStackTest, self).setUp()

    def test_stack_update_nochange(self):
        template = _change_rsrc_properties(test_template_one_resource,
                                           ['test1'],
                                           {'value': 'test_no_change'})
        stack_identifier = self.stack_create(
            template=template)
        expected_resources = {'test1': 'OS::Heat::TestResource'}
        self.assertEqual(expected_resources,
                         self.list_resources(stack_identifier))

        # Update with no changes, resources should be unchanged
        self.update_stack(stack_identifier, template)
        self.assertEqual(expected_resources,
                         self.list_resources(stack_identifier))

    def test_stack_in_place_update(self):
        template = _change_rsrc_properties(test_template_one_resource,
                                           ['test1'],
                                           {'value': 'test_in_place'})
        stack_identifier = self.stack_create(
            template=template)
        expected_resources = {'test1': 'OS::Heat::TestResource'}
        self.assertEqual(expected_resources,
                         self.list_resources(stack_identifier))
        resource = self.client.resources.list(stack_identifier)
        initial_phy_id = resource[0].physical_resource_id

        tmpl_update = _change_rsrc_properties(
            test_template_one_resource, ['test1'],
            {'value': 'test_in_place_update'})
        # Update the Value
        self.update_stack(stack_identifier, tmpl_update)
        resource = self.client.resources.list(stack_identifier)
        # By default update_in_place
        self.assertEqual(initial_phy_id,
                         resource[0].physical_resource_id)

    def test_stack_update_replace(self):
        template = _change_rsrc_properties(test_template_one_resource,
                                           ['test1'],
                                           {'value': 'test_replace'})
        stack_identifier = self.stack_create(
            template=template)
        expected_resources = {'test1': 'OS::Heat::TestResource'}
        self.assertEqual(expected_resources,
                         self.list_resources(stack_identifier))
        resource = self.client.resources.list(stack_identifier)
        initial_phy_id = resource[0].physical_resource_id

        # Update the value and also set update_replace prop
        tmpl_update = _change_rsrc_properties(
            test_template_one_resource, ['test1'],
            {'value': 'test_in_place_update', 'update_replace': True})
        self.update_stack(stack_identifier, tmpl_update)
        resource = self.client.resources.list(stack_identifier)
        # update Replace
        self.assertNotEqual(initial_phy_id,
                            resource[0].physical_resource_id)

    def test_stack_update_add_remove(self):
        template = _change_rsrc_properties(test_template_one_resource,
                                           ['test1'],
                                           {'value': 'test_add_remove'})
        stack_identifier = self.stack_create(
            template=template)
        initial_resources = {'test1': 'OS::Heat::TestResource'}
        self.assertEqual(initial_resources,
                         self.list_resources(stack_identifier))

        tmpl_update = _change_rsrc_properties(
            test_template_two_resource, ['test1', 'test2'],
            {'value': 'test_add_remove_update'})
        # Add one resource via a stack update
        self.update_stack(stack_identifier, tmpl_update)
        updated_resources = {'test1': 'OS::Heat::TestResource',
                             'test2': 'OS::Heat::TestResource'}
        self.assertEqual(updated_resources,
                         self.list_resources(stack_identifier))

        # Then remove it by updating with the original template
        self.update_stack(stack_identifier, template)
        self.assertEqual(initial_resources,
                         self.list_resources(stack_identifier))

    def test_stack_update_rollback(self):
        template = _change_rsrc_properties(test_template_one_resource,
                                           ['test1'],
                                           {'value': 'test_update_rollback'})
        stack_identifier = self.stack_create(
            template=template)
        initial_resources = {'test1': 'OS::Heat::TestResource'}
        self.assertEqual(initial_resources,
                         self.list_resources(stack_identifier))

        tmpl_update = _change_rsrc_properties(
            test_template_two_resource, ['test1', 'test2'],
            {'value': 'test_update_rollback', 'fail': True})
        # stack update, also set failure
        self.update_stack(stack_identifier, tmpl_update,
                          expected_status='ROLLBACK_COMPLETE',
                          disable_rollback=False)
        # since stack update failed only the original resource is present
        updated_resources = {'test1': 'OS::Heat::TestResource'}
        self.assertEqual(updated_resources,
                         self.list_resources(stack_identifier))

    def test_stack_update_provider(self):
        template = _change_rsrc_properties(
            test_template_one_resource, ['test1'],
            {'value': 'test_provider_template'})
        files = {'provider.template': json.dumps(template)}
        env = {'resource_registry':
               {'My::TestResource': 'provider.template'}}
        stack_identifier = self.stack_create(
            template=self.provider_template,
            files=files,
            environment=env
        )

        initial_resources = {'test1': 'My::TestResource'}
        self.assertEqual(initial_resources,
                         self.list_resources(stack_identifier))

        # Prove the resource is backed by a nested stack, save the ID
        nested_identifier = self.assert_resource_is_a_stack(stack_identifier,
                                                            'test1')
        nested_id = nested_identifier.split('/')[-1]

        # Then check the expected resources are in the nested stack
        nested_resources = {'test1': 'OS::Heat::TestResource'}
        self.assertEqual(nested_resources,
                         self.list_resources(nested_identifier))
        tmpl_update = _change_rsrc_properties(
            test_template_two_resource, ['test1', 'test2'],
            {'value': 'test_provider_template'})
        # Add one resource via a stack update by changing the nested stack
        files['provider.template'] = json.dumps(tmpl_update)
        self.update_stack(stack_identifier, self.provider_template,
                          environment=env, files=files)

        # Parent resources should be unchanged and the nested stack
        # should have been updated in-place without replacement
        self.assertEqual(initial_resources,
                         self.list_resources(stack_identifier))
        rsrc = self.client.resources.get(stack_identifier, 'test1')
        self.assertEqual(rsrc.physical_resource_id, nested_id)

        # Then check the expected resources are in the nested stack
        nested_resources = {'test1': 'OS::Heat::TestResource',
                            'test2': 'OS::Heat::TestResource'}
        self.assertEqual(nested_resources,
                         self.list_resources(nested_identifier))

    def test_stack_update_provider_group(self):
        '''Test two-level nested update.'''
        # Create a ResourceGroup (which creates a nested stack),
        # containing provider resources (which create a nested
        # stack), thus excercising an update which traverses
        # two levels of nesting.
        template = _change_rsrc_properties(
            test_template_one_resource, ['test1'],
            {'value': 'test_provider_group_template'})
        files = {'provider.template': json.dumps(template)}
        env = {'resource_registry':
               {'My::TestResource': 'provider.template'}}

        stack_identifier = self.stack_create(
            template=self.provider_group_template,
            files=files,
            environment=env
        )

        initial_resources = {'test_group': 'OS::Heat::ResourceGroup'}
        self.assertEqual(initial_resources,
                         self.list_resources(stack_identifier))

        # Prove the resource is backed by a nested stack, save the ID
        nested_identifier = self.assert_resource_is_a_stack(stack_identifier,
                                                            'test_group')

        # Then check the expected resources are in the nested stack
        nested_resources = {'0': 'My::TestResource',
                            '1': 'My::TestResource'}
        self.assertEqual(nested_resources,
                         self.list_resources(nested_identifier))

        for n_rsrc in nested_resources:
            rsrc = self.client.resources.get(nested_identifier, n_rsrc)
            provider_stack = self.client.stacks.get(rsrc.physical_resource_id)
            provider_identifier = '%s/%s' % (provider_stack.stack_name,
                                             provider_stack.id)
            provider_resources = {u'test1': u'OS::Heat::TestResource'}
            self.assertEqual(provider_resources,
                             self.list_resources(provider_identifier))

        tmpl_update = _change_rsrc_properties(
            test_template_two_resource, ['test1', 'test2'],
            {'value': 'test_provider_group_template'})
        # Add one resource via a stack update by changing the nested stack
        files['provider.template'] = json.dumps(tmpl_update)
        self.update_stack(stack_identifier, self.provider_group_template,
                          environment=env, files=files)

        # Parent resources should be unchanged and the nested stack
        # should have been updated in-place without replacement
        self.assertEqual(initial_resources,
                         self.list_resources(stack_identifier))

        # Resource group stack should also be unchanged (but updated)
        nested_stack = self.client.stacks.get(nested_identifier)
        self.assertEqual('UPDATE_COMPLETE', nested_stack.stack_status)
        self.assertEqual(nested_resources,
                         self.list_resources(nested_identifier))

        for n_rsrc in nested_resources:
            rsrc = self.client.resources.get(nested_identifier, n_rsrc)
            provider_stack = self.client.stacks.get(rsrc.physical_resource_id)
            provider_identifier = '%s/%s' % (provider_stack.stack_name,
                                             provider_stack.id)
            provider_resources = {'test1': 'OS::Heat::TestResource',
                                  'test2': 'OS::Heat::TestResource'}
            self.assertEqual(provider_resources,
                             self.list_resources(provider_identifier))

    def test_stack_update_with_replacing_userdata(self):
        """Confirm that we can update userdata of instance during updating
        stack by the user of member role.

        Make sure that a resource that inherites from StackUser can be deleted
        during updating stack.
        """
        if not self.conf.minimal_image_ref:
            raise self.skipException("No minimal image configured to test")
        if not self.conf.minimal_instance_type:
            raise self.skipException("No flavor configured to test")

        parms = {'flavor': self.conf.minimal_instance_type,
                 'image': self.conf.minimal_image_ref,
                 'network': self.conf.fixed_network_name,
                 'user_data': ''}
        name = self._stack_rand_name()

        stack_identifier = self.stack_create(
            stack_name=name,
            template=self.update_userdata_template,
            parameters=parms
        )

        parms_updated = parms
        parms_updated['user_data'] = 'two'
        self.update_stack(
            stack_identifier,
            template=self.update_userdata_template,
            parameters=parms_updated)
