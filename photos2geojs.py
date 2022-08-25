# @author: jmacura 2019
# with a huge help of: https://developer.here.com/blog/getting-started-with-geocoding-exif-image-metadata-in-python3

from geojson import Point, Feature, FeatureCollection
from geojson import dumps as geodumps
from glob import glob
from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS
#from pprint import pprint #for dev purposes only

# source: https://developer.here.com/blog/getting-started-with-geocoding-exif-image-metadata-in-python3
def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()

# source: https://developer.here.com/blog/getting-started-with-geocoding-exif-image-metadata-in-python3
#def get_labeled_exif(exif):
#    labeled = {}
#    for (key, val) in exif.items():
#        labeled[TAGS.get(key)] = val
#    return labeled

# source: https://developer.here.com/blog/getting-started-with-geocoding-exif-image-metadata-in-python3
def get_geotagging(exif):
    if not exif:
        raise ValueError("No EXIF metadata found")
    geotagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                raise ValueError("No EXIF geotagging found")
            for (key, val) in GPSTAGS.items():
                if key in exif[idx]:
                    geotagging[val] = exif[idx][key]
    return geotagging

# source: https://developer.here.com/blog/getting-started-with-geocoding-exif-image-metadata-in-python3
def get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0
    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds
    return round(degrees + minutes + seconds, 6)

# source: https://developer.here.com/blog/getting-started-with-geocoding-exif-image-metadata-in-python3
def get_coordinates(geotags):
    lat = get_decimal_from_dms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])
    lon = get_decimal_from_dms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])
    return (lon, lat) #intentionally GeoJSON swapped order

def make_geojs_feature(coords, filename):
    prop = {"id": filename.split(".")[0]}
    return Feature(geometry = Point(coords), properties = prop)

features = []
for filename in glob('*.jpg'):
    if not filename.endswith('(2).jpg'):
        exif = get_exif(filename)
        geotags = get_geotagging(exif)
        coords = get_coordinates(geotags)
        feature = make_geojs_feature(coords, filename)
        features.append(feature)
        #pprint(feature)
        #print()

all_points = FeatureCollection(features)
#pprint(all_points)
with open("photos.geojson", 'w', encoding='utf-8') as out:
    out.write(geodumps(all_points))
