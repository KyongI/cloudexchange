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

from heat.engine.clients.os import monasca as client_plugin
from heat.engine import resource
from heat.engine.resources.openstack.monasca import alarm_definition
from heat.engine import stack
from heat.engine import template
from heat.tests import common
from heat.tests import utils


sample_template = {
    'heat_template_version': '2015-10-15',
    'resources': {
        'test_resource': {
            'type': 'OS::Monasca::AlarmDefinition',
            'properties': {
                'name': 'sample_alarm_id',
                'description': 'sample alarm def',
                'expression': 'sample expression',
                'match_by': ['match_by'],
                'severity': 'low',
                'ok_actions': ['sample_notification'],
                'alarm_actions': ['sample_notification'],
                'undetermined_actions': ['sample_notification'],
                'actions_enabled': False
            }
        }
    }
}

RESOURCE_TYPE = 'OS::Monasca::AlarmDefinition'


class MonascaAlarmDefinition(alarm_definition.MonascaAlarmDefinition):
    '''
    Monasca service is not available by default. So, this class overrides
    the is_service_available to return True
    '''
    @classmethod
    def is_service_available(cls, context):
        return True


class MonascaAlarmDefinitionTest(common.HeatTestCase):

    def setUp(self):
        super(MonascaAlarmDefinitionTest, self).setUp()

        self.ctx = utils.dummy_context()
        # As monascaclient is not part of requirements.txt, RESOURCE_TYPE is
        # not registered by default. For testing, its registered here
        resource._register_class(RESOURCE_TYPE,
                                 MonascaAlarmDefinition)
        self.stack = stack.Stack(
            self.ctx, 'test_stack',
            template.Template(sample_template)
        )

        self.test_resource = self.stack['test_resource']

        # Mock client plugin
        self.test_client_plugin = mock.MagicMock()
        self.test_resource.client_plugin = mock.MagicMock(
            return_value=self.test_client_plugin)
        self.test_client_plugin.get_notification.return_value = (
            'sample_notification'
        )

        # Mock client
        self.test_client = mock.MagicMock()
        self.test_resource.client = mock.MagicMock(
            return_value=self.test_client)

    def _get_mock_resource(self):
        value = dict(id='477e8273-60a7-4c41-b683-fdb0bc7cd152')

        return value

    def test_resource_handle_create(self):
        mock_alarm_create = self.test_client.alarm_definitions.create
        mock_alarm_patch = self.test_client.alarm_definitions.patch
        mock_resource = self._get_mock_resource()
        mock_alarm_create.return_value = mock_resource

        # validate the properties
        self.assertEqual(
            'sample_alarm_id',
            self.test_resource.properties.get(
                alarm_definition.MonascaAlarmDefinition.NAME))
        self.assertEqual(
            'sample alarm def',
            self.test_resource.properties.get(
                alarm_definition.MonascaAlarmDefinition.DESCRIPTION))
        self.assertEqual(
            'sample expression',
            self.test_resource.properties.get(
                alarm_definition.MonascaAlarmDefinition.EXPRESSION))
        self.assertEqual(
            ['match_by'],
            self.test_resource.properties.get(
                alarm_definition.MonascaAlarmDefinition.MATCH_BY))
        self.assertEqual(
            'low',
            self.test_resource.properties.get(
                alarm_definition.MonascaAlarmDefinition.SEVERITY))
        self.assertEqual(
            ['sample_notification'],
            self.test_resource.properties.get(
                alarm_definition.MonascaAlarmDefinition.OK_ACTIONS))
        self.assertEqual(
            ['sample_notification'],
            self.test_resource.properties.get(
                alarm_definition.MonascaAlarmDefinition.ALARM_ACTIONS))
        self.assertEqual(
            ['sample_notification'],
            self.test_resource.properties.get(
                alarm_definition.MonascaAlarmDefinition.UNDETERMINED_ACTIONS))
        self.assertEqual(
            False,
            self.test_resource.properties.get(
                alarm_definition.MonascaAlarmDefinition.ACTIONS_ENABLED))

        self.test_resource.data_set = mock.Mock()
        self.test_resource.handle_create()
        # validate physical resource id
        self.assertEqual(mock_resource['id'], self.test_resource.resource_id)

        args = dict(
            name='sample_alarm_id',
            description='sample alarm def',
            expression='sample expression',
            match_by=['match_by'],
            severity='low',
            ok_actions=['sample_notification'],
            alarm_actions=['sample_notification'],
            undetermined_actions=['sample_notification']
        )

        mock_alarm_create.assert_called_once_with(**args)
        mock_alarm_patch.assert_called_once_with(
            alarm_id=self.test_resource.resource_id,
            actions_enabled=False)

    def test_resource_handle_update(self):
        mock_alarm_patch = self.test_client.alarm_definitions.patch
        self.test_resource.resource_id = '477e8273-60a7-4c41-b683-fdb0bc7cd151'

        prop_diff = {
            alarm_definition.MonascaAlarmDefinition.NAME:
                'name-updated',
            alarm_definition.MonascaAlarmDefinition.DESCRIPTION:
                'description-updated',
            alarm_definition.MonascaAlarmDefinition.EXPRESSION:
                'expression-updated',
            alarm_definition.MonascaAlarmDefinition.ACTIONS_ENABLED:
                True,
            alarm_definition.MonascaAlarmDefinition.SEVERITY:
                'medium',
            alarm_definition.MonascaAlarmDefinition.OK_ACTIONS:
                ['sample_notification'],
            alarm_definition.MonascaAlarmDefinition.ALARM_ACTIONS:
                ['sample_notification'],
            alarm_definition.MonascaAlarmDefinition.UNDETERMINED_ACTIONS:
                ['sample_notification']}

        self.test_resource.handle_update(json_snippet=None,
                                         tmpl_diff=None,
                                         prop_diff=prop_diff)

        args = dict(
            alarm_id=self.test_resource.resource_id,
            name='name-updated',
            description='description-updated',
            expression='expression-updated',
            actions_enabled=True,
            severity='medium',
            ok_actions=['sample_notification'],
            alarm_actions=['sample_notification'],
            undetermined_actions=['sample_notification']
        )

        mock_alarm_patch.assert_called_once_with(**args)

    def test_resource_handle_update_sub_expression(self):
        '''
        Monasca does not allow to update the metrics in the expression though
        it allows to update the metrics measurement condition range. Monasca
        client raises HTTPUnProcessable in this case

        so UpdateReplace is raised to re-create the alarm-definition with
        updated new expression.
        '''
        # TODO(skraynev): remove it when monasca client will be
        #                 merged in global requirements
        class HTTPUnProcessable(Exception):
            pass

        client_plugin.monasca_exc = mock.Mock()
        client_plugin.monasca_exc.HTTPUnProcessable = HTTPUnProcessable
        mock_alarm_patch = self.test_client.alarm_definitions.patch
        mock_alarm_patch.side_effect = (
            client_plugin.monasca_exc.HTTPUnProcessable)
        self.test_resource.resource_id = '477e8273-60a7-4c41-b683-fdb0bc7cd151'

        prop_diff = {alarm_definition.MonascaAlarmDefinition.EXPRESSION:
                     'expression-updated'}

        self.assertRaises(resource.UpdateReplace,
                          self.test_resource.handle_update,
                          json_snippet=None,
                          tmpl_diff=None,
                          prop_diff=prop_diff)

    def test_resource_handle_delete(self):
        mock_alarm_delete = self.test_client.alarm_definitions.delete
        self.test_resource.resource_id = '477e8273-60a7-4c41-b683-fdb0bc7cd151'
        mock_alarm_delete.return_value = None

        self.assertIsNone(self.test_resource.handle_delete())
        mock_alarm_delete.assert_called_once_with(
            alarm_id=self.test_resource.resource_id
        )

    def test_resource_handle_delete_resource_id_is_none(self):
        self.test_resource.resource_id = None
        self.assertIsNone(self.test_resource.handle_delete())

    def test_resource_handle_delete_not_found(self):
        # TODO(skraynev): remove it when monasca client will be
        #                 merged in global requirements
        class NotFound(Exception):
            pass

        client_plugin.monasca_exc = mock.Mock()
        client_plugin.monasca_exc.NotFound = NotFound

        self.test_resource.resource_id = '477e8273-60a7-4c41-b683-fdb0bc7cd151'
        mock_alarm_delete = self.test_client.alarm_definitions.delete
        mock_alarm_delete.side_effect = client_plugin.monasca_exc.NotFound
        self.assertIsNone(self.test_resource.handle_delete())
        self.assertEqual(1,
                         self.test_client_plugin.ignore_not_found.call_count)
        e_type = type(self.test_client_plugin.ignore_not_found.call_args[0][0])
        self.assertEqual(type(client_plugin.monasca_exc.NotFound()), e_type)

    def test_resource_mapping(self):
        mapping = alarm_definition.resource_mapping()
        self.assertEqual(1, len(mapping))
        self.assertEqual(alarm_definition.MonascaAlarmDefinition,
                         mapping[RESOURCE_TYPE])
        self.assertIsInstance(self.test_resource,
                              alarm_definition.MonascaAlarmDefinition)

    def test_resource_show_resource(self):
        mock_notification_get = self.test_client.alarm_definitions.get
        mock_notification_get.return_value = {}

        self.assertEqual({},
                         self.test_resource._show_resource(),
                         'Failed to show resource')
