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
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine import support


class KeystoneProject(resource.Resource):
    """Heat Template Resource for Keystone Project."""

    support_status = support.SupportStatus(
        version='2015.1',
        message=_('Supported versions: keystone v3'))

    default_client_name = 'keystone'

    PROPERTIES = (
        NAME, DOMAIN, DESCRIPTION, ENABLED
    ) = (
        'name', 'domain', 'description', 'enabled'
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of keystone project.'),
            update_allowed=True
        ),
        DOMAIN: properties.Schema(
            properties.Schema.STRING,
            _('Name or id of keystone domain.'),
            default='default',
            update_allowed=True,
            constraints=[constraints.CustomConstraint('keystone.domain')]
        ),
        DESCRIPTION: properties.Schema(
            properties.Schema.STRING,
            _('Description of keystone project.'),
            default='',
            update_allowed=True
        ),
        ENABLED: properties.Schema(
            properties.Schema.BOOLEAN,
            _('This project is enabled or disabled.'),
            default=True,
            update_allowed=True
        )
    }

    def _create_project(self,
                        project_name,
                        description,
                        domain,
                        enabled):
        domain = self.client_plugin().get_domain_id(domain)

        return self.client().client.projects.create(
            name=project_name,
            domain=domain,
            description=description,
            enabled=enabled)

    def _delete_project(self, project_id):
        return self.client().client.projects.delete(project_id)

    def _update_project(self,
                        project_id,
                        domain,
                        new_name=None,
                        new_description=None,
                        enabled=None):
        values = dict()

        if new_name is not None:
            values['name'] = new_name
        if new_description is not None:
            values['description'] = new_description
        if enabled is not None:
            values['enabled'] = enabled

        values['project'] = project_id
        domain = self.client_plugin().get_domain_id(domain)

        values['domain'] = domain

        return self.client().client.projects.update(**values)

    def handle_create(self):
        project_name = (self.properties.get(self.NAME) or
                        self.physical_resource_name())
        description = self.properties.get(self.DESCRIPTION)
        domain = self.properties.get(self.DOMAIN)
        enabled = self.properties.get(self.ENABLED)

        project = self._create_project(
            project_name=project_name,
            description=description,
            domain=domain,
            enabled=enabled
        )

        self.resource_id_set(project.id)

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        name = prop_diff.get(self.NAME) or self.physical_resource_name()
        description = prop_diff.get(self.DESCRIPTION)
        enabled = prop_diff.get(self.ENABLED)
        domain = (prop_diff.get(self.DOMAIN) or
                  self._stored_properties_data.get(self.DOMAIN))

        self._update_project(
            project_id=self.resource_id,
            domain=domain,
            new_name=name,
            new_description=description,
            enabled=enabled
        )

    def handle_delete(self):
        if self.resource_id is not None:
            try:
                self._delete_project(project_id=self.resource_id)
            except Exception as ex:
                self.client_plugin().ignore_not_found(ex)


def resource_mapping():
    return {
        'OS::Keystone::Project': KeystoneProject
    }
