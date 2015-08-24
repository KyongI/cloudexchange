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

"""Resources for Rackspace DNS."""

from oslo_log import log as logging

from heat.common import exception
from heat.common.i18n import _
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine import support

try:
    from pyrax.exceptions import NotFound
    PYRAX_INSTALLED = True
except ImportError:
    # Setup fake exception for testing without pyrax
    class NotFound(Exception):
        pass

    PYRAX_INSTALLED = False

LOG = logging.getLogger(__name__)


class CloudDns(resource.Resource):

    """Represents a DNS resource."""

    support_status = support.SupportStatus(
        status=support.UNSUPPORTED,
        message=_('This resource is not supported, use at your own risk.'))

    PROPERTIES = (
        NAME, EMAIL_ADDRESS, TTL, COMMENT, RECORDS,
    ) = (
        'name', 'emailAddress', 'ttl', 'comment', 'records',
    )

    _RECORD_KEYS = (
        RECORD_COMMENT, RECORD_NAME, RECORD_DATA, RECORD_PRIORITY, RECORD_TTL,
        RECORD_TYPE,
    ) = (
        'comment', 'name', 'data', 'priority', 'ttl',
        'type',
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Specifies the name for the domain or subdomain. Must be a '
              'valid domain name.'),
            required=True,
            constraints=[
                constraints.Length(min=3),
            ]
        ),
        EMAIL_ADDRESS: properties.Schema(
            properties.Schema.STRING,
            _('Email address to use for contacting the domain administrator.'),
            required=True,
            update_allowed=True
        ),
        TTL: properties.Schema(
            properties.Schema.INTEGER,
            _('How long other servers should cache recorddata.'),
            default=3600,
            constraints=[
                constraints.Range(min=300),
            ],
            update_allowed=True
        ),
        COMMENT: properties.Schema(
            properties.Schema.STRING,
            _('Optional free form text comment'),
            constraints=[
                constraints.Length(max=160),
            ],
            update_allowed=True
        ),
        RECORDS: properties.Schema(
            properties.Schema.LIST,
            _('Domain records'),
            schema=properties.Schema(
                properties.Schema.MAP,
                schema={
                    RECORD_COMMENT: properties.Schema(
                        properties.Schema.STRING,
                        _('Optional free form text comment'),
                        constraints=[
                            constraints.Length(max=160),
                        ]
                    ),
                    RECORD_NAME: properties.Schema(
                        properties.Schema.STRING,
                        _('Specifies the name for the domain or '
                          'subdomain. Must be a valid domain name.'),
                        required=True,
                        constraints=[
                            constraints.Length(min=3),
                        ]
                    ),
                    RECORD_DATA: properties.Schema(
                        properties.Schema.STRING,
                        _('Type specific record data'),
                        required=True
                    ),
                    RECORD_PRIORITY: properties.Schema(
                        properties.Schema.INTEGER,
                        _('Required for MX and SRV records, but '
                          'forbidden for other record types. If '
                          'specified, must be an integer from 0 to '
                          '65535.'),
                        constraints=[
                            constraints.Range(0, 65535),
                        ]
                    ),
                    RECORD_TTL: properties.Schema(
                        properties.Schema.INTEGER,
                        _('How long other servers should cache '
                          'recorddata.'),
                        default=3600,
                        constraints=[
                            constraints.Range(min=300),
                        ]
                    ),
                    RECORD_TYPE: properties.Schema(
                        properties.Schema.STRING,
                        _('Specifies the record type.'),
                        required=True,
                        constraints=[
                            constraints.AllowedValues(['A', 'AAAA', 'NS',
                                                       'MX', 'CNAME',
                                                       'TXT', 'SRV']),
                        ]
                    ),
                },
            ),
            update_allowed=True
        ),
    }

    def cloud_dns(self):
        return self.client('cloud_dns')

    def handle_create(self):
        """Create a Rackspace CloudDns Instance."""
        # There is no check_create_complete as the pyrax create for DNS is
        # synchronous.
        LOG.debug("CloudDns handle_create called.")
        args = dict((k, v) for k, v in self.properties.items())
        for rec in args[self.RECORDS] or {}:
            # only pop the priority for the correct types
            rec_type = rec[self.RECORD_TYPE]
            if (rec_type != 'MX') and (rec_type != 'SRV'):
                rec.pop(self.RECORD_PRIORITY, None)
        dom = self.cloud_dns().create(**args)
        self.resource_id_set(dom.id)

    def handle_check(self):
        self.cloud_dns().get(self.resource_id)

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        """Update a Rackspace CloudDns Instance."""
        LOG.debug("CloudDns handle_update called.")
        if not self.resource_id:
            raise exception.Error(_('Update called on a non-existent domain'))
        if prop_diff:
            dom = self.cloud_dns().get(self.resource_id)

            # handle records separately
            records = prop_diff.pop(self.RECORDS, {})

        if prop_diff:
            # Handle top level domain properties
            dom.update(**prop_diff)

        # handle records
        if records:
            recs = dom.list_records()
            # 1. delete all the current records other than rackspace NS records
            [rec.delete() for rec in recs if rec.type != 'NS' or
                'stabletransit.com' not in rec.data]
            # 2. update with the new records in prop_diff
            dom.add_records(records)

    def handle_delete(self):
        """Delete a Rackspace CloudDns Instance."""
        LOG.debug("CloudDns handle_delete called.")
        if self.resource_id:
            try:
                dom = self.cloud_dns().get(self.resource_id)
                dom.delete()
            except NotFound:
                pass


def resource_mapping():
    return {'Rackspace::Cloud::DNS': CloudDns}


def available_resource_mapping():
    if PYRAX_INSTALLED:
        return resource_mapping()
    return {}
