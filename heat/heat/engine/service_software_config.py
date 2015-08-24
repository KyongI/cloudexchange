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

from oslo_db import api as oslo_db_api
from oslo_db import exception as db_exc
from oslo_log import log as logging
from oslo_serialization import jsonutils
from oslo_service import service
from oslo_utils import timeutils
import requests
import six
from six.moves.urllib import parse as urlparse

from heat.common import exception
from heat.common.i18n import _
from heat.common.i18n import _LI
from heat.db import api as db_api
from heat.engine import api
from heat.objects import software_config as software_config_object
from heat.objects import software_deployment as software_deployment_object
from heat.rpc import api as rpc_api

LOG = logging.getLogger(__name__)


class SoftwareConfigService(service.Service):

    def show_software_config(self, cnxt, config_id):
        sc = software_config_object.SoftwareConfig.get_by_id(cnxt, config_id)
        return api.format_software_config(sc)

    def list_software_configs(self, cnxt, limit=None, marker=None,
                              tenant_safe=True):
        scs = software_config_object.SoftwareConfig.get_all(
            cnxt,
            limit=limit,
            marker=marker,
            tenant_safe=tenant_safe)
        result = [api.format_software_config(sc, detail=False) for sc in scs]
        return result

    def create_software_config(self, cnxt, group, name, config,
                               inputs, outputs, options):

        sc = software_config_object.SoftwareConfig.create(cnxt, {
            'group': group,
            'name': name,
            'config': {
                'inputs': inputs,
                'outputs': outputs,
                'options': options,
                'config': config
            },
            'tenant': cnxt.tenant_id})
        return api.format_software_config(sc)

    def delete_software_config(self, cnxt, config_id):
        software_config_object.SoftwareConfig.delete(cnxt, config_id)

    def list_software_deployments(self, cnxt, server_id):
        all_sd = software_deployment_object.SoftwareDeployment.get_all(
            cnxt, server_id)
        result = [api.format_software_deployment(sd) for sd in all_sd]
        return result

    def metadata_software_deployments(self, cnxt, server_id):
        if not server_id:
            raise ValueError(_('server_id must be specified'))
        all_sd = software_deployment_object.SoftwareDeployment.get_all(
            cnxt, server_id)
        # sort the configs by config name, to give the list of metadata a
        # deterministic and controllable order.
        all_sd_s = sorted(all_sd, key=lambda sd: sd.config.name)
        result = [api.format_software_config(sd.config) for sd in all_sd_s]
        return result

    @oslo_db_api.wrap_db_retry(max_retries=10, retry_on_request=True)
    def _push_metadata_software_deployments(self, cnxt, server_id, sd):
        rs = db_api.resource_get_by_physical_resource_id(cnxt, server_id)
        if not rs:
            return
        deployments = self.metadata_software_deployments(cnxt, server_id)
        md = rs.rsrc_metadata or {}
        md['deployments'] = deployments
        rows_updated = db_api.resource_update(
            cnxt, rs.id, {'rsrc_metadata': md}, rs.atomic_key)
        if not rows_updated:
            raise db_exc.RetryRequest(
                exception.DeploymentConcurrentTransaction(server=server_id))

        metadata_put_url = None
        metadata_queue_id = None
        for rd in rs.data:
            if rd.key == 'metadata_put_url':
                metadata_put_url = rd.value
                break
            elif rd.key == 'metadata_queue_id':
                metadata_queue_id = rd.value
                break
        if metadata_put_url:
            json_md = jsonutils.dumps(md)
            requests.put(metadata_put_url, json_md)
        elif metadata_queue_id:
            zaqar_plugin = cnxt.clients.client_plugin('zaqar')
            zaqar = zaqar_plugin.create_for_tenant(sd.stack_user_project_id)
            queue = zaqar.queue(metadata_queue_id)
            queue.post({'body': md, 'ttl': zaqar_plugin.DEFAULT_TTL})

    def _refresh_swift_software_deployment(self, cnxt, sd, deploy_signal_id):
        container, object_name = urlparse.urlparse(
            deploy_signal_id).path.split('/')[-2:]
        swift_plugin = cnxt.clients.client_plugin('swift')
        swift = swift_plugin.client()

        try:
            headers = swift.head_object(container, object_name)
        except Exception as ex:
            # ignore not-found, in case swift is not consistent yet
            if swift_plugin.is_not_found(ex):
                LOG.info(_LI('Signal object not found: %(c)s %(o)s'), {
                    'c': container, 'o': object_name})
                return sd
            raise ex

        lm = headers.get('last-modified')

        last_modified = swift_plugin.parse_last_modified(lm)
        prev_last_modified = sd.updated_at

        if prev_last_modified:
            # assume stored as utc, convert to offset-naive datetime
            prev_last_modified = prev_last_modified.replace(tzinfo=None)

        if prev_last_modified and (last_modified <= prev_last_modified):
            return sd

        try:
            (headers, obj) = swift.get_object(container, object_name)
        except Exception as ex:
            # ignore not-found, in case swift is not consistent yet
            if swift_plugin.is_not_found(ex):
                LOG.info(_LI(
                    'Signal object not found: %(c)s %(o)s'), {
                        'c': container, 'o': object_name})
                return sd
            raise ex
        if obj:
            self.signal_software_deployment(
                cnxt, sd.id, jsonutils.loads(obj),
                last_modified.isoformat())

        return software_deployment_object.SoftwareDeployment.get_by_id(
            cnxt, sd.id)

    def _refresh_zaqar_software_deployment(self, cnxt, sd, deploy_queue_id):
        zaqar_plugin = cnxt.clients.client_plugin('zaqar')
        zaqar = zaqar_plugin.create_for_tenant(sd.stack_user_project_id)
        queue = zaqar.queue(deploy_queue_id)

        messages = list(queue.pop())
        if messages:
            self.signal_software_deployment(
                cnxt, sd.id, messages[0].body, None)

        return software_deployment_object.SoftwareDeployment.get_by_id(
            cnxt, sd.id)

    def show_software_deployment(self, cnxt, deployment_id):
        sd = software_deployment_object.SoftwareDeployment.get_by_id(
            cnxt, deployment_id)
        if sd.status == rpc_api.SOFTWARE_DEPLOYMENT_IN_PROGRESS:
            c = sd.config.config
            input_values = dict((i['name'], i['value']) for i in c['inputs'])
            transport = input_values.get('deploy_signal_transport')
            if transport == 'TEMP_URL_SIGNAL':
                sd = self._refresh_swift_software_deployment(
                    cnxt, sd, input_values.get('deploy_signal_id'))
            elif transport == 'ZAQAR_SIGNAL':
                sd = self._refresh_zaqar_software_deployment(
                    cnxt, sd, input_values.get('deploy_queue_id'))
        return api.format_software_deployment(sd)

    def create_software_deployment(self, cnxt, server_id, config_id,
                                   input_values, action, status,
                                   status_reason, stack_user_project_id):

        sd = software_deployment_object.SoftwareDeployment.create(cnxt, {
            'config_id': config_id,
            'server_id': server_id,
            'input_values': input_values,
            'tenant': cnxt.tenant_id,
            'stack_user_project_id': stack_user_project_id,
            'action': action,
            'status': status,
            'status_reason': status_reason})
        self._push_metadata_software_deployments(cnxt, server_id, sd)
        return api.format_software_deployment(sd)

    def signal_software_deployment(self, cnxt, deployment_id, details,
                                   updated_at):

        if not deployment_id:
            raise ValueError(_('deployment_id must be specified'))

        sd = software_deployment_object.SoftwareDeployment.get_by_id(
            cnxt, deployment_id)
        status = sd.status

        if not status == rpc_api.SOFTWARE_DEPLOYMENT_IN_PROGRESS:
            # output values are only expected when in an IN_PROGRESS state
            return

        details = details or {}

        output_status_code = rpc_api.SOFTWARE_DEPLOYMENT_OUTPUT_STATUS_CODE
        ov = sd.output_values or {}
        status = None
        status_reasons = {}
        status_code = details.get(output_status_code)
        if status_code and str(status_code) != '0':
            status = rpc_api.SOFTWARE_DEPLOYMENT_FAILED
            status_reasons[output_status_code] = _(
                'Deployment exited with non-zero status code: %s'
            ) % details.get(output_status_code)
            event_reason = 'deployment failed (%s)' % status_code
        else:
            event_reason = 'deployment succeeded'

        for output in sd.config.config['outputs'] or []:
            out_key = output['name']
            if out_key in details:
                ov[out_key] = details[out_key]
                if output.get('error_output', False):
                    status = rpc_api.SOFTWARE_DEPLOYMENT_FAILED
                    status_reasons[out_key] = details[out_key]
                    event_reason = 'deployment failed'

        for out_key in rpc_api.SOFTWARE_DEPLOYMENT_OUTPUTS:
            ov[out_key] = details.get(out_key)

        if status == rpc_api.SOFTWARE_DEPLOYMENT_FAILED:
            # build a status reason out of all of the values of outputs
            # flagged as error_output
            status_reasons = [' : '.join((k, six.text_type(status_reasons[k])))
                              for k in status_reasons]
            status_reason = ', '.join(status_reasons)
        else:
            status = rpc_api.SOFTWARE_DEPLOYMENT_COMPLETE
            status_reason = _('Outputs received')

        self.update_software_deployment(
            cnxt, deployment_id=deployment_id,
            output_values=ov, status=status, status_reason=status_reason,
            config_id=None, input_values=None, action=None,
            updated_at=updated_at)
        # Return a string describing the outcome of handling the signal data
        return event_reason

    def update_software_deployment(self, cnxt, deployment_id, config_id,
                                   input_values, output_values, action,
                                   status, status_reason, updated_at):
        update_data = {}
        if config_id:
            update_data['config_id'] = config_id
        if input_values:
            update_data['input_values'] = input_values
        if output_values:
            update_data['output_values'] = output_values
        if action:
            update_data['action'] = action
        if status:
            update_data['status'] = status
        if status_reason:
            update_data['status_reason'] = status_reason
        if updated_at:
            update_data['updated_at'] = timeutils.normalize_time(
                timeutils.parse_isotime(updated_at))
        else:
            update_data['updated_at'] = timeutils.utcnow()

        sd = software_deployment_object.SoftwareDeployment.update_by_id(
            cnxt, deployment_id, update_data)

        # only push metadata if this update resulted in the config_id
        # changing, since metadata is just a list of configs
        if config_id:
            self._push_metadata_software_deployments(cnxt, sd.server_id, sd)

        return api.format_software_deployment(sd)

    def delete_software_deployment(self, cnxt, deployment_id):
        software_deployment_object.SoftwareDeployment.delete(
            cnxt, deployment_id)
