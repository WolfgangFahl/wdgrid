"""
Created on 2024-01-04

@author: wf
"""
from ngwidgets.webserver import NiceGuiWebserver
from ngwidgets.widgets import Link
from lodstorage.query import Query, Endpoint
from nicegui import ui

class QueryView():
    """
    widget to display queries
    """
    
    def __init__(self,webserver:NiceGuiWebserver,name:str,sparql_endpoint:Endpoint):
        """
        Initialize the QueryView object with a given webserver and name.

        Args:
            webserver (NiceGuiWebserver): The web server instance to be used.
            name (str): The name identifier for the query display.
            sparql_endpoint(endpoint): the SPARQL endpoint to use
        """
        self.webserver=webserver
        self.name=name
        self.setup()
        self.sparql_query=""
        self.sparql_markup=""
        self.sparql_endpoint=sparql_endpoint
        
    def setup(self):
        """Set up the UI components for the query display."""
        with ui.expansion(self.name) as self.expansion:
            self.code_view=ui.code("",language='sparql')
        with ui.row() as self.link_row:    
            self.try_it_link_view=ui.html()
            self.download_link_view=ui.html()
            pass
        
    def show_query(self,sparql_query:str):
        """
        Update the display with a new SPARQL query.

        Args:
            sparql_query (str): The SPARQL query string to be displayed.
        """
        self.sparql_query=sparql_query.strip()
        # we might need to change the endpoint
        self.query=Query(name=self.name,query=sparql_query)
        if self.sparql_endpoint:
            try_it_url_encoded=self.query.getTryItUrl(baseurl=self.sparql_endpoint.website,database=self.sparql_endpoint.database)
            with self.link_row:
                try_it_link=Link.create(try_it_url_encoded,"try it!")
                self.try_it_link_view.content=try_it_link
        with self.expansion:
            self.code_view.markdown.content=f"""```sparql
    {sparql_query}
    ```"""
            self.code_view.update()
        pass
