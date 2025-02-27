#  Copyright (c) ZenML GmbH 2021. All Rights Reserved.
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

# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: ce_cli.cli
.. moduleauthor:: ZenML GmbH <support@zenml.io>
"""

import click

from zenml import __version__
from zenml.logger import set_root_verbosity


@click.group()
@click.version_option(__version__, "--version", "-v")
def cli() -> None:
    """ZenML"""
    set_root_verbosity()


if __name__ == "__main__":
    cli()
