import osmium
import networkx as nx
import matplotlib.pyplot as plt

# Pass 1: Collect node IDs used in highway ways
class RoadWayHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.road_node_ids = set()
        self.edges = []

    def way(self, w):
        if 'highway' in w.tags:
            refs = [n.ref for n in w.nodes]
            self.road_node_ids.update(refs)
            for i in range(len(refs) - 1):
                self.edges.append((refs[i], refs[i+1]))

# Pass 2: Collect only the relevant node coordinates
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
# way_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Central_US_Polygon_7ea12566-1eea-478a-8f3b-33dc53fad01e.osm.pbf", locations=True)
way_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Ash_Grove_Bois_Darc_5aef2215-f332-4525-a5e2-aab28e7c8ae7.osm.pbf", locations=True)
# way_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Ash_Grove_f006e4cb-88e7-4a50-ae08-2e7a1ce319a8.osm.pbf", locations=True)

# Step 2: Collect only the matching node coordinates
node_handler = RoadNodeHandler(way_handler.road_node_ids)
# way_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Central_US_Polygon_7ea12566-1eea-478a-8f3b-33dc53fad01e.osm.pbf", locations=True)
node_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Ash_Grove_Bois_Darc_5aef2215-f332-4525-a5e2-aab28e7c8ae7.osm.pbf", locations=True)
# node_handler.apply_file("D:\Iron-Butt\OpenStreetMap_Datasets_And_Images\Ash_Grove_f006e4cb-88e7-4a50-ae08-2e7a1ce319a8.osm.pbf", locations=True)

# Step 3: Build the graph
ctr = 0
G = nx.Graph()


nodeCtr = 0
# Add Nodes
for node_id, (lat, lon) in node_handler.nodes.items():
    nodeCtr += 1
    G.add_node(node_id, pos=(lon, lat))

wayCtr = 0
# Add ways
for u, v in way_handler.edges:
    wayCtr += 1
    if u in node_handler.nodes and v in node_handler.nodes:
        G.add_edge(u, v)

# Print graph stats
print(f"Nodes: {len(G.nodes)}")
print(f"Node Ctr: {nodeCtr}")
print(f"Edges: {len(G.edges)}")
print(f"Edges Ctr: {wayCtr}")


# Step 4: Visualize
if len(G.nodes) == 0:
    print("No valid road nodes found.")
else:
    pos = nx.get_node_attributes(G, 'pos')
    plt.figure(figsize=(10, 10))
    nx.draw(G, pos, node_size=1, edge_color='gray')
    plt.title("Road Graph from OSM")
    plt.axis("off")
    plt.show()