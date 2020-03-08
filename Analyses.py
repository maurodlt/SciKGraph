import networkx as nx
import copy
import nltk
import subprocess

def single_cluster_modularityOV(graph, Clusters, f, nCluster):#, resultPosition):
    E_in = 0
    E_out = 0
    E = 0

    for e in graph.edges():
        E += graph[e[0]][e[1]]['weight']

    for v in Clusters[nCluster]:
        for e in graph[v]:
            for c in Clusters:
                if e in c:
                    if c == Clusters[nCluster]:
                        E_in += 1/f[v] * 1/f[e] * graph[v][e]['weight'] / 2
                    else:
                        E_out += 1/f[v] * 1/f[e] * graph[v][e]['weight']
    #thread_result[resultPosition] = (E_in / E) - ((((2*E_in) + E_out)/(2*E))**2)
    return (E_in / E) - ((((2*E_in) + E_out)/(2*E))**2)


def calc_f(graph, Clusters):
    f = {}
    for i in graph.nodes():
        count = 0
        for c in Clusters:
            if i in c:
                count += 1
        if count < 1:
            count = 1
        f[i] = count
    return f

def merge_Clusters(Clusters, i, j, f):
    for n in Clusters[j]:
        if n not in Clusters[i]:
            Clusters[i].append(n)
        else:
            if f[n] > 1:
                f[n] -= 1

    Clusters.remove(Clusters[j])
    return Clusters, f

###################------------ MERGE SMALL CLUSTERS INTO LARGER ONES -----------------######################3
def reduceClusters(g, Clusters, nFinalClusters):
    f = calc_f(g, Clusters)
    for j in range(len(Clusters)-1, nFinalClusters-1, -1):
        better_i_value = 1000
        better_i = -1
        #print('Merging cluster', j)
        index_max = nFinalClusters
        if j < nFinalClusters:
            index_max = j-1

        for c,i in zip(Clusters[:index_max], range(index_max)):
            mod_i = single_cluster_modularityOV(g, Clusters, f, i)
            mod_j = single_cluster_modularityOV(g, Clusters, f, j)
            mod_iUj = single_cluster_modularityOV(g, *merge_Clusters(copy.deepcopy(Clusters), i, j, copy.deepcopy(f)), i)
            if mod_i + mod_j - mod_iUj  < better_i_value:
                better_i = i
                better_i_value = mod_i + mod_j - mod_iUj
            #print('Analyzing option', i)

        #print(better_i_value)
        merge_Clusters(Clusters, better_i, j, f)
    return Clusters


def clusterRelationGraph(g, Clusters):
    f = calc_f(g, Clusters)
    connections = []

    #init connections
    for c in Clusters:
        connection = []
        for c2 in Clusters:
            connection.append(0)
        connections.append(connection)

    #calc connections
    for e in g.edges():
        for c in range(len(Clusters)):
            if e[0] in Clusters[c]:
                for c2 in range(len(Clusters)):
                    if e[1] in Clusters[c2]:
                        connections[c][c2] += f[e[0]] * f[e[1]] * g[e[0]][e[1]]['weight']

    cluster_relation_graph = nx.Graph()
    id_Cluster = 0
    for n in connections:
        cluster_relation_graph.add_node(id_Cluster, peso=len(Clusters[id_Cluster]))
        id_Cluster += 1

    for c1 in range(len(connections)):
        for c2 in range(len(connections)):
            if cluster_relation_graph.has_edge(c1,c2):
                    cluster_relation_graph[c1][c2]['weight'] += connections[c1][c2]
            else:
                    cluster_relation_graph.add_edge(c1,c2, weight=connections[c1][c2])

    return cluster_relation_graph


################################################################### KEYPHRASE EXTRACTION ########################################################
def nodeRank(g):
    r = nx.degree_centrality(g)
    rank = {}
    for p in r:
        rank[p] = r[str(p)]
    rank = sorted(rank.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    return rank

def takeSecond(elem):
    return elem[1]

def keyPhrasesCompilation(keyWords, g, g2, dictionaryCode,lenght,totalWords):
    keyphrases_dict = {code : value for code, value in keyWords}

    coumpound_keyphrases = []

    #identify compound keyphrases
    for k in keyWords[:lenght]:
        for k2 in keyWords[:lenght]:
            if g2.has_edge(k[0], k2[0]) and g2[k[0]][k2[0]]['weight'] >= int(totalWords / 1000) + 2: #verify occurrences
                if g2.has_edge(k2[0], k[0]) == False or g2[k2[0]][k[0]]['weight'] < g2[k[0]][k2[0]]['weight']:
                    weight = g.out_degree(k[0], weight='weight') + g.in_degree(k2[0], weight='weight') #normalization factor | w(Out(i)) + w(In(j))
                    phrase = [k[0] + ',' + k2[0], g[k[0]][k2[0]]['weight'] / weight] #weight compound keyphrase  |  NIE_{i,j}
                    if phrase not in coumpound_keyphrases:
                        coumpound_keyphrases.append(phrase)

    coumpound_keyphrases = sorted(coumpound_keyphrases, key=lambda kv: (kv[1], kv[0]), reverse=True)
    keyphrases_weight = [t[1] for t in coumpound_keyphrases]
    keyphrases_weight_norm = [float(i)/sum(keyphrases_weight) for i in keyphrases_weight]  #normalize NIE   |   NIE_{i,j} / (sum_all(NIE))
    keyphrases = [t for t in coumpound_keyphrases]

    for kp, n in zip(keyphrases, keyphrases_weight_norm):
        codes = kp[0].split(',')
        #rank keyphrases
        kp[1] = ((keyphrases_dict[codes[0]] + keyphrases_dict[codes[1]])) * n   # CC_{i,j}
        kp[0] = dictionaryCode[codes[0]] + ' ' + dictionaryCode[codes[1]]

    soma = sum([v[1] for v in keyphrases])
    keyphrases = [[k[0], k[1]/soma] for k in keyphrases]   #NCC_{i,j}
    keywords = [[dictionaryCode[k[0]], k[1]] for k in keyWords]
    merged = keyphrases[:6] + keywords #FWC U NCC_{1:6}
    merged.sort(key=takeSecond, reverse=True)
    return merged

def extract_keyphrases(g, dictionaryCode):
    g = nx.Graph(g)
    phrases = []
    words = []

    #First Rank
    keyphrases = nodeRank(g)

    #Exclude words different from nouns, verbs and adjectives
    new_keyphrases = []
    for k in keyphrases:
        words = dictionaryCode[k[0]]
        tokens = nltk.word_tokenize(words)
        notDesiredTags = False

        for w in nltk.pos_tag(tokens):
            if w[1][0] != 'N' and w[1][0] != 'J' and w[1][0] != 'V':
                notDesiredTags = True
        if notDesiredTags:
            bla = [k[0], 0]
            new_keyphrases.append(bla)
        else:
            new_keyphrases.append(k)


    keyphrases = new_keyphrases
    keywords = sorted(keyphrases, key=lambda kv: (kv[1], kv[0]), reverse=True)

    #excludes last 87% keyphrases
    lenght = int(.13*len(keywords))
    summation = sum([v[1] for v in keywords[:lenght]])
    keywords = [[k[0], k[1]/summation] for k in keywords[:lenght]]

    #re-weight mult-term keyphrases
    keywords = [[k[0], (k[1]**(1/(len(dictionaryCode[k[0]].split(' ')))))] for k in keywords[:lenght]]
    keywords = sorted(keywords, key=lambda kv: (kv[1], kv[0]), reverse=True)


    nodesToRemove = []
    for n in g:
        inKeywords = False
        for k in keywords:
            if k[0] == n:
                inKeywords = True
        if inKeywords == False:
            nodesToRemove.append(n)

    for n in nodesToRemove:
        g.remove_node(n)


    totalWords = 0
    for n in g.nodes():
        totalWords += g.nodes()[n]['peso']

    keyphrases = keyPhrasesCompilation(keyphrases,g,g,dictionaryCode,lenght,totalWords)

    return keyphrases






########################### COMPARE COVERS ############################################
def parseAnswer(answer):
    parsedAnswer = []
    for line in answer:
        line = line.split('\t')
        if len(line) >= 2:
            parsedAnswer.append(line)

    for l in parsedAnswer:
        l[0] = l[0].replace(':', '').replace(' ', '')
    return parsedAnswer

def compareFullCovers(cover1, cover2, folderNMI, NMI_type='NMI<Max>'):
    command = folderNMI + ' ' + cover1 + ' ' + cover2
    p = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    answer = p.stdout.decode('ascii').split('\n')
    parsedAnswer = parseAnswer(answer)

    if NMI_type == 'NMI<Max>':
        return parsedAnswer[0][1]
    elif NMI_type == 'lfkNMI':
        return parsedAnswer[1][1]
    elif NMI_type == 'NMI<Sum>':
        return parsedAnswer[2][1]
    else:
        print('Wrong NMI_type!\n')
        return parsedAnswer


def calcDegreeCentrality(g):
    grau = {}
    for v in g:
        grau[v] = len(g[v])
    #sorted_grau = sorted(grau.items(), key=operator.itemgetter(1), reverse=True)
    return grau

def calcNodesCentrality(g1,g2):
    grau = {}
    for v in g1:
        grau[v] = len(g1[v])
    for v2 in g2:
        if v2 in grau:
            grau[v2] = (len(g1[v2]) + len(g2[v2])) / 2
        else:
            grau[v2] = len(g2[v2])
    return grau

def clusterCentrality(cluster, g, nodeCentrality):
    total = 0
    for n in cluster:
        total += nodeCentrality[n]
    return total

def calcClustersCentralities(cover, g, nodeCentrality):
    centralities = {}
    for c,i in zip(cover, range(len(cover))):
        centralities[i] = clusterCentrality(c, g, nodeCentrality)

    return centralities

def comunitySimilarity(c1,c2, n1,n2,nodeCentrality, clustersCentralities1, clustersCentralities2):
    similarity = 0
    for n in c1:
        if n in c2:
            #similarity += 1
            similarity += nodeCentrality[n]

    #return similarity / max(len(c1), len(c2))
    return [similarity / max(clustersCentralities1[n1], clustersCentralities2[n2]), similarity / min(clustersCentralities1[n1], clustersCentralities2[n2])]

def bestComunitySimilarity(comunity, cover1, nodeCentrality, clustersCentralities1, clustersCentralities2):
    higherSimilarity = -1
    nCluster = -1
    for c, i in zip(cover1, range(len(cover1))):
        similarity = comunitySimilarity(c, comunity, nodeCentrality, clustersCentralities1, clustersCentralities2)
        if similarity > higherSimilarity:
            higherSimilarity = similarity
            nCluster = i

    return higherSimilarity, nCluster

def coverSimilarities(cover1, cover2, nodeCentrality, clustersCentralities1, clustersCentralities2, sizeThreshold=10):
    all_similarities = []

    for c1, n1 in zip(cover1, range(len(cover1))):
        if len(c1) >= sizeThreshold:
            local_similarities = []
            for c2, n2 in zip(cover2, range(len(cover2))):
                if len(c2) >= sizeThreshold:
                    local_similarities.append(comunitySimilarity(c1,c2,n1,n2, nodeCentrality, clustersCentralities1, clustersCentralities2))
                else:
                    local_similarities.append([0,0])
            all_similarities.append(local_similarities)
        else:
            local_similarities = []
            for c2 in cover2:
                local_similarities.append([0,0])
            all_similarities.append(local_similarities)

    return all_similarities

def compareCovers(all_similarities, threshold):

    similar_clusters = []
    for c1 in range(len(all_similarities)):
        for c2 in range(len(all_similarities[c1])):
            if all_similarities[c1][c2][0] >= threshold:
                #if [c2,c1,all_similarities[c1][c2]] not in similar_clusters:
                similar_clusters.append([c1,c2,all_similarities[c1][c2][0]])

    return similar_clusters




############################## EVOLUTION ################################################

def evolution(c1, c2, sKGraph1, sKGraph2):
    new_graph = nx.Graph()
    for n in c1:
        if n in c2:
            new_graph.add_node(n, peso=sKGraph1.sciKGraph.nodes()[n]['peso']+sKGraph2.sciKGraph.nodes()[n]['peso'], clusters=3, dicionario=sKGraph1.dictionaryCodeMerged[n])
        else:
            new_graph.add_node(n, peso=sKGraph1.sciKGraph.nodes()[n]['peso'], clusters=1, dicionario=sKGraph1.dictionaryCodeMerged[n])
    for n in c2:
        if n not in c1:
            new_graph.add_node(n, peso=sKGraph2.sciKGraph.nodes()[n]['peso'], clusters=2, dicionario=sKGraph2.dictionaryCodeMerged[n])

    for e in sKGraph1.sciKGraph.edges():
        if new_graph.has_node(e[0]) and new_graph.has_node(e[1]):
            if e in sKGraph2.sciKGraph.edges():
                new_graph.add_edge(e[0], e[1], weight= sKGraph1.sciKGraph[e[0]][e[1]]['weight'] + sKGraph2.sciKGraph[e[0]][e[1]]['weight'])
            else:
                new_graph.add_edge(e[0], e[1], weight= sKGraph1.sciKGraph[e[0]][e[1]]['weight'])

    for e in sKGraph2.sciKGraph.edges():
        if new_graph.has_node(e[0]) and new_graph.has_node(e[1]):
            if e not in sKGraph1.sciKGraph.edges():
                new_graph.add_edge(e[0], e[1], weight= sKGraph2.sciKGraph[e[0]][e[1]]['weight'])

    return new_graph
