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

import datetime
import mock
from oslo_config import cfg

from heat.common import exception
from heat.engine import event
from heat.engine import rsrc_defn
from heat.engine import stack
from heat.engine import template
from heat.objects import event as event_object
from heat.objects import stack as stack_object
from heat.tests import common
from heat.tests import generic_resource as generic_rsrc
from heat.tests import utils

cfg.CONF.import_opt('event_purge_batch_size', 'heat.common.config')
cfg.CONF.import_opt('max_events_per_stack', 'heat.common.config')

tmpl = {
    'HeatTemplateFormatVersion': '2012-12-12',
    'Resources': {
        'EventTestResource': {
            'Type': 'ResourceWithRequiredProps',
            'Properties': {'Foo': 'goo'}
        }
    }
}


class EventTest(common.HeatTestCase):

    def setUp(self):
        super(EventTest, self).setUp()
        self.username = 'event_test_user'

        self.ctx = utils.dummy_context()

        self.m.ReplayAll()

        self.stack = stack.Stack(self.ctx, 'event_load_test_stack',
                                 template.Template(tmpl))
        self.stack.store()

        self.resource = self.stack['EventTestResource']
        self.resource._store()
        self.addCleanup(stack_object.Stack.delete, self.ctx, self.stack.id)

    def test_load(self):
        self.resource.resource_id_set('resource_physical_id')

        e = event.Event(self.ctx, self.stack, 'TEST', 'IN_PROGRESS', 'Testing',
                        'wibble', self.resource.properties,
                        self.resource.name, self.resource.type())

        e.store()
        self.assertIsNotNone(e.id)

        loaded_e = event.Event.load(self.ctx, e.id)

        self.assertEqual(self.stack.id, loaded_e.stack.id)
        self.assertEqual(self.resource.name, loaded_e.resource_name)
        self.assertEqual('wibble', loaded_e.physical_resource_id)
        self.assertEqual('TEST', loaded_e.action)
        self.assertEqual('IN_PROGRESS', loaded_e.status)
        self.assertEqual('Testing', loaded_e.reason)
        self.assertIsNotNone(loaded_e.timestamp)
        self.assertEqual({'Foo': 'goo'}, loaded_e.resource_properties)

    def test_load_with_timestamp(self):
        self.resource.resource_id_set('resource_physical_id')
        timestamp = datetime.datetime.utcnow()

        e = event.Event(self.ctx, self.stack, 'TEST', 'IN_PROGRESS', 'Testing',
                        'wibble', self.resource.properties,
                        self.resource.name, self.resource.type(),
                        timestamp=timestamp)

        e.store()
        self.assertIsNotNone(e.id)

        loaded_e = event.Event.load(self.ctx, e.id)

        self.assertEqual(timestamp, loaded_e.timestamp)

    def test_load_no_event(self):
        with mock.patch("heat.objects.event.Event") as event_mock:
            event_mock.get_by_id.return_value = None
            self.assertRaisesRegex(exception.NotFound,
                                   "^No event exists with id",
                                   event.Event.load, self.ctx, 1)

    def test_load_given_stack_event(self):
        self.resource.resource_id_set('resource_physical_id')

        e = event.Event(self.ctx, self.stack, 'TEST', 'IN_PROGRESS', 'Testing',
                        'wibble', self.resource.properties,
                        self.resource.name, self.resource.type())

        e.store()
        self.assertIsNotNone(e.id)

        ev = event_object.Event.get_by_id(self.ctx, e.id)

        loaded_e = event.Event.load(self.ctx, e.id, stack=self.stack, event=ev)

        self.assertEqual(self.stack.id, loaded_e.stack.id)
        self.assertEqual(self.resource.name, loaded_e.resource_name)
        self.assertEqual('wibble', loaded_e.physical_resource_id)
        self.assertEqual('TEST', loaded_e.action)
        self.assertEqual('IN_PROGRESS', loaded_e.status)
        self.assertEqual('Testing', loaded_e.reason)
        self.assertIsNotNone(loaded_e.timestamp)
        self.assertEqual({'Foo': 'goo'}, loaded_e.resource_properties)

    def test_store_caps_events(self):
        cfg.CONF.set_override('event_purge_batch_size', 1)
        cfg.CONF.set_override('max_events_per_stack', 1)
        self.resource.resource_id_set('resource_physical_id')

        e = event.Event(self.ctx, self.stack, 'TEST', 'IN_PROGRESS', 'Testing',
                        'alabama', self.resource.properties,
                        self.resource.name, self.resource.type())
        e.store()
        self.assertEqual(1, len(event_object.Event.get_all_by_stack(
            self.ctx,
            self.stack.id)))
        e = event.Event(self.ctx, self.stack, 'TEST', 'IN_PROGRESS', 'Testing',
                        'arizona', self.resource.properties,
                        self.resource.name, self.resource.type())
        e.store()
        events = event_object.Event.get_all_by_stack(self.ctx, self.stack.id)
        self.assertEqual(1, len(events))
        self.assertEqual('arizona', events[0].physical_resource_id)

    def test_identifier(self):
        event_uuid = 'abc123yc-9f88-404d-a85b-531529456xyz'
        e = event.Event(self.ctx, self.stack, 'TEST', 'IN_PROGRESS', 'Testing',
                        'wibble', self.resource.properties,
                        self.resource.name, self.resource.type(),
                        uuid=event_uuid)

        e.store()
        expected_identifier = {
            'stack_name': self.stack.name,
            'stack_id': self.stack.id,
            'tenant': self.ctx.tenant_id,
            'path': '/resources/EventTestResource/events/%s' % str(event_uuid)
        }
        self.assertEqual(expected_identifier, e.identifier())

    def test_identifier_is_none(self):
        e = event.Event(self.ctx, self.stack, 'TEST', 'IN_PROGRESS', 'Testing',
                        'wibble', self.resource.properties,
                        self.resource.name, self.resource.type())

        e.store()
        self.assertIsNone(e.identifier())

    def test_badprop(self):
        rname = 'bad_resource'
        defn = rsrc_defn.ResourceDefinition(rname,
                                            'ResourceWithRequiredProps',
                                            {'IntFoo': False})

        res = generic_rsrc.ResourceWithRequiredProps(rname, defn, self.stack)
        e = event.Event(self.ctx, self.stack, 'TEST', 'IN_PROGRESS', 'Testing',
                        'wibble', res.properties, res.name, res.type())
        self.assertIn('Error', e.resource_properties)
