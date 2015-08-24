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

from oslo_log import log as logging
from oslo_serialization import jsonutils
from oslo_utils import timeutils
import six

from heat.common.i18n import _
from heat.common.i18n import _LI
from heat.engine import attributes
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine.resources import wait_condition as wc_base
from heat.engine import support

LOG = logging.getLogger(__name__)


class HeatWaitCondition(resource.Resource):

    support_status = support.SupportStatus(version='2014.2')

    PROPERTIES = (
        HANDLE, TIMEOUT, COUNT,
    ) = (
        'handle', 'timeout', 'count',
    )

    ATTRIBUTES = (
        DATA,
    ) = (
        'data',
    )

    properties_schema = {
        HANDLE: properties.Schema(
            properties.Schema.STRING,
            _('A reference to the wait condition handle used to signal this '
              'wait condition.'),
            required=True
        ),
        TIMEOUT: properties.Schema(
            properties.Schema.NUMBER,
            _('The number of seconds to wait for the correct number of '
              'signals to arrive.'),
            required=True,
            constraints=[
                constraints.Range(1, 43200),
            ]
        ),
        COUNT: properties.Schema(
            properties.Schema.INTEGER,
            _('The number of success signals that must be received before '
              'the stack creation process continues.'),
            constraints=[
                constraints.Range(min=1),
            ],
            default=1,
            update_allowed=True
        ),
    }

    attributes_schema = {
        DATA: attributes.Schema(
            _('JSON string containing data associated with wait '
              'condition signals sent to the handle.'),
            cache_mode=attributes.Schema.CACHE_NONE,
            type=attributes.Schema.STRING
        ),
    }

    def __init__(self, name, definition, stack):
        super(HeatWaitCondition, self).__init__(name, definition, stack)

    def _get_handle_resource(self):
        return self.stack.resource_by_refid(self.properties[self.HANDLE])

    def _wait(self, handle, started_at, timeout_in):
        if timeutils.is_older_than(started_at, timeout_in):
            exc = wc_base.WaitConditionTimeout(self, handle)
            LOG.info(_LI('%(name)s Timed out (%(timeout)s)'),
                     {'name': str(self), 'timeout': str(exc)})
            raise exc

        handle_status = handle.get_status()

        if any(s != handle.STATUS_SUCCESS for s in handle_status):
            failure = wc_base.WaitConditionFailure(self, handle)
            LOG.info(_LI('%(name)s Failed (%(failure)s)'),
                     {'name': str(self), 'failure': str(failure)})
            raise failure

        if len(handle_status) >= self.properties[self.COUNT]:
            LOG.info(_LI("%s Succeeded"), str(self))
            return True
        return False

    def handle_create(self):
        handle = self._get_handle_resource()
        started_at = timeutils.utcnow()
        return handle, started_at, float(self.properties[self.TIMEOUT])

    def check_create_complete(self, data):
        return self._wait(*data)

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        if prop_diff:
            self.properties = json_snippet.properties(self.properties_schema,
                                                      self.context)

        handle = self._get_handle_resource()
        started_at = timeutils.utcnow()
        return handle, started_at, float(self.properties[self.TIMEOUT])

    def check_update_complete(self, data):
        return self._wait(*data)

    def handle_delete(self):
        handle = self._get_handle_resource()
        if handle:
            handle.metadata_set({})

    def _resolve_attribute(self, key):
        handle = self._get_handle_resource()
        if key == self.DATA:
            meta = handle.metadata_get(refresh=True)
            res = {k: meta[k][handle.DATA] for k in meta}
            LOG.debug('%(name)s.GetAtt(%(key)s) == %(res)s'
                      % {'name': self.name,
                         'key': key,
                         'res': res})

            return six.text_type(jsonutils.dumps(res))


def resource_mapping():
    return {
        'OS::Heat::WaitCondition': HeatWaitCondition,
    }
