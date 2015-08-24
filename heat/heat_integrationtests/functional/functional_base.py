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

from heat_integrationtests.common import test


class FunctionalTestsBase(test.HeatIntegrationTest):

    def setUp(self):
        super(FunctionalTestsBase, self).setUp()
        self.check_skip_test()
        self.client = self.orchestration_client

    def check_skip_test(self):
        test_cls_name = self.__class__.__name__
        test_method_name = '.'.join([test_cls_name, self._testMethodName])
        test_skipped = (self.conf.skip_functional_test_list and (
            test_cls_name in self.conf.skip_functional_test_list or
            test_method_name in self.conf.skip_functional_test_list))

        if self.conf.skip_functional_tests or test_skipped:
            self.skipTest('Test disabled in conf, skipping')
