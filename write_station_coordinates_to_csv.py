import csv

from preprocess import get_station_coordinates


station_coordinates = get_station_coordinates()

f = open('station_coordinates.csv', 'w')
with f:
    fields = ['station_id', 'latitude', 'longitude']
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for id_, coords in station_coordinates.items():
        writer.writerow({'station_id': id_, 'latitude': coords[0], 'longitude': coords[1]})

