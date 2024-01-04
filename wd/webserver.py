"""
Created on 2024-01-03

@author: wf
"""
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.webserver import WebserverConfig
from ngwidgets.widgets import Link
from nicegui import Client, ui

from wd.version import Version
from wd.wditem_search import WikidataItemSearch
from wd.truly_tabular_display import TrulyTabularDisplay
from lodstorage.query import EndpointManager


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
        self.endpoints = EndpointManager.getEndpoints(lang="sparql")
        self.lang="en"
        
        @ui.page("/tt/{qid}")
        async def truly_tabular(client: Client, qid: str):
            """
            initiate the truly tabular analysis for the given Wikidata QIDs
            """
            await self.truly_tabular(qid)

    async def truly_tabular(self, qid: str):
        """
        show a truly tabular analysis of the given Wikidata id

        Args:
            qid(str): the Wikidata id of the item to analyze
        """

        def show():
            self.ttd = TrulyTabularDisplay(self, qid)

        await (self.setup_content_div(show))

    def configure_settings(self):
        """
        extra settings
        """
        WikidataItemSearch.setup_language_select(target=self)
 
    async def home(self, _client: Client):
        """
        provide the main content page
        """

        def record_filter(qid: str, record: dict):
            if "label" and "desc" in record:
                text = f"""{record["label"]}({qid})☞{record["desc"]}"""
                tt_link = Link.create(f"/tt/{qid}", text)
                # getting the link to be at second position
                # is a bit tricky
                temp_items = list(record.items())
                # Add the new item in the second position
                temp_items.insert(1, ("truly tabular", tt_link))

                # Clear the original dictionary and update it with the new order of items
                record.clear()
                record.update(temp_items)

        def show():
            self.wd_item_search = WikidataItemSearch(self, record_filter=record_filter)

        await (self.setup_content_div(show))
