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

import os

from oslo_config import cfg

import heat_integrationtests


IntegrationTestGroup = [

    cfg.StrOpt('username',
               default=os.environ.get('OS_USERNAME'),
               help="Username to use for API requests."),
    cfg.StrOpt('password',
               default=os.environ.get('OS_PASSWORD'),
               help="API key to use when authenticating.",
               secret=True),
    cfg.StrOpt('tenant_name',
               default=(os.environ.get('OS_PROJECT_NAME') or
                        os.environ.get('OS_TENANT_NAME')),
               help="Tenant name to use for API requests."),
    cfg.StrOpt('auth_url',
               default=os.environ.get('OS_AUTH_URL'),
               help="Full URI of the OpenStack Identity API (Keystone), v2"),
    cfg.StrOpt('region',
               default=os.environ.get('OS_REGION_NAME'),
               help="The region name to us"),
    cfg.StrOpt('instance_type',
               help="Instance type for tests. Needs to be big enough for a "
                    "full OS plus the test workload"),
    cfg.StrOpt('minimal_instance_type',
               help="Instance type enough for simplest cases."),
    cfg.StrOpt('image_ref',
               help="Name of image to use for tests which boot servers."),
    cfg.StrOpt('keypair_name',
               default=None,
               help="Name of existing keypair to launch servers with."),
    cfg.StrOpt('minimal_image_ref',
               help="Name of minimal (e.g cirros) image to use when "
                    "launching test instances."),
    cfg.StrOpt('auth_version',
               default='v2',
               help="Identity API version to be used for authentication "
                    "for API tests."),
    cfg.BoolOpt('disable_ssl_certificate_validation',
                default=False,
                help="Set to True if using self-signed SSL certificates."),
    cfg.IntOpt('build_interval',
               default=4,
               help="Time in seconds between build status checks."),
    cfg.IntOpt('build_timeout',
               default=1200,
               help="Timeout in seconds to wait for a stack to build."),
    cfg.StrOpt('network_for_ssh',
               default='heat-net',
               help="Network used for SSH connections."),
    cfg.StrOpt('fixed_network_name',
               default='heat-net',
               help="Visible fixed network name "),
    cfg.StrOpt('floating_network_name',
               default='public',
               help="Visible floating network name "),
    cfg.StrOpt('boot_config_env',
               default=('heat_integrationtests/scenario/templates'
                        '/boot_config_none_env.yaml'),
               help="Path to environment file which defines the "
                    "resource type Heat::InstallConfigAgent. Needs to "
                    "be appropriate for the image_ref."),
    cfg.StrOpt('fixed_subnet_name',
               default='heat-subnet',
               help="Visible fixed sub-network name "),
    cfg.IntOpt('ssh_timeout',
               default=300,
               help="Timeout in seconds to wait for authentication to "
                    "succeed."),
    cfg.IntOpt('ip_version_for_ssh',
               default=4,
               help="IP version used for SSH connections."),
    cfg.IntOpt('ssh_channel_timeout',
               default=60,
               help="Timeout in seconds to wait for output from ssh "
                    "channel."),
    cfg.IntOpt('tenant_network_mask_bits',
               default=28,
               help="The mask bits for tenant ipv4 subnets"),
    cfg.BoolOpt('skip_scenario_tests',
                default=False,
                help="Skip all scenario tests"),
    cfg.BoolOpt('skip_functional_tests',
                default=False,
                help="Skip all functional tests"),
    cfg.ListOpt('skip_functional_test_list',
                help="List of functional test class or class.method "
                     "names to skip ex. AutoscalingGroupTest,"
                     "InstanceGroupBasicTest.test_size_updates_work"),
    cfg.ListOpt('skip_scenario_test_list',
                help="List of scenario test class or class.method "
                     "names to skip ex. NeutronLoadBalancerTest, "
                     "CeilometerAlarmTest.test_alarm"),
    cfg.ListOpt('skip_test_stack_action_list',
                help="List of stack actions in tests to skip "
                     "ex. ABANDON, ADOPT, SUSPEND, RESUME"),
    cfg.IntOpt('volume_size',
               default=1,
               help='Default size in GB for volumes created by volumes tests'),
    cfg.IntOpt('connectivity_timeout',
               default=120,
               help="Timeout in seconds to wait for connectivity to "
                    "server."),
    cfg.IntOpt('sighup_timeout',
               default=30,
               help="Timeout in seconds to wait for adding or removing child"
                    "process after receiving of sighup signal")
]


def init_conf(read_conf=True):

    default_config_files = None
    if read_conf:
        confpath = os.path.join(
            os.path.dirname(os.path.realpath(heat_integrationtests.__file__)),
            'heat_integrationtests.conf')
        if os.path.isfile(confpath):
            default_config_files = [confpath]

    conf = cfg.ConfigOpts()
    conf(args=[], project='heat_integrationtests',
         default_config_files=default_config_files)

    for opt in IntegrationTestGroup:
        conf.register_opt(opt)
    return conf


def list_opts():
    yield None, IntegrationTestGroup
