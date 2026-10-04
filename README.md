# wdgrid
nicegui based wikidata grid and sync

| | |
| :--- | :--- |
| **PyPi** | [![PyPI Status](https://img.shields.io/pypi/v/wdgrid.svg)](https://pypi.python.org/pypi/wdgrid/) [![License](https://img.shields.io/github/license/WolfgangFahl/wdgrid.svg)](https://www.apache.org/licenses/LICENSE-2.0) [![pypi](https://img.shields.io/pypi/pyversions/wdgrid)](https://pypi.org/project/wdgrid/) [![format](https://img.shields.io/pypi/format/wdgrid)](https://pypi.org/project/wdgrid/) [![downloads](https://img.shields.io/pypi/dd/wdgrid)](https://pypi.org/project/wdgrid/) |
| **GitHub** | [![Github Actions Build](https://github.com/WolfgangFahl/wdgrid/actions/workflows/build.yml/badge.svg)](https://github.com/WolfgangFahl/wdgrid/actions/workflows/build.yml) [![Release](https://img.shields.io/github/v/release/WolfgangFahl/wdgrid)](https://github.com/WolfgangFahl/wdgrid/releases) [![Contributors](https://img.shields.io/github/contributors/WolfgangFahl/wdgrid)](https://github.com/WolfgangFahl/wdgrid/graphs/contributors) [![Last Commit](https://img.shields.io/github/last-commit/WolfgangFahl/wdgrid)](https://github.com/WolfgangFahl/wdgrid/commits/) [![GitHub issues](https://img.shields.io/github/issues/WolfgangFahl/wdgrid.svg)](https://github.com/WolfgangFahl/wdgrid/issues) [![GitHub closed issues](https://img.shields.io/github/issues-closed/WolfgangFahl/wdgrid.svg)](https://github.com/WolfgangFahl/wdgrid/issues/?q=is%3Aissue+is%3Aclosed) |
| **Code** | [![style-black](https://img.shields.io/badge/%20style-black-000000.svg)](https://github.com/psf/black) [![imports-isort](https://img.shields.io/badge/%20imports-isort-%231674b1)](https://pycqa.github.io/isort/) [![Join the discussion at https://github.com/WolfgangFahl/wdgrid/discussions](https://img.shields.io/github/discussions/WolfgangFahl/wdgrid)](https://github.com/WolfgangFahl/wdgrid/discussions) |
| **Docs** | [![API Docs](https://img.shields.io/badge/API-Documentation-blue)](https://WolfgangFahl.github.io/wdgrid/) [![formatter-docformatter](https://img.shields.io/badge/%20formatter-docformatter-fedcba.svg)](https://github.com/PyCQA/docformatter) [![style-google](https://img.shields.io/badge/%20style-google-3666d6.svg)](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings) |
| **Cite** | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20035246.svg)](https://doi.org/10.5281/zenodo.20035246) |

[![BITPlan](http://wiki.bitplan.com/images/wiki/thumb/3/38/BITPlanLogoFontLessTransparent.png/198px-BITPlanLogoFontLessTransparent.png)](http://www.bitplan.com)

## Cite as

If you use wdgrid in your research, please cite it via its Zenodo concept DOI
(which always resolves to the latest version):

> Fahl, W. *wdgrid — NiceGUI-based Wikidata grid display and sync.*
> Zenodo. https://doi.org/10.5281/zenodo.20035246

Machine-readable metadata is available in [`CITATION.cff`](./CITATION.cff);
GitHub's "Cite this repository" button and Zenodo pick it up automatically.
For a specific release, use the version DOI shown on the corresponding
[Zenodo record](https://doi.org/10.5281/zenodo.20035246).

## Demo
* [RWTH Aachen i5](https://wdgrid.wikidata.dbis.rwth-aachen.de/)
* [BITPlan](https://wdgrid.bitplan.com)

## REST API
The truly tabular analysis is available as JSON via `/api/tt/{qid}`.
The Swagger UI is at `/docs` of each demo, e.g. https://wdgrid.bitplan.com/docs

```bash
# instance count and property frequencies of car carrier (Q356847)
curl -s https://wdgrid.bitplan.com/api/tt/Q356847

# ship (Q11446): only properties used by at least 50 % of the instances
curl -s "https://wdgrid.bitplan.com/api/tt/Q11446?min_frequency=50"

# car carrier including the instances of its subclasses
curl -s "https://wdgrid.bitplan.com/api/tt/Q356847?predicate=wdt:P31/wdt:P279*"

# same analysis on the RWTH Aachen i5 demo
curl -s https://wdgrid.wikidata.dbis.rwth-aachen.de/api/tt/Q356847
```

Query parameters: `predicate` (default `wdt:P31`), `lang` (default `en`),
`endpoint` (name of the SPARQL endpoint), `min_frequency` (default `20.0`),
`stats` (default `false`, adds the non tabular statistics with one query per property).

## Links
* [Python](https://www.python.org/)
* [wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page)
* [wikidata query service](https://query.wikidata.org/)
* [qlever wikidata query service](https://qlever.cs.uni-freiburg.de/wikidata)

## Documentation
[Wiki](http://wiki.bitplan.com/index.php/Wdgrid)
