# Copyright (c) 2014 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_log import log as logging

from heat.common import exception
from heat.common.i18n import _
from heat.common.i18n import _LI
from heat.engine import attributes
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine import support

LOG = logging.getLogger(__name__)


class SaharaCluster(resource.Resource):

    PROPERTIES = (
        NAME, PLUGIN_NAME, HADOOP_VERSION, CLUSTER_TEMPLATE_ID,
        KEY_NAME, IMAGE, MANAGEMENT_NETWORK, IMAGE_ID,
    ) = (
        'name', 'plugin_name', 'hadoop_version', 'cluster_template_id',
        'key_name', 'image', 'neutron_management_network', 'default_image_id',
    )

    ATTRIBUTES = (
        STATUS, INFO,
    ) = (
        "status", "info",
    )

    CLUSTER_STATUSES = (
        CLUSTER_ACTIVE, CLUSTER_ERROR
    ) = (
        'Active', 'Error'
    )
    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Hadoop cluster name.'),
        ),
        PLUGIN_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Plugin name.'),
            required=True,
        ),
        HADOOP_VERSION: properties.Schema(
            properties.Schema.STRING,
            _('Version of Hadoop running on instances.'),
            required=True,
        ),
        CLUSTER_TEMPLATE_ID: properties.Schema(
            properties.Schema.STRING,
            _('ID of the Cluster Template used for '
              'Node Groups and configurations.'),
            required=True,
        ),
        KEY_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Keypair added to instances to make them accessible for user.'),
            constraints=[
                constraints.CustomConstraint('nova.keypair')
            ],
        ),
        IMAGE: properties.Schema(
            properties.Schema.STRING,
            _('Name or UUID of the image used to boot Hadoop nodes.'),
            support_status=support.SupportStatus(
                status=support.DEPRECATED,
                message=_('Use property %s.') % IMAGE_ID,
                version='2015.1',
                previous_status=support.SupportStatus(version='2014.2')),
            constraints=[
                constraints.CustomConstraint('glance.image')
            ],
        ),
        IMAGE_ID: properties.Schema(
            properties.Schema.STRING,
            _('Default name or UUID of the image used to boot Hadoop nodes.'),
            constraints=[
                constraints.CustomConstraint('sahara.image'),
            ],
            support_status=support.SupportStatus(version='2015.1')
        ),
        MANAGEMENT_NETWORK: properties.Schema(
            properties.Schema.STRING,
            _('Name or UUID of network.'),
            constraints=[
                constraints.CustomConstraint('neutron.network')
            ],
        ),
    }

    attributes_schema = {
        STATUS: attributes.Schema(
            _("Cluster status."),
            type=attributes.Schema.STRING
        ),
        INFO: attributes.Schema(
            _("Cluster information."),
            type=attributes.Schema.MAP
        ),
    }

    default_client_name = 'sahara'

    entity = 'clusters'

    def _validate_depr_keys(self, properties, key, depr_key):
        value = properties.get(key)
        depr_value = properties.get(depr_key)
        if value and depr_value:
            raise exception.ResourcePropertyConflict(value, depr_value)

    def _cluster_name(self):
        name = self.properties[self.NAME]
        if name:
            return name
        return self.physical_resource_name()

    def handle_create(self):
        plugin_name = self.properties[self.PLUGIN_NAME]
        hadoop_version = self.properties[self.HADOOP_VERSION]
        cluster_template_id = self.properties[self.CLUSTER_TEMPLATE_ID]
        image_id = (self.properties[self.IMAGE_ID] or
                    self.properties[self.IMAGE])
        if image_id:
            image_id = self.client_plugin('glance').get_image_id(image_id)

        # check that image is provided in case when
        # cluster template is missing one
        cluster_template = self.client().cluster_templates.get(
            cluster_template_id)
        if cluster_template.default_image_id is None and not image_id:
            msg = _("%(img)s must be provided: Referenced cluster template "
                    "%(tmpl)s has no default_image_id defined.") % {
                        'img': self.IMAGE, 'tmpl': cluster_template_id}
            raise exception.StackValidationFailed(message=msg)

        key_name = self.properties[self.KEY_NAME]
        net_id = self.properties[self.MANAGEMENT_NETWORK]
        if net_id:
            if self.is_using_neutron():
                net_id = self.client_plugin('neutron').find_neutron_resource(
                    self.properties, self.MANAGEMENT_NETWORK, 'network')
            else:
                net_id = self.client_plugin('nova').get_nova_network_id(
                    net_id)

        cluster = self.client().clusters.create(
            self._cluster_name(),
            plugin_name, hadoop_version,
            cluster_template_id=cluster_template_id,
            user_keypair_id=key_name,
            default_image_id=image_id,
            net_id=net_id)
        LOG.info(_LI('Cluster "%s" is being started.'), cluster.name)
        self.resource_id_set(cluster.id)
        return self.resource_id

    def check_create_complete(self, cluster_id):
        cluster = self.client().clusters.get(cluster_id)
        if cluster.status == self.CLUSTER_ERROR:
            raise resource.ResourceInError(resource_status=cluster.status)

        if cluster.status != self.CLUSTER_ACTIVE:
            return False

        LOG.info(_LI("Cluster '%s' has been created"), cluster.name)
        return True

    def check_delete_complete(self, resource_id):
        if not resource_id:
            return True

        try:
            cluster = self.client().clusters.get(resource_id)
        except Exception as ex:
            self.client_plugin().ignore_not_found(ex)
            LOG.info(_LI("Cluster '%s' has been deleted"),
                     self._cluster_name())
            return True
        else:
            if cluster.status == self.CLUSTER_ERROR:
                raise resource.ResourceInError(resource_status=cluster.status)

        return False

    def _resolve_attribute(self, name):
        cluster = self.client().clusters.get(self.resource_id)
        return getattr(cluster, name, None)

    def validate(self):
        res = super(SaharaCluster, self).validate()

        if res:
            return res

        self._validate_depr_keys(self.properties, self.IMAGE_ID, self.IMAGE)
        # check if running on neutron and MANAGEMENT_NETWORK missing
        if (self.is_using_neutron() and
                not self.properties[self.MANAGEMENT_NETWORK]):
            msg = _("%s must be provided"
                    ) % self.MANAGEMENT_NETWORK
            raise exception.StackValidationFailed(message=msg)


def resource_mapping():
    return {
        'OS::Sahara::Cluster': SaharaCluster,
    }
