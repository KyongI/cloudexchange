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

from oslo_config import cfg

from heat.common import exception
from heat.common.i18n import _
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine import support
from heat.engine import watchrule


class CloudWatchAlarm(resource.Resource):
    PROPERTIES = (
        COMPARISON_OPERATOR, ALARM_DESCRIPTION, EVALUATION_PERIODS,
        METRIC_NAME, NAMESPACE, PERIOD, STATISTIC, ALARM_ACTIONS,
        OKACTIONS, DIMENSIONS, INSUFFICIENT_DATA_ACTIONS, THRESHOLD,
        UNITS,
    ) = (
        'ComparisonOperator', 'AlarmDescription', 'EvaluationPeriods',
        'MetricName', 'Namespace', 'Period', 'Statistic', 'AlarmActions',
        'OKActions', 'Dimensions', 'InsufficientDataActions', 'Threshold',
        'Units',
    )

    properties_schema = {
        COMPARISON_OPERATOR: properties.Schema(
            properties.Schema.STRING,
            _('Operator used to compare the specified Statistic with '
              'Threshold.'),
            constraints=[
                constraints.AllowedValues(['GreaterThanOrEqualToThreshold',
                                           'GreaterThanThreshold',
                                           'LessThanThreshold',
                                           'LessThanOrEqualToThreshold']),
            ],
            required=True,
            update_allowed=True
        ),
        ALARM_DESCRIPTION: properties.Schema(
            properties.Schema.STRING,
            _('Description for the alarm.'),
            update_allowed=True
        ),
        EVALUATION_PERIODS: properties.Schema(
            properties.Schema.STRING,
            _('Number of periods to evaluate over.'),
            required=True,
            update_allowed=True
        ),
        METRIC_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Metric name watched by the alarm.'),
            required=True
        ),
        NAMESPACE: properties.Schema(
            properties.Schema.STRING,
            _('Namespace for the metric.'),
            required=True
        ),
        PERIOD: properties.Schema(
            properties.Schema.STRING,
            _('Period (seconds) to evaluate over.'),
            required=True,
            update_allowed=True
        ),
        STATISTIC: properties.Schema(
            properties.Schema.STRING,
            _('Metric statistic to evaluate.'),
            constraints=[
                constraints.AllowedValues(['SampleCount', 'Average', 'Sum',
                                           'Minimum', 'Maximum']),
            ],
            required=True,
            update_allowed=True
        ),
        ALARM_ACTIONS: properties.Schema(
            properties.Schema.LIST,
            _('A list of actions to execute when state transitions to alarm.'),
            update_allowed=True
        ),
        OKACTIONS: properties.Schema(
            properties.Schema.LIST,
            _('A list of actions to execute when state transitions to ok.'),
            update_allowed=True
        ),
        DIMENSIONS: properties.Schema(
            properties.Schema.LIST,
            _('A list of dimensions (arbitrary name/value pairs) associated '
              'with the metric.')
        ),
        INSUFFICIENT_DATA_ACTIONS: properties.Schema(
            properties.Schema.LIST,
            _('A list of actions to execute when state transitions to '
              'insufficient-data.'),
            update_allowed=True
        ),
        THRESHOLD: properties.Schema(
            properties.Schema.STRING,
            _('Threshold to evaluate against.'),
            required=True,
            update_allowed=True
        ),
        UNITS: properties.Schema(
            properties.Schema.STRING,
            _('Unit for the metric.'),
            constraints=[
                constraints.AllowedValues(['Seconds', 'Microseconds',
                                           'Milliseconds', 'Bytes',
                                           'Kilobytes', 'Megabytes',
                                           'Gigabytes', 'Terabytes', 'Bits',
                                           'Kilobits', 'Megabits',
                                           'Gigabits', 'Terabits', 'Percent',
                                           'Count', 'Bytes/Second',
                                           'Kilobytes/Second',
                                           'Megabytes/Second',
                                           'Gigabytes/Second',
                                           'Terabytes/Second', 'Bits/Second',
                                           'Kilobits/Second',
                                           'Megabits/Second',
                                           'Gigabits/Second',
                                           'Terabits/Second', 'Count/Second',
                                           None]),
            ],
            update_allowed=True
        ),
    }

    strict_dependency = False

    support_status = support.SupportStatus(
        status=support.HIDDEN,
        message=_('OS::Heat::CWLiteAlarm is deprecated, '
                  'use OS::Ceilometer::Alarm instead.'),
        version='5.0.0',
        previous_status=support.SupportStatus(
            status=support.DEPRECATED,
            version='2014.2'
        )
    )

    def handle_create(self):
        wr = watchrule.WatchRule(context=self.context,
                                 watch_name=self.physical_resource_name(),
                                 rule=self.parsed_template('Properties'),
                                 stack_id=self.stack.id)
        wr.store()

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        # If Properties has changed, update self.properties, so we
        # get the new values during any subsequent adjustment
        if prop_diff:
            self.properties = json_snippet.properties(self.properties_schema,
                                                      self.context)
            loader = watchrule.WatchRule.load
            wr = loader(self.context,
                        watch_name=self.physical_resource_name())

            wr.rule = self.parsed_template('Properties')
            wr.store()

    def handle_delete(self):
        try:
            wr = watchrule.WatchRule.load(
                self.context, watch_name=self.physical_resource_name())
            wr.destroy()
        except exception.WatchRuleNotFound:
            pass

    def handle_suspend(self):
        wr = watchrule.WatchRule.load(self.context,
                                      watch_name=self.physical_resource_name())
        wr.state_set(wr.SUSPENDED)

    def handle_resume(self):
        wr = watchrule.WatchRule.load(self.context,
                                      watch_name=self.physical_resource_name())
        # Just set to NODATA, which will be re-evaluated next periodic task
        wr.state_set(wr.NODATA)

    def handle_check(self):
        watch_name = self.physical_resource_name()
        watchrule.WatchRule.load(self.context, watch_name=watch_name)

    def FnGetRefId(self):
        return self.physical_resource_name_or_FnGetRefId()

    def physical_resource_name(self):
        return '%s-%s' % (self.stack.name, self.name)


def resource_mapping():
    cfg.CONF.import_opt('enable_cloud_watch_lite', 'heat.common.config')
    if cfg.CONF.enable_cloud_watch_lite:
        return {
            'OS::Heat::CWLiteAlarm': CloudWatchAlarm,
        }
    else:
        return {}
