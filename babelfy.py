'''
Created on 02/12/2015

@author: David
'''
from __future__ import print_function
import json
import sys

if sys.version_info[0] == 3:
    import urllib.request
else:
    import urllib
    
class BabelfyJSONKeys(object):
    
    
    TOKEN_FRAGMENT = "tokenFragment"
    CHAR_FRAGMENT = "charFragment"
    CHAR_FRAGMENT_START = "start"
    CHAR_FRAGMENT_END = "end"
    BABEL_SYNSET_ID = "babelSynsetID"
    DBPEDIA_URL = "DBpediaURL"
    BABELNET_URL = "BabelNetURL"
    SCORE = "score"
    COHERENCE_SCORE = "coherenceScore" 
    GLOBAL_SCORE ="globalScore"
    SOURCE =  "source"

class AnnTypeValues(object):
    
    ALL = "ALL" #Disambiguates all
    CONCEPTS = "CONCEPTS" #Disambiguates concepts only
    NAMED_ENTITIES = "NAMED_ENTITIES" #Disambiguates named entities only
    
class AnnResValues(object):
    BN = "BN" #Annotate with BabelNet synsets
    WIKI = "WIKI" #Annotate with Wikipedia page titles
    WN = "WN" #Annotate with WordNet synsets

class MatchValues(object):
    EXACT_MATCHING = "EXACT MATCHING" #Only exact matches are considered for disambiguation
    PARTIAL_MATCHING = "PARTIAL MATCHING" #Both exact and partial matches (e.g.
    
class MCSValues(object):
    OFF = "OFF" #Do not use Most Common Sense
    ON = "ON" #Use Most Common Sense
    ON_WITH_STOPWORDS = "ON_WITH_STOPWORDS" #Use Most Common Sense even on Stopwords

class CandsValues(object):
    ALL = "ALL" #Return all candidates for a fragment.
    TOP = "TOP" #Return only the top ranked candidate for a fragment.

class PosTagValues(object):
    #Tokenize the input string by splitting all characters as single tokens 
    #(all tagged as nouns, so that we can disambiguate nouns).
    CHAR_BASED_TOKENIZATION_ALL_NOUN = "CHAR_BASED_TOKENIZATION_ALL_NOUN" 
    INPUT_FRAGMENTS_AS_NOUNS = "INPUT_FRAGMENTS_AS_NOUNS" #Interprets input fragment words as nouns.
    NOMINALIZE_ADJECTIVES = "NOMINALIZE_ADJECTIVES"  #Interprets all adjectives as nouns.
    STANDARD = "STANDARD" #Standard PoS tagging process.

class SemanticAnnotation(object):
           
    def __init__(self,babelfy_dict):
        self.babelfy_dict = babelfy_dict
    
    def babelfy_dict(self):
        return self.babelfy_dict    
    
    def token_fragment(self):
        return self.babelfy_dict[BabelfyJSONKeys.TOKEN_FRAGMENT]
    
    def char_fragment(self):
        return self.babelfy_dict[BabelfyJSONKeys.CHAR_FRAGMENT]
    
    def char_fragment_start(self):
        return self.char_fragment()[BabelfyJSONKeys.CHAR_FRAGMENT_START]
    
    def char_fragment_end(self):
        return self.char_fragment()[BabelfyJSONKeys.CHAR_FRAGMENT_END]
    
    def babel_synset_id(self):
        return self.babelfy_dict[BabelfyJSONKeys.BABEL_SYNSET_ID]
    
    def dbpedia_url(self):
        return self.babelfy_dict[BabelfyJSONKeys.DBPEDIA_URL]
    
    def babelnet_url(self):
        return self.babelfy_dict[BabelfyJSONKeys.BABELNET_URL]
    
    def coherence_score(self):
        return self.babelfy_dict[BabelfyJSONKeys.COHERENCE_SCORE]
    
    def global_score(self):
        return self.babelfy_dict[BabelfyJSONKeys.GLOBAL_SCORE]
    
    def source(self):
        return self.babelfy_dict[BabelfyJSONKeys.SOURCE]
    
    def postag(self):
        return self.babel_synset_id()[-1]

    
    def pprint(self):
        print(self.babel_synset_id())
        print(self.babelnet_url())
        print(self.dbpedia_url())
        print(self.source())

class Babelfy(object):

    TEXT = "text"
    LANG = "lang"
    KEY = "key"
    ANNTYPE= "annType"
    ANNRES = "annRes"
    TH = "th"
    MATCH = "match"
    MCS = "MCS"
    DENS = "dens"
    CANDS = "cands"
    POSTAG = "postag"
    EXTAIDA = "extAIDA"
        
    PARAMETERS = [TEXT,LANG,KEY,ANNTYPE,ANNRES,TH,MATCH,MCS,DENS,CANDS,POSTAG,EXTAIDA]
    
    API = "https://babelfy.io/v1/"
    DISAMBIGUATE = "disambiguate?"
    
        
    def disambiguate(self, text,lang,key, anntype=None, annres=None, th=None,
                     match=None,mcs=None,dens=None,cands=None,postag=None,
                     extaida=None):
        
        values = [text,lang,key,anntype,annres,th,match,mcs,dens,
                            cands,postag,extaida]
        
        query = "&".join([param+"="+value for param,value in zip(self.PARAMETERS, values)
                         if value is not None])

        if sys.version_info[0] == 3:
        	with urllib.request.urlopen(self.API+self.DISAMBIGUATE+query) as url:
            		json_string = url.read()
        else:
        	json_string = urllib.urlopen(self.API+self.DISAMBIGUATE+query).read()
        babelfy_jsons = json.loads(json_string)
        return [SemanticAnnotation(babelfy_json) for babelfy_json in babelfy_jsons]
