import math

import pandas as pd
import googlemaps

from api_key import API_KEY

gmaps = googlemaps.Client(key=API_KEY)


time = gmaps.distance_matrix(
            start_ls,
            end_ls,
            mode='driving',
            traffic_model='optimistic',
            departure_time=1544000018,
        )

# load in the data points 

all_times = {}
for route in [(64, 190), (39, 22), (189, 190), (67, 74), (22, 190), (80, 78), (39, 46), (133, 124),
              (4, 22), (80, 190)]:
    start, end = route
    start_points = pd.read_csv(f'sample_points/r{start}.csv', header=0)
    end_points = pd.read_csv(f'sample_points/r{end}.csv', header=0)
    num_points = start_points.shape[0]
    num_splits = math.ceil(num_points/100)
    print(num_points)
    print(num_splits)
    times = []
    for j in range(num_splits):
        start_ls = []
        end_ls = []
        for i in range(100):
            start_ls.append((start_points['x'][100*j+i],start_points['y'][100*j+i]))
            end_ls.append((end_points['x'][100*j+i], end_points['y'][100*j+i]))

        time = gmaps.distance_matrix(
            start_ls,
            end_ls,
            mode='driving',
            traffic_model='optimistic',
            departure_time=1544000018,
        )
        times.append(time)
        break

    all_times[route] = times

    

