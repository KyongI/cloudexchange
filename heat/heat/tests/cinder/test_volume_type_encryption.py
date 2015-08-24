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

from heat.engine.resources.openstack.cinder import cinder_encrypted_vol_type
from heat.engine import stack
from heat.engine import template
from heat.tests import common
from heat.tests import utils

cinder_volume_type_encryption = {
    'heat_template_version': '2015-04-30',
    'resources': {
        'my_encrypted_vol_type': {
            'type': 'OS::Cinder::EncryptedVolumeType',
            'properties': {
                'provider': 'nova.volume.encryptors.luks.LuksEncryptor',
                'control_location': 'front-end',
                'cipher': 'aes-xts-plain64',
                'key_size': '512',
                'volume_type': '01bd581d-33fe-4d6d-bd7b-70ae076d39fb'
            }
        }
    }
}


class CinderEncryptedVolumeTypeTest(common.HeatTestCase):
    def setUp(self):
        super(CinderEncryptedVolumeTypeTest, self).setUp()

        self.ctx = utils.dummy_context()

        self.stack = stack.Stack(
            self.ctx, 'cinder_vol_type_encryption_test_stack',
            template.Template(cinder_volume_type_encryption)
        )

        self.my_encrypted_vol_type = self.stack['my_encrypted_vol_type']
        cinder = mock.MagicMock()
        self.cinderclient = mock.MagicMock()
        self.my_encrypted_vol_type.client = cinder
        cinder.return_value = self.cinderclient
        self.volume_encryption_types = \
            self.cinderclient.volume_encryption_types

    def test_resource_mapping(self):
        mapping = cinder_encrypted_vol_type.resource_mapping()
        self.assertEqual(1, len(mapping))
        self.assertEqual(cinder_encrypted_vol_type.CinderEncryptedVolumeType,
                         mapping['OS::Cinder::EncryptedVolumeType'])
        self.assertIsInstance(
            self.my_encrypted_vol_type,
            cinder_encrypted_vol_type.CinderEncryptedVolumeType
        )

    def test_handle_create(self):
        value = mock.MagicMock()
        volume_type_id = '01bd581d-33fe-4d6d-bd7b-70ae076d39fb'
        value.volume_type_id = volume_type_id
        self.volume_encryption_types.create.return_value = value

        with mock.patch.object(self.my_encrypted_vol_type.client_plugin(),
                               'get_volume_type') as mock_get_volume_type:
            mock_get_volume_type.return_value = volume_type_id
            self.my_encrypted_vol_type.handle_create()
            mock_get_volume_type.assert_called_once_with(volume_type_id)

        specs = {
            'control_location': 'front-end',
            'cipher': 'aes-xts-plain64',
            'key_size': 512,
            'provider': 'nova.volume.encryptors.luks.LuksEncryptor'
        }
        self.volume_encryption_types.create.assert_called_once_with(
            volume_type=volume_type_id, specs=specs)
        self.assertEqual(volume_type_id,
                         self.my_encrypted_vol_type.resource_id)

    def test_handle_update(self):
        update_args = {
            'control_location': 'back-end',
            'key_size': 256,
            'cipher': 'aes-cbc-essiv',
            'provider':
                'nova.volume.encryptors.cryptsetup.CryptsetupEncryptor'
        }
        volume_type_id = '01bd581d-33fe-4d6d-bd7b-70ae076d39fb'
        self.my_encrypted_vol_type.resource_id = volume_type_id
        self.my_encrypted_vol_type.handle_update(json_snippet=None,
                                                 tmpl_diff=None,
                                                 prop_diff=update_args)

        self.volume_encryption_types.update.assert_called_once_with(
            volume_type=volume_type_id, specs=update_args)

    def test_handle_delete(self):
        volume_type_id = '01bd581d-33fe-4d6d-bd7b-70ae076d39fb'
        self.my_encrypted_vol_type.resource_id = volume_type_id
        self.volume_encryption_types.delete.return_value = None
        self.assertEqual('01bd581d-33fe-4d6d-bd7b-70ae076d39fb',
                         self.my_encrypted_vol_type.handle_delete())

    def test_handle_delete_rsrc_not_found(self):
        exc = self.cinderclient.HTTPClientError('Not Found.')
        self.volume_encryption_types.delete.side_effect = exc
        self.assertIsNone(self.my_encrypted_vol_type.handle_delete())
