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

from oslo_serialization import jsonutils
import six
import sqlalchemy
from sqlalchemy.orm import sessionmaker


def upgrade(migrate_engine):
    Session = sessionmaker(bind=migrate_engine)
    session = Session()

    meta = sqlalchemy.MetaData(bind=migrate_engine)

    templ_table = sqlalchemy.Table('raw_template', meta, autoload=True)
    raw_templates = templ_table.select().execute()

    CFN_TO_HOT_RESOURCE_ATTRS = {'Type': 'type',
                                 'Properties': 'properties',
                                 'Metadata': 'metadata',
                                 'DependsOn': 'depends_on',
                                 'DeletionPolicy': 'deletion_policy',
                                 'UpdatePolicy': 'update_policy'}

    CFN_TO_HOT_OUTPUT_ATTRS = {'Description': 'description',
                               'Value': 'value'}

    def _translate(section, translate_map):
        changed = False

        for name, details in six.iteritems(section):
            for old_key, new_key in six.iteritems(translate_map):
                if old_key in details:
                    details[new_key] = details[old_key]
                    del details[old_key]
                    changed = True

        return changed

    for raw_template in raw_templates:
        template = jsonutils.loads(raw_template.template)
        if 'heat_template_version' in template:

            changed = False

            resources = template.get('resources', {})
            if _translate(resources, CFN_TO_HOT_RESOURCE_ATTRS):
                changed = True

            outputs = template.get('outputs', {})
            if _translate(outputs, CFN_TO_HOT_OUTPUT_ATTRS):
                changed = True

            if changed:
                (templ_table.update().
                    where(templ_table.c.id == raw_template.id).
                    values(template=jsonutils.dumps(template)).
                    execute())
                session.commit()
    session.close()
