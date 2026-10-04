"""
Created on 2026-10-04

@author: wf
"""

from ngwidgets.webserver_test import WebserverTest

from wd.wdgrid_cmd import WdgridCmd
from wd.webserver import WdgridWebServer


class TestTrulyTabularApi(WebserverTest):
    """
    test the truly tabular REST API
    see https://github.com/WolfgangFahl/wdgrid/issues/6
    """

    def setUp(self, debug=False, profile=True):
        WebserverTest.setUp(
            self, WdgridWebServer, WdgridCmd, debug=debug, profile=profile
        )

    def test_openapi_has_entries(self):
        """
        test that the OpenAPI spec has wdgrid metadata and path entries
        """
        spec = self.ws.app.openapi()
        self.assertEqual("wdgrid", spec["info"]["title"])
        paths = spec["paths"]
        if self.debug:
            print(list(paths.keys()))
        self.assertIn("/api/tt/{qid}", paths)

    def test_api_truly_tabular(self):
        """
        test the /api/tt/{qid} endpoint with car carrier
        """
        response = self.client.get("/api/tt/Q356847")
        self.assertEqual(200, response.status_code)
        analysis = response.json()
        if self.debug:
            print(analysis)
        self.assertEqual("Q356847", analysis["qid"])
        self.assertEqual("car carrier", analysis["label"])
        self.assertTrue(analysis["count"] > 400)
        properties = analysis["properties"]
        self.assertTrue(len(properties) > 0)
        for prop in properties:
            self.assertTrue(prop["propertyId"].startswith("P"))
            self.assertTrue(prop["%"] >= 20.0)

    def test_api_unknown_endpoint(self):
        """
        test that an unknown endpoint leads to a 404
        """
        response = self.client.get("/api/tt/Q356847?endpoint=unknown")
        self.assertEqual(404, response.status_code)
