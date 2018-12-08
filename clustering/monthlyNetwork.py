import csv
import numpy as np
import networkx as nx
import collections
import matplotlib.pyplot as plt
import scipy
import random
from itertools import count

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
        edges = [(p[0], p[1], weights[p]) for p in weights]
        #edges = topEdges(edges)

    # create graph
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(edges)
    return G, node_loc
    #print(G.nodes())
    #print("Number of nodes: ", G.number_of_nodes())
    #print("Number of solo offenders: ", len(list(nx.isolates(G))))
    #print ("Number of edges: ", G.number_of_edges())
    #print ("Number of connected components - pre: ", nx.number_connected_components(G))

def topEdges(edges):
    #print(G.get_edge_data(edges[0][0],edges[0][1]))
    newEdges = sorted(edges, key=lambda t: t[2], reverse=True)[:50]
    #print(newEdges)
    return newEdges


#create maps of routes for each month - morning and evening
OverallM = nx.DiGraph()
OverallE = nx.DiGraph()

for i in range(13):
    mornFile = 'Month' + str(i) + '-cleaned-morning.csv'
    eveFile = 'Month' + str(i) + '-cleaned-evening.csv'
    M, node_locM = createGraph(mornFile)
    E, node_locE = createGraph(eveFile)

    nx.set_node_attributes(M, 'Position', node_locM)
    nx.set_node_attributes(E, 'Position', node_locE)

    nx.compose(OverallM,M)
    nx.compose(OverallE,E)

    nx.write_gml(E, "Month" + str(i) + "-graphEve.gml", stringizer=str)
    nx.write_gml(M, "Month" + str(i) + "-graphMorn.gml", stringizer=str)

    Edegree = nx.degree(E)
    Mdegree = nx.degree(M)

    #pos = node_loc 

    Medges = M.edges() #topEdges(M.edges(), M)
    Eedges = E.edges() #topEdges(E.edges(), E)

    #print(pos)

    Mweights = [M[u][v]['weight'] for u,v in Medges]
    Eweights = [E[u][v]['weight'] for u,v in Eedges]

    '''
    nx.draw(E, pos, nodelist=Edegree.keys(), edges=Eedges, with_labels=True, node_size=[v for v in Edegree.values()], width=Eweights)
    #nx.draw(E, pos, edges=Eedges, )
    title = "Month" + str(i) + "-graphEve"
    plt.title(title)
    plt.show()
    plt.savefig(title + '.png')

    #nx.draw(M, pos, edges=Medges, )
    nx.draw(M, pos, nodelist=Mdegree.keys(), with_labels=True, edges=Medges ,node_size=[v for v in Mdegree.values()], width=Mweights)
    title = "Month" + str(i) + "-graphMorn"
    plt.title(title)
    plt.savefig(title + '.png')
    '''

nx.write_gml(OverallE, "Overall-graphEve.gml", stringizer=str)
nx.write_gml(OverallM, "Overall-graphMorn.gml", stringizer=str)

