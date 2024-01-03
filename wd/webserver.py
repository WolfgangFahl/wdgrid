"""
Created on 2024-01-03

@author: wf
"""
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.webserver import WebserverConfig
from wd.version import Version
from wd.wditem_search import WikidataItemSearch
from nicegui import Client

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
 
        
    async def home(self,_client:Client):
        """
        provide the main content page
        """
        def show():
            self.wd_item_search=WikidataItemSearch(self)
            
        await(self.setup_content_div(show))
