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

import copy

import mock

from heat.common import exception
from heat.common import template_format
from heat.engine import resources
from heat.engine.resources.openstack.manila import share_type as mshare_type
from heat.engine import rsrc_defn
from heat.engine import scheduler
from heat.tests import common
from heat.tests import utils

manila_template = """
heat_template_version: 2013-05-23
resources:
  test_share_type:
    type: OS::Manila::ShareType
    properties:
      name: test_share_type
      driver_handles_share_servers: True
      extra_specs: {"test":"test"}
      is_public: False
"""


class DummyShare(object):
    def __init__(self):
        self.to_dict = lambda: {'attr': 'val'}


class ManilaShareTypeTest(common.HeatTestCase):

    def setUp(self):
        super(ManilaShareTypeTest, self).setUp()
        resources.initialise()
        utils.setup_dummy_db()
        self.ctx = utils.dummy_context()

    def _init_share(self, stack_name, share_type_name="test_share_type"):
        # parse stack
        tmp = template_format.parse(manila_template)
        self.stack = utils.parse_stack(tmp, stack_name=stack_name)
        defns = self.stack.t.resource_definitions(self.stack)
        res_def = defns["test_share_type"]
        share_type = mshare_type.ManilaShareType(
            share_type_name, res_def, self.stack)
        # mock clients and plugins
        mock_client = mock.MagicMock()
        client = mock.MagicMock(return_value=mock_client)
        share_type.client = client
        mock_plugin = mock.MagicMock()
        client_plugin = mock.MagicMock(return_value=mock_plugin)
        share_type.client_plugin = client_plugin

        return share_type

    def test_share_type_create(self):
        share_type = self._init_share("stack_share_type_create")
        fake_share_type = mock.MagicMock(id="type_id")
        share_type.client().share_types.create.return_value = fake_share_type
        scheduler.TaskRunner(share_type.create)()
        self.assertEqual("type_id", share_type.resource_id)
        share_type.client().share_types.create.assert_called_once_with(
            name="test_share_type", spec_driver_handles_share_servers=True,
            is_public=False)
        fake_share_type.set_keys.assert_called_once_with({"test": "test"})

    def test_share_type_delete(self):
        share_type = self._init_share("stack_share_type_delete")
        fake_share_type = mock.MagicMock(id="type_id")
        share_type.client().share_types.create.return_value = fake_share_type
        scheduler.TaskRunner(share_type.create)()

        scheduler.TaskRunner(share_type.delete)()
        share_type.client().share_types.delete.assert_called_once_with(
            "type_id")

    def test_share_type_delete_not_found(self):
        share_type = self._init_share("stack_share_type_delete_not_found")
        fake_share_type = mock.MagicMock(id="type_id")
        share_type.client().share_types.create.return_value = fake_share_type
        scheduler.TaskRunner(share_type.create)()

        exc = exception.NotFound()
        share_type.client().share_types.delete.side_effect = exc
        scheduler.TaskRunner(share_type.delete)()
        share_type.client_plugin().ignore_not_found.assert_called_once_with(
            exc)

    def test_share_type_update(self):
        share_type = self._init_share("stack_share_type_update")
        share_type.client().share_types.create.return_value = mock.MagicMock(
            id="type_id")
        fake_share_type = mock.MagicMock()
        share_type.client().share_types.get.return_value = fake_share_type
        scheduler.TaskRunner(share_type.create)()
        updated_props = copy.deepcopy(share_type.properties.data)
        updated_props[mshare_type.ManilaShareType.EXTRA_SPECS] = {
            "fake_key": "fake_value"}
        after = rsrc_defn.ResourceDefinition(share_type.name,
                                             share_type.type(), updated_props)
        scheduler.TaskRunner(share_type.update, after)()
        fake_share_type.unset_keys.assert_called_once_with({"test": "test"})
        fake_share_type.set_keys.assert_called_with(
            updated_props[mshare_type.ManilaShareType.EXTRA_SPECS])

    def test_show_resource(self):
        share_type = self._init_share("stack_share_type_create")
        share_type.client().share_types.create.return_value = mock.Mock(
            id='type_id')
        share_type.client().share_types.get.return_value = DummyShare()
        scheduler.TaskRunner(share_type.create)()
        self.assertEqual({'attr': 'val'}, share_type.FnGetAtt('show'))
