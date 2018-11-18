import os
import numpy as np
import matplotlib.pyplot as plt
from dateutil import parser
from multiprocessing import Pool
from functools import partial

def _get_path(year, month):
    clean_month = (str(month) if len(str(month)) == 2 else (f'0{month}'))
    return f"data/{str(year)}{clean_month}-bluebikes-tripdata.csv"
    
def preprocess(year, month):
    '''
    Return a numpy array of the data in the csv file specified
    '''
    path = _get_path(year, month)
    try:  
        fo = open(path, "r")
        lines = fo.readlines()
        dataset = [np.array([i.strip("\"").strip('\n') for i in line.split(",")]) for line in lines[1:]]
        return np.vstack(dataset)
    except:
       print(f"Filepath: {path} for year: {year} and month: {month} not found in data folder.")

def get_headers(year, month):
    fo = open(_get_path(year, month), "r")
    return [header.strip("\"").replace(" ", "").strip("\n") for header in fo.readlines()[0].split(",")]

def _in_range(time, interval):
    return 1 if (parser.parse(time).hour <= interval[1] and parser.parse(time).hour >= interval[0]) else 0

def _narrow_dataset_by_time(dataset, interval):
    p = Pool(8)
    filtered = p.map(partial(_in_range, interval=interval), [i for i in dataset[:,index_map['starttime']]])
    return dataset[np.array(filtered)==1]
    
def plot_station_use_heat_map(dataset, interval=(0,24), start=True):
    '''
    Plots a heatmap of number of trips starting or ending at a given hubway station by latitude and longitude
    
    Args:
      * interval [tuple(int)]: what hour range to plot (start_hour, end_hour), note this is **inclusive**
      * dataset [np array]: dataset to use in the analysis
      * start [boolean]: plots the stations associated with the start or end of the trip.
                         true for start station false for end station
    '''
    dataset = _narrow_dataset_by_time(dataset.copy(), interval)
    coord = 'startstationid' if start else 'endstationid'
    unique, count = np.unique(dataset[:,index_map[coord]], return_counts=True)
    lat = [station_coordinates[int(i)][0] for i in unique]
    long = [station_coordinates[int(i)][1] for i in unique]
    
    # Plot...
    plt.scatter(long, lat, c=count, s=2, cmap='rainbow')
    buffer = .02
    # adjust axis because of 0 (null) values in lat / long
    plt.ylim((min([i for i in lat if i > 0])-buffer, max(lat)+buffer))
    plt.xlim((min(long)-buffer, max([i for i in long if i < 0])+buffer))
    plt.colorbar()
    plt.show()

def get_full_year():
    '''
    Get data for the full year, note this is not sorted and is constructed with rows in random order
    '''
    y2018 = {i+1: preprocess(2018, i+1) for i in range(9)}
    y2017 = {i: preprocess(2017, i) for i in range(10,13)}
    return np.vstack([month for month in {**y2017, **y2018}.values()])

def get_station_coordinates():
    '''
    Maps station ids to their respective latitudes and longitudes
    '''
    return {
        int(row[index_map['endstationid']]):
        (float(row[index_map['endstationlatitude']]), float(row[index_map['endstationlongitude']]))
        for row in get_full_year()
    }
