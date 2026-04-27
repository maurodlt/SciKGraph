import networkx as nx
import copy

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


#################------------ MERGE SMALL CLUSTERS IN LARGER ONES FULL COMPARISON-----------------#####################
def reduceClusters_fullComparison(g, Clusters, nFinalClusters):
	f = calc_f(g, Clusters)
	for j in range(len(Clusters)-1, nFinalClusters-1, -1):
	    better_i_value = 1000
	    better_i = -1
	    index_max = 0
	    if j < nFinalClusters:
            index_max = j-1
	    for c,i in zip(Clusters, range(len(Clusters)-1)):

		mod_i = single_cluster_modularityOV(g, Clusters, f, i)
		mod_j = single_cluster_modularityOV(g, Clusters, f, j)
		mod_iUj = single_cluster_modularityOV(g, *merge_Clusters(copy.deepcopy(Clusters), i, j, copy.deepcopy(f)), i)


		if mod_i + mod_j - mod_iUj  < better_i_value:
		    better_i = i
		    better_i_value = mod_i + mod_j - mod_iUj

	    merge_Clusters(Clusters, better_i, j, f)

    return Clusters


def reduceCLusters_simple(Clusters, nFinalClusters):
    return Clusters[:nFinalClusters]
