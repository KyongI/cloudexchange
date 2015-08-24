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

from heat.engine import constraints
from heat.engine import properties
from heat.engine.resources.openstack.keystone import project
from heat.engine import stack
from heat.engine import template
from heat.tests import common
from heat.tests import utils

keystone_project_template = {
    'heat_template_version': '2013-05-23',
    'resources': {
        'test_project': {
            'type': 'OS::Keystone::Project',
            'properties': {
                'name': 'test_project_1',
                'description': 'Test project',
                'domain': 'default',
                'enabled': 'True'
            }
        }
    }
}

RESOURCE_TYPE = 'OS::Keystone::Project'


class KeystoneProjectTest(common.HeatTestCase):
    def setUp(self):
        super(KeystoneProjectTest, self).setUp()

        self.ctx = utils.dummy_context()

        self.stack = stack.Stack(
            self.ctx, 'test_stack_keystone',
            template.Template(keystone_project_template)
        )

        self.test_project = self.stack['test_project']

        # Mock client
        self.keystoneclient = mock.MagicMock()
        self.test_project.client = mock.MagicMock()
        self.test_project.client.return_value = self.keystoneclient
        self.projects = self.keystoneclient.client.projects

        # Mock client plugin
        def _domain_side_effect(value):
            return value

        keystone_client_plugin = mock.MagicMock()
        keystone_client_plugin.get_domain_id.side_effect = _domain_side_effect
        self.test_project.client_plugin = mock.MagicMock()
        self.test_project.client_plugin.return_value = keystone_client_plugin

    def _get_mock_project(self):
        value = mock.MagicMock()
        project_id = '477e8273-60a7-4c41-b683-fdb0bc7cd151'
        value.id = project_id

        return value

    def test_resource_mapping(self):
        mapping = project.resource_mapping()
        self.assertEqual(1, len(mapping))
        self.assertEqual(project.KeystoneProject, mapping[RESOURCE_TYPE])
        self.assertIsInstance(self.test_project, project.KeystoneProject)

    def test_project_handle_create(self):
        mock_project = self._get_mock_project()
        self.projects.create.return_value = mock_project

        # validate the properties
        self.assertEqual(
            'test_project_1',
            self.test_project.properties.get(project.KeystoneProject.NAME))
        self.assertEqual(
            'Test project',
            self.test_project.properties.get(
                project.KeystoneProject.DESCRIPTION))
        self.assertEqual(
            'default',
            self.test_project.properties.get(project.KeystoneProject.DOMAIN))
        self.assertEqual(
            True,
            self.test_project.properties.get(project.KeystoneProject.ENABLED))

        self.test_project.handle_create()

        # validate project creation
        self.projects.create.assert_called_once_with(
            name='test_project_1',
            description='Test project',
            domain='default',
            enabled=True)

        # validate physical resource id
        self.assertEqual(mock_project.id, self.test_project.resource_id)

    def test_properties_title(self):
        property_title_map = {
            project.KeystoneProject.NAME: 'name',
            project.KeystoneProject.DESCRIPTION: 'description',
            project.KeystoneProject.DOMAIN: 'domain',
            project.KeystoneProject.ENABLED: 'enabled'
        }

        for actual_title, expected_title in property_title_map.items():
            self.assertEqual(
                expected_title,
                actual_title,
                'KeystoneProject PROPERTIES(%s) title modified.' %
                actual_title)

    def test_property_name_validate_schema(self):
        schema = project.KeystoneProject.properties_schema[
            project.KeystoneProject.NAME]
        self.assertEqual(
            True,
            schema.update_allowed,
            'update_allowed for property %s is modified' %
            project.KeystoneProject.NAME)

        self.assertEqual(properties.Schema.STRING,
                         schema.type,
                         'type for property %s is modified' %
                         project.KeystoneProject.NAME)

        self.assertEqual('Name of keystone project.',
                         schema.description,
                         'description for property %s is modified' %
                         project.KeystoneProject.NAME)

    def test_property_description_validate_schema(self):
        schema = project.KeystoneProject.properties_schema[
            project.KeystoneProject.DESCRIPTION]
        self.assertEqual(
            True,
            schema.update_allowed,
            'update_allowed for property %s is modified' %
            project.KeystoneProject.DESCRIPTION)

        self.assertEqual(properties.Schema.STRING,
                         schema.type,
                         'type for property %s is modified' %
                         project.KeystoneProject.DESCRIPTION)

        self.assertEqual('Description of keystone project.',
                         schema.description,
                         'description for property %s is modified' %
                         project.KeystoneProject.DESCRIPTION)

        self.assertEqual(
            '',
            schema.default,
            'default for property %s is modified' %
            project.KeystoneProject.DESCRIPTION)

    def test_property_domain_validate_schema(self):
        schema = project.KeystoneProject.properties_schema[
            project.KeystoneProject.DOMAIN]
        self.assertEqual(
            True,
            schema.update_allowed,
            'update_allowed for property %s is modified' %
            project.KeystoneProject.DOMAIN)

        self.assertEqual(properties.Schema.STRING,
                         schema.type,
                         'type for property %s is modified' %
                         project.KeystoneProject.DOMAIN)

        self.assertEqual('Name or id of keystone domain.',
                         schema.description,
                         'description for property %s is modified' %
                         project.KeystoneProject.DOMAIN)

        self.assertEqual(
            [constraints.CustomConstraint('keystone.domain')],
            schema.constraints,
            'constrains for property %s is modified' %
            project.KeystoneProject.DOMAIN)

        self.assertEqual(
            'default',
            schema.default,
            'default for property %s is modified' %
            project.KeystoneProject.DOMAIN)

    def test_property_enabled_validate_schema(self):
        schema = project.KeystoneProject.properties_schema[
            project.KeystoneProject.ENABLED]
        self.assertEqual(
            True,
            schema.update_allowed,
            'update_allowed for property %s is modified' %
            project.KeystoneProject.DOMAIN)

        self.assertEqual(properties.Schema.BOOLEAN,
                         schema.type,
                         'type for property %s is modified' %
                         project.KeystoneProject.ENABLED)

        self.assertEqual('This project is enabled or disabled.',
                         schema.description,
                         'description for property %s is modified' %
                         project.KeystoneProject.ENABLED)

        self.assertEqual(
            True,
            schema.default,
            'default for property %s is modified' %
            project.KeystoneProject.ENABLED)

    def _get_property_schema_value_default(self, name):
        schema = project.KeystoneProject.properties_schema[name]
        return schema.default

    def test_project_handle_create_default(self):
        values = {
            project.KeystoneProject.NAME: None,
            project.KeystoneProject.DESCRIPTION:
            (self._get_property_schema_value_default(
             project.KeystoneProject.DESCRIPTION)),
            project.KeystoneProject.DOMAIN:
            (self._get_property_schema_value_default(
             project.KeystoneProject.DOMAIN)),
            project.KeystoneProject.ENABLED:
            (self._get_property_schema_value_default(
             project.KeystoneProject.ENABLED))
        }

        def _side_effect(key):
            return values[key]

        mock_project = self._get_mock_project()
        self.projects.create.return_value = mock_project
        self.test_project.properties = mock.MagicMock()
        self.test_project.properties.get.side_effect = _side_effect

        self.test_project.physical_resource_name = mock.MagicMock()
        self.test_project.physical_resource_name.return_value = 'foo'

        # validate the properties
        self.assertEqual(
            None,
            self.test_project.properties.get(project.KeystoneProject.NAME))
        self.assertEqual(
            '',
            self.test_project.properties.get(
                project.KeystoneProject.DESCRIPTION))
        self.assertEqual(
            'default',
            self.test_project.properties.get(project.KeystoneProject.DOMAIN))
        self.assertEqual(
            True,
            self.test_project.properties.get(project.KeystoneProject.ENABLED))

        self.test_project.handle_create()

        # validate project creation
        self.projects.create.assert_called_once_with(
            name='foo',
            description='',
            domain='default',
            enabled=True)

    def test_project_handle_update(self):
        self.test_project.resource_id = '477e8273-60a7-4c41-b683-fdb0bc7cd151'

        prop_diff = {project.KeystoneProject.NAME: 'test_project_1_updated',
                     project.KeystoneProject.DESCRIPTION:
                     'Test Project updated',
                     project.KeystoneProject.ENABLED: False,
                     project.KeystoneProject.DOMAIN: 'test_domain'}

        self.test_project.handle_update(json_snippet=None,
                                        tmpl_diff=None,
                                        prop_diff=prop_diff)

        self.projects.update.assert_called_once_with(
            project=self.test_project.resource_id,
            name=prop_diff[project.KeystoneProject.NAME],
            description=prop_diff[project.KeystoneProject.DESCRIPTION],
            enabled=prop_diff[project.KeystoneProject.ENABLED],
            domain='test_domain'
        )

    def test_project_handle_update_default(self):
        self.test_project.resource_id = '477e8273-60a7-4c41-b683-fdb0bc7cd151'
        self.test_project._stored_properties_data = dict(domain='default')
        self.test_project.physical_resource_name = mock.MagicMock()
        self.test_project.physical_resource_name.return_value = 'foo'

        prop_diff = {project.KeystoneProject.DESCRIPTION:
                     'Test Project updated',
                     project.KeystoneProject.ENABLED: False}

        self.test_project.handle_update(json_snippet=None,
                                        tmpl_diff=None,
                                        prop_diff=prop_diff)

        # validate default name to physical resource name and
        # domain is set from stored properties used during creation.
        self.projects.update.assert_called_once_with(
            project=self.test_project.resource_id,
            name='foo',
            description=prop_diff[project.KeystoneProject.DESCRIPTION],
            enabled=prop_diff[project.KeystoneProject.ENABLED],
            domain='default'
        )

    def test_project_handle_delete(self):
        self.test_project.resource_id = '477e8273-60a7-4c41-b683-fdb0bc7cd151'
        self.projects.delete.return_value = None

        self.assertIsNone(self.test_project.handle_delete())
        self.projects.delete.assert_called_once_with(
            self.test_project.resource_id
        )

    def test_project_handle_delete_resource_id_is_none(self):
        self.resource_id = None
        self.assertIsNone(self.test_project.handle_delete())

    def test_project_handle_delete_not_found(self):
        exc = self.keystoneclient.NotFound
        self.projects.delete.side_effect = exc

        self.assertIsNone(self.test_project.handle_delete())
