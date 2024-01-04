"""
Created on 2024-01-04

@author: wf
"""
from lodstorage.trulytabular import TrulyTabular, WikidataProperty
from ngwidgets.webserver import NiceGuiWebserver
from ngwidgets.widgets import Link
from nicegui import ui, run
from wd.pareto import Pareto
from wd.query_display import QueryDisplay
from wd.wditem_search import WikidataItemSearch
from dataclasses import dataclass


@dataclass
class TrulyTabularConfig:
    lang: str = "en"
    list_separator: str = "|"
    endpoint_name: str = "wikidata"
    with_subclasses: bool = False

    @property
    def subclass_predicate(self) -> str:
        """
        Get the subclass predicate string based on the with_subclasses flag.

        Returns:
            str: The subclass predicate.
        """
        return "wdt:P31/wdt:P279*" if self.with_subclasses else "wdt:P31"

    def setup_ui(self,webserver):
        WikidataItemSearch.setup_language_select(target=self)
        ui.checkbox("subclasses", value=self.with_subclasses).bind_value(
            self, "with_subclasses"
        )
        list_separators = {
            "|": "|",
            ",": ",",
            ";": ";",
            ":": ":",
            "\x1c": "FS - ASCII(28)",
            "\x1d": "GS - ASCII(29)",
            "\x1e": "RS - ASCII(30)",
            "\x1f": "US - ASCII(31)",
        }
        webserver.add_select("List separator",list_separators).bind_value(self,"list_separator")



class TrulyTabularDisplay:
    """
    Displays a truly tabular analysis for a given Wikidata
    item
    """

    def __init__(self, webserver: NiceGuiWebserver, qid: str):
        self.webserver = webserver
        self.config = webserver.tt_config
        self.qid = qid
        self.pareto_levels = {}
        self.tt = None
        for level in range(1, 10):
            pareto = Pareto(level)
            self.pareto_levels[level] = pareto
        self.setup()

    def handle_exception(self, ex):
        """
        delegate handle_exception calls
        """
        self.webserver.handle_exception(ex, self.webserver.do_trace)

    def setup(self):
        """
        set up the user interface
        """
        with ui.element("div").classes("w-full"):
            with ui.splitter() as splitter:
                with splitter.before:
                    self.item_input = ui.input(
                        "item", value=self.qid, on_change=self.update_view
                    ).bind_value(self, "qid")
                    with ui.row() as self.item_row:
                        self.item_link_view = ui.html()
                        self.item_count_view = ui.html()
                with splitter.after as self.query_display_container:
                    self.count_query_display = QueryDisplay(
                        self.webserver, name="count query"
                    )
        # immediately do an async call of update view
        ui.timer(0, self.update_view, once=True)

    def update_item_count_view(self):
        """
        update the item count
        """
        try:
            self.ttcount, countQuery = self.tt.count()
            with self.item_row:
                if self.tt.error:
                    self.item_count_view.content = "❓"
                else:
                    self.item_count_view.content = f"{self.ttcount} instances found"
            with self.query_display_container:
                self.count_query_display.show_query(countQuery)
        except Exception as ex:
            self.handle_exception(ex)

    def update_item_link_view(self):
        with self.item_row:
            item_text = self.tt.item.asText(long=True)
            item_url = self.tt.item.url
            item_link = Link.create(item_url, item_text)
            self.item_link_view.content = item_link

    async def update_view(self):
        # todo add details such as endpointConf
        self.tt = TrulyTabular(
            itemQid=self.qid,
            subclassPredicate=self.config.subclass_predicate,
            debug=self.webserver.debug,
        )  # Initialize TrulyTabular with the qid
        self.update_item_link_view()
        await run.io_bound(self.update_item_count_view)
