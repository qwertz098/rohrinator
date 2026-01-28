import cadquery as cq
from cadquery import exporters

# Nur S355J2H-Daten aus Tabelle
sleeve_data = [
    {"gewinde": "1/4\"", "d3": 30, "d1": 21, "d": 19, "L": 60,  "bestellnr": "HDM 01403002"},
    {"gewinde": "3/8\"", "d3": 30, "d1": 26.5, "d": 23, "L": 100, "bestellnr": "HDM 03803002"},
    {"gewinde": "1/2\"", "d3": 40, "d1": 33, "d": 27, "L": 150,  "bestellnr": "HDM 01204002"},
    {"gewinde": "3/4\"", "d3": 50, "d1": 42, "d": 33, "L": 200,  "bestellnr": "HDM 03405002"},
    {"gewinde": "1\"",    "d3": 50, "d1": 48, "d": 40, "L": 400,  "bestellnr": "HDM 10005002"},
    {"gewinde": "1 1/4\"", "d3": 55, "d1": 60, "d": 50, "L": 550,  "bestellnr": "HDM 11405502"},
    {"gewinde": "1 1/2\"", "d3": 70, "d1": 70, "d": 56, "L": 700,  "bestellnr": "HDM 11207002"},
    {"gewinde": "2\"",    "d3": 70, "d1": 76, "d": 69, "L": 900,  "bestellnr": "HDM 20007002"},
]

def create_sleeve(params):
    d3, d1, d, L = params['d3'], params['d1'], params['d'], params['L']
    outer_r = d3 / 2
    inner_end_r = d1 / 2
    inner_min_r = d / 2
    avg_wall = (d3 - d1) / 2  # Vollständig definiert!
    
    # Äußerer Körper
    body_outer = cq.Workplane("XY").cylinder(L, outer_r)
    
    # Innerer Hohlraum
    cyl_inner = cq.Workplane("XY").cylinder(L * 0.4, inner_min_r)
    cone_inner = cq.Solid.makeCone(inner_min_r, inner_end_r, L*0.6).translate((0,0,L*0.4))
    inner_void = cyl_inner.union(cone_inner)
    
    sleeve = body_outer.cut(inner_void)
    
    # Sichere Fasen (nur wenn Wand dick genug)
    if avg_wall > 1.5:
        try:
            sleeve = sleeve.faces("<Z").edges().chamfer(0.5, 45)
        except: pass
        try:
            sleeve = sleeve.faces(">Z").edges().chamfer(0.5, 15)
        except: pass
    
    # Sichere Rundung
    try:
        sleeve = sleeve.edges("|Z").fillet(0.5)
    except: pass
    
    return sleeve

# Generiere alle S355J2H-sleeven
for i, data in enumerate(sleeve_data):
    sleeve = create_sleeve(data)
    filename = f"Sleeve_{data['gewinde'].replace('/', '_')}_{data['bestellnr']}.step"
    exporters.export(sleeve, filename)
    #vol = sleeve.val().Volume * 7.85e-9  # Volumen in kg bei Stahl-Dichte 7.85 g/cm³
    print(f"Generiert {filename} [L={data['L']}mm]")

# Zeige Beispiel (1/4" in CQ-Viewer)
#show_object(create_sleeve(s355j2h_data[0]), name="sleeve_1-4in")
