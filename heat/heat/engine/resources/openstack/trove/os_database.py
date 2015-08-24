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

from heat.common import exception
from heat.common.i18n import _
from heat.common.i18n import _LI
from heat.common.i18n import _LW
from heat.engine import attributes
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine import support

LOG = logging.getLogger(__name__)


class OSDBInstance(resource.Resource):
    '''
    OpenStack cloud database instance resource.
    '''

    support_status = support.SupportStatus(version='2014.1')

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
        NAME, FLAVOR, SIZE, DATABASES, USERS, AVAILABILITY_ZONE,
        RESTORE_POINT, DATASTORE_TYPE, DATASTORE_VERSION, NICS,
        REPLICA_OF, REPLICA_COUNT,
    ) = (
        'name', 'flavor', 'size', 'databases', 'users', 'availability_zone',
        'restore_point', 'datastore_type', 'datastore_version', 'networks',
        'replica_of', 'replica_count'
    )

    _DATABASE_KEYS = (
        DATABASE_CHARACTER_SET, DATABASE_COLLATE, DATABASE_NAME,
    ) = (
        'character_set', 'collate', 'name',
    )

    _USER_KEYS = (
        USER_NAME, USER_PASSWORD, USER_HOST, USER_DATABASES,
    ) = (
        'name', 'password', 'host', 'databases',
    )

    _NICS_KEYS = (
        NET, PORT, V4_FIXED_IP
    ) = (
        'network', 'port', 'fixed_ip'
    )

    ATTRIBUTES = (
        HOSTNAME, HREF,
    ) = (
        'hostname', 'href',
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the DB instance to create.'),
            constraints=[
                constraints.Length(max=255),
            ]
        ),
        FLAVOR: properties.Schema(
            properties.Schema.STRING,
            _('Reference to a flavor for creating DB instance.'),
            required=True,
            constraints=[
                constraints.CustomConstraint('trove.flavor')
            ]
        ),
        DATASTORE_TYPE: properties.Schema(
            properties.Schema.STRING,
            _("Name of registered datastore type."),
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
            constraints=[constraints.Length(max=255)]
        ),
        SIZE: properties.Schema(
            properties.Schema.INTEGER,
            _('Database volume size in GB.'),
            required=True,
            constraints=[
                constraints.Range(1, 150),
            ]
        ),
        NICS: properties.Schema(
            properties.Schema.LIST,
            _("List of network interfaces to create on instance."),
            default=[],
            schema=properties.Schema(
                properties.Schema.MAP,
                schema={
                    NET: properties.Schema(
                        properties.Schema.STRING,
                        _('Name or UUID of the network to attach this NIC to. '
                          'Either %(port)s or %(net)s must be specified.') % {
                              'port': PORT, 'net': NET},
                        constraints=[
                            constraints.CustomConstraint('neutron.network')
                        ]
                    ),
                    PORT: properties.Schema(
                        properties.Schema.STRING,
                        _('Name or UUID of Neutron port to attach this '
                          'NIC to. '
                          'Either %(port)s or %(net)s must be specified.') % {
                              'port': PORT, 'net': NET},
                        constraints=[
                            constraints.CustomConstraint('neutron.port')
                        ],
                    ),
                    V4_FIXED_IP: properties.Schema(
                        properties.Schema.STRING,
                        _('Fixed IPv4 address for this NIC.'),
                        constraints=[
                            constraints.CustomConstraint('ip_addr')
                        ]
                    ),
                },
            ),
        ),
        DATABASES: properties.Schema(
            properties.Schema.LIST,
            _('List of databases to be created on DB instance creation.'),
            default=[],
            schema=properties.Schema(
                properties.Schema.MAP,
                schema={
                    DATABASE_CHARACTER_SET: properties.Schema(
                        properties.Schema.STRING,
                        _('Set of symbols and encodings.'),
                        default='utf8'
                    ),
                    DATABASE_COLLATE: properties.Schema(
                        properties.Schema.STRING,
                        _('Set of rules for comparing characters in a '
                          'character set.'),
                        default='utf8_general_ci'
                    ),
                    DATABASE_NAME: properties.Schema(
                        properties.Schema.STRING,
                        _('Specifies database names for creating '
                          'databases on instance creation.'),
                        required=True,
                        constraints=[
                            constraints.Length(max=64),
                            constraints.AllowedPattern(r'[a-zA-Z0-9_]+'
                                                       r'[a-zA-Z0-9_@?#\s]*'
                                                       r'[a-zA-Z0-9_]+'),
                        ]
                    ),
                },
            )
        ),
        USERS: properties.Schema(
            properties.Schema.LIST,
            _('List of users to be created on DB instance creation.'),
            default=[],
            schema=properties.Schema(
                properties.Schema.MAP,
                schema={
                    USER_NAME: properties.Schema(
                        properties.Schema.STRING,
                        _('User name to create a user on instance '
                          'creation.'),
                        required=True,
                        constraints=[
                            constraints.Length(max=16),
                            constraints.AllowedPattern(r'[a-zA-Z0-9_]+'
                                                       r'[a-zA-Z0-9_@?#\s]*'
                                                       r'[a-zA-Z0-9_]+'),
                        ]
                    ),
                    USER_PASSWORD: properties.Schema(
                        properties.Schema.STRING,
                        _('Password for those users on instance '
                          'creation.'),
                        required=True,
                        constraints=[
                            constraints.AllowedPattern(r'[a-zA-Z0-9_]+'
                                                       r'[a-zA-Z0-9_@?#\s]*'
                                                       r'[a-zA-Z0-9_]+'),
                        ]
                    ),
                    USER_HOST: properties.Schema(
                        properties.Schema.STRING,
                        _('The host from which a user is allowed to '
                          'connect to the database.'),
                        default='%'
                    ),
                    USER_DATABASES: properties.Schema(
                        properties.Schema.LIST,
                        _('Names of databases that those users can '
                          'access on instance creation.'),
                        schema=properties.Schema(
                            properties.Schema.STRING,
                        ),
                        required=True,
                        constraints=[
                            constraints.Length(min=1),
                        ]
                    ),
                },
            )
        ),
        AVAILABILITY_ZONE: properties.Schema(
            properties.Schema.STRING,
            _('Name of the availability zone for DB instance.')
        ),
        RESTORE_POINT: properties.Schema(
            properties.Schema.STRING,
            _('DB instance restore point.')
        ),
        REPLICA_OF: properties.Schema(
            properties.Schema.STRING,
            _('Identifier of the source instance to replicate.'),
            support_status=support.SupportStatus(version='5.0.0')
        ),
        REPLICA_COUNT: properties.Schema(
            properties.Schema.INTEGER,
            _('The number of replicas to be created.'),
            support_status=support.SupportStatus(version='5.0.0')
        ),
    }

    attributes_schema = {
        HOSTNAME: attributes.Schema(
            _("Hostname of the instance."),
            type=attributes.Schema.STRING
        ),
        HREF: attributes.Schema(
            _("Api endpoint reference of the instance."),
            type=attributes.Schema.STRING
        ),
    }

    default_client_name = 'trove'

    entity = 'instances'

    def __init__(self, name, json_snippet, stack):
        super(OSDBInstance, self).__init__(name, json_snippet, stack)
        self._href = None
        self._dbinstance = None

    @property
    def dbinstance(self):
        """Get the trove dbinstance."""
        if not self._dbinstance and self.resource_id:
            self._dbinstance = self.client().instances.get(self.resource_id)

        return self._dbinstance

    def _dbinstance_name(self):
        name = self.properties[self.NAME]
        if name:
            return name

        return self.physical_resource_name()

    def handle_create(self):
        '''
        Create cloud database instance.
        '''
        self.flavor = self.client_plugin().get_flavor_id(
            self.properties[self.FLAVOR])
        self.volume = {'size': self.properties[self.SIZE]}
        self.databases = self.properties[self.DATABASES]
        self.users = self.properties[self.USERS]
        restore_point = self.properties[self.RESTORE_POINT]
        if restore_point:
            restore_point = {"backupRef": restore_point}
        zone = self.properties[self.AVAILABILITY_ZONE]
        self.datastore_type = self.properties[self.DATASTORE_TYPE]
        self.datastore_version = self.properties[self.DATASTORE_VERSION]
        replica_of = self.properties[self.REPLICA_OF]
        replica_count = self.properties[self.REPLICA_COUNT]

        # convert user databases to format required for troveclient.
        # that is, list of database dictionaries
        for user in self.users:
            dbs = [{'name': db} for db in user.get(self.USER_DATABASES, [])]
            user[self.USER_DATABASES] = dbs

        # convert networks to format required by troveclient
        nics = []
        for nic in self.properties[self.NICS]:
            nic_dict = {}
            net = nic.get(self.NET)
            if net:
                if self.is_using_neutron():
                    net_id = (self.client_plugin(
                        'neutron').find_neutron_resource(
                        nic, self.NET, 'network'))
                else:
                    net_id = (self.client_plugin(
                        'nova').get_nova_network_id(net))
                nic_dict['net-id'] = net_id
            port = nic.get(self.PORT)
            if port:
                neutron = self.client_plugin('neutron')
                nic_dict['port-id'] = neutron.find_neutron_resource(
                    nic, self.PORT, 'port')
            ip = nic.get(self.V4_FIXED_IP)
            if ip:
                nic_dict['v4-fixed-ip'] = ip
            nics.append(nic_dict)

        # create db instance
        instance = self.client().instances.create(
            self._dbinstance_name(),
            self.flavor,
            volume=self.volume,
            databases=self.databases,
            users=self.users,
            restorePoint=restore_point,
            availability_zone=zone,
            datastore=self.datastore_type,
            datastore_version=self.datastore_version,
            nics=nics,
            replica_of=replica_of,
            replica_count=replica_count)
        self.resource_id_set(instance.id)

        return instance.id

    def _refresh_instance(self, instance_id):
        try:
            instance = self.client().instances.get(instance_id)
            return instance
        except Exception as exc:
            if self.client_plugin().is_over_limit(exc):
                LOG.warn(_LW("Stack %(name)s (%(id)s) received an "
                             "OverLimit response during instance.get():"
                             " %(exception)s"),
                         {'name': self.stack.name,
                          'id': self.stack.id,
                          'exception': exc})
                return None
            else:
                raise

    def check_create_complete(self, instance_id):
        '''
        Check if cloud DB instance creation is complete.
        '''
        instance = self._refresh_instance(instance_id)  # refresh attributes
        if instance is None:
            return False
        if instance.status in self.BAD_STATUSES:
            raise resource.ResourceInError(
                resource_status=instance.status,
                status_reason=self.TROVE_STATUS_REASON.get(instance.status,
                                                           _("Unknown")))

        if instance.status != self.ACTIVE:
            return False
        LOG.info(_LI("Database instance %(database)s created (flavor:%("
                     "flavor)s,volume:%(volume)s, datastore:%("
                     "datastore_type)s, datastore_version:%("
                     "datastore_version)s)"),
                 {'database': self._dbinstance_name(),
                  'flavor': self.flavor,
                  'volume': self.volume,
                  'datastore_type': self.datastore_type,
                  'datastore_version': self.datastore_version})
        return True

    def handle_check(self):
        instance = self.client().instances.get(self.resource_id)
        status = instance.status
        checks = [
            {'attr': 'status', 'expected': self.ACTIVE, 'current': status},
        ]
        self._verify_check_conditions(checks)

    def handle_delete(self):
        '''
        Delete a cloud database instance.
        '''
        if not self.resource_id:
            return

        try:
            instance = self.client().instances.get(self.resource_id)
        except Exception as ex:
            self.client_plugin().ignore_not_found(ex)
        else:
            instance.delete()
            return instance.id

    def check_delete_complete(self, instance_id):
        '''
        Check for completion of cloud DB instance deletion
        '''
        if not instance_id:
            return True

        try:
            # For some time trove instance may continue to live
            self._refresh_instance(instance_id)
        except Exception as ex:
            self.client_plugin().ignore_not_found(ex)
            return True

        return False

    def validate(self):
        '''
        Validate any of the provided params
        '''
        res = super(OSDBInstance, self).validate()
        if res:
            return res

        datastore_type = self.properties[self.DATASTORE_TYPE]
        datastore_version = self.properties[self.DATASTORE_VERSION]

        self.client_plugin().validate_datastore(
            datastore_type, datastore_version,
            self.DATASTORE_TYPE, self.DATASTORE_VERSION)

        # check validity of user and databases
        users = self.properties[self.USERS]
        if users:
            databases = self.properties[self.DATABASES]
            if not databases:
                msg = _('Databases property is required if users property '
                        'is provided for resource %s.') % self.name
                raise exception.StackValidationFailed(message=msg)

            db_names = set([db[self.DATABASE_NAME] for db in databases])
            for user in users:
                missing_db = [db_name for db_name in user[self.USER_DATABASES]
                              if db_name not in db_names]

                if missing_db:
                    msg = (_('Database %(dbs)s specified for user does '
                             'not exist in databases for resource %(name)s.')
                           % {'dbs': missing_db, 'name': self.name})
                    raise exception.StackValidationFailed(message=msg)

        # check validity of NICS
        is_neutron = self.is_using_neutron()
        nics = self.properties[self.NICS]
        for nic in nics:
            if not is_neutron and nic.get(self.PORT):
                msg = _("Can not use %s property on Nova-network.") % self.PORT
                raise exception.StackValidationFailed(message=msg)

            if bool(nic.get(self.NET)) == bool(nic.get(self.PORT)):
                msg = _("Either %(net)s or %(port)s must be provided.") % {
                    'net': self.NET, 'port': self.PORT}
                raise exception.StackValidationFailed(message=msg)

    def href(self):
        if not self._href and self.dbinstance:
            if not self.dbinstance.links:
                self._href = None
            else:
                for link in self.dbinstance.links:
                    if link['rel'] == 'self':
                        self._href = link[self.HREF]
                        break

        return self._href

    def _resolve_attribute(self, name):
        if name == self.HOSTNAME:
            return self.dbinstance.hostname
        elif name == self.HREF:
            return self.href()


def resource_mapping():
    return {
        'OS::Trove::Instance': OSDBInstance,
    }
