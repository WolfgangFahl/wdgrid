"""
Created on 2024-01-04

@author: wf
"""
from lodstorage.trulytabular import TrulyTabular, WikidataProperty
from ngwidgets.webserver import NiceGuiWebserver
from ngwidgets.widgets import Link
from nicegui import ui, run
from wd.pareto import Pareto


class TrulyTabularView:
    """
    Displays a truly tabular analysis for a given Wikidata
    item
    """

    def __init__(self, webserver: NiceGuiWebserver, qid: str):
        self.webserver = webserver
        self.qid = qid
        self.with_subclasses = False
        self.pareto_levels = {}
        for level in range(1, 10):
            pareto = Pareto(level)
            self.pareto_levels[level] = pareto
        self.setup()

    @property
    def subclass_predicate(self) -> str:
        """
        Get the subclass predicate string based on the with_subclasses flag.

        Returns:
            str: The subclass predicate.
        """
        return "wdt:P31/wdt:P279*" if self.with_subclasses else "wdt:P31"

    def handle_exception(self, ex):
        self.webserver.handle_exception(ex, self.webserver.do_trace)

    def setup(self):
        """
        set up the user interface
        """
        self.item_input = ui.input(
            "item", value=self.qid, on_change=self.update_view
        ).bind_value(self, "qid")
        ui.checkbox("subclasses", value=self.with_subclasses).bind_value(
            self, "with_subclasses"
        )
        with ui.row() as self.item_row:
            self.item_link_view = ui.html()
            self.item_count_view = ui.html()
        # immediately do an async call of update view
        ui.timer(0, self.update_view, once=True)

    def update_item_count_view(self):
        """
        update the item count
        """
        try:
            # todo add details such as endpointConf
            self.tt = TrulyTabular(
                itemQid=self.qid,
                subclassPredicate=self.subclass_predicate,
                debug=self.webserver.debug,
            )  # Initialize TrulyTabular with the qid
            self.ttcount, countQuery = self.tt.count()
            with self.item_row:
                if self.tt.error:
                    self.item_count_view.content = "❓"
                else:
                    self.item_count_view.content = f"{self.ttcount} instances found"
        except Exception as ex:
            self.handle_exception(ex)

    def update_item_link_view(self):
        item_url = f"https://www.wikidata.org/wiki/{self.qid}"
        item_link = Link.create(item_url, self.qid)
        with self.item_row:
            self.item_link_view.content = item_link

    async def update_view(self):
        self.update_item_link_view()
        await run.io_bound(self.update_item_count_view)
