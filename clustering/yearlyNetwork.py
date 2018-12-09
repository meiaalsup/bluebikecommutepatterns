import csv
import numpy as np
import networkx as nx
import collections
import matplotlib.pyplot as plt
import scipy
import random
from itertools import count
from collections import Counter
from collections import defaultdict
from matplotlib import cm
import pandas as pd
from sklearn import cluster
from dateutil import parser
from multiprocessing import Pool
from functools import partial
import folium


### CREATION ###
def createGraph(fn):
    with open(str(fn)) as csv_file:
        nodes = []
        edges = []
        weights = {}
        node_loc = {}
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            else: 
                start = row[3]
                end = row[7]
                #add new nodes
                if start not in nodes:
                    nodes.append(start)
                    node_loc[start] = (float(row[6]),float(row[5]))
                if end not in nodes:
                    nodes.append(end)
                    node_loc[end] = (float(row[10]),float(row[9]))

                weights[(start,end)] = weights.get((start,end), 0) + 1
        
        #save network
        return Counter(weights), nodes, node_loc

def topEdges(edges):
    #print(G.get_edge_data(edges[0][0],edges[0][1]))
    newEdges = sorted(edges, key=lambda t: t[2], reverse=True)[:50]
    #print(newEdges)

MEdges = []
MVertices = []
MWeights = Counter({})
EEdges = []
EVertices = []
EWeights = Counter({})
locsM = {}
locsE = {}

#create maps of routes for each month - morning and evening
for i in range(13): #13
    mornFile = 'Month' + str(i) + '-cleaned-morning.csv'
    eveFile = 'Month' + str(i) + '-cleaned-evening.csv'

    Mweight, MNodes, node_locM = createGraph(mornFile)
    Eweight, ENodes, node_locE = createGraph(eveFile)

    MWeights = MWeights + Mweight
    EWeights = EWeights + Eweight

    locsM = node_locM
    locsE = node_locE
    MVertices = MNodes
    EVertices = ENodes

#edges
MEdges = [(p[0], p[1], MWeights[p]) for p in MWeights]
EEdges = [(p[0], p[1], EWeights[p]) for p in EWeights]

#create graphs 
OverallM = nx.DiGraph()
OverallM.add_nodes_from(MVertices)
OverallM.add_weighted_edges_from(MEdges)
nx.set_node_attributes(OverallM, 'Position', locsM)

OverallE = nx.DiGraph() 
OverallE.add_nodes_from(EVertices)
OverallE.add_weighted_edges_from(EEdges)
nx.set_node_attributes(OverallE, 'Position', locsE)

eveclusters = pd.read_pickle("cluterLabels-evening.pkl")
mornclusters = pd.read_pickle("cluterLabels-morning.pkl")
print(len(eveclusters))
#print(mornclusters, len(mornclusters))

#nx.write_gml(OverallE, "Overall-graphEve-cluster.gml", stringizer=str)
#nx.write_gml(OverallM, "Overall-graphMorn-cluster.gml", stringizer=str)
evedict = eveclusters.to_dict(orient='index')
morndict = mornclusters.to_dict(orient='index')
print()
###PRINT IMAGE###
def plot_stations(graph, clabels):
    lat = [] 
    lon = []
    names = []
    clusters = []
    #print(clabels)
    print(len(G.nodes()))
    failed = []
    pos = {}
    clust = {}

    for node, attr in graph.nodes(data=True):
        if(attr):
            try: 
                l = clabels[int(node)]['Label']
                clusters.append(l)
                pos[node] = (attr['Position'][0], attr['Position'][1])
                clust[node] = l
                #lon.append(attr['Position'][0])
                #lat.append(attr['Position'][1])
                names.append(node)
            except:
                failed.append(node)
        else:
             print("failed attr", node, attr)
    print(failed) 
    # Plot...
    plt.figure(figsize = (10,9))
    
    m = folium.Map([42.337102, -71.1], tiles='Stamen Terrain', zoom_start=12, max_zoom=18)
    '''for _id, coords in pos.items():
        folium.CircleMarker(
            [coords[1], coords[0]],
            radius = 1,
            popup=f'{_id}',
        ).add_to(m)'''

    #plt.scatter(lon, lat, c=clusters, s=10, cmap='tab10')
    nx.draw_networkx_nodes(G = graph, pos = pos, node_list = graph.nodes(), alpha = 0.8, node_size = 20, node_color = clusters, cmap ="tab10")

    #buffer = .02
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    # adjust axis because of 0 (null) values in lat / long
    #plt.ylim((min([i for i in lat if i > 0])-buffer, max(lat)+buffer))
    #plt.xlim((min(lon)-buffer, max([i for i in lon if i < 0])+buffer))

    plt.show()

#plot_stations(OverallE, evedict)
# plot_stations(OverallM, morndict)

def graph_to_edge_matrix(G):
    """Convert a networkx graph into an edge matrix.
    See https://www.wikiwand.com/en/Incidence_matrix for a good explanation on edge matrices
   
    Parameters
    ----------
    G : networkx graph
    """
    # Initialize edge matrix with zeros
    intNodes = [int(i) for i in G.nodes()]
    print("NumNodes : " + str(len(G)))

    maxN = max(intNodes) + 1
    edge_mat = np.zeros((maxN, maxN), dtype=int)

    # Loop to set 0 or 1 (diagonal elements are set to 1)
    for start, end, a in G.edges(data=True):
        weight = a['weight']
        edge_mat[int(start)][int(end)] += weight

    return edge_mat

k_clusters = 3

MMatrix = graph_to_edge_matrix(OverallM)
EMatrix = graph_to_edge_matrix(OverallE)

MModel = cluster.KMeans(n_clusters=k_clusters, n_init=200)
EModel = cluster.KMeans(n_clusters=k_clusters, n_init=200)

MModel.fit(MMatrix)
EModel.fit(EMatrix)

ELabels = list(EModel.labels_)
MLabels = list(MModel.labels_)
Edf = pd.DataFrame(data = ELabels, index = range(len(EMatrix)), columns = ['Label'])

Mdf = pd.DataFrame(data = MLabels, index = range(len(MMatrix)), columns = ['Label'])

newMdict = Mdf.to_dict(orient='index')
newEdict = Edf.to_dict(orient='index')

plot_stations(OverallE, newEdict)
plot_stations(OverallM, newMdict)
