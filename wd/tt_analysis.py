"""
Created on 2026-10-04

@author: wf
"""

from typing import Any, Dict, Optional

from ez_wikidata.trulytabular import TrulyTabular

from wd.truly_tabular_display import PropertySelection, TrulyTabularConfig


class TrulyTabularAnalysis:
    """
    UI independent truly tabular analysis of a Wikidata item
    """

    def __init__(self, config: TrulyTabularConfig, debug: bool = False):
        """
        constructor

        Args:
            config(TrulyTabularConfig): the configuration to use
            debug(bool): if True switch on debugging
        """
        self.config = config
        self.debug = debug

    def analyze(
        self,
        qid: str,
        search_predicate: str = "wdt:P31",
        lang: Optional[str] = None,
        endpoint_name: Optional[str] = None,
        min_frequency: Optional[float] = None,
        with_stats: bool = False,
    ) -> Dict[str, Any]:
        """
        analyze the given Wikidata item

        Args:
            qid(str): the Wikidata id of the item to analyze e.g. Q356847 car carrier
            search_predicate(str): the search predicate to use e.g. instance of
            lang(str): the language for labels - default from config
            endpoint_name(str): the name of the SPARQL endpoint - default from config
            min_frequency(float): the minimum frequency of the properties in percent - default from config
            with_stats(bool): if True add the non tabular statistics per property (one query per property)

        Returns:
            dict: the item, its instance count and the property frequencies

        Raises:
            KeyError: if the endpoint name is unknown
        """
        if lang is None:
            lang = self.config.lang
        if endpoint_name is None:
            endpoint_name = self.config.endpoint_name
        if min_frequency is None:
            min_frequency = self.config.min_property_frequency
        endpoint = self.config.endpoints.get(endpoint_name)
        if endpoint is None:
            raise KeyError(f"unknown endpoint {endpoint_name}")
        tt = TrulyTabular(
            itemQid=qid,
            search_predicate=search_predicate,
            endpointConf=endpoint,
            lang=lang,
            debug=self.debug,
        )
        count, _count_query = tt.count()
        if tt.error:
            raise tt.error
        min_count = round(count * min_frequency / 100.0)
        mfp_query = tt.mostFrequentPropertiesQuery(minCount=min_count)
        property_lod = tt.sparql.queryAsListOfDicts(mfp_query.query)
        properties = []
        if property_lod:
            property_selection = PropertySelection(
                property_lod,
                total=count,
                paretoLevels=self.config.pareto_levels,
                minFrequency=min_frequency,
            )
            for record in property_selection.propertyList:
                property_id = record["prop"].replace(
                    "http://www.wikidata.org/entity/", ""
                )
                prop = {
                    "propertyId": property_id,
                    "property": record["propLabel"],
                    "type": record["wbType"].replace("http://wikiba.se/ontology#", ""),
                    "count": int(record["count"]),
                    "%": float(record["%"]),
                    "pareto": record["pareto"],
                }
                if with_stats:
                    wd_property = tt.wpm.get_properties_by_ids([property_id]).get(
                        property_id
                    )
                    if wd_property is not None:
                        stats_row = tt.genWdPropertyStatistic(
                            wd_property, count, withQuery=False
                        )
                        for col in ["1", "maxf", "non tabular", "non tabular%"]:
                            prop[col] = stats_row.get(col)
                properties.append(prop)
        analysis = {
            "qid": qid,
            "label": tt.item.qlabel,
            "description": tt.item.description,
            "search_predicate": search_predicate,
            "endpoint": endpoint_name,
            "count": count,
            "min_frequency": min_frequency,
            "properties": properties,
        }
        return analysis
