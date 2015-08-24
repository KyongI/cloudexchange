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

from heat.common.i18n import _
from heat.engine import clients
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine import support


class MonascaAlarmDefinition(resource.Resource):
    """Heat Template Resource for Monasca Alarm definition."""

    support_status = support.SupportStatus(
        version='5.0.0',
        status=support.UNSUPPORTED)

    default_client_name = 'monasca'

    entity = 'alarm_definitions'

    SEVERITY_LEVELS = (
        LOW, MEDIUM, HIGH, CRITICAL
    ) = (
        'low', 'medium', 'high', 'critical'
    )

    PROPERTIES = (
        NAME, DESCRIPTION, EXPRESSION, MATCH_BY, SEVERITY,
        OK_ACTIONS, ALARM_ACTIONS, UNDETERMINED_ACTIONS,
        ACTIONS_ENABLED
    ) = (
        'name', 'description', 'expression', 'match_by', 'severity',
        'ok_actions', 'alarm_actions', 'undetermined_actions',
        'actions_enabled'
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the alarm. By default, physical resource name is '
              'used.'),
            update_allowed=True
        ),
        DESCRIPTION: properties.Schema(
            properties.Schema.STRING,
            _('Description of the alarm.'),
            update_allowed=True
        ),
        EXPRESSION: properties.Schema(
            properties.Schema.STRING,
            _('Expression of the alarm to evaluate.'),
            update_allowed=True,
            required=True
        ),
        MATCH_BY: properties.Schema(
            properties.Schema.LIST,
            _('The metric dimensions to match to the alarm dimensions. '
              'One or more dimension key names separated by a comma.')
        ),
        SEVERITY: properties.Schema(
            properties.Schema.STRING,
            _('Severity of the alarm.'),
            update_allowed=True,
            constraints=[constraints.AllowedValues(
                SEVERITY_LEVELS
            )],
            default=LOW
        ),
        OK_ACTIONS: properties.Schema(
            properties.Schema.LIST,
            _('The notification methods to use when an alarm state is OK.'),
            update_allowed=True,
            schema=properties.Schema(
                properties.Schema.STRING,
                _('Monasca notification'),
                constraints=[constraints.CustomConstraint(
                    'monasca.notification')
                ]
            )
        ),
        ALARM_ACTIONS: properties.Schema(
            properties.Schema.LIST,
            _('The notification methods to use when an alarm state is ALARM.'),
            update_allowed=True,
            schema=properties.Schema(
                properties.Schema.STRING,
                _('Monasca notification'),
                constraints=[constraints.CustomConstraint(
                    'monasca.notification')
                ]
            )
        ),
        UNDETERMINED_ACTIONS: properties.Schema(
            properties.Schema.LIST,
            _('The notification methods to use when an alarm state is '
              'UNDETERMINED.'),
            update_allowed=True,
            schema=properties.Schema(
                properties.Schema.STRING,
                _('Monasca notification'),
                constraints=[constraints.CustomConstraint(
                    'monasca.notification')
                ]
            )
        ),
        ACTIONS_ENABLED: properties.Schema(
            properties.Schema.BOOLEAN,
            _('Whether to enable the actions or not.'),
            update_allowed=True,
            default=True,
        ),
    }

    def handle_create(self):
        args = dict(
            name=(self.properties[self.NAME] or
                  self.physical_resource_name()),
            description=self.properties[self.DESCRIPTION],
            expression=self.properties[self.EXPRESSION],
            match_by=self.properties[self.MATCH_BY],
            severity=self.properties[self.SEVERITY],
            ok_actions=self.properties[self.OK_ACTIONS],
            alarm_actions=self.properties[self.ALARM_ACTIONS],
            undetermined_actions=self.properties[
                self.UNDETERMINED_ACTIONS]
        )

        alarm = self.client().alarm_definitions.create(**args)
        self.resource_id_set(alarm['id'])

        # Monasca enables action by default
        actions_enabled = self.properties[self.ACTIONS_ENABLED]
        if not actions_enabled:
            self.client().alarm_definitions.patch(
                alarm_id=self.resource_id,
                actions_enabled=actions_enabled
            )

    def handle_update(self, prop_diff, json_snippet=None, tmpl_diff=None):
        args = dict(alarm_id=self.resource_id)

        if prop_diff.get(self.NAME):
            args['name'] = prop_diff.get(self.NAME)

        if prop_diff.get(self.DESCRIPTION):
            args['description'] = prop_diff.get(self.DESCRIPTION)

        if prop_diff.get(self.EXPRESSION):
            args['expression'] = prop_diff.get(self.EXPRESSION)

        if prop_diff.get(self.SEVERITY):
            args['severity'] = prop_diff.get(self.SEVERITY)

        if prop_diff.get(self.OK_ACTIONS):
            args['ok_actions'] = prop_diff.get(self.OK_ACTIONS)

        if prop_diff.get(self.ALARM_ACTIONS):
            args['alarm_actions'] = prop_diff.get(self.ALARM_ACTIONS)

        if prop_diff.get(self.UNDETERMINED_ACTIONS):
            args['undetermined_actions'] = prop_diff.get(
                self.UNDETERMINED_ACTIONS
            )

        if prop_diff.get(self.ACTIONS_ENABLED):
            args['actions_enabled'] = prop_diff.get(self.ACTIONS_ENABLED)

        if len(args) > 1:
            try:
                self.client().alarm_definitions.patch(**args)
            except Exception as ex:
                if self.client_plugin().is_un_processable(ex):
                    # Monasca does not allow to update the sub expression
                    raise resource.UpdateReplace(resource_name=self.name)

    def handle_delete(self):
        if self.resource_id is not None:
            try:
                self.client().alarm_definitions.delete(
                    alarm_id=self.resource_id)
            except Exception as ex:
                self.client_plugin().ignore_not_found(ex)

    # FIXME(kanagaraj-manickam) Remove this method once monasca defect 1484900
    # is fixed.
    def _show_resource(self):
        return self.client().alarm_definitions.get(self.resource_id)


def resource_mapping():
    return {
        'OS::Monasca::AlarmDefinition': MonascaAlarmDefinition
    }


def available_resource_mapping():
    if not clients.has_client(MonascaAlarmDefinition.default_client_name):
        return {}

    return resource_mapping()
