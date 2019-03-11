import os
import xmltodict
import types
import collections

ordereddict = collections.OrderedDict()

def find_keys(col, L):
    if type(col) == type(""):
        return []
    else:
        #print(list(col.keys()))
        if type(col) == type(ordereddict):
            L.extend(list(col.keys()))
            for item in col:
                find_keys(col[item], L)
        else:
            for i in range(len(col)):
                if type(col[i]) == type(ordereddict):
                    find_keys(col[i], L)

with open("NCT00029822.xml") as content1, open("NCT00172107.xml") as content2, open("NCT00430677.xml") as content3:
    doc1 = xmltodict.parse(content1.read())
    doc2 = xmltodict.parse(content2.read())
    doc3 = xmltodict.parse(content3.read())
    L1 = []
    L2 = []
    L3 = []
    find_keys(doc1, L1)
    find_keys(doc2, L2)
    find_keys(doc3, L3)

    print(set(L1))
    print(set(L2))
    print(set(L3))