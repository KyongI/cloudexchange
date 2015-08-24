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

from ceilometerclient import exc as ceil_exc
from ceilometerclient.openstack.common.apiclient import exceptions as c_a_exc
from cinderclient import exceptions as cinder_exc
from glanceclient import exc as glance_exc
from heatclient import client as heatclient
from heatclient import exc as heat_exc
from keystoneclient.auth.identity import v3
from keystoneclient import exceptions as keystone_exc
from manilaclient import exceptions as manila_exc
import mock
from neutronclient.common import exceptions as neutron_exc
from oslo_config import cfg
from saharaclient.api import base as sahara_base
import six
from swiftclient import exceptions as swift_exc
from testtools import testcase
from troveclient import client as troveclient
from zaqarclient.transport import errors as zaqar_exc

from heat.common import context
from heat.common import exception
from heat.engine import clients
from heat.engine.clients import client_plugin
from heat.tests import common
from heat.tests import fakes
from heat.tests.nova import fakes as fakes_nova
from heat.tests import utils


class ClientsTest(common.HeatTestCase):

    def test_bad_cloud_backend(self):
        con = mock.Mock()
        cfg.CONF.set_override('cloud_backend', 'some.weird.object')
        exc = self.assertRaises(exception.Invalid, clients.Clients, con)
        self.assertIn('Invalid cloud_backend setting in heat.conf detected',
                      six.text_type(exc))

        cfg.CONF.set_override('cloud_backend', 'heat.engine.clients.Clients')
        exc = self.assertRaises(exception.Invalid, clients.Clients, con)
        self.assertIn('Invalid cloud_backend setting in heat.conf detected',
                      six.text_type(exc))

    def test_clients_get_heat_url(self):
        con = mock.Mock()
        con.tenant_id = "b363706f891f48019483f8bd6503c54b"
        c = clients.Clients(con)
        con.clients = c

        obj = c.client_plugin('heat')
        obj._get_client_option = mock.Mock()
        obj._get_client_option.return_value = None
        obj.url_for = mock.Mock(name="url_for")
        obj.url_for.return_value = "url_from_keystone"
        self.assertEqual("url_from_keystone", obj.get_heat_url())
        heat_url = "http://0.0.0.0:8004/v1/%(tenant_id)s"
        obj._get_client_option.return_value = heat_url
        tenant_id = "b363706f891f48019483f8bd6503c54b"
        result = heat_url % {"tenant_id": tenant_id}
        self.assertEqual(result, obj.get_heat_url())
        obj._get_client_option.return_value = result
        self.assertEqual(result, obj.get_heat_url())

    def test_clients_get_heat_cfn_url(self):
        con = mock.Mock()
        c = clients.Clients(con)
        con.clients = c

        obj = c.client_plugin('heat')
        obj._get_client_option = mock.Mock()
        obj._get_client_option.return_value = None
        obj.url_for = mock.Mock(name="url_for")
        heat_cfn_url = "http://0.0.0.0:8000/v1"
        obj.url_for.return_value = heat_cfn_url
        self.assertEqual(heat_cfn_url, obj.get_heat_cfn_url())

    @mock.patch.object(heatclient, 'Client')
    def test_clients_heat(self, mock_call):
        self.stub_keystoneclient()
        con = mock.Mock()
        con.auth_url = "http://auth.example.com:5000/v2.0"
        con.tenant_id = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        c = clients.Clients(con)
        con.clients = c

        obj = c.client_plugin('heat')
        obj.url_for = mock.Mock(name="url_for")
        obj.url_for.return_value = "url_from_keystone"
        obj.client()
        self.assertEqual('url_from_keystone', obj.get_heat_url())

    @mock.patch.object(heatclient, 'Client')
    def test_clients_heat_no_auth_token(self, mock_call):
        con = mock.Mock()
        con.auth_url = "http://auth.example.com:5000/v2.0"
        con.tenant_id = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = None
        con.auth_plugin = fakes.FakeAuth(auth_token='anewtoken')
        self.stub_keystoneclient(context=con)
        c = clients.Clients(con)
        con.clients = c

        obj = c.client_plugin('heat')
        obj.url_for = mock.Mock(name="url_for")
        obj.url_for.return_value = "url_from_keystone"
        self.assertEqual('anewtoken', c.client('keystone').auth_token)

    @mock.patch.object(heatclient, 'Client')
    def test_clients_heat_cached(self, mock_call):
        self.stub_auth()
        con = mock.Mock()
        con.auth_url = "http://auth.example.com:5000/v2.0"
        con.tenant_id = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        con.trust_id = None
        c = clients.Clients(con)
        con.clients = c

        obj = c.client_plugin('heat')
        obj.get_heat_url = mock.Mock(name="get_heat_url")
        obj.get_heat_url.return_value = None
        obj.url_for = mock.Mock(name="url_for")
        obj.url_for.return_value = "url_from_keystone"
        obj._client = None
        heat = obj.client()
        heat_cached = obj.client()
        self.assertEqual(heat, heat_cached)


class FooClientsPlugin(client_plugin.ClientPlugin):

    def _create(self):
        pass

    @property
    def auth_token(self):
        return '5678'


class ClientPluginTest(common.HeatTestCase):

    def test_get_client_option(self):
        con = mock.Mock()
        con.auth_url = "http://auth.example.com:5000/v2.0"
        con.tenant_id = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        c = clients.Clients(con)
        con.clients = c

        plugin = FooClientsPlugin(con)

        cfg.CONF.set_override('ca_file', '/tmp/bar',
                              group='clients_heat')
        cfg.CONF.set_override('ca_file', '/tmp/foo',
                              group='clients')
        cfg.CONF.set_override('endpoint_type', 'internalURL',
                              group='clients')

        # check heat group
        self.assertEqual('/tmp/bar',
                         plugin._get_client_option('heat', 'ca_file'))

        # check fallback clients group for known client
        self.assertEqual('internalURL',
                         plugin._get_client_option('glance', 'endpoint_type'))

        # check fallback clients group for unknown client foo
        self.assertEqual('/tmp/foo',
                         plugin._get_client_option('foo', 'ca_file'))

    def test_get_client_args(self):
        plugin = FooClientsPlugin(mock.Mock())

        plugin.url_for = mock.Mock(return_value='sample_endpoint_url')
        plugin.context = mock.Mock()
        plugin.context.auth_url = 'sample_auth_url'
        plugin.context.tenant_id = 'sample_project_id'

        mock_args = {
            'endpoint_type': 'internalURL',
            'ca_file': '/tmp/ca_file',
            'cert_file': '/tmp/cert_file',
            'key_file': '/tmp/key_file',
            'insecure': True
        }

        def _side_effect(service_name, arg_name):
            return mock_args[arg_name]

        plugin._get_client_option = mock.Mock(side_effect=_side_effect)

        args = plugin._get_client_args('sample_service',
                                       'foo_type')

        self.assertEqual('foo_type',
                         args['service_type'],
                         'invalid service_type')

        self.assertEqual('sample_auth_url',
                         args['auth_url'],
                         'invalid auth_url')

        self.assertEqual('sample_project_id',
                         args['project_id'],
                         'invalid project_id')

        self.assertEqual('5678',
                         args['token'](),
                         'invalid auth_token')

        self.assertEqual('sample_endpoint_url',
                         args['os_endpoint'],
                         'invalid os_endpoint')

        self.assertEqual('internalURL',
                         args['endpoint_type'],
                         'invalid endpoint_type')

        self.assertEqual('/tmp/ca_file',
                         args['cacert'],
                         'invalid cacert')

        self.assertEqual('/tmp/cert_file',
                         args['cert_file'],
                         'invalid cert_file')

        self.assertEqual('/tmp/key_file',
                         args['key_file'],
                         'invalid key_file')

        self.assertTrue(args['insecure'],
                        'invalid insecure')

    def test_auth_token(self):
        con = mock.Mock()
        con.auth_token = "1234"
        con.trust_id = None

        c = clients.Clients(con)
        con.clients = c

        plugin = FooClientsPlugin(con)

        # assert token is from plugin rather than context
        # even though both are set
        self.assertEqual('5678', plugin.auth_token)

    def test_url_for(self):
        con = mock.Mock()
        con.auth_token = "1234"
        con.trust_id = None

        c = clients.Clients(con)
        con.clients = c

        con.auth_plugin = mock.Mock(name="auth_plugin")
        con.auth_plugin.get_endpoint = mock.Mock(name="get_endpoint")
        con.auth_plugin.get_endpoint.return_value = 'http://192.0.2.1/foo'
        plugin = FooClientsPlugin(con)

        self.assertEqual('http://192.0.2.1/foo',
                         plugin.url_for(service_type='foo'))
        self.assertTrue(con.auth_plugin.get_endpoint.called)

    @mock.patch.object(context, "RequestContext")
    @mock.patch.object(v3, "Token", name="v3_token")
    def test_get_missing_service_catalog(self, mock_v3, mkreqctx):
        class FakeKeystone(fakes.FakeKeystoneClient):
            def __init__(self):
                super(FakeKeystone, self).__init__()
                self.client = self
                self.version = 'v3'

        self.stub_keystoneclient(fake_client=FakeKeystone())
        con = mock.Mock(auth_token="1234", trust_id=None)
        c = clients.Clients(con)
        con.clients = c

        con.auth_plugin = mock.Mock(name="auth_plugin")
        get_endpoint_side_effects = [
            keystone_exc.EmptyCatalog(), None, 'http://192.0.2.1/bar']
        con.auth_plugin.get_endpoint = mock.Mock(
            name="get_endpoint", side_effect=get_endpoint_side_effects)

        mock_token_obj = mock.Mock()
        mock_token_obj.get_auth_ref.return_value = {'catalog': 'foo'}
        mock_v3.return_value = mock_token_obj

        plugin = FooClientsPlugin(con)
        mock_cxt_dict = {'auth_token_info': {'token': {'catalog': 'baz'}}}
        plugin.context.to_dict.return_value = mock_cxt_dict

        mkreqctx.from_dict.return_value.auth_plugin = con.auth_plugin

        self.assertEqual('http://192.0.2.1/bar',
                         plugin.url_for(service_type='bar'))

    def test_abstract_create(self):
        con = mock.Mock()
        c = clients.Clients(con)
        con.clients = c

        self.assertRaises(TypeError, client_plugin.ClientPlugin, c)


class TestClientPluginsInitialise(common.HeatTestCase):

    @testcase.skip('skipped until keystone can read context auth_ref')
    def test_create_all_clients(self):
        con = mock.Mock()
        con.auth_url = "http://auth.example.com:5000/v2.0"
        con.tenant_id = "b363706f891f48019483f8bd6503c54b"
        con.auth_token = "3bcc3d3a03f44e3d8377f9247b0ad155"
        c = clients.Clients(con)
        con.clients = c

        for plugin_name in clients._mgr.names():
            self.assertTrue(clients.has_client(plugin_name))
            c.client(plugin_name)

    def test_create_all_client_plugins(self):
        plugin_types = clients._mgr.names()
        self.assertIsNotNone(plugin_types)

        con = mock.Mock()
        c = clients.Clients(con)
        con.clients = c

        for plugin_name in plugin_types:
            plugin = c.client_plugin(plugin_name)
            self.assertIsNotNone(plugin)
            self.assertEqual(c, plugin.clients)
            self.assertEqual(con, plugin.context)
            self.assertIsNone(plugin._client)
            self.assertTrue(clients.has_client(plugin_name))
            self.assertTrue(isinstance(plugin.service_types, list))
            self.assertTrue(len(plugin.service_types) >= 1,
                            'service_types is not defined for plugin')


class TestIsNotFound(common.HeatTestCase):

    scenarios = [
        ('ceilometer_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='ceilometer',
            exception=lambda: ceil_exc.HTTPNotFound(details='gone'),
        )),
        ('ceilometer_not_found_apiclient', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='ceilometer',
            exception=lambda: c_a_exc.NotFound(details='gone'),
        )),
        ('ceilometer_exception', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=False,
            is_conflict=False,
            plugin='ceilometer',
            exception=lambda: Exception()
        )),
        ('ceilometer_overlimit', dict(
            is_not_found=False,
            is_over_limit=True,
            is_client_exception=True,
            is_conflict=False,
            plugin='ceilometer',
            exception=lambda: ceil_exc.HTTPOverLimit(details='over'),
        )),
        ('ceilometer_conflict', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=True,
            plugin='ceilometer',
            exception=lambda: ceil_exc.HTTPConflict(),
        )),
        ('cinder_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='cinder',
            exception=lambda: cinder_exc.NotFound(code=404),
        )),
        ('cinder_exception', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=False,
            is_conflict=False,
            plugin='cinder',
            exception=lambda: Exception()
        )),
        ('cinder_overlimit', dict(
            is_not_found=False,
            is_over_limit=True,
            is_client_exception=True,
            is_conflict=False,
            plugin='cinder',
            exception=lambda: cinder_exc.OverLimit(code=413),
        )),
        ('cinder_conflict', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=True,
            plugin='cinder',
            exception=lambda: cinder_exc.ClientException(
                code=409, message='conflict'),
        )),
        ('glance_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='glance',
            exception=lambda: glance_exc.HTTPNotFound(details='gone'),
        )),
        ('glance_exception', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=False,
            is_conflict=False,
            plugin='glance',
            exception=lambda: Exception()
        )),
        ('glance_overlimit', dict(
            is_not_found=False,
            is_over_limit=True,
            is_client_exception=True,
            is_conflict=False,
            plugin='glance',
            exception=lambda: glance_exc.HTTPOverLimit(details='over'),
        )),
        ('glance_conflict', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=True,
            plugin='glance',
            exception=lambda: glance_exc.HTTPConflict(),
        )),
        ('heat_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='heat',
            exception=lambda: heat_exc.HTTPNotFound(message='gone'),
        )),
        ('heat_exception', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=False,
            is_conflict=False,
            plugin='heat',
            exception=lambda: Exception()
        )),
        ('heat_overlimit', dict(
            is_not_found=False,
            is_over_limit=True,
            is_client_exception=True,
            is_conflict=False,
            plugin='heat',
            exception=lambda: heat_exc.HTTPOverLimit(message='over'),
        )),
        ('heat_conflict', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=True,
            plugin='heat',
            exception=lambda: heat_exc.HTTPConflict(),
        )),
        ('keystone_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='keystone',
            exception=lambda: keystone_exc.NotFound(details='gone'),
        )),
        ('keystone_exception', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=False,
            is_conflict=False,
            plugin='keystone',
            exception=lambda: Exception()
        )),
        ('keystone_overlimit', dict(
            is_not_found=False,
            is_over_limit=True,
            is_client_exception=True,
            is_conflict=False,
            plugin='keystone',
            exception=lambda: keystone_exc.RequestEntityTooLarge(
                details='over'),
        )),
        ('keystone_conflict', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=True,
            plugin='keystone',
            exception=lambda: keystone_exc.Conflict(
                message='Conflict'),
        )),
        ('neutron_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='neutron',
            exception=lambda: neutron_exc.NotFound,
        )),
        ('neutron_network_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='neutron',
            exception=lambda: neutron_exc.NetworkNotFoundClient(),
        )),
        ('neutron_port_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='neutron',
            exception=lambda: neutron_exc.PortNotFoundClient(),
        )),
        ('neutron_status_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='neutron',
            exception=lambda: neutron_exc.NeutronClientException(
                status_code=404),
        )),
        ('neutron_exception', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=False,
            is_conflict=False,
            plugin='neutron',
            exception=lambda: Exception()
        )),
        ('neutron_overlimit', dict(
            is_not_found=False,
            is_over_limit=True,
            is_client_exception=True,
            is_conflict=False,
            plugin='neutron',
            exception=lambda: neutron_exc.NeutronClientException(
                status_code=413),
        )),
        ('neutron_conflict', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=True,
            plugin='neutron',
            exception=lambda: neutron_exc.Conflict(),
        )),
        ('nova_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            is_unprocessable_entity=False,
            plugin='nova',
            exception=lambda: fakes_nova.fake_exception(),
        )),
        ('nova_exception', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=False,
            is_conflict=False,
            is_unprocessable_entity=False,
            plugin='nova',
            exception=lambda: Exception()
        )),
        ('nova_overlimit', dict(
            is_not_found=False,
            is_over_limit=True,
            is_client_exception=True,
            is_conflict=False,
            is_unprocessable_entity=False,
            plugin='nova',
            exception=lambda: fakes_nova.fake_exception(413),
        )),
        ('nova_unprocessable_entity', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            is_unprocessable_entity=True,
            plugin='nova',
            exception=lambda: fakes_nova.fake_exception(422),
        )),
        ('nova_conflict', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=True,
            is_unprocessable_entity=False,
            plugin='nova',
            exception=lambda: fakes_nova.fake_exception(409),
        )),
        ('swift_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='swift',
            exception=lambda: swift_exc.ClientException(
                msg='gone', http_status=404),
        )),
        ('swift_exception', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=False,
            is_conflict=False,
            plugin='swift',
            exception=lambda: Exception()
        )),
        ('swift_overlimit', dict(
            is_not_found=False,
            is_over_limit=True,
            is_client_exception=True,
            is_conflict=False,
            plugin='swift',
            exception=lambda: swift_exc.ClientException(
                msg='ouch', http_status=413),
        )),
        ('swift_conflict', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=True,
            plugin='swift',
            exception=lambda: swift_exc.ClientException(
                msg='conflict', http_status=409),
        )),
        ('trove_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='trove',
            exception=lambda: troveclient.exceptions.NotFound(message='gone'),
        )),
        ('trove_exception', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=False,
            is_conflict=False,
            plugin='trove',
            exception=lambda: Exception()
        )),
        ('trove_overlimit', dict(
            is_not_found=False,
            is_over_limit=True,
            is_client_exception=True,
            is_conflict=False,
            plugin='trove',
            exception=lambda: troveclient.exceptions.RequestEntityTooLarge(
                message='over'),
        )),
        ('trove_conflict', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=True,
            plugin='trove',
            exception=lambda: troveclient.exceptions.Conflict(
                message='Conflict'),
        )),
        ('sahara_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='sahara',
            exception=lambda: sahara_base.APIException(
                error_message='gone1', error_code=404),
        )),
        ('sahara_exception', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=False,
            is_conflict=False,
            plugin='sahara',
            exception=lambda: Exception()
        )),
        ('sahara_overlimit', dict(
            is_not_found=False,
            is_over_limit=True,
            is_client_exception=True,
            is_conflict=False,
            plugin='sahara',
            exception=lambda: sahara_base.APIException(
                error_message='over1', error_code=413),
        )),
        ('sahara_conflict', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=True,
            plugin='sahara',
            exception=lambda: sahara_base.APIException(
                error_message='conflict1', error_code=409),
        )),
        ('zaqar_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='zaqar',
            exception=lambda: zaqar_exc.ResourceNotFound(),
        )),
        ('manila_not_found', dict(
            is_not_found=True,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=False,
            plugin='manila',
            exception=lambda: manila_exc.NotFound(),
        )),
        ('manila_exception', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=False,
            is_conflict=False,
            plugin='manila',
            exception=lambda: Exception()
        )),
        ('manila_overlimit', dict(
            is_not_found=False,
            is_over_limit=True,
            is_client_exception=True,
            is_conflict=False,
            plugin='manila',
            exception=lambda: manila_exc.RequestEntityTooLarge(),
        )),
        ('manila_conflict', dict(
            is_not_found=False,
            is_over_limit=False,
            is_client_exception=True,
            is_conflict=True,
            plugin='manila',
            exception=lambda: manila_exc.Conflict(),
        )),
    ]

    def test_is_not_found(self):
        con = mock.Mock()
        c = clients.Clients(con)
        client_plugin = c.client_plugin(self.plugin)
        try:
            raise self.exception()
        except Exception as e:
            if self.is_not_found != client_plugin.is_not_found(e):
                raise

    def test_ignore_not_found(self):
        con = mock.Mock()
        c = clients.Clients(con)
        client_plugin = c.client_plugin(self.plugin)
        try:
            exp = self.exception()
            exp_class = exp.__class__
            raise exp
        except Exception as e:
            if self.is_not_found:
                client_plugin.ignore_not_found(e)
            else:
                self.assertRaises(exp_class,
                                  client_plugin.ignore_not_found,
                                  e)

    def test_ignore_conflict_and_not_found(self):
        con = mock.Mock()
        c = clients.Clients(con)
        client_plugin = c.client_plugin(self.plugin)
        try:
            exp = self.exception()
            exp_class = exp.__class__
            raise exp
        except Exception as e:
            if self.is_conflict or self.is_not_found:
                client_plugin.ignore_conflict_and_not_found(e)
            else:
                self.assertRaises(exp_class,
                                  client_plugin.ignore_conflict_and_not_found,
                                  e)

    def test_is_over_limit(self):
        con = mock.Mock()
        c = clients.Clients(con)
        client_plugin = c.client_plugin(self.plugin)
        try:
            raise self.exception()
        except Exception as e:
            if self.is_over_limit != client_plugin.is_over_limit(e):
                raise

    def test_is_client_exception(self):
        con = mock.Mock()
        c = clients.Clients(con)
        client_plugin = c.client_plugin(self.plugin)
        try:
            raise self.exception()
        except Exception as e:
            ice = self.is_client_exception
            actual = client_plugin.is_client_exception(e)
            if ice != actual:
                raise

    def test_is_conflict(self):
        con = mock.Mock()
        c = clients.Clients(con)
        client_plugin = c.client_plugin(self.plugin)
        try:
            raise self.exception()
        except Exception as e:
            if self.is_conflict != client_plugin.is_conflict(e):
                raise

    def test_is_unprocessable_entity(self):
        con = mock.Mock()
        c = clients.Clients(con)
        # only 'nova' client plugin need to check this exception
        if self.plugin == 'nova':
            client_plugin = c.client_plugin(self.plugin)
            try:
                raise self.exception()
            except Exception as e:
                iue = self.is_unprocessable_entity
                if iue != client_plugin.is_unprocessable_entity(e):
                    raise


class ClientAPIVersionTest(common.HeatTestCase):

    def test_cinder_api_v1_and_v2(self):
        self.stub_auth()
        ctx = utils.dummy_context()
        client = clients.Clients(ctx).client('cinder')
        self.assertEqual(2, client.volume_api_version)

    def test_cinder_api_v1_only(self):
        self.stub_auth(only_services=['volume'])
        ctx = utils.dummy_context()
        client = clients.Clients(ctx).client('cinder')
        self.assertEqual(1, client.volume_api_version)

    def test_cinder_api_v2_only(self):
        self.stub_auth(only_services=['volumev2'])
        ctx = utils.dummy_context()
        client = clients.Clients(ctx).client('cinder')
        self.assertEqual(2, client.volume_api_version)
