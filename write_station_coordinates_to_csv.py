import csv

from preprocess import get_station_coordinates


station_coordinates = get_station_coordinates()

f = open('station_coordinates.csv', 'w')
with f:
    fields = ['station_id', 'longitude','latitude']
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for id_, coords in station_coordinates.items():
        if coords[0] > 0:
            writer.writerow({
                'station_id': id_,
                'longitude': coords[1],
                'latitude': coords[0], 
            })

