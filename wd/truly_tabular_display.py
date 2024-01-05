"""
Created on 2024-01-04

@author: wf
"""
import collections
from dataclasses import dataclass
from typing import Dict, List, Tuple

from lodstorage.query import Endpoint, EndpointManager
from lodstorage.trulytabular import TrulyTabular
from ngwidgets.lod_grid import ListOfDictsGrid
from ngwidgets.webserver import NiceGuiWebserver
from ngwidgets.widgets import Lang, Link
from nicegui import run, ui
from numpy.random.mtrand import pareto
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError

from wd.pareto import Pareto
from wd.query_view import QueryView

@dataclass
class TrulyTabularConfig:
    """
    Configuration class for Truly Tabular operations.

    Attributes:
        lang (str): Language code (default is "en").
        list_separator (str): Character used to separate items in lists (default is "|").
        endpoint_name (str): Name of the endpoint to use (default is "wikidata").
        with_subclasses (bool): Flag indicating whether to include subclasses in the queries (default is False).
    """

    lang: str = "en"
    list_separator: str = "|"
    endpoint_name: str = "wikidata"
    with_subclasses: bool = False
    pareto_level = 1

    def __post_init__(self):
        """
        Post-initialization to setup additional attributes.
        """
        self.endpoints = EndpointManager.getEndpoints(lang="sparql")
        self.languages = Lang.get_language_dict()
        self.pareto_levels = {}
        self.pareto_select = {}
        for level in range(1, 10):
            pareto = Pareto(level)
            self.pareto_levels[level] = pareto
            self.pareto_select[level] = pareto.asText(long=True)
        pass

    @property
    def sparql_endpoint(self) -> Endpoint:
        endpoint = self.endpoints.get(self.endpoint_name, None)
        return endpoint

    @property
    def pareto(self) -> Pareto:
        pareto = self.pareto_levels[self.pareto_level]
        return pareto

    @property
    def subclass_predicate(self) -> str:
        """
        Get the subclass predicate string based on the with_subclasses flag.

        Returns:
            str: The subclass predicate.
        """
        return "wdt:P31/wdt:P279*" if self.with_subclasses else "wdt:P31"

    def setup_ui(self, webserver):
        """
        setup the user interface
        """
        with ui.grid(columns=2):
            webserver.add_select("lang", self.languages, with_input=True).bind_value(
                self, "lang"
            )
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
            webserver.add_select("List separator", list_separators).bind_value(
                self, "list_separator"
            )
            webserver.add_select("Endpoint", list(self.endpoints.keys())).bind_value(
                self, "endpoint_name"
            )
            webserver.add_select("Pareto level", self.pareto_select).bind_value(
                self, "pareto_level"
            )


class PropertySelection:
    """
    select properties
    """

    aggregates = ["min", "max", "avg", "sample", "list", "count"]

    def __init__(
        self,
        inputList,
        total: int,
        paretoLevels: Dict[int, Pareto],
        minFrequency: float,
    ):
        """
           Constructor

        Args:
            propertyList(list): the list of properties to show
            total(int): total number of properties
            paretolLevels: a dict of paretoLevels with the key corresponding to the level
            minFrequency(float): the minimum frequency of the properties to select in percent
        """
        self.propertyMap: Dict[str, dict] = dict()
        self.headerMap = {}
        self.propertyList = []
        self.total = total
        self.paretoLevels = paretoLevels
        self.minFrequency = minFrequency
        for record in inputList:
            ratio = int(record["count"]) / self.total
            level = self.getParetoLevel(ratio)
            record["%"] = f"{ratio*100:.1f}"
            record["pareto"] = level
            # if record["pareto"]<=paretoLimit:
            orecord = collections.OrderedDict(record.copy())
            self.propertyList.append(orecord)
        pass

    def getParetoLevel(self, ratio):
        level = 0
        for pareto in reversed(self.paretoLevels.values()):
            if pareto.ratioInLevel(ratio):
                level = pareto.level
        return level

    def getInfoHeaderColumn(self, col: str) -> str:
        href = f"https://wiki.bitplan.com/index.php/Truly_Tabular_RDF/Info#{col}"
        info = f"{col}<br><a href='{href}'style='color:white' target='_blank'>ⓘ</a>"
        return info

    def hasMinFrequency(self, record: dict) -> bool:
        """
        Check if the frequency of the given property record is greater than the minimal frequency

        Returns:
            True if property frequency is greater or equal than the minFrequency. Otherwise False
        """
        ok = float(record.get("%", 0)) >= self.minFrequency
        return ok

    def select(self) -> List[Tuple[str, dict]]:
        """
        select all properties that fulfill hasMinFrequency

        Returns:
            list of all selected properties as tuple list consisting of property id and record
        """
        selected = []
        for propertyId, propRecord in self.propertyMap.items():
            if self.hasMinFrequency(propRecord):
                selected.append((propertyId, propRecord))
        return selected

    def prepare(self):
        """
        prepare the propertyList

        Args:
            total(int): the total number of records
            paretoLevels(list): the pareto Levels to use
        """

        self.headerMap = {}
        cols = [
            "#",
            "%",
            "pareto",
            "property",
            "propertyId",
            "type",
            "1",
            "maxf",
            "nt",
            "nt%",
            "?f",
            "?ex",
            "✔",
        ]
        cols.extend(PropertySelection.aggregates)
        cols.extend(["ignore", "label", "select"])
        for col in cols:
            self.headerMap[col] = self.getInfoHeaderColumn(col)
        for i, prop in enumerate(self.propertyList):
            # add index as first column
            prop["#"] = i + 1
            prop.move_to_end("#", last=False)
            propLabel = prop.pop("propLabel")
            url = prop.pop("prop")
            itemId = url.replace("http://www.wikidata.org/entity/", "")
            prop["propertyId"] = itemId
            prop["property"] = Link.create(url, propLabel)
            prop["type"] = prop.pop("wbType").replace("http://wikiba.se/ontology#", "")
            prop["1"] = ""
            prop["maxf"] = ""
            prop["nt"] = ""
            prop["nt%"] = ""
            prop["?f"] = ""
            prop["?ex"] = ""
            prop["✔"] = ""
            # workaround count being first element
            prop["count"] = prop.pop("count")
            for col in PropertySelection.aggregates:
                prop[col] = ""
            prop["ignore"] = ""
            prop["label"] = ""
            prop["select"] = ""

            self.propertyMap[itemId] = prop


class TrulyTabularDisplay:
    """
    Displays a truly tabular analysis for a given Wikidata
    item
    """

    def __init__(self, webserver: NiceGuiWebserver, qid: str):
        self.webserver = webserver
        self.config = webserver.tt_config
        self.qid = qid
        self.tt = None
        self.setup()

    def handle_exception(self, ex):
        """
        delegate handle_exception calls
        """
        self.webserver.handle_exception(ex, self.webserver.do_trace)

    @staticmethod
    def isTimeoutException(ex: EndPointInternalError):
        """
        Checks if the given exception is a query timeout exception

        Returns:
            True if the given exception is caused by a query timeout
        """
        check_for = "java.util.concurrent.TimeoutException"
        msg = ex.args[0]
        res = False
        if isinstance(msg, str):
            if check_for in msg:
                res = True
        return res

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
                    self.count_query_view = QueryView(
                        self.webserver,
                        name="count Query",
                        sparql_endpoint=self.config.sparql_endpoint,
                    )
                    self.property_query_view = QueryView(
                        self.webserver,
                        name="property Query",
                        sparql_endpoint=self.config.sparql_endpoint,
                    )
            with ui.row() as self.property_grid_row:
                self.property_grid = ListOfDictsGrid()
        # immediately do an async call of update view
        ui.timer(0, self.update_view, once=True)

    def update_item_count_view(self):
        """
        update the item count
        """
        try:
            self.ttcount, countQuery = self.tt.count()
            with self.query_display_container:
                self.count_query_view.show_query(countQuery)
            with self.item_row:
                if self.tt.error:
                    self.item_count_view.content = "❓"
                else:
                    self.item_count_view.content = f"{self.ttcount} instances found"
                    self.update_property_query_view(total=self.ttcount)
        except Exception as ex:
            self.handle_exception(ex)

    def update_property_query_view(self, total: int):
        """
        update the property query view
        """
        pareto = self.config.pareto
        if total is not None:
            min_count = round(total / pareto.oneOutOf)
        else:
            min_count = 0
        with self.query_display_container:
            msg = f"searching properties with at least {min_count} usages"
            ui.notify(msg)
            mfp_query = self.tt.mostFrequentPropertiesQuery(minCount=min_count)
            self.property_query_view.show_query(mfp_query.query)
            self.update_properties_table(mfp_query)

    def update_properties_table(self, mfp_query):
        """
        update my properties table

        Args:
            mfp_query(Query): the query for the most frequently used properties
        """
        with self.query_display_container:
            msg = f"running query for most frequently used properties of {str(self.tt)} ..."
            ui.notify(msg)
            try:
                property_lod = self.tt.sparql.queryAsListOfDicts(mfp_query.query)
            except EndPointInternalError as ex:
                if self.isTimeoutException(ex):
                    raise Exception("Query timeout of the property table query")
            self.min_property_frequency=self.config.pareto.asPercent()    
            self.property_selection = PropertySelection(
                property_lod,
                total=self.ttcount,
                paretoLevels=self.config.pareto_levels,
                minFrequency=self.min_property_frequency)
            self.property_selection.prepare()
            with self.property_grid_row:
                view_lod=self.property_selection.propertyList
                self.property_grid.load_lod(view_lod)
                self.property_grid.update()

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
        )
        for query_view in self.count_query_view, self.property_query_view:
            query_view.sparql_endpoint = self.config.sparql_endpoint
        # Initialize TrulyTabular with the qid
        self.update_item_link_view()
        await run.io_bound(self.update_item_count_view)
