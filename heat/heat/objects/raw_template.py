# Copyright 2014 Intel Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


"""
RawTemplate object
"""

import copy

from oslo_config import cfg
from oslo_versionedobjects import base
from oslo_versionedobjects import fields

from heat.common import crypt
from heat.common import environment_format as env_fmt
from heat.db import api as db_api
from heat.objects import fields as heat_fields


class RawTemplate(
    base.VersionedObject,
    base.VersionedObjectDictCompat,
    base.ComparableVersionedObject,
):
    fields = {
        'id': fields.StringField(),
        'files': heat_fields.JsonField(nullable=True),
        'template': heat_fields.JsonField(),
        'environment': heat_fields.JsonField(),
    }

    @staticmethod
    def _from_db_object(context, tpl, db_tpl):
        for field in tpl.fields:
            tpl[field] = db_tpl[field]

        tpl.environment = copy.deepcopy(tpl.environment)
        # If any of the parameters were encrypted, then decrypt them
        if (tpl.environment is not None and
                env_fmt.ENCRYPTED_PARAM_NAMES in tpl.environment):
            parameters = tpl.environment[env_fmt.PARAMETERS]
            encrypted_param_names = tpl.environment[
                env_fmt.ENCRYPTED_PARAM_NAMES]

            for param_name in encrypted_param_names:
                method, value = parameters[param_name]
                decrypted_val = crypt.decrypt(method, value)
                parameters[param_name] = decrypted_val
            tpl.environment[env_fmt.PARAMETERS] = parameters

        tpl._context = context
        tpl.obj_reset_changes()
        return tpl

    @classmethod
    def get_by_id(cls, context, template_id):
        raw_template_db = db_api.raw_template_get(context, template_id)
        return cls._from_db_object(context, cls(), raw_template_db)

    @classmethod
    def encrypt_hidden_parameters(cls, tmpl):
        if cfg.CONF.encrypt_parameters_and_properties:
            for param_name, param in tmpl.env.params.items():
                if not tmpl.param_schemata()[param_name].hidden:
                    continue
                clear_text_val = tmpl.env.params.get(param_name)
                tmpl.env.params[param_name] = crypt.encrypt(clear_text_val)
                tmpl.env.encrypted_param_names.append(param_name)

    @classmethod
    def create(cls, context, values):
        return cls._from_db_object(context, cls(),
                                   db_api.raw_template_create(context, values))

    @classmethod
    def update_by_id(cls, context, template_id, values):
        return cls._from_db_object(
            context, cls(),
            db_api.raw_template_update(context, template_id, values))

    @classmethod
    def delete(cls, context, template_id):
        db_api.raw_template_delete(context, template_id)
