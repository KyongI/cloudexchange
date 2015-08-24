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

from heat.common import exception
from heat.common.i18n import _
from heat.engine.clients import progress
from heat.engine import resource


class BaseVolume(resource.Resource):
    '''
    Base Volume Manager.
    '''

    default_client_name = 'cinder'

    def handle_create(self):
        backup_id = self.properties.get(self.BACKUP_ID)
        cinder = self.client()
        if backup_id is not None:
            vol_id = cinder.restores.restore(backup_id).volume_id

            vol = cinder.volumes.get(vol_id)
            kwargs = self._fetch_name_and_description(
                cinder.volume_api_version)
            cinder.volumes.update(vol_id, **kwargs)
        else:
            kwargs = self._create_arguments()
            kwargs.update(self._fetch_name_and_description(
                cinder.volume_api_version))
            vol = cinder.volumes.create(**kwargs)
        self.resource_id_set(vol.id)

        return vol.id

    def check_create_complete(self, vol_id):
        vol = self.client().volumes.get(vol_id)

        if vol.status == 'available':
            return True
        if vol.status in self._volume_creating_status:
            return False
        if vol.status == 'error':
            raise resource.ResourceInError(
                resource_status=vol.status)
        else:
            raise resource.ResourceUnknownStatus(
                resource_status=vol.status,
                result=_('Volume create failed'))

    def _name(self):
        return self.physical_resource_name()

    def _description(self):
        return self.physical_resource_name()

    def _fetch_name_and_description(self, api_version, name=None,
                                    description=None):
        if api_version == 1:
            return {'display_name': name or self._name(),
                    'display_description': description or self._description()}
        else:
            return {'name': name or self._name(),
                    'description': description or self._description()}

    def handle_check(self):
        vol = self.client().volumes.get(self.resource_id)
        statuses = ['available', 'in-use']
        checks = [
            {'attr': 'status', 'expected': statuses, 'current': vol.status},
        ]
        self._verify_check_conditions(checks)

    def handle_snapshot_delete(self, state):
        backup = state not in ((self.CREATE, self.FAILED),
                               (self.UPDATE, self.FAILED))
        prg = progress.VolumeDeleteProgress()
        prg.backup['called'] = not backup
        prg.backup['complete'] = not backup
        return prg

    def handle_delete(self):
        if self.resource_id is None:
            return progress.VolumeDeleteProgress(True)
        prg = progress.VolumeDeleteProgress()
        prg.backup['called'] = True
        prg.backup['complete'] = True
        return prg

    def _create_backup(self):
        backup = self.client().backups.create(self.resource_id)
        return backup.id

    def _check_create_backup_complete(self, prg):
        backup = self.client().backups.get(prg.backup_id)
        if backup.status == 'creating':
            return False
        if backup.status == 'available':
            return True
        else:
            raise resource.ResourceUnknownStatus(
                resource_status=backup.status,
                result=_('Volume backup failed'))

    def _delete_volume(self):
        try:
            cinder = self.client()
            vol = cinder.volumes.get(self.resource_id)
            if vol.status == 'in-use':
                raise exception.Error(_('Volume in use'))
            # if the volume is already in deleting status,
            # just wait for the deletion to complete
            if vol.status != 'deleting':
                cinder.volumes.delete(self.resource_id)
            else:
                return True
        except Exception as ex:
            self.client_plugin().ignore_not_found(ex)
            return True
        else:
            return False

    def check_delete_complete(self, prg):
        if not prg.backup['called']:
            prg.backup_id = self._create_backup()
            prg.backup['called'] = True
            return False

        if not prg.backup['complete']:
            prg.backup['complete'] = self._check_create_backup_complete(prg)
            return False

        if not prg.delete['called']:
            prg.delete['complete'] = self._delete_volume()
            prg.delete['called'] = True
            return False

        if not prg.delete['complete']:
            try:
                self.client().volumes.get(self.resource_id)
            except Exception as ex:
                self.client_plugin().ignore_not_found(ex)
                prg.delete['complete'] = True
                return True
            else:
                return False
        return True


class BaseVolumeAttachment(resource.Resource):
    '''
    Base Volume Attachment Manager.
    '''

    default_client_name = 'cinder'

    def handle_create(self):
        server_id = self.properties[self.INSTANCE_ID]
        volume_id = self.properties[self.VOLUME_ID]
        dev = self.properties[self.DEVICE]

        attach_id = self.client_plugin('nova').attach_volume(
            server_id, volume_id, dev)

        self.resource_id_set(attach_id)

        return volume_id

    def check_create_complete(self, volume_id):
        return self.client_plugin().check_attach_volume_complete(volume_id)

    def handle_delete(self):
        server_id = self.properties[self.INSTANCE_ID]
        vol_id = self.properties[self.VOLUME_ID]
        self.client_plugin('nova').detach_volume(server_id,
                                                 self.resource_id)
        prg = progress.VolumeDetachProgress(
            server_id, vol_id, self.resource_id)
        prg.called = True
        return prg

    def check_delete_complete(self, prg):
        if not prg.cinder_complete:
            prg.cinder_complete = self.client_plugin(
            ).check_detach_volume_complete(prg.vol_id)
            return False
        if not prg.nova_complete:
            prg.nova_complete = self.client_plugin(
                'nova').check_detach_volume_complete(prg.srv_id,
                                                     prg.attach_id)
            return prg.nova_complete
        return True
