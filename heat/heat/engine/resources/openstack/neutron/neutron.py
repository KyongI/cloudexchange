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
from oslo_utils import uuidutils
import six

import warnings

from heat.common import exception
from heat.common.i18n import _
from heat.engine import properties as properties_module
from heat.engine import resource


class NeutronResource(resource.Resource):

    default_client_name = 'neutron'

    def validate(self):
        '''
        Validate any of the provided params
        '''
        res = super(NeutronResource, self).validate()
        if res:
            return res
        return self.validate_properties(self.properties)

    @staticmethod
    def validate_properties(properties):
        '''
        Validates to ensure nothing in value_specs overwrites
        any key that exists in the schema.

        Also ensures that shared and tenant_id is not specified
        in value_specs.
        '''
        if 'value_specs' in six.iterkeys(properties):
            vs = properties.get('value_specs')
            banned_keys = set(['shared', 'tenant_id']).union(
                six.iterkeys(properties))
            for k in banned_keys.intersection(six.iterkeys(vs)):
                return '%s not allowed in value_specs' % k

    @staticmethod
    def _validate_depr_property_required(properties, prop_key, depr_prop_key):
        if isinstance(properties, properties_module.Properties):
            prop_value = properties.data.get(prop_key)
            depr_prop_value = properties.data.get(depr_prop_key)
        else:
            prop_value = properties.get(prop_key)
            depr_prop_value = properties.get(depr_prop_key)

        if prop_value and depr_prop_value:
            raise exception.ResourcePropertyConflict(prop_key,
                                                     depr_prop_key)
        if not prop_value and not depr_prop_value:
            raise exception.PropertyUnspecifiedError(prop_key,
                                                     depr_prop_key)

    @staticmethod
    def prepare_properties(properties, name):
        '''
        Prepares the property values so that they can be passed directly to
        the Neutron create call.

        Removes None values and value_specs, merges value_specs with the main
        values.
        '''
        props = dict((k, v) for k, v in properties.items()
                     if v is not None and k != 'value_specs')

        if 'name' in six.iterkeys(properties):
            props.setdefault('name', name)

        if 'value_specs' in six.iterkeys(properties):
            props.update(properties.get('value_specs'))

        return props

    def prepare_update_properties(self, definition):
        '''
        Prepares the property values so that they can be passed directly to
        the Neutron update call.

        Removes any properties which are not update_allowed, then processes
        as for prepare_properties.
        '''
        p = definition.properties(self.properties_schema, self.context)
        update_props = dict((k, v) for k, v in p.items()
                            if p.props.get(k).schema.update_allowed)

        props = self.prepare_properties(
            update_props,
            self.physical_resource_name())
        return props

    @staticmethod
    def is_built(attributes):
        status = attributes['status']
        if status == 'BUILD':
            return False
        if status in ('ACTIVE', 'DOWN'):
            return True
        elif status == 'ERROR':
            raise resource.ResourceInError(
                resource_status=status)
        else:
            raise resource.ResourceUnknownStatus(
                resource_status=status,
                result=_('Resource is not built'))

    def _resolve_attribute(self, name):
        try:
            attributes = self._show_resource()
        except Exception as ex:
            self.client_plugin().ignore_not_found(ex)
            return None
        return attributes[name]

    def FnGetRefId(self):
        return six.text_type(self.resource_id)

    @staticmethod
    def get_secgroup_uuids(security_groups, client, tenant_id):
        '''
        Returns a list of security group UUIDs.
        Args:
            security_groups: List of security group names or UUIDs
            client: reference to neutronclient
            tenant_id: the tenant id to match the security_groups
        '''
        warnings.warn('neutron.NeutronResource.get_secgroup_uuids is '
                      'deprecated. Use '
                      'self.client_plugin("neutron").get_secgroup_uuids')
        seclist = []
        all_groups = None
        for sg in security_groups:
            if uuidutils.is_uuid_like(sg):
                seclist.append(sg)
            else:
                if not all_groups:
                    response = client.list_security_groups()
                    all_groups = response['security_groups']
                same_name_groups = [g for g in all_groups if g['name'] == sg]
                groups = [g['id'] for g in same_name_groups]
                if len(groups) == 0:
                    raise exception.PhysicalResourceNotFound(resource_id=sg)
                elif len(groups) == 1:
                    seclist.append(groups[0])
                else:
                    # for admin roles, can get the other users'
                    # securityGroups, so we should match the tenant_id with
                    # the groups, and return the own one
                    own_groups = [g['id'] for g in same_name_groups
                                  if g['tenant_id'] == tenant_id]
                    if len(own_groups) == 1:
                        seclist.append(own_groups[0])
                    else:
                        raise exception.PhysicalResourceNameAmbiguity(name=sg)
        return seclist

    def _not_found_in_call(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as ex:
            self.client_plugin().ignore_not_found(ex)
            return True
        else:
            return False

    def check_delete_complete(self, check):
        # NOTE(pshchelo): when longer check is needed, check is returned
        # as True, otherwise None is implicitly returned as check
        if not check:
            return True

        return self._not_found_in_call(self._show_resource)
