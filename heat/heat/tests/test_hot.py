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

import copy

import six

from heat.common import exception
from heat.common import identifier
from heat.common import template_format
from heat.engine import environment
from heat.engine import function
from heat.engine.hot import functions as hot_functions
from heat.engine.hot import parameters as hot_param
from heat.engine.hot import template as hot_template
from heat.engine import parameters
from heat.engine import resource
from heat.engine import resources
from heat.engine import rsrc_defn
from heat.engine import stack as parser
from heat.engine import template
from heat.tests import common
from heat.tests import generic_resource as generic_rsrc
from heat.tests import utils

empty_template = template_format.parse('''{
  "HeatTemplateFormatVersion" : "2012-12-12",
}''')

hot_tpl_empty = template_format.parse('''
heat_template_version: 2013-05-23
''')

hot_juno_tpl_empty = template_format.parse('''
heat_template_version: 2014-10-16
''')

hot_kilo_tpl_empty = template_format.parse('''
heat_template_version: 2015-04-30
''')

hot_liberty_tpl_empty = template_format.parse('''
heat_template_version: 2015-10-15
''')

hot_tpl_empty_sections = template_format.parse('''
heat_template_version: 2013-05-23
parameters:
resources:
outputs:
''')

hot_tpl_generic_resource = template_format.parse('''
heat_template_version: 2013-05-23
resources:
  resource1:
    type: GenericResourceType
''')

hot_tpl_complex_attrs = template_format.parse('''
heat_template_version: 2013-05-23
resources:
  resource1:
    type: ResourceWithComplexAttributesType
''')

hot_tpl_mapped_props = template_format.parse('''
heat_template_version: 2013-05-23
resources:
  resource1:
    type: ResWithComplexPropsAndAttrs
  resource2:
    type: ResWithComplexPropsAndAttrs
    properties:
      a_list: { get_attr: [ resource1, list] }
      a_string: { get_attr: [ resource1, string ] }
      a_map: { get_attr: [ resource1, map] }
''')


class DummyClass(object):
    metadata = None

    def metadata_get(self):
        return self.metadata

    def metadata_set(self, metadata):
        self.metadata = metadata


class HOTemplateTest(common.HeatTestCase):
    """Test processing of HOT templates."""

    @staticmethod
    def resolve(snippet, template, stack=None):
        return function.resolve(template.parse(stack, snippet))

    def test_defaults(self):
        """Test default content behavior of HOT template."""

        tmpl = template.Template(hot_tpl_empty)
        # check if we get the right class
        self.assertIsInstance(tmpl, hot_template.HOTemplate20130523)
        # test getting an invalid section
        self.assertNotIn('foobar', tmpl)

        # test defaults for valid sections
        self.assertEqual('No description', tmpl[tmpl.DESCRIPTION])
        self.assertEqual({}, tmpl[tmpl.RESOURCES])
        self.assertEqual({}, tmpl[tmpl.OUTPUTS])

    def test_defaults_for_empty_sections(self):
        """Test default secntion's content behavior of HOT template."""

        tmpl = template.Template(hot_tpl_empty_sections)
        # check if we get the right class
        self.assertIsInstance(tmpl, hot_template.HOTemplate20130523)
        # test getting an invalid section
        self.assertNotIn('foobar', tmpl)

        # test defaults for valid sections
        self.assertEqual('No description', tmpl[tmpl.DESCRIPTION])
        self.assertEqual({}, tmpl[tmpl.RESOURCES])
        self.assertEqual({}, tmpl[tmpl.OUTPUTS])

        stack = parser.Stack(utils.dummy_context(), 'test_stack', tmpl)

        self.assertIsNone(stack.parameters._validate_user_parameters())
        self.assertIsNone(stack.parameters._validate_tmpl_parameters())
        self.assertIsNone(stack.validate())

    def test_translate_resources_good(self):
        """Test translation of resources into internal engine format."""

        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        resources:
          resource1:
            type: AWS::EC2::Instance
            properties:
              property1: value1
            metadata:
              foo: bar
            depends_on: dummy
            deletion_policy: dummy
            update_policy:
              foo: bar
        ''')

        expected = {'resource1': {'Type': 'AWS::EC2::Instance',
                                  'Properties': {'property1': 'value1'},
                                  'Metadata': {'foo': 'bar'},
                                  'DependsOn': 'dummy',
                                  'DeletionPolicy': 'dummy',
                                  'UpdatePolicy': {'foo': 'bar'}}}

        tmpl = template.Template(hot_tpl)
        self.assertEqual(expected, tmpl[tmpl.RESOURCES])

    def test_translate_resources_bad_no_data(self):
        """Test translation of resources without any mapping."""

        hot_tpl = template_format.parse("""
        heat_template_version: 2013-05-23
        resources:
          resource1:
        """)

        tmpl = template.Template(hot_tpl)
        error = self.assertRaises(exception.StackValidationFailed,
                                  tmpl.__getitem__, tmpl.RESOURCES)
        self.assertEqual('Each resource must contain a type key.',
                         six.text_type(error))

    def test_translate_resources_bad_type(self):
        """Test translation of resources including invalid keyword."""

        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        resources:
          resource1:
            Type: AWS::EC2::Instance
            properties:
              property1: value1
            metadata:
              foo: bar
            depends_on: dummy
            deletion_policy: dummy
            update_policy:
              foo: bar
        ''')

        tmpl = template.Template(hot_tpl)
        err = self.assertRaises(exception.StackValidationFailed,
                                tmpl.__getitem__, tmpl.RESOURCES)
        self.assertEqual('"Type" is not a valid keyword '
                         'inside a resource definition',
                         six.text_type(err))

    def test_translate_resources_bad_properties(self):
        """Test translation of resources including invalid keyword."""

        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        resources:
          resource1:
            type: AWS::EC2::Instance
            Properties:
              property1: value1
            metadata:
              foo: bar
            depends_on: dummy
            deletion_policy: dummy
            update_policy:
              foo: bar
        ''')

        tmpl = template.Template(hot_tpl)
        err = self.assertRaises(exception.StackValidationFailed,
                                tmpl.__getitem__, tmpl.RESOURCES)
        self.assertEqual('"Properties" is not a valid keyword '
                         'inside a resource definition',
                         six.text_type(err))

    def test_translate_resources_resources_without_name(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        resources:
          type: AWS::EC2::Instance
          properties:
            property1: value1
          metadata:
            foo: bar
          depends_on: dummy
          deletion_policy: dummy
        ''')
        tmpl = template.Template(hot_tpl)
        error = self.assertRaises(exception.StackValidationFailed,
                                  tmpl.__getitem__, tmpl.RESOURCES)
        self.assertEqual('"resources" must contain a map of resource maps. '
                         'Found a [%s] instead' % six.text_type,
                         six.text_type(error))

    def test_translate_resources_bad_metadata(self):
        """Test translation of resources including invalid keyword."""

        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        resources:
          resource1:
            type: AWS::EC2::Instance
            properties:
              property1: value1
            Metadata:
              foo: bar
            depends_on: dummy
            deletion_policy: dummy
            update_policy:
              foo: bar
        ''')

        tmpl = template.Template(hot_tpl)
        err = self.assertRaises(exception.StackValidationFailed,
                                tmpl.__getitem__, tmpl.RESOURCES)

        self.assertEqual('"Metadata" is not a valid keyword '
                         'inside a resource definition',
                         six.text_type(err))

    def test_translate_resources_bad_depends_on(self):
        """Test translation of resources including invalid keyword."""

        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        resources:
          resource1:
            type: AWS::EC2::Instance
            properties:
              property1: value1
            metadata:
              foo: bar
            DependsOn: dummy
            deletion_policy: dummy
            update_policy:
              foo: bar
        ''')

        tmpl = template.Template(hot_tpl)
        err = self.assertRaises(exception.StackValidationFailed,
                                tmpl.__getitem__, tmpl.RESOURCES)
        self.assertEqual('"DependsOn" is not a valid keyword '
                         'inside a resource definition',
                         six.text_type(err))

    def test_translate_resources_bad_deletion_policy(self):
        """Test translation of resources including invalid keyword."""

        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        resources:
          resource1:
            type: AWS::EC2::Instance
            properties:
              property1: value1
            metadata:
              foo: bar
            depends_on: dummy
            DeletionPolicy: dummy
            update_policy:
              foo: bar
        ''')

        tmpl = template.Template(hot_tpl)
        err = self.assertRaises(exception.StackValidationFailed,
                                tmpl.__getitem__, tmpl.RESOURCES)
        self.assertEqual('"DeletionPolicy" is not a valid keyword '
                         'inside a resource definition',
                         six.text_type(err))

    def test_translate_resources_bad_update_policy(self):
        """Test translation of resources including invalid keyword."""

        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        resources:
          resource1:
            type: AWS::EC2::Instance
            properties:
              property1: value1
            metadata:
              foo: bar
            depends_on: dummy
            deletion_policy: dummy
            UpdatePolicy:
              foo: bar
        ''')

        tmpl = template.Template(hot_tpl)
        err = self.assertRaises(exception.StackValidationFailed,
                                tmpl.__getitem__, tmpl.RESOURCES)
        self.assertEqual('"UpdatePolicy" is not a valid keyword '
                         'inside a resource definition',
                         six.text_type(err))

    def test_translate_outputs_good(self):
        """Test translation of outputs into internal engine format."""

        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        outputs:
          output1:
            description: output1
            value: value1
        ''')

        expected = {'output1': {'Description': 'output1', 'Value': 'value1'}}

        tmpl = template.Template(hot_tpl)
        self.assertEqual(expected, tmpl[tmpl.OUTPUTS])

    def test_translate_outputs_bad_no_data(self):
        """Test translation of outputs without any mapping."""

        hot_tpl = template_format.parse("""
        heat_template_version: 2013-05-23
        outputs:
          output1:
        """)

        tmpl = template.Template(hot_tpl)
        error = self.assertRaises(exception.StackValidationFailed,
                                  tmpl.__getitem__, tmpl.OUTPUTS)
        self.assertEqual('Each output must contain a value key.',
                         six.text_type(error))

    def test_translate_outputs_bad_without_name(self):
        """Test translation of outputs without name."""

        hot_tpl = template_format.parse("""
        heat_template_version: 2013-05-23
        outputs:
          description: wrong output
          value: value1
        """)

        tmpl = template.Template(hot_tpl)
        error = self.assertRaises(exception.StackValidationFailed,
                                  tmpl.__getitem__, tmpl.OUTPUTS)
        self.assertEqual('"outputs" must contain a map of output maps. '
                         'Found a [%s] instead' % six.text_type,
                         six.text_type(error))

    def test_translate_outputs_bad_description(self):
        """Test translation of outputs into internal engine format."""

        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        outputs:
          output1:
            Description: output1
            value: value1
        ''')

        tmpl = template.Template(hot_tpl)
        err = self.assertRaises(exception.StackValidationFailed,
                                tmpl.__getitem__, tmpl.OUTPUTS)
        self.assertIn('Description', six.text_type(err))

    def test_translate_outputs_bad_value(self):
        """Test translation of outputs into internal engine format."""

        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        outputs:
          output1:
            description: output1
            Value: value1
        ''')

        tmpl = template.Template(hot_tpl)
        err = self.assertRaises(exception.StackValidationFailed,
                                tmpl.__getitem__, tmpl.OUTPUTS)
        self.assertIn('Value', six.text_type(err))

    def test_resource_group_list_join(self):
        """Test list_join on a ResourceGroup's inner attributes

        This should not fail during validation (i.e. before the ResourceGroup
        can return the list of the runtime values.
        """
        hot_tpl = template_format.parse('''
        heat_template_version: 2014-10-16
        resources:
          rg:
            type: OS::Heat::ResourceGroup
            properties:
              count: 3
              resource_def:
                type: OS::Nova::Server
        ''')
        tmpl = template.Template(hot_tpl)
        stack = parser.Stack(utils.dummy_context(), 'test_stack', tmpl)
        snippet = {'list_join': ["\n", {'get_attr': ['rg', 'name']}]}
        self.assertEqual('', self.resolve(snippet, tmpl, stack))

    def test_str_replace(self):
        """Test str_replace function."""

        snippet = {'str_replace': {'template': 'Template var1 string var2',
                                   'params': {'var1': 'foo', 'var2': 'bar'}}}
        snippet_resolved = 'Template foo string bar'

        tmpl = template.Template(hot_tpl_empty)

        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl))

    def test_str_replace_number(self):
        """Test str_replace function with numbers."""

        snippet = {'str_replace': {'template': 'Template number string bar',
                                   'params': {'number': 1}}}
        snippet_resolved = 'Template 1 string bar'

        tmpl = template.Template(hot_tpl_empty)

        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl))

    def test_str_fn_replace(self):
        """Test Fn:Replace function."""

        snippet = {'Fn::Replace': [{'$var1': 'foo', '$var2': 'bar'},
                                   'Template $var1 string $var2']}
        snippet_resolved = 'Template foo string bar'

        tmpl = template.Template(hot_tpl_empty)

        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl))

    def test_str_replace_syntax(self):
        """
        Test str_replace function syntax.

        Pass wrong syntax (array instead of dictionary) to function and
        validate that we get a TypeError.
        """

        snippet = {'str_replace': [{'template': 'Template var1 string var2'},
                                   {'params': {'var1': 'foo', 'var2': 'bar'}}]}

        tmpl = template.Template(hot_tpl_empty)

        self.assertRaises(TypeError, self.resolve, snippet, tmpl)

    def test_str_replace_invalid_param_keys(self):
        """
        Test str_replace function parameter keys.

        Pass wrong parameters to function and verify that we get
        a KeyError.
        """

        snippet = {'str_replace': {'tmpl': 'Template var1 string var2',
                                   'params': {'var1': 'foo', 'var2': 'bar'}}}

        tmpl = template.Template(hot_tpl_empty)

        self.assertRaises(KeyError, self.resolve, snippet, tmpl)

        snippet = {'str_replace': {'tmpl': 'Template var1 string var2',
                                   'parms': {'var1': 'foo', 'var2': 'bar'}}}

        self.assertRaises(KeyError, self.resolve, snippet, tmpl)

    def test_str_replace_invalid_param_types(self):
        """
        Test str_replace function parameter values.

        Pass parameter values of wrong type to function and verify that we get
        a TypeError.
        """

        snippet = {'str_replace': {'template': 12345,
                                   'params': {'var1': 'foo', 'var2': 'bar'}}}

        tmpl = template.Template(hot_tpl_empty)

        self.assertRaises(TypeError, self.resolve, snippet, tmpl)

        snippet = {'str_replace': {'template': 'Template var1 string var2',
                                   'params': ['var1', 'foo', 'var2', 'bar']}}

        self.assertRaises(TypeError, self.resolve, snippet, tmpl)

    def test_get_file(self):
        """Test get_file function."""

        snippet = {'get_file': 'file:///tmp/foo.yaml'}
        snippet_resolved = 'foo contents'

        tmpl = template.Template(hot_tpl_empty, files={
            'file:///tmp/foo.yaml': 'foo contents'
        })
        stack = parser.Stack(utils.dummy_context(), 'param_id_test', tmpl)

        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl, stack))

    def test_get_file_not_string(self):
        """Test get_file function with non-string argument."""

        snippet = {'get_file': ['file:///tmp/foo.yaml']}
        tmpl = template.Template(hot_tpl_empty)
        stack = parser.Stack(utils.dummy_context(), 'param_id_test', tmpl)
        notStrErr = self.assertRaises(TypeError, self.resolve,
                                      snippet, tmpl, stack)
        self.assertEqual(
            'Argument to "get_file" must be a string',
            six.text_type(notStrErr))

    def test_get_file_missing_files(self):
        """Test get_file function with no matching key in files section."""

        snippet = {'get_file': 'file:///tmp/foo.yaml'}

        tmpl = template.Template(hot_tpl_empty, files={
            'file:///tmp/bar.yaml': 'bar contents'
        })
        stack = parser.Stack(utils.dummy_context(), 'param_id_test', tmpl)

        missingErr = self.assertRaises(ValueError, self.resolve,
                                       snippet, tmpl, stack)
        self.assertEqual(
            ('No content found in the "files" section for '
             'get_file path: file:///tmp/foo.yaml'),
            six.text_type(missingErr))

    def test_get_file_nested_does_not_resolve(self):
        """Test get_file function does not resolve nested calls."""
        snippet = {'get_file': 'file:///tmp/foo.yaml'}
        snippet_resolved = '{get_file: file:///tmp/bar.yaml}'

        tmpl = template.Template(hot_tpl_empty, files={
            'file:///tmp/foo.yaml': snippet_resolved,
            'file:///tmp/bar.yaml': 'bar content',
        })
        stack = parser.Stack(utils.dummy_context(), 'param_id_test', tmpl)

        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl, stack))

    def test_list_join(self):
        snippet = {'list_join': [',', ['bar', 'baz']]}
        snippet_resolved = 'bar,baz'
        tmpl = template.Template(hot_kilo_tpl_empty)
        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl))

    def test_join_multiple(self):
        snippet = {'list_join': [',', ['bar', 'baz'], ['bar2', 'baz2']]}
        snippet_resolved = 'bar,baz,bar2,baz2'
        tmpl = template.Template(hot_liberty_tpl_empty)
        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl))

    def test_join_invalid(self):
        snippet = {'list_join': 'bad'}
        tmpl = template.Template(hot_liberty_tpl_empty)
        exc = self.assertRaises(TypeError, self.resolve, snippet, tmpl)
        self.assertIn('Incorrect arguments', six.text_type(exc))

    def test_join_invalid_value(self):
        snippet = {'list_join': [',']}
        tmpl = template.Template(hot_liberty_tpl_empty)

        exc = self.assertRaises(ValueError, self.resolve, snippet, tmpl)
        self.assertIn('Incorrect arguments', six.text_type(exc))

    def test_join_invalid_multiple(self):
        snippet = {'list_join': [',', 'bad', ['foo']]}
        tmpl = template.Template(hot_liberty_tpl_empty)
        exc = self.assertRaises(TypeError, self.resolve, snippet, tmpl)
        self.assertIn('Incorrect arguments', six.text_type(exc))

    def test_repeat(self):
        """Test repeat function."""
        hot_tpl = template_format.parse('''
        heat_template_version: 2015-04-30
        parameters:
          param:
            type: comma_delimited_list
            default: 'a,b,c'
        ''')
        snippet = {'repeat': {'template': 'this is var%',
                   'for_each': {'var%': {'get_param': 'param'}}}}
        snippet_resolved = ['this is a', 'this is b', 'this is c']

        tmpl = template.Template(hot_tpl)
        stack = parser.Stack(utils.dummy_context(), 'test_stack', tmpl)

        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl, stack))

    def test_repeat_dict_template(self):
        """Test repeat function with a dictionary as a template."""
        snippet = {'repeat': {'template': {'key-%var%': 'this is %var%'},
                              'for_each': {'%var%': ['a', 'b', 'c']}}}
        snippet_resolved = [{'key-a': 'this is a'},
                            {'key-b': 'this is b'},
                            {'key-c': 'this is c'}]

        tmpl = template.Template(hot_kilo_tpl_empty)

        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl))

    def test_repeat_list_template(self):
        """Test repeat function with a list as a template."""
        snippet = {'repeat': {'template': ['this is %var%', 'static'],
                              'for_each': {'%var%': ['a', 'b', 'c']}}}
        snippet_resolved = [['this is a', 'static'],
                            ['this is b', 'static'],
                            ['this is c', 'static']]

        tmpl = template.Template(hot_kilo_tpl_empty)

        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl))

    def test_repeat_multi_list(self):
        """Test repeat function with multiple input lists."""
        snippet = {'repeat': {'template': 'this is %var1%-%var2%',
                              'for_each': {'%var1%': ['a', 'b', 'c'],
                                           '%var2%': ['1', '2']}}}
        snippet_resolved = ['this is a-1', 'this is b-1', 'this is c-1',
                            'this is a-2', 'this is b-2', 'this is c-2']

        tmpl = template.Template(hot_kilo_tpl_empty)

        result = self.resolve(snippet, tmpl)
        self.assertEqual(len(result), len(snippet_resolved))
        for item in result:
            self.assertIn(item, snippet_resolved)

    def test_repeat_bad_args(self):
        """
        Test that the repeat function reports a proper error when missing
        or invalid arguments.
        """
        tmpl = template.Template(hot_kilo_tpl_empty)

        # missing for_each
        snippet = {'repeat': {'template': 'this is %var%'}}
        self.assertRaises(KeyError, self.resolve, snippet, tmpl)

        # misspelled for_each
        snippet = {'repeat': {'template': 'this is %var%',
                              'foreach': {'%var%': ['a', 'b', 'c']}}}
        self.assertRaises(KeyError, self.resolve, snippet, tmpl)

        # for_each is not a map
        snippet = {'repeat': {'template': 'this is %var%',
                              'for_each': '%var%'}}
        self.assertRaises(TypeError, self.resolve, snippet, tmpl)

        # value given to for_each entry is not a list
        snippet = {'repeat': {'template': 'this is %var%',
                              'for_each': {'%var%': 'a'}}}
        self.assertRaises(TypeError, self.resolve, snippet, tmpl)

        # misspelled template
        snippet = {'repeat': {'templte': 'this is %var%',
                              'for_each': {'%var%': ['a', 'b', 'c']}}}
        self.assertRaises(KeyError, self.resolve, snippet, tmpl)

    def test_digest(self):
        snippet = {'digest': ['md5', 'foobar']}
        snippet_resolved = '3858f62230ac3c915f300c664312c63f'

        tmpl = template.Template(hot_kilo_tpl_empty)
        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl))

    def test_digest_invalid_types(self):
        tmpl = template.Template(hot_kilo_tpl_empty)

        invalid_snippets = [
            {'digest': 'invalid'},
            {'digest': {'foo': 'invalid'}},
            {'digest': [123]},
        ]
        for snippet in invalid_snippets:
            exc = self.assertRaises(TypeError, self.resolve, snippet, tmpl)
            self.assertIn('must be a list of strings', six.text_type(exc))

    def test_digest_incorrect_number_arguments(self):
        tmpl = template.Template(hot_kilo_tpl_empty)

        invalid_snippets = [
            {'digest': []},
            {'digest': ['foo']},
            {'digest': ['md5']},
            {'digest': ['md5', 'foo', 'bar']},
        ]
        for snippet in invalid_snippets:
            exc = self.assertRaises(ValueError, self.resolve, snippet, tmpl)
            self.assertIn('usage: ["<algorithm>", "<value>"]',
                          six.text_type(exc))

    def test_digest_invalid_algorithm(self):
        tmpl = template.Template(hot_kilo_tpl_empty)

        snippet = {'digest': ['invalid_algorithm', 'foobar']}
        exc = self.assertRaises(ValueError, self.resolve, snippet, tmpl)
        self.assertIn('Algorithm must be one of', six.text_type(exc))

    def test_str_split(self):
        tmpl = template.Template(hot_liberty_tpl_empty)
        snippet = {'str_split': [',', 'bar,baz']}
        snippet_resolved = ['bar', 'baz']
        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl))

    def test_str_split_index(self):
        tmpl = template.Template(hot_liberty_tpl_empty)
        snippet = {'str_split': [',', 'bar,baz', 1]}
        snippet_resolved = 'baz'
        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl))

    def test_str_split_index_str(self):
        tmpl = template.Template(hot_liberty_tpl_empty)
        snippet = {'str_split': [',', 'bar,baz', '1']}
        snippet_resolved = 'baz'
        self.assertEqual(snippet_resolved, self.resolve(snippet, tmpl))

    def test_str_split_index_bad(self):
        tmpl = template.Template(hot_liberty_tpl_empty)
        snippet = {'str_split': [',', 'bar,baz', 'bad']}
        exc = self.assertRaises(ValueError, self.resolve, snippet, tmpl)
        self.assertIn('Incorrect index to \"str_split\"', six.text_type(exc))

    def test_str_split_index_out_of_range(self):
        tmpl = template.Template(hot_liberty_tpl_empty)
        snippet = {'str_split': [',', 'bar,baz', '2']}
        exc = self.assertRaises(ValueError, self.resolve, snippet, tmpl)
        expected = 'Incorrect index to \"str_split\" should be between 0 and 1'
        self.assertEqual(expected, six.text_type(exc))

    def test_str_split_bad_novalue(self):
        tmpl = template.Template(hot_liberty_tpl_empty)
        snippet = {'str_split': [',']}
        exc = self.assertRaises(ValueError, self.resolve, snippet, tmpl)
        self.assertIn('Incorrect arguments to \"str_split\"',
                      six.text_type(exc))

    def test_str_split_bad_empty(self):
        tmpl = template.Template(hot_liberty_tpl_empty)
        snippet = {'str_split': []}
        exc = self.assertRaises(ValueError, self.resolve, snippet, tmpl)
        self.assertIn('Incorrect arguments to \"str_split\"',
                      six.text_type(exc))

    def test_prevent_parameters_access(self):
        """
        Test that the parameters section can't be accessed using the template
        as a dictionary.
        """
        expected_description = "This can be accessed"
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        description: {0}
        parameters:
          foo:
            type: string
        '''.format(expected_description))

        tmpl = template.Template(hot_tpl)
        self.assertEqual(expected_description, tmpl['description'])

        err_str = "can not be accessed directly"

        # Hot template test
        keyError = self.assertRaises(KeyError, tmpl.__getitem__, 'parameters')
        self.assertIn(err_str, six.text_type(keyError))

        # CFN template test
        keyError = self.assertRaises(KeyError, tmpl.__getitem__, 'Parameters')
        self.assertIn(err_str, six.text_type(keyError))

    def test_parameters_section_not_iterable(self):
        """
        Test that the parameters section is not returned when the template is
        used as an iterable.
        """
        expected_description = "This can be accessed"
        tmpl = template.Template({'heat_template_version': '2013-05-23',
                                  'description': expected_description,
                                  'parameters':
                                  {'foo': {'Type': 'String',
                                           'Required': True}}})
        self.assertEqual(expected_description, tmpl['description'])
        self.assertNotIn('parameters', six.iterkeys(tmpl))

    def test_invalid_hot_version(self):
        """
        Test HOT version check.

        Pass an invalid HOT version to template.Template.__new__() and
        validate that we get a ValueError.
        """

        tmpl_str = "heat_template_version: this-ain't-valid"
        hot_tmpl = template_format.parse(tmpl_str)
        self.assertRaises(exception.InvalidTemplateVersion,
                          template.Template, hot_tmpl)

    def test_valid_hot_version(self):
        """
        Test HOT version check.

        Pass a valid HOT version to template.Template.__new__() and
        validate that we get back a parsed template.
        """

        tmpl_str = "heat_template_version: 2013-05-23"
        hot_tmpl = template_format.parse(tmpl_str)
        parsed_tmpl = template.Template(hot_tmpl)
        expected = ('heat_template_version', '2013-05-23')
        observed = parsed_tmpl.version
        self.assertEqual(expected, observed)

    def test_resource_facade(self):
        metadata_snippet = {'resource_facade': 'metadata'}
        deletion_policy_snippet = {'resource_facade': 'deletion_policy'}
        update_policy_snippet = {'resource_facade': 'update_policy'}

        parent_resource = DummyClass()
        parent_resource.metadata_set({"foo": "bar"})
        parent_resource.t = rsrc_defn.ResourceDefinition(
            'parent', 'SomeType',
            deletion_policy=rsrc_defn.ResourceDefinition.RETAIN,
            update_policy={"blarg": "wibble"})
        parent_resource.stack = parser.Stack(utils.dummy_context(),
                                             'toplevel_stack',
                                             template.Template(hot_tpl_empty))
        stack = parser.Stack(utils.dummy_context(), 'test_stack',
                             template.Template(hot_tpl_empty),
                             parent_resource='parent')
        stack._parent_stack = dict(parent=parent_resource)
        self.assertEqual({"foo": "bar"},
                         self.resolve(metadata_snippet, stack.t, stack))
        self.assertEqual('Retain',
                         self.resolve(deletion_policy_snippet, stack.t, stack))
        self.assertEqual({"blarg": "wibble"},
                         self.resolve(update_policy_snippet, stack.t, stack))

    def test_resource_facade_function(self):
        deletion_policy_snippet = {'resource_facade': 'deletion_policy'}

        parent_resource = DummyClass()
        parent_resource.metadata_set({"foo": "bar"})
        tmpl = template.Template(hot_juno_tpl_empty)
        parent_resource.stack = parser.Stack(utils.dummy_context(),
                                             'toplevel_stack',
                                             tmpl)
        del_policy = hot_functions.Join(parent_resource.stack,
                                        'list_join', ['eta', ['R', 'in']])
        parent_resource.t = rsrc_defn.ResourceDefinition(
            'parent', 'SomeType',
            deletion_policy=del_policy)

        stack = parser.Stack(utils.dummy_context(), 'test_stack',
                             template.Template(hot_tpl_empty),
                             parent_resource='parent')
        stack._parent_stack = dict(parent=parent_resource)
        self.assertEqual('Retain',
                         self.resolve(deletion_policy_snippet, stack.t, stack))

    def test_resource_facade_invalid_arg(self):
        snippet = {'resource_facade': 'wibble'}
        stack = parser.Stack(utils.dummy_context(), 'test_stack',
                             template.Template(hot_tpl_empty))
        error = self.assertRaises(ValueError,
                                  self.resolve,
                                  snippet,
                                  stack.t, stack)
        self.assertIn(list(six.iterkeys(snippet))[0], six.text_type(error))

    def test_resource_facade_missing_deletion_policy(self):
        snippet = {'resource_facade': 'deletion_policy'}

        parent_resource = DummyClass()
        parent_resource.metadata_set({"foo": "bar"})
        parent_resource.t = rsrc_defn.ResourceDefinition('parent', 'SomeType')
        parent_stack = parser.Stack(utils.dummy_context(),
                                    'toplevel_stack',
                                    template.Template(hot_tpl_empty))
        parent_stack._resources = {'parent': parent_resource}
        stack = parser.Stack(utils.dummy_context(), 'test_stack',
                             template.Template(hot_tpl_empty),
                             parent_resource='parent')
        stack._parent_stack = parent_stack
        self.assertEqual('Delete', self.resolve(snippet, stack.t, stack))

    def test_removed_function(self):
        snippet = {'Fn::GetAZs': ''}
        stack = parser.Stack(utils.dummy_context(), 'test_stack',
                             template.Template(hot_juno_tpl_empty))
        error = self.assertRaises(exception.InvalidTemplateVersion,
                                  function.validate,
                                  stack.t.parse(stack, snippet))
        self.assertIn(next(six.iterkeys(snippet)), six.text_type(error))

    def test_add_resource(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        resources:
          resource1:
            type: AWS::EC2::Instance
            properties:
              property1: value1
            metadata:
              foo: bar
            depends_on:
              - dummy
            deletion_policy: Retain
            update_policy:
              foo: bar
        ''')
        source = template.Template(hot_tpl)
        empty = template.Template(copy.deepcopy(hot_tpl_empty))
        stack = parser.Stack(utils.dummy_context(), 'test_stack', source)

        for defn in six.itervalues(source.resource_definitions(stack)):
            empty.add_resource(defn)

        self.assertEqual(hot_tpl['resources'], empty.t['resources'])


class HotStackTest(common.HeatTestCase):
    """Test stack function when stack was created from HOT template."""
    def setUp(self):
        super(HotStackTest, self).setUp()

        self.tmpl = template.Template(copy.deepcopy(empty_template))
        self.ctx = utils.dummy_context()

    def resolve(self, snippet):
        return function.resolve(self.stack.t.parse(self.stack, snippet))

    def test_get_attr_multiple_rsrc_status(self):
        """Test resolution of get_attr occurrences in HOT template."""

        hot_tpl = hot_tpl_generic_resource
        self.stack = parser.Stack(self.ctx, 'test_get_attr',
                                  template.Template(hot_tpl))
        self.stack.store()
        self.stack.create()
        self.assertEqual((parser.Stack.CREATE, parser.Stack.COMPLETE),
                         self.stack.state)

        snippet = {'Value': {'get_attr': ['resource1', 'foo']}}
        rsrc = self.stack['resource1']
        for action, status in (
                (rsrc.CREATE, rsrc.IN_PROGRESS),
                (rsrc.CREATE, rsrc.COMPLETE),
                (rsrc.RESUME, rsrc.IN_PROGRESS),
                (rsrc.RESUME, rsrc.COMPLETE),
                (rsrc.UPDATE, rsrc.IN_PROGRESS),
                (rsrc.UPDATE, rsrc.COMPLETE)):
            rsrc.state_set(action, status)

            # GenericResourceType has an attribute 'foo' which yields the
            # resource name.
            self.assertEqual({'Value': 'resource1'}, self.resolve(snippet))

    def test_get_attr_invalid(self):
        """Test resolution of get_attr occurrences in HOT template."""

        hot_tpl = hot_tpl_generic_resource
        self.stack = parser.Stack(self.ctx, 'test_get_attr',
                                  template.Template(hot_tpl))
        self.stack.store()
        self.stack.create()
        self.assertEqual((parser.Stack.CREATE, parser.Stack.COMPLETE),
                         self.stack.state)
        self.assertRaises(exception.InvalidTemplateAttribute,
                          self.resolve,
                          {'Value': {'get_attr': ['resource1', 'NotThere']}})

    def test_get_attr_invalid_resource(self):
        """Test resolution of get_attr occurrences in HOT template."""

        hot_tpl = hot_tpl_complex_attrs
        self.stack = parser.Stack(self.ctx,
                                  'test_get_attr_invalid_none',
                                  template.Template(hot_tpl))
        self.stack.store()
        self.stack.create()
        self.assertEqual((parser.Stack.CREATE, parser.Stack.COMPLETE),
                         self.stack.state)

        snippet = {'Value': {'get_attr': ['resource2', 'who_cares']}}
        self.assertRaises(exception.InvalidTemplateReference,
                          self.resolve, snippet)

    def test_get_resource(self):
        """Test resolution of get_resource occurrences in HOT template."""

        hot_tpl = hot_tpl_generic_resource
        self.stack = parser.Stack(self.ctx, 'test_get_resource',
                                  template.Template(hot_tpl))
        self.stack.store()
        self.stack.create()
        self.assertEqual((parser.Stack.CREATE, parser.Stack.COMPLETE),
                         self.stack.state)

        snippet = {'value': {'get_resource': 'resource1'}}
        self.assertEqual({'value': 'resource1'}, self.resolve(snippet))

    def test_set_param_id(self):
        tmpl = template.Template(hot_tpl_empty)
        self.stack = parser.Stack(self.ctx, 'param_id_test', tmpl)
        self.assertEqual('None', self.stack.parameters['OS::stack_id'])
        self.stack.store()
        stack_identifier = self.stack.identifier()
        self.assertEqual(self.stack.id, self.stack.parameters['OS::stack_id'])
        self.assertEqual(stack_identifier.stack_id,
                         self.stack.parameters['OS::stack_id'])
        self.m.VerifyAll()

    def test_set_wrong_param(self):
        tmpl = template.Template(hot_tpl_empty)
        stack_id = identifier.HeatIdentifier('', "stack_testit", None)
        params = tmpl.parameters(None, {})
        self.assertFalse(params.set_stack_id(None))
        self.assertTrue(params.set_stack_id(stack_id))

    def test_set_param_id_update(self):
        tmpl = template.Template(
            {'heat_template_version': '2013-05-23',
             'resources': {'AResource': {'type': 'ResourceWithPropsType',
                           'metadata': {'Bar': {'get_param': 'OS::stack_id'}},
                           'properties': {'Foo': 'abc'}}}})
        self.stack = parser.Stack(self.ctx, 'update_stack_id_test', tmpl)
        self.stack.store()
        self.stack.create()
        self.assertEqual((parser.Stack.CREATE, parser.Stack.COMPLETE),
                         self.stack.state)

        stack_id = self.stack.parameters['OS::stack_id']

        tmpl2 = template.Template(
            {'heat_template_version': '2013-05-23',
             'resources': {'AResource': {'type': 'ResourceWithPropsType',
                           'metadata': {'Bar': {'get_param': 'OS::stack_id'}},
                           'properties': {'Foo': 'xyz'}}}})
        updated_stack = parser.Stack(self.ctx, 'updated_stack', tmpl2)

        self.stack.update(updated_stack)
        self.assertEqual((parser.Stack.UPDATE, parser.Stack.COMPLETE),
                         self.stack.state)
        self.assertEqual('xyz', self.stack['AResource'].properties['Foo'])

        self.assertEqual(stack_id,
                         self.stack['AResource'].metadata_get()['Bar'])

    def test_load_param_id(self):
        tmpl = template.Template(hot_tpl_empty)
        self.stack = parser.Stack(self.ctx, 'param_load_id_test', tmpl)
        self.stack.store()
        stack_identifier = self.stack.identifier()
        self.assertEqual(stack_identifier.stack_id,
                         self.stack.parameters['OS::stack_id'])

        newstack = parser.Stack.load(self.ctx, stack_id=self.stack.id)
        self.assertEqual(stack_identifier.stack_id,
                         newstack.parameters['OS::stack_id'])

    def test_update_modify_param_ok_replace(self):
        tmpl = {
            'heat_template_version': '2013-05-23',
            'parameters': {
                'foo': {'type': 'string'}
            },
            'resources': {
                'AResource': {
                    'type': 'ResourceWithPropsType',
                    'properties': {'Foo': {'get_param': 'foo'}}
                }
            }
        }

        self.m.StubOutWithMock(generic_rsrc.ResourceWithProps,
                               'update_template_diff')

        self.stack = parser.Stack(self.ctx, 'update_test_stack',
                                  template.Template(
                                      tmpl, env=environment.Environment(
                                          {'foo': 'abc'})))
        self.stack.store()
        self.stack.create()
        self.assertEqual((parser.Stack.CREATE, parser.Stack.COMPLETE),
                         self.stack.state)

        updated_stack = parser.Stack(self.ctx, 'updated_stack',
                                     template.Template(
                                         tmpl, env=environment.Environment(
                                             {'foo': 'xyz'})))

        def check_props(*args):
            self.assertEqual('abc', self.stack['AResource'].properties['Foo'])

        generic_rsrc.ResourceWithProps.update_template_diff(
            {'Type': 'ResourceWithPropsType',
             'Properties': {'Foo': 'xyz'}},
            {'Type': 'ResourceWithPropsType',
             'Properties': {'Foo': 'abc'}}
        ).WithSideEffects(check_props).AndRaise(resource.UpdateReplace)
        self.m.ReplayAll()

        self.stack.update(updated_stack)
        self.assertEqual((parser.Stack.UPDATE, parser.Stack.COMPLETE),
                         self.stack.state)
        self.assertEqual('xyz', self.stack['AResource'].properties['Foo'])
        self.m.VerifyAll()

    def test_update_modify_files_ok_replace(self):
        tmpl = {
            'heat_template_version': '2013-05-23',
            'parameters': {},
            'resources': {
                'AResource': {
                    'type': 'ResourceWithPropsType',
                    'properties': {'Foo': {'get_file': 'foo'}}
                }
            }
        }

        self.m.StubOutWithMock(generic_rsrc.ResourceWithProps,
                               'update_template_diff')

        self.stack = parser.Stack(self.ctx, 'update_test_stack',
                                  template.Template(tmpl,
                                                    files={'foo': 'abc'}))
        self.stack.store()
        self.stack.create()
        self.assertEqual((parser.Stack.CREATE, parser.Stack.COMPLETE),
                         self.stack.state)

        updated_stack = parser.Stack(self.ctx, 'updated_stack',
                                     template.Template(tmpl,
                                                       files={'foo': 'xyz'}))

        def check_props(*args):
            self.assertEqual('abc', self.stack['AResource'].properties['Foo'])

        generic_rsrc.ResourceWithProps.update_template_diff(
            {'Type': 'ResourceWithPropsType',
             'Properties': {'Foo': 'xyz'}},
            {'Type': 'ResourceWithPropsType',
             'Properties': {'Foo': 'abc'}}
        ).WithSideEffects(check_props).AndRaise(resource.UpdateReplace)
        self.m.ReplayAll()

        self.stack.update(updated_stack)
        self.assertEqual((parser.Stack.UPDATE, parser.Stack.COMPLETE),
                         self.stack.state)
        self.assertEqual('xyz', self.stack['AResource'].properties['Foo'])
        self.m.VerifyAll()


class StackAttributesTest(common.HeatTestCase):
    """
    Test stack get_attr function when stack was created from HOT template.
    """
    def setUp(self):
        super(StackAttributesTest, self).setUp()

        self.ctx = utils.dummy_context()

        self.m.ReplayAll()

    scenarios = [
        ('get_flat_attr',
         dict(hot_tpl=hot_tpl_generic_resource,
              snippet={'Value': {'get_attr': ['resource1', 'foo']}},
              resource_name='resource1',
              expected={'Value': 'resource1'})),
        ('get_list_attr',
         dict(hot_tpl=hot_tpl_complex_attrs,
              snippet={'Value': {'get_attr': ['resource1', 'list', 0]}},
              resource_name='resource1',
              expected={
                  'Value':
                  generic_rsrc.ResourceWithComplexAttributes.list[0]})),
        ('get_flat_dict_attr',
         dict(hot_tpl=hot_tpl_complex_attrs,
              snippet={'Value': {'get_attr': ['resource1',
                                              'flat_dict',
                                              'key2']}},
              resource_name='resource1',
              expected={
                  'Value':
                  generic_rsrc.ResourceWithComplexAttributes.
                  flat_dict['key2']})),
        ('get_nested_attr_list',
         dict(hot_tpl=hot_tpl_complex_attrs,
              snippet={'Value': {'get_attr': ['resource1',
                                              'nested_dict',
                                              'list',
                                              0]}},
              resource_name='resource1',
              expected={
                  'Value':
                  generic_rsrc.ResourceWithComplexAttributes.
                  nested_dict['list'][0]})),
        ('get_nested_attr_dict',
         dict(hot_tpl=hot_tpl_complex_attrs,
              snippet={'Value': {'get_attr': ['resource1',
                                              'nested_dict',
                                              'dict',
                                              'a']}},
              resource_name='resource1',
              expected={
                  'Value':
                  generic_rsrc.ResourceWithComplexAttributes.
                  nested_dict['dict']['a']})),
        ('get_attr_none',
         dict(hot_tpl=hot_tpl_complex_attrs,
              snippet={'Value': {'get_attr': ['resource1',
                                              'none',
                                              'who_cares']}},
              resource_name='resource1',
              expected={'Value': None}))
    ]

    def test_get_attr(self):
        """Test resolution of get_attr occurrences in HOT template."""

        self.stack = parser.Stack(self.ctx, 'test_get_attr',
                                  template.Template(self.hot_tpl))
        self.stack.store()
        self.stack.create()
        self.assertEqual((parser.Stack.CREATE, parser.Stack.COMPLETE),
                         self.stack.state)

        rsrc = self.stack[self.resource_name]
        for action, status in (
                (rsrc.CREATE, rsrc.IN_PROGRESS),
                (rsrc.CREATE, rsrc.COMPLETE),
                (rsrc.RESUME, rsrc.IN_PROGRESS),
                (rsrc.RESUME, rsrc.COMPLETE),
                (rsrc.UPDATE, rsrc.IN_PROGRESS),
                (rsrc.UPDATE, rsrc.COMPLETE)):
            rsrc.state_set(action, status)

            resolved = function.resolve(self.stack.t.parse(self.stack,
                                                           self.snippet))
            self.assertEqual(self.expected, resolved)


class StackGetAttrValidationTest(common.HeatTestCase):

    def setUp(self):
        super(StackGetAttrValidationTest, self).setUp()
        self.ctx = utils.dummy_context()

    def test_validate_props_from_attrs(self):
        stack = parser.Stack(self.ctx, 'test_props_from_attrs',
                             template.Template(hot_tpl_mapped_props))
        stack.resources['resource1'].list = None
        stack.resources['resource1'].map = None
        stack.resources['resource1'].string = None
        try:
            stack.validate()
        except exception.StackValidationFailed as exc:
            self.fail("Validation should have passed: %s" % six.text_type(exc))
        self.assertEqual([],
                         stack.resources['resource2'].properties['a_list'])
        self.assertEqual({},
                         stack.resources['resource2'].properties['a_map'])
        self.assertEqual('',
                         stack.resources['resource2'].properties['a_string'])


class StackParametersTest(common.HeatTestCase):
    """
    Test stack get_param function when stack was created from HOT template.
    """

    scenarios = [
        ('Ref_string',
         dict(params={'foo': 'bar', 'blarg': 'wibble'},
              snippet={'properties': {'prop1': {'Ref': 'foo'},
                                      'prop2': {'Ref': 'blarg'}}},
              expected={'properties': {'prop1': 'bar',
                                       'prop2': 'wibble'}})),
        ('get_param_string',
         dict(params={'foo': 'bar', 'blarg': 'wibble'},
              snippet={'properties': {'prop1': {'get_param': 'foo'},
                                      'prop2': {'get_param': 'blarg'}}},
              expected={'properties': {'prop1': 'bar',
                                       'prop2': 'wibble'}})),
        ('get_list_attr',
         dict(params={'list': 'foo,bar'},
              snippet={'properties': {'prop1': {'get_param': ['list', 1]}}},
              expected={'properties': {'prop1': 'bar'}})),
        ('get_flat_dict_attr',
         dict(params={'flat_dict':
                      {'key1': 'val1', 'key2': 'val2', 'key3': 'val3'}},
              snippet={'properties': {'prop1': {'get_param':
                                                ['flat_dict', 'key2']}}},
              expected={'properties': {'prop1': 'val2'}})),
        ('get_nested_attr_list',
         dict(params={'nested_dict':
                      {'list': [1, 2, 3],
                       'string': 'abc',
                       'dict': {'a': 1, 'b': 2, 'c': 3}}},
              snippet={'properties': {'prop1': {'get_param':
                                                ['nested_dict',
                                                 'list',
                                                 0]}}},
              expected={'properties': {'prop1': 1}})),
        ('get_nested_attr_dict',
         dict(params={'nested_dict':
                      {'list': [1, 2, 3],
                       'string': 'abc',
                       'dict': {'a': 1, 'b': 2, 'c': 3}}},
              snippet={'properties': {'prop1': {'get_param':
                                                ['nested_dict',
                                                 'dict',
                                                 'a']}}},
              expected={'properties': {'prop1': 1}})),
        ('get_attr_none',
         dict(params={'none': None},
              snippet={'properties': {'prop1': {'get_param':
                                                ['none',
                                                 'who_cares']}}},
              expected={'properties': {'prop1': ''}})),
        ('pseudo_stack_id',
         dict(params={},
              snippet={'properties': {'prop1': {'get_param':
                                                'OS::stack_id'}}},
              expected={'properties':
                        {'prop1': '1ba8c334-2297-4312-8c7c-43763a988ced'}})),
        ('pseudo_stack_name',
         dict(params={},
              snippet={'properties': {'prop1': {'get_param':
                                                'OS::stack_name'}}},
              expected={'properties': {'prop1': 'test'}})),
        ('pseudo_project_id',
         dict(params={},
              snippet={'properties': {'prop1': {'get_param':
                                                'OS::project_id'}}},
              expected={'properties':
                        {'prop1': '9913ef0a-b8be-4b33-b574-9061441bd373'}})),

    ]

    props_template = template_format.parse('''
    heat_template_version: 2013-05-23
    parameters:
        foo:
            type: string
            default: ''
        blarg:
            type: string
            default: ''
        list:
            type: comma_delimited_list
            default: ''
        flat_dict:
            type: json
            default: {}
        nested_dict:
            type: json
            default: {}
        none:
            type: string
            default: 'default'
    ''')

    def test_param_refs(self):
        """Test if parameter references work."""
        env = environment.Environment(self.params)
        tmpl = template.Template(self.props_template, env=env)
        stack = parser.Stack(utils.dummy_context(), 'test', tmpl,
                             stack_id='1ba8c334-2297-4312-8c7c-43763a988ced',
                             tenant_id='9913ef0a-b8be-4b33-b574-9061441bd373')
        self.assertEqual(self.expected,
                         function.resolve(tmpl.parse(stack, self.snippet)))


class HOTParamValidatorTest(common.HeatTestCase):
    """Test HOTParamValidator."""

    def test_multiple_constraint_descriptions(self):
        len_desc = 'string length should be between 8 and 16'
        pattern_desc1 = 'Value must consist of characters only'
        pattern_desc2 = 'Value must start with a lowercase character'
        param = {
            'db_name': {
                'description': 'The WordPress database name',
                'type': 'string',
                'default': 'wordpress',
                'constraints': [
                    {'length': {'min': 6, 'max': 16},
                     'description': len_desc},
                    {'allowed_pattern': '[a-zA-Z]+',
                     'description': pattern_desc1},
                    {'allowed_pattern': '[a-z]+[a-zA-Z]*',
                     'description': pattern_desc2}]}}

        name = 'db_name'
        schema = param['db_name']

        def v(value):
            param_schema = hot_param.HOTParamSchema.from_dict(name, schema)
            param_schema.validate()
            param_schema.validate_value(value)
            return True

        value = 'wp'
        err = self.assertRaises(exception.StackValidationFailed, v, value)
        self.assertIn(len_desc, six.text_type(err))

        value = 'abcdefghijklmnopq'
        err = self.assertRaises(exception.StackValidationFailed, v, value)
        self.assertIn(len_desc, six.text_type(err))

        value = 'abcdefgh1'
        err = self.assertRaises(exception.StackValidationFailed, v, value)
        self.assertIn(pattern_desc1, six.text_type(err))

        value = 'Abcdefghi'
        err = self.assertRaises(exception.StackValidationFailed, v, value)
        self.assertIn(pattern_desc2, six.text_type(err))

        value = 'abcdefghi'
        self.assertTrue(v(value))

        value = 'abcdefghI'
        self.assertTrue(v(value))

    def test_hot_template_validate_param(self):
        len_desc = 'string length should be between 8 and 16'
        pattern_desc1 = 'Value must consist of characters only'
        pattern_desc2 = 'Value must start with a lowercase character'
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
          db_name:
            description: The WordPress database name
            type: string
            default: wordpress
            constraints:
              - length: { min: 8, max: 16 }
                description: %s
              - allowed_pattern: "[a-zA-Z]+"
                description: %s
              - allowed_pattern: "[a-z]+[a-zA-Z]*"
                description: %s
        ''' % (len_desc, pattern_desc1, pattern_desc2))
        tmpl = template.Template(hot_tpl)

        def run_parameters(value):
            tmpl.parameters(
                identifier.HeatIdentifier('', "stack_testit", None),
                {'db_name': value}).validate(validate_value=True)
            return True

        value = 'wp'
        err = self.assertRaises(exception.StackValidationFailed,
                                run_parameters, value)
        self.assertIn(len_desc, six.text_type(err))

        value = 'abcdefghijklmnopq'
        err = self.assertRaises(exception.StackValidationFailed,
                                run_parameters, value)
        self.assertIn(len_desc, six.text_type(err))

        value = 'abcdefgh1'
        err = self.assertRaises(exception.StackValidationFailed,
                                run_parameters, value)
        self.assertIn(pattern_desc1, six.text_type(err))

        value = 'Abcdefghi'
        err = self.assertRaises(exception.StackValidationFailed,
                                run_parameters, value)
        self.assertIn(pattern_desc2, six.text_type(err))

        value = 'abcdefghi'
        self.assertTrue(run_parameters(value))

        value = 'abcdefghI'
        self.assertTrue(run_parameters(value))

    def test_range_constraint(self):
        range_desc = 'Value must be between 30000 and 50000'
        param = {
            'db_port': {
                'description': 'The database port',
                'type': 'number',
                'default': 31000,
                'constraints': [
                    {'range': {'min': 30000, 'max': 50000},
                     'description': range_desc}]}}

        name = 'db_port'
        schema = param['db_port']

        def v(value):
            param_schema = hot_param.HOTParamSchema.from_dict(name, schema)
            param_schema.validate()
            param_schema.validate_value(value)
            return True

        value = 29999
        err = self.assertRaises(exception.StackValidationFailed, v, value)
        self.assertIn(range_desc, six.text_type(err))

        value = 50001
        err = self.assertRaises(exception.StackValidationFailed, v, value)
        self.assertIn(range_desc, six.text_type(err))

        value = 30000
        self.assertTrue(v(value))

        value = 40000
        self.assertTrue(v(value))

        value = 50000
        self.assertTrue(v(value))

    def test_custom_constraint(self):
        class ZeroConstraint(object):
            def validate(self, value, context):
                return value == "0"

        env = resources.global_env()
        env.register_constraint("zero", ZeroConstraint)
        self.addCleanup(env.constraints.pop, "zero")

        desc = 'Value must be zero'
        param = {
            'param1': {
                'type': 'string',
                'constraints': [
                    {'custom_constraint': 'zero',
                     'description': desc}]}}

        name = 'param1'
        schema = param['param1']

        def v(value):
            param_schema = hot_param.HOTParamSchema.from_dict(name, schema)
            param_schema.validate()
            param_schema.validate_value(value)
            return True

        value = "1"
        err = self.assertRaises(exception.StackValidationFailed, v, value)
        self.assertEqual(desc, six.text_type(err))

        value = "2"
        err = self.assertRaises(exception.StackValidationFailed, v, value)
        self.assertEqual(desc, six.text_type(err))

        value = "0"
        self.assertTrue(v(value))

    def test_custom_constraint_default_skip(self):
        schema = {
            'type': 'string',
            'constraints': [{
                'custom_constraint': 'skipping',
                'description': 'Must be skipped on default value'
            }],
            'default': 'foo'
        }
        param_schema = hot_param.HOTParamSchema.from_dict('p', schema)

        param_schema.validate()

    def test_range_constraint_invalid_default(self):
        range_desc = 'Value must be between 30000 and 50000'
        param = {
            'db_port': {
                'description': 'The database port',
                'type': 'number',
                'default': 15,
                'constraints': [
                    {'range': {'min': 30000, 'max': 50000},
                     'description': range_desc}]}}

        schema = hot_param.HOTParamSchema.from_dict('db_port',
                                                    param['db_port'])
        err = self.assertRaises(exception.InvalidSchemaError,
                                schema.validate)
        self.assertIn(range_desc, six.text_type(err))

    def test_validate_schema_wrong_key(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
            param1:
                foo: bar
        ''')
        error = self.assertRaises(
            exception.InvalidSchemaError, parameters.Parameters,
            "stack_testit", template.Template(hot_tpl))
        self.assertEqual("Invalid key 'foo' for parameter (param1)",
                         six.text_type(error))

    def test_validate_schema_no_type(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
            param1:
                description: Hi!
        ''')
        error = self.assertRaises(
            exception.InvalidSchemaError, parameters.Parameters,
            "stack_testit", template.Template(hot_tpl))
        self.assertEqual("Missing parameter type for parameter: param1",
                         six.text_type(error))

    def test_validate_schema_unknown_type(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
            param1:
                type: Unicode
        ''')
        error = self.assertRaises(
            exception.InvalidSchemaError, parameters.Parameters,
            "stack_testit", template.Template(hot_tpl))
        self.assertEqual(
            "Invalid type (Unicode)", six.text_type(error))

    def test_validate_schema_constraints(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
            param1:
                type: string
                constraints:
                   - allowed_valus: [foo, bar]
                default: foo
        ''')
        error = self.assertRaises(
            exception.InvalidSchemaError, parameters.Parameters,
            "stack_testit", template.Template(hot_tpl))
        self.assertEqual(
            "Invalid key 'allowed_valus' for parameter constraints",
            six.text_type(error))

    def test_validate_schema_constraints_not_list(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
            param1:
                type: string
                constraints: 1
                default: foo
        ''')
        error = self.assertRaises(
            exception.InvalidSchemaError, parameters.Parameters,
            "stack_testit", template.Template(hot_tpl))
        self.assertEqual(
            "Invalid parameter constraints for parameter param1, "
            "expected a list", six.text_type(error))

    def test_validate_schema_constraints_not_mapping(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
            param1:
                type: string
                constraints: [foo]
                default: foo
        ''')
        error = self.assertRaises(
            exception.InvalidSchemaError, parameters.Parameters,
            "stack_testit", template.Template(hot_tpl))
        self.assertEqual(
            "Invalid parameter constraints, expected a mapping",
            six.text_type(error))

    def test_validate_schema_empty_constraints(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
            param1:
                type: string
                constraints:
                    - description: a constraint
                default: foo
        ''')
        error = self.assertRaises(
            exception.InvalidSchemaError, parameters.Parameters,
            "stack_testit", template.Template(hot_tpl))
        self.assertEqual("No constraint expressed", six.text_type(error))

    def test_validate_schema_constraints_range_wrong_format(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
            param1:
                type: number
                constraints:
                   - range: foo
                default: foo
        ''')
        error = self.assertRaises(
            exception.InvalidSchemaError, parameters.Parameters,
            "stack_testit", template.Template(hot_tpl))
        self.assertEqual(
            "Invalid range constraint, expected a mapping",
            six.text_type(error))

    def test_validate_schema_constraints_range_invalid_key(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
            param1:
                type: number
                constraints:
                    - range: {min: 1, foo: bar}
                default: 1
        ''')
        error = self.assertRaises(
            exception.InvalidSchemaError, parameters.Parameters,
            "stack_testit", template.Template(hot_tpl))
        self.assertEqual(
            "Invalid key 'foo' for range constraint", six.text_type(error))

    def test_validate_schema_constraints_length_wrong_format(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
            param1:
                type: string
                constraints:
                   - length: foo
                default: foo
        ''')
        error = self.assertRaises(
            exception.InvalidSchemaError, parameters.Parameters,
            "stack_testit", template.Template(hot_tpl))
        self.assertEqual(
            "Invalid length constraint, expected a mapping",
            six.text_type(error))

    def test_validate_schema_constraints_length_invalid_key(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
            param1:
                type: string
                constraints:
                    - length: {min: 1, foo: bar}
                default: foo
        ''')
        error = self.assertRaises(
            exception.InvalidSchemaError, parameters.Parameters,
            "stack_testit", template.Template(hot_tpl))
        self.assertEqual(
            "Invalid key 'foo' for length constraint", six.text_type(error))

    def test_validate_schema_constraints_wrong_allowed_pattern(self):
        hot_tpl = template_format.parse('''
        heat_template_version: 2013-05-23
        parameters:
            param1:
                type: string
                constraints:
                    - allowed_pattern: [foo, bar]
                default: foo
        ''')
        error = self.assertRaises(
            exception.InvalidSchemaError, parameters.Parameters,
            "stack_testit", template.Template(hot_tpl))
        self.assertEqual(
            "AllowedPattern must be a string", six.text_type(error))
