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
StackLock object
"""

from oslo_versionedobjects import base
from oslo_versionedobjects import fields

from heat.db import api as db_api


class StackLock(base.VersionedObject,
                base.VersionedObjectDictCompat,
                base.ComparableVersionedObject):
    fields = {
        'engine_id': fields.StringField(nullable=True),
        'stack_id': fields.StringField(),
        'created_at': fields.DateTimeField(read_only=True),
        'updated_at': fields.DateTimeField(nullable=True),
    }

    @classmethod
    def create(cls, stack_id, engine_id):
        return db_api.stack_lock_create(stack_id, engine_id)

    @classmethod
    def steal(cls, stack_id, old_engine_id, new_engine_id):
        return db_api.stack_lock_steal(stack_id,
                                       old_engine_id,
                                       new_engine_id)

    @classmethod
    def release(cls, stack_id, engine_id):
        return db_api.stack_lock_release(stack_id, engine_id)

    @classmethod
    def get_engine_id(cls, stack_id):
        return db_api.stack_lock_get_engine_id(stack_id)
