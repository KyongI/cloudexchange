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

from glanceclient import exc as glance_exceptions
import mock
import six

from heat.common import exception
from heat.common import template_format
from heat.engine.resources.openstack.glance import glance_image as gi
from heat.engine import stack as parser
from heat.engine import template
from heat.tests import common
from heat.tests import utils

image_template = '''
heat_template_version: 2013-05-23
description: This template to define a glance image.
resources:
  my_image:
    type: OS::Glance::Image
    properties:
      name: cirros_image
      id: 41f0e60c-ebb4-4375-a2b4-845ae8b9c995
      disk_format: qcow2
      container_format: bare
      is_public: True
      min_disk: 10
      min_ram: 512
      protected: False
      location: https://launchpad.net/cirros/cirros-0.3.0-x86_64-disk.img
'''

image_template_validate = '''
heat_template_version: 2013-05-23
description: This template to define a glance image.
resources:
  image:
    type: OS::Glance::Image
    properties:
      name: image_validate
      disk_format: qcow2
      container_format: bare
      location: https://launchpad.net/cirros/cirros-0.3.0-x86_64-disk.img
'''


class GlanceImageTest(common.HeatTestCase):
    def setUp(self):
        super(GlanceImageTest, self).setUp()

        utils.setup_dummy_db()
        self.ctx = utils.dummy_context()

        tpl = template_format.parse(image_template)
        self.stack = parser.Stack(
            self.ctx, 'glance_image_test_stack',
            template.Template(tpl)
        )

        self.my_image = self.stack['my_image']
        glance = mock.MagicMock()
        self.glanceclient = mock.MagicMock()
        self.my_image.client = glance
        glance.return_value = self.glanceclient
        self.images = self.glanceclient.images

    def _test_validate(self, resource, error_msg):
        exc = self.assertRaises(exception.StackValidationFailed,
                                resource.validate)
        self.assertIn(error_msg, six.text_type(exc))

    def test_resource_mapping(self):
        mapping = gi.resource_mapping()
        self.assertEqual(1, len(mapping))
        self.assertEqual(gi.GlanceImage, mapping['OS::Glance::Image'])
        self.assertIsInstance(self.my_image, gi.GlanceImage)

    def test_invalid_min_disk(self):
        # invalid 'min_disk'
        tpl = template_format.parse(image_template_validate)
        stack = parser.Stack(
            self.ctx, 'glance_image_stack_validate',
            template.Template(tpl)
        )
        image = stack['image']
        image.t['Properties']['min_disk'] = -1
        error_msg = ('Property error: resources.image.properties.min_disk: '
                     '-1 is out of range (min: 0, max: None)')
        self._test_validate(image, error_msg)

    def test_invalid_min_ram(self):
        # invalid 'min_ram'
        tpl = template_format.parse(image_template_validate)
        stack = parser.Stack(
            self.ctx, 'glance_image_stack_validate',
            template.Template(tpl)
        )
        image = stack['image']
        image.t['Properties']['min_ram'] = -1
        error_msg = ('Property error: resources.image.properties.min_ram: '
                     '-1 is out of range (min: 0, max: None)')
        self._test_validate(image, error_msg)

    def test_miss_disk_format(self):
        # miss disk_format
        tpl = template_format.parse(image_template_validate)
        stack = parser.Stack(
            self.ctx, 'glance_image_stack_validate',
            template.Template(tpl)
        )
        image = stack['image']
        image.t['Properties'].pop('disk_format')
        error_msg = 'Property disk_format not assigned'
        self._test_validate(image, error_msg)

    def test_invalid_disk_format(self):
        # invalid disk_format
        tpl = template_format.parse(image_template_validate)
        stack = parser.Stack(
            self.ctx, 'glance_image_stack_validate',
            template.Template(tpl)
        )
        image = stack['image']
        image.t['Properties']['disk_format'] = 'incorrect_format'
        error_msg = ('Property error: '
                     'resources.image.properties.disk_format: '
                     '"incorrect_format" is not an allowed value '
                     '[ami, ari, aki, vhd, vmdk, raw, qcow2, vdi, iso]')
        self._test_validate(image, error_msg)

    def test_miss_container_format(self):
        # miss container_format
        tpl = template_format.parse(image_template_validate)
        stack = parser.Stack(
            self.ctx, 'glance_image_stack_validate',
            template.Template(tpl)
        )
        image = stack['image']
        image.t['Properties'].pop('container_format')
        error_msg = 'Property container_format not assigned'
        self._test_validate(image, error_msg)

    def test_invalid_container_format(self):
        # invalid container_format
        tpl = template_format.parse(image_template_validate)
        stack = parser.Stack(
            self.ctx, 'glance_image_stack_validate',
            template.Template(tpl)
        )
        image = stack['image']
        image.t['Properties']['container_format'] = 'incorrect_format'
        error_msg = ('Property error: '
                     'resources.image.properties.container_format: '
                     '"incorrect_format" is not an allowed value '
                     '[ami, ari, aki, bare, ova, ovf]')
        self._test_validate(image, error_msg)

    def test_miss_location(self):
        # miss location
        tpl = template_format.parse(image_template_validate)
        stack = parser.Stack(
            self.ctx, 'glance_image_stack_validate',
            template.Template(tpl)
        )
        image = stack['image']
        image.t['Properties'].pop('location')
        error_msg = 'Property location not assigned'
        self._test_validate(image, error_msg)

    def test_image_handle_create(self):
        value = mock.MagicMock()
        image_id = '41f0e60c-ebb4-4375-a2b4-845ae8b9c995'
        value.id = image_id
        self.images.create.return_value = value
        self.my_image.handle_create()
        self.assertEqual(image_id, self.my_image.resource_id)

    def test_image_handle_delete(self):
        self.resource_id = None
        self.assertIsNone(self.my_image.handle_delete())
        image_id = '41f0e60c-ebb4-4375-a2b4-845ae8b9c995'
        self.my_image.resource_id = image_id
        self.images.delete.return_value = None
        self.assertEqual('41f0e60c-ebb4-4375-a2b4-845ae8b9c995',
                         self.my_image.handle_delete())
        self.images.delete.side_effect = glance_exceptions.HTTPNotFound(404)
        self.assertIsNone(self.my_image.handle_delete())

    def test_image_show_resourse_v1(self):
        self.glanceclient.version = 1.0
        self.my_image.resource_id = 'test_image_id'
        image = mock.MagicMock()
        images = mock.MagicMock()
        image.to_dict.return_value = {'image': 'info'}
        images.get.return_value = image
        self.my_image.client().images = images
        self.assertEqual({'image': 'info'}, self.my_image.FnGetAtt('show'))
        images.get.assert_called_once_with('test_image_id')

    def test_image_show_resourse_v2(self):
        self.my_image.resource_id = 'test_image_id'
        # glance image in v2 is warlock.model object, so it can be
        # handled via dict(). In test we use easiest analog - dict.
        image = {"key1": "val1", "key2": "val2"}
        self.images.get.return_value = image
        self.glanceclient.version = 2.0
        self.assertEqual({"key1": "val1", "key2": "val2"},
                         self.my_image.FnGetAtt('show'))
        self.images.get.assert_called_once_with('test_image_id')
