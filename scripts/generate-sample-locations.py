"""Generate illustrative path-side positions, not surveyed bench locations.
Run from the repository root. IDs and adoption records remain stable.
"""
import json
import math
from pathlib import Path

# Multiple winding routes cover the park instead of six circular point clouds.
# Coordinates are (latitude, longitude); these are illustrative walking corridors.
routes = [
    [(40.8854,-73.8982),(40.8873,-73.8986),(40.8895,-73.8988),(40.8918,-73.8984),(40.8942,-73.8977),(40.8970,-73.8966),(40.8974,-73.8949),(40.8949,-73.8947),(40.8925,-73.8951),(40.8900,-73.8958),(40.8877,-73.8960)],
    [(40.8846,-73.8964),(40.8848,-73.8946),(40.8855,-73.8927),(40.8866,-73.8910),(40.8883,-73.8901),(40.8895,-73.8894),(40.8909,-73.8889),(40.8928,-73.8893),(40.8948,-73.8891),(40.8965,-73.8880),(40.8978,-73.8875)],
    [(40.8844,-73.9000),(40.8862,-73.8998),(40.8884,-73.8998),(40.8908,-73.8997),(40.8931,-73.8992),(40.8955,-73.8988),(40.8980,-73.8980),(40.9000,-73.8972),(40.9016,-73.8961),(40.9030,-73.8949)],
    [(40.8900,-73.8847),(40.8924,-73.8849),(40.8950,-73.8851),(40.8975,-73.8849),(40.9000,-73.8844),(40.9024,-73.8843),(40.9048,-73.8847),(40.9072,-73.8845),(40.9094,-73.8838)],
    [(40.8989,-73.8949),(40.9005,-73.8938),(40.9021,-73.8942),(40.9040,-73.8958),(40.9057,-73.8974),(40.9074,-73.8971),(40.9090,-73.8954),(40.9097,-73.8927),(40.9086,-73.8906),(40.9068,-73.8891),(40.9055,-73.8874),(40.9034,-73.8873),(40.9015,-73.8889),(40.9000,-73.8912)],
    [(40.8909,-73.8805),(40.8930,-73.8792),(40.8950,-73.8780),(40.8969,-73.8779),(40.8988,-73.8770),(40.9006,-73.8774),(40.9025,-73.8781),(40.9043,-73.8779),(40.9062,-73.8788),(40.9081,-73.8795),(40.9093,-73.8811)],
]
locations = []
for i in range(524):
    zone = i % 6
    route = routes[zone]
    lengths = [math.hypot((b[0]-a[0])*111320,(b[1]-a[1])*84100) for a,b in zip(route,route[1:])]
    count = len(range(zone,524,6))
    # Even distance spacing with small deterministic variation, and a few metres
    # of side offset; no circular clusters and no random changes on reload.
    fraction = (i//6 + .5 + .16*math.sin(i*7.13))/count
    distance = fraction*sum(lengths)
    for a,b,length in zip(route,route[1:],lengths):
        if distance <= length:
            t = distance/length
            offset = 4*math.sin(i*2.39996)
            lat = a[0]+(b[0]-a[0])*t + offset/111320*((b[1]-a[1])*84100/length)
            lng = a[1]+(b[1]-a[1])*t - offset/84100*((b[0]-a[0])*111320/length)
            locations.append({'id':i+1,'lat':round(lat,7),'lng':round(lng,7)})
            break
        distance -= length
assert len(locations)==524
Path('src/sample-locations.json').write_text(json.dumps(locations,indent=2)+'\n')
values=',\n'.join(f"({b['id']},{b['lat']},{b['lng']})" for b in locations)
Path('supabase/update-sample-locations.sql').write_text('-- Only updates coordinates of the existing sample inventory; preserves adoptions.\nupdate public.benches b set lat=v.lat, lng=v.lng\nfrom (values\n'+values+'\n) as v(id,lat,lng) where b.id=v.id;\n')
p=Path('supabase/demo-seed.sql')
existing=p.read_text()
adoptions=existing[existing.index('insert into public.adoptions'):]
p.write_text("-- OPTIONAL: illustrative sample locations, not an official bench inventory.\ninsert into public.benches(id,area,lat,lng)\nselect id, (array['Parade Ground','Van Cortlandt Lake','Southwest Playground','Old Croton Aqueduct','North Woods','Allen Shandler Recreation Area'])[(id-1)%6+1], lat,lng\nfrom (values\n"+values+'\n) as v(id,lat,lng);\n'+adoptions)
