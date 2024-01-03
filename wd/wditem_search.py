"""
Created on 2024-01-03

@author: wf
"""
import asyncio
from nicegui import ui
from wd.wdsearch import WikidataSearch
from ngwidgets.widgets import Lang,Link

class WikidataItemSearch():
    """
    wikidata item search 
    """
    
    def __init__(self,webserver):
        """
        constructor
        """
        self.webserver=webserver
        self.lang="en"
        self.wd_search=WikidataSearch(self.lang)
        self.search_debounce_task = None
        self.keyStrokeTime=0.65 # minimum time in seconds to wait between keystrokes before starting searching
        self.languages = Lang.get_language_dict()
        self.search_result_row=None
        self.setup()
        
    def setup(self):
        with ui.card().style('width: 25%'):
            with ui.row():
                # Create a dropdown for language selection with the default language selected
                # Bind the label text to the selection's value, so it updates automatically
                ui.select(self.languages,with_input=True, value=self.lang).bind_value(self, 'lang')
            with ui.row():
                self.search_input=ui.input(label='search',on_change=self.on_search_change)
            with ui.row() as self.search_result_row:    
                self.search_result=ui.html()
          
    async def on_search_change(self,_args):
        """
        react on changes in the search input
        """
        # Cancel the existing search task if it's still waiting
        if self.search_debounce_task:
            self.search_debounce_task.cancel()

        # Create a new task for the new search
        self.search_debounce_task = asyncio.create_task(self.debounced_search())
       
    async def debounced_search(self):
        """
        Waits for a period of inactivity and then performs the search.
        """
        try:
            # Wait for the debounce period (keyStrokeTime)
            await asyncio.sleep(self.keyStrokeTime)
            search_for=self.search_input.value
            if self.search_result_row:
                with self.search_result_row:
                    ui.notify(f"searching wikidata for {search_for} ({self.lang})...")
                    self.wd_search.language=self.lang
                    wd_search_result=self.wd_search.searchOptions(search_for)
                    html=self.get_html(wd_search_result)
                    self.search_result.content=html
        except asyncio.CancelledError:
            # The search was cancelled because of new input, so just quietly exit
            pass
        except BaseException as ex:
            self.webserver.handle_exception(ex,self.webserver)
 
    def get_html(self,wd_search_result)->str:
        """
        get the html markup for the given search result
        
        
        """
        markup=""
        delim=""
        for qid,itemLabel,desc in wd_search_result:
            text=f"{itemLabel} ({qid}) {desc}"
            url=f"https://www.wikidata.org/wiki/{qid}"
            link=Link.create(url,text)
            markup=f"{markup}{delim}{link}"
            delim="<br>"
        return markup
          
