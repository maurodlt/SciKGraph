from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
import scikgraph.SciKGraph as skg
import pickle
import scikgraph.OClustR as OCR
import json
import scikgraph.Analyses
import copy
import sys
import networkx as nx


def _server_layout_spring(g):
    pos = nx.spring_layout(g, iterations=50, seed=42)
    return {str(n): {"x": float(p[0]) * 1000.0, "y": float(p[1]) * 1000.0}
            for n, p in pos.items()}


# side: "browser" (Cytoscape.js computes positions on load) or "server"
# (positions are pre-computed and embedded in networks.js; browser renders preset).
LAYOUTS = {
    "spring":     {"side": "server", "fn": _server_layout_spring},
    "cose":       {"side": "browser"},
    "concentric": {"side": "browser"},
    "circle":     {"side": "browser"},
    "grid":       {"side": "browser"},
}
DEFAULT_LAYOUT = "spring"

#from IPython.display import Image


def create_app():
    app = Flask(__name__)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['SECRET_KEY'] = os.urandom(24)
    UPLOAD_FOLDER = '/home/mauro/Documents/flask_app/static/temp/'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    Bootstrap(app)
    sKGraph = skg.SciKGraph()
    sKGraph1 = skg.SciKGraph()
    sKGraph2 = skg.SciKGraph()
    maxNodeWeight = 10
    minNodeWeight = 1
    maxEdgeWeight = 1
    minEdgeWeight = 10
    mediumNodeWeight = int((maxNodeWeight + minNodeWeight) / 2)

    STYLES_BASE_MARKER = '},{},{}'

    def _nx_to_cyjs_elements(g, clusters=None, positions=None):
        elements = {"nodes": [], "edges": []}
        parent_of = {}
        if clusters:
            for i, members in enumerate(clusters):
                pid = 'group' + str(i)
                elements["nodes"].append({"data": {
                    "id": pid, "SUID": pid, "name": pid,
                    "shared_name": pid, "group_node": True,
                }})
                for n in members:
                    parent_of[str(n)] = pid
        for nid, attrs in g.nodes(data=True):
            sid = str(nid)
            data = {"id": sid, "SUID": sid, "name": sid, "shared_name": sid}
            for k, v in attrs.items():
                if k == 'dicionario' and isinstance(v, str):
                    data[k] = v.replace('+', ' ')
                else:
                    data[k] = v
            if sid in parent_of:
                data["parent"] = parent_of[sid]
            element = {"data": data}
            if positions is not None and sid in positions:
                element["position"] = positions[sid]
            elements["nodes"].append(element)
        for u, v, attrs in g.edges(data=True):
            edge_data = {"source": str(u), "target": str(v)}
            edge_data.update(attrs)
            elements["edges"].append({"data": edge_data})
        return elements

    def _resolve_layout(layout_name):
        return LAYOUTS.get(layout_name, LAYOUTS[DEFAULT_LAYOUT])

    def _write_networks_js(g, clusters=None, layout_name=DEFAULT_LAYOUT):
        spec = _resolve_layout(layout_name)
        if spec["side"] == "server":
            positions = spec["fn"](g)
            browser_layout = "preset"
        else:
            positions = None
            browser_layout = layout_name
        elements = _nx_to_cyjs_elements(g, clusters, positions=positions)
        payload = {"SciKGraph": {"elements": elements, "layout": browser_layout}}
        path = os.path.join(app.root_path, 'static', 'networks.js')
        with open(path, 'w') as f:
            f.write('var networks = ' + json.dumps(payload) + ';')
        sKGraph.visualization_enabled = True
        return elements

    def _write_disabled_networks_js():
        """Write a marker that tells main.js to show 'Visualization disabled'."""
        payload = {"SciKGraph": {"disabled": True}}
        path = os.path.join(app.root_path, 'static', 'networks.js')
        with open(path, 'w') as f:
            f.write('var networks = ' + json.dumps(payload) + ';')
        sKGraph.visualization_enabled = False

    def _current_target_graph():
        """Pick the most relevant graph for the global render panel."""
        if len(sKGraph.pre_processed_graph) > 0:
            return sKGraph.pre_processed_graph
        if not isinstance(sKGraph.sciKGraph, int):
            return sKGraph.sciKGraph
        return None

    def _read_styles_base():
        path = os.path.join(app.root_path, 'static', 'styles.js')
        with open(path, 'r') as f:
            lines = f.readlines()
        cut = 0
        for i, ln in enumerate(lines):
            if STYLES_BASE_MARKER in ln:
                cut = i
        return path, lines[:cut + 1]

    def _style_node_size(min_peso, max_peso, min_size, max_size):
        return (',{"selector":"node[ peso <= ' + str(min_peso) + ']",'
                '"css":{"height":' + str(min_size) + '.0,"width":' + str(min_size) + '.0}},'
                '{"selector":"node[ peso >= ' + str(max_peso) + ' ]",'
                '"css":{"height":' + str(max_size) + '.0,"width":' + str(max_size) + '.0}},'
                '{"selector":"node[peso > ' + str(min_peso) + '][peso < ' + str(max_peso) + ']",'
                '"css":{"height":"mapData(peso,' + str(min_peso) + ',' + str(max_peso) + ',' + str(min_size) + ',' + str(max_size) + ')",'
                '"width":"mapData(peso,' + str(min_peso) + ',' + str(max_peso) + ',' + str(min_size) + ',' + str(max_size) + ')"}}')

    def _style_gradient_color(min_peso, medium_peso, max_peso):
        return (',{"selector":"node[peso >= ' + str(max_peso) + ']",'
                '"css":{"background-color":"rgb(102,37,6)"}},'
                '{"selector":"node[peso >= ' + str(medium_peso) + '][peso < ' + str(max_peso) + ']",'
                '"css":{"background-color":"mapData(peso,' + str(medium_peso) + ',' + str(max_peso) + ',rgb(254,153,41),rgb(153,52,4))"}},'
                '{"selector":"node[peso > ' + str(min_peso) + '][peso < ' + str(medium_peso) + ']",'
                '"css":{"background-color":"mapData(peso,' + str(min_peso) + ',' + str(medium_peso) + ',rgb(255,247,188),rgb(254,153,41))"}},'
                '{"selector":"node[peso <= ' + str(min_peso) + ']",'
                '"css":{"background-color":"rgb(255,247,188)"}}')

    def _style_cluster_index_colors():
        # Evolution view: fixed colors for the three evolution clusters (1/2/3).
        return (',{"selector":"node[clusters = \'1.0\']","css":{"background-color":"rgb(0,0,255)"}},'
                '{"selector":"node[clusters = \'2.0\']","css":{"background-color":"rgb(255,255,51)"}},'
                '{"selector":"node[clusters = \'3.0\']","css":{"background-color":"rgb(0,255,51)"}}')

    def _style_label_size(min_peso, max_peso, min_label, max_label):
        return (',{"selector":"node[peso >= ' + str(max_peso) + ']",'
                '"css":{"font-size":' + str(max_label) + '}},'
                '{"selector":"node[peso > ' + str(min_peso) + '][peso < ' + str(max_peso) + ']",'
                '"css":{"font-size":"mapData(peso,' + str(min_peso) + ',' + str(max_peso) + ',' + str(min_label) + ',' + str(max_label) + ')"}},'
                '{"selector":"node[peso <= ' + str(min_peso) + ']",'
                '"css":{"font-size":' + str(min_label) + '}}')

    def _style_edge_width(min_edge, max_edge, min_width, max_width):
        return (',{"selector":"edge[ weight >= ' + str(max_edge) + ']",'
                '"css":{"width":' + str(max_width) + '.0}},'
                '{"selector":"edge[ weight <= ' + str(min_edge) + ' ]",'
                '"css":{"width":' + str(min_width) + '.0}},'
                '{"selector":"edge[ weight = 0 ]","css":{"width":0.0}},'
                '{"selector":"edge[weight > ' + str(min_edge) + '][weight < ' + str(max_edge) + ']",'
                '"css":{"width":"mapData(weight,' + str(min_edge) + ',' + str(max_edge) + ',' + str(min_width) + ',' + str(max_width) + ')"}}')

    def _style_group_nodes(group_ids):
        frag = ''
        for gid in group_ids:
            frag += (',{"selector":"node[ id = \'' + gid + '\' ]",'
                     '"css":{"shape":"rectangle","background-opacity":0.19607843137254902,'
                     '"padding":"10px","text-valign":"top","text-halign":"center"}}')
        return frag

    def _write_styles(fragments):
        path, base = _read_styles_base()
        with open(path, 'w') as f:
            f.writelines(base)
            for frag in fragments:
                f.write(frag)
            f.write("]\n} ]")

    def plot_network(g, clusters=None,
                     min_peso=None, max_peso=None, medium_peso=None,
                     layout_name=None):
        if min_peso is None or max_peso is None:
            max_peso, min_peso = sKGraph.marginalWeights(g)
            medium_peso = int((max_peso + min_peso) / 2)
        group_ids = ['group' + str(i) for i in range(len(clusters))] if clusters else []
        _write_networks_js(g, clusters=clusters,
                           layout_name=layout_name or DEFAULT_LAYOUT)
        _write_styles([
            _style_node_size(min_peso, max_peso, 10, 200),
            _style_gradient_color(min_peso, medium_peso, max_peso),
            _style_label_size(min_peso, max_peso, 10, 200 / 4),
            _style_group_nodes(group_ids),
        ])

    def plot_evolution_graph(g, clusters=None,
                             min_peso=None, max_peso=None, medium_peso=None,
                             layout_name=None):
        if min_peso is None or max_peso is None:
            max_peso, min_peso = sKGraph.marginalWeights(g)
            medium_peso = int((max_peso + min_peso) / 2)
        group_ids = ['group' + str(i) for i in range(len(clusters))] if clusters else []
        _write_networks_js(g, clusters=clusters,
                           layout_name=layout_name or DEFAULT_LAYOUT)
        _write_styles([
            _style_node_size(min_peso, max_peso, 10, 100),
            _style_cluster_index_colors(),
            _style_label_size(min_peso, max_peso, 10, 100 / 4),
            _style_group_nodes(group_ids),
        ])

    def plot_relation_graph(g, min_peso, max_peso, medium_peso,
                            min_edge, max_edge, layout_name=None):
        _write_networks_js(g, clusters=None,
                           layout_name=layout_name or "circle")
        _write_styles([
            _style_node_size(min_peso, max_peso, 5, 50),
            _style_edge_width(min_edge, max_edge, 1, 10),
            _style_gradient_color(min_peso, medium_peso, max_peso),
            _style_label_size(min_peso, max_peso, 10, 50 / 4),
        ])

    def _read_render_options(target_skg=None):
        """Returns (layout_name, render_flag). Reads layoutSelect and
        renderVisualizationCheck from the current request form. The hidden
        marker `renderVisualizationFormMarker` lets us tell "checkbox absent"
        (default = render) from "checkbox unchecked" (skip)."""
        owner = target_skg if target_skg is not None else sKGraph
        layout = request.form.get('layoutSelect') or getattr(owner, 'last_layout', None) or DEFAULT_LAYOUT
        if layout not in LAYOUTS:
            layout = DEFAULT_LAYOUT
        owner.last_layout = layout
        if 'renderVisualizationFormMarker' in request.form:
            render = 'renderVisualizationCheck' in request.form
        else:
            render = True
        return layout, render

    @app.context_processor
    def inject_render_defaults():
        # Surfaces the current layout choice + render state to all templates.
        return {
            'last_layout': getattr(sKGraph, 'last_layout', DEFAULT_LAYOUT),
            'available_layouts': list(LAYOUTS.keys()),
            'render_enabled': getattr(sKGraph, 'visualization_enabled', True),
        }

    @app.route('/create', methods=['POST', 'GET'])
    def create():
        global maxNodeWeight, minNodeWeight, mediumNodeWeight
        ### -----------------------------------    Construct Graph          -----------------------------------------###
        if request.method == 'POST':
            layout_name, render_flag = _read_render_options()

            ### ------------------------------    Update Visualization Setting    ------------------------------###
            if 'updateVisualizationButton' in request.form:
                sKGraph.visualization_enabled = render_flag
                target = _current_target_graph()
                if not render_flag:
                    _write_disabled_networks_js()
                elif target is not None:
                    plot_network(target,
                                 clusters=sKGraph.crisp_clusters or None,
                                 layout_name=layout_name)
                sorted_concepts = sKGraph.rank(g=target, dictionaryCodeMerged=sKGraph.dictionaryCodeMerged) if target is not None else []
                return render_template('createSciKGraph.html', key_concepts=sorted_concepts[:200], documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=0 if target is None else len(target), total_edges=0 if target is None else len(target.edges()), deleted_edges=len(sKGraph.deleted_edges), deleted_concepts=len(sKGraph.deleted_nodes), deleted_isolated_concepts=len(sKGraph.deleted_isolated_nodes))

            elif 'languageSelect' in request.form:
                documentsList = []
                documentsNamesList = []
                files = request.files.getlist("documentPathsInput")
                for file in files:
                    documentsList.append(file.read())
                    documentsNamesList.append(file.filename)

                babelfy_key = request.form.get('babelfyKeyInput')

                language = request.form.get('languageSelect')

                distance = request.form.get('distanceInput')

                if 'clusterIfFailCheck' in request.form:
                    mergeIfFail = True
                else:
                    mergeIfFail = False

                # A fresh Construct invalidates any prior pre-processing/clustering.
                sKGraph.pre_processed_graph = nx.DiGraph()
                sKGraph.clusters = []
                sKGraph.crisp_clusters = []
                sKGraph.deleted_nodes = []
                sKGraph.deleted_edges = []
                sKGraph.deleted_isolated_nodes = []
                sKGraph.create_SciKGraph(documentsList, documentsNamesList, babelfy_key = babelfy_key, language = language, distance_window=int(distance), mergeIfFail = mergeIfFail)
                if render_flag:
                    plot_network(sKGraph.sciKGraph, layout_name=layout_name)
                else:
                    _write_disabled_networks_js()
                flash("Graph constructed: " + str(len(sKGraph.sciKGraph)) + " concepts, " + str(len(sKGraph.sciKGraph.edges())) + " edges.", "success")
                sorted_concepts = sKGraph.rank(g=sKGraph.sciKGraph, dictionaryCodeMerged=sKGraph.dictionaryCodeMerged)
                return render_template('createSciKGraph.html', key_concepts = sorted_concepts[:200], documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=len(sKGraph.sciKGraph), total_edges=len(sKGraph.sciKGraph.edges()))

            ### -----------------------------------    Open Graph          -----------------------------------------###
            elif 'openSciKGraphInput' in request.files:
                file = request.files['openSciKGraphInput']
                sKGraph.clear_variables()
                sKGraph.open_variables_pickle(file)
                if render_flag:
                    plot_network(sKGraph.sciKGraph, clusters=sKGraph.crisp_clusters, layout_name=layout_name)
                sorted_concepts = sKGraph.rank(g=sKGraph.sciKGraph, dictionaryCodeMerged=sKGraph.dictionaryCodeMerged)
                return render_template('createSciKGraph.html', key_concepts = sorted_concepts[:200], documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=len(sKGraph.sciKGraph), total_edges=len(sKGraph.sciKGraph.edges()), deleted_edges= len(sKGraph.deleted_edges), deleted_concepts= len(sKGraph.deleted_nodes), deleted_isolated_concepts= len(sKGraph.deleted_isolated_nodes))


            ### -----------------------------------    Save Graph          -----------------------------------------###
            elif 'saveGraphButton' in request.form:
                saveFileName = os.path.join(app.root_path, 'saveFiles', 'lastSession.sckg')
                sKGraph.save_variables(saveFileName)
                return send_file(saveFileName, as_attachment=True)


            ### -----------------------------------    Pre-process Graph          -----------------------------------------###
            elif 'verticesThresholdInput' in request.form:
                verticesThresholdList = request.form.getlist("verticesThresholdSelect")
                codesThresholdList = []
                for v in verticesThresholdList:
                    codesThresholdList.append(v[-12:])


                edgesThreshold = request.form.get('edgesThresholdInput')
                sKGraph.pre_process_graph(sKGraph.sciKGraph, int(edgesThreshold), 0, list_nodes = codesThresholdList)
                if render_flag:
                    plot_network(sKGraph.pre_processed_graph, layout_name=layout_name)
                flash("Pre-processing complete: " + str(len(sKGraph.pre_processed_graph)) + " concepts, " + str(len(sKGraph.pre_processed_graph.edges())) + " edges remain.", "success")
                sorted_concepts = sKGraph.rank(g=sKGraph.pre_processed_graph, dictionaryCodeMerged=sKGraph.dictionaryCodeMerged)
                return render_template('createSciKGraph.html', deleted_edges= len(sKGraph.deleted_edges), deleted_concepts= len(sKGraph.deleted_nodes), deleted_isolated_concepts= len(sKGraph.deleted_isolated_nodes), key_concepts = sorted_concepts[:200], documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=len(sKGraph.pre_processed_graph), total_edges=len(sKGraph.pre_processed_graph.edges()))

            ### -----------------------------------    Cluster Graph          -----------------------------------------###
            elif 'clusterGraphButton' in request.form:
                if len(sKGraph.pre_processed_graph) > 2:
                    sKGraph.cluster_graph(sKGraph.pre_processed_graph)
                    cluster_graph = sKGraph.pre_processed_graph
                else:
                    sKGraph.cluster_graph(sKGraph.sciKGraph)
                    cluster_graph = sKGraph.sciKGraph

                if render_flag:
                    plot_network(cluster_graph, clusters=sKGraph.crisp_clusters, layout_name=layout_name)

                flash("Clustering complete: " + str(len(sKGraph.crisp_clusters)) + " clusters.", "success")
                sorted_concepts = sKGraph.rank(g=sKGraph.sciKGraph, dictionaryCodeMerged=sKGraph.dictionaryCodeMerged)

                return render_template('createSciKGraph.html', key_concepts = sorted_concepts[:200], documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=len(sKGraph.sciKGraph), total_edges=len(sKGraph.sciKGraph.edges()), deleted_edges= len(sKGraph.deleted_edges), deleted_concepts= len(sKGraph.deleted_nodes), deleted_isolated_concepts= len(sKGraph.deleted_isolated_nodes))

            # POST with no matching branch — fall through to a safe re-render
            # so we never return None (which would 500 the request).

        sorted_concepts = [] if isinstance(sKGraph.sciKGraph, int) else sKGraph.rank(g=sKGraph.sciKGraph, dictionaryCodeMerged=sKGraph.dictionaryCodeMerged)
        return render_template(
            'createSciKGraph.html',
            key_concepts=sorted_concepts[:200],
            documents=len(sKGraph.graphName),
            language=sKGraph.language or 'EN',
            cooccurrence=(sKGraph.distance_window + 1) if sKGraph.distance_window else 0,
            total_concepts=0 if isinstance(sKGraph.sciKGraph, int) else len(sKGraph.sciKGraph),
            total_edges=0 if isinstance(sKGraph.sciKGraph, int) else len(sKGraph.sciKGraph.edges()),
            deleted_edges=len(sKGraph.deleted_edges),
            deleted_concepts=len(sKGraph.deleted_nodes),
            deleted_isolated_concepts=len(sKGraph.deleted_isolated_nodes),
        )

    @app.route('/analyze', methods=['POST', 'GET'])
    def analyze():
        global maxNodeWeight, minNodeWeight, mediumNodeWeight, minEdgeWeight, maxEdgeWeight
        modularity = '-'
        single_modularity = '-'
        nClusterModularity = 0
        graph_keys = ['-','-','-','-','-']
        graph_centrality = ['-','-','-','-','-']
        cluster_keys = ['-','-','-','-','-']
        cluster_centrality = ['-','-','-','-','-']
        nClusterKeys = 0

        if request.method == 'POST':
            layout_name, render_flag = _read_render_options()

            ### ------------------------------    Update Visualization Setting    ------------------------------###
            if 'updateVisualizationButton' in request.form:
                sKGraph.visualization_enabled = render_flag
                target = _current_target_graph()
                if not render_flag:
                    _write_disabled_networks_js()
                elif target is not None:
                    plot_network(target,
                                 clusters=sKGraph.crisp_clusters or None,
                                 layout_name=layout_name)
                return render_template('analyze.html', nClusters = len(sKGraph.crisp_clusters), singleModularity = single_modularity, nclusterModularity = nClusterModularity, modularit = modularity, gKeys = graph_keys, gCentralities = graph_centrality, nKeys = len(graph_keys), nClustKeys = nClusterKeys, cKeys = cluster_keys, cCentralities = cluster_centrality, nCKeys = len(cluster_keys), documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=0 if isinstance(sKGraph.sciKGraph, int) else len(sKGraph.sciKGraph), total_edges= 0 if isinstance(sKGraph.sciKGraph, int) else len(sKGraph.sciKGraph.edges()), deleted_edges= len(sKGraph.deleted_edges), deleted_concepts= len(sKGraph.deleted_nodes), deleted_isolated_concepts= len(sKGraph.deleted_isolated_nodes))

            #################### REDUCE CLUSTERS ################################
            if 'reduceClustersInput' in request.form:
                reduceClusters = request.form.get('reduceClustersInput')
                sKGraph.clusters  = Analyses.reduceClusters(sKGraph.sciKGraph, sKGraph.clusters, int(reduceClusters))
                sKGraph.crisp_clusters = sKGraph.to_crisp(sKGraph.clusters)
                if render_flag:
                    plot_network(sKGraph.sciKGraph, clusters=sKGraph.crisp_clusters, layout_name=layout_name)
                flash("Cluster reduction complete: " + str(len(sKGraph.crisp_clusters)) + " clusters.", "success")

            ######################## RELATION GRAPH #############################
            elif 'clusterRelationButton' in request.form:
                relation_graph, maxEdgeWeight, minEdgeWeight = Analyses.clusterRelationGraph(sKGraph.sciKGraph, sKGraph.clusters)
                cluster_sizes = [len(c) for c in sKGraph.clusters]
                minNodeWeight = min(cluster_sizes) if cluster_sizes else 0
                maxNodeWeight = max(cluster_sizes) if cluster_sizes else 0
                mediumNodeWeight = int((maxNodeWeight + minNodeWeight) / 2)
                if render_flag:
                    plot_relation_graph(relation_graph,
                                        min_peso=minNodeWeight, max_peso=maxNodeWeight,
                                        medium_peso=mediumNodeWeight,
                                        min_edge=minEdgeWeight, max_edge=maxEdgeWeight,
                                        layout_name=layout_name)

            ########################## MODULARITY ###############################
            elif 'graphModularityButton' in request.form:
                f = Analyses.calc_f(sKGraph.sciKGraph, sKGraph.clusters)
                modularity = 0
                for i in range(len(sKGraph.clusters)):
                    modularity += Analyses.single_cluster_modularityOV(sKGraph.sciKGraph, sKGraph.clusters, f, i)
                modularity = str(round(modularity, 5))

            ############################ SINGLE MODULARITY ######################
            elif 'clusterModularityInput' in request.form:
                nClusterModularity = request.form.get('clusterModularityInput')
                f = Analyses.calc_f(sKGraph.sciKGraph, sKGraph.clusters)
                single_modularity = str(round(Analyses.single_cluster_modularityOV(sKGraph.sciKGraph, sKGraph.clusters, f, int(nClusterModularity)),5))


            ############################# GRAPH KEY-CONCEPTS ####################################
            elif 'graphKeyConceptsButton' in request.form:
                gkeys = sKGraph.key_concepts(g=sKGraph.sciKGraph, dictionaryCodeMerged=sKGraph.dictionaryCodeMerged)
                graph_keys = []
                graph_centrality = []
                for i in gkeys[:30]:
                    graph_keys.append(i[0].replace('+', ' '))
                    graph_centrality.append(round(i[1],5))

            ############################ GRAPH KEYPHRASES ##############################
            elif 'graphKeyphrasesButton' in request.form:
                gkeys = Analyses.extract_keyphrases(copy.deepcopy(sKGraph.sciKGraph), sKGraph.dictionaryCodeMerged)
                graph_keys = []
                graph_centrality = []
                for i in gkeys[:30]:
                    graph_keys.append(i[0].replace('+', ' '))
                    graph_centrality.append(round(i[1],5))

            elif 'clusterKeyConceptsButton' in request.form:
                nClusterKeys = int(request.form.get('clusterKeysInputs'))
                cls_subgraph = sKGraph.sciKGraph.subgraph(sKGraph.clusters[nClusterKeys])

                ckeys = sKGraph.key_concepts(cls_subgraph, dictionaryCodeMerged=sKGraph.dictionaryCodeMerged)
                cluster_keys = []
                cluster_centrality = []
                for i in ckeys[:10]:
                    cluster_keys.append(i[0].replace('+', ' '))
                    cluster_centrality.append(round(i[1],5))


            elif 'clusterKeyphrasesButton' in request.form:
                nClusterKeys = int(request.form.get('clusterKeysInputs'))
                cls_subgraph = sKGraph.sciKGraph.subgraph(sKGraph.clusters[nClusterKeys])

                ckeys = Analyses.extract_keyphrases(cls_subgraph, sKGraph.dictionaryCodeMerged)
                cluster_keys = []
                cluster_centrality = []
                for i in ckeys[:10]:
                    cluster_keys.append(i[0].replace('+', ' '))
                    cluster_centrality.append(round(i[1],5))

            ### -----------------------------------    Open Graph          -----------------------------------------###
            elif 'openSciKGraphInput' in request.files:
                file = request.files['openSciKGraphInput']
                sKGraph.clear_variables()
                sKGraph.open_variables_pickle(file)
                if render_flag:
                    plot_network(sKGraph.sciKGraph, clusters=sKGraph.crisp_clusters, layout_name=layout_name)
                sorted_concepts = sKGraph.rank(g=sKGraph.sciKGraph, dictionaryCodeMerged=sKGraph.dictionaryCodeMerged)
                return render_template('createSciKGraph.html', key_concepts = sorted_concepts[:200], documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=len(sKGraph.sciKGraph), total_edges=len(sKGraph.sciKGraph.edges()), deleted_edges= len(sKGraph.deleted_edges), deleted_concepts= len(sKGraph.deleted_nodes), deleted_isolated_concepts= len(sKGraph.deleted_isolated_nodes))


            ### -----------------------------------    Save Graph          -----------------------------------------###
            elif 'saveGraphButton' in request.form:
                saveFileName = os.path.join(app.root_path, 'saveFiles', 'lastSession.sckg')
                sKGraph.save_variables(saveFileName)
                return send_file(saveFileName, as_attachment=True)



            return render_template('analyze.html', nClusters = len(sKGraph.crisp_clusters), singleModularity = single_modularity, nclusterModularity = nClusterModularity, modularit = modularity, gKeys = graph_keys, gCentralities = graph_centrality, nKeys = len(graph_keys), nClustKeys = nClusterKeys, cKeys = cluster_keys, cCentralities = cluster_centrality, nCKeys = len(cluster_keys), documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=0 if isinstance(sKGraph.sciKGraph, int) else len(sKGraph.sciKGraph), total_edges= 0 if isinstance(sKGraph.sciKGraph, int) else len(sKGraph.sciKGraph.edges()), deleted_edges= len(sKGraph.deleted_edges), deleted_concepts= len(sKGraph.deleted_nodes), deleted_isolated_concepts= len(sKGraph.deleted_isolated_nodes))

        else:
            return render_template('analyze.html', nClusters = len(sKGraph.crisp_clusters), singleModularity = single_modularity, nclusterModularity = nClusterModularity, modularit = modularity, gKeys = graph_keys, gCentralities = graph_centrality, nKeys = len(graph_keys), nClustKeys = nClusterKeys, cKeys = cluster_keys, cCentralities = cluster_centrality, nCKeys = len(cluster_keys), documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=0 if isinstance(sKGraph.sciKGraph, int) else len(sKGraph.sciKGraph), total_edges= 0 if isinstance(sKGraph.sciKGraph, int) else len(sKGraph.sciKGraph.edges()), deleted_edges= len(sKGraph.deleted_edges), deleted_concepts= len(sKGraph.deleted_nodes), deleted_isolated_concepts= len(sKGraph.deleted_isolated_nodes))

    @app.route('/evolution', methods=['POST', 'GET'])
    def evolution():
        global maxNodeWeight, minNodeWeight, mediumNodeWeight
        covers_similarity = '-'
        similar_clusters = [['-','-','-'],['-','-','-'],['-','-','-'],['-','-','-'],['-','-','-']]
        coversLoadedLabel = ""
        min_cluster_threshold = "10"
        similarity_threshold = "0.5"
        overlapping_clusters = [['-','-','-'],['-','-','-'],['-','-','-'],['-','-','-'],['-','-','-']]
        cluster_1 = '0'
        cluster_2 = '0'

        if request.method == 'POST':
            layout_name, render_flag = _read_render_options()

            ### ------------------------------    Update Visualization Setting    ------------------------------###
            if 'updateVisualizationButton' in request.form:
                sKGraph.visualization_enabled = render_flag
                if not render_flag:
                    _write_disabled_networks_js()
                # Evolution has no persistent current graph to re-render when
                # render_flag is True; if the user wants a graph here, they
                # need to (re)submit the overlap action with render enabled.
                return render_template('evolution.html', coversLoaded=coversLoadedLabel, coversSimilarity=covers_similarity, similarClusters=similar_clusters, minClusterThreshold=min_cluster_threshold, similarityThreshold=similarity_threshold, overelappingClusters=overlapping_clusters, cluster1=cluster_1, cluster2=cluster_2)

            if 'loadClusters' in request.form:
                file1 = request.files['graph1Input']
                sKGraph1.clear_variables()
                sKGraph1.open_variables_pickle(file1)
                sKGraph1.name = request.files['graph1Input'].name

                file2 = request.files['graph2Input']
                sKGraph2.clear_variables()
                sKGraph2.open_variables_pickle(file2)
                sKGraph2.name = request.files['graph2Input'].name

                coversLoadedLabel = "Loaded:" + str(sKGraph1.name) + ";" + str(sKGraph2.name)

                return render_template('evolution.html', coversLoaded = coversLoadedLabel, coversSimilarity = covers_similarity, similarClusters = similar_clusters, minClusterThreshold=min_cluster_threshold, similarityThreshold = similarity_threshold, overelappingClusters = overlapping_clusters, cluster1 = cluster_1, cluster2 = cluster_2)


            elif 'coverSimilarityButton' in request.form:
                saveFileName1 = os.path.join(app.root_path, 'saveFiles', 'clusters1.txt')
                sKGraph1.save_clusters_txt(saveFileName1, sKGraph1.clusters)

                saveFileName2 = os.path.join(app.root_path, 'saveFiles', 'clusters2.txt')
                sKGraph2.save_clusters_txt(saveFileName2, sKGraph2.clusters)

                nmiFile = os.path.join(app.root_path, 'static', 'onmi')
                covers_similarity = Analyses.compareFullCovers(saveFileName1, saveFileName2, nmiFile)

                coversLoadedLabel = "Loaded:" + str(sKGraph1.name) + ";" + str(sKGraph2.name)

                return render_template('evolution.html', coversLoaded = coversLoadedLabel, coversSimilarity = covers_similarity, similarClusters = similar_clusters, minClusterThreshold=min_cluster_threshold, similarityThreshold = similarity_threshold, overelappingClusters = overlapping_clusters, cluster1 = cluster_1, cluster2 = cluster_2)

            elif 'clusterSimilarityButton' in request.form:
                min_cluster_threshold = str(request.form.get('minClusterSizeInput'))
                similarity_threshold = str(request.form.get('similarityThresholdInput'))

                nodeCentrality = Analyses.calcNodesCentrality(sKGraph1.sciKGraph,sKGraph2.sciKGraph)
                c1Centralities = Analyses.calcClustersCentralities(sKGraph1.clusters, sKGraph1.sciKGraph, nodeCentrality)
                c2Centralities = Analyses.calcClustersCentralities(sKGraph2.clusters, sKGraph2.sciKGraph, nodeCentrality)
                all_similarities = Analyses.coverSimilarities(sKGraph1.clusters, sKGraph2.clusters, nodeCentrality, c1Centralities, c2Centralities, sizeThreshold=int(min_cluster_threshold))
                similar_clusters = Analyses.compareCovers(all_similarities, float(similarity_threshold))

                return render_template('evolution.html', coversLoaded = coversLoadedLabel, coversSimilarity = covers_similarity, similarClusters = similar_clusters, minClusterThreshold=min_cluster_threshold, similarityThreshold = similarity_threshold, overelappingClusters = overlapping_clusters, cluster1 = cluster_1, cluster2 = cluster_2)

            elif 'clustersOverlappingButton' in request.form:

                #generate list of vertices
                cluster_1 = request.form.get('cluster1OverlapInput')
                cluster_2 = request.form.get('cluster2OverlapInput')

                only1 = []
                only2 = []
                both = []

                for i in sKGraph1.clusters[int(cluster_1)]:
                    if i not in sKGraph2.clusters[int(cluster_2)]:
                        only1.append(i)
                    else:
                        both.append(i)

                for i in sKGraph2.clusters[int(cluster_2)]:
                    if i not in both and i not in sKGraph1.clusters[int(cluster_1)]:
                        only2.append(i)

                o1 = []
                o2 = []
                b = []

                for i in range(max(len(only1),len(only2),len(both))):
                    if len(only1) > i:
                        o1.append(sKGraph1.dictionaryCodeMerged[only1[i]])
                    else:
                        o1.append('-')
                    if len(only2) > i:
                        o2.append(sKGraph2.dictionaryCodeMerged[only2[i]])
                    else:
                        o2.append('-')
                    if len(both) > i:
                        b.append(sKGraph1.dictionaryCodeMerged[both[i]])
                    else:
                        b.append('-')

                overlapping_clusters = []
                overlapping_clusters.append(o1)
                overlapping_clusters.append(o2)
                overlapping_clusters.append(b)

                overlapping_clusters = [[overlapping_clusters[j][i] for j in range(len(overlapping_clusters))] for i in range(len(overlapping_clusters[0]))]


                #generate visualization
                c1 = sKGraph1.clusters[int(cluster_1)]
                c2 = sKGraph2.clusters[int(cluster_2)]

                #comparison of two clusters from different covers
                new_graph = Analyses.evolution(c1, c2, sKGraph1, sKGraph2)

                evo_clusters = [
                    [n for n in new_graph.nodes() if new_graph.nodes()[n].get('clusters') == i]
                    for i in range(1, 4)
                ]
                if render_flag:
                    plot_evolution_graph(new_graph, clusters=evo_clusters, layout_name=layout_name)

                return render_template('evolution.html', coversLoaded = coversLoadedLabel, coversSimilarity = covers_similarity, similarClusters = similar_clusters, minClusterThreshold=min_cluster_threshold, similarityThreshold = similarity_threshold, overelappingClusters = overlapping_clusters, cluster1 = cluster_1, cluster2 = cluster_2)


        else:
            return render_template('evolution.html', coversLoaded = coversLoadedLabel, coversSimilarity = covers_similarity, similarClusters = similar_clusters, minClusterThreshold=min_cluster_threshold, similarityThreshold = similarity_threshold, overelappingClusters = overlapping_clusters, cluster1 = cluster_1, cluster2 = cluster_2)

    @app.route('/')
    def index():
        return redirect(url_for('create'))
        #return create()

    return app

#if __name__ == '__main__':
#    create_app()
