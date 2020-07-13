import string
import networkx as nx
import re
from nltk import word_tokenize, pos_tag
from pybabelfy.babelfy import *
from nltk.stem import PorterStemmer
from math import log
import pickle
import glob
import os
import nltk
import operator
import sys
import matplotlib.pyplot as plt
#from wordcloud import WordCloud
#from matplotlib_venn import venn3
import copy

class OClustR():

    def __init__(self):#, BabelfyKey, inputFile, outputDirectory = './', distance_window = 2, language = 'EN', graphType = 'direct'):
        #init variables
        self.Clusters = []
        self.g = nx.Graph()
        self.crisp_clusters = []



    def to_undirected(self, graph):
        #create graph
        g = nx.Graph()
        #copy nodes
        for n in graph.nodes():
            g.add_node(n, peso=graph.nodes()[n]['peso'], dicionario=graph.nodes()[n]['dicionario'])
        #copy edges (to_undirected)
        for e in graph.edges():
            if g.has_edge(e[0], e[1]):
                g[e[0]][e[1]]['weight'] += graph[e[0]][e[1]]['weight']
            else:
                g.add_edge(e[0], e[1], weight=graph[e[0]][e[1]]['weight'])

        return g

    def apply_edges_threshold(self, g, edges_threshold, list_edges = []):
        if list_edges != []:
            g.remove_edges_from(list_edges)
        else:
            edgesToRemove = []
            for e in g.edges():
                if g[e[0]][e[1]]['weight'] <= edges_threshold:
                    edgesToRemove.append(e)
            for e in edgesToRemove:
                g.remove_edge(e[0], e[1])
        return g, edgesToRemove

    def apply_nodes_thresold(self, g, nodesThreshold, list_nodes=[]):
        if list_nodes != []:
            g.remove_nodes_from(list_nodes)
            deleted = list_nodes
        else:
            deleted = []
            grau = nx.degree_centrality(g)
            sorted_grau = sorted(grau.items(), key=operator.itemgetter(1), reverse=True)

            for v in sorted_grau[:nodesThreshold]:
                deleted.append(v[0])
                g.remove_node(v[0])
        return g, deleted

    def remove_isolated_nodes(self, g):
        #remove isoleted nodes
        l = []
        for n in g.nodes():
            if g.degree[n] == 0:
                l.append(n)
        for i in l:
            g.remove_node(i)
        return g, l

    def pre_process(self, g, edges_threshold, nodes_threshold, list_edges = [], list_nodes = []):
        g = self.to_undirected(g)
        g, rem_e = self.apply_edges_threshold(g, edges_threshold, list_edges)
        g, rem_n = self.apply_nodes_thresold(g, nodes_threshold, list_nodes)
        g, rem_iso_n = self.remove_isolated_nodes(g)
        return g, rem_e, rem_n, rem_iso_n

    #def take_second(self, elem):
    #    return elem[1]

    def phase_1(self, g):
        #densityR
        densityR = {}
        for v in g.nodes():
            count = 0
            for a in g[v]:
                if g.degree[a] <= g.degree[v]:
                    count += 1
            densityR[v] = count / len(g[v])

        #aprox_intra_sim
        aprox_intra_sim = {}
        for v in g.nodes():
            sim = 0
            for a in g[v]:
                sim += g[v][a]['weight']
            aprox_intra_sim[v] = sim / len(g[v])

        #compactnessR
        compactnessR = {}
        for v in g.nodes():
            count = 0
            for u in g[v]:
                if aprox_intra_sim[v] >= aprox_intra_sim[u]:
                    count += 1
            compactnessR[v] = count / len(g[v])

        #relevance
        relevance = {}
        for v in g.nodes():
            relevance[v] = (compactnessR[v] + (densityR[v])) / 2

        L = []
        C = []
        covered = {}

        for v in g.nodes():
            covered[v] = False
            if relevance[v] > 0:
                L.append([v, relevance[v]])

        #L.sort(key=self.take_second,reverse=True)
        L.sort(key = lambda x: x[1],reverse=True)

        for v in L:
            if covered[v[0]] == False:
                C.append([v[0], g.degree[v[0]]])
                covered[v[0]] = True
                for u in g[v[0]]:
                    covered[u] = True
            else:
                append = False
                for u in g[v[0]]:
                    if covered[u] == False:
                        covered[u] = True
                        append = True
                if append == True:
                    C.append([v[0], g.degree[v[0]]])
        return C, covered

    def phase_2(self, g, C, covered):
        #sort C by degree
        C.sort(key= lambda x: x[1],reverse=True)
        c = []
        for v in C:
            c.append(v[0])
        C = c
        c = []

        #mark each vertex in C as not-analyzed
        for cov in covered:
            covered[cov] = False

        #Calc shared vertices per cluster
        Shared = {}
        for v in C:
            # check if central node is shared
            if v in Shared:
                Shared[v] += 1
            else:
                Shared[v] = 0

            #check if satellites are shared
            for u in g[v]:
                if u in Shared:
                    Shared[u] += 1
                else:
                    Shared[u] = 0

        removedFromC = {}
        for v in g.nodes():
            removedFromC[v] = False

        SC = []
        linked = {}
        for v in C:
            linked[v] = []
            if removedFromC[v] == False:
                for u in g[v]:

                    if covered[u] == False and removedFromC[u] == False and u in C:
                        nShared = 0
                        nNonShared = 0
                        nonShared = []

                        for i in g[u]:
                            if Shared[i] >= 1:
                                nShared += 1
                            else:
                                nonShared.append(i)
                                nNonShared += 1
                        if  nShared * 1 > nNonShared:
                            linked[v].append(nonShared)
                            for i in nonShared:
                                removedFromC[i] = True

                            for i in g[u]:
                                if Shared[i] >= 1:
                                    Shared[i] -= 1
                            #C.remove(u)
                            removedFromC[u] = True
                        else:
                            covered[u] = True

            if removedFromC[v] == False:
                cluster = []
                cluster.append(v)
                for u in g[v]:
                    cluster.append(u)
                for l in linked[v]:
                    for i in l:
                        #if i not in cluster:
                        cluster.append(i)

                SC.append([cluster, len(cluster)])
                SC.sort(key = lambda x: x[1], reverse=True)

        Clusters = []
        for c in SC:
            clus = []
            for v in c[0]:
                clus.append(v)
            Clusters.append(clus)

        return Clusters

    def to_crisp(self, Clusters):
        ##Crisp Cluster
        crisp = []
        elem = []
        for c in Clusters:
            cl = []
            for v in c:
                if v not in elem:
                    cl.append(v)
                    elem.append(v)
            if len(cl) >= 1:
                crisp.append(cl)
        return crisp

    def save_clusters(self, saveFile, Clusters, crisp = -1):
        #save clusters
        with open(saveFile + "clustersOClustR.pickle", "wb") as fp:
            pickle.dump(Clusters, fp, protocol=2)

        if crisp != -1:
            with open(saveFile + "crisp.pickle", "wb") as fp:
                pickle.dump(crisp, fp, protocol=2)

        return

    def cluster_graph(self, g):
        self.g = self.to_undirected(g)
        C, covered = self.phase_1(self.g)
        self.Clusters = self.phase_2(self.g, C, covered)
        self.crisp_clusters = self.to_crisp(self.Clusters)

        return self.Clusters, self.crisp_clusters, self.g

	# Graph vertice weight 'peso'
	# Graph edge weight 'weight'
	#list_node and list_edge override edges_threshold and nodes_threshold
    def identify_clusters(self, g, edges_threshold, nodes_threshold, list_nodes = [], list_edges = []):
        g = self.to_undirected(g)
        self.g = self.pre_process(g, edges_threshold, nodes_threshold, list_nodes = [], list_edges = [])[0]
        C, covered = self.phase_1(self.g)
        self.Clusters = self.phase_2(self.g, C, covered)
        self.crisp_clusters = self.to_crisp(self.Clusters)

        return self.Clusters, self.crisp_clusters, self.g
