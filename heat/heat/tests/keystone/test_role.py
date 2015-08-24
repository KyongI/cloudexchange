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

import mock

from heat.engine.resources.openstack.keystone import role
from heat.engine import stack
from heat.engine import template
from heat.tests import common
from heat.tests import utils

keystone_role_template = {
    'heat_template_version': '2013-05-23',
    'resources': {
        'test_role': {
            'type': 'OS::Keystone::Role',
            'properties': {
                'name': 'test_role_1'
            }
        }
    }
}

RESOURCE_TYPE = 'OS::Keystone::Role'


class KeystoneRoleTest(common.HeatTestCase):
    def setUp(self):
        super(KeystoneRoleTest, self).setUp()

        self.ctx = utils.dummy_context()

        self.stack = stack.Stack(
            self.ctx, 'test_stack_keystone',
            template.Template(keystone_role_template)
        )

        self.test_role = self.stack['test_role']

        self.keystoneclient = mock.MagicMock()
        self.test_role.client = mock.MagicMock()
        self.test_role.client.return_value = self.keystoneclient
        self.roles = self.keystoneclient.client.roles

    def _get_mock_role(self):
        value = mock.MagicMock()
        role_id = '477e8273-60a7-4c41-b683-fdb0bc7cd151'
        value.id = role_id

        return value

    def test_resource_mapping(self):
        mapping = role.resource_mapping()
        self.assertEqual(1, len(mapping))
        self.assertEqual(role.KeystoneRole, mapping[RESOURCE_TYPE])
        self.assertIsInstance(self.test_role, role.KeystoneRole)

    def test_role_handle_create(self):
        mock_role = self._get_mock_role()
        self.roles.create.return_value = mock_role

        # validate the properties
        self.assertEqual('test_role_1',
                         self.test_role.properties.get(role.KeystoneRole.NAME))

        self.test_role.handle_create()

        # validate role creation with given name
        self.roles.create.assert_called_once_with(name='test_role_1')

        # validate physical resource id
        self.assertEqual(mock_role.id, self.test_role.resource_id)

    def test_role_handle_create_default_name(self):
        # reset the NAME value to None, to make sure role is
        # created with physical_resource_name
        self.test_role.properties = mock.MagicMock()
        self.test_role.properties.get.return_value = None

        self.test_role.handle_create()

        # validate role creation with default name
        physical_resource_name = self.test_role.physical_resource_name()
        self.roles.create.assert_called_once_with(name=physical_resource_name)

    def test_role_handle_update(self):
        self.test_role.resource_id = '477e8273-60a7-4c41-b683-fdb0bc7cd151'

        # update the name property
        prop_diff = {role.KeystoneRole.NAME: 'test_role_1_updated'}

        self.test_role.handle_update(json_snippet=None,
                                     tmpl_diff=None,
                                     prop_diff=prop_diff)

        self.roles.update.assert_called_once_with(
            role=self.test_role.resource_id,
            name=prop_diff[role.KeystoneRole.NAME]
        )

    def test_role_handle_delete(self):
        self.test_role.resource_id = '477e8273-60a7-4c41-b683-fdb0bc7cd151'
        self.roles.delete.return_value = None

        self.assertIsNone(self.test_role.handle_delete())
        self.roles.delete.assert_called_once_with(
            self.test_role.resource_id
        )

    def test_role_handle_delete_resource_id_is_none(self):
        self.resource_id = None
        self.assertIsNone(self.test_role.handle_delete())

        assert not self.roles.delete.called

    def test_role_handle_delete_not_found(self):
        exc = self.keystoneclient.NotFound
        self.roles.delete.side_effect = exc

        self.assertIsNone(self.test_role.handle_delete())
