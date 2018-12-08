import googlemaps

API_KEY = 'AIzaSyBLUuLuM2qPUJrbRNbdD1YLF2mdj-EFFYY'
gmaps = googlemaps.Client(key=API_KEY)

res = gmaps.distance_matrix((42.35044, -71.08945), (42.35083, -71.08981), mode='walking')
print(res)
