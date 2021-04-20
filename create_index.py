from bs4 import BeautifulSoup
from collections import defaultdict
import cPickle as pickle
import os
import lxml.html
import re
import io
import sys
import math

class Posting():
    def __init__(self,docid,wf,indices,tf_idf,doc_length):
        self.docid = docid
        self.wf = wf
        self.indices = indices
        self.tf_idf = tf_idf
        self.doc_length = doc_length

    def getdocid(self):
        return self.docid

    def getwf(self):
        return self.wf

    def getindices(self):
        return self.indices

    def gettf_idf(self):
        return self.tf_idf

    def getdoc_length(self):
        return self.doc_length

invalid = ["b","c","d","e","f","g","h","j","k","l","m","n","o","p","q","r","s","t","u",
           "v","w","x","z",r"\""]
inv_index = defaultdict(list)

def tokenize(txt):
    txt = re.sub(r'[^\s\w|_]', ' ', txt)
    txt = txt.replace(u'\ufeff', ' ')
    tokens = txt.split(' ')
    tokens = re.split("[\s\n]+", txt)
    tokens.remove('')
    return tokens

def calcTf(tokens):
    #dictionary for words
    list = {}

    #counting how many each word occurs in the text
    for word in tokens:
        list[word] = list.get(word, 0) + 1

    tfDictonary = {}  #dictionary for TF values

    num_of_words = len(tokens) #total number of words in the page(or tokens)

    #for each word, calculate the TF value.
    for word, count in list.items():
        tfDictonary[word] = count/float(num_of_words)

    return tfDictonary

def calc_idf():
    idfcount = {}
    idf = {}
    os.chdir('WEBPAGES_RAW')
    directory = os.getcwd()
    folder_count = 0
    doc_count = 0
    N = 0
    for i in os.listdir(directory):
        if "bookkeeping" not in i and "data" not in i:
            os.chdir(str(folder_count))
            cur_folder = os.getcwd()
            docs = os.listdir(cur_folder)
            doc_count = 0
            for doc in docs:

                doc_folder = os.getcwd()
                doc_name = os.listdir(doc_folder)[doc_count]
                fname = os.path.join(doc_folder,doc_name)
                print(fname)
                with io.open(fname, 'r', encoding="utf8") as f:
                    corpus = dict()
                    soup = BeautifulSoup(f.read(), 'lxml')

                tokens = tokenize(str(soup.find_all()))
                tokens = set(tokens)

                for word in tokens:
                    lower = word.lower()
                    if lower not in invalid:
                        idfcount[lower] = idfcount.get(lower, 0) + 1
                        

                doc_count += 1
                N+= 1
            folder_count += 1
            os.chdir(directory)
            if (folder_count == 75):
                break

    for word, counts in idfcount.items():
        idf[word] = math.log10(N / float(counts))

    os.chdir(directory)
    return idf


if __name__ == '__main__':
    sys.setrecursionlimit(100000)
    
    idf = calc_idf()4
    
    directory = os.getcwd()
    folder_count = 0
    doc_count = 0
    for i in os.listdir(directory):
        if "bookkeeping" not in i and "data" not in i:
            os.chdir(str(folder_count))
            cur_folder = os.getcwd()
            doc_count = 0
            docs = os.listdir(cur_folder)
            #print("printing docs")
            #print(docs)
            for doc in docs:
                doc_folder = os.getcwd()
                doc_name = os.listdir(doc_folder)[doc_count]
                fname = os.path.join(doc_folder,doc_name)
                print(fname)
                with io.open(fname, 'r', encoding="utf8") as f:
                    corpus = dict()
                    soup = BeautifulSoup(f.read(), 'lxml')

                tokens = tokenize(str(soup.find_all()))
                doc_length = len(tokens)
                tokens = set(tokens)
                tfidf = {}
                tf = calcTf(tokens)
                for word , tfvalue in tf.items():
                    lower = word.lower()
                    if lower not in invalid:
                        tfidf[lower] = tfvalue*idf[lower]

                indexed_tokens = enumerate(tokens)
                indices = defaultdict(list)
                docid = str(folder_count) + '/' + doc_name
                for index,token in indexed_tokens:
                    lower = token.lower()
                    if lower not in invalid:
                        indices[lower].append(index)
                for token in indices:
                    posting = Posting(docid,len(indices[token]),indices[token],tfidf[token],doc_length)
                    inv_index[token].append(posting)

                doc_count += 1
            folder_count += 1
            os.chdir(directory)
            if (folder_count == 75):
                break
    print(doc_count)
    os.chdir(directory)
    pickle.dump(inv_index, open("data.p", "wb"))
