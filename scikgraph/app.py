from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
import SciKGraph as skg
import pickle
import OClustR as OCR
import json
import Analyses
import copy
import subprocess


from py2cytoscape import cyrest
from py2cytoscape import util as cy
from py2cytoscape.data.cyrest_client import CyRestClient
from IPython.display import Image

cytoscape=cyrest.cyclient()
cyjs = CyRestClient()

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
UPLOAD_FOLDER = '/home/mauro/Documents/flask_app/static/temp/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Bootstrap(app)
sKGraph = skg.SciKGraph()
sKGraph1 = skg.SciKGraph()
sKGraph2 = skg.SciKGraph()

@app.route('/create', methods=['POST', 'GET'])
def create():

    ### -----------------------------------    Construct Graph          -----------------------------------------###
    if request.method == 'POST':

        if 'languageSelect' in request.form:
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

            sKGraph.create_SciKGraph(documentsList, documentsNamesList, babelfy_key = babelfy_key, language = language, distance_window=int(distance), mergeIfFail = mergeIfFail)
            plot = cyjs.network.create_from_networkx(sKGraph.sciKGraph)
            plot_network()
            sorted_concepts = sKGraph.rank(g=sKGraph.sciKGraph, dictionaryCodeMerged=sKGraph.dictionaryCodeMerged)
            return render_template('createSciKGraph.html', key_concepts = sorted_concepts[:200], documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=len(sKGraph.sciKGraph), total_edges=len(sKGraph.sciKGraph.edges()))

        ### -----------------------------------    Open Graph          -----------------------------------------###
        elif 'openSciKGraphInput' in request.files:
            file = request.files['openSciKGraphInput']
            sKGraph.clear_variables()
            sKGraph.open_variables_pickle(file)
            plot = cyjs.network.create_from_networkx(sKGraph.sciKGraph)

            #plot_network()

            #create groups
            for c, count in zip(sKGraph.crisp_clusters, range(len(sKGraph.crisp_clusters))):
                group = ''
                for n in c:
                    group += 'name:' + str(n) + ','
                group = group[:-1]
                cytoscape.group.create(nodeList=group, groupName='group'+str(count))

            plot_network()
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
            plot = cyjs.network.create_from_networkx(sKGraph.pre_processed_graph)
            plot_network()
            sorted_concepts = sKGraph.rank(g=sKGraph.pre_processed_graph, dictionaryCodeMerged=sKGraph.dictionaryCodeMerged)
            return render_template('createSciKGraph.html', deleted_edges= len(sKGraph.deleted_edges), deleted_concepts= len(sKGraph.deleted_nodes), deleted_isolated_concepts= len(sKGraph.deleted_isolated_nodes), key_concepts = sorted_concepts[:200], documents=len(sKGraph.graphName), language=sKGraph.language, cooccurrence=sKGraph.distance_window + 1, total_concepts=len(sKGraph.pre_processed_graph), total_edges=len(sKGraph.pre_processed_graph.edges()))

        ### -----------------------------------    Cluster Graph          -----------------------------------------###
        elif 'clusterGraphButton' in request.form:
            if len(sKGraph.pre_processed_graph) > 2:
                sKGraph.cluster_graph(sKGraph.pre_processed_graph)

            else:
                sKGraph.cluster_graph(sKGraph.sciKGraph)


            #create groups
            for c, count in zip(sKGraph.crisp_clusters, range(len(sKGraph.crisp_clusters))):
                group = ''
                for n in c:
                    group += 'name:' + str(n) + ','
                group = group[:-1]
                print('group'+str(count), group)
                cytoscape.group.create(nodeList=group, groupName='group'+str(count))

            plot_network()
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

        #################### REDUCE CLUSTERS ################################
        if 'reduceClustersInput' in request.form:
            reduceClusters = request.form.get('reduceClustersInput')
            sKGraph.clusters  = Analyses.reduceClusters(sKGraph.sciKGraph, sKGraph.clusters, int(reduceClusters))
            sKGraph.crisp_clusters = sKGraph.to_crisp(sKGraph.clusters)

            plot = cyjs.network.create_from_networkx(sKGraph.sciKGraph)
            #create groups
            for c, count in zip(sKGraph.crisp_clusters, range(len(sKGraph.crisp_clusters))):
                group = ''
                for n in c:
                    group += 'name:' + str(n) + ','
                group = group[:-1]
                cytoscape.group.create(nodeList=group, groupName='group'+str(count))
            plot_network()

        ######################## RELATION GRAPH #############################
        elif 'clusterRelationButton' in request.form:
            plot = cyjs.network.create_from_networkx(Analyses.clusterRelationGraph(sKGraph.sciKGraph, sKGraph.clusters))
            plot_network()

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

            plot = cyjs.network.create_from_networkx(new_graph)
            #create groups
            for i in range(1,4):
                group = ''
                for n in new_graph.nodes():
                    if new_graph.nodes()[n]['clusters'] == i:
                        group += 'name:' + str(n) + ','
                group = group[:-1]
                cytoscape.group.create(nodeList=group, groupName='group'+str(i))
            plot_network()

            return render_template('evolution.html', coversLoaded = coversLoadedLabel, coversSimilarity = covers_similarity, similarClusters = similar_clusters, minClusterThreshold=min_cluster_threshold, similarityThreshold = similarity_threshold, overelappingClusters = overlapping_clusters, cluster1 = cluster_1, cluster2 = cluster_2)


    else:
        return render_template('evolution.html', coversLoaded = coversLoadedLabel, coversSimilarity = covers_similarity, similarClusters = similar_clusters, minClusterThreshold=min_cluster_threshold, similarityThreshold = similarity_threshold, overelappingClusters = overlapping_clusters, cluster1 = cluster_1, cluster2 = cluster_2)

@app.route('/')
def index():
    return create()

def plot_network():
    saveFileName = os.path.join(app.root_path, 'static', 'sciKGraph.cx')
    cytoscape.layout.cose()

    #delete old network
    for i in cyjs.network.get_all():
        if i != cytoscape.network.get()['SUID']:
            cytoscape.network.destroy(network='SUID:'+str(i))

    subprocess.run(["rm", saveFileName])
    cytoscape.network.export(OutputFile=saveFileName, options='cx')




    with open(saveFileName) as json_file:
        cx = json.load(json_file)

    content = parse_cx_to_js(cx)

    saveFileName = os.path.join(app.root_path, 'static', 'networks.js')
    f = open(saveFileName,'w')
    f.write('var networks = {"From cyREST": ')
    f.write(content)
    f.write('}')
    f.close()

    return


def parse_cx_to_js(cx):
    #create nodes
    nodes = {}
    for n in cx[2]['nodes']:
        data = {}
        position = {}
        node = {}
        data['id'] = str(n['@id'])
        data['shared_name'] = n['n']
        data['SUID'] = n['@id']
        node['data'] = data
        node['position'] = position
        nodes[n['@id']] = node


    #set nodes attributes
    for l in cx[7]['nodeAttributes']:
        atributos = [v for k, v in l.items() ]

        if atributos[2] == 'NumChildren' or atributos[2] == 'NumDescendents':
            atributos[3] = int(float(atributos[3]))
        elif atributos[2] == 'selected':
            atributos[3] = False
        elif atributos[2] == 'peso':
            atributos[3] = float(atributos[3])
        elif atributos[2] == 'id':
                atributos[2] = 'id_original'
        nodes[atributos[1]]['data'][atributos[2]] = atributos[3]

    #set nodes position
    for l in cx[9]['cartesianLayout']:
        position = [v for k, v in l.items() ]
        nodes[position[0]]['position']['x'] = position[2]
        nodes[position[0]]['position']['y'] = position[3]

    #set edges
    edges = {}
    for l in cx[8]['edgeAttributes']:
        atributos = [v for k, v in l.items() ]
        if atributos[2] == 'source':
            atributos[2] = 'source_original'
        elif atributos[2] == 'target':
            atributos[2] = 'target_original'
        elif atributos[2] == 'selected':
            atributos[3] = False
        elif atributos[2] == 'weight':
            atributos[3] = float(atributos[3])

        if atributos[1] in edges:
            edges[atributos[1]]['data'][atributos[2]] = atributos[3]
        else:
            data = {}
            edge = {'data': data}
            data[atributos[2]] = atributos[3]
            edge['data'] = data
            edges[atributos[1]] = edge


    #set edges attributes
    for l in cx[3]['edges']:
        if l['@id'] in edges:
            edges[l['@id']]['data']['id'] = str(l['@id'])
            edges[l['@id']]['data']['source'] = str(l['s'])
            edges[l['@id']]['data']['target'] = str(l['t'])
            edges[l['@id']]['data']['SUID'] = l['@id']


    ########organize json
    elements = {}
    #put nodes in a list
    list_nodes = []
    for n in nodes:
        list_nodes.append(nodes[n])
    elements['nodes'] = list_nodes
    #put edgfes in a list
    list_edges = []
    for e in edges:
        list_edges.append(edges[e])
    elements['edges'] = list_edges

    #create final json
    network_id = cx[6]['cyHiddenAttributes'][-1]['s']
    data = {'shared_name': 'From cyREST', 'name': 'From cyREST', 'SUID': network_id, '__Annotations': [], 'selected': False}
    final = {'format_version': '1,0', 'generated_by': 'cytoscape', 'target_cytoscapejs_version': '~2.1', 'data': data, 'elements': elements}
    #final = {'From cyREST': final}

    return json.dumps(final)

if __name__ == '__main__':
    app.run(debug=True)
