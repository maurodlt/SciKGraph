from flask import Flask, render_template, request, send_file, flash
from flask_bootstrap import Bootstrap
import os
import json
import copy
import networkx as nx
from scikgraph import SciKGraph as skg
from scikgraph import Analyses


def _server_layout_spring(g):
    pos = nx.spring_layout(g, iterations=50, seed=42)
    return {str(n): {"x": float(p[0]) * 1000.0, "y": float(p[1]) * 1000.0}
            for n, p in pos.items()}


LAYOUTS = {
    "spring":     {"side": "server", "fn": _server_layout_spring},
    "cose":       {"side": "browser"},
    "concentric": {"side": "browser"},
    "circle":     {"side": "browser"},
    "grid":       {"side": "browser"},
}
DEFAULT_LAYOUT = "spring"

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = os.urandom(24)
UPLOAD_FOLDER = '/home/mauro/Documents/flask_app/static/temp/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Bootstrap(app)
sKGraph = skg.SciKGraph()
sKGraph1 = skg.SciKGraph()
sKGraph2 = skg.SciKGraph()


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


def plot_network(g, clusters=None, layout_name=None):
    name = layout_name or DEFAULT_LAYOUT
    spec = LAYOUTS.get(name, LAYOUTS[DEFAULT_LAYOUT])
    if spec["side"] == "server":
        positions = spec["fn"](g)
        browser_layout = "preset"
    else:
        positions = None
        browser_layout = name
    elements = _nx_to_cyjs_elements(g, clusters, positions=positions)
    payload = {"SciKGraph": {"elements": elements, "layout": browser_layout}}
    path = os.path.join(app.root_path, 'static', 'networks.js')
    with open(path, 'w') as f:
        f.write('var networks = ' + json.dumps(payload) + ';')
    sKGraph.visualization_enabled = True


def _write_disabled_networks_js():
    payload = {"SciKGraph": {"disabled": True}}
    path = os.path.join(app.root_path, 'static', 'networks.js')
    with open(path, 'w') as f:
        f.write('var networks = ' + json.dumps(payload) + ';')
    sKGraph.visualization_enabled = False


def _read_render_options(target_skg):
    layout = request.form.get('layoutSelect') or getattr(target_skg, 'last_layout', None) or DEFAULT_LAYOUT
    if layout not in LAYOUTS:
        layout = DEFAULT_LAYOUT
    target_skg.last_layout = layout
    if 'renderVisualizationFormMarker' in request.form:
        render = 'renderVisualizationCheck' in request.form
    else:
        render = True
    return layout, render

@app.route('/create', methods=['POST', 'GET'])
def create():

    ### -----------------------------------    Construct Graph          -----------------------------------------###
    if request.method == 'POST':
        layout_name, render_flag = _read_render_options(sKGraph)

        if 'updateVisualizationButton' in request.form:
            if len(sKGraph.pre_processed_graph) > 0:
                target = sKGraph.pre_processed_graph
            elif not isinstance(sKGraph.sciKGraph, int):
                target = sKGraph.sciKGraph
            else:
                target = None
            if not render_flag:
                _write_disabled_networks_js()
            elif target is not None:
                plot_network(target,
                             clusters=sKGraph.crisp_clusters or None,
                             layout_name=layout_name)
            return render_template('createSciKGraph.html')

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
            import networkx as _nx
            sKGraph.pre_processed_graph = _nx.DiGraph()
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
            return render_template('createSciKGraph.html', key_concepts = sorted_concepts[:200], documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=len(sKGraph.sciKGraph), total_edges=len(sKGraph.sciKGraph.edges()))


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
            return render_template('createSciKGraph.html', key_concepts = sorted_concepts[:200], documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=len(sKGraph.sciKGraph), total_edges=len(sKGraph.sciKGraph.edges()))

    else:
        return render_template('createSciKGraph.html')

@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    modularity = '-'
    single_modularity = '-'
    nClusterModularity = 0
    graph_keys = ['-','-','-','-','-']
    graph_centrality = ['-','-','-','-','-']
    cluster_keys = ['-','-','-','-','-']
    cluster_centrality = ['-','-','-','-','-']
    nClusterKeys = 0

    if request.method == 'POST':
        layout_name, render_flag = _read_render_options(sKGraph)

        if 'updateVisualizationButton' in request.form:
            target = sKGraph.sciKGraph if not isinstance(sKGraph.sciKGraph, int) else None
            if not render_flag:
                _write_disabled_networks_js()
            elif target is not None:
                plot_network(target,
                             clusters=sKGraph.crisp_clusters or None,
                             layout_name=layout_name)
            return render_template('analyze.html', nClusters = len(sKGraph.crisp_clusters), singleModularity = single_modularity, nclusterModularity = nClusterModularity, modularit = modularity, gKeys = graph_keys, gCentralities = graph_centrality, nKeys = len(graph_keys), nClustKeys = nClusterKeys, cKeys = cluster_keys, cCentralities = cluster_centrality, nCKeys = len(cluster_keys))

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
            relation_graph = Analyses.clusterRelationGraph(sKGraph.sciKGraph, sKGraph.clusters)
            # clusterRelationGraph in __init__.py returns (graph, max_edge, min_edge); accept either form
            if isinstance(relation_graph, tuple):
                relation_graph = relation_graph[0]
            if render_flag:
                plot_network(relation_graph, layout_name='circle')

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

        return render_template('analyze.html', nClusters = len(sKGraph.crisp_clusters), singleModularity = single_modularity, nclusterModularity = nClusterModularity, modularit = modularity, gKeys = graph_keys, gCentralities = graph_centrality, nKeys = len(graph_keys), nClustKeys = nClusterKeys, cKeys = cluster_keys, cCentralities = cluster_centrality, nCKeys = len(cluster_keys))

    else:
        return render_template('analyze.html', nClusters = len(sKGraph.crisp_clusters), singleModularity = single_modularity, nclusterModularity = nClusterModularity, modularit = modularity, gKeys = graph_keys, gCentralities = graph_centrality, nKeys = len(graph_keys), nClustKeys = nClusterKeys, cKeys = cluster_keys, cCentralities = cluster_centrality, nCKeys = len(cluster_keys))

@app.route('/evolution', methods=['POST', 'GET'])
def evolution():
    covers_similarity = '-'
    similar_clusters = [['-','-','-'],['-','-','-'],['-','-','-'],['-','-','-'],['-','-','-']]
    coversLoadedLabel = ""
    min_cluster_threshold = "10"
    similarity_threshold = "0.5"
    overlapping_clusters = [['-','-','-'],['-','-','-'],['-','-','-'],['-','-','-'],['-','-','-']]
    cluster_1 = '0'
    cluster_2 = '0'

    if request.method == 'POST':
        layout_name, render_flag = _read_render_options(sKGraph1)

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
                plot_network(new_graph, clusters=evo_clusters, layout_name=layout_name)

            return render_template('evolution.html', coversLoaded = coversLoadedLabel, coversSimilarity = covers_similarity, similarClusters = similar_clusters, minClusterThreshold=min_cluster_threshold, similarityThreshold = similarity_threshold, overelappingClusters = overlapping_clusters, cluster1 = cluster_1, cluster2 = cluster_2)


    else:
        return render_template('evolution.html', coversLoaded = coversLoadedLabel, coversSimilarity = covers_similarity, similarClusters = similar_clusters, minClusterThreshold=min_cluster_threshold, similarityThreshold = similarity_threshold, overelappingClusters = overlapping_clusters, cluster1 = cluster_1, cluster2 = cluster_2)

@app.route('/')
def index():
    return create()

if __name__ == '__main__':
    app.run(debug=True)
