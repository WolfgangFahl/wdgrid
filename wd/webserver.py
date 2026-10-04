"""
Created on 2024-01-03

@author: wf
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException
from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.webserver import WebserverConfig
from ngwidgets.widgets import Link
from nicegui import Client, app, ui

from wd.truly_tabular_display import TrulyTabularConfig, TrulyTabularDisplay
from wd.tt_analysis import TrulyTabularAnalysis
from wd.version import Version
from wd.wditem_search import WikidataItemSearch


class WdgridWebServer(InputWebserver):
    """
    Server for Wikidata Grid
    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        """
        get the configuration for this Webserver
        """
        copy_right = "(c)2022-2026 Wolfgang Fahl"
        config = WebserverConfig(
            short_name="wdgrid",
            copy_right=copy_right,
            version=Version(),
            default_port=9997,
        )
        server_config = WebserverConfig.get(config)
        server_config.solution_class = WdgridSolution
        return server_config

    def __init__(self):
        """Constructs all the necessary attributes for the WebServer object."""
        InputWebserver.__init__(self, config=WdgridWebServer.get_config())
        version = self.config.version
        # OpenAPI metadata so /docs shows wdgrid instead of FastAPI defaults
        app.title = version.name
        app.version = version.version
        app.description = version.description
        self.tt_analysis = TrulyTabularAnalysis(TrulyTabularConfig())

        @ui.page("/tt/{qid}")
        async def truly_tabular(client: Client, qid: str):
            """
            initiate the truly tabular analysis for the given Wikidata QIDs
            """
            await self.page(client, WdgridSolution.truly_tabular, qid)

        @app.get("/api/tt/{qid}", tags=["wdgrid"])
        def api_truly_tabular(
            qid: str,
            predicate: str = "wdt:P31",
            lang: str = "en",
            endpoint: Optional[str] = None,
            min_frequency: float = 20.0,
            stats: bool = False,
        ) -> Dict[str, Any]:
            """
            Get the truly tabular analysis for the given Wikidata item.

            Args:
                qid: Wikidata id of the item to analyze e.g. Q356847 for car carrier
                predicate: the search predicate e.g. wdt:P31 for instance of
                lang: the language for labels
                endpoint: the name of the SPARQL endpoint - default is the endpoint the server was started with
                min_frequency: the minimum frequency of the properties in percent
                stats: if true add the non tabular statistics (one query per property)
            """
            if endpoint is None:
                endpoint = getattr(getattr(self, "args", None), "endpointName", None)
            try:
                analysis = self.tt_analysis.analyze(
                    qid,
                    search_predicate=predicate,
                    lang=lang,
                    endpoint_name=endpoint,
                    min_frequency=min_frequency,
                    with_stats=stats,
                )
            except KeyError as ke:
                raise HTTPException(status_code=404, detail=str(ke))
            except Exception as ex:
                raise HTTPException(status_code=502, detail=str(ex))
            return analysis


class WdgridSolution(InputWebSolution):
    """
    Wikidata Grid client specific UI
    """

    def __init__(self, webserver: WdgridWebServer, client: Client):
        super().__init__(webserver, client)  # Call to the superclass constructor
        self.debug = webserver.debug
        self.tt_config = TrulyTabularConfig()

    async def truly_tabular(self, qid: str):
        """
        show a truly tabular analysis of the given Wikidata id

        Args:
            qid(str): the Wikidata id of the item to analyze
        """

        def show():
            self.ttd = TrulyTabularDisplay(self, qid)

        await self.setup_content_div(show)

    def configure_settings(self):
        """
        extra settings
        """
        self.tt_config.setup_ui(self)

    def prepare_ui(self):
        """
        overrideable configuration
        """
        self.tt_config.endpoint_name = self.args.endpointName

    async def home(self):
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
            self.wd_item_search = WikidataItemSearch(
                self, record_filter=record_filter, lang=self.tt_config.lang
            )

        await self.setup_content_div(show)
