import osmium
import networkx as nx
import matplotlib.pyplot as plt
import mplcursors
from collections import defaultdict

# Pass 1: Collect node IDs used in named highway ways
class RoadWayHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.edges = []                             #All edges that are part of a highway way. [(nodeID1, nodeID2), (nodeID2, nodeID3)...]
        self.road_node_ids = set()                  #All node IDs that are part of a highway way
        self.node_to_way_names = defaultdict(set)   #K/V pair: K=NodeID  V=Way name(s) the node is a part of. Keep in mind, many ways can make up a whole street
        self.whole_street = defaultdict(list)       #K/V pair: K=Street name  V=All the edges that make up that street

    def way(self, w):
        if 'highway' in w.tags and 'name' in w.tags:
        # if 'name' in w.tags:
            name = w.tags['name']
            refs = [n.ref for n in w.nodes]
            self.road_node_ids.update(refs)
            for node_id in refs:
                self.node_to_way_names[node_id].add(name)
            for i in range(len(refs) - 1):
                self.edges.append((refs[i], refs[i+1]))
                self.whole_street[name].append((refs[i], refs[i+1]))



# Pass 2: Collect coordinates of relevant nodes
class RoadNodeHandler(osmium.SimpleHandler):
    def __init__(self, road_node_ids):
        super().__init__()
        self.road_node_ids = road_node_ids
        self.nodes = {}


    def node(self, n):
        if n.id in self.road_node_ids:
            self.nodes[n.id] = (n.location.lat, n.location.lon)


# Step 1: Collect road node IDs and edges
way_handler = RoadWayHandler()
way_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Springfield_eb1756d4-9f2c-458b-ad88-0ef32c477594.osm.pbf")
# way_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Central_US_Polygon_7ea12566-1eea-478a-8f3b-33dc53fad01e.osm.pbf", locations=True)
# way_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Ash_Grove_Bois_Darc_5aef2215-f332-4525-a5e2-aab28e7c8ae7.osm.pbf", locations=True)
# way_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Ash_Grove_f006e4cb-88e7-4a50-ae08-2e7a1ce319a8.osm.pbf", locations=True)
# way_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Ash_Grove_Everton_c67e9f90-41cf-49c7-8db7-92c6afe2f4be.osm.pbf", locations=True)

# Step 2: Collect only the matching node coordinates
node_handler = RoadNodeHandler(way_handler.road_node_ids)
node_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Springfield_eb1756d4-9f2c-458b-ad88-0ef32c477594.osm.pbf")
# node_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Central_US_Polygon_7ea12566-1eea-478a-8f3b-33dc53fad01e.osm.pbf", locations=True)
# node_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Ash_Grove_Bois_Darc_5aef2215-f332-4525-a5e2-aab28e7c8ae7.osm.pbf", locations=True)
# node_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Ash_Grove_f006e4cb-88e7-4a50-ae08-2e7a1ce319a8.osm.pbf", locations=True)
# node_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Ash_Grove_Everton_c67e9f90-41cf-49c7-8db7-92c6afe2f4be.osm.pbf", locations=True)

# Step 3: Build the graph
G = nx.Graph()
for node_id, (lat, lon) in node_handler.nodes.items():
    G.add_node(node_id, pos=(lon, lat), lat=lat, lon=lon)

for u, v in way_handler.edges:
    if u in node_handler.nodes and v in node_handler.nodes:
        G.add_edge(u, v)

print(f"Nodes: {len(G.nodes)}")
print(f"Edges: {len(G.edges)}")

# Step 4: Identify intersections (degree >= 3)
intersection_nodes = [n for n in G.nodes if G.degree[n] >= 3]

# Step 5: Visualize
if not G.nodes:
    print("No valid road nodes found.")
else:
    pos = nx.get_node_attributes(G, 'pos')

    fig, ax = plt.subplots(figsize=(10, 10))
    
    nx.draw(G, pos, node_size=0.25, edge_color='gray', ax=ax)

    # Draw red intersection nodes
    intersection_pos = [pos[n] for n in intersection_nodes]
    sc = ax.scatter(
        [x for x, y in intersection_pos],
        [y for x, y in intersection_pos],
        c='red', s=5, label="Intersections"
    )

    # Build tooltip data
    node_index_map = {i: node_id for i, node_id in enumerate(intersection_nodes)}

    cursor = mplcursors.cursor(sc, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        node_id = node_index_map[sel.index]
        lat = G.nodes[node_id]['lat']
        lon = G.nodes[node_id]['lon']
        street_names = way_handler.node_to_way_names.get(node_id, [])
        name_text = "\n".join(street_names) if street_names else "Unnamed roads"
        sel.annotation.set_text(
            # f"Lat: {lat:.6f}\nLon: {lon:.6f}\n{ name_text }"
            f"{node_id}\n{name_text}"
        )

    plt.title("Road Graph with Intersection Names and Coordinates (Hover Red Dots)")
    plt.axis("off")

    # Optional fullscreen or resize
    manager = plt.get_current_fig_manager()
    manager.resize(1250, 550)
    try:
        manager.window.wm_geometry("+100+0")
    except AttributeError:
        pass  # Some backends may not support this

    #debug
    for street in way_handler.whole_street:
        if street == "West University Street":
            print(street, len(way_handler.whole_street[street]))
    
    plt.show()