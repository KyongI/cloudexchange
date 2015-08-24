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

import mock
from oslo_config import cfg

from heat.common import template_format
from heat.engine import environment
from heat.engine import resource as res
from heat.engine import stack as parser
from heat.engine import template as templatem
from heat.objects import raw_template as raw_template_object
from heat.objects import resource as resource_objects
from heat.objects import stack as stack_object
from heat.objects import sync_point as sync_point_object
from heat.rpc import worker_client
from heat.tests import common
from heat.tests.engine import tools
from heat.tests import utils


@mock.patch.object(worker_client.WorkerClient, 'check_resource')
class StackConvergenceCreateUpdateDeleteTest(common.HeatTestCase):
    def setUp(self):
        super(StackConvergenceCreateUpdateDeleteTest, self).setUp()
        cfg.CONF.set_override('convergence_engine', True)
        self.stack = None

    @mock.patch.object(parser.Stack, 'mark_complete')
    def test_converge_empty_template(self, mock_mc, mock_cr):
        empty_tmpl = templatem.Template.create_empty_template()
        stack = parser.Stack(utils.dummy_context(), 'empty_tmpl_stack',
                             empty_tmpl, convergence=True)
        stack.store()
        stack.converge_stack(template=stack.t, action=stack.CREATE)
        self.assertFalse(mock_cr.called)
        mock_mc.assert_called_once_with(stack.current_traversal)

    def test_conv_wordpress_single_instance_stack_create(self, mock_cr):
        stack = tools.get_stack('test_stack', utils.dummy_context(),
                                convergence=True)
        stack.store()  # usually, stack is stored before converge is called

        stack.converge_stack(template=stack.t, action=stack.CREATE)
        self.assertIsNone(stack.ext_rsrcs_db)
        self.assertEqual('Dependencies([((1, True), None)])',
                         repr(stack.convergence_dependencies))

        stack_db = stack_object.Stack.get_by_id(stack.context, stack.id)
        self.assertIsNotNone(stack_db.current_traversal)
        self.assertIsNotNone(stack_db.raw_template_id)

        self.assertIsNone(stack_db.prev_raw_template_id)

        self.assertEqual(stack_db.convergence, True)
        self.assertEqual({'edges': [[[1, True], None]]}, stack_db.current_deps)
        leaves = stack.convergence_dependencies.leaves()
        expected_calls = []
        for rsrc_id, is_update in leaves:
            expected_calls.append(
                mock.call.worker_client.WorkerClient.check_resource(
                    stack.context, rsrc_id, stack.current_traversal,
                    {'input_data': []},
                    is_update, None))
        self.assertEqual(expected_calls, mock_cr.mock_calls)

    def test_conv_string_five_instance_stack_create(self, mock_cr):
        stack = tools.get_stack('test_stack', utils.dummy_context(),
                                template=tools.string_template_five,
                                convergence=True)
        stack.store()
        stack.converge_stack(template=stack.t, action=stack.CREATE)
        self.assertIsNone(stack.ext_rsrcs_db)
        self.assertEqual('Dependencies(['
                         '((1, True), (3, True)), '
                         '((2, True), (3, True)), '
                         '((3, True), (4, True)), '
                         '((3, True), (5, True))])',
                         repr(stack.convergence_dependencies))

        stack_db = stack_object.Stack.get_by_id(stack.context, stack.id)
        self.assertIsNotNone(stack_db.current_traversal)
        self.assertIsNotNone(stack_db.raw_template_id)
        self.assertIsNone(stack_db.prev_raw_template_id)
        self.assertEqual(stack_db.convergence, True)
        self.assertEqual(sorted([[[3, True], [5, True]],    # C, A
                                 [[3, True], [4, True]],    # C, B
                                 [[1, True], [3, True]],    # E, C
                                 [[2, True], [3, True]]]),  # D, C
                         sorted(stack_db.current_deps['edges']))

        # check if needed_by is stored properly
        expected_needed_by = {'A': [3], 'B': [3],
                              'C': [1, 2],
                              'D': [], 'E': []}
        rsrcs_db = resource_objects.Resource.get_all_by_stack(
            stack_db._context, stack_db.id
        )
        self.assertEqual(5, len(rsrcs_db))
        for rsrc_name, rsrc_obj in rsrcs_db.items():
            self.assertEqual(sorted(expected_needed_by[rsrc_name]),
                             sorted(rsrc_obj.needed_by))
            self.assertEqual(stack_db.raw_template_id,
                             rsrc_obj.current_template_id)

        # check if sync_points were stored
        for entity_id in [5, 4, 3, 2, 1, stack_db.id]:
            sync_point = sync_point_object.SyncPoint.get_by_key(
                stack_db._context, entity_id, stack_db.current_traversal, True
            )
            self.assertIsNotNone(sync_point)
            self.assertEqual(stack_db.id, sync_point.stack_id)

        leaves = stack.convergence_dependencies.leaves()
        expected_calls = []
        for rsrc_id, is_update in leaves:
            expected_calls.append(
                mock.call.worker_client.WorkerClient.check_resource(
                    stack.context, rsrc_id, stack.current_traversal,
                    {'input_data': []},
                    is_update, None))
        self.assertEqual(expected_calls, mock_cr.mock_calls)

    def _mock_convg_db_update_requires(self, key_id=False):
        """Updates requires column of resources.
        Required for testing the generation of convergence dependency graph
        on an update.
        """
        requires = dict()
        for rsrc_id, is_update in self.stack.convergence_dependencies:
            if is_update:
                reqs = self.stack.convergence_dependencies.requires((
                    rsrc_id, is_update))
                requires[rsrc_id] = list({id for id, is_update in reqs})

        rsrcs_db = resource_objects.Resource.get_all_by_stack(
            self.stack.context, self.stack.id, key_id=key_id)

        for rsrc_id, rsrc in rsrcs_db.items():
            if rsrc.id in requires:
                rsrcs_db[rsrc_id].requires = requires[rsrc.id]
        return rsrcs_db

    def test_conv_string_five_instance_stack_update(self, mock_cr):
        stack = tools.get_stack('test_stack', utils.dummy_context(),
                                template=tools.string_template_five,
                                convergence=True)
        stack.store()
        # create stack
        stack.converge_stack(template=stack.t, action=stack.CREATE)

        curr_stack_db = stack_object.Stack.get_by_id(stack.context, stack.id)
        curr_stack = parser.Stack.load(curr_stack_db._context,
                                       stack=curr_stack_db)
        # update stack with new template
        t2 = template_format.parse(tools.string_template_five_update)
        template2 = templatem.Template(
            t2, env=environment.Environment({'KeyName2': 'test2'}))

        # on our previous create_complete, worker would have updated the
        # rsrc.requires. Mock the same behavior here.
        self.stack = stack
        with mock.patch.object(
                parser.Stack, '_db_resources_get',
                side_effect=self._mock_convg_db_update_requires):
            curr_stack.converge_stack(template=template2, action=stack.UPDATE)

        self.assertIsNotNone(curr_stack.ext_rsrcs_db)
        self.assertEqual('Dependencies(['
                         '((3, False), (1, False)), '
                         '((3, False), (2, False)), '
                         '((4, False), (3, False)), '
                         '((4, False), (4, True)), '
                         '((5, False), (3, False)), '
                         '((5, False), (5, True)), '
                         '((6, True), (8, True)), '
                         '((7, True), (8, True)), '
                         '((8, True), (4, True)), '
                         '((8, True), (5, True))])',
                         repr(curr_stack.convergence_dependencies))

        stack_db = stack_object.Stack.get_by_id(curr_stack.context,
                                                curr_stack.id)
        self.assertIsNotNone(stack_db.raw_template_id)
        self.assertIsNotNone(stack_db.current_traversal)
        self.assertIsNotNone(stack_db.prev_raw_template_id)
        self.assertEqual(True, stack_db.convergence)
        self.assertEqual(sorted([[[7, True], [8, True]],
                                 [[8, True], [5, True]],
                                 [[8, True], [4, True]],
                                 [[6, True], [8, True]],
                                 [[3, False], [2, False]],
                                 [[3, False], [1, False]],
                                 [[5, False], [3, False]],
                                 [[5, False], [5, True]],
                                 [[4, False], [3, False]],
                                 [[4, False], [4, True]]]),
                         sorted(stack_db.current_deps['edges']))
        '''
        To visualize:

        G(7, True)       H(6, True)
            \                 /
              \             /           B(4, False)   A(5, False)
                \         /               /       \  /    /
                  \     /            /           /
               F(8, True)       /             /     \  /
                    /  \    /             /     C(3, False)
                  /      \            /            /    \
                /     /    \      /
              /    /         \ /                /          \
        B(4, True)      A(5, True)       D(2, False)    E(1, False)

        Leaves are at the bottom
        '''

        # check if needed_by are stored properly
        # For A & B:
        # needed_by=C, F

        expected_needed_by = {'A': [3, 8], 'B': [3, 8],
                              'C': [1, 2],
                              'D': [], 'E': [],
                              'F': [6, 7],
                              'G': [], 'H': []}
        rsrcs_db = resource_objects.Resource.get_all_by_stack(
            stack_db._context, stack_db.id
        )
        self.assertEqual(8, len(rsrcs_db))
        for rsrc_name, rsrc_obj in rsrcs_db.items():
            self.assertEqual(sorted(expected_needed_by[rsrc_name]),
                             sorted(rsrc_obj.needed_by))

        # check if sync_points are created for forward traversal
        # [F, H, G, A, B, Stack]
        for entity_id in [8, 7, 6, 5, 4, stack_db.id]:
            sync_point = sync_point_object.SyncPoint.get_by_key(
                stack_db._context, entity_id, stack_db.current_traversal, True
            )
            self.assertIsNotNone(sync_point)
            self.assertEqual(stack_db.id, sync_point.stack_id)

        # check if sync_points are created for cleanup traversal
        # [A, B, C, D, E]
        for entity_id in [5, 4, 3, 2, 1]:
            sync_point = sync_point_object.SyncPoint.get_by_key(
                stack_db._context, entity_id, stack_db.current_traversal, False
            )
            self.assertIsNotNone(sync_point)
            self.assertEqual(stack_db.id, sync_point.stack_id)

        leaves = stack.convergence_dependencies.leaves()
        expected_calls = []
        for rsrc_id, is_update in leaves:
            expected_calls.append(
                mock.call.worker_client.WorkerClient.check_resource(
                    stack.context, rsrc_id, stack.current_traversal,
                    {'input_data': []},
                    is_update, None))

        leaves = curr_stack.convergence_dependencies.leaves()
        for rsrc_id, is_update in leaves:
            expected_calls.append(
                mock.call.worker_client.WorkerClient.check_resource(
                    curr_stack.context, rsrc_id, curr_stack.current_traversal,
                    {'input_data': []},
                    is_update, None))
        self.assertEqual(expected_calls, mock_cr.mock_calls)

    def test_conv_empty_template_stack_update_delete(self, mock_cr):
        stack = tools.get_stack('test_stack', utils.dummy_context(),
                                template=tools.string_template_five,
                                convergence=True)
        stack.store()
        # create stack
        stack.converge_stack(template=stack.t, action=stack.CREATE)

        # update stack with new template
        template2 = templatem.Template.create_empty_template(
            version=stack.t.version)

        curr_stack_db = stack_object.Stack.get_by_id(stack.context, stack.id)
        curr_stack = parser.Stack.load(curr_stack_db._context,
                                       stack=curr_stack_db)
        # on our previous create_complete, worker would have updated the
        # rsrc.requires. Mock the same behavior here.
        self.stack = stack
        with mock.patch.object(
                parser.Stack, '_db_resources_get',
                side_effect=self._mock_convg_db_update_requires):
            curr_stack.converge_stack(template=template2, action=stack.DELETE)

        self.assertIsNotNone(curr_stack.ext_rsrcs_db)
        self.assertEqual('Dependencies(['
                         '((3, False), (1, False)), '
                         '((3, False), (2, False)), '
                         '((4, False), (3, False)), '
                         '((5, False), (3, False))])',
                         repr(curr_stack.convergence_dependencies))

        stack_db = stack_object.Stack.get_by_id(curr_stack.context,
                                                curr_stack.id)
        self.assertIsNotNone(stack_db.current_traversal)
        self.assertIsNotNone(stack_db.prev_raw_template_id)
        self.assertEqual(sorted([[[3, False], [2, False]],
                                 [[3, False], [1, False]],
                                 [[5, False], [3, False]],
                                 [[4, False], [3, False]]]),
                         sorted(stack_db.current_deps['edges']))

        expected_needed_by = {'A': [3], 'B': [3],
                              'C': [1, 2],
                              'D': [], 'E': []}
        rsrcs_db = resource_objects.Resource.get_all_by_stack(
            stack_db._context, stack_db.id
        )
        self.assertEqual(5, len(rsrcs_db))
        for rsrc_name, rsrc_obj in rsrcs_db.items():
            self.assertEqual(sorted(expected_needed_by[rsrc_name]),
                             sorted(rsrc_obj.needed_by))

        # check if sync_points are created for cleanup traversal
        # [A, B, C, D, E, Stack]
        for entity_id in [5, 4, 3, 2, 1, stack_db.id]:
            is_update = False
            if entity_id == stack_db.id:
                is_update = True
            sync_point = sync_point_object.SyncPoint.get_by_key(
                stack_db._context, entity_id, stack_db.current_traversal,
                is_update)
            self.assertIsNotNone(sync_point, 'entity %s' % entity_id)
            self.assertEqual(stack_db.id, sync_point.stack_id)

        leaves = stack.convergence_dependencies.leaves()
        expected_calls = []
        for rsrc_id, is_update in leaves:
            expected_calls.append(
                mock.call.worker_client.WorkerClient.check_resource(
                    stack.context, rsrc_id, stack.current_traversal,
                    {'input_data': []},
                    is_update, None))

        leaves = curr_stack.convergence_dependencies.leaves()
        for rsrc_id, is_update in leaves:
            expected_calls.append(
                mock.call.worker_client.WorkerClient.check_resource(
                    curr_stack.context, rsrc_id, curr_stack.current_traversal,
                    {'input_data': []},
                    is_update, None))
        self.assertEqual(expected_calls, mock_cr.mock_calls)

    def test_mark_complete_purges_db(self, mock_cr):
        stack = tools.get_stack('test_stack', utils.dummy_context(),
                                template=tools.string_template_five,
                                convergence=True)
        stack.store()
        stack.purge_db = mock.Mock()
        stack.mark_complete(stack.current_traversal)
        self.assertTrue(stack.purge_db.called)

    @mock.patch.object(raw_template_object.RawTemplate, 'delete')
    def test_purge_db_deletes_previous_template(self, mock_tmpl_delete,
                                                mock_cr):
        stack = tools.get_stack('test_stack', utils.dummy_context(),
                                template=tools.string_template_five,
                                convergence=True)
        stack.prev_raw_template_id = 10
        stack.purge_db()
        self.assertTrue(mock_tmpl_delete.called)

    @mock.patch.object(raw_template_object.RawTemplate, 'delete')
    def test_purge_db_does_not_delete_previous_template_when_stack_fails(
            self, mock_tmpl_delete, mock_cr):
        stack = tools.get_stack('test_stack', utils.dummy_context(),
                                template=tools.string_template_five,
                                convergence=True)
        stack.status = stack.FAILED
        stack.purge_db()
        self.assertFalse(mock_tmpl_delete.called)

    def test_purge_db_deletes_sync_points(self, mock_cr):
        stack = tools.get_stack('test_stack', utils.dummy_context(),
                                template=tools.string_template_five,
                                convergence=True)
        stack.store()
        stack.purge_db()
        rows = sync_point_object.SyncPoint.delete_all_by_stack_and_traversal(
            stack.context, stack.id, stack.current_traversal)
        self.assertEqual(0, rows)

    @mock.patch.object(stack_object.Stack, 'delete')
    def test_purge_db_deletes_stack_for_deleted_stack(self, mock_stack_delete,
                                                      mock_cr):
        stack = tools.get_stack('test_stack', utils.dummy_context(),
                                template=tools.string_template_five,
                                convergence=True)
        stack.store()
        stack.state_set(stack.DELETE, stack.COMPLETE, 'test reason')
        stack.purge_db()
        self.assertTrue(mock_stack_delete.called)

    def test_get_best_existing_db_resource(self, mock_cr):
        stack = tools.get_stack('test_stack', utils.dummy_context(),
                                template=tools.string_template_five,
                                convergence=True)
        stack.store()
        stack.prev_raw_template_id = 2
        stack.t.id = 1
        dummy_res = stack.resources['A']
        a_res_2 = res.Resource('A', dummy_res.t, stack)
        a_res_2.current_template_id = 2
        a_res_2.id = 2
        a_res_3 = res.Resource('A', dummy_res.t, stack)
        a_res_3.current_template_id = 3
        a_res_3.id = 3
        a_res_1 = res.Resource('A', dummy_res.t, stack)
        a_res_1.current_template_id = 1
        a_res_1.id = 1
        existing_res = {2: a_res_2,
                        3: a_res_3,
                        1: a_res_1}
        stack.ext_rsrcs_db = existing_res
        best_res = stack._get_best_existing_rsrc_db('A')
        # should return resource with template id 1 which is current template
        self.assertEqual(a_res_1.id, best_res.id)

        # no resource with current template id as 1
        existing_res = {2: a_res_2,
                        3: a_res_3}
        stack.ext_rsrcs_db = existing_res
        best_res = stack._get_best_existing_rsrc_db('A')
        # should return resource with template id 2 which is prev template
        self.assertEqual(a_res_2.id, best_res.id)


class TestConvgStackRollback(common.HeatTestCase):

    def setUp(self):
        super(TestConvgStackRollback, self).setUp()
        self.ctx = utils.dummy_context()
        self.stack = tools.get_stack('test_stack_rollback', self.ctx,
                                     template=tools.string_template_five,
                                     convergence=True)

    def test_trigger_rollback_uses_old_template_if_available(self):
        # create a template and assign to stack as previous template
        t = template_format.parse(tools.wp_template)
        prev_tmpl = templatem.Template(t)
        prev_tmpl.store(context=self.ctx)
        self.stack.prev_raw_template_id = prev_tmpl.id
        # mock failure
        self.stack.action = self.stack.UPDATE
        self.stack.status = self.stack.FAILED
        self.stack.store()
        # mock converge_stack()
        self.stack.converge_stack = mock.Mock()
        # call trigger_rollbac
        self.stack.rollback()

        # Make sure stack converge is called with previous template
        self.assertTrue(self.stack.converge_stack.called)
        self.assertIsNone(self.stack.prev_raw_template_id)
        call_args, call_kwargs = self.stack.converge_stack.call_args
        template_used_for_rollback = call_args[0]
        self.assertEqual(prev_tmpl.id, template_used_for_rollback.id)

    def test_trigger_rollback_uses_empty_template_if_prev_tmpl_not_available(
            self):
        # mock create failure with no previous template
        self.stack.prev_raw_template_id = None
        self.stack.action = self.stack.CREATE
        self.stack.status = self.stack.FAILED
        self.stack.store()
        # mock converge_stack()
        self.stack.converge_stack = mock.Mock()
        # call trigger_rollback
        self.stack.rollback()

        # Make sure stack converge is called with empty template
        self.assertTrue(self.stack.converge_stack.called)
        call_args, call_kwargs = self.stack.converge_stack.call_args
        template_used_for_rollback = call_args[0]
        self.assertEqual({}, template_used_for_rollback['resources'])


class TestConvgComputeDependencies(common.HeatTestCase):
    def setUp(self):
        super(TestConvgComputeDependencies, self).setUp()
        self.ctx = utils.dummy_context()
        self.stack = tools.get_stack('test_stack_convg', self.ctx,
                                     template=tools.string_template_five,
                                     convergence=True)

    def _fake_db_resources(self, stack):
        db_resources = {}
        i = 0
        for rsrc_name in ['E', 'D', 'C', 'B', 'A']:
            i += 1
            rsrc = mock.MagicMock()
            rsrc.id = i
            rsrc.name = rsrc_name
            rsrc.current_template_id = stack.prev_raw_template_id
            db_resources[i] = rsrc
        db_resources[3].requires = [4, 5]
        db_resources[1].requires = [3]
        db_resources[2].requires = [3]
        return db_resources

    def test_dependencies_create_stack_without_mock(self):
        self.stack.store()
        self.current_resources = self.stack._update_or_store_resources()
        self.stack._compute_convg_dependencies(self.stack.ext_rsrcs_db,
                                               self.stack.dependencies,
                                               self.current_resources)
        self.assertEqual('Dependencies(['
                         '((1, True), (3, True)), '
                         '((2, True), (3, True)), '
                         '((3, True), (4, True)), '
                         '((3, True), (5, True))])',
                         repr(self.stack._convg_deps))

    def test_dependencies_update_same_template(self):
        t = template_format.parse(tools.string_template_five)
        tmpl = templatem.Template(t)
        self.stack.t = tmpl
        self.stack.t.id = 2
        self.stack.prev_raw_template_id = 1
        db_resources = self._fake_db_resources(self.stack)
        curr_resources = {res.name: res for id, res in db_resources.items()}
        self.stack._compute_convg_dependencies(db_resources,
                                               self.stack.dependencies,
                                               curr_resources)
        self.assertEqual('Dependencies(['
                         '((1, False), (1, True)), '
                         '((1, True), (3, True)), '
                         '((2, False), (2, True)), '
                         '((2, True), (3, True)), '
                         '((3, False), (1, False)), '
                         '((3, False), (2, False)), '
                         '((3, False), (3, True)), '
                         '((3, True), (4, True)), '
                         '((3, True), (5, True)), '
                         '((4, False), (3, False)), '
                         '((4, False), (4, True)), '
                         '((5, False), (3, False)), '
                         '((5, False), (5, True))])',
                         repr(self.stack._convg_deps))

    def test_dependencies_update_new_template(self):
        t = template_format.parse(tools.string_template_five_update)
        tmpl = templatem.Template(t)
        self.stack.t = tmpl
        self.stack.t.id = 2
        self.stack.prev_raw_template_id = 1
        db_resources = self._fake_db_resources(self.stack)

        curr_resources = {res.name: res for id, res in db_resources.items()}
        # 'H', 'G', 'F' are part of new template
        i = len(db_resources)
        for new_rsrc in ['H', 'G', 'F']:
            i += 1
            rsrc = mock.MagicMock()
            rsrc.name = new_rsrc
            rsrc.id = i
            curr_resources[new_rsrc] = rsrc

        self.stack._compute_convg_dependencies(db_resources,
                                               self.stack.dependencies,
                                               curr_resources)
        self.assertEqual('Dependencies(['
                         '((3, False), (1, False)), '
                         '((3, False), (2, False)), '
                         '((4, False), (3, False)), '
                         '((4, False), (4, True)), '
                         '((5, False), (3, False)), '
                         '((5, False), (5, True)), '
                         '((6, True), (8, True)), '
                         '((7, True), (8, True)), '
                         '((8, True), (4, True)), '
                         '((8, True), (5, True))])',
                         repr(self.stack._convg_deps))

    def test_dependencies_update_replace_rollback(self):
        t = template_format.parse(tools.string_template_five)
        tmpl = templatem.Template(t)
        self.stack.t = tmpl
        self.stack.t.id = 1
        self.stack.prev_raw_template_id = 2
        db_resources = self._fake_db_resources(self.stack)

        # previous resource E still exists in db.
        db_resources[1].current_template_id = 1
        # resource that replaced E
        res = mock.MagicMock()
        res.id = 6
        res.name = 'E'
        res.requires = [3]
        res.replaces = 1
        res.current_template_id = 2
        db_resources[6] = res

        curr_resources = {res.name: res for id, res in db_resources.items()}
        # best existing resource
        curr_resources['E'] = db_resources[1]
        self.stack._compute_convg_dependencies(db_resources,
                                               self.stack.dependencies,
                                               curr_resources)
        self.assertEqual('Dependencies(['
                         '((1, False), (1, True)), '
                         '((1, False), (6, False)), '
                         '((1, True), (3, True)), '
                         '((2, False), (2, True)), '
                         '((2, True), (3, True)), '
                         '((3, False), (1, False)), '
                         '((3, False), (2, False)), '
                         '((3, False), (3, True)), '
                         '((3, False), (6, False)), '
                         '((3, True), (4, True)), '
                         '((3, True), (5, True)), '
                         '((4, False), (3, False)), '
                         '((4, False), (4, True)), '
                         '((5, False), (3, False)), '
                         '((5, False), (5, True))])',
                         repr(self.stack._convg_deps))

    def test_dependencies_update_delete(self):
        tmpl = templatem.Template.create_empty_template(
            version=self.stack.t.version)
        self.stack.t = tmpl
        self.stack.t.id = 2
        self.stack.prev_raw_template_id = 1
        db_resources = self._fake_db_resources(self.stack)
        curr_resources = {res.name: res for id, res in db_resources.items()}
        self.stack._compute_convg_dependencies(db_resources,
                                               self.stack.dependencies,
                                               curr_resources)
        self.assertEqual('Dependencies(['
                         '((3, False), (1, False)), '
                         '((3, False), (2, False)), '
                         '((4, False), (3, False)), '
                         '((5, False), (3, False))])',
                         repr(self.stack._convg_deps))
