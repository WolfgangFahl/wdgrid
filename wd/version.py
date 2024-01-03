"""
Created on 2024-01-02

@author: wf
"""
import wd
from dataclasses import dataclass


@dataclass
class Version(object):
    """
    Version handling for wdgrid
    """

    name = "wdgrid"
    version = wd.__version__
    description = "wikdata grid and sync"
    date = "2021-12-12"
    updated = "2024-02-03"

    authors = "Wolfgang Fahl"

    doc_url = "https://wiki.bitplan.com/index.php/Wdgrid"
    chat_url = "https://github.com/WolfgangFahl/wdgrid/discussions"
    cm_url = "https://github.com/WolfgangFahl/wdgrid"

    license = f"""Copyright 2023 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied."""

    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""
