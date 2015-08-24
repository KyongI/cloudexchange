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

from requests import exceptions
import six

from heat.common import exception
from heat.common.i18n import _
from heat.common import template_format
from heat.common import urlfetch
from heat.engine import attributes
from heat.engine import properties
from heat.engine.resources import stack_resource


class NestedStack(stack_resource.StackResource):
    '''
    A Resource representing a child stack to allow composition of templates.
    '''

    PROPERTIES = (
        TEMPLATE_URL, TIMEOUT_IN_MINS, PARAMETERS,
    ) = (
        'TemplateURL', 'TimeoutInMinutes', 'Parameters',
    )

    properties_schema = {
        TEMPLATE_URL: properties.Schema(
            properties.Schema.STRING,
            _('The URL of a template that specifies the stack to be created '
              'as a resource.'),
            required=True,
            update_allowed=True
        ),
        TIMEOUT_IN_MINS: properties.Schema(
            properties.Schema.INTEGER,
            _('The length of time, in minutes, to wait for the nested stack '
              'creation.'),
            update_allowed=True
        ),
        PARAMETERS: properties.Schema(
            properties.Schema.MAP,
            _('The set of parameters passed to this nested stack.'),
            update_allowed=True
        ),
    }

    def child_template(self):
        try:
            template_data = urlfetch.get(self.properties[self.TEMPLATE_URL])
        except (exceptions.RequestException, IOError) as r_exc:
            raise ValueError(_("Could not fetch remote template '%(url)s': "
                             "%(exc)s") %
                             {'url': self.properties[self.TEMPLATE_URL],
                              'exc': r_exc})

        return template_format.parse(template_data)

    def child_params(self):
        return self.properties[self.PARAMETERS]

    def handle_adopt(self, resource_data=None):
        return self._create_with_template(resource_adopt_data=resource_data)

    def handle_create(self):
        return self._create_with_template()

    def _create_with_template(self, resource_adopt_data=None):
        template = self.child_template()
        return self.create_with_template(template,
                                         self.child_params(),
                                         self.properties[self.TIMEOUT_IN_MINS],
                                         adopt_data=resource_adopt_data)

    def FnGetAtt(self, key, *path):
        if key and not key.startswith('Outputs.'):
            raise exception.InvalidTemplateAttribute(resource=self.name,
                                                     key=key)
        attribute = self.get_output(key.partition('.')[-1])
        return attributes.select_from_attribute(attribute, path)

    def FnGetRefId(self):
        if self.nested() is None:
            return six.text_type(self.name)

        return self.nested().identifier().arn()

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        # Nested stack template may be changed even if the prop_diff is empty.
        self.properties = json_snippet.properties(self.properties_schema,
                                                  self.context)

        try:
            template_data = urlfetch.get(self.properties[self.TEMPLATE_URL])
        except (exceptions.RequestException, IOError) as r_exc:
            raise ValueError(_("Could not fetch remote template '%(url)s': "
                             "%(exc)s") %
                             {'url': self.properties[self.TEMPLATE_URL],
                              'exc': r_exc})

        template = template_format.parse(template_data)

        return self.update_with_template(template,
                                         self.properties[self.PARAMETERS],
                                         self.properties[self.TIMEOUT_IN_MINS])


def resource_mapping():
    return {
        'AWS::CloudFormation::Stack': NestedStack,
    }
