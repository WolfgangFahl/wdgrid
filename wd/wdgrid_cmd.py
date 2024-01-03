"""
Created on 2024-01-03

@author: wf
"""
from ngwidgets.cmd import WebserverCmd
from wd.webserver import WdgridWebServer
import sys
from argparse import ArgumentParser

class WdgridCmd(WebserverCmd):
    """
    Command line for wiki data grid web server
    """
    
    def getArgParser(self,description:str,version_msg)->ArgumentParser:
        """
        override the default argparser call
        """        
        parser=super().getArgParser(description, version_msg)
        #parser.add_argument("-v", "--verbose", action="store_true", help="show verbose output [default: %(default)s]")
        #parser.add_argument("-rp", "--root_path",default=ScanWebServer.examples_path(),help="path to example pdf files [default: %(default)s]")
        #parser.add_argument("-wc", "--webcam",help="url of webcam for scans [default: %(default)s]")
        return parser
    
def main(argv:list=None):
    """
    main call
    """
    cmd=WdgridCmd(config=WdgridWebServer.get_config(),webserver_cls=WdgridWebServer)
    exit_code=cmd.cmd_main(argv)
    return exit_code
        
DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())
