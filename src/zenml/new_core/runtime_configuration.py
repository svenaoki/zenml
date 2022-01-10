#  Copyright (c) ZenML GmbH 2022. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
from typing import Any, Optional

from zenml.logger import get_logger

logger = get_logger(__name__)
RUN_NAME_OPTION_KEY = "run_name"


class RuntimeConfiguration(dict):
    """RuntimeConfiguration store dynamic options for a pipeline run.

    Use `stack.runtime_options()` to get all available runtime options for the
    components of a specific ZenML stack.

    This class is a `dict` subclass, so getting/setting runtime options is done
    using `some_value = runtime_configuration["some_key"]` and
    `runtime_configuration["some_key"] = 1`.
    """

    def __init__(self, run_name: Optional[str] = None, **runtime_options: Any):
        """Initializes a RuntimeConfiguration object.

        Args:
            run_name: Optional name of the pipeline run.
            **runtime_options: Additional runtime options.
        """
        runtime_options[RUN_NAME_OPTION_KEY] = run_name
        super().__init__(runtime_options)

    @property
    def run_name(self) -> Optional[str]:
        """Name of the pipeline run."""
        return self[RUN_NAME_OPTION_KEY]
