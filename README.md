# SciKGraph

A web application that helps researchers explore and understand scientific
fields by building, clustering, and visualizing **knowledge graphs** from
corpora of scientific text.

Documents are semantically annotated through the [Babelfy](https://babelfy.io)
API, the resulting concepts are connected by co-occurrence, and the graph is
clustered with the [OClustR](https://doi.org/10.1016/j.patrec.2013.04.005)
algorithm. Visualization happens entirely in the browser via Cytoscape.js.

## Requirements

- **Python 3.10+**
- **Linux x86-64** — required by the bundled `static/onmi` binary used for
  cluster comparison (see [Native dependency: oNMI](#native-dependency-onmi))
- A free [Babelfy API key](https://babelnet.org/register) (used during graph
  construction)

## Installation

### From PyPI

```bash
python -m venv scikgraph_env
source scikgraph_env/bin/activate
pip install scikgraph
```

### From source

```bash
git clone https://github.com/your-org/SciKGraph.git
cd SciKGraph
python -m venv scikgraph_env
source scikgraph_env/bin/activate
pip install -e .
```

`pip install -e .` installs the package in editable mode using the metadata
in [`pyproject.toml`](pyproject.toml) and the dependencies declared there
(no need for a separate `pip install -r requirements.txt`).

## Running the application

After either install path, with the virtualenv activated, run:

```bash
scikgraph
```

This starts the app on <http://localhost:8080/>. Use `--host` and `--port`
to override the defaults, e.g. `scikgraph --port 9000`.

Equivalent commands, if you prefer them:

```bash
python -m scikgraph
waitress-serve --call 'scikgraph:create_app'
```

## Using the web app

The app is organised around three pages:

- **`/create`** — upload `.txt` documents, paste your Babelfy key, and click
  *Construct Graph*. Once a graph exists you can iterate via *Pre-process*
  (vertex/edge thresholds) and *Cluster Graph* (OClustR).
- **`/analyze`** — modularity, key-concept and key-phrase extraction, cluster
  reduction, and the cluster-relation graph view.
- **`/evolution`** — load two saved `.sckg` sessions to compute their cover
  similarity (oNMI) and visualise overlapping clusters.

### Visualization settings

- **Layout** — choose one of: `spring`, `cose`, `concentric`, `circle`, `grid`.
- **Render graph** — turn the visualization on or off.
- **Update visualization setting** — apply the current settings.

The Construct Graph form has its own *Render after submit* checkbox that
controls whether the visualization is updated as part of that specific action.

## Native dependency: oNMI

[`static/onmi`](static/onmi) is a precompiled **Linux x86-64** build of
[Aaron McDaid's Overlapping NMI tool](https://github.com/aaronmcdaid/Overlapping-NMI),
used by the *Covers Similarity* feature on the Track Evolution page to compare
two cluster covers.

- It is **not** a Python package and cannot be installed via pip.
- It only runs on **Linux x86-64**. On other platforms, recompile the binary
  from the upstream source and replace the file, otherwise the *Covers
  Similarity* button will fail.

## Architecture

- **Backend**: Flask application factory in [`__init__.py`](__init__.py).
- **Graph construction**: [`SciKGraph.py`](SciKGraph.py) — text parsing,
  Babelfy disambiguation, co-occurrence graph building, save/open `.sckg`.
- **Clustering**: [`OClustR.py`](OClustR.py) — the OClustR overlapping
  clustering algorithm.
- **Analyses**: [`Analyses.py`](Analyses.py) — modularity, key-phrase
  extraction (NLTK), cover comparison (oNMI).
- **Frontend**: vanilla JS in [`static/main.js`](static/main.js) and
  [`static/render-panel.js`](static/render-panel.js); per-render assets
  [`static/networks.js`](static/networks.js) and
  [`static/styles.js`](static/styles.js) are regenerated on every render and
  should not be hand-edited.

## License

This project (the SciKGraph code, templates, and documentation) is distributed
under the **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0
International** license (CC BY-NC-ND 4.0). You may share it with attribution
for **non-commercial purposes only** and may not distribute modified versions.
See <https://creativecommons.org/licenses/by-nc-nd/4.0/> for the full terms.

### Third-Party Notices

This repository bundles the following third-party libraries inside
[`static/vendor.js`](static/vendor.js):

- **Cytoscape.js 2.4.6** — Copyright © The Cytoscape Consortium.
  Licensed under the [MIT License](https://github.com/cytoscape/cytoscape.js/blob/master/LICENSE).
- **jQuery** — Copyright © JS Foundation and other contributors.
  Licensed under the [MIT License](https://jquery.org/license/).

The MIT license requires that its copyright and permission notice be included
when the software is redistributed. They are reproduced via the references
above and apply to the bundled minified code in `static/vendor.js`.

[`static/onmi`](static/onmi) is a precompiled binary of
[Overlapping NMI](https://github.com/aaronmcdaid/Overlapping-NMI) by
Aaron McDaid, distributed under its upstream license. It is invoked as a
separate process and not linked into SciKGraph at the source level.

## Citing SciKGraph

If you use SciKGraph in academic work, please cite both:

```bibtex
@article{scikgraphApp-Tosi,
  author  = {Mauro Dalle Lucca Tosi and Julio Cesar dos Reis},
  title   = {Understanding the evolution of a scientific field by clustering and visualizing knowledge graphs},
  journal = {Journal of Information Science},
  year    = {2020},
  doi     = {10.1177/0165551520937915},
  url     = {https://doi.org/10.1177/0165551520937915}
}

@article{tosi2021scikgraph,
  title     = {SciKGraph: A knowledge graph approach to structure a scientific field},
  author    = {Tosi, Mauro Dalle Lucca and dos Reis, Julio Cesar},
  journal   = {Journal of Informetrics},
  volume    = {15},
  number    = {1},
  pages     = {101109},
  year      = {2021},
  publisher = {Elsevier},
  doi       = {10.1016/j.joi.2020.101109},
  url       = {https://doi.org/10.1016/j.joi.2020.101109}
}
```
