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
import math 
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D

# map { station # : [in-degree, out-degree,#bikes, long, lat, trip-duration-in, trip-duration-out, avgAgeOut]}
def createList(fn, stations):
    with open(str(fn)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            else: 
                start = int(row[3])
                end = int(row[7])
                time = float(row[0])/60.0
                try: 
                    age = 2018 - float(row[13]) #offset age to reasonable #
                except:
                    age = 30
                latStart = float(row[5])
                lonStart = float(row[6])
                latEnd = float(row[9])
                lonEnd = float(row[10])
                #add new nodes
                [inDeg, outDeg, numBikes, _, _, tripDurIn, tripDurOut, avgAge] = stations[start]
                stations[start] = [inDeg, outDeg + 1, numBikes, lonStart, latStart, tripDurIn, tripDurOut + time, avgAge + age]

                [inDeg, outDeg, numBikes, _, _, tripDurIn, tripDurOut, avgAge] = stations[end]
                stations[end] = [inDeg + 1, outDeg, numBikes, lonEnd, latEnd, tripDurIn + time, tripDurOut, avgAge + age]
    return stations

def averageAges(stations):
    toRemove = []
    for station in stations:
        [inDeg, outDeg, numBikes, lon, lat, tripDurIn, tripDurOut, age] = stations[station]
        
        if lon == 0 or lat ==0 :
            toRemove.append(station)
        else:
            avgAge = (age)/(inDeg + outDeg)
            if inDeg != 0:
                avgTimeIn = tripDurIn/inDeg
            else:
                avgTimeIn = 0
            
            if outDeg != 0:
                avgTimeOut = tripDurOut/outDeg
            else:
                avgTimeOut = 0
            
            stations[station] = [math.sqrt(inDeg), math.sqrt(outDeg), numBikes, lon, lat, avgTimeIn, avgTimeOut, avgAge]
    
    for station in toRemove:
        del stations[station]
    return stations

def namesToBikes(rides,numBikes):
    namesToNum = {}
    with open(str(numBikes)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            else: 
                name = row[1]
                numBikes = int(row[5])
                namesToNum[name] = numBikes
    numToNum = {}
    with open(str(rides)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            else: 
                nameStart = row[4]
                numStart = int(row[3])
                nameEnd = row[8]
                numEnd = int(row[7])
                if not (numStart in numToNum) and nameStart in namesToNum:
                    numToNum[numStart] = namesToNum[nameStart]
                if not (numEnd in numToNum) and  nameEnd in namesToNum:
                    numToNum[numEnd] = namesToNum[nameEnd] - 11# 17.544 #center at avg
    return numToNum
                
def addNumBikes(stations, numBike):
    for station in stations:
        if station in numBike:
            stations[station][2] = numBike[station]
        else:
            stations[station][2] = 11

# map { station # : [0 in-degree,1 out-degree,2 #bikes,3 long,4 lat, 5 trip-duration-in,6 trip-duration-out,7 avgAgeOut]}
def createAttributeList():
    mornList = defaultdict(lambda : [0,0,0,0,0,0,0,0])
    eveList = defaultdict(lambda : [0,0,0,0,0,0,0,0])
    for i in range(2): #13
        mornFile = 'Month' + str(i) + '-cleaned-morning.csv'
        eveFile = 'Month' + str(i) + '-cleaned-evening.csv'
        mornList = createList(mornFile, mornList)
        eveList = createList(eveFile, eveList)
    
    #add number of bikes
    numBike = namesToBikes('Month12-cleaned-morning.csv', 'Hubway_Stations_as_of_July_2017.csv')
    addNumBikes(mornList, numBike)
    addNumBikes(eveList, numBike)

    #average ages
    mornList = averageAges(mornList)
    eveList = averageAges(eveList)

    return mornList, eveList

from matplotlib.text import Annotation
from mpl_toolkits.mplot3d.proj3d import proj_transform
class Annotation3D(Annotation):
    '''Annotate the point xyz with text s'''

    def __init__(self, s, xyz, *args, **kwargs):
        Annotation.__init__(self,s, xy=(0,0), *args, **kwargs)
        self._verts3d = xyz        

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.xy=(xs,ys)
        Annotation.draw(self, renderer)

def annotate3D(ax, s, *args, **kwargs):
    '''add anotation text s to to Axes3d ax'''
    tag = Annotation3D(s, *args, **kwargs)
    ax.add_artist(tag)

def performPCA(dfM):
    #dfM = StandardScaler().fit_transform(dfM)
    #print(dfM)

    pca = PCA(n_components=3)
    principalComponents = pca.fit_transform(dfM)
    principalDf = pd.DataFrame(data = principalComponents, index = dfM.index, columns = ['PC1', 'PC2', 'PC3'])

    #print("PCA")
    #print(principalDf)
    varRatio = pca.explained_variance_ratio_
    #print(varRatio)
    label =  "Explained Variance Ratio: " + str(varRatio[0]) + " , " + str(varRatio[1])+ " , " + str(varRatio[2])
    print(label, sum(varRatio))
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    xs = principalDf['PC1'].tolist()
    ys = principalDf['PC2'].tolist()
    zs = principalDf['PC3'].tolist()
    ax.scatter(xs,ys,zs)

    ax.set_xlabel('Principal Component 1', fontsize = 15)
    ax.set_ylabel('Principal Component 2', fontsize = 15)
    ax.set_zlabel('Principal Component 3', fontsize = 15)
    ax.set_title('3 component PCA', fontsize = 20)
    #ax.text(x=70,y=-20,z=0, s=label)
    xyzn = zip(xs, ys, zs)
    indices = principalDf.index.values
    for j, xyz_ in enumerate(xyzn):
        annotate3D(ax, s=str(indices[j]), xyz=xyz_, fontsize=10, xytext=(-3,3),
               textcoords='offset points', ha='right',va='bottom')    

    ax.grid()
    plt.show()

    return principalDf

from sklearn.cluster import KMeans
def performKMeans(X):
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(X)
    y_kmeans = kmeans.predict(X)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('Principal Component 1', fontsize = 15)
    ax.set_ylabel('Principal Component 2', fontsize = 15)
    ax.set_zlabel('Principal Component 3', fontsize = 15)
    ax.set_title('2 Cluster KMeans', fontsize = 20)

    xs = X['PC1']
    ys = X['PC2']
    zs = X['PC3']
    xyzn = zip(xs, ys, zs)
    print("Predictions:",y_kmeans)
    plt.scatter(xs, ys,zs, c=y_kmeans, cmap='tab10')

    centers = kmeans.cluster_centers_
    print(centers)
    #plt.scatter(x=centers[:, 0], y=centers[:, 1], zs=centers[:, 2], s = 20, c='red',  alpha=0.5)

    indices = X.index.values
    '''for j, xyz_ in enumerate(xyzn):
        #ax.annotate(index, (row['PC1'], row['PC2'], row['PC3']))
        annotate3D(ax, s=str(indices[j]), xyz=xyz_, fontsize=10, xytext=(-3,3),
               textcoords='offset points', ha='right',va='bottom')   
    '''
    ax.grid()
    plt.show() 

    return


from sklearn.cluster import SpectralClustering
def performSpectral(X, name):
    model = SpectralClustering(n_clusters=3, affinity='nearest_neighbors',
                           assign_labels='kmeans')
    labels = model.fit_predict(X)
    print("Spectral", labels)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('Principal Component 1', fontsize = 15)
    ax.set_ylabel('Principal Component 2', fontsize = 15)
    ax.set_zlabel('Principal Component 3', fontsize = 15)
    ax.set_title('3 Cluster Spectral', fontsize = 20)

    xs = X['PC1']
    ys = X['PC2']
    zs = X['PC3']
    xyzn = zip(xs, ys, zs)
    plt.scatter(xs, ys,zs, c=labels, cmap='tab10')

    df = pd.DataFrame(data = labels, index = X.index, columns = ['Label'])
    df.to_pickle(name) 

    ax.grid()
    plt.show() 

### CODE FOR ACTION ###
mornList, eveList = createAttributeList()

#PCA to 2 dimensions
# map { station # : [0 in-degree,1 out-degree,2 #bikes,3 long,4 lat, 5 trip-duration-in,6 trip-duration-out,7 avgAgeOut]}
#columns=['inDeg', 'outDeg', 'numBikes', 'long', 'lat', 'durIn', 'durOut', 'avgAge']
dfM = pd.DataFrame.from_dict(mornList, orient='index')
#print(dfM)
redM = performPCA(dfM)

dfE = pd.DataFrame.from_dict(eveList, orient='index')
redE = performPCA(dfE)

# k means clustering
performKMeans(redM)
performKMeans(redE)
#show results

performSpectral(redM, "cluterLabels-morning.pkl")
performSpectral(redE, "cluterLabels-evening.pkl")
#

