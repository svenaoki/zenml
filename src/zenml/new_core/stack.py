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
import os
import time
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, AbstractSet, Any, Dict, List, Optional

from zenml.enums import StackComponentType
from zenml.io.utils import get_global_config_directory
from zenml.logger import get_logger
from zenml.new_core.runtime_configuration import RuntimeConfiguration
from zenml.new_core.stack_component import StackComponent
from zenml.utils import string_utils

if TYPE_CHECKING:
    from zenml.artifact_stores import BaseArtifactStore
    from zenml.container_registries import BaseContainerRegistry
    from zenml.metadata_stores import BaseMetadataStore
    from zenml.orchestrators import BaseOrchestrator
    from zenml.pipelines import BasePipeline

logger = get_logger(__name__)


class Stack:
    """ZenML stack class.

    A ZenML stack is a collection of multiple stack components that are
    required to run ZenML pipelines. Some of these components (orchestrator,
    metadata store and artifact store) are required to run any kind of
    pipeline, other components like the container registry are only required
    if other stack components depend on them.
    """

    def __init__(
        self,
        name: str,
        *,
        orchestrator: "BaseOrchestrator",
        metadata_store: "BaseMetadataStore",
        artifact_store: "BaseArtifactStore",
        container_registry: Optional["BaseContainerRegistry"] = None,
    ):
        """Initializes and validates a stack instance.

        Raises:
             StackValidationError: If the stack configuration is not valid.
        """
        self._name = name
        self._orchestrator = orchestrator
        self._metadata_store = metadata_store
        self._artifact_store = artifact_store
        self._container_registry = container_registry

        self.validate()

    @classmethod
    def default_local_stack(cls) -> "Stack":
        """Creates a stack instance which is configured to run locally."""
        from zenml.artifact_stores import LocalArtifactStore
        from zenml.metadata_stores import SQLiteMetadataStore
        from zenml.orchestrators import LocalOrchestrator

        orchestrator = LocalOrchestrator(name="local_orchestrator")

        artifact_store_uuid = uuid.uuid4()
        artifact_store_path = os.path.join(
            get_global_config_directory(),
            "local_stores",
            str(artifact_store_uuid),
        )
        artifact_store = LocalArtifactStore(
            name="local_artifact_store",
            uuid=artifact_store_uuid,
            path=artifact_store_path,
        )

        metadata_store_path = os.path.join(artifact_store_path, "metadata.db")
        metadata_store = SQLiteMetadataStore(
            name="local_metadata_store", uri=metadata_store_path
        )

        return cls(
            name="local_stack",
            orchestrator=orchestrator,
            metadata_store=metadata_store,
            artifact_store=artifact_store,
        )

    @property
    def components(self) -> Dict[StackComponentType, StackComponent]:
        """All components of the stack."""
        return {
            component.type: component
            for component in [
                self.orchestrator,
                self.metadata_store,
                self.artifact_store,
                self.container_registry,
            ]
            if component is not None
        }

    @property
    def name(self) -> str:
        """The name of the stack."""
        return self._name

    @property
    def orchestrator(self) -> "BaseOrchestrator":
        """The orchestrator of the stack."""
        return self._orchestrator

    @property
    def metadata_store(self) -> "BaseMetadataStore":
        """The metadata store of the stack."""
        return self._metadata_store

    @property
    def artifact_store(self) -> "BaseArtifactStore":
        """The artifact store of the stack."""
        return self._artifact_store

    @property
    def container_registry(self) -> Optional["BaseContainerRegistry"]:
        """The container registry of the stack."""
        return self._container_registry

    # TODO [LOW]: Implement CLI method to generate configuration file from a
    #  stack's available runtime options
    @property
    def runtime_options(self) -> Dict[str, Any]:
        """Runtime options that are available to configure this stack.

        This method combines the available runtime options for all components
        of this stack. See `StackComponent.runtime_options()` for
        more information.
        """
        runtime_options = {}
        for component in self.components.values():
            duplicate_runtime_options = (
                runtime_options.keys() & component.runtime_options.keys()
            )
            if duplicate_runtime_options:
                logger.warning(
                    "Found duplicate runtime options %s.",
                    duplicate_runtime_options,
                )

            runtime_options.update(component.runtime_options)

        return runtime_options

    def requirements(
        self, exclude_components: AbstractSet[StackComponentType]
    ) -> List[str]:
        """List of PyPI requirements for the stack.

        This method combines the requirements of all stack components (except
        the ones specified in `exclude_components`).

        Args:
            exclude_components: Set of component types for which the
                requirements should not be included in the output.
        """
        requirements = []
        for component_type, component in self.components.items():
            if component_type not in exclude_components:
                requirements.extend(component.requirements)

        return requirements

    def validate(self) -> None:
        """Checks whether the stack configuration is valid.

        To check if a stack configuration is valid, the following criteria must
        be met:
        - all components must support the execution mode (either local or
         remote execution) specified by the orchestrator of the stack
        - the `StackValidator` of each stack component has to validate the
         stack to make sure all the components are compatible with each other

        Raises:
             StackValidationError: If the stack configuration is not valid.
        """
        # TODO [HIGH]: Check if all components support either local/remote
        #  execution depending on the mode specified by the orchestrator

        for component in self.components.values():
            if component.validator:
                component.validator.validate(stack=self)

    def deploy_pipeline(
        self,
        pipeline: "BasePipeline",
        runtime_configuration: RuntimeConfiguration,
    ) -> Any:
        """Deploys a pipeline on this stack.

        Args:
            pipeline: The pipeline to deploy.
            runtime_configuration: Contains all the runtime configuration
                options specified for the pipeline run.

        Returns:
            The return value of the call to `orchestrator.run_pipeline(...)`.
        """
        for component in self.components.values():
            component.prepare_pipeline_deployment(
                pipeline=pipeline,
                stack=self,
                runtime_configuration=runtime_configuration,
            )

        for component in self.components.values():
            component.prepare_pipeline_run()

        run_name = runtime_configuration.run_name or (
            f"{pipeline.name}-"
            f'{datetime.now().strftime("%d_%h_%y-%H_%M_%S_%f")}'
        )

        logger.info(
            "Using stack `%s` to run pipeline `%s`...",
            self.name,
            pipeline.name,
        )
        start_time = time.time()

        return_value = self.orchestrator.run_pipeline(
            pipeline, stack=self, run_name=run_name
        )

        run_duration = time.time() - start_time
        logger.info(
            "Pipeline run `%s` has finished in %s.",
            run_name,
            string_utils.get_human_readable_time(run_duration),
        )

        for component in self.components.values():
            component.cleanup_pipeline_run()

        return return_value
        )
