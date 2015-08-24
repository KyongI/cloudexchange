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

import logging

from cinderclient import client as cc
from cinderclient import exceptions
from keystoneclient import exceptions as ks_exceptions

from heat.common import exception
from heat.common.i18n import _
from heat.common.i18n import _LI
from heat.engine.clients import client_plugin
from heat.engine import constraints
from heat.engine import resource


LOG = logging.getLogger(__name__)


class CinderClientPlugin(client_plugin.ClientPlugin):

    exceptions_module = exceptions

    service_types = [VOLUME, VOLUME_V2] = ['volume', 'volumev2']

    def get_volume_api_version(self):
        '''Returns the most recent API version.'''

        endpoint_type = self._get_client_option('cinder', 'endpoint_type')
        try:
            self.url_for(service_type=self.VOLUME_V2,
                         endpoint_type=endpoint_type)
            return 2
        except ks_exceptions.EndpointNotFound:
            try:
                self.url_for(service_type=self.VOLUME,
                             endpoint_type=endpoint_type)
                return 1
            except ks_exceptions.EndpointNotFound:
                return None

    def _create(self):

        con = self.context

        volume_api_version = self.get_volume_api_version()
        if volume_api_version == 1:
            service_type = self.VOLUME
            client_version = '1'
        elif volume_api_version == 2:
            service_type = self.VOLUME_V2
            client_version = '2'
        else:
            raise exception.Error(_('No volume service available.'))
        LOG.info(_LI('Creating Cinder client with volume API version %d.'),
                 volume_api_version)

        endpoint_type = self._get_client_option('cinder', 'endpoint_type')
        args = {
            'service_type': service_type,
            'auth_url': con.auth_url or '',
            'project_id': con.tenant,
            'username': None,
            'api_key': None,
            'endpoint_type': endpoint_type,
            'http_log_debug': self._get_client_option('cinder',
                                                      'http_log_debug'),
            'cacert': self._get_client_option('cinder', 'ca_file'),
            'insecure': self._get_client_option('cinder', 'insecure')
        }

        client = cc.Client(client_version, **args)
        management_url = self.url_for(service_type=service_type,
                                      endpoint_type=endpoint_type)
        client.client.auth_token = self.auth_token
        client.client.management_url = management_url

        client.volume_api_version = volume_api_version

        return client

    def get_volume(self, volume):
        try:
            return self.client().volumes.get(volume)
        except exceptions.NotFound as ex:
            LOG.info(_LI('Volume (%(volume)s) not found: %(ex)s'),
                     {'volume': volume, 'ex': ex})
            raise exception.EntityNotFound(entity='Volume', name=volume)

    def get_volume_snapshot(self, snapshot):
        try:
            return self.client().volume_snapshots.get(snapshot)
        except exceptions.NotFound as ex:
            LOG.info(_LI('VolumeSnapshot (%(snapshot)s) not found: %(ex)s'),
                     {'snapshot': snapshot, 'ex': ex})
            raise exception.EntityNotFound(entity='VolumeSnapshot',
                                           name=snapshot)

    def get_volume_backup(self, backup):
        try:
            return self.client().backups.get(backup)
        except exceptions.NotFound as ex:
            LOG.info(_LI('Volume backup (%(backup)s) not found: %(ex)s'),
                     {'backup': backup, 'ex': ex})
            raise exception.EntityNotFound(entity='Volume backup',
                                           name=backup)

    def get_volume_type(self, volume_type):
        vt_id = None
        volume_type_list = self.client().volume_types.list()
        for vt in volume_type_list:
            if vt.name == volume_type:
                vt_id = vt.id
                break
            if vt.id == volume_type:
                vt_id = vt.id
                break
        if vt_id is None:
            raise exception.EntityNotFound(entity='VolumeType',
                                           name=volume_type)

        return vt_id

    def is_not_found(self, ex):
        return isinstance(ex, exceptions.NotFound)

    def is_over_limit(self, ex):
        return isinstance(ex, exceptions.OverLimit)

    def is_conflict(self, ex):
        return (isinstance(ex, exceptions.ClientException) and
                ex.code == 409)

    def check_detach_volume_complete(self, vol_id):
        try:
            vol = self.client().volumes.get(vol_id)
        except Exception as ex:
            self.ignore_not_found(ex)
            return True

        if vol.status in ('in-use', 'detaching'):
            LOG.debug('%s - volume still in use' % vol_id)
            return False

        LOG.debug('Volume %(id)s - status: %(status)s' % {
            'id': vol.id, 'status': vol.status})

        if vol.status not in ('available', 'deleting'):
            LOG.debug("Detachment failed - volume %(vol)s "
                      "is in %(status)s status" % {"vol": vol.id,
                                                   "status": vol.status})
            raise resource.ResourceUnknownStatus(
                resource_status=vol.status,
                result=_('Volume detachment failed'))
        else:
            return True

    def check_attach_volume_complete(self, vol_id):
        vol = self.client().volumes.get(vol_id)
        if vol.status in ('available', 'attaching'):
            LOG.debug("Volume %(id)s is being attached - "
                      "volume status: %(status)s" % {'id': vol_id,
                                                     'status': vol.status})
            return False

        if vol.status != 'in-use':
            LOG.debug("Attachment failed - volume %(vol)s is "
                      "in %(status)s status" % {"vol": vol_id,
                                                "status": vol.status})
            raise resource.ResourceUnknownStatus(
                resource_status=vol.status,
                result=_('Volume attachment failed'))

        LOG.info(_LI('Attaching volume %(id)s complete'), {'id': vol_id})
        return True


class VolumeConstraint(constraints.BaseCustomConstraint):

    expected_exceptions = (exception.EntityNotFound,)

    def validate_with_client(self, client, volume):
        client.client_plugin('cinder').get_volume(volume)


class VolumeSnapshotConstraint(constraints.BaseCustomConstraint):

    expected_exceptions = (exception.EntityNotFound,)

    def validate_with_client(self, client, snapshot):
        client.client_plugin('cinder').get_volume_snapshot(snapshot)


class VolumeTypeConstraint(constraints.BaseCustomConstraint):

    expected_exceptions = (exception.EntityNotFound,)

    def validate_with_client(self, client, volume_type):
        client.client_plugin('cinder').get_volume_type(volume_type)


class VolumeBackupConstraint(constraints.BaseCustomConstraint):

    expected_exceptions = (exception.EntityNotFound,)

    def validate_with_client(self, client, backup):
        client.client_plugin('cinder').get_volume_backup(backup)
