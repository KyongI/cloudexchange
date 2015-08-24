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

import mox
from neutronclient.common import exceptions
from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.v2_0 import client as neutronclient
import six

from heat.common import exception
from heat.common import template_format
from heat.engine.resources.openstack.neutron import vpnservice
from heat.engine import scheduler
from heat.tests import common
from heat.tests import utils


vpnservice_template = '''
heat_template_version: 2015-04-30
description: Template to test vpnservice Neutron resource
resources:
  VPNService:
    type: OS::Neutron::VPNService
    properties:
      name: VPNService
      description: My new VPN service
      admin_state_up: true
      router_id: rou123
      subnet: sub123
'''

vpnservice_template_deprecated = vpnservice_template.replace(
    'subnet', 'subnet_id')

ipsec_site_connection_template = '''
heat_template_version: 2015-04-30
description: Template to test IPsec policy resource
resources:
  IPsecSiteConnection:
    type: OS::Neutron::IPsecSiteConnection,
    properties:
      name: IPsecSiteConnection
      description: My new VPN connection
      peer_address: 172.24.4.233
      peer_id: 172.24.4.233
      peer_cidrs: [ 10.2.0.0/24 ]
      mtu: 1500
      dpd:
        actions: hold
        interval: 30
        timeout: 120
      psk: secret
      initiator: bi-directional
      admin_state_up: true
      ikepolicy_id: ike123
      ipsecpolicy_id: ips123
      vpnservice_id: vpn123
'''

ikepolicy_template = '''
heat_template_version: 2015-04-30
description: Template to test IKE policy resource
resources:
  IKEPolicy:
    type: OS::Neutron::IKEPolicy
    properties:
      name: IKEPolicy
      description: My new IKE policy
      auth_algorithm: sha1
      encryption_algorithm: 3des
      phase1_negotiation_mode: main
      lifetime:
        units: seconds
        value: 3600
      pfs: group5
      ike_version: v1
'''

ipsecpolicy_template = '''
heat_template_version: 2015-04-30
description: Template to test IPsec policy resource
resources:
  IPsecPolicy:
    type: OS::Neutron::IPsecPolicy
    properties:
      name: IPsecPolicy
      description: My new IPsec policy
      transform_protocol: esp
      encapsulation_mode: tunnel
      auth_algorithm: sha1
      encryption_algorithm: 3des
      lifetime:
        units: seconds
        value: 3600
      pfs : group5
'''


class VPNServiceTest(common.HeatTestCase):

    VPN_SERVICE_CONF = {
        'vpnservice': {
            'name': 'VPNService',
            'description': 'My new VPN service',
            'admin_state_up': True,
            'router_id': 'rou123',
            'subnet_id': 'sub123'
        }
    }

    def setUp(self):
        super(VPNServiceTest, self).setUp()
        self.m.StubOutWithMock(neutronclient.Client, 'create_vpnservice')
        self.m.StubOutWithMock(neutronclient.Client, 'delete_vpnservice')
        self.m.StubOutWithMock(neutronclient.Client, 'show_vpnservice')
        self.m.StubOutWithMock(neutronclient.Client, 'update_vpnservice')
        self.m.StubOutWithMock(neutronV20, 'find_resourceid_by_name_or_id')

    def create_vpnservice(self, resolve_neutron=True, resolve_router=True):
        self.stub_SubnetConstraint_validate()
        self.stub_RouterConstraint_validate()
        neutronV20.find_resourceid_by_name_or_id(
            mox.IsA(neutronclient.Client),
            'subnet',
            'sub123'
        ).AndReturn('sub123')
        if resolve_neutron:
            snippet = template_format.parse(vpnservice_template)
        else:
            snippet = template_format.parse(vpnservice_template_deprecated)
        if resolve_router:
            neutronV20.find_resourceid_by_name_or_id(
                mox.IsA(neutronclient.Client),
                'router',
                'rou123'
            ).AndReturn('rou123')
            props = snippet['resources']['VPNService']['properties']
            props['router'] = 'rou123'
            del props['router_id']
        neutronclient.Client.create_vpnservice(
            self.VPN_SERVICE_CONF).AndReturn({'vpnservice': {'id': 'vpn123'}})

        self.stack = utils.parse_stack(snippet)
        resource_defns = self.stack.t.resource_definitions(self.stack)
        return vpnservice.VPNService('vpnservice',
                                     resource_defns['VPNService'],
                                     self.stack)

    def test_create_deprecated(self):
        self._test_create(resolve_neutron=False)

    def test_create(self):
        self._test_create()

    def test_create_router_id(self):
        self._test_create(resolve_router=False)

    def _test_create(self, resolve_neutron=True, resolve_router=True):
        rsrc = self.create_vpnservice(resolve_neutron, resolve_router)
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_create_failed(self):
        neutronV20.find_resourceid_by_name_or_id(
            mox.IsA(neutronclient.Client),
            'subnet',
            'sub123'
        ).MultipleTimes().AndReturn('sub123')
        self.stub_RouterConstraint_validate()

        neutronclient.Client.create_vpnservice(self.VPN_SERVICE_CONF).AndRaise(
            exceptions.NeutronClientException())
        self.m.ReplayAll()
        snippet = template_format.parse(vpnservice_template)
        self.stack = utils.parse_stack(snippet)
        resource_defns = self.stack.t.resource_definitions(self.stack)
        rsrc = vpnservice.VPNService('vpnservice',
                                     resource_defns['VPNService'],
                                     self.stack)
        error = self.assertRaises(exception.ResourceFailure,
                                  scheduler.TaskRunner(rsrc.create))
        self.assertEqual(
            'NeutronClientException: resources.vpnservice: '
            'An unknown exception occurred.',
            six.text_type(error))
        self.assertEqual((rsrc.CREATE, rsrc.FAILED), rsrc.state)
        self.m.VerifyAll()

    def test_delete(self):
        neutronclient.Client.delete_vpnservice('vpn123')
        neutronclient.Client.show_vpnservice('vpn123').AndRaise(
            exceptions.NeutronClientException(status_code=404))
        rsrc = self.create_vpnservice()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_delete_already_gone(self):
        neutronclient.Client.delete_vpnservice('vpn123').AndRaise(
            exceptions.NeutronClientException(status_code=404))
        rsrc = self.create_vpnservice()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_delete_failed(self):
        neutronclient.Client.delete_vpnservice('vpn123').AndRaise(
            exceptions.NeutronClientException(status_code=400))
        rsrc = self.create_vpnservice()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        error = self.assertRaises(exception.ResourceFailure,
                                  scheduler.TaskRunner(rsrc.delete))
        self.assertEqual(
            'NeutronClientException: resources.vpnservice: '
            'An unknown exception occurred.',
            six.text_type(error))
        self.assertEqual((rsrc.DELETE, rsrc.FAILED), rsrc.state)
        self.m.VerifyAll()

    def test_attribute(self):
        rsrc = self.create_vpnservice()
        neutronclient.Client.show_vpnservice('vpn123').MultipleTimes(
        ).AndReturn(self.VPN_SERVICE_CONF)
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual('VPNService', rsrc.FnGetAtt('name'))
        self.assertEqual('My new VPN service', rsrc.FnGetAtt('description'))
        self.assertIs(True, rsrc.FnGetAtt('admin_state_up'))
        self.assertEqual('rou123', rsrc.FnGetAtt('router_id'))
        self.assertEqual('sub123', rsrc.FnGetAtt('subnet_id'))
        self.m.VerifyAll()

    def test_attribute_failed(self):
        rsrc = self.create_vpnservice()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        error = self.assertRaises(exception.InvalidTemplateAttribute,
                                  rsrc.FnGetAtt, 'non-existent_property')
        self.assertEqual(
            'The Referenced Attribute (vpnservice non-existent_property) is '
            'incorrect.',
            six.text_type(error))
        self.m.VerifyAll()

    def test_update(self):
        rsrc = self.create_vpnservice()
        neutronclient.Client.update_vpnservice(
            'vpn123', {'vpnservice': {'admin_state_up': False}})
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        update_template = copy.deepcopy(rsrc.t)
        update_template['Properties']['admin_state_up'] = False
        scheduler.TaskRunner(rsrc.update, update_template)()
        self.m.VerifyAll()


class IPsecSiteConnectionTest(common.HeatTestCase):

    IPSEC_SITE_CONNECTION_CONF = {
        'ipsec_site_connection': {
            'name': 'IPsecSiteConnection',
            'description': 'My new VPN connection',
            'peer_address': '172.24.4.233',
            'peer_id': '172.24.4.233',
            'peer_cidrs': ['10.2.0.0/24'],
            'mtu': 1500,
            'dpd': {
                'actions': 'hold',
                'interval': 30,
                'timeout': 120
            },
            'psk': 'secret',
            'initiator': 'bi-directional',
            'admin_state_up': True,
            'ikepolicy_id': 'ike123',
            'ipsecpolicy_id': 'ips123',
            'vpnservice_id': 'vpn123'
        }
    }

    def setUp(self):
        super(IPsecSiteConnectionTest, self).setUp()
        self.m.StubOutWithMock(neutronclient.Client,
                               'create_ipsec_site_connection')
        self.m.StubOutWithMock(neutronclient.Client,
                               'delete_ipsec_site_connection')
        self.m.StubOutWithMock(neutronclient.Client,
                               'show_ipsec_site_connection')
        self.m.StubOutWithMock(neutronclient.Client,
                               'update_ipsec_site_connection')

    def create_ipsec_site_connection(self):
        neutronclient.Client.create_ipsec_site_connection(
            self.IPSEC_SITE_CONNECTION_CONF).AndReturn(
                {'ipsec_site_connection': {'id': 'con123'}})
        snippet = template_format.parse(ipsec_site_connection_template)
        self.stack = utils.parse_stack(snippet)
        resource_defns = self.stack.t.resource_definitions(self.stack)
        return vpnservice.IPsecSiteConnection(
            'ipsec_site_connection',
            resource_defns['IPsecSiteConnection'],
            self.stack)

    def test_create(self):
        rsrc = self.create_ipsec_site_connection()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_create_failed(self):
        neutronclient.Client.create_ipsec_site_connection(
            self.IPSEC_SITE_CONNECTION_CONF).AndRaise(
                exceptions.NeutronClientException())
        self.m.ReplayAll()
        snippet = template_format.parse(ipsec_site_connection_template)
        self.stack = utils.parse_stack(snippet)
        resource_defns = self.stack.t.resource_definitions(self.stack)
        rsrc = vpnservice.IPsecSiteConnection(
            'ipsec_site_connection',
            resource_defns['IPsecSiteConnection'],
            self.stack)
        error = self.assertRaises(exception.ResourceFailure,
                                  scheduler.TaskRunner(rsrc.create))
        self.assertEqual(
            'NeutronClientException: resources.ipsec_site_connection: '
            'An unknown exception occurred.',
            six.text_type(error))
        self.assertEqual((rsrc.CREATE, rsrc.FAILED), rsrc.state)
        self.m.VerifyAll()

    def test_delete(self):
        neutronclient.Client.delete_ipsec_site_connection('con123')
        neutronclient.Client.show_ipsec_site_connection('con123').AndRaise(
            exceptions.NeutronClientException(status_code=404))
        rsrc = self.create_ipsec_site_connection()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_delete_already_gone(self):
        neutronclient.Client.delete_ipsec_site_connection('con123').AndRaise(
            exceptions.NeutronClientException(status_code=404))
        rsrc = self.create_ipsec_site_connection()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_delete_failed(self):
        neutronclient.Client.delete_ipsec_site_connection('con123').AndRaise(
            exceptions.NeutronClientException(status_code=400))
        rsrc = self.create_ipsec_site_connection()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        error = self.assertRaises(exception.ResourceFailure,
                                  scheduler.TaskRunner(rsrc.delete))
        self.assertEqual(
            'NeutronClientException: resources.ipsec_site_connection: '
            'An unknown exception occurred.',
            six.text_type(error))
        self.assertEqual((rsrc.DELETE, rsrc.FAILED), rsrc.state)
        self.m.VerifyAll()

    def test_attribute(self):
        rsrc = self.create_ipsec_site_connection()
        neutronclient.Client.show_ipsec_site_connection(
            'con123').MultipleTimes().AndReturn(
                self.IPSEC_SITE_CONNECTION_CONF)
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual('IPsecSiteConnection', rsrc.FnGetAtt('name'))
        self.assertEqual('My new VPN connection', rsrc.FnGetAtt('description'))
        self.assertEqual('172.24.4.233', rsrc.FnGetAtt('peer_address'))
        self.assertEqual('172.24.4.233', rsrc.FnGetAtt('peer_id'))
        self.assertEqual(['10.2.0.0/24'], rsrc.FnGetAtt('peer_cidrs'))
        self.assertEqual('hold', rsrc.FnGetAtt('dpd')['actions'])
        self.assertEqual(30, rsrc.FnGetAtt('dpd')['interval'])
        self.assertEqual(120, rsrc.FnGetAtt('dpd')['timeout'])
        self.assertEqual('secret', rsrc.FnGetAtt('psk'))
        self.assertEqual('bi-directional', rsrc.FnGetAtt('initiator'))
        self.assertIs(True, rsrc.FnGetAtt('admin_state_up'))
        self.assertEqual('ike123', rsrc.FnGetAtt('ikepolicy_id'))
        self.assertEqual('ips123', rsrc.FnGetAtt('ipsecpolicy_id'))
        self.assertEqual('vpn123', rsrc.FnGetAtt('vpnservice_id'))
        self.m.VerifyAll()

    def test_attribute_failed(self):
        rsrc = self.create_ipsec_site_connection()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        error = self.assertRaises(exception.InvalidTemplateAttribute,
                                  rsrc.FnGetAtt, 'non-existent_property')
        self.assertEqual(
            'The Referenced Attribute (ipsec_site_connection '
            'non-existent_property) is incorrect.',
            six.text_type(error))
        self.m.VerifyAll()

    def test_update(self):
        rsrc = self.create_ipsec_site_connection()
        neutronclient.Client.update_ipsec_site_connection(
            'con123', {'ipsec_site_connection': {'admin_state_up': False}})
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        update_template = copy.deepcopy(rsrc.t)
        update_template['Properties']['admin_state_up'] = False
        scheduler.TaskRunner(rsrc.update, update_template)()
        self.m.VerifyAll()


class IKEPolicyTest(common.HeatTestCase):

    IKE_POLICY_CONF = {
        'ikepolicy': {
            'name': 'IKEPolicy',
            'description': 'My new IKE policy',
            'auth_algorithm': 'sha1',
            'encryption_algorithm': '3des',
            'phase1_negotiation_mode': 'main',
            'lifetime': {
                'units': 'seconds',
                'value': 3600
            },
            'pfs': 'group5',
            'ike_version': 'v1'
        }
    }

    def setUp(self):
        super(IKEPolicyTest, self).setUp()
        self.m.StubOutWithMock(neutronclient.Client, 'create_ikepolicy')
        self.m.StubOutWithMock(neutronclient.Client, 'delete_ikepolicy')
        self.m.StubOutWithMock(neutronclient.Client, 'show_ikepolicy')
        self.m.StubOutWithMock(neutronclient.Client, 'update_ikepolicy')

    def create_ikepolicy(self):
        neutronclient.Client.create_ikepolicy(
            self.IKE_POLICY_CONF).AndReturn(
                {'ikepolicy': {'id': 'ike123'}})
        snippet = template_format.parse(ikepolicy_template)
        self.stack = utils.parse_stack(snippet)
        resource_defns = self.stack.t.resource_definitions(self.stack)
        return vpnservice.IKEPolicy('ikepolicy',
                                    resource_defns['IKEPolicy'],
                                    self.stack)

    def test_create(self):
        rsrc = self.create_ikepolicy()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_create_failed(self):
        neutronclient.Client.create_ikepolicy(
            self.IKE_POLICY_CONF).AndRaise(
                exceptions.NeutronClientException())
        self.m.ReplayAll()
        snippet = template_format.parse(ikepolicy_template)
        self.stack = utils.parse_stack(snippet)
        resource_defns = self.stack.t.resource_definitions(self.stack)
        rsrc = vpnservice.IKEPolicy(
            'ikepolicy',
            resource_defns['IKEPolicy'],
            self.stack)
        error = self.assertRaises(exception.ResourceFailure,
                                  scheduler.TaskRunner(rsrc.create))
        self.assertEqual(
            'NeutronClientException: resources.ikepolicy: '
            'An unknown exception occurred.',
            six.text_type(error))
        self.assertEqual((rsrc.CREATE, rsrc.FAILED), rsrc.state)
        self.m.VerifyAll()

    def test_delete(self):
        neutronclient.Client.delete_ikepolicy('ike123')
        neutronclient.Client.show_ikepolicy('ike123').AndRaise(
            exceptions.NeutronClientException(status_code=404))
        rsrc = self.create_ikepolicy()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_delete_already_gone(self):
        neutronclient.Client.delete_ikepolicy('ike123').AndRaise(
            exceptions.NeutronClientException(status_code=404))
        rsrc = self.create_ikepolicy()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_delete_failed(self):
        neutronclient.Client.delete_ikepolicy('ike123').AndRaise(
            exceptions.NeutronClientException(status_code=400))
        rsrc = self.create_ikepolicy()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        error = self.assertRaises(exception.ResourceFailure,
                                  scheduler.TaskRunner(rsrc.delete))
        self.assertEqual(
            'NeutronClientException: resources.ikepolicy: '
            'An unknown exception occurred.',
            six.text_type(error))
        self.assertEqual((rsrc.DELETE, rsrc.FAILED), rsrc.state)
        self.m.VerifyAll()

    def test_attribute(self):
        rsrc = self.create_ikepolicy()
        neutronclient.Client.show_ikepolicy(
            'ike123').MultipleTimes().AndReturn(self.IKE_POLICY_CONF)
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual('IKEPolicy', rsrc.FnGetAtt('name'))
        self.assertEqual('My new IKE policy', rsrc.FnGetAtt('description'))
        self.assertEqual('sha1', rsrc.FnGetAtt('auth_algorithm'))
        self.assertEqual('3des', rsrc.FnGetAtt('encryption_algorithm'))
        self.assertEqual('main', rsrc.FnGetAtt('phase1_negotiation_mode'))
        self.assertEqual('seconds', rsrc.FnGetAtt('lifetime')['units'])
        self.assertEqual(3600, rsrc.FnGetAtt('lifetime')['value'])
        self.assertEqual('group5', rsrc.FnGetAtt('pfs'))
        self.assertEqual('v1', rsrc.FnGetAtt('ike_version'))
        self.m.VerifyAll()

    def test_attribute_failed(self):
        rsrc = self.create_ikepolicy()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        error = self.assertRaises(exception.InvalidTemplateAttribute,
                                  rsrc.FnGetAtt, 'non-existent_property')
        self.assertEqual(
            'The Referenced Attribute (ikepolicy non-existent_property) is '
            'incorrect.',
            six.text_type(error))
        self.m.VerifyAll()

    def test_update(self):
        rsrc = self.create_ikepolicy()
        neutronclient.Client.update_ikepolicy('ike123',
                                              {'ikepolicy': {
                                                  'name': 'New IKEPolicy'}})
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        update_template = copy.deepcopy(rsrc.t)
        update_template['Properties']['name'] = 'New IKEPolicy'
        scheduler.TaskRunner(rsrc.update, update_template)()
        self.m.VerifyAll()


class IPsecPolicyTest(common.HeatTestCase):

    IPSEC_POLICY_CONF = {
        'ipsecpolicy': {
            'name': 'IPsecPolicy',
            'description': 'My new IPsec policy',
            'transform_protocol': 'esp',
            'encapsulation_mode': 'tunnel',
            'auth_algorithm': 'sha1',
            'encryption_algorithm': '3des',
            'lifetime': {
                'units': 'seconds',
                'value': 3600
            },
            'pfs': 'group5'
        }
    }

    def setUp(self):
        super(IPsecPolicyTest, self).setUp()
        self.m.StubOutWithMock(neutronclient.Client, 'create_ipsecpolicy')
        self.m.StubOutWithMock(neutronclient.Client, 'delete_ipsecpolicy')
        self.m.StubOutWithMock(neutronclient.Client, 'show_ipsecpolicy')
        self.m.StubOutWithMock(neutronclient.Client, 'update_ipsecpolicy')

    def create_ipsecpolicy(self):
        neutronclient.Client.create_ipsecpolicy(
            self.IPSEC_POLICY_CONF).AndReturn(
                {'ipsecpolicy': {'id': 'ips123'}})
        snippet = template_format.parse(ipsecpolicy_template)
        self.stack = utils.parse_stack(snippet)
        resource_defns = self.stack.t.resource_definitions(self.stack)
        return vpnservice.IPsecPolicy('ipsecpolicy',
                                      resource_defns['IPsecPolicy'],
                                      self.stack)

    def test_create(self):
        rsrc = self.create_ipsecpolicy()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_create_failed(self):
        neutronclient.Client.create_ipsecpolicy(
            self.IPSEC_POLICY_CONF).AndRaise(
                exceptions.NeutronClientException())
        self.m.ReplayAll()
        snippet = template_format.parse(ipsecpolicy_template)
        self.stack = utils.parse_stack(snippet)
        resource_defns = self.stack.t.resource_definitions(self.stack)
        rsrc = vpnservice.IPsecPolicy(
            'ipsecpolicy',
            resource_defns['IPsecPolicy'],
            self.stack)
        error = self.assertRaises(exception.ResourceFailure,
                                  scheduler.TaskRunner(rsrc.create))
        self.assertEqual(
            'NeutronClientException: resources.ipsecpolicy: '
            'An unknown exception occurred.',
            six.text_type(error))
        self.assertEqual((rsrc.CREATE, rsrc.FAILED), rsrc.state)
        self.m.VerifyAll()

    def test_delete(self):
        neutronclient.Client.delete_ipsecpolicy('ips123')
        neutronclient.Client.show_ipsecpolicy('ips123').AndRaise(
            exceptions.NeutronClientException(status_code=404))
        rsrc = self.create_ipsecpolicy()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_delete_already_gone(self):
        neutronclient.Client.delete_ipsecpolicy('ips123').AndRaise(
            exceptions.NeutronClientException(status_code=404))
        rsrc = self.create_ipsecpolicy()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        scheduler.TaskRunner(rsrc.delete)()
        self.assertEqual((rsrc.DELETE, rsrc.COMPLETE), rsrc.state)
        self.m.VerifyAll()

    def test_delete_failed(self):
        neutronclient.Client.delete_ipsecpolicy('ips123').AndRaise(
            exceptions.NeutronClientException(status_code=400))
        rsrc = self.create_ipsecpolicy()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        error = self.assertRaises(exception.ResourceFailure,
                                  scheduler.TaskRunner(rsrc.delete))
        self.assertEqual(
            'NeutronClientException: resources.ipsecpolicy: '
            'An unknown exception occurred.',
            six.text_type(error))
        self.assertEqual((rsrc.DELETE, rsrc.FAILED), rsrc.state)
        self.m.VerifyAll()

    def test_attribute(self):
        rsrc = self.create_ipsecpolicy()
        neutronclient.Client.show_ipsecpolicy(
            'ips123').MultipleTimes().AndReturn(self.IPSEC_POLICY_CONF)
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual('IPsecPolicy', rsrc.FnGetAtt('name'))
        self.assertEqual('My new IPsec policy', rsrc.FnGetAtt('description'))
        self.assertEqual('esp', rsrc.FnGetAtt('transform_protocol'))
        self.assertEqual('tunnel', rsrc.FnGetAtt('encapsulation_mode'))
        self.assertEqual('sha1', rsrc.FnGetAtt('auth_algorithm'))
        self.assertEqual('3des', rsrc.FnGetAtt('encryption_algorithm'))
        self.assertEqual('seconds', rsrc.FnGetAtt('lifetime')['units'])
        self.assertEqual(3600, rsrc.FnGetAtt('lifetime')['value'])
        self.assertEqual('group5', rsrc.FnGetAtt('pfs'))
        self.m.VerifyAll()

    def test_attribute_failed(self):
        rsrc = self.create_ipsecpolicy()
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        error = self.assertRaises(exception.InvalidTemplateAttribute,
                                  rsrc.FnGetAtt, 'non-existent_property')
        self.assertEqual(
            'The Referenced Attribute (ipsecpolicy non-existent_property) is '
            'incorrect.',
            six.text_type(error))
        self.m.VerifyAll()

    def test_update(self):
        rsrc = self.create_ipsecpolicy()
        neutronclient.Client.update_ipsecpolicy(
            'ips123',
            {'ipsecpolicy': {'name': 'New IPsecPolicy'}})
        self.m.ReplayAll()
        scheduler.TaskRunner(rsrc.create)()
        update_template = copy.deepcopy(rsrc.t)
        update_template['Properties']['name'] = 'New IPsecPolicy'
        scheduler.TaskRunner(rsrc.update, update_template)()
        self.m.VerifyAll()
