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
from heat.common.i18n import _LI
from heat.common.i18n import _LW
from heat.engine import attributes
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine import support

LOG = logging.getLogger(__name__)


class TroveCluster(resource.Resource):

    support_status = support.SupportStatus(version='2015.1')

    TROVE_STATUS = (
        ERROR, FAILED, ACTIVE,
    ) = (
        'ERROR', 'FAILED', 'ACTIVE',
    )

    TROVE_STATUS_REASON = {
        FAILED: _('The database instance was created, but heat failed to set '
                  'up the datastore. If a database instance is in the FAILED '
                  'state, it should be deleted and a new one should be '
                  'created.'),
        ERROR: _('The last operation for the database instance failed due to '
                 'an error.'),
    }

    BAD_STATUSES = (ERROR, FAILED)

    PROPERTIES = (
        NAME, DATASTORE_TYPE, DATASTORE_VERSION, INSTANCES,
    ) = (
        'name', 'datastore_type', 'datastore_version', 'instances',
    )

    _INSTANCE_KEYS = (
        FLAVOR, VOLUME_SIZE,
    ) = (
        'flavor', 'volume_size',
    )

    ATTRIBUTES = (
        INSTANCES_ATTR, IP
    ) = (
        'instances', 'ip'
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the cluster to create.'),
            constraints=[
                constraints.Length(max=255),
            ]
        ),
        DATASTORE_TYPE: properties.Schema(
            properties.Schema.STRING,
            _("Name of registered datastore type."),
            required=True,
            constraints=[
                constraints.Length(max=255)
            ]
        ),
        DATASTORE_VERSION: properties.Schema(
            properties.Schema.STRING,
            _("Name of the registered datastore version. "
              "It must exist for provided datastore type. "
              "Defaults to using single active version. "
              "If several active versions exist for provided datastore type, "
              "explicit value for this parameter must be specified."),
            required=True,
            constraints=[constraints.Length(max=255)]
        ),
        INSTANCES: properties.Schema(
            properties.Schema.LIST,
            _("List of database instances."),
            required=True,
            schema=properties.Schema(
                properties.Schema.MAP,
                schema={
                    FLAVOR: properties.Schema(
                        properties.Schema.STRING,
                        _('Flavor of the instance.'),
                        required=True,
                        constraints=[
                            constraints.CustomConstraint('trove.flavor')
                        ]
                    ),
                    VOLUME_SIZE: properties.Schema(
                        properties.Schema.INTEGER,
                        _('Size of the instance disk volume in GB.'),
                        required=True,
                        constraints=[
                            constraints.Range(1, 150),
                        ]
                    )
                }
            )
        )
    }

    attributes_schema = {
        INSTANCES: attributes.Schema(
            _("A list of instances ids."),
            type=attributes.Schema.LIST
        ),
        IP: attributes.Schema(
            _("A list of cluster instance IPs."),
            type=attributes.Schema.LIST
        )
    }

    default_client_name = 'trove'

    entity = 'clusters'

    def _cluster_name(self):
        return self.properties[self.NAME] or self.physical_resource_name()

    def handle_create(self):
        datastore_type = self.properties[self.DATASTORE_TYPE]
        datastore_version = self.properties[self.DATASTORE_VERSION]

        # convert instances to format required by troveclient
        instances = []
        for instance in self.properties[self.INSTANCES]:
            instances.append({
                'flavorRef': self.client_plugin().get_flavor_id(
                    instance[self.FLAVOR]),
                'volume': {'size': instance[self.VOLUME_SIZE]}
            })

        args = {
            'name': self._cluster_name(),
            'datastore': datastore_type,
            'datastore_version': datastore_version,
            'instances': instances
        }
        cluster = self.client().clusters.create(**args)
        self.resource_id_set(cluster.id)
        return cluster.id

    def _refresh_cluster(self, cluster_id):
        try:
            cluster = self.client().clusters.get(cluster_id)
            return cluster
        except Exception as exc:
            if self.client_plugin().is_over_limit(exc):
                LOG.warn(_LW("Stack %(name)s (%(id)s) received an "
                             "OverLimit response during clusters.get():"
                             " %(exception)s"),
                         {'name': self.stack.name,
                          'id': self.stack.id,
                          'exception': exc})
                return None
            else:
                raise

    def check_create_complete(self, cluster_id):
        cluster = self._refresh_cluster(cluster_id)

        if cluster is None:
            return False

        for instance in cluster.instances:
            if instance['status'] in self.BAD_STATUSES:
                raise resource.ResourceInError(
                    resource_status=instance['status'],
                    status_reason=self.TROVE_STATUS_REASON.get(
                        instance['status'], _("Unknown")))

            if instance['status'] != self.ACTIVE:
                return False

        LOG.info(_LI("Cluster '%s' has been created"), cluster.name)
        return True

    def handle_delete(self):
        if not self.resource_id:
            return

        try:
            cluster = self.client().clusters.get(self.resource_id)
        except Exception as ex:
            self.client_plugin().ignore_not_found(ex)
        else:
            cluster.delete()
            return cluster.id

    def check_delete_complete(self, cluster_id):
        if not cluster_id:
            return True

        try:
            # For some time trove cluster may continue to live
            self._refresh_cluster(cluster_id)
        except Exception as ex:
            self.client_plugin().ignore_not_found(ex)
            return True

        return False

    def validate(self):
        res = super(TroveCluster, self).validate()
        if res:
            return res

        datastore_type = self.properties[self.DATASTORE_TYPE]
        datastore_version = self.properties[self.DATASTORE_VERSION]

        self.client_plugin().validate_datastore(
            datastore_type, datastore_version,
            self.DATASTORE_TYPE, self.DATASTORE_VERSION)

    def _resolve_attribute(self, name):
        if name == self.INSTANCES_ATTR:
            instances = []
            cluster = self.client().clusters.get(self.resource_id)
            for instance in cluster.instances:
                instances.append(instance['id'])
            return instances
        elif name == self.IP:
            cluster = self.client().clusters.get(self.resource_id)
            return cluster.ip


def resource_mapping():
    return {
        'OS::Trove::Cluster': TroveCluster
    }
