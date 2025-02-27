#  Copyright (c) ZenML GmbH 2021. All Rights Reserved.
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

from abc import abstractmethod
from typing import Any

from zenml.artifacts import DataArtifact
from zenml.steps import BaseStep, BaseStepConfig, StepContext


class BaseDriftDetectionConfig(BaseStepConfig):
    """Base class for drift detection step configurations"""


class BaseDriftDetectionStep(BaseStep):
    """Base step implementation for any drift detection step implementation
    on ZenML"""

    STEP_INNER_FUNC_NAME = "entrypoint"

    @abstractmethod
    def entrypoint(  # type: ignore[override]
        self,
        reference_dataset: DataArtifact,
        comparison_dataset: DataArtifact,
        config: BaseDriftDetectionConfig,
        context: StepContext,
    ) -> Any:
        """Base entrypoint for any drift detection implementation"""
