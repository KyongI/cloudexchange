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
from heat.engine import attributes
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine import support


class CronTrigger(resource.Resource):
    support_status = support.SupportStatus(version='5.0.0')

    PROPERTIES = (
        NAME, PATTERN, WORKFLOW, FIRST_TIME, COUNT
    ) = (
        'name', 'pattern', 'workflow', 'first_time', 'count'
    )

    _WORKFLOW_KEYS = (
        WORKFLOW_NAME, WORKFLOW_INPUT
    ) = (
        'name', 'input'
    )

    ATTRIBUTES = (
        NEXT_EXECUTION_TIME, REMAINING_EXECUTIONS
    ) = (
        'next_execution_time', 'remaining_executions'
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the cron trigger.')
        ),
        PATTERN: properties.Schema(
            properties.Schema.STRING,
            _('Cron expression.'),
            constraints=[
                constraints.CustomConstraint(
                    'cron_expression')
            ]
        ),
        WORKFLOW: properties.Schema(
            properties.Schema.MAP,
            _('Workflow to execute.'),
            required=True,
            schema={
                WORKFLOW_NAME: properties.Schema(
                    properties.Schema.STRING,
                    _('Name of the workflow.')
                ),
                WORKFLOW_INPUT: properties.Schema(
                    properties.Schema.MAP,
                    _('Input values for the workflow.')
                )
            }
        ),
        FIRST_TIME: properties.Schema(
            properties.Schema.STRING,
            _('Time of the first execution in format "YYYY-MM-DD HH:MM".')
        ),
        COUNT: properties.Schema(
            properties.Schema.INTEGER,
            _('Remaining executions.')
        )
    }

    attributes_schema = {
        NEXT_EXECUTION_TIME: attributes.Schema(
            _('Time of the next execution in format "YYYY-MM-DD HH:MM:SS".'),
            type=attributes.Schema.STRING
        ),
        REMAINING_EXECUTIONS: attributes.Schema(
            _('Number of remaining executions.'),
            type=attributes.Schema.INTEGER
        )
    }

    default_client_name = 'mistral'

    entity = 'cron_triggers'

    def _cron_trigger_name(self):
        return self.properties.get(self.NAME) or self.physical_resource_name()

    def handle_create(self):
        workflow = self.properties.get(self.WORKFLOW)
        args = {
            'name': self._cron_trigger_name(),
            'pattern': self.properties.get(self.PATTERN),
            'workflow_name': workflow.get(self.WORKFLOW_NAME),
            'workflow_input': workflow.get(self.WORKFLOW_INPUT),
            'first_time': self.properties.get(self.FIRST_TIME),
            'count': self.properties.get(self.COUNT)
        }

        cron_trigger = self.client().cron_triggers.create(**args)
        self.resource_id_set(cron_trigger.name)

    def _resolve_attribute(self, name):
        try:
            trigger = self.client().cron_triggers.get(self.resource_id)
        except Exception as ex:
            self.client_plugin().ignore_not_found(ex)
            return ''
        if name == self.NEXT_EXECUTION_TIME:
            return trigger.next_execution_time
        elif name == self.REMAINING_EXECUTIONS:
            return trigger.remaining_executions

    # TODO(tlashchova): remove this method when mistralclient>1.0.0 is used.
    def _show_resource(self):
        cron_trigger = self.client().cron_triggers.get(self.resource_id)
        if hasattr(cron_trigger, 'to_dict'):
            super(CronTrigger, self)._show_resource()
        return cron_trigger._data


def resource_mapping():
    return {
        'OS::Mistral::CronTrigger': CronTrigger,
    }
