"""
Created on 2024-01-03

@author: wf
"""
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.webserver import WebserverConfig
from wd.version import Version

class WdgridWebServer(InputWebserver):
    """
    Server for Wikidata Grid
    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        """
        get the configuration for this Webserver
        """
        copy_right = "(c)2022-2024 Wolfgang Fahl"
        config = WebserverConfig(
            copy_right=copy_right, version=Version(), default_port=9999
        )
        return config

    def __init__(self):
        """Constructs all the necessary attributes for the WebServer object."""
        InputWebserver.__init__(self, config=WdgridWebServer.get_config())
 
