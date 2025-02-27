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
"""
The mlflow integrations currently enables you to use mlflow tracking as a
convenient way to visualize your experiment runs within the mlflow ui
"""
from zenml.integrations.constants import MLFLOW
from zenml.integrations.integration import Integration


class MlflowIntegration(Integration):
    """Definition of Plotly integration for ZenML."""

    NAME = MLFLOW
    REQUIREMENTS = ["mlflow>=1.2.0"]


MlflowIntegration.check_installation()
