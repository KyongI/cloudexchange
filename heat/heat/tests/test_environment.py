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

import os.path
import sys

import fixtures
import mock
from oslo_config import cfg
import six

from heat.common import environment_format
from heat.common import exception
from heat.engine import environment
from heat.engine import resources
from heat.engine.resources.aws.ec2 import instance
from heat.engine.resources.openstack.nova import server
from heat.tests import common
from heat.tests import generic_resource

cfg.CONF.import_opt('environment_dir', 'heat.common.config')


class EnvironmentTest(common.HeatTestCase):
    def setUp(self):
        super(EnvironmentTest, self).setUp()
        self.g_env = resources.global_env()

    def test_load_old_parameters(self):
        old = {u'a': u'ff', u'b': u'ss'}
        expected = {u'parameters': old,
                    u'encrypted_param_names': [],
                    u'parameter_defaults': {},
                    u'resource_registry': {u'resources': {}}}
        env = environment.Environment(old)
        self.assertEqual(expected, env.user_env_as_dict())

    def test_load_new_env(self):
        new_env = {u'parameters': {u'a': u'ff', u'b': u'ss'},
                   u'encrypted_param_names': [],
                   u'parameter_defaults': {u'ff': 'new_def'},
                   u'resource_registry': {u'OS::Food': u'fruity.yaml',
                                          u'resources': {}}}
        env = environment.Environment(new_env)
        self.assertEqual(new_env, env.user_env_as_dict())

    def test_global_registry(self):
        self.g_env.register_class('CloudX::Nova::Server',
                                  generic_resource.GenericResource)
        new_env = {u'parameters': {u'a': u'ff', u'b': u'ss'},
                   u'resource_registry': {u'OS::*': 'CloudX::*'}}
        env = environment.Environment(new_env)
        self.assertEqual('CloudX::Nova::Server',
                         env.get_resource_info('OS::Nova::Server',
                                               'my_db_server').name)

    def test_map_one_resource_type(self):
        new_env = {u'parameters': {u'a': u'ff', u'b': u'ss'},
                   u'resource_registry': {u'resources':
                                          {u'my_db_server':
                                           {u'OS::DBInstance': 'db.yaml'}}}}
        env = environment.Environment(new_env)

        info = env.get_resource_info('OS::DBInstance', 'my_db_server')
        self.assertEqual('db.yaml', info.value)

    def test_map_all_resources_of_type(self):
        self.g_env.register_class('OS::Nova::FloatingIP',
                                  generic_resource.GenericResource)

        new_env = {u'parameters': {u'a': u'ff', u'b': u'ss'},
                   u'resource_registry':
                   {u'OS::Networking::FloatingIP': 'OS::Nova::FloatingIP',
                    u'OS::Loadbalancer': 'lb.yaml'}}

        env = environment.Environment(new_env)
        self.assertEqual('OS::Nova::FloatingIP',
                         env.get_resource_info('OS::Networking::FloatingIP',
                                               'my_fip').name)

    def test_resource_sort_order_len(self):
        new_env = {u'resource_registry': {u'resources': {u'my_fip': {
            u'OS::Networking::FloatingIP': 'ip.yaml'}}},
            u'OS::Networking::FloatingIP': 'OS::Nova::FloatingIP'}

        env = environment.Environment(new_env)
        self.assertEqual('ip.yaml',
                         env.get_resource_info('OS::Networking::FloatingIP',
                                               'my_fip').value)

    def test_env_load(self):
        new_env = {u'resource_registry': {u'resources': {u'my_fip': {
            u'OS::Networking::FloatingIP': 'ip.yaml'}}}}

        env = environment.Environment()
        self.assertIsNone(env.get_resource_info('OS::Networking::FloatingIP',
                                                'my_fip'))

        env.load(new_env)
        self.assertEqual('ip.yaml',
                         env.get_resource_info('OS::Networking::FloatingIP',
                                               'my_fip').value)

    def test_register_with_path(self):
        yaml_env = '''
        resource_registry:
          test::one: a.yaml
          resources:
            res_x:
              test::two: b.yaml
'''

        env = environment.Environment(environment_format.parse(yaml_env))
        self.assertEqual('a.yaml', env.get_resource_info('test::one').value)
        self.assertEqual('b.yaml',
                         env.get_resource_info('test::two', 'res_x').value)

        env2 = environment.Environment()
        env2.register_class('test::one',
                            'a.yaml',
                            path=['test::one'])
        env2.register_class('test::two',
                            'b.yaml',
                            path=['resources', 'res_x', 'test::two'])

        self.assertEqual(env.user_env_as_dict(), env2.user_env_as_dict())

    def test_constraints(self):
        env = environment.Environment({})

        first_constraint = object()
        second_constraint = object()
        env.register_constraint("constraint1", first_constraint)
        env.register_constraint("constraint2", second_constraint)
        self.assertIs(first_constraint, env.get_constraint("constraint1"))
        self.assertIs(second_constraint, env.get_constraint("constraint2"))
        self.assertIs(None, env.get_constraint("no_constraint"))

    def test_constraints_registry(self):
        constraint_content = '''
class MyConstraint(object):
    pass

def constraint_mapping():
    return {"constraint1": MyConstraint}
        '''
        plugin_dir = self.useFixture(fixtures.TempDir())
        plugin_file = os.path.join(plugin_dir.path, 'test.py')
        with open(plugin_file, 'w+') as ef:
            ef.write(constraint_content)
        self.addCleanup(sys.modules.pop, "heat.engine.plugins.test")
        cfg.CONF.set_override('plugin_dirs', plugin_dir.path)

        env = environment.Environment({})
        resources._load_global_environment(env)

        self.assertEqual("MyConstraint",
                         env.get_constraint("constraint1").__name__)
        self.assertIs(None, env.get_constraint("no_constraint"))

    def test_constraints_registry_error(self):
        constraint_content = '''
def constraint_mapping():
    raise ValueError("oops")
        '''
        plugin_dir = self.useFixture(fixtures.TempDir())
        plugin_file = os.path.join(plugin_dir.path, 'test.py')
        with open(plugin_file, 'w+') as ef:
            ef.write(constraint_content)
        self.addCleanup(sys.modules.pop, "heat.engine.plugins.test")
        cfg.CONF.set_override('plugin_dirs', plugin_dir.path)

        env = environment.Environment({})
        error = self.assertRaises(ValueError,
                                  resources._load_global_environment, env)
        self.assertEqual("oops", six.text_type(error))

    def test_constraints_registry_stevedore(self):
        env = environment.Environment({})
        resources._load_global_environment(env)

        self.assertEqual("FlavorConstraint",
                         env.get_constraint("nova.flavor").__name__)
        self.assertIs(None, env.get_constraint("no_constraint"))


class EnvironmentDuplicateTest(common.HeatTestCase):

    scenarios = [
        ('same', dict(resource_type='test.yaml',
                      expected_equal=True)),
        ('diff_temp', dict(resource_type='not.yaml',
                           expected_equal=False)),
        ('diff_map', dict(resource_type='OS::SomethingElse',
                          expected_equal=False)),
        ('diff_path', dict(resource_type='a/test.yaml',
                           expected_equal=False)),
    ]

    def test_env_load(self):
        env_initial = {u'resource_registry': {
            u'OS::Test::Dummy': 'test.yaml'}}

        env = environment.Environment()
        env.load(env_initial)
        info = env.get_resource_info('OS::Test::Dummy', 'something')
        replace_log = 'Changing %s from %s to %s' % ('OS::Test::Dummy',
                                                     'test.yaml',
                                                     self.resource_type)
        self.assertNotIn(replace_log, self.LOG.output)
        env_test = {u'resource_registry': {
            u'OS::Test::Dummy': self.resource_type}}
        env.load(env_test)

        if self.expected_equal:
            # should return exactly the same object.
            self.assertIs(info, env.get_resource_info('OS::Test::Dummy',
                                                      'my_fip'))
            self.assertNotIn(replace_log, self.LOG.output)
        else:
            self.assertIn(replace_log, self.LOG.output)
            self.assertNotEqual(info,
                                env.get_resource_info('OS::Test::Dummy',
                                                      'my_fip'))

    def test_env_register_while_get_resource_info(self):
        env_test = {u'resource_registry': {
            u'OS::Test::Dummy': self.resource_type}}
        env = environment.Environment()
        env.load(env_test)
        env.get_resource_info('OS::Test::Dummy')
        self.assertEqual({'OS::Test::Dummy': self.resource_type,
                          'resources': {}},
                         env.user_env_as_dict().get(
                             environment_format.RESOURCE_REGISTRY))

        env_test = {u'resource_registry': {
            u'resources': {u'test': {u'OS::Test::Dummy': self.resource_type}}}}
        env.load(env_test)
        env.get_resource_info('OS::Test::Dummy')
        self.assertEqual({u'OS::Test::Dummy': self.resource_type,
                          'resources': {u'test': {u'OS::Test::Dummy':
                                                  self.resource_type}}},
                         env.user_env_as_dict().get(
                             environment_format.RESOURCE_REGISTRY))


class GlobalEnvLoadingTest(common.HeatTestCase):

    def test_happy_path(self):
        with mock.patch('glob.glob') as m_ldir:
            m_ldir.return_value = ['/etc_etc/heat/environment.d/a.yaml']
            env_dir = '/etc_etc/heat/environment.d'
            env_content = '{"resource_registry": {}}'

            env = environment.Environment({}, user_env=False)

            with mock.patch('heat.engine.environment.open',
                            mock.mock_open(read_data=env_content),
                            create=True) as m_open:
                environment.read_global_environment(env, env_dir)

        m_ldir.assert_called_once_with(env_dir + '/*')
        m_open.assert_called_once_with('%s/a.yaml' % env_dir)

    def test_empty_env_dir(self):
        with mock.patch('glob.glob') as m_ldir:
            m_ldir.return_value = []
            env_dir = '/etc_etc/heat/environment.d'

            env = environment.Environment({}, user_env=False)
            environment.read_global_environment(env, env_dir)

        m_ldir.assert_called_once_with(env_dir + '/*')

    def test_continue_on_ioerror(self):
        """assert we get all files processed even if there are
        processing exceptions.
        """
        with mock.patch('glob.glob') as m_ldir:
            m_ldir.return_value = ['/etc_etc/heat/environment.d/a.yaml',
                                   '/etc_etc/heat/environment.d/b.yaml']
            env_dir = '/etc_etc/heat/environment.d'
            env_content = '{}'

            env = environment.Environment({}, user_env=False)

            with mock.patch('heat.engine.environment.open',
                            mock.mock_open(read_data=env_content),
                            create=True) as m_open:
                m_open.side_effect = IOError
                environment.read_global_environment(env, env_dir)

        m_ldir.assert_called_once_with(env_dir + '/*')
        expected = [mock.call('%s/a.yaml' % env_dir),
                    mock.call('%s/b.yaml' % env_dir)]
        self.assertEqual(expected, m_open.call_args_list)

    def test_continue_on_parse_error(self):
        """assert we get all files processed even if there are
        processing exceptions.
        """
        with mock.patch('glob.glob') as m_ldir:
            m_ldir.return_value = ['/etc_etc/heat/environment.d/a.yaml',
                                   '/etc_etc/heat/environment.d/b.yaml']
            env_dir = '/etc_etc/heat/environment.d'
            env_content = '{@$%#$%'

            env = environment.Environment({}, user_env=False)

            with mock.patch('heat.engine.environment.open',
                            mock.mock_open(read_data=env_content),
                            create=True) as m_open:
                environment.read_global_environment(env, env_dir)

        m_ldir.assert_called_once_with(env_dir + '/*')
        expected = [mock.call('%s/a.yaml' % env_dir),
                    mock.call('%s/b.yaml' % env_dir)]
        self.assertEqual(expected, m_open.call_args_list)

    def test_env_resources_override_plugins(self):
        # assertion: any template resources in the global environment
        #            should override the default plugins.

        # 1. set our own global test env
        #    (with a template resource that shadows a plugin)
        g_env_content = '''
        resource_registry:
          "OS::Nova::Server": "file:///not_really_here.yaml"
        '''
        envdir = self.useFixture(fixtures.TempDir())
        #
        envfile = os.path.join(envdir.path, 'test.yaml')
        with open(envfile, 'w+') as ef:
            ef.write(g_env_content)
        cfg.CONF.set_override('environment_dir', envdir.path)

        # 2. load global env
        g_env = environment.Environment({}, user_env=False)
        resources._load_global_environment(g_env)

        # 3. assert our resource is in place.
        self.assertEqual('file:///not_really_here.yaml',
                         g_env.get_resource_info('OS::Nova::Server').value)

    def test_env_one_resource_disable(self):
        # prove we can disable a resource in the global environment

        g_env_content = '''
        resource_registry:
            "OS::Nova::Server":
        '''
        # 1. fake an environment file
        envdir = self.useFixture(fixtures.TempDir())
        envfile = os.path.join(envdir.path, 'test.yaml')
        with open(envfile, 'w+') as ef:
            ef.write(g_env_content)
        cfg.CONF.set_override('environment_dir', envdir.path)

        # 2. load global env
        g_env = environment.Environment({}, user_env=False)
        resources._load_global_environment(g_env)

        # 3. assert our resource is in now gone.
        self.assertIsNone(g_env.get_resource_info('OS::Nova::Server'))

        # 4. make sure we haven't removed something we shouldn't have
        self.assertEqual(instance.Instance,
                         g_env.get_resource_info('AWS::EC2::Instance').value)

    def test_env_multi_resources_disable(self):
        # prove we can disable resources in the global environment

        g_env_content = '''
        resource_registry:
            "AWS::*":
        '''
        # 1. fake an environment file
        envdir = self.useFixture(fixtures.TempDir())
        envfile = os.path.join(envdir.path, 'test.yaml')
        with open(envfile, 'w+') as ef:
            ef.write(g_env_content)
        cfg.CONF.set_override('environment_dir', envdir.path)

        # 2. load global env
        g_env = environment.Environment({}, user_env=False)
        resources._load_global_environment(g_env)

        # 3. assert our resources are now gone.
        self.assertIsNone(g_env.get_resource_info('AWS::EC2::Instance'))

        # 4. make sure we haven't removed something we shouldn't have
        self.assertEqual(server.Server,
                         g_env.get_resource_info('OS::Nova::Server').value)

    def test_env_user_cant_disable_sys_resource(self):
        # prove a user can't disable global resources from the user environment

        u_env_content = '''
        resource_registry:
            "AWS::*":
        '''
        # 1. load user env
        u_env = environment.Environment()
        u_env.load(environment_format.parse(u_env_content))

        # 2. assert global resources are NOT gone.
        self.assertEqual(
            instance.Instance,
            u_env.get_resource_info('AWS::EC2::Instance').value)

    def test_env_ignore_files_starting_dot(self):
        # prove we can disable a resource in the global environment

        g_env_content = ''
        # 1. fake an environment file
        envdir = self.useFixture(fixtures.TempDir())
        with open(os.path.join(envdir.path, 'a.yaml'), 'w+') as ef:
            ef.write(g_env_content)
        with open(os.path.join(envdir.path, '.test.yaml'), 'w+') as ef:
            ef.write(g_env_content)
        with open(os.path.join(envdir.path, 'b.yaml'), 'w+') as ef:
            ef.write(g_env_content)
        cfg.CONF.set_override('environment_dir', envdir.path)

        # 2. load global env
        g_env = environment.Environment({}, user_env=False)
        with mock.patch('heat.engine.environment.open',
                        mock.mock_open(read_data=g_env_content),
                        create=True) as m_open:
            resources._load_global_environment(g_env)

        # 3. assert that the file were ignored
        expected = [mock.call('%s/a.yaml' % envdir.path),
                    mock.call('%s/b.yaml' % envdir.path)]
        call_list = m_open.call_args_list

        expected.sort()
        call_list.sort()

        self.assertEqual(expected, call_list)


class ChildEnvTest(common.HeatTestCase):

    def test_params_flat(self):
        new_params = {'foo': 'bar', 'tester': 'Yes'}
        penv = environment.Environment()
        expected = {'parameters': new_params,
                    'encrypted_param_names': [],
                    'parameter_defaults': {},
                    'resource_registry': {'resources': {}}}
        cenv = environment.get_child_environment(penv, new_params)
        self.assertEqual(expected, cenv.user_env_as_dict())

    def test_params_normal(self):
        new_params = {'parameters': {'foo': 'bar', 'tester': 'Yes'}}
        penv = environment.Environment()
        expected = {'parameter_defaults': {},
                    'encrypted_param_names': [],
                    'resource_registry': {'resources': {}}}
        expected.update(new_params)
        cenv = environment.get_child_environment(penv, new_params)
        self.assertEqual(expected, cenv.user_env_as_dict())

    def test_params_parent_overwritten(self):
        new_params = {'parameters': {'foo': 'bar', 'tester': 'Yes'}}
        parent_params = {'parameters': {'gone': 'hopefully'}}
        penv = environment.Environment(env=parent_params)
        expected = {'parameter_defaults': {},
                    'encrypted_param_names': [],
                    'resource_registry': {'resources': {}}}
        expected.update(new_params)
        cenv = environment.get_child_environment(penv, new_params)
        self.assertEqual(expected, cenv.user_env_as_dict())

    def test_registry_merge_simple(self):
        env1 = {u'resource_registry': {u'OS::Food': u'fruity.yaml'}}
        env2 = {u'resource_registry': {u'OS::Fruit': u'apples.yaml'}}
        penv = environment.Environment(env=env1)
        cenv = environment.get_child_environment(penv, env2)
        rr = cenv.user_env_as_dict()['resource_registry']
        self.assertIn('OS::Food', rr)
        self.assertIn('OS::Fruit', rr)

    def test_registry_merge_favor_child(self):
        env1 = {u'resource_registry': {u'OS::Food': u'carrots.yaml'}}
        env2 = {u'resource_registry': {u'OS::Food': u'apples.yaml'}}
        penv = environment.Environment(env=env1)
        cenv = environment.get_child_environment(penv, env2)
        res = cenv.get_resource_info('OS::Food')
        self.assertEqual('apples.yaml', res.value)

    def test_item_to_remove_simple(self):
        env = {u'resource_registry': {u'OS::Food': u'fruity.yaml'}}
        penv = environment.Environment(env)
        victim = penv.get_resource_info('OS::Food', resource_name='abc')
        self.assertIsNotNone(victim)
        cenv = environment.get_child_environment(penv, None,
                                                 item_to_remove=victim)
        res = cenv.get_resource_info('OS::Food', resource_name='abc')
        self.assertIsNone(res)
        self.assertNotIn('OS::Food',
                         cenv.user_env_as_dict()['resource_registry'])
        # make sure the parent env is uneffected
        innocent = penv.get_resource_info('OS::Food', resource_name='abc')
        self.assertIsNotNone(innocent)

    def test_item_to_remove_complex(self):
        env = {u'resource_registry': {u'OS::Food': u'fruity.yaml',
                                      u'resources': {u'abc': {
                                          u'OS::Food': u'nutty.yaml'}}}}
        penv = environment.Environment(env)
        # the victim we want is the most specific one.
        victim = penv.get_resource_info('OS::Food', resource_name='abc')
        self.assertEqual(['resources', 'abc', 'OS::Food'], victim.path)
        cenv = environment.get_child_environment(penv, None,
                                                 item_to_remove=victim)
        res = cenv.get_resource_info('OS::Food', resource_name='abc')
        self.assertEqual(['OS::Food'], res.path)
        rr = cenv.user_env_as_dict()['resource_registry']
        self.assertIn('OS::Food', rr)
        self.assertNotIn('OS::Food', rr['resources']['abc'])
        # make sure the parent env is uneffected
        innocent2 = penv.get_resource_info('OS::Food', resource_name='abc')
        self.assertEqual(['resources', 'abc', 'OS::Food'], innocent2.path)

    def test_item_to_remove_none(self):
        env = {u'resource_registry': {u'OS::Food': u'fruity.yaml'}}
        penv = environment.Environment(env)
        victim = penv.get_resource_info('OS::Food', resource_name='abc')
        self.assertIsNotNone(victim)
        cenv = environment.get_child_environment(penv, None)
        res = cenv.get_resource_info('OS::Food', resource_name='abc')
        self.assertIsNotNone(res)

    def test_drill_down_to_child_resource(self):
        env = {
            u'resource_registry': {
                u'OS::Food': u'fruity.yaml',
                u'resources': {
                    u'a': {
                        u'OS::Fruit': u'apples.yaml',
                        u'hooks': 'pre-create',
                    },
                    u'nested': {
                        u'b': {
                            u'OS::Fruit': u'carrots.yaml',
                        },
                        u'nested_res': {
                            u'hooks': 'pre-create',
                        }
                    }
                }
            }
        }
        penv = environment.Environment(env)
        cenv = environment.get_child_environment(
            penv, None, child_resource_name=u'nested')
        registry = cenv.user_env_as_dict()['resource_registry']
        resources = registry['resources']
        self.assertIn('nested_res', resources)
        self.assertIn('hooks', resources['nested_res'])
        self.assertIsNotNone(
            cenv.get_resource_info('OS::Food', resource_name='abc'))
        self.assertIsNone(
            cenv.get_resource_info('OS::Fruit', resource_name='a'))
        res = cenv.get_resource_info('OS::Fruit', resource_name='b')
        self.assertIsNotNone(res)
        self.assertEqual(u'carrots.yaml', res.value)

    def test_drill_down_non_matching_wildcard(self):
        env = {
            u'resource_registry': {
                u'resources': {
                    u'nested': {
                        u'c': {
                            u'OS::Fruit': u'carrots.yaml',
                            u'hooks': 'pre-create',
                        },
                    },
                    u'*_doesnt_match_nested': {
                        u'nested_res': {
                            u'hooks': 'pre-create',
                        },
                    }
                }
            }
        }
        penv = environment.Environment(env)
        cenv = environment.get_child_environment(
            penv, None, child_resource_name=u'nested')
        registry = cenv.user_env_as_dict()['resource_registry']
        resources = registry['resources']
        self.assertIn('c', resources)
        self.assertNotIn('nested_res', resources)
        res = cenv.get_resource_info('OS::Fruit', resource_name='c')
        self.assertIsNotNone(res)
        self.assertEqual(u'carrots.yaml', res.value)

    def test_drill_down_matching_wildcard(self):
        env = {
            u'resource_registry': {
                u'resources': {
                    u'nested': {
                        u'c': {
                            u'OS::Fruit': u'carrots.yaml',
                            u'hooks': 'pre-create',
                        },
                    },
                    u'nest*': {
                        u'nested_res': {
                            u'hooks': 'pre-create',
                        },
                    }
                }
            }
        }
        penv = environment.Environment(env)
        cenv = environment.get_child_environment(
            penv, None, child_resource_name=u'nested')
        registry = cenv.user_env_as_dict()['resource_registry']
        resources = registry['resources']
        self.assertIn('c', resources)
        self.assertIn('nested_res', resources)
        res = cenv.get_resource_info('OS::Fruit', resource_name='c')
        self.assertIsNotNone(res)
        self.assertEqual(u'carrots.yaml', res.value)

    def test_drill_down_prefer_exact_match(self):
        env = {
            u'resource_registry': {
                u'resources': {
                    u'*esource': {
                        u'hooks': 'pre-create',
                    },
                    u'res*': {
                        u'hooks': 'pre-create',
                    },
                    u'resource': {
                        u'OS::Fruit': u'carrots.yaml',
                        u'hooks': 'pre-update',
                    },
                    u'resource*': {
                        u'hooks': 'pre-create',
                    },
                    u'*resource': {
                        u'hooks': 'pre-create',
                    },
                    u'*sour*': {
                        u'hooks': 'pre-create',
                    },
                }
            }
        }
        penv = environment.Environment(env)
        cenv = environment.get_child_environment(
            penv, None, child_resource_name=u'resource')
        registry = cenv.user_env_as_dict()['resource_registry']
        resources = registry['resources']
        self.assertEqual(u'carrots.yaml', resources[u'OS::Fruit'])
        self.assertEqual('pre-update', resources[u'hooks'])


class ResourceRegistryTest(common.HeatTestCase):

    def test_resources_load(self):
        resources = {
            u'pre_create': {
                u'OS::Fruit': u'apples.yaml',
                u'hooks': 'pre-create',
            },
            u'pre_update': {
                u'hooks': 'pre-update',
            },
            u'both': {
                u'hooks': ['pre-create', 'pre-update'],
            },
            u'b': {
                u'OS::Food': u'fruity.yaml',
            },
            u'nested': {
                u'res': {
                    u'hooks': 'pre-create',
                },
            },
        }
        registry = environment.ResourceRegistry(None, {})
        registry.load({'resources': resources})
        self.assertIsNotNone(registry.get_resource_info(
            'OS::Fruit', resource_name='pre_create'))
        self.assertIsNotNone(registry.get_resource_info(
            'OS::Food', resource_name='b'))
        resources = registry.as_dict()['resources']
        self.assertEqual('pre-create',
                         resources['pre_create']['hooks'])
        self.assertEqual('pre-update',
                         resources['pre_update']['hooks'])
        self.assertEqual(['pre-create', 'pre-update'],
                         resources['both']['hooks'])
        self.assertEqual('pre-create',
                         resources['nested']['res']['hooks'])

    def test_load_registry_invalid_hook_type(self):
        resources = {
            u'resources': {
                u'a': {
                    u'hooks': 'invalid-type',
                }
            }
        }

        registry = environment.ResourceRegistry(None, {})
        msg = ('Invalid hook type "invalid-type" for resource breakpoint, '
               'acceptable hook types are: (\'pre-create\', \'pre-update\')')
        ex = self.assertRaises(exception.InvalidBreakPointHook,
                               registry.load, {'resources': resources})
        self.assertEqual(msg, six.text_type(ex))


class HookMatchTest(common.HeatTestCase):

    def test_plain_matches(self):
        resources = {
            u'a': {
                u'OS::Fruit': u'apples.yaml',
                u'hooks': [u'pre-create', u'pre-update'],
            },
            u'b': {
                u'OS::Food': u'fruity.yaml',
            },
            u'nested': {
                u'res': {
                    u'hooks': 'pre-create',
                },
            },
        }
        registry = environment.ResourceRegistry(None, {})
        registry.load({
            u'OS::Fruit': u'apples.yaml',
            'resources': resources})

        self.assertTrue(registry.matches_hook(
            'a', environment.HOOK_PRE_CREATE))
        self.assertFalse(registry.matches_hook(
            'b', environment.HOOK_PRE_CREATE))
        self.assertFalse(registry.matches_hook(
            'OS::Fruit', environment.HOOK_PRE_CREATE))
        self.assertFalse(registry.matches_hook(
            'res', environment.HOOK_PRE_CREATE))
        self.assertFalse(registry.matches_hook(
            'unknown', environment.HOOK_PRE_CREATE))

    def test_wildcard_matches(self):
        resources = {
            u'prefix_*': {
                u'hooks': 'pre-create',
            },
            u'*_suffix': {
                u'hooks': 'pre-create',
            },
            u'*': {
                u'hooks': 'pre-update',
            },
        }
        registry = environment.ResourceRegistry(None, {})
        registry.load({'resources': resources})

        self.assertTrue(registry.matches_hook(
            'prefix_', environment.HOOK_PRE_CREATE))
        self.assertTrue(registry.matches_hook(
            'prefix_some', environment.HOOK_PRE_CREATE))
        self.assertFalse(registry.matches_hook(
            'some_prefix', environment.HOOK_PRE_CREATE))

        self.assertTrue(registry.matches_hook(
            '_suffix', environment.HOOK_PRE_CREATE))
        self.assertTrue(registry.matches_hook(
            'some_suffix', environment.HOOK_PRE_CREATE))
        self.assertFalse(registry.matches_hook(
            '_suffix_blah', environment.HOOK_PRE_CREATE))

        self.assertTrue(registry.matches_hook(
            'some_prefix', environment.HOOK_PRE_UPDATE))
        self.assertTrue(registry.matches_hook(
            '_suffix_blah', environment.HOOK_PRE_UPDATE))

    def test_hook_types(self):
        resources = {
            u'pre_create': {
                u'hooks': 'pre-create',
            },
            u'pre_update': {
                u'hooks': 'pre-update',
            },
            u'both': {
                u'hooks': ['pre-create', 'pre-update'],
            },
        }
        registry = environment.ResourceRegistry(None, {})
        registry.load({'resources': resources})

        self.assertTrue(registry.matches_hook(
            'pre_create', environment.HOOK_PRE_CREATE))
        self.assertFalse(registry.matches_hook(
            'pre_create', environment.HOOK_PRE_UPDATE))

        self.assertTrue(registry.matches_hook(
            'pre_update', environment.HOOK_PRE_UPDATE))
        self.assertFalse(registry.matches_hook(
            'pre_update', environment.HOOK_PRE_CREATE))

        self.assertTrue(registry.matches_hook(
            'both', environment.HOOK_PRE_CREATE))
        self.assertTrue(registry.matches_hook(
            'both', environment.HOOK_PRE_UPDATE))
