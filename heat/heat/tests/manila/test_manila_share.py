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
import collections
import copy

import mock
import six

from heat.common import exception
from heat.common import template_format
from heat.engine import resource
from heat.engine.resources.openstack.manila import share as mshare
from heat.engine import rsrc_defn
from heat.engine import scheduler
from heat.tests import common
from heat.tests import utils


manila_template = """
heat_template_version: 2015-04-30
resources:
  test_share:
    type: OS::Manila::Share
    properties:
      share_protocol: NFS
      size: 1
      access_rules:
        - access_to: 127.0.0.1
          access_type: ip
          access_level: ro
      name: basic_test_share
      description: basic test share
      is_public: True
      metadata: {"key": "value"}
"""


class DummyShare(object):
    def __init__(self):
        self.availability_zone = 'az'
        self.host = 'host'
        self.export_locations = 'el'
        self.share_server_id = 'id'
        self.created_at = 'ca'
        self.status = 's'
        self.project_id = 'p_id'
        self.to_dict = lambda: {'attr': 'val'}


class ManilaShareTest(common.HeatTestCase):

    def setUp(self):
        super(ManilaShareTest, self).setUp()
        utils.setup_dummy_db()
        self.ctx = utils.dummy_context()

        self.fake_share = mock.MagicMock(id="test_share_id")
        self.available_share = mock.MagicMock(
            id="test_share_id",
            status=mshare.ManilaShare.STATUS_AVAILABLE)
        self.failed_share = mock.MagicMock(
            id="test_share_id",
            status=mshare.ManilaShare.STATUS_ERROR)
        self.deleting_share = mock.MagicMock(
            id="test_share_id",
            status=mshare.ManilaShare.STATUS_DELETING)

    def _init_share(self, stack_name):
        tmp = template_format.parse(manila_template)
        self.stack = utils.parse_stack(tmp, stack_name=stack_name)
        res_def = self.stack.t.resource_definitions(self.stack)["test_share"]
        share = mshare.ManilaShare("test_share", res_def, self.stack)

        # replace clients and plugins with mocks
        mock_client = mock.MagicMock()
        client = mock.MagicMock(return_value=mock_client)
        share.client = client
        mock_plugin = mock.MagicMock()
        client_plugin = mock.MagicMock(return_value=mock_plugin)
        share.client_plugin = client_plugin

        return share

    def _create_share(self, stack_name):
        share = self._init_share(stack_name)
        share.client().shares.create.return_value = self.fake_share
        share.client().shares.get.return_value = self.available_share
        scheduler.TaskRunner(share.create)()
        return share

    def test_share_create(self):
        share = self._create_share("stack_share_create")

        expected_state = (share.CREATE, share.COMPLETE)
        self.assertEqual(expected_state, share.state,
                         "Share is not in expected state")
        self.assertEqual(self.fake_share.id, share.resource_id,
                         "Expected share ID was not propagated to share")

        share.client().shares.allow.assert_called_once_with(
            access="127.0.0.1", access_level="ro",
            share=share.resource_id, access_type="ip")
        args, kwargs = share.client().shares.create.call_args
        message_end = " parameter was not passed to manila client"
        self.assertEqual(u"NFS", kwargs["share_proto"],
                         "Share protocol" + message_end)
        self.assertEqual(1, kwargs["size"], "Share size" + message_end)
        self.assertEqual("basic_test_share", kwargs["name"],
                         "Share name" + message_end)
        self.assertEqual("basic test share", kwargs["description"],
                         "Share description" + message_end)
        self.assertEqual({u"key": u"value"}, kwargs["metadata"],
                         "Metadata" + message_end)
        self.assertTrue(kwargs["is_public"])
        share.client().shares.get.assert_called_once_with(self.fake_share.id)

    def test_share_create_fail(self):
        share = self._init_share("stack_share_create_fail")
        share.client().shares.get.return_value = self.failed_share
        exc = self.assertRaises(resource.ResourceInError,
                                share.check_create_complete,
                                self.failed_share)
        self.assertIn("Error during creation", six.text_type(exc))

    def test_share_create_unknown_status(self):
        share = self._init_share("stack_share_create_unknown")
        share.client().shares.get.return_value = self.deleting_share
        exc = self.assertRaises(resource.ResourceUnknownStatus,
                                share.check_create_complete,
                                self.deleting_share)
        self.assertIn("Unknown status", six.text_type(exc))

    def test_share_delete(self):
        share = self._create_share("stack_share_delete")
        share.client().shares.get.side_effect = exception.NotFound()
        share.client_plugin().ignore_not_found.return_value = None
        scheduler.TaskRunner(share.delete)()
        share.client().shares.delete.assert_called_once_with(
            self.fake_share.id)

    def test_share_delete_fail(self):
        share = self._create_share("stack_share_delete_fail")
        share.client().shares.delete.return_value = None
        share.client().shares.get.return_value = self.failed_share
        exc = self.assertRaises(exception.ResourceFailure,
                                scheduler.TaskRunner(share.delete))
        self.assertIn("Error during deleting share", six.text_type(exc))

    def test_share_check(self):
        share = self._create_share("stack_share_check")
        scheduler.TaskRunner(share.check)()
        expected_state = (share.CHECK, share.COMPLETE)
        self.assertEqual(expected_state, share.state,
                         "Share is not in expected state")

    def test_share_check_fail(self):
        share = self._create_share("stack_share_check_fail")
        share.client().shares.get.return_value = self.failed_share
        exc = self.assertRaises(exception.ResourceFailure,
                                scheduler.TaskRunner(share.check))
        self.assertIn("Error: resources.test_share: 'status': expected "
                      "'['available']'", six.text_type(exc))

    def test_share_update(self):
        share = self._create_share("stack_share_update")
        updated_share_props = copy.deepcopy(share.properties.data)
        updated_share_props[mshare.ManilaShare.DESCRIPTION] = "desc"
        updated_share_props[mshare.ManilaShare.NAME] = "name"
        updated_share_props[mshare.ManilaShare.IS_PUBLIC] = True
        share.client().shares.update.return_value = None
        after = rsrc_defn.ResourceDefinition(share.name, share.type(),
                                             updated_share_props)
        scheduler.TaskRunner(share.update, after)()
        kwargs = {
            "display_name": "name",
            "display_description": "desc",
        }
        share.client().shares.update.assert_called_once_with(
            share.resource_id, **kwargs)

    def test_share_update_access_rules(self):
        share = self._create_share("stack_share_update_access_rules")
        updated_share_props = copy.deepcopy(share.properties.data)
        updated_share_props[mshare.ManilaShare.ACCESS_RULES] = [
            {mshare.ManilaShare.ACCESS_TO: "127.0.0.2",
             mshare.ManilaShare.ACCESS_TYPE: "ip",
             mshare.ManilaShare.ACCESS_LEVEL: "ro"}]
        share.client().shares.deny.return_value = None
        current_rule = {
            mshare.ManilaShare.ACCESS_TO: "127.0.0.1",
            mshare.ManilaShare.ACCESS_TYPE: "ip",
            mshare.ManilaShare.ACCESS_LEVEL: "ro",
            "id": "test_access_rule"
        }
        rule_tuple = collections.namedtuple("DummyRule",
                                            list(current_rule.keys()))
        share.client().shares.access_list.return_value = [
            rule_tuple(**current_rule)]
        after = rsrc_defn.ResourceDefinition(share.name, share.type(),
                                             updated_share_props)
        scheduler.TaskRunner(share.update, after)()

        share.client().shares.access_list.assert_called_once_with(
            share.resource_id)
        share.client().shares.allow.assert_called_with(
            share=share.resource_id, access_type="ip",
            access="127.0.0.2", access_level="ro")
        share.client().shares.deny.assert_called_once_with(
            share=share.resource_id, id="test_access_rule")

    def test_share_update_metadata(self):
        share = self._create_share("stack_share_update_metadata")
        updated_share_props = copy.deepcopy(share.properties.data)
        updated_share_props[mshare.ManilaShare.METADATA] = {
            "fake_key": "fake_value"}
        share.client().shares.update_all_metadata.return_value = None

        after = rsrc_defn.ResourceDefinition(share.name, share.type(),
                                             updated_share_props)
        scheduler.TaskRunner(share.update, after)()
        share.client().shares.update_all_metadata.assert_called_once_with(
            share.resource_id,
            updated_share_props[mshare.ManilaShare.METADATA])

    def test_attributes(self):
        share = self._create_share("share")
        share.client().shares.get.return_value = DummyShare()
        self.assertEqual('az', share.FnGetAtt('availability_zone'))
        self.assertEqual('host', share.FnGetAtt('host'))
        self.assertEqual('el', share.FnGetAtt('export_locations'))
        self.assertEqual('id', share.FnGetAtt('share_server_id'))
        self.assertEqual('ca', share.FnGetAtt('created_at'))
        self.assertEqual('s', share.FnGetAtt('status'))
        self.assertEqual('p_id', share.FnGetAtt('project_id'))
        self.assertEqual({'attr': 'val'}, share.FnGetAtt('show'))
