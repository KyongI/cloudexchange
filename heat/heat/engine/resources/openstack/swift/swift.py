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
import six
from six.moves.urllib import parse as urlparse

from heat.common import exception
from heat.common.i18n import _
from heat.common.i18n import _LW
from heat.engine import attributes
from heat.engine import properties
from heat.engine import resource
from heat.engine import support

LOG = logging.getLogger(__name__)


class SwiftContainer(resource.Resource):
    PROPERTIES = (
        NAME, X_CONTAINER_READ, X_CONTAINER_WRITE, X_CONTAINER_META,
        X_ACCOUNT_META, PURGE_ON_DELETE,
    ) = (
        'name', 'X-Container-Read', 'X-Container-Write', 'X-Container-Meta',
        'X-Account-Meta', 'PurgeOnDelete',
    )

    ATTRIBUTES = (
        DOMAIN_NAME, WEBSITE_URL, ROOT_URL, OBJECT_COUNT, BYTES_USED,
        HEAD_CONTAINER,
    ) = (
        'DomainName', 'WebsiteURL', 'RootURL', 'ObjectCount', 'BytesUsed',
        'HeadContainer',
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name for the container. If not specified, a unique name will '
              'be generated.')
        ),
        X_CONTAINER_READ: properties.Schema(
            properties.Schema.STRING,
            _('Specify the ACL permissions on who can read objects in the '
              'container.')
        ),
        X_CONTAINER_WRITE: properties.Schema(
            properties.Schema.STRING,
            _('Specify the ACL permissions on who can write objects to the '
              'container.')
        ),
        X_CONTAINER_META: properties.Schema(
            properties.Schema.MAP,
            _('A map of user-defined meta data to associate with the '
              'container. Each key in the map will set the header '
              'X-Container-Meta-{key} with the corresponding value.'),
            default={}
        ),
        X_ACCOUNT_META: properties.Schema(
            properties.Schema.MAP,
            _('A map of user-defined meta data to associate with the '
              'account. Each key in the map will set the header '
              'X-Account-Meta-{key} with the corresponding value.'),
            default={}
        ),
        PURGE_ON_DELETE: properties.Schema(
            properties.Schema.BOOLEAN,
            _("If True, delete any objects in the container "
              "when the container is deleted. "
              "Otherwise, deleting a non-empty container "
              "will result in an error."),
            default=False,
            support_status=support.SupportStatus(
                version='2015.1')
        ),
    }

    attributes_schema = {
        DOMAIN_NAME: attributes.Schema(
            _('The host from the container URL.'),
            type=attributes.Schema.STRING
        ),
        WEBSITE_URL: attributes.Schema(
            _('The URL of the container.'),
            type=attributes.Schema.STRING
        ),
        ROOT_URL: attributes.Schema(
            _('The parent URL of the container.'),
            type=attributes.Schema.STRING
        ),
        OBJECT_COUNT: attributes.Schema(
            _('The number of objects stored in the container.'),
            type=attributes.Schema.INTEGER
        ),
        BYTES_USED: attributes.Schema(
            _('The number of bytes stored in the container.'),
            type=attributes.Schema.INTEGER
        ),
        HEAD_CONTAINER: attributes.Schema(
            _('A map containing all headers for the container.'),
            type=attributes.Schema.MAP
        ),
    }

    default_client_name = 'swift'

    def physical_resource_name(self):
        name = self.properties[self.NAME]
        if name:
            return name

        return super(SwiftContainer, self).physical_resource_name()

    @staticmethod
    def _build_meta_headers(obj_type, meta_props):
        '''
        Returns a new dict where each key is prepended with:
        X-Container-Meta-
        '''
        if meta_props is None:
            return {}
        return dict(
            ('X-' + obj_type.title() + '-Meta-' + k, v)
            for (k, v) in meta_props.items())

    def handle_create(self):
        """Create a container."""
        container = self.physical_resource_name()

        container_headers = SwiftContainer._build_meta_headers(
            "container", self.properties[self.X_CONTAINER_META])

        account_headers = SwiftContainer._build_meta_headers(
            "account", self.properties[self.X_ACCOUNT_META])

        for key in (self.X_CONTAINER_READ, self.X_CONTAINER_WRITE):
            if self.properties[key] is not None:
                container_headers[key] = self.properties[key]

        LOG.debug('SwiftContainer create container %(container)s with '
                  'container headers %(container_headers)s and '
                  'account headers %(account_headers)s'
                  % {'container': container,
                     'account_headers': account_headers,
                     'container_headers': container_headers})

        self.client().put_container(container, container_headers)

        if account_headers:
            self.client().post_account(account_headers)

        self.resource_id_set(container)

    def _get_objects(self):
        try:
            container, objects = self.client().get_container(self.resource_id)
        except Exception as ex:
            self.client_plugin().ignore_not_found(ex)
            return None
        return objects

    def _deleter(self, obj=None):
        """Delete the underlying container or an object inside it."""
        args = [self.resource_id]
        if obj:
            deleter = self.client().delete_object
            args.append(obj['name'])
        else:
            deleter = self.client().delete_container
        try:
            deleter(*args)
        except Exception as ex:
            self.client_plugin().ignore_not_found(ex)

    def handle_delete(self):
        if self.resource_id is None:
            return

        objects = self._get_objects()

        if objects:
            if self.properties[self.PURGE_ON_DELETE]:
                self._deleter(objects.pop())  # save first container refresh
            else:
                msg = _("Deleting non-empty container (%(id)s) "
                        "when %(prop)s is False") % {
                            'id': self.resource_id,
                            'prop': self.PURGE_ON_DELETE}
                raise exception.ResourceActionNotSupported(action=msg)
        # objects is either None (container is gone already) or (empty) list
        if objects is not None:
            objects = len(objects)
        return objects

    def check_delete_complete(self, objects):
        if objects is None:  # resource was not created or is gone already
            return True
        if objects:  # integer >=0 from the first invocation
            objs = self._get_objects()
            if objs is None:
                return True  # container is gone already
            if objs:
                self._deleter(objs.pop())
                if objs:  # save one last _get_objects() API call
                    return False

        self._deleter()
        return True

    def handle_check(self):
        self.client().get_container(self.resource_id)

    def FnGetRefId(self):
        return six.text_type(self.resource_id)

    def _resolve_attribute(self, key):
        parsed = list(urlparse.urlparse(self.client().url))
        if key == self.DOMAIN_NAME:
            return parsed[1].split(':')[0]
        elif key == self.WEBSITE_URL:
            return '%s://%s%s/%s' % (parsed[0], parsed[1], parsed[2],
                                     self.resource_id)
        elif key == self.ROOT_URL:
            return '%s://%s%s' % (parsed[0], parsed[1], parsed[2])
        elif self.resource_id and key in (
                self.OBJECT_COUNT, self.BYTES_USED, self.HEAD_CONTAINER):
            try:
                headers = self.client().head_container(self.resource_id)
            except Exception as ex:
                if self.client_plugin().is_client_exception(ex):
                    LOG.warn(_LW("Head container failed: %s"), ex)
                    return None
                raise
            else:
                if key == self.OBJECT_COUNT:
                    return headers['x-container-object-count']
                elif key == self.BYTES_USED:
                    return headers['x-container-bytes-used']
                elif key == self.HEAD_CONTAINER:
                    return headers

    def _show_resource(self):
        return self.client().head_container(self.resource_id)


def resource_mapping():
    return {
        'OS::Swift::Container': SwiftContainer,
    }
