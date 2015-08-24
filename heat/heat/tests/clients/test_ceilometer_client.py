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

from ceilometerclient import client as cc
from keystoneclient import exceptions

from heat.tests import common
from heat.tests import utils


class CeilometerClientPluginTests(common.HeatTestCase):

    def test_create(self):
        self.patchobject(cc.AuthPlugin, 'redirect_to_aodh_endpoint',
                         side_effect=exceptions.EndpointNotFound)
        context = utils.dummy_context()
        plugin = context.clients.client_plugin('ceilometer')
        client = plugin.client()
        self.assertIsNotNone(client.alarms)
        self.assertEqual('http://server.test:5000/v2.0',
                         client.auth_plugin.opts['auth_url'])
