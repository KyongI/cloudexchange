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
from heat.engine.clients.os import nova
from heat.engine.resources.openstack.manila import share_network
from heat.engine import scheduler
from heat.tests import common
from heat.tests import utils


stack_template = """
heat_template_version: 2015-04-30
resources:
  share_network:
    type: OS::Manila::ShareNetwork
    properties:
      name: 1
      description: 2
      neutron_network: 3
      neutron_subnet: 4
      security_services: [6, 7]
"""


class DummyShareNetwork(object):
    def __init__(self):
        self.id = '42'
        self.segmentation_id = '2'
        self.cidr = '3'
        self.ip_version = '5'
        self.network_type = '6'
        self.to_dict = lambda: {'attr': 'val'}


class ManilaShareNetworkTest(common.HeatTestCase):

    def setUp(self):
        super(ManilaShareNetworkTest, self).setUp()
        utils.setup_dummy_db()
        self.ctx = utils.dummy_context()

        t = template_format.parse(stack_template)
        self.stack = utils.parse_stack(t)
        resource_defns = self.stack.t.resource_definitions(self.stack)
        self.rsrc_defn = resource_defns['share_network']

        self.client = mock.Mock()
        self.patchobject(share_network.ManilaShareNetwork, 'client',
                         return_value=self.client)
        self.client_plugin = mock.Mock()
        self.patchobject(share_network.ManilaShareNetwork, 'client_plugin',
                         return_value=self.client_plugin)
        self.stub_NetworkConstraint_validate()
        self.stub_NovaNetworkConstraint()
        self.stub_SubnetConstraint_validate()

    def _create_network(self, name, snippet, stack):
        net = share_network.ManilaShareNetwork(name, snippet, stack)
        self.client.share_networks.create.return_value = DummyShareNetwork()
        self.client.share_networks.get.return_value = DummyShareNetwork()

        def get_security_service(id):
            return mock.Mock(id=id)

        self.client_plugin.get_security_service.side_effect = (
            get_security_service)

        scheduler.TaskRunner(net.create)()
        return net

    def test_create(self, rsrc_defn=None, stack=None):
        if rsrc_defn is None:
            rsrc_defn = self.rsrc_defn
        if stack is None:
            stack = self.stack
        net = self._create_network('share_network', rsrc_defn, stack)
        self.assertEqual((net.CREATE, net.COMPLETE), net.state)
        self.assertEqual('42', net.resource_id)
        net.client().share_networks.create.assert_called_with(
            name='1', description='2', neutron_net_id='3',
            neutron_subnet_id='4', nova_net_id=None)
        calls = [mock.call('42', '6'), mock.call('42', '7')]
        net.client().share_networks.add_security_service.assert_has_calls(
            calls, any_order=True)

    def test_create_fail(self):
        self.client.share_networks.add_security_service.side_effect = (
            Exception())
        self.assertRaises(
            exception.ResourceFailure,
            self._create_network, 'share_network', self.rsrc_defn, self.stack)

    def test_update(self):
        net = self._create_network('share_network', self.rsrc_defn, self.stack)
        update_template = copy.deepcopy(net.t)
        update_template['Properties']['name'] = 'a'
        update_template['Properties']['description'] = 'b'
        update_template['Properties']['neutron_network'] = 'c'
        update_template['Properties']['neutron_subnet'] = 'd'
        update_template['Properties']['security_services'] = ['7', '8']
        scheduler.TaskRunner(net.update, update_template)()
        self.assertEqual((net.UPDATE, net.COMPLETE), net.state)

        exp_args = {
            'name': 'a',
            'description': 'b',
            'neutron_net_id': 'c',
            'neutron_subnet_id': 'd',
            'nova_net_id': None
        }
        net.client().share_networks.update.assert_called_with('42', **exp_args)
        net.client().share_networks.add_security_service.assert_called_with(
            '42', '8')
        net.client().share_networks.remove_security_service.assert_called_with(
            '42', '6')

    def test_update_security_services(self):
        net = self._create_network('share_network', self.rsrc_defn, self.stack)
        update_template = copy.deepcopy(net.t)
        update_template['Properties']['security_services'] = ['7', '8']
        scheduler.TaskRunner(net.update, update_template)()
        self.assertEqual((net.UPDATE, net.COMPLETE), net.state)
        called = net.client().share_networks.update.called
        self.assertFalse(called)
        net.client().share_networks.add_security_service.assert_called_with(
            '42', '8')
        net.client().share_networks.remove_security_service.assert_called_with(
            '42', '6')

    def test_update_fail(self):
        net = self._create_network('share_network', self.rsrc_defn, self.stack)
        self.client.share_networks.remove_security_service.side_effect = (
            Exception())
        update_template = copy.deepcopy(net.t)
        update_template['Properties']['security_services'] = []
        run = scheduler.TaskRunner(net.update, update_template)
        self.assertRaises(exception.ResourceFailure, run)

    def test_delete(self):
        net = self._create_network('share_network', self.rsrc_defn, self.stack)
        scheduler.TaskRunner(net.delete)()
        self.assertEqual((net.DELETE, net.COMPLETE), net.state)
        self.client.share_networks.delete.assert_called_once_with(
            net.resource_id)

    def test_delete_not_found(self):
        net = self._create_network('share_network', self.rsrc_defn, self.stack)
        self.client.share_networks.delete.side_effect = (
            self.client.exceptions.NotFound())
        scheduler.TaskRunner(net.delete)()
        self.assertEqual((net.DELETE, net.COMPLETE), net.state)
        self.client.share_networks.delete.assert_called_once_with(
            net.resource_id)

    def test_nova_net_neutron_net_conflict(self):
        t = template_format.parse(stack_template)
        t['resources']['share_network']['properties']['nova_network'] = 1
        stack = utils.parse_stack(t)
        rsrc_defn = stack.t.resource_definitions(stack)['share_network']
        net = self._create_network('share_network', rsrc_defn, stack)
        msg = ('Cannot define the following properties at the same time: '
               'neutron_network, nova_network.')
        self.assertRaisesRegexp(exception.ResourcePropertyConflict, msg,
                                net.validate)

    def test_nova_net_neutron_subnet_conflict(self):
        t = template_format.parse(stack_template)
        t['resources']['share_network']['properties']['nova_network'] = 1
        del t['resources']['share_network']['properties']['neutron_network']
        stack = utils.parse_stack(t)
        rsrc_defn = stack.t.resource_definitions(stack)['share_network']
        net = self._create_network('share_network', rsrc_defn, stack)
        msg = ('Cannot define the following properties at the same time: '
               'neutron_subnet, nova_network.')
        self.assertRaisesRegexp(exception.ResourcePropertyConflict, msg,
                                net.validate)

    def test_nova_constraint_fail(self):
        validate = self.patchobject(nova.NetworkConstraint, 'validate')
        validate.return_value = False
        t = template_format.parse(stack_template)
        t['resources']['share_network']['properties']['nova_network'] = 1
        stack = utils.parse_stack(t)
        rsrc_defn = stack.t.resource_definitions(stack)['share_network']
        self.assertRaises(exception.ResourceFailure,
                          self._create_network, 'share_network',
                          rsrc_defn, stack)

    def test_attributes(self):
        net = self._create_network('share_network', self.rsrc_defn,
                                   self.stack)
        self.assertEqual('2', net.FnGetAtt('segmentation_id'))
        self.assertEqual('3', net.FnGetAtt('cidr'))
        self.assertEqual('5', net.FnGetAtt('ip_version'))
        self.assertEqual('6', net.FnGetAtt('network_type'))
        self.assertEqual({'attr': 'val'}, net.FnGetAtt('show'))

    def test_resource_mapping(self):
        mapping = share_network.resource_mapping()
        self.assertEqual(1, len(mapping))
        self.assertEqual(share_network.ManilaShareNetwork,
                         mapping['OS::Manila::ShareNetwork'])
