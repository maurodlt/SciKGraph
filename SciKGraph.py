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
import OClustR as OCR
import operator
#import nltk

class SciKGraph():

    def __init__(self):#, BabelfyKey, inputFile, outputDirectory = './', distance_window = 2, language = 'EN', graphType = 'direct'):
        #init variables
        self.key = ''
        self.inputFile = ''
        self.outputDirectory = ''
        self.distance_window = 0
        self.graphName = []
        self.dictionaries = []
        self.dictionariesCode = []
        self.graphsI = []
        self.graphsD = []
        self.sciKGraph = 0
        self.pre_processed_graph = 0
        self.dictionaryCodeMerged = {}
        self.language = ''
        self.deleted_nodes = 0
        self.deleted_edges = 0
        self.deleted_isolated_nodes = 0
        self.name=""

        self.clusters = []
        self.crisp_clusters = []
        self.pre_processed_graph = nx.DiGraph()



        #if self.outputDirectory[-1] != '/':
        #    self.outputDirectory = self.outputDirectory + '/'

    #rank Concepts
    def rank(self, g, dictionaryCodeMerged):
        grau = nx.degree_centrality(g)
        sorted_grau = sorted(grau.items(), key=operator.itemgetter(1), reverse=True)
        sorted_concepts = []
        for i in sorted_grau:
            #sorted_concepts.append([dictionaryCodeMerged[i[0]], i[0]])
            sorted_concepts.append(dictionaryCodeMerged[i[0]].lower().replace('+', ' ') + '  :  ' + i[0])

        return sorted_concepts


    #key Concepts
    def key_concepts(self, g, dictionaryCodeMerged):
        grau = nx.degree_centrality(g)
        sorted_grau = sorted(grau.items(), key=operator.itemgetter(1), reverse=True)
        sorted_concepts = []
        for i in sorted_grau:
            sorted_concepts.append([dictionaryCodeMerged[i[0]], i[1]])

        return sorted_concepts

    # open and close file
    def open_file(self,fileName):
        file = open(fileName,"r")
        text = file.read()
        file.close()
        return text

    #parse and split text in chuncks of at most 3000 characters
    def parse_text(self,text):
        #remove special characters
        punctuationToRemove = string.punctuation.replace('!','').replace('.','').replace('?','').replace('-','').replace(',','')
        translator = str.maketrans('', '', punctuationToRemove)
        parsedText = text.translate(translator)
        #remove numbers
        parsedText = re.sub(r'[0-9]+', '', parsedText)
        #remove double spaces
        parsedText = re.sub(r'  ', ' ', parsedText)
        #remove non-printable characters
        parsedText = "".join(filter(lambda x: x in string.printable, parsedText))
        #remove spaces
        parsedText = re.sub(r' ', '+', parsedText)
        #split text in chuncks of at most 5000 characters
        punctuation = ['.','?','!']
        splitted_text = []
        splitted_text.append("")
        n_lines = len(parsedText.splitlines())
        for line in parsedText.splitlines():
            if n_lines == 1:
                splitted_text[-1] = line
            else:
                if len(splitted_text[-1] + line) < 4500 and splitted_text[-1][-1:] not in punctuation or len(splitted_text[-1] + line) <= 3000:
                    splitted_text[-1] = splitted_text[-1] + '+' + line
                else:
                    splitted_text.append(line)
        translator = str.maketrans('', '', "?!.")
        for l in splitted_text:
            l = l.translate(translator)
        return splitted_text

    def frag(self,semantic_annotation, input_text):
        start = semantic_annotation.char_fragment_start()
        end = semantic_annotation.char_fragment_end()
        return input_text[start:end+1]

    def babelfy(self,lang, key, splitted_text):
        babelapi = Babelfy()
        #bn = BabelNet(key)
        paragraphs_annotations = []
        paragraphs_text = []
        paragraphs_code = []

        count = 0
        for paragraph in splitted_text: #annotate each paragraph
            words_annotations = []
            words_text = []
            words_code = []
            semantic_annotations = babelapi.disambiguate(paragraph,lang,key,match="EXACT_MATCHING",cands="TOP",mcs="ON",anntype="ALL")

            #exclude unused annotations (single words of multiword expressions)
            for semantic_annotation in semantic_annotations:
                if len(words_annotations) == 0 or words_annotations[-1].char_fragment_end() < semantic_annotation.char_fragment_start():
                    words_annotations.append(semantic_annotation)
                    words_text.append(self.frag(semantic_annotation,paragraph))
                    words_code.append(semantic_annotation.babel_synset_id())

                elif words_annotations[-1].char_fragment_start() == semantic_annotation.char_fragment_start():
                    del words_annotations[-1]
                    words_annotations.append(semantic_annotation)
                    del words_text[-1]
                    words_text.append(self.frag(semantic_annotation,paragraph))
                    del words_code[-1]
                    words_code.append(semantic_annotation.babel_synset_id())


            paragraphs_annotations.append(words_annotations)
            paragraphs_text.append(words_text)
            paragraphs_code.append(words_code)
            count = count + 1
            print(str(count) + '/' + str(len(splitted_text)))
        return paragraphs_annotations, paragraphs_text, paragraphs_code

    #Create the following Dicts
    def create_dicts(self,paragraphs_text, paragraphs_code):
        ###        dictionary[word] = code             ###
        ###        dictionaryCode[code] = word        ###
        ###        weight[code] = weight            ###
        dictionary={}
        weight={}
        dictionaryCode={}
        for paragraph, codes in zip(paragraphs_text, paragraphs_code):
            for word, code in zip(paragraph, codes):
                if code not in weight:
                    weight[code] = 1
                else:
                    weight[code] = weight[code] + 1

                if word not in dictionary:
                    dictionary[word] = code
                if code not in dictionaryCode:
                    dictionaryCode[code] = word
        return dictionary, dictionaryCode, weight

    def create_simple_graph(self,peso, paragraphs_code, dictionaryCode, dist):
        g = nx.DiGraph() #indirect Graph
        g2 = nx.DiGraph() #direct Grap

        #calc the weight of each vertice
        for code, weight in peso.items():
            g.add_node(code, peso=weight, dicionario=dictionaryCode[code])
            g2.add_node(code, peso=weight, dicionario=dictionaryCode[code])

        #create and weight edges
        for line in paragraphs_code:
            i = 0
            for word in line:
                i = i + 1
                j = 0
                for word2 in line:
                    j = j + 1
                    if j - i < dist and j - i > 0: #indirect edges
                        if g.has_edge(word, word2):
                            g[word][word2]['weight'] += 1 - log(j-i,dist)
                        else:
                            if word != word2:
                                g.add_edge(word, word2, weight=float(1 - log(j-i,dist)))
                    if j - i == 1: #direct edges
                        if g2.has_edge(word, word2):
                            g2[word][word2]['weight'] += 1
                        else:
                            if word != word2:
                                g2.add_edge(word, word2, weight=1)
        return g, g2

    def save_clusters_txt(self, saveFile, Clusters):
        f=open(saveFile,"w+")
        for c in Clusters:
            line = ''
            for n in c:
                line += n + ' '
            f.write(line[:-1] + '\n')
        f.close()
        return


    def saveClusters(self, saveFile="", Clusters=[], crisp="", clusterType='normal'):
        file = ''
        #save clusters

        #write crisp
        if crisp != "":
            with open(saveFile + "crisp.pickle", "wb") as fp:
                pickle.dump(crisp, fp, protocol=2)

            f=open(saveFile + "crisp.txt","w+")
            for c in crisp:
                line = ''
                for n in c:
                    line += n + ' '
                f.write(line[:-1] + '\n')
            f.close()

        #write normal clusters
        if clusterType =='normal':
            with open(saveFile + "clusters.pickle", "wb") as fp:
                pickle.dump(Clusters, fp, protocol=2)

            f=open(saveFile + "clusters.txt","w+")
            for c in Clusters:
                line = ''
                for n in c:
                    line += n + ' '
                f.write(line[:-1] + '\n')
            f.close()

        #write reduced clusters
        elif clusterType =='reduced':
            with open(saveFile + "reducedClusters.pickle", "wb") as fp:
                pickle.dump(Clusters, fp, protocol=2)

            f=open(saveFile + "reducedClusters.txt","w+")
            for c in Clusters:
                line = ''
                for n in c:
                    line += n + ' '
                f.write(line[:-1] + '\n')
            f.close()

        else:
            print('Wrong cluster Type!\nCluster not saved')

    def save_variables_pickle(self):
        save = []
        save.append(self.graphName)
        save.append(self.dictionaries)
        save.append(self.dictionariesCode)
        save.append(self.graphsI)
        save.append(self.graphsD)
        save.append(self.dictionaryCodeMerged)
        save.append(self.sciKGraph)
        save.append(self.crisp_clusters)
        save.append(self.pre_processed_graph)
        save.append(self.clusters)

        file = pickle.dumps(save, protocol=2)
        #with open('/home/mauro/Downloads/testeDownload.sckg', "wb") as fp:
        #    pickle.dump(save, fp, protocol=2)


        return file


    def save_variables(self,output_file, save_graph_name=False, save_directories = False, save_directories_code = False, save_graphs_i = False, save_graphs_d = False, save_directories_code_merged = False, save_SciKGraph = False, save_clusters = False, save_crisp_clusters = False, save_pre_processed_graph = False):
        save = []
        save.append(self.graphName)
        save.append(self.dictionaries)
        save.append(self.dictionariesCode)
        save.append(self.graphsI)
        save.append(self.graphsD)
        save.append(self.dictionaryCodeMerged)
        save.append(self.sciKGraph)
        save.append(self.crisp_clusters)
        save.append(self.pre_processed_graph)
        save.append(self.clusters)


        try:
            with open(output_file, "wb") as fp:
                pickle.dump(save, fp, protocol=2)
        except:
            raise

        return

        '''
        try:
            if save_graph_name:
                with open(output_directory + "graphName.pickle", "wb") as fp:
                    pickle.dump(self.graphName, fp)

            if save_directories:
                with open(output_directory + "dictionaries.pickle", "wb") as fp:
                    pickle.dump(self.dictionaries, fp)

            if save_directories_code:
                with open(output_directory + "dictionariesCode.pickle", "wb") as fp:
                    pickle.dump(self.dictionariesCode, fp)

            if save_graphs_i:
                with open(output_directory + "graphsI.pickle", "wb") as fp:
                    pickle.dump(self.graphsI, fp)

            if save_graphs_d:
                with open(output_directory + "graphsD.pickle", "wb") as fp:
                    pickle.dump(self.graphsD, fp)

            if save_directories_code_merged:
                with open(output_directory + "dictionaryCodeMerged.pickle", "wb") as fp:
                    pickle.dump(self.dictionaryCodeMerged, fp)

            if save_SciKGraph:
                with open(output_directory + "sciKGraph.pickle", "wb") as fp:
                    pickle.dump(self.sciKGraph, fp)

            if save_clusters:
                with open(output_directory + "clusters.pickle", "wb") as fp:
                    pickle.dump(self.clusters, fp)

            if save_crisp_clusters:
                with open(output_directory + "crisp_clusters.pickle", "wb") as fp:
                    pickle.dump(self.crisp_clusters, fp)


            if save_pre_processed_graph:
                with open(output_directory + "pre_processed_graph.pickle", "wb") as fp:
                    pickle.dump(self.pre_processed_graph, fp)
        except:
            raise
            '''

    def open_variables_pickle(self, file):
        data = pickle.load(file)

        self.graphName = data[0]
        self.dictionaries = data[1]
        self.dictionariesCode = data[2]
        self.graphsI = data[3]
        self.graphsD = data[4]
        self.dictionaryCodeMerged = data[5]
        self.sciKGraph = data[6]
        self.crisp_clusters = data[7]
        self.pre_processed_graph = data[8]
        self.clusters = data[9]




    def open_variables(self,open_directory, open_graph_name=False, open_directories = False, open_directories_code = False, open_graph_i = False, open_graph_d = False, open_dictionary_code_merged = False, open_SciKGraph = False, open_clusters = False, open_crisp_clusters = False, open_pre_processed_graph = False):

        with open(open_directory, "rb") as fp:
            data = pickle.load(fp)

        self.graphName = data[0]
        self.dictionaries = data[1]
        self.dictionariesCode = data[2]
        self.graphsI = data[3]
        self.graphsD = data[4]
        self.dictionaryCodeMerged = data[5]
        self.sciKGraph = data[6]
        self.crisp_clusters = data[7]
        self.pre_processed_graph = data[8]
        self.clusters = data[9]

        return


        '''
        try:
            if open_graph_name:
                with open (open_directory + "graphName.pickle", 'rb') as fp:
                    self.graphName = pickle.load(fp)

            if open_directories:
                with open (open_directory + "dictionaries.pickle", 'rb') as fp:
                    self.dictionaries = pickle.load(fp)

            if open_directories_code:
                with open (open_directory + "dictionariesCode.pickle", 'rb') as fp:
                    self.dictionariesCode = pickle.load(fp)

            if open_graph_i:
                with open (open_directory + "graphsI.pickle", 'rb') as fp:
                    self.graphsI = pickle.load(fp)

            if open_graph_d:
                with open (open_directory + "graphsD.pickle", 'rb') as fp:
                    self.graphsD = pickle.load(fp)

            if open_dictionary_code_merged:
                with open (open_directory + "dictionaryCodeMerged.pickle", 'rb') as fp:
                    self.dictionaryCodeMerged = pickle.load(fp)

            if open_SciKGraph:
                with open (open_directory + "sciKGraph.pickle", 'rb') as fp:
                    self.sciKGraph = pickle.load(fp)

            if open_clusters:
                with open (open_directory + "clusters.pickle", 'rb') as fp:
                    self.clusters = pickle.load(fp)

            if open_crisp_clusters:
                with open (open_directory + "crisp_clusters.pickle", 'rb') as fp:
                    self.crisp_clusters = pickle.load(fp)

            if open_pre_processed_graph:
                with open (open_directory + "pre_processed_graph.pickle", 'rb') as fp:
                    self.pre_processed_graph = pickle.load(fp)
        except:
            raise
            '''



    def clear_variables(self):
        self.key = ''
        self.inputFile = ''
        self.outputDirectory = ''
        self.distance_window = 0
        self.graphName = []
        self.dictionaries = []
        self.dictionariesCode = []
        self.graphsI = []
        self.graphsD = []
        self.sciKGraph = 0
        self.dictionaryCodeMerged = {}
        self.name=""
        return

    def create_single_SciKGraph(self,filename, babelfy_key, language, distance_window):
        text = filename.decode('ascii')
        st = self.parse_text(text)
        pa, pt, pc  = self.babelfy(language, babelfy_key, st)
        d, dc, p = self.create_dicts(pt, pc)

        gI, gD = self.create_simple_graph(p, pc, dc, distance_window)
        return d, dc, gI, gD


    #Merges graphs and dictionaries
    ## graphs: list of graphs to merge
    ## dictionaryCode: list of the graphs dictionaries
    def merge_graphs(self,graphs, dictionaryCode):
        #create dictionaryCodeMerged
        dictionaryCodeMerged = {}
        for dic in dictionaryCode:
            for w in dic:
                if w not in dictionaryCodeMerged:
                    dictionaryCodeMerged[w] = dic[w]


        #merge graphs
        graph = nx.compose_all(graphs).copy()

        #reset nodes weights
        for i in graph.nodes():
            graph.nodes()[i]['peso'] = 0

        #recalc nodes weights
        for i in range(len(graphs)):
            for n in graphs[i]:
                graph.nodes()[n]['peso'] += graphs[i].nodes()[n]['peso']
                graph.nodes()[n]['dicionario'] = dictionaryCodeMerged[n]

        #reset arc weight
        for i in graph.edges():
            graph[i[0]][i[1]]['weight'] = 0

        #recalc arc weight
        for i in range(len(graphs)):
            for e in graphs[i].edges():
                graph[e[0]][e[1]]['weight'] += graphs[i][e[0]][e[1]]['weight']



        return graph, dictionaryCodeMerged

    def create_SciKGraph(self, files, file_names, babelfy_key = None, language = 'EN', graphType = 'direct', distance_window=2, mergeIfFail = False):
        distance_window = distance_window + 1
        if distance_window <=2:
            graphType = 'direct'
        else:
            graphType = 'indirect'

        self.language = language

        #check if scikgraph should be fully updated (occurs when distance window changes)
        if self.distance_window != distance_window:
            self.distance_window = distance_window
            self.graphName = []

        toMerge = []
        count = 0
        added = 0
        for file, file_name in zip(files, file_names):
            count += 1
            if file_name not in self.graphName:
                try:
                    d, dc, gI, gD = self.create_single_SciKGraph(file, babelfy_key, language, distance_window)

                    self.graphName.append(file_name)
                    self.dictionaries.append(d)
                    self.dictionariesCode.append(dc)
                    self.graphsI.append(gI)
                    self.graphsD.append(gD)
                    added += 1

                except Exception as e:
                    if len(self.graphName) > 0 or mergeIfFail:
                        print('Error Babelfying text (check your Babelcoins)\n', e, '\n')
                        print(self.graphName, '\nThe documents in \'graphName\' were correctly babelfied.\nThe SciKGraph was created with the correctly babelfied texts, to update this version with the other texts fix the error (probably babelfy key error) and run this method again.')
                        break
                    else:
                        if len(self.graphName) > 0:
                            print(self.graphName, '\nThe documents in \'graphName\' were correctly babelfied.\nTo create the SciKGraph (using the previously babelfied documents) run this method again.\n')
                        print('Error Babelfying text (check your Babelcoins)\n')
                        raise

            if graphType == 'direct':
                toMerge = self.graphsD
            elif graphType == 'indirect':
                toMerge = self.graphsI
            else:
                print('graphType not listed!\nDirect graph used.')
                toMerge = self.graphsD

        #check if at leat 1 graph can be added to scikgraph
        if added > 0:
            graph, dictionaryMerged = self.merge_graphs(toMerge, self.dictionariesCode)
            self.sciKGraph = graph
            self.dictionaryCodeMerged = dictionaryMerged

        return self.sciKGraph, self.dictionaryCodeMerged

    def find_communities(self, g, edges_threshold, nodes_threshold):
        ocr = OCR.OClustR()
        self.clusters, self.crisp_clusters, self.pre_processed_graph = ocr.identify_clusters(g, edges_threshold, nodes_threshold)
        return self.clusters, self.crisp_clusters, self.pre_processed_graph

    def cluster_graph(self, g):
        ocr = OCR.OClustR()
        self.clusters, self.crisp_clusters, self.sciKGraph = ocr.cluster_graph(g)
        return



    def pre_process_graph(self, g, edges_threshold, nodes_threshold, list_edges = [], list_nodes = []):
        oClustR = OCR.OClustR()
        g, rem_e, rem_n, rem_iso_n = oClustR.pre_process(g, edges_threshold, nodes_threshold, list_edges, list_nodes)
        self.pre_processed_graph = g
        self.deleted_isolated_nodes = rem_iso_n
        self.deleted_nodes = rem_n
        self.deleted_edges = rem_e
        return

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


    def start(self, inputDirectory, babelfy_key, edges_threshold=0, nodes_threshold=0, list_nodes = [], list_edges = [], language = 'EN', graphType = 'direct', distance_window=2, mergeIfFail = False):
        if babelfy_key == None:
            babelfy_key = self.key

        filenames = []

        try:
            for filename in sorted(glob.glob(os.path.join(inputDirectory, '*.txt'))):
                filenames.append(filename)
            if len(filename) == 0:
                raise EmptyDirectoryError('There is no .txt file in the inputDirectory.')
        except:
            raise


        self.sciKGraph, self.dictionaryCodeMerged = self.create_SciKGraph(filenames, babelfy_key, language, graphType, distance_window, mergeIfFail)
        return self.sciKGraph
        #oClustR = OCR.OClustR()
        #self.clusters, self.crisp_clusters, self.pre_processed_graph = oClustR.identify_clusters(self.sciKGraph, edges_threshold, nodes_threshold)

        #return self.clusters, self.pre_processed_graph
