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

import uuid

import mock
from saharaclient.api import base as sahara_base
import six

from heat.common import exception
from heat.engine.clients.os import sahara
from heat.tests import common
from heat.tests import utils


class SaharaUtilsTests(common.HeatTestCase):
    """
    Basic tests for the helper methods in
    :module:'heat.engine.resources.clients.os.sahara'.
    """

    def setUp(self):
        super(SaharaUtilsTests, self).setUp()
        self.sahara_client = mock.MagicMock()
        con = utils.dummy_context()
        c = con.clients
        self.sahara_plugin = c.client_plugin('sahara')
        self.sahara_plugin._client = self.sahara_client
        self.my_image = mock.MagicMock()

    def test_get_image_id(self):
        """Tests the get_image_id function."""
        img_id = str(uuid.uuid4())
        img_name = 'myfakeimage'
        self.my_image.id = img_id
        self.my_image.name = img_name
        self.sahara_client.images.get.return_value = self.my_image
        self.sahara_client.images.find.side_effect = [[self.my_image], []]

        self.assertEqual(img_id, self.sahara_plugin.get_image_id(img_id))
        self.assertEqual(img_id, self.sahara_plugin.get_image_id(img_name))
        self.assertRaises(exception.EntityNotFound,
                          self.sahara_plugin.get_image_id, 'noimage')

        calls = [mock.call(name=img_name),
                 mock.call(name='noimage')]
        self.sahara_client.images.get.assert_called_once_with(img_id)
        self.sahara_client.images.find.assert_has_calls(calls)

    def test_get_image_id_by_name_in_uuid(self):
        """Tests the get_image_id function by name in uuid."""
        img_id = str(uuid.uuid4())
        img_name = str(uuid.uuid4())
        self.my_image.id = img_id
        self.my_image.name = img_name
        self.sahara_client.images.get.side_effect = [
            sahara_base.APIException(error_code=400,
                                     error_name='IMAGE_NOT_REGISTERED')]

        self.sahara_client.images.find.return_value = [self.my_image]
        self.assertEqual(img_id, self.sahara_plugin.get_image_id(img_name))

        self.sahara_client.images.get.assert_called_once_with(img_name)
        self.sahara_client.images.find.assert_called_once_with(name=img_name)

    def test_get_image_id_sahara_exception(self):
        """Test get_image_id when sahara raises an exception."""
        # Simulate HTTP exception
        img_name = str(uuid.uuid4())
        self.sahara_client.images.find.side_effect = [
            sahara_base.APIException(error_message="Error", error_code=404)]

        expected_error = "Error retrieving image list from sahara: Error"
        e = self.assertRaises(exception.Error,
                              self.sahara_plugin.get_image_id_by_name,
                              img_name)
        self.assertEqual(expected_error, six.text_type(e))

        self.sahara_client.images.find.assert_called_once_with(name=img_name)

    def test_get_image_id_not_found(self):
        """Tests the get_image_id function while image is not found."""
        img_name = str(uuid.uuid4())
        self.my_image.name = img_name
        self.sahara_client.images.get.side_effect = [
            sahara_base.APIException(error_code=400,
                                     error_name='IMAGE_NOT_REGISTERED')]
        self.sahara_client.images.find.return_value = []

        self.assertRaises(exception.EntityNotFound,
                          self.sahara_plugin.get_image_id, img_name)

        self.sahara_client.images.get.assert_called_once_with(img_name)
        self.sahara_client.images.find.assert_called_once_with(name=img_name)

    def test_get_image_id_name_ambiguity(self):
        """Tests the get_image_id function while name ambiguity ."""
        img_name = 'ambiguity_name'
        self.my_image.name = img_name

        self.sahara_client.images.find.return_value = [self.my_image,
                                                       self.my_image]
        self.assertRaises(exception.PhysicalResourceNameAmbiguity,
                          self.sahara_plugin.get_image_id, img_name)
        self.sahara_client.images.find.assert_called_once_with(name=img_name)


class ImageConstraintTest(common.HeatTestCase):

    def setUp(self):
        super(ImageConstraintTest, self).setUp()
        self.ctx = utils.dummy_context()
        self.mock_get_image = mock.Mock()
        self.ctx.clients.client_plugin(
            'sahara').get_image_id = self.mock_get_image
        self.constraint = sahara.ImageConstraint()

    def test_validation(self):
        self.mock_get_image.return_value = "id1"
        self.assertTrue(self.constraint.validate("foo", self.ctx))

    def test_validation_error(self):
        self.mock_get_image.side_effect = exception.EntityNotFound(
            entity='Image', name='bar')
        self.assertFalse(self.constraint.validate("bar", self.ctx))
