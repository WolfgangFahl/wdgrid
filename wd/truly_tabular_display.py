"""
Created on 2024-01-04

@author: wf
"""
import asyncio
import collections
from dataclasses import dataclass
from typing import Dict, List, Tuple
from urllib.error import HTTPError

from lodstorage.query import Endpoint, EndpointManager, Query
from lodstorage.trulytabular import TrulyTabular
from ngwidgets.lod_grid import ListOfDictsGrid, GridConfig
from ngwidgets.webserver import NiceGuiWebserver
from ngwidgets.widgets import Lang, Link
from nicegui import run, ui
from numpy.random.mtrand import pareto
from SPARQLWrapper.SPARQLExceptions import EndPointInternalError

from wd.pareto import Pareto
from wd.query_view import QueryView
from ngwidgets.progress import NiceguiProgressbar
from pydantic_core.core_schema import NoneSchema


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
    # minimum percentual frequency of availability
    min_property_frequency = 20.0

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
    
    @property
    def aggregates(self)->list:
        aggregates = ["min", "max", "avg", "sample", "list", "count"]
        return aggregates
    
    @property
    def option_cols(self)->list:
        option_cols=["ignore", "label"]
        return option_cols
    
    @property
    def checkbox_cols(self)->list:
        """
        get all my checkbox columns
        """
        checkbox_cols=self.aggregates
        checkbox_cols.extend(self.option_cols)
        return checkbox_cols

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
        cols.extend(self.checkbox_cols)
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
            for col in self.checkbox_cols:
                prop[col] = False

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
        self.naive_query_view=None
        self.aggregate_query_view=None
        self.setup()
        
    async def ui_yield(self):
        await asyncio.sleep(0) # allow other tasks to run on the event loop        

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
        with ui.element("div").classes("w-full") as self.main_container:
            with ui.splitter() as splitter:
                with splitter.before:
                    self.item_input = ui.input(
                        "item", value=self.qid, on_change=self.update_display
                    ).bind_value(self, "qid")
                    with ui.row() as self.item_row:
                        self.item_link_view = ui.html()
                        self.item_count_view = ui.html()
                    with ui.row():
                        self.webserver.add_select(
                            "Pareto level",
                            self.config.pareto_select,
                            on_change=self.on_pareto_change,
                        ).bind_value(self.config, "pareto_level")
                        self.min_property_frequency_input = ui.input(
                            "min%",
                            value=str(self.config.min_property_frequency),
                        ).on("keydown.enter", self.on_min_property_frequency_change)
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
            with ui.row() as self.generate_button_row:
                self.generate_button = ui.button(
                    "Generate SPARQL queries", on_click=self.on_generate_button_click
                )
                self.generate_button.disable()
            with ui.row() as self.progressbar_row:
                self.progress_bar = NiceguiProgressbar(
                    total=0, desc="Property statistics", unit="prop"
                )
            with ui.row() as self.property_grid_row:
                config=GridConfig(multiselect=True)
                self.property_grid = ListOfDictsGrid(config=config)
        # immediately do an async call of update view
        ui.timer(0, self.update_display, once=True)

    def createTrulyTabular(self, itemQid: str, propertyIds=[]):
        """
        create a Truly Tabular configuration for my configure endpoint and the given itemQid and
        propertyIds

        Args:
            itemQid(str): e.g. Q5 human
            propertyIds(list): list of property Ids (if any) such as P17 country
        """
        tt = TrulyTabular(
            itemQid=itemQid,
            propertyIds=propertyIds,
            subclassPredicate=self.config.subclass_predicate,
            endpointConf=self.config.sparql_endpoint,
            debug=self.webserver.debug,
        )
        return tt

    def wikiTrulyTabularPropertyStats(self, itemId: str, propertyId: str):
        """
        get the truly tabular property statistics

        Args:
            itemId(str): the Wikidata item identifier
            propertyId(str): the property id
        """
        try:
            tt = self.createTrulyTabular(itemId, propertyIds=[propertyId])
            statsRow = next(tt.genPropertyStatistics())
            for key in ["queryf", "queryex"]:
                queryText = statsRow[key]
                sparql = f"# This query was generated by Truly Tabular\n{queryText}"
                query = Query(name=key, query=sparql)
                tryItUrlEncoded = query.getTryItUrl(
                    baseurl=self.config.sparql_endpoint.website,
                    database=self.config.sparql_endpoint.database,
                )
                tryItLink = Link.create(
                    url=tryItUrlEncoded,
                    text="try it!",
                    tooltip=f"try out with {self.config.sparql_endpoint.name}",
                    target="_blank",
                )
                statsRow[f"{key}TryIt"] = tryItLink
            return statsRow
        except (BaseException, HTTPError) as ex:
            self.handle_exception(ex)
            return None

    async def getPropertyIdMap(self)->Dict:
        """
        get the map of selected property ids
        with generation specs

        Returns:
            dict: a dict of list
        """
        idMap = {}
        cols = self.property_selection.checkbox_cols
        selected_rows= await self.property_grid.get_selected_rows()
        for srow in selected_rows:
            propertyId = srow["propertyId"]
            key_value = srow["#"]
            genList = []
            for col_key in cols:
                checked=self.property_grid.get_cell_value(key_value, col_key)   
                if checked:
                    genList.append(col_key)
            idMap[propertyId] = genList
        return idMap

    async def generateQueries(self):
        """
        generate and show the queries
        """
        try:
            propertyIdMap = await self.getPropertyIdMap()
            tt = self.createTrulyTabular(
                itemQid=self.qid, propertyIds=list(propertyIdMap.keys())
            )
            
            if self.naive_query_view is None:
                with self.query_display_container:
                    self.naive_query_view=QueryView(
                            self.webserver,
                            name="naive Query",
                            sparql_endpoint=self.config.sparql_endpoint,
                        )
            if self.aggregate_query_view is None:
                with self.query_display_container:
                    self.aggregate_query_view=QueryView(
                            self.webserver,
                            name="aggregate Query",
                            sparql_endpoint=self.config.sparql_endpoint,
                        )
            sparqlQuery = tt.generateSparqlQuery(
                genMap=propertyIdMap,
                naive=True,
                lang=self.config.lang,
                listSeparator=self.config.list_separator,
            )
            naiveSparqlQuery = Query(name="naive SPARQL Query", query=sparqlQuery)
            self.naive_query_view.show_query(naiveSparqlQuery.query)
            sparqlQuery = tt.generateSparqlQuery(
                genMap=propertyIdMap,
                naive=False,
                lang=self.config.lang,
                listSeparator=self.config.list_separator,
            )
            self.aggregateSparqlQuery = Query(
                name="aggregate SPARQL Query", query=sparqlQuery
            )
            self.aggregate_query_view.show_query(self.aggregateSparqlQuery.query)
            ui.notify("SPARQL queries generated")
        except Exception as ex:
            self.handle_exception(ex)

    async def on_generate_button_click(self, _event):
        """
        handle the generate button click
        """
        try:
            ui.notify(f"generating SPARQL query for {str(self.tt)}")
            await self.generateQueries()
        except BaseException as ex:
            self.handleException(ex)

    async def on_min_property_frequency_change(self, _event):
        """
        handle a change in the minimum property frequency input
        """
        value_str = self.min_property_frequency_input.value
        try:
            self.config.min_property_frequency = float(value_str)
            ui.notify(f"new freq: {self.config.min_property_frequency}")
            await self.update_display()
        except Exception as _ex:
            ui.notify(f"invalid frequency value {value_str}")
            pass

    async def on_pareto_change(self, _event):
        """
        handle changes in the pareto level
        """
        ui.notify(f"pareto level changed to {self.config.pareto_level} ")
        self.config.min_property_frequency = self.config.pareto.asPercent()
        self.min_property_frequency_input.value = str(
            self.config.min_property_frequency
        )

    def get_stats_rows(self, property_grid_rows: list):
        """
        get the statistic rows for the given property_grid_rows
        """
        for row in property_grid_rows:
            property_id = row["propertyId"]
            row_key = row["#"]
            stats_row = self.wikiTrulyTabularPropertyStats(self.tt.itemQid, property_id)
            if stats_row:
                stats_row["✔"] = "✔"
            else:
                stats_row={"✔": "❌"}
            for col_key, statsColumn in [
                ("1", "1"),
                ("maxf", "maxf"),
                ("nt", "non tabular"),
                ("nt%", "non tabular%"),
                ("?f", "queryfTryIt"),
                ("?ex", "queryexTryIt"),
                ("✔", "✔"),
            ]:
                if statsColumn in stats_row:
                    value = stats_row[statsColumn]
                    self.property_grid.update_cell(row_key, col_key, value)
            self.property_grid.update()
            pass

    def update_item_count_view(self):
        """
        update the item count
        """
        try:
            self.ttcount, countQuery = self.tt.count()
            self.count_query_view.show_query(countQuery)
            content = "❓" if self.tt.error else f"{self.ttcount} instances found"
            with self.item_row:
                self.item_count_view.content = content
            if not self.tt.error:
                self.update_property_query_view(total=self.ttcount)

        except Exception as ex:
            self.handle_exception(ex)

    def update_property_query_view(self, total: int):
        """
        update the property query view
        """
        try:
            pareto = self.config.pareto
            if total is not None:
                min_count = round(total * self.config.min_property_frequency / 100.0)
            else:
                min_count = 0
            msg = f"searching properties with at least {min_count} usages"
            with self.main_container:
                ui.notify(msg)
            mfp_query = self.tt.mostFrequentPropertiesQuery(minCount=min_count)
            self.property_query_view.show_query(mfp_query.query)
            self.update_properties_table(mfp_query)
        except Exception as ex:
            self.handle_exception(ex)
            
    def prepare_generation_specs(self):
        """
        prepare the interactive generation specification
        """
        # render generation spec columns as checkboxes
        for col in self.property_selection.checkbox_cols:
        #    self.property_grid.set_checkbox_renderer(col)
            pass
        for row in self.property_selection.propertyList:
            has_min_frequency=self.property_selection.hasMinFrequency(row)
            row["count"]=True
            if has_min_frequency:
                if row["type"] == "WikibaseItem":
                    row["label"]=True
            else:
                row["ignore"]=True
            pass
        col_def=self.property_grid.get_column_def("#")
        col_def["headerCheckboxSelection"]=True
        self.property_grid.update()
        self.property_grid.select_all_rows()
        self.generate_button.enable()
            
    def update_properties_table(self, mfp_query):
        """
        update my properties table

        Args:
            mfp_query(Query): the query for the most frequently used properties
        """
        try:
            with self.query_display_container:
                msg = f"running query for most frequently used properties of {str(self.tt)} ..."
                ui.notify(msg)
            try:
                property_lod = self.tt.sparql.queryAsListOfDicts(mfp_query.query)
            except EndPointInternalError as ex:
                if self.isTimeoutException(ex):
                    raise Exception("Query timeout of the property table query")
            self.property_selection = PropertySelection(
                property_lod,
                total=self.ttcount,
                paretoLevels=self.config.pareto_levels,
                minFrequency=self.config.min_property_frequency,
            )
            self.property_selection.prepare()
            with self.property_grid_row:
                self.view_lod = self.property_selection.propertyList
                self.property_grid.load_lod(self.view_lod)
                self.property_grid.set_checkbox_selection("#")
                self.property_grid.update()
            self.update_property_stats()
            self.prepare_generation_specs()
        except Exception as ex:
            self.handle_exception(ex)
            
    def update_property_stats(self):
        """
        update the property statistics
        """
        try:
            count = len(self.property_selection.propertyList)
            with self.main_container:
                ui.notify(f"Getting property statistics for {count} properties")
                self.progress_bar.total = count
                self.progress_bar.reset()
            for row in self.property_selection.propertyList:
                # run in background
                asyncio.run(run.io_bound(self.get_stats_rows,[row]))
                with self.main_container:
                    self.progress_bar.update(1)
            pass
            with self.main_container:  
                self.progress_bar.reset()
                ui.notify(f"Done getting statistics for {count} properties")   
        except Exception as ex:
            self.handle_exception(ex)
            
    async def on_property_grid_selection_change(self, event):
        """
        the property grid selection has changed
        """
        source = event.args.get("source", None)
        if source == "checkboxSelected":
            selected_rows = await self.property_grid.get_selected_rows()
            ui.notify(f"Selection changed: {selected_rows}")

    async def update_item_link_view(self):
        with self.item_row:
            item_text = self.tt.item.asText(long=True)
            item_url = self.tt.item.url
            item_link = Link.create(item_url, item_text)
            self.item_link_view.content = item_link

    async def update_display(self):
        """ 
        update the display
        """
        try:
            if self.webserver.log_view:
                self.webserver.log_view.clear()
            self.tt = self.createTrulyTabular(self.qid)
            for query_view in self.count_query_view, self.property_query_view:
                query_view.sparql_endpoint = self.config.sparql_endpoint
            # Initialize TrulyTabular with the qid
            await self.update_item_link_view()
            await run.io_bound(self.update_item_count_view)
        except Exception as ex:
            self.handle_exception(ex)