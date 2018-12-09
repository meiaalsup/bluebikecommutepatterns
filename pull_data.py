import math

import pandas as pd
import googlemaps
import json
import csv

from api_key import API_KEY

gmaps = googlemaps.Client(key=API_KEY)


routes = [
    (64, 190),
    (39, 22), (189, 190), (67, 74), (22, 190), (80, 78), (39, 46), (133, 124), (4, 22),
    (80, 190)]
num_to_sample = 3

def sample(mode='driving'):
    full_output = {}
    all_times = {}
    for route in routes:
        start, end = route
        start_points = pd.read_csv(f'sample_points/r{start}.csv', header=0)[:200]
        end_points = pd.read_csv(f'sample_points/r{end}.csv', header=0)[:200]
        num_to_sample = start_points.shape[0]
        times = []
        output = []
        for i in range(num_to_sample):
            time = gmaps.distance_matrix(
                (start_points['y'][i],start_points['x'][i]),
                (end_points['y'][i], end_points['x'][i]),
                mode=mode,
                #traffic_model='optimistic',
            )
            if 'duration' in time['rows'][0]['elements'][0]:
                times.append(time['rows'][0]['elements'][0]['duration']['value'])
            else:
                times.append(0)
            output.append(time)
     
        all_times[route] = times
        full_output[str(route)] = output
    writer = csv.DictWriter(
        open(f'{mode}_times.csv', 'w'),
        fieldnames=[str(r) for r in routes]
    )  
    writer.writeheader()

    for j in range(num_to_sample):
        row = {str(r): all_times[r][j] for r in routes}
        writer.writerow(row)
    json.dump(full_output, open(f'{mode}_routes_full_output', 'w'))

sample('driving')
sample('transit')
