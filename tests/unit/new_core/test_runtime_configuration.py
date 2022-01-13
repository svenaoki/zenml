#  Copyright (c) ZenML GmbH 2022. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
from zenml.stack import RuntimeConfiguration


def test_initializing_runtime_configuration_with_options():
    """Tests that the runtime configuration stores values that are passed
    during initialization."""
    runtime_configuration = RuntimeConfiguration(
        run_name="test_name", other_option=False
    )

    assert runtime_configuration.run_name == "test_name"
    assert runtime_configuration["other_option"] is False


def test_setting_runtime_options_after_initialization():
    """Tests that the runtime configuration stores values that are passed after
    initialization."""
    runtime_configuration = RuntimeConfiguration()
    assert runtime_configuration.run_name is None

    runtime_configuration["some_option"] = 43
    assert runtime_configuration["some_option"] == 43
