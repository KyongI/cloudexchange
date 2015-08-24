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
import six
import webob.exc

import heat.api.middleware.fault as fault
import heat.api.openstack.v1.events as events
from heat.common import exception as heat_exc
from heat.common import identifier
from heat.common import policy
from heat.rpc import client as rpc_client
from heat.tests.api.openstack_v1 import tools
from heat.tests import common


@mock.patch.object(policy.Enforcer, 'enforce')
class EventControllerTest(tools.ControllerTest, common.HeatTestCase):
    '''
    Tests the API class which acts as the WSGI controller,
    the endpoint processing API requests after they are routed
    '''

    def setUp(self):
        super(EventControllerTest, self).setUp()
        # Create WSGI controller instance

        class DummyConfig(object):
            bind_port = 8004

        cfgopts = DummyConfig()
        self.controller = events.EventController(options=cfgopts)

    def test_resource_index_event_id_integer(self, mock_enforce):
        self._test_resource_index('42', mock_enforce)

    def test_resource_index_event_id_uuid(self, mock_enforce):
        self._test_resource_index('a3455d8c-9f88-404d-a85b-5315293e67de',
                                  mock_enforce)

    def _test_resource_index(self, event_id, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'index', True)
        res_name = 'WikiDatabase'
        stack_identity = identifier.HeatIdentifier(self.tenant,
                                                   'wordpress', '6')
        res_identity = identifier.ResourceIdentifier(resource_name=res_name,
                                                     **stack_identity)
        ev_identity = identifier.EventIdentifier(event_id=event_id,
                                                 **res_identity)

        req = self._get(stack_identity._tenant_path() +
                        '/resources/' + res_name + '/events')

        kwargs = {'stack_identity': stack_identity,
                  'limit': None, 'sort_keys': None, 'marker': None,
                  'sort_dir': None, 'filters': None}

        engine_resp = [
            {
                u'stack_name': u'wordpress',
                u'event_time': u'2012-07-23T13:05:39Z',
                u'stack_identity': dict(stack_identity),
                u'resource_name': res_name,
                u'resource_status_reason': u'state changed',
                u'event_identity': dict(ev_identity),
                u'resource_action': u'CREATE',
                u'resource_status': u'IN_PROGRESS',
                u'physical_resource_id': None,
                u'resource_properties': {u'UserData': u'blah'},
                u'resource_type': u'AWS::EC2::Instance',
            },
            {
                u'stack_name': u'wordpress',
                u'event_time': u'2012-07-23T13:05:39Z',
                u'stack_identity': dict(stack_identity),
                u'resource_name': 'SomeOtherResource',
                u'logical_resource_id': 'SomeOtherResource',
                u'resource_status_reason': u'state changed',
                u'event_identity': dict(ev_identity),
                u'resource_action': u'CREATE',
                u'resource_status': u'IN_PROGRESS',
                u'physical_resource_id': None,
                u'resource_properties': {u'UserData': u'blah'},
                u'resource_type': u'AWS::EC2::Instance',
            }
        ]
        self.m.StubOutWithMock(rpc_client.EngineClient, 'call')
        rpc_client.EngineClient.call(
            req.context, ('list_events', kwargs)
        ).AndReturn(engine_resp)
        self.m.ReplayAll()

        result = self.controller.index(req, tenant_id=self.tenant,
                                       stack_name=stack_identity.stack_name,
                                       stack_id=stack_identity.stack_id,
                                       resource_name=res_name)

        expected = {
            'events': [
                {
                    'id': event_id,
                    'links': [
                        {'href': self._url(ev_identity), 'rel': 'self'},
                        {'href': self._url(res_identity), 'rel': 'resource'},
                        {'href': self._url(stack_identity), 'rel': 'stack'},
                    ],
                    u'resource_name': res_name,
                    u'logical_resource_id': res_name,
                    u'resource_status_reason': u'state changed',
                    u'event_time': u'2012-07-23T13:05:39Z',
                    u'resource_status': u'CREATE_IN_PROGRESS',
                    u'physical_resource_id': None,
                }
            ]
        }

        self.assertEqual(expected, result)
        self.m.VerifyAll()

    def test_stack_index_event_id_integer(self, mock_enforce):
        self._test_stack_index('42', mock_enforce)

    def test_stack_index_event_id_uuid(self, mock_enforce):
        self._test_stack_index('a3455d8c-9f88-404d-a85b-5315293e67de',
                               mock_enforce)

    def _test_stack_index(self, event_id, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'index', True)
        res_name = 'WikiDatabase'
        stack_identity = identifier.HeatIdentifier(self.tenant,
                                                   'wordpress', '6')
        res_identity = identifier.ResourceIdentifier(resource_name=res_name,
                                                     **stack_identity)
        ev_identity = identifier.EventIdentifier(event_id=event_id,
                                                 **res_identity)

        req = self._get(stack_identity._tenant_path() + '/events')

        kwargs = {'stack_identity': stack_identity,
                  'limit': None, 'sort_keys': None, 'marker': None,
                  'sort_dir': None, 'filters': None}

        engine_resp = [
            {
                u'stack_name': u'wordpress',
                u'event_time': u'2012-07-23T13:05:39Z',
                u'stack_identity': dict(stack_identity),
                u'resource_name': res_name,
                u'resource_status_reason': u'state changed',
                u'event_identity': dict(ev_identity),
                u'resource_action': u'CREATE',
                u'resource_status': u'IN_PROGRESS',
                u'physical_resource_id': None,
                u'resource_properties': {u'UserData': u'blah'},
                u'resource_type': u'AWS::EC2::Instance',
            }
        ]
        self.m.StubOutWithMock(rpc_client.EngineClient, 'call')
        rpc_client.EngineClient.call(
            req.context,
            ('list_events', kwargs)
        ).AndReturn(engine_resp)
        self.m.ReplayAll()

        result = self.controller.index(req, tenant_id=self.tenant,
                                       stack_name=stack_identity.stack_name,
                                       stack_id=stack_identity.stack_id)

        expected = {
            'events': [
                {
                    'id': event_id,
                    'links': [
                        {'href': self._url(ev_identity), 'rel': 'self'},
                        {'href': self._url(res_identity), 'rel': 'resource'},
                        {'href': self._url(stack_identity), 'rel': 'stack'},
                    ],
                    u'resource_name': res_name,
                    u'logical_resource_id': res_name,
                    u'resource_status_reason': u'state changed',
                    u'event_time': u'2012-07-23T13:05:39Z',
                    u'resource_status': u'CREATE_IN_PROGRESS',
                    u'physical_resource_id': None,
                }
            ]
        }

        self.assertEqual(expected, result)
        self.m.VerifyAll()

    def test_index_stack_nonexist(self, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'index', True)
        stack_identity = identifier.HeatIdentifier(self.tenant,
                                                   'wibble', '6')

        req = self._get(stack_identity._tenant_path() + '/events')

        kwargs = {'stack_identity': stack_identity,
                  'limit': None, 'sort_keys': None, 'marker': None,
                  'sort_dir': None, 'filters': None}

        error = heat_exc.StackNotFound(stack_name='a')
        self.m.StubOutWithMock(rpc_client.EngineClient, 'call')
        rpc_client.EngineClient.call(
            req.context,
            ('list_events', kwargs)
        ).AndRaise(tools.to_remote_error(error))
        self.m.ReplayAll()

        resp = tools.request_with_middleware(
            fault.FaultWrapper,
            self.controller.index,
            req, tenant_id=self.tenant,
            stack_name=stack_identity.stack_name,
            stack_id=stack_identity.stack_id)

        self.assertEqual(404, resp.json['code'])
        self.assertEqual('StackNotFound', resp.json['error']['type'])
        self.m.VerifyAll()

    def test_index_err_denied_policy(self, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'index', False)
        stack_identity = identifier.HeatIdentifier(self.tenant,
                                                   'wibble', '6')

        req = self._get(stack_identity._tenant_path() + '/events')

        resp = tools.request_with_middleware(
            fault.FaultWrapper,
            self.controller.index,
            req, tenant_id=self.tenant,
            stack_name=stack_identity.stack_name,
            stack_id=stack_identity.stack_id)

        self.assertEqual(403, resp.status_int)
        self.assertIn('403 Forbidden', six.text_type(resp))

    def test_index_resource_nonexist(self, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'index', True)
        event_id = '42'
        res_name = 'WikiDatabase'
        stack_identity = identifier.HeatIdentifier(self.tenant,
                                                   'wordpress', '6')
        res_identity = identifier.ResourceIdentifier(resource_name=res_name,
                                                     **stack_identity)
        ev_identity = identifier.EventIdentifier(event_id=event_id,
                                                 **res_identity)

        req = self._get(stack_identity._tenant_path() +
                        '/resources/' + res_name + '/events')

        kwargs = {'stack_identity': stack_identity,
                  'limit': None, 'sort_keys': None, 'marker': None,
                  'sort_dir': None, 'filters': None}

        engine_resp = [
            {
                u'stack_name': u'wordpress',
                u'event_time': u'2012-07-23T13:05:39Z',
                u'stack_identity': dict(stack_identity),
                u'resource_name': 'SomeOtherResource',
                u'resource_status_reason': u'state changed',
                u'event_identity': dict(ev_identity),
                u'resource_action': u'CREATE',
                u'resource_status': u'IN_PROGRESS',
                u'physical_resource_id': None,
                u'resource_properties': {u'UserData': u'blah'},
                u'resource_type': u'AWS::EC2::Instance',
            }
        ]
        self.m.StubOutWithMock(rpc_client.EngineClient, 'call')
        rpc_client.EngineClient.call(
            req.context,
            ('list_events', kwargs)
        ).AndReturn(engine_resp)
        self.m.ReplayAll()

        self.assertRaises(webob.exc.HTTPNotFound,
                          self.controller.index,
                          req, tenant_id=self.tenant,
                          stack_name=stack_identity.stack_name,
                          stack_id=stack_identity.stack_id,
                          resource_name=res_name)
        self.m.VerifyAll()

    @mock.patch.object(rpc_client.EngineClient, 'call')
    def test_index_whitelists_pagination_params(self, mock_call, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'index', True)
        params = {
            'limit': 10,
            'sort_keys': 'fake sort keys',
            'marker': 'fake marker',
            'sort_dir': 'fake sort dir',
            'balrog': 'you shall not pass!'
        }
        stack_identity = identifier.HeatIdentifier(self.tenant,
                                                   'wibble', '6')

        req = self._get(stack_identity._tenant_path() + '/events',
                        params=params)

        mock_call.return_value = []

        self.controller.index(req, tenant_id=self.tenant,
                              stack_name=stack_identity.stack_name,
                              stack_id=stack_identity.stack_id)

        rpc_call_args, _ = mock_call.call_args
        engine_args = rpc_call_args[1][1]
        self.assertEqual(6, len(engine_args))
        self.assertIn('limit', engine_args)
        self.assertEqual(10, engine_args['limit'])
        self.assertIn('sort_keys', engine_args)
        self.assertEqual(['fake sort keys'], engine_args['sort_keys'])
        self.assertIn('marker', engine_args)
        self.assertEqual('fake marker', engine_args['marker'])
        self.assertIn('sort_dir', engine_args)
        self.assertEqual('fake sort dir', engine_args['sort_dir'])
        self.assertIn('filters', engine_args)
        self.assertIsNone(engine_args['filters'])
        self.assertNotIn('balrog', engine_args)

    @mock.patch.object(rpc_client.EngineClient, 'call')
    def test_index_limit_not_int(self, mock_call, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'index', True)
        sid = identifier.HeatIdentifier(self.tenant, 'wibble', '6')

        req = self._get(sid._tenant_path() + '/events',
                        params={'limit': 'not-an-int'})

        ex = self.assertRaises(webob.exc.HTTPBadRequest,
                               self.controller.index, req,
                               tenant_id=self.tenant,
                               stack_name=sid.stack_name,
                               stack_id=sid.stack_id)
        self.assertEqual("Only integer is acceptable by 'limit'.",
                         six.text_type(ex))
        self.assertFalse(mock_call.called)

    @mock.patch.object(rpc_client.EngineClient, 'call')
    def test_index_whitelist_filter_params(self, mock_call, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'index', True)
        params = {
            'resource_status': 'COMPLETE',
            'resource_action': 'CREATE',
            'resource_name': 'my_server',
            'resource_type': 'OS::Nova::Server',
            'balrog': 'you shall not pass!'
        }
        stack_identity = identifier.HeatIdentifier(self.tenant,
                                                   'wibble', '6')

        req = self._get(stack_identity._tenant_path() + '/events',
                        params=params)

        mock_call.return_value = []

        self.controller.index(req, tenant_id=self.tenant,
                              stack_name=stack_identity.stack_name,
                              stack_id=stack_identity.stack_id)

        rpc_call_args, _ = mock_call.call_args
        engine_args = rpc_call_args[1][1]
        self.assertIn('filters', engine_args)

        filters = engine_args['filters']
        self.assertEqual(4, len(filters))
        self.assertIn('resource_status', filters)
        self.assertEqual('COMPLETE', filters['resource_status'])
        self.assertIn('resource_action', filters)
        self.assertEqual('CREATE', filters['resource_action'])
        self.assertIn('resource_name', filters)
        self.assertEqual('my_server', filters['resource_name'])
        self.assertIn('resource_type', filters)
        self.assertEqual('OS::Nova::Server', filters['resource_type'])
        self.assertNotIn('balrog', filters)

    def test_show_event_id_integer(self, mock_enforce):
        self._test_show('42', mock_enforce)

    def test_show_event_id_uuid(self, mock_enforce):
        self._test_show('a3455d8c-9f88-404d-a85b-5315293e67de', mock_enforce)

    def _test_show(self, event_id, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'show', True)
        res_name = 'WikiDatabase'
        stack_identity = identifier.HeatIdentifier(self.tenant,
                                                   'wordpress', '6')
        res_identity = identifier.ResourceIdentifier(resource_name=res_name,
                                                     **stack_identity)
        ev1_identity = identifier.EventIdentifier(event_id='41',
                                                  **res_identity)
        ev_identity = identifier.EventIdentifier(event_id=event_id,
                                                 **res_identity)

        req = self._get(stack_identity._tenant_path() +
                        '/resources/' + res_name + '/events/' + event_id)

        kwargs = {'stack_identity': stack_identity,
                  'limit': None, 'sort_keys': None, 'marker': None,
                  'sort_dir': None, 'filters': None}

        engine_resp = [
            {
                u'stack_name': u'wordpress',
                u'event_time': u'2012-07-23T13:05:39Z',
                u'stack_identity': dict(stack_identity),
                u'resource_name': res_name,
                u'resource_status_reason': u'state changed',
                u'event_identity': dict(ev1_identity),
                u'resource_action': u'CREATE',
                u'resource_status': u'IN_PROGRESS',
                u'physical_resource_id': None,
                u'resource_properties': {u'UserData': u'blah'},
                u'resource_type': u'AWS::EC2::Instance',
            },
            {
                u'stack_name': u'wordpress',
                u'event_time': u'2012-07-23T13:06:00Z',
                u'stack_identity': dict(stack_identity),
                u'resource_name': res_name,
                u'resource_status_reason': u'state changed',
                u'event_identity': dict(ev_identity),
                u'resource_action': u'CREATE',
                u'resource_status': u'COMPLETE',
                u'physical_resource_id':
                u'a3455d8c-9f88-404d-a85b-5315293e67de',
                u'resource_properties': {u'UserData': u'blah'},
                u'resource_type': u'AWS::EC2::Instance',
            }
        ]
        self.m.StubOutWithMock(rpc_client.EngineClient, 'call')
        rpc_client.EngineClient.call(
            req.context,
            ('list_events', kwargs)
        ).AndReturn(engine_resp)
        self.m.ReplayAll()

        result = self.controller.show(req, tenant_id=self.tenant,
                                      stack_name=stack_identity.stack_name,
                                      stack_id=stack_identity.stack_id,
                                      resource_name=res_name,
                                      event_id=event_id)

        expected = {
            'event': {
                'id': event_id,
                'links': [
                    {'href': self._url(ev_identity), 'rel': 'self'},
                    {'href': self._url(res_identity), 'rel': 'resource'},
                    {'href': self._url(stack_identity), 'rel': 'stack'},
                ],
                u'resource_name': res_name,
                u'logical_resource_id': res_name,
                u'resource_status_reason': u'state changed',
                u'event_time': u'2012-07-23T13:06:00Z',
                u'resource_status': u'CREATE_COMPLETE',
                u'physical_resource_id':
                u'a3455d8c-9f88-404d-a85b-5315293e67de',
                u'resource_type': u'AWS::EC2::Instance',
                u'resource_properties': {u'UserData': u'blah'},
            }
        }

        self.assertEqual(expected, result)
        self.m.VerifyAll()

    def test_show_nonexist_event_id_integer(self, mock_enforce):
        self._test_show_nonexist('42', '41', mock_enforce)

    def test_show_nonexist_event_id_uuid(self, mock_enforce):
        self._test_show_nonexist('a3455d8c-9f88-404d-a85b-5315293e67de',
                                 'x3455x8x-9x88-404x-x85x-5315293x67xx',
                                 mock_enforce)

    def _test_show_nonexist(self, event_id, search_event_id, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'show', True)
        res_name = 'WikiDatabase'
        stack_identity = identifier.HeatIdentifier(self.tenant,
                                                   'wordpress', '6')
        res_identity = identifier.ResourceIdentifier(resource_name=res_name,
                                                     **stack_identity)
        ev_identity = identifier.EventIdentifier(event_id=search_event_id,
                                                 **res_identity)

        req = self._get(stack_identity._tenant_path() +
                        '/resources/' + res_name + '/events/' + event_id)

        kwargs = {'stack_identity': stack_identity,
                  'limit': None, 'sort_keys': None, 'marker': None,
                  'sort_dir': None, 'filters': None}

        engine_resp = [
            {
                u'stack_name': u'wordpress',
                u'event_time': u'2012-07-23T13:05:39Z',
                u'stack_identity': dict(stack_identity),
                u'resource_name': res_name,
                u'resource_status_reason': u'state changed',
                u'event_identity': dict(ev_identity),
                u'resource_action': u'CREATE',
                u'resource_status': u'IN_PROGRESS',
                u'physical_resource_id': None,
                u'resource_properties': {u'UserData': u'blah'},
                u'resource_type': u'AWS::EC2::Instance',
            }
        ]
        self.m.StubOutWithMock(rpc_client.EngineClient, 'call')
        rpc_client.EngineClient.call(
            req.context, ('list_events', kwargs)).AndReturn(engine_resp)
        self.m.ReplayAll()

        self.assertRaises(webob.exc.HTTPNotFound,
                          self.controller.show,
                          req, tenant_id=self.tenant,
                          stack_name=stack_identity.stack_name,
                          stack_id=stack_identity.stack_id,
                          resource_name=res_name, event_id=event_id)
        self.m.VerifyAll()

    def test_show_bad_resource(self, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'show', True)
        event_id = '42'
        res_name = 'WikiDatabase'
        stack_identity = identifier.HeatIdentifier(self.tenant,
                                                   'wordpress', '6')
        res_identity = identifier.ResourceIdentifier(resource_name=res_name,
                                                     **stack_identity)
        ev_identity = identifier.EventIdentifier(event_id='41',
                                                 **res_identity)

        req = self._get(stack_identity._tenant_path() +
                        '/resources/' + res_name + '/events/' + event_id)

        kwargs = {'stack_identity': stack_identity,
                  'limit': None, 'sort_keys': None, 'marker': None,
                  'sort_dir': None, 'filters': None}

        engine_resp = [
            {
                u'stack_name': u'wordpress',
                u'event_time': u'2012-07-23T13:05:39Z',
                u'stack_identity': dict(stack_identity),
                u'resource_name': 'SomeOtherResourceName',
                u'resource_status_reason': u'state changed',
                u'event_identity': dict(ev_identity),
                u'resource_action': u'CREATE',
                u'resource_status': u'IN_PROGRESS',
                u'physical_resource_id': None,
                u'resource_properties': {u'UserData': u'blah'},
                u'resource_type': u'AWS::EC2::Instance',
            }
        ]
        self.m.StubOutWithMock(rpc_client.EngineClient, 'call')
        rpc_client.EngineClient.call(
            req.context, ('list_events', kwargs)).AndReturn(engine_resp)
        self.m.ReplayAll()

        self.assertRaises(webob.exc.HTTPNotFound,
                          self.controller.show,
                          req, tenant_id=self.tenant,
                          stack_name=stack_identity.stack_name,
                          stack_id=stack_identity.stack_id,
                          resource_name=res_name, event_id=event_id)
        self.m.VerifyAll()

    def test_show_stack_nonexist(self, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'show', True)
        event_id = '42'
        res_name = 'WikiDatabase'
        stack_identity = identifier.HeatIdentifier(self.tenant,
                                                   'wibble', '6')

        req = self._get(stack_identity._tenant_path() +
                        '/resources/' + res_name + '/events/' + event_id)

        kwargs = {'stack_identity': stack_identity,
                  'limit': None, 'sort_keys': None, 'marker': None,
                  'sort_dir': None, 'filters': None}

        error = heat_exc.StackNotFound(stack_name='a')
        self.m.StubOutWithMock(rpc_client.EngineClient, 'call')
        rpc_client.EngineClient.call(
            req.context, ('list_events', kwargs)
        ).AndRaise(tools.to_remote_error(error))
        self.m.ReplayAll()

        resp = tools.request_with_middleware(
            fault.FaultWrapper,
            self.controller.show,
            req, tenant_id=self.tenant,
            stack_name=stack_identity.stack_name,
            stack_id=stack_identity.stack_id,
            resource_name=res_name,
            event_id=event_id)

        self.assertEqual(404, resp.json['code'])
        self.assertEqual('StackNotFound', resp.json['error']['type'])
        self.m.VerifyAll()

    def test_show_err_denied_policy(self, mock_enforce):
        self._mock_enforce_setup(mock_enforce, 'show', False)
        event_id = '42'
        res_name = 'WikiDatabase'
        stack_identity = identifier.HeatIdentifier(self.tenant,
                                                   'wibble', '6')

        req = self._get(stack_identity._tenant_path() +
                        '/resources/' + res_name + '/events/' + event_id)

        resp = tools.request_with_middleware(
            fault.FaultWrapper,
            self.controller.show,
            req, tenant_id=self.tenant,
            stack_name=stack_identity.stack_name,
            stack_id=stack_identity.stack_id,
            resource_name=res_name,
            event_id=event_id)

        self.assertEqual(403, resp.status_int)
        self.assertIn('403 Forbidden', six.text_type(resp))
