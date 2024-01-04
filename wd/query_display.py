"""
Created on 2024-01-04

@author: wf
"""
from ngwidgets.webserver import NiceGuiWebserver
from nicegui import ui
class QueryDisplay():
    """
    display queries
    """
    
    def __init__(self,webserver:NiceGuiWebserver,name:str):
        self.webserver=webserver
        self.name=name
        self.setup()
        self.sparql_query=""
        self.sparql_markup=""
        
    def setup(self):
        with ui.expansion(self.name) as self.expansion:
            self.code_view=ui.code("",language='sparql')
            pass
        
    def show_query(self,sparql_query:str):
        self.sparql_query=sparql_query
        self.code_view.markdown.content=f"""```sparql
{sparql_query}
```"""
        self.code_view.update()
        pass
