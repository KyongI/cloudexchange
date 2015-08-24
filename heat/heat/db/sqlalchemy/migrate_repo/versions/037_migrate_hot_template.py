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

from oslo_serialization import jsonutils
import six
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from heat.engine.hot import parameters


def upgrade(migrate_engine):
    Session = sessionmaker(bind=migrate_engine)
    session = Session()

    meta = sqlalchemy.MetaData(bind=migrate_engine)

    templ_table = sqlalchemy.Table('raw_template', meta, autoload=True)
    raw_templates = templ_table.select().execute()

    for raw_template in raw_templates:
        template = jsonutils.loads(raw_template.template)
        if ('heat_template_version' in template
                and 'parameters' in template):

            for parameter, schema in six.iteritems(template['parameters']):
                changed = False

                def _commit_schema(parameter, schema):
                    template['parameters'][parameter] = schema
                    (templ_table.update().
                        where(templ_table.c.id == raw_template.id).
                        values(template=jsonutils.dumps(template)).
                        execute())
                    session.commit()

                if 'Type' in schema:
                    schema['type'] = schema['Type']
                    del schema['Type']
                    changed = True

                if (schema.get('type') not in parameters.HOTParamSchema.TYPES
                        and schema['type'].istitle()):
                    schema['type'] = schema['type'].lower()
                    changed = True

                if changed:
                    _commit_schema(parameter, schema)
    session.close()
