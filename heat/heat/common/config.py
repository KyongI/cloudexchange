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

"""
Routines for configuring Heat
"""
import logging as sys_logging
import os

from eventlet.green import socket
from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_log import log as logging

from heat.common import exception
from heat.common.i18n import _
from heat.common.i18n import _LW
from heat.common import wsgi


LOG = logging.getLogger(__name__)
paste_deploy_group = cfg.OptGroup('paste_deploy')
paste_deploy_opts = [
    cfg.StrOpt('flavor',
               help=_("The flavor to use.")),
    cfg.StrOpt('api_paste_config', default="api-paste.ini",
               help=_("The API paste config file to use."))]


service_opts = [
    cfg.IntOpt('periodic_interval',
               default=60,
               help=_('Seconds between running periodic tasks.')),
    cfg.StrOpt('heat_metadata_server_url',
               default="",
               help=_('URL of the Heat metadata server.')),
    cfg.StrOpt('heat_waitcondition_server_url',
               help=_('URL of the Heat waitcondition server.')),
    cfg.StrOpt('heat_watch_server_url',
               default="",
               help=_('URL of the Heat CloudWatch server.')),
    cfg.StrOpt('instance_connection_is_secure',
               default="0",
               help=_('Instance connection to CFN/CW API via https.')),
    cfg.StrOpt('instance_connection_https_validate_certificates',
               default="1",
               help=_('Instance connection to CFN/CW API validate certs if '
                      'SSL is used.')),
    cfg.StrOpt('region_name_for_services',
               help=_('Default region name used to get services endpoints.')),
    cfg.StrOpt('heat_stack_user_role',
               default="heat_stack_user",
               help=_('Keystone role for heat template-defined users.')),
    cfg.StrOpt('stack_user_domain_id',
               deprecated_opts=[cfg.DeprecatedOpt('stack_user_domain',
                                                  group=None)],
               help=_('Keystone domain ID which contains heat '
                      'template-defined users. If this option is set, '
                      'stack_user_domain_name option will be ignored.')),
    cfg.StrOpt('stack_user_domain_name',
               help=_('Keystone domain name which contains heat '
                      'template-defined users. If `stack_user_domain_id` '
                      'option is set, this option is ignored.')),
    cfg.StrOpt('stack_domain_admin',
               help=_('Keystone username, a user with roles sufficient to '
                      'manage users and projects in the stack_user_domain.')),
    cfg.StrOpt('stack_domain_admin_password',
               secret=True,
               help=_('Keystone password for stack_domain_admin user.')),
    cfg.IntOpt('max_template_size',
               default=524288,
               help=_('Maximum raw byte size of any template.')),
    cfg.IntOpt('max_nested_stack_depth',
               default=5,
               help=_('Maximum depth allowed when using nested stacks.')),
    cfg.IntOpt('num_engine_workers',
               default=processutils.get_worker_count(),
               help=_('Number of heat-engine processes to fork and run.'))]

engine_opts = [
    cfg.ListOpt('plugin_dirs',
                default=['/usr/lib64/heat', '/usr/lib/heat',
                         '/usr/local/lib/heat', '/usr/local/lib64/heat'],
                help=_('List of directories to search for plug-ins.')),
    cfg.StrOpt('environment_dir',
               default='/etc/heat/environment.d',
               help=_('The directory to search for environment files.')),
    cfg.StrOpt('deferred_auth_method',
               choices=['password', 'trusts'],
               default='trusts',
               help=_('Select deferred auth method, '
                      'stored password or trusts.')),
    cfg.ListOpt('trusts_delegated_roles',
                default=[],
                help=_('Subset of trustor roles to be delegated to heat.'
                       ' If left unset, all roles of a user will be'
                       ' delegated to heat when creating a stack.')),
    cfg.IntOpt('max_resources_per_stack',
               default=1000,
               help=_('Maximum resources allowed per top-level stack. '
                      '-1 stands for unlimited.')),
    cfg.IntOpt('max_stacks_per_tenant',
               default=100,
               help=_('Maximum number of stacks any one tenant may have'
                      ' active at one time.')),
    cfg.IntOpt('action_retry_limit',
               default=5,
               help=_('Number of times to retry to bring a '
                      'resource to a non-error state. Set to 0 to disable '
                      'retries.')),
    cfg.IntOpt('event_purge_batch_size',
               default=10,
               help=_("Controls how many events will be pruned whenever a "
                      "stack's events exceed max_events_per_stack. Set this "
                      "lower to keep more events at the expense of more "
                      "frequent purges.")),
    cfg.IntOpt('max_events_per_stack',
               default=1000,
               help=_('Maximum events that will be available per stack. Older'
                      ' events will be deleted when this is reached. Set to 0'
                      ' for unlimited events per stack.')),
    cfg.IntOpt('stack_action_timeout',
               default=3600,
               help=_('Timeout in seconds for stack action (ie. create or'
                      ' update).')),
    cfg.IntOpt('error_wait_time',
               default=240,
               help=_('Error wait time in seconds for stack action (ie. create'
                      ' or update).')),
    cfg.IntOpt('engine_life_check_timeout',
               default=2,
               help=_('RPC timeout for the engine liveness check that is used'
                      ' for stack locking.')),
    cfg.BoolOpt('enable_cloud_watch_lite',
                default=False,
                help=_('Enable the legacy OS::Heat::CWLiteAlarm resource.')),
    cfg.BoolOpt('enable_stack_abandon',
                default=False,
                help=_('Enable the preview Stack Abandon feature.')),
    cfg.BoolOpt('enable_stack_adopt',
                default=False,
                help=_('Enable the preview Stack Adopt feature.')),
    cfg.BoolOpt('convergence_engine',
                default=False,
                help=_('Enables engine with convergence architecture. All '
                       'stacks with this option will be created using '
                       'convergence engine .')),
    cfg.StrOpt('default_software_config_transport',
               choices=['POLL_SERVER_CFN',
                        'POLL_SERVER_HEAT',
                        'POLL_TEMP_URL'],
               default='POLL_SERVER_CFN',
               help=_('Template default for how the server should receive the '
                      'metadata required for software configuration. '
                      'POLL_SERVER_CFN will allow calls to the cfn API action '
                      'DescribeStackResource authenticated with the provided '
                      'keypair (requires enabled heat-api-cfn). '
                      'POLL_SERVER_HEAT will allow calls to the '
                      'Heat API resource-show using the provided keystone '
                      'credentials (requires keystone v3 API, and configured '
                      'stack_user_* config options). '
                      'POLL_TEMP_URL will create and populate a '
                      'Swift TempURL with metadata for polling (requires '
                      'object-store endpoint which supports TempURL).')),
    cfg.StrOpt('default_deployment_signal_transport',
               choices=['CFN_SIGNAL',
                        'TEMP_URL_SIGNAL',
                        'HEAT_SIGNAL'],
               default='CFN_SIGNAL',
               help=_('Template default for how the server should signal to '
                      'heat with the deployment output values. CFN_SIGNAL '
                      'will allow an HTTP POST to a CFN keypair signed URL '
                      '(requires enabled heat-api-cfn). '
                      'TEMP_URL_SIGNAL will create a Swift TempURL to be '
                      'signaled via HTTP PUT (requires object-store endpoint '
                      'which supports TempURL). '
                      'HEAT_SIGNAL will allow calls to the Heat API '
                      'resource-signal using the provided keystone '
                      'credentials')),
    cfg.ListOpt('hidden_stack_tags',
                default=[],
                help=_('Stacks containing these tag names will be hidden. '
                       'Multiple tags should be given in a comma-delimited '
                       'list (eg. hidden_stack_tags=hide_me,me_too).')),
    cfg.StrOpt('onready',
               help=_('Deprecated.')),
    cfg.BoolOpt('stack_scheduler_hints',
                default=False,
                help=_('When this feature is enabled, scheduler hints'
                       ' identifying the heat stack context of a server'
                       ' resource are passed to the configured schedulers in'
                       ' nova, for server creates done using heat resource'
                       ' types OS::Nova::Server and AWS::EC2::Instance.'
                       ' heat_root_stack_id will be set to the id of the root'
                       ' stack of the resource, heat_stack_id will be set to'
                       ' the id of the resource\'s parent stack,'
                       ' heat_stack_name will be set to the name of the'
                       ' resource\'s parent stack, heat_path_in_stack will be'
                       ' set to a list of tuples,'
                       ' (stackresourcename, stackname) with list[0] being'
                       ' (None, rootstackname), and heat_resource_name will'
                       ' be set to the resource\'s name.')),
    cfg.BoolOpt('encrypt_parameters_and_properties',
                default=False,
                help=_('Encrypt template parameters that were marked as'
                       ' hidden and also all the resource properties before'
                       ' storing them in database.'))]

rpc_opts = [
    cfg.StrOpt('host',
               default=socket.gethostname(),
               help=_('Name of the engine node. '
                      'This can be an opaque identifier. '
                      'It is not necessarily a hostname, FQDN, '
                      'or IP address.'))]

profiler_group = cfg.OptGroup('profiler')
profiler_opts = [
    cfg.BoolOpt("profiler_enabled", default=False,
                help=_('If False fully disable profiling feature.')),
    cfg.BoolOpt("trace_sqlalchemy", default=False,
                help=_("If False do not trace SQL requests."))
]

auth_password_group = cfg.OptGroup('auth_password')
auth_password_opts = [
    cfg.BoolOpt('multi_cloud',
                default=False,
                help=_('Allow orchestration of multiple clouds.')),
    cfg.ListOpt('allowed_auth_uris',
                default=[],
                help=_('Allowed keystone endpoints for auth_uri when '
                       'multi_cloud is enabled. At least one endpoint needs '
                       'to be specified.'))]

# these options define baseline defaults that apply to all clients
default_clients_opts = [
    cfg.StrOpt('endpoint_type',
               default='publicURL',
               help=_(
                   'Type of endpoint in Identity service catalog to use '
                   'for communication with the OpenStack service.')),
    cfg.StrOpt('ca_file',
               help=_('Optional CA cert file to use in SSL connections.')),
    cfg.StrOpt('cert_file',
               help=_('Optional PEM-formatted certificate chain file.')),
    cfg.StrOpt('key_file',
               help=_('Optional PEM-formatted file that contains the '
                      'private key.')),
    cfg.BoolOpt('insecure',
                default=False,
                help=_("If set, then the server's certificate will not "
                       "be verified."))]

# these options can be defined for each client
# they must not specify defaults, since any options not defined in a client
# specific group is looked up on the generic group above
clients_opts = [
    cfg.StrOpt('endpoint_type',
               help=_(
                   'Type of endpoint in Identity service catalog to use '
                   'for communication with the OpenStack service.')),
    cfg.StrOpt('ca_file',
               help=_('Optional CA cert file to use in SSL connections.')),
    cfg.StrOpt('cert_file',
               help=_('Optional PEM-formatted certificate chain file.')),
    cfg.StrOpt('key_file',
               help=_('Optional PEM-formatted file that contains the '
                      'private key.')),
    cfg.BoolOpt('insecure',
                help=_("If set, then the server's certificate will not "
                       "be verified."))]

heat_client_opts = [
    cfg.StrOpt('url',
               default='',
               help=_('Optional heat url in format like'
                      ' http://0.0.0.0:8004/v1/%(tenant_id)s.'))]

keystone_client_opts = [
    cfg.StrOpt('auth_uri',
               default='',
               help=_('Unversioned keystone url in format like'
                      ' http://0.0.0.0:5000.'))]

client_http_log_debug_opts = [
    cfg.BoolOpt('http_log_debug',
                default=False,
                help=_("Allow client's debug log output."))]

revision_group = cfg.OptGroup('revision')
revision_opts = [
    cfg.StrOpt('heat_revision',
               default='unknown',
               help=_('Heat build revision. '
                      'If you would prefer to manage your build revision '
                      'separately, you can move this section to a different '
                      'file and add it as another config option.'))]


def startup_sanity_check():
    if (not cfg.CONF.stack_user_domain_id and
            not cfg.CONF.stack_user_domain_name):
        # FIXME(shardy): Legacy fallback for folks using old heat.conf
        # files which lack domain configuration
        LOG.warn(_LW('stack_user_domain_id or stack_user_domain_name not '
                     'set in heat.conf falling back to using default'))
    else:
        domain_admin_user = cfg.CONF.stack_domain_admin
        domain_admin_password = cfg.CONF.stack_domain_admin_password
        if not (domain_admin_user and domain_admin_password):
            raise exception.Error(_('heat.conf misconfigured, cannot '
                                    'specify "stack_user_domain_id" or '
                                    '"stack_user_domain_name" without '
                                    '"stack_domain_admin" and '
                                    '"stack_domain_admin_password"'))
    auth_key_len = len(cfg.CONF.auth_encryption_key)
    if auth_key_len in (16, 24):
        LOG.warn(
            _LW('Please update auth_encryption_key to be 32 characters.'))
    elif auth_key_len != 32:
        raise exception.Error(_('heat.conf misconfigured, auth_encryption_key '
                                'must be 32 characters'))


def list_opts():
    yield None, rpc_opts
    yield None, engine_opts
    yield None, service_opts
    yield paste_deploy_group.name, paste_deploy_opts
    yield auth_password_group.name, auth_password_opts
    yield revision_group.name, revision_opts
    yield profiler_group.name, profiler_opts
    yield 'clients', default_clients_opts

    for client in ('nova', 'swift', 'neutron', 'cinder',
                   'ceilometer', 'keystone', 'heat', 'glance', 'trove',
                   'sahara'):
        client_specific_group = 'clients_' + client
        yield client_specific_group, clients_opts

    yield 'clients_heat', heat_client_opts
    yield 'clients_keystone', keystone_client_opts
    yield 'clients_nova', client_http_log_debug_opts
    yield 'clients_cinder', client_http_log_debug_opts


cfg.CONF.register_group(paste_deploy_group)
cfg.CONF.register_group(auth_password_group)
cfg.CONF.register_group(revision_group)
cfg.CONF.register_group(profiler_group)

for group, opts in list_opts():
    cfg.CONF.register_opts(opts, group=group)


def _get_deployment_flavor():
    """
    Retrieve the paste_deploy.flavor config item, formatted appropriately
    for appending to the application name.
    """
    flavor = cfg.CONF.paste_deploy.flavor
    return '' if not flavor else ('-' + flavor)


def _get_deployment_config_file():
    """
    Retrieve the deployment_config_file config item, formatted as an
    absolute pathname.
    """
    config_path = cfg.CONF.find_file(
        cfg.CONF.paste_deploy['api_paste_config'])
    if config_path is None:
        return None

    return os.path.abspath(config_path)


def load_paste_app(app_name=None):
    """
    Builds and returns a WSGI app from a paste config file.

    We assume the last config file specified in the supplied ConfigOpts
    object is the paste config file.

    :param app_name: name of the application to load

    :raises RuntimeError when config file cannot be located or application
            cannot be loaded from config file
    """
    if app_name is None:
        app_name = cfg.CONF.prog

    # append the deployment flavor to the application name,
    # in order to identify the appropriate paste pipeline
    app_name += _get_deployment_flavor()

    conf_file = _get_deployment_config_file()
    if conf_file is None:
        raise RuntimeError(_("Unable to locate config file"))

    try:
        app = wsgi.paste_deploy_app(conf_file, app_name, cfg.CONF)

        # Log the options used when starting if we're in debug mode...
        if cfg.CONF.debug:
            cfg.CONF.log_opt_values(logging.getLogger(app_name),
                                    sys_logging.DEBUG)

        return app
    except (LookupError, ImportError) as e:
        raise RuntimeError(_("Unable to load %(app_name)s from "
                             "configuration file %(conf_file)s."
                             "\nGot: %(e)r") % {'app_name': app_name,
                                                'conf_file': conf_file,
                                                'e': e})
