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

import datetime

import mock
from oslo_utils import timeutils
import six

from heat.common import exception
from heat.common import template_format
from heat.engine import resource
from heat.engine import scheduler
from heat.tests.autoscaling import inline_templates
from heat.tests import common
from heat.tests import utils


as_template = inline_templates.as_template
as_params = inline_templates.as_params


class TestAutoScalingPolicy(common.HeatTestCase):
    def setUp(self):
        super(TestAutoScalingPolicy, self).setUp()

    def create_scaling_policy(self, t, stack, resource_name):
        rsrc = stack[resource_name]
        self.assertIsNone(rsrc.validate())
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        return rsrc

    def test_validate_scaling_policy_ok(self):
        t = template_format.parse(inline_templates.as_template)
        t['Resources']['WebServerScaleUpPolicy']['Properties'][
            'ScalingAdjustment'] = 33
        t['Resources']['WebServerScaleUpPolicy']['Properties'][
            'AdjustmentType'] = 'PercentChangeInCapacity'
        t['Resources']['WebServerScaleUpPolicy']['Properties'][
            'MinAdjustmentStep'] = 2
        stack = utils.parse_stack(t, params=as_params)
        self.policy = stack['WebServerScaleUpPolicy']
        self.assertIsNone(self.policy.validate())

    def test_validate_scaling_policy_error(self):
        t = template_format.parse(inline_templates.as_template)
        t['Resources']['WebServerScaleUpPolicy']['Properties'][
            'ScalingAdjustment'] = 1
        t['Resources']['WebServerScaleUpPolicy']['Properties'][
            'AdjustmentType'] = 'ChangeInCapacity'
        t['Resources']['WebServerScaleUpPolicy']['Properties'][
            'MinAdjustmentStep'] = 2
        stack = utils.parse_stack(t, params=as_params)
        self.policy = stack['WebServerScaleUpPolicy']
        ex = self.assertRaises(exception.ResourcePropertyValueDependency,
                               self.policy.validate)
        self.assertIn('MinAdjustmentStep property should only '
                      'be specified for AdjustmentType with '
                      'value PercentChangeInCapacity.', six.text_type(ex))

    def test_scaling_policy_bad_group(self):
        t = template_format.parse(inline_templates.as_template_bad_group)
        stack = utils.parse_stack(t, params=as_params)

        up_policy = self.create_scaling_policy(t, stack,
                                               'WebServerScaleUpPolicy')

        ex = self.assertRaises(exception.ResourceFailure, up_policy.signal)
        self.assertIn('Alarm WebServerScaleUpPolicy could '
                      'not find scaling group', six.text_type(ex))

    def test_scaling_policy_not_alarm_state(self):
        """If the details don't have 'alarm' then don't progress."""
        t = template_format.parse(as_template)
        stack = utils.parse_stack(t, params=as_params)
        pol = self.create_scaling_policy(t, stack, 'WebServerScaleUpPolicy')

        test = {'current': 'not_an_alarm'}
        with mock.patch.object(pol, '_cooldown_inprogress',
                               side_effect=AssertionError()) as dont_call:
            self.assertRaises(resource.NoActionRequired,
                              pol.handle_signal, details=test)
            self.assertEqual([], dont_call.call_args_list)

    def test_scaling_policy_cooldown_toosoon(self):
        """If _cooldown_inprogress() returns True don't progress."""
        t = template_format.parse(as_template)
        stack = utils.parse_stack(t, params=as_params)
        pol = self.create_scaling_policy(t, stack, 'WebServerScaleUpPolicy')
        test = {'current': 'alarm'}

        with mock.patch.object(pol.stack, 'resource_by_refid',
                               side_effect=AssertionError) as dont_call:
            with mock.patch.object(pol, '_cooldown_inprogress',
                                   return_value=True) as mock_cip:
                self.assertRaises(resource.NoActionRequired,
                                  pol.handle_signal, details=test)
                mock_cip.assert_called_once_with()
            self.assertEqual([], dont_call.call_args_list)

    def test_scaling_policy_cooldown_ok(self):
        t = template_format.parse(as_template)
        stack = utils.parse_stack(t, params=as_params)
        pol = self.create_scaling_policy(t, stack, 'WebServerScaleUpPolicy')
        test = {'current': 'alarm'}

        group = self.patchobject(pol.stack, 'resource_by_refid').return_value
        group.name = 'fluffy'
        with mock.patch.object(pol, '_cooldown_inprogress',
                               return_value=False) as mock_cip:
            pol.handle_signal(details=test)
            mock_cip.assert_called_once_with()
        group.adjust.assert_called_once_with(1, 'ChangeInCapacity', None)


class TestCooldownMixin(common.HeatTestCase):
    def setUp(self):
        super(TestCooldownMixin, self).setUp()

    def create_scaling_policy(self, t, stack, resource_name):
        rsrc = stack[resource_name]
        self.assertIsNone(rsrc.validate())
        scheduler.TaskRunner(rsrc.create)()
        self.assertEqual((rsrc.CREATE, rsrc.COMPLETE), rsrc.state)
        return rsrc

    def test_cooldown_is_in_progress_toosoon(self):
        t = template_format.parse(as_template)
        stack = utils.parse_stack(t, params=as_params)
        pol = self.create_scaling_policy(t, stack, 'WebServerScaleUpPolicy')

        now = timeutils.utcnow()
        previous_meta = {'cooldown': {
            now.isoformat(): 'ChangeInCapacity : 1'}}
        self.patchobject(pol, 'metadata_get', return_value=previous_meta)
        self.assertTrue(pol._cooldown_inprogress())

    def test_cooldown_is_in_progress_scaling_unfinished(self):
        t = template_format.parse(as_template)
        stack = utils.parse_stack(t, params=as_params)
        pol = self.create_scaling_policy(t, stack, 'WebServerScaleUpPolicy')

        previous_meta = {'scaling_in_progress': True}
        self.patchobject(pol, 'metadata_get', return_value=previous_meta)
        self.assertTrue(pol._cooldown_inprogress())

    def test_cooldown_not_in_progress(self):
        t = template_format.parse(as_template)
        stack = utils.parse_stack(t, params=as_params)
        pol = self.create_scaling_policy(t, stack, 'WebServerScaleUpPolicy')

        awhile_ago = timeutils.utcnow() - datetime.timedelta(seconds=100)
        previous_meta = {
            'cooldown': {
                awhile_ago.isoformat(): 'ChangeInCapacity : 1'
            },
            'scaling_in_progress': False
        }
        self.patchobject(pol, 'metadata_get', return_value=previous_meta)
        self.assertFalse(pol._cooldown_inprogress())

    def test_scaling_policy_cooldown_zero(self):
        t = template_format.parse(as_template)

        # Create the scaling policy (with Cooldown=0) and scale up one
        properties = t['Resources']['WebServerScaleUpPolicy']['Properties']
        properties['Cooldown'] = '0'

        stack = utils.parse_stack(t, params=as_params)
        pol = self.create_scaling_policy(t, stack, 'WebServerScaleUpPolicy')

        now = timeutils.utcnow()
        previous_meta = {now.isoformat(): 'ChangeInCapacity : 1'}
        self.patchobject(pol, 'metadata_get', return_value=previous_meta)
        self.assertFalse(pol._cooldown_inprogress())

    def test_scaling_policy_cooldown_none(self):
        t = template_format.parse(as_template)

        # Create the scaling policy no Cooldown property, should behave the
        # same as when Cooldown==0
        properties = t['Resources']['WebServerScaleUpPolicy']['Properties']
        del properties['Cooldown']

        stack = utils.parse_stack(t, params=as_params)
        pol = self.create_scaling_policy(t, stack, 'WebServerScaleUpPolicy')

        now = timeutils.utcnow()
        previous_meta = {now.isoformat(): 'ChangeInCapacity : 1'}
        self.patchobject(pol, 'metadata_get', return_value=previous_meta)
        self.assertFalse(pol._cooldown_inprogress())

    def test_metadata_is_written(self):
        t = template_format.parse(as_template)
        stack = utils.parse_stack(t, params=as_params)
        pol = self.create_scaling_policy(t, stack, 'WebServerScaleUpPolicy')

        nowish = timeutils.utcnow()
        reason = 'cool as'
        meta_set = self.patchobject(pol, 'metadata_set')
        self.patchobject(timeutils, 'utcnow', return_value=nowish)
        pol._cooldown_timestamp(reason)
        meta_set.assert_called_once_with(
            {'cooldown': {nowish.isoformat(): reason},
             'scaling_in_progress': False})


class ScalingPolicyAttrTest(common.HeatTestCase):
    def setUp(self):
        super(ScalingPolicyAttrTest, self).setUp()
        t = template_format.parse(as_template)
        self.stack = utils.parse_stack(t, params=as_params)
        self.policy = self.stack['WebServerScaleUpPolicy']
        self.assertIsNone(self.policy.validate())
        scheduler.TaskRunner(self.policy.create)()
        self.assertEqual((self.policy.CREATE, self.policy.COMPLETE),
                         self.policy.state)

    def test_alarm_attribute(self):
        self.assertIn("WebServerScaleUpPolicy",
                      self.policy.FnGetAtt('AlarmUrl'))
