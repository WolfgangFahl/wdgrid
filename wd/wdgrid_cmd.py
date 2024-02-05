"""
Created on 2024-01-03

@author: wf
"""
import sys
from argparse import ArgumentParser

from lodstorage.query import EndpointManager
from ngwidgets.cmd import WebserverCmd

from wd.webserver import WdgridWebServer


class WdgridCmd(WebserverCmd):
    """
    Command line for wiki data grid web server
    """

    def getArgParser(self, description: str, version_msg) -> ArgumentParser:
        """
        override the default argparser call
        """
        parser = super().getArgParser(description, version_msg)
        parser.add_argument(
            "-en",
            "--endpointName",
            default="wikidata",
            help=f"Name of the endpoint to use for queries. Available by default: {EndpointManager.getEndpointNames(lang='sparql')}",
        )
        return parser


def main(argv: list = None):
    """
    main call
    """
    cmd = WdgridCmd(config=WdgridWebServer.get_config(), webserver_cls=WdgridWebServer)
    exit_code = cmd.cmd_main(argv)
    return exit_code


DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
