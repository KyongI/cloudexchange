# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock

from heat.common import exception
from heat.engine import resource
from heat.engine import scheduler
from heat.engine import stack
from heat.engine import sync_point
from heat.engine import worker
from heat.rpc import worker_client
from heat.tests import common
from heat.tests.engine import tools
from heat.tests import utils


class WorkerServiceTest(common.HeatTestCase):
    def setUp(self):
        super(WorkerServiceTest, self).setUp()

    def test_make_sure_rpc_version(self):
        self.assertEqual(
            '1.2',
            worker.WorkerService.RPC_API_VERSION,
            ('RPC version is changed, please update this test to new version '
             'and make sure additional test cases are added for RPC APIs '
             'added in new version'))

    @mock.patch('heat.common.messaging.get_rpc_server',
                return_value=mock.Mock())
    @mock.patch('oslo_messaging.Target',
                return_value=mock.Mock())
    @mock.patch('heat.rpc.worker_client.WorkerClient',
                return_value=mock.Mock())
    def test_service_start(self,
                           rpc_client_class,
                           target_class,
                           rpc_server_method
                           ):
        self.worker = worker.WorkerService('host-1',
                                           'topic-1',
                                           'engine_id',
                                           mock.Mock())

        self.worker.start()

        # Make sure target is called with proper parameters
        target_class.assert_called_once_with(
            version=worker.WorkerService.RPC_API_VERSION,
            server=self.worker.host,
            topic=self.worker.topic)

        # Make sure rpc server creation with proper target
        # and WorkerService is initialized with it
        target = target_class.return_value
        rpc_server_method.assert_called_once_with(target,
                                                  self.worker)
        rpc_server = rpc_server_method.return_value
        self.assertEqual(rpc_server,
                         self.worker._rpc_server,
                         "Failed to create RPC server")

        # Make sure rpc server is started.
        rpc_server.start.assert_called_once_with()

        # Make sure rpc client is created and initialized in WorkerService
        rpc_client = rpc_client_class.return_value
        rpc_client_class.assert_called_once_with()
        self.assertEqual(rpc_client,
                         self.worker._rpc_client,
                         "Failed to create RPC client")

    def test_service_stop(self):
        self.worker = worker.WorkerService('host-1',
                                           'topic-1',
                                           'engine_id',
                                           mock.Mock())
        with mock.patch.object(self.worker, '_rpc_server') as mock_rpc_server:
            self.worker.stop()
            mock_rpc_server.stop.assert_called_once_with()
            mock_rpc_server.wait.assert_called_once_with()


@mock.patch.object(worker, 'construct_input_data')
@mock.patch.object(worker, 'check_stack_complete')
@mock.patch.object(worker, 'propagate_check_resource')
@mock.patch.object(worker, 'check_resource_cleanup')
@mock.patch.object(worker, 'check_resource_update')
class CheckWorkflowUpdateTest(common.HeatTestCase):
    @mock.patch.object(worker_client.WorkerClient, 'check_resource',
                       lambda *_: None)
    def setUp(self):
        super(CheckWorkflowUpdateTest, self).setUp()
        thread_group_mgr = mock.Mock()
        self.worker = worker.WorkerService('host-1',
                                           'topic-1',
                                           'engine_id',
                                           thread_group_mgr)
        self.worker._rpc_client = worker_client.WorkerClient()
        self.ctx = utils.dummy_context()
        self.stack = tools.get_stack(
            'check_workflow_create_stack', self.ctx,
            template=tools.string_template_five, convergence=True)
        self.stack.converge_stack(self.stack.t)
        self.resource = self.stack['A']
        self.is_update = True
        self.graph_key = (self.resource.id, self.is_update)
        self.orig_load_method = stack.Stack.load
        stack.Stack.load = mock.Mock(return_value=self.stack)

    def tearDown(self):
        super(CheckWorkflowUpdateTest, self).tearDown()
        stack.Stack.load = self.orig_load_method

    def test_resource_not_available(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        self.worker.check_resource(
            self.ctx, 'non-existant-id', self.stack.current_traversal, {},
            True, None)
        for mocked in [mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid]:
            self.assertFalse(mocked.called)

    def test_stale_traversal(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        self.worker.check_resource(self.ctx, self.resource.id,
                                   'stale-traversal', {}, True, None)
        for mocked in [mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid]:
            self.assertFalse(mocked.called)

    def test_is_update_traversal(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        self.worker.check_resource(
            self.ctx, self.resource.id, self.stack.current_traversal, {},
            self.is_update, None)
        mock_cru.assert_called_once_with(self.resource,
                                         self.resource.stack.t.id,
                                         {}, self.worker.engine_id,
                                         mock.ANY)
        self.assertFalse(mock_crc.called)

        expected_calls = []
        for req, fwd in self.stack.convergence_dependencies.leaves():
            expected_calls.append(
                (mock.call.worker.propagate_check_resource.
                    assert_called_once_with(
                        self.ctx, mock.ANY, mock.ANY,
                        self.stack.current_traversal, mock.ANY,
                        self.graph_key, {}, self.is_update)))
        mock_csc.assert_called_once_with(
            self.ctx, mock.ANY, self.stack.current_traversal,
            self.resource.id,
            mock.ANY, True)

    @mock.patch.object(resource.Resource, 'make_replacement')
    def test_is_update_traversal_raise_update_replace(
            self, mock_mr, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        mock_cru.side_effect = resource.UpdateReplace
        self.worker.check_resource(
            self.ctx, self.resource.id, self.stack.current_traversal, {},
            self.is_update, None)
        mock_cru.assert_called_once_with(self.resource,
                                         self.resource.stack.t.id,
                                         {}, self.worker.engine_id,
                                         self.stack.timeout_secs())
        self.assertTrue(mock_mr.called)
        self.assertFalse(mock_crc.called)
        self.assertFalse(mock_pcr.called)
        self.assertFalse(mock_csc.called)

    @mock.patch.object(worker.WorkerService, '_try_steal_engine_lock')
    def test_is_update_traversal_raise_update_inprogress(
            self, mock_tsl, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        mock_cru.side_effect = resource.UpdateInProgress
        self.worker.engine_id = 'some-thing-else'
        mock_tsl.return_value = True
        self.worker.check_resource(
            self.ctx, self.resource.id, self.stack.current_traversal, {},
            self.is_update, None)
        mock_cru.assert_called_once_with(self.resource,
                                         self.resource.stack.t.id,
                                         {}, self.worker.engine_id,
                                         self.stack.timeout_secs())
        self.assertFalse(mock_crc.called)
        self.assertFalse(mock_pcr.called)
        self.assertFalse(mock_csc.called)

    def test_try_steal_lock_alive(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        res = self.worker._try_steal_engine_lock(self.ctx,
                                                 self.resource.id)
        self.assertFalse(res)

    @mock.patch.object(worker.listener_client, 'EngineListenerClient')
    @mock.patch.object(worker.resource_objects.Resource, 'get_obj')
    def test_try_steal_lock_dead(
            self, mock_get, mock_elc, mock_cru, mock_crc, mock_pcr,
            mock_csc, mock_cid):
        fake_res = mock.Mock()
        fake_res.engine_id = 'some-thing-else'
        mock_get.return_value = fake_res
        mock_elc.return_value.is_alive.return_value = False
        res = self.worker._try_steal_engine_lock(self.ctx,
                                                 self.resource.id)
        self.assertTrue(res)

    @mock.patch.object(worker.listener_client, 'EngineListenerClient')
    @mock.patch.object(worker.resource_objects.Resource, 'get_obj')
    def test_try_steal_lock_not_dead(
            self, mock_get, mock_elc, mock_cru, mock_crc, mock_pcr,
            mock_csc, mock_cid):
        fake_res = mock.Mock()
        fake_res.engine_id = self.worker.engine_id
        mock_get.return_value = fake_res
        mock_elc.return_value.is_alive.return_value = True
        res = self.worker._try_steal_engine_lock(self.ctx,
                                                 self.resource.id)
        self.assertFalse(res)

    def test_resource_update_failure_sets_stack_state_as_failed(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        self.stack.state_set(self.stack.UPDATE, self.stack.IN_PROGRESS, '')
        self.resource.state_set(self.resource.UPDATE,
                                self.resource.IN_PROGRESS)
        self.worker._trigger_rollback = mock.Mock()
        dummy_ex = exception.ResourceNotAvailable(
            resource_name=self.resource.name)
        mock_cru.side_effect = exception.ResourceFailure(
            dummy_ex, self.resource, action=self.resource.UPDATE)
        self.worker.check_resource(self.ctx, self.resource.id,
                                   self.stack.current_traversal, {},
                                   self.is_update, None)
        s = self.stack.load(self.ctx, stack_id=self.stack.id)
        self.assertEqual((s.UPDATE, s.FAILED), (s.action, s.status))
        self.assertEqual('Resource UPDATE failed: '
                         'ResourceNotAvailable: resources.A: The Resource (A)'
                         ' is not available.', s.status_reason)

    def test_resource_cleanup_failure_sets_stack_state_as_failed(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        self.is_update = False  # invokes check_resource_cleanup
        self.stack.state_set(self.stack.UPDATE, self.stack.IN_PROGRESS, '')
        self.resource.state_set(self.resource.UPDATE,
                                self.resource.IN_PROGRESS)
        self.worker._trigger_rollback = mock.Mock()
        dummy_ex = exception.ResourceNotAvailable(
            resource_name=self.resource.name)
        mock_crc.side_effect = exception.ResourceFailure(
            dummy_ex, self.resource, action=self.resource.UPDATE)
        self.worker.check_resource(self.ctx, self.resource.id,
                                   self.stack.current_traversal, {},
                                   self.is_update, None)
        s = self.stack.load(self.ctx, stack_id=self.stack.id)
        self.assertEqual((s.UPDATE, s.FAILED), (s.action, s.status))
        self.assertEqual('Resource UPDATE failed: '
                         'ResourceNotAvailable: resources.A: The Resource (A)'
                         ' is not available.', s.status_reason)

    def test_resource_update_failure_triggers_rollback_if_enabled(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        self.stack.disable_rollback = False
        self.stack.store()
        self.worker._trigger_rollback = mock.Mock()
        dummy_ex = exception.ResourceNotAvailable(
            resource_name=self.resource.name)
        mock_cru.side_effect = exception.ResourceFailure(
            dummy_ex, self.resource, action=self.resource.UPDATE)
        self.worker.check_resource(self.ctx, self.resource.id,
                                   self.stack.current_traversal, {},
                                   self.is_update, None)
        self.assertTrue(self.worker._trigger_rollback.called)
        # make sure the rollback is called on given stack
        call_args, call_kwargs = self.worker._trigger_rollback.call_args
        called_stack = call_args[0]
        self.assertEqual(self.stack.id, called_stack.id)

    def test_resource_cleanup_failure_triggers_rollback_if_enabled(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        self.is_update = False  # invokes check_resource_cleanup
        self.stack.disable_rollback = False
        self.stack.store()
        self.worker._trigger_rollback = mock.Mock()
        dummy_ex = exception.ResourceNotAvailable(
            resource_name=self.resource.name)
        mock_crc.side_effect = exception.ResourceFailure(
            dummy_ex, self.resource, action=self.resource.UPDATE)
        self.worker.check_resource(self.ctx, self.resource.id,
                                   self.stack.current_traversal, {},
                                   self.is_update, None)
        self.assertTrue(self.worker._trigger_rollback.called)
        # make sure the rollback is called on given stack
        call_args, call_kwargs = self.worker._trigger_rollback.call_args
        called_stack = call_args[0]
        self.assertEqual(self.stack.id, called_stack.id)

    def test_rollback_is_not_triggered_on_rollback_disabled_stack(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        self.stack.disable_rollback = True
        self.stack.store()
        self.worker._trigger_rollback = mock.Mock()
        dummy_ex = exception.ResourceNotAvailable(
            resource_name=self.resource.name)
        mock_cru.side_effect = exception.ResourceFailure(
            dummy_ex, self.resource, action=self.stack.CREATE)
        self.worker.check_resource(self.ctx, self.resource.id,
                                   self.stack.current_traversal, {},
                                   self.is_update, None)
        self.assertFalse(self.worker._trigger_rollback.called)

    def test_rollback_not_re_triggered_for_a_rolling_back_stack(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        self.stack.disable_rollback = False
        self.stack.action = self.stack.ROLLBACK
        self.stack.status = self.stack.IN_PROGRESS
        self.stack.store()
        self.worker._trigger_rollback = mock.MagicMock()
        dummy_ex = exception.ResourceNotAvailable(
            resource_name=self.resource.name)
        mock_cru.side_effect = exception.ResourceFailure(
            dummy_ex, self.resource, action=self.stack.CREATE)
        self.worker.check_resource(self.ctx, self.resource.id,
                                   self.stack.current_traversal, {},
                                   self.is_update, None)
        self.assertFalse(self.worker._trigger_rollback.called)

    def test_resource_update_failure_purges_db_for_stack_failure(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        self.stack.disable_rollback = True
        self.stack.store()
        self.stack.purge_db = mock.Mock()
        dummy_ex = exception.ResourceNotAvailable(
            resource_name=self.resource.name)
        mock_cru.side_effect = exception.ResourceFailure(
            dummy_ex, self.resource, action=self.resource.UPDATE)
        self.worker.check_resource(self.ctx, self.resource.id,
                                   self.stack.current_traversal, {},
                                   self.is_update, None)
        self.assertTrue(self.stack.purge_db.called)

    def test_resource_cleanup_failure_purges_db_for_stack_failure(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        self.is_update = False
        self.stack.disable_rollback = True
        self.stack.store()
        self.stack.purge_db = mock.Mock()
        dummy_ex = exception.ResourceNotAvailable(
            resource_name=self.resource.name)
        mock_crc.side_effect = exception.ResourceFailure(
            dummy_ex, self.resource, action=self.resource.UPDATE)
        self.worker.check_resource(self.ctx, self.resource.id,
                                   self.stack.current_traversal, {},
                                   self.is_update, None)
        self.assertTrue(self.stack.purge_db.called)

    @mock.patch.object(worker.WorkerService, '_retrigger_check_resource')
    @mock.patch.object(stack.Stack, 'load')
    def test_initiate_propagate_rsrc_retriggers_check_rsrc_on_new_stack_update(
            self, mock_stack_load, mock_rcr, mock_cru, mock_crc, mock_pcr,
            mock_csc, mock_cid):
        key = sync_point.make_key(self.resource.id,
                                  self.stack.current_traversal,
                                  self.is_update)
        mock_pcr.side_effect = sync_point.SyncPointNotFound(key)
        updated_stack = stack.Stack(self.ctx, self.stack.name, self.stack.t,
                                    self.stack.id,
                                    current_traversal='some_newy_trvl_uuid')
        mock_stack_load.return_value = updated_stack
        self.worker._initiate_propagate_resource(self.ctx, self.resource.id,
                                                 self.stack.current_traversal,
                                                 self.is_update, self.resource,
                                                 self.stack)
        mock_rcr.assert_called_once_with(self.ctx, self.is_update,
                                         self.resource.id, updated_stack)

    @mock.patch.object(sync_point, 'sync')
    def test_retrigger_check_resource(self, mock_sync, mock_cru, mock_crc,
                                      mock_pcr, mock_csc, mock_cid):
        self.is_update = True
        resC = self.stack['C']
        expected_graph_key = (resC.id, self.is_update)
        # A, B are predecessors to C when is_update is True
        expected_predecessors = {(self.stack['A'].id, True),
                                 (self.stack['B'].id, True)}
        self.worker._retrigger_check_resource(self.ctx, self.is_update,
                                              resC.id, self.stack)
        mock_sync.assert_called_once_with(self.ctx, resC.id,
                                          self.stack.current_traversal,
                                          self.is_update, mock.ANY,
                                          mock.ANY,
                                          {expected_graph_key: None})
        call_args, call_kwargs = mock_sync.call_args
        actual_predecessors = call_args[5]
        self.assertItemsEqual(expected_predecessors, actual_predecessors)

    @mock.patch.object(stack.Stack, 'purge_db')
    def test_handle_failure(self, mock_purgedb, mock_cru, mock_crc, mock_pcr,
                            mock_csc, mock_cid):
        self.worker._handle_failure(self.ctx, self.stack, 'dummy-reason')
        mock_purgedb.assert_called_once_with()
        self.assertEqual('dummy-reason', self.stack.status_reason)

        # test with rollback
        self.worker._trigger_rollback = mock.Mock()
        self.stack.disable_rollback = False
        self.stack.state_set(self.stack.UPDATE, self.stack.IN_PROGRESS, '')
        self.worker._handle_failure(self.ctx, self.stack, 'dummy-reason')
        self.worker._trigger_rollback.assert_called_once_with(self.stack)

    def test_handle_stack_timeout(self, mock_cru, mock_crc, mock_pcr,
                                  mock_csc, mock_cid):
        self.worker._handle_failure = mock.Mock()
        self.worker._handle_stack_timeout(self.ctx, self.stack)
        self.worker._handle_failure.assert_called_once_with(
            self.ctx, self.stack, u'Timed out')

    def test_do_check_resource_marks_stack_as_failed_if_stack_timesout(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        mock_cru.side_effect = scheduler.Timeout(None, 60)
        self.is_update = True
        self.worker._handle_stack_timeout = mock.Mock()
        self.worker._do_check_resource(self.ctx, self.stack.current_traversal,
                                       self.stack.t, {}, self.is_update,
                                       self.resource, self.stack, {})
        self.worker._handle_stack_timeout.assert_called_once_with(
            self.ctx, self.stack)

    def test_do_check_resource_ignores_timeout_for_new_update(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        # Ensure current_traversal is check before marking the stack as
        # failed due to time-out.
        mock_cru.side_effect = scheduler.Timeout(None, 60)
        self.is_update = True
        self.worker._handle_stack_timeout = mock.Mock()
        old_traversal = self.stack.current_traversal
        self.stack.current_traversal = 'new_traversal'
        self.worker._do_check_resource(self.ctx, old_traversal,
                                       self.stack.t, {}, self.is_update,
                                       self.resource, self.stack, {})
        self.assertFalse(self.worker._handle_stack_timeout.called)

    @mock.patch.object(stack.Stack, 'has_timed_out')
    def test_check_resource_handles_timeout(self, mock_to, mock_cru, mock_crc,
                                            mock_pcr, mock_csc, mock_cid):
        mock_to.return_value = True
        self.worker._handle_stack_timeout = mock.Mock()
        self.worker.check_resource(self.ctx, self.resource.id,
                                   self.stack.current_traversal,
                                   {}, self.is_update, {})
        self.assertTrue(self.worker._handle_stack_timeout.called)


@mock.patch.object(worker, 'construct_input_data')
@mock.patch.object(worker, 'check_stack_complete')
@mock.patch.object(worker, 'propagate_check_resource')
@mock.patch.object(worker, 'check_resource_cleanup')
@mock.patch.object(worker, 'check_resource_update')
class CheckWorkflowCleanupTest(common.HeatTestCase):
    @mock.patch.object(worker_client.WorkerClient, 'check_resource',
                       lambda *_: None)
    def setUp(self):
        super(CheckWorkflowCleanupTest, self).setUp()
        thread_group_mgr = mock.Mock()
        self.worker = worker.WorkerService('host-1',
                                           'topic-1',
                                           'engine_id',
                                           thread_group_mgr)
        self.worker._rpc_client = worker_client.WorkerClient()
        self.ctx = utils.dummy_context()
        tstack = tools.get_stack(
            'check_workflow_create_stack', self.ctx,
            template=tools.string_template_five, convergence=True)
        tstack.converge_stack(tstack.t, action=tstack.CREATE)
        self.stack = stack.Stack.load(self.ctx, stack_id=tstack.id)
        self.stack.converge_stack(self.stack.t, action=self.stack.DELETE)
        self.resource = self.stack['A']
        self.is_update = False
        self.graph_key = (self.resource.id, self.is_update)

    def test_is_cleanup_traversal(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        self.worker.check_resource(
            self.ctx, self.resource.id, self.stack.current_traversal, {},
            self.is_update, None)
        self.assertFalse(mock_cru.called)
        mock_crc.assert_called_once_with(
            self.resource, self.resource.stack.t.id,
            {}, self.worker.engine_id,
            self.stack.timeout_secs())

    def test_is_cleanup_traversal_raise_update_inprogress(
            self, mock_cru, mock_crc, mock_pcr, mock_csc, mock_cid):
        mock_crc.side_effect = resource.UpdateInProgress
        self.worker.check_resource(
            self.ctx, self.resource.id, self.stack.current_traversal, {},
            self.is_update, None)
        mock_crc.assert_called_once_with(self.resource,
                                         self.resource.stack.t.id,
                                         {}, self.worker.engine_id,
                                         self.stack.timeout_secs())
        self.assertFalse(mock_cru.called)
        self.assertFalse(mock_pcr.called)
        self.assertFalse(mock_csc.called)


class MiscMethodsTest(common.HeatTestCase):
    def setUp(self):
        super(MiscMethodsTest, self).setUp()
        self.ctx = utils.dummy_context()
        self.stack = tools.get_stack(
            'check_workflow_create_stack', self.ctx,
            template=tools.string_template_five, convergence=True)
        self.stack.converge_stack(self.stack.t)
        self.resource = self.stack['A']

    def test_construct_input_data_ok(self):
        expected_input_data = {'attrs': {'value': None},
                               'id': mock.ANY,
                               'reference_id': 'A',
                               'name': 'A'}
        actual_input_data = worker.construct_input_data(self.resource)
        self.assertEqual(expected_input_data, actual_input_data)

    def test_construct_input_data_exception(self):
        expected_input_data = {'attrs': {},
                               'id': mock.ANY,
                               'reference_id': 'A',
                               'name': 'A'}
        self.resource.FnGetAtt = mock.Mock(
            side_effect=exception.InvalidTemplateAttribute(resource='A',
                                                           key='value'))
        actual_input_data = worker.construct_input_data(self.resource)
        self.assertEqual(expected_input_data, actual_input_data)

    @mock.patch.object(sync_point, 'sync')
    def test_check_stack_complete_root(self, mock_sync):
        worker.check_stack_complete(
            self.ctx, self.stack, self.stack.current_traversal,
            self.stack['E'].id, self.stack.convergence_dependencies,
            True)
        mock_sync.assert_called_once_with(
            self.ctx, self.stack.id, self.stack.current_traversal, True,
            mock.ANY, mock.ANY, {(self.stack['E'].id, True): None})

    @mock.patch.object(sync_point, 'sync')
    def test_check_stack_complete_child(self, mock_sync):
        worker.check_stack_complete(
            self.ctx, self.stack, self.stack.current_traversal,
            self.resource.id, self.stack.convergence_dependencies,
            True)
        self.assertFalse(mock_sync.called)

    @mock.patch.object(sync_point, 'sync')
    def test_propagate_check_resource(self, mock_sync):
        worker.propagate_check_resource(
            self.ctx, mock.ANY, mock.ANY,
            self.stack.current_traversal, mock.ANY,
            ('A', True), {}, True, None)
        self.assertTrue(mock_sync.called)

    @mock.patch.object(resource.Resource, 'create_convergence')
    @mock.patch.object(resource.Resource, 'update_convergence')
    def test_check_resource_update_init_action(self, mock_update, mock_create):
        self.resource.action = 'INIT'
        worker.check_resource_update(self.resource, self.resource.stack.t.id,
                                     {}, 'engine-id',
                                     self.stack.timeout_secs())
        self.assertTrue(mock_create.called)
        self.assertFalse(mock_update.called)

    @mock.patch.object(resource.Resource, 'create_convergence')
    @mock.patch.object(resource.Resource, 'update_convergence')
    def test_check_resource_update_create_action(
            self, mock_update, mock_create):
        self.resource.action = 'CREATE'
        worker.check_resource_update(self.resource, self.resource.stack.t.id,
                                     {}, 'engine-id',
                                     self.stack.timeout_secs())
        self.assertFalse(mock_create.called)
        self.assertTrue(mock_update.called)

    @mock.patch.object(resource.Resource, 'create_convergence')
    @mock.patch.object(resource.Resource, 'update_convergence')
    def test_check_resource_update_update_action(
            self, mock_update, mock_create):
        self.resource.action = 'UPDATE'
        worker.check_resource_update(self.resource, self.resource.stack.t.id,
                                     {}, 'engine-id',
                                     self.stack.timeout_secs())
        self.assertFalse(mock_create.called)
        self.assertTrue(mock_update.called)

    @mock.patch.object(resource.Resource, 'delete_convergence')
    def test_check_resource_cleanup_delete(self, mock_delete):
        self.resource.current_template_id = 'new-template-id'
        worker.check_resource_cleanup(self.resource, self.resource.stack.t.id,
                                      {}, 'engine-id',
                                      self.stack.timeout_secs())
        self.assertTrue(mock_delete.called)
