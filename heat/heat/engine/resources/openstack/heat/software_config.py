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

from oslo_log import log as logging

from heat.common.i18n import _
from heat.engine import attributes
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine import support
from heat.rpc import api as rpc_api

LOG = logging.getLogger(__name__)


class SoftwareConfig(resource.Resource):
    '''
    A resource for describing and storing software configuration.

    The software_configs API which backs this resource creates immutable
    configs, so any change to the template resource definition will result
    in a new config being created, and the old one being deleted.

    Configs can be defined in the same template which uses them, or they can
    be created in one stack, and passed to another stack via a parameter.

    A config resource can be referenced in other resource properties which
    are config-aware. This includes the properties OS::Nova::Server user_data,
    OS::Heat::SoftwareDeployment config and OS::Heat::MultipartMime parts
    config.

    Along with the config script itself, this resource can define schemas for
    inputs and outputs which the config script is expected to consume and
    produce. Inputs and outputs are optional and will map to concepts which
    are specific to the configuration tool being used.
    '''

    support_status = support.SupportStatus(version='2014.1')

    PROPERTIES = (
        GROUP, CONFIG, OPTIONS, INPUTS, OUTPUTS
    ) = (
        'group', 'config', 'options', 'inputs', 'outputs'
    )

    IO_PROPERTIES = (
        NAME, DESCRIPTION, TYPE, DEFAULT, ERROR_OUTPUT
    ) = (
        'name', 'description', 'type', 'default', 'error_output'
    )

    ATTRIBUTES = (
        CONFIG_ATTR,
    ) = (
        'config',
    )

    input_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the input.'),
            required=True
        ),
        DESCRIPTION: properties.Schema(
            properties.Schema.STRING,
            _('Description of the input.')
        ),
        TYPE: properties.Schema(
            properties.Schema.STRING,
            _('Type of the value of the input.'),
            default='String',
            constraints=[constraints.AllowedValues((
                'String', 'Number', 'CommaDelimitedList', 'Json', 'Boolean'))]
        ),
        DEFAULT: properties.Schema(
            properties.Schema.STRING,
            _('Default value for the input if none is specified.'),
        ),
    }

    output_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the output.'),
            required=True
        ),
        DESCRIPTION: properties.Schema(
            properties.Schema.STRING,
            _('Description of the output.')
        ),
        TYPE: properties.Schema(
            properties.Schema.STRING,
            _('Type of the value of the output.'),
            default='String',
            constraints=[constraints.AllowedValues((
                'String', 'Number', 'CommaDelimitedList', 'Json', 'Boolean'))]
        ),
        ERROR_OUTPUT: properties.Schema(
            properties.Schema.BOOLEAN,
            _('Denotes that the deployment is in an error state if this '
              'output has a value.'),
            default=False
        )
    }

    properties_schema = {
        GROUP: properties.Schema(
            properties.Schema.STRING,
            _('Namespace to group this software config by when delivered to '
              'a server. This may imply what configuration tool is going to '
              'perform the configuration.'),
            default='Heat::Ungrouped'
        ),
        CONFIG: properties.Schema(
            properties.Schema.STRING,
            _('Configuration script or manifest which specifies what actual '
              'configuration is performed.'),
        ),
        OPTIONS: properties.Schema(
            properties.Schema.MAP,
            _('Map containing options specific to the configuration '
              'management tool used by this resource.'),
        ),
        INPUTS: properties.Schema(
            properties.Schema.LIST,
            _('Schema representing the inputs that this software config is '
              'expecting.'),
            schema=properties.Schema(properties.Schema.MAP,
                                     schema=input_schema)
        ),
        OUTPUTS: properties.Schema(
            properties.Schema.LIST,
            _('Schema representing the outputs that this software config '
              'will produce.'),
            schema=properties.Schema(properties.Schema.MAP,
                                     schema=output_schema)
        ),
    }

    attributes_schema = {
        CONFIG_ATTR: attributes.Schema(
            _("The config value of the software config."),
            type=attributes.Schema.STRING
        ),
    }

    def handle_create(self):
        props = dict(self.properties)
        props[self.NAME] = self.physical_resource_name()

        sc = self.rpc_client().create_software_config(self.context, **props)
        self.resource_id_set(sc[rpc_api.SOFTWARE_CONFIG_ID])

    def handle_delete(self):

        if self.resource_id is None:
            return

        try:
            self.rpc_client().delete_software_config(
                self.context, self.resource_id)
        except Exception as ex:
            self.rpc_client().ignore_error_named(ex, 'NotFound')

    def _resolve_attribute(self, name):
        '''
        "config" returns the config value of the software config. If the
         software config does not exist, returns an empty string.
        '''
        if name == self.CONFIG_ATTR and self.resource_id:
            try:
                sc = self.rpc_client().show_software_config(
                    self.context, self.resource_id)
                return sc[rpc_api.SOFTWARE_CONFIG_CONFIG]
            except Exception as ex:
                self.rpc_client().ignore_error_named(ex, 'NotFound')


def resource_mapping():
    return {
        'OS::Heat::SoftwareConfig': SoftwareConfig,
    }
