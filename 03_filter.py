import json
import csv
from itertools import combinations
from collections import defaultdict

# Parameters
THRESHOLD = 2  # Keep only edges with weight >= THRESHOLD
INPUT_FILE = "data/pangenome_articles.json"

# Load articles
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    articles = json.load(f)

# Build co-authorship network
edges = defaultdict(int)
all_nodes = {}

for article in articles:
    authors = article.get("authors", [])
    
    for author in authors:
        name = author.get("name", "")
        if name and name not in all_nodes:
            all_nodes[name] = author.get("affiliation", "")
    
    author_names = [a.get("name", "") for a in authors if a.get("name")]
    for author1, author2 in combinations(author_names, 2):
        edge = tuple(sorted([author1, author2]))
        edges[edge] += 1

# Filter edges by threshold
filtered_edges = {edge: weight for edge, weight in edges.items() if weight >= THRESHOLD}

# Keep only nodes that have at least one edge
connected_authors = set()
for author1, author2 in filtered_edges.keys():
    connected_authors.add(author1)
    connected_authors.add(author2)

filtered_nodes = {name: affil for name, affil in all_nodes.items() if name in connected_authors}

print(f"Original: {len(all_nodes)} nodes, {len(edges)} edges")
print(f"Filtered (weight >= {THRESHOLD}): {len(filtered_nodes)} nodes, {len(filtered_edges)} edges")

# --- Save CYTOSCAPE CSV ---
with open("data/filtered_edges.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["source", "target", "weight"])
    for (author1, author2), weight in filtered_edges.items():
        writer.writerow([author1, author2, weight])

with open("data/filtered_nodes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "affiliation"])
    for name, affiliation in filtered_nodes.items():
        writer.writerow([name, affiliation])

# --- Save GEPHI GEXF ---
def escape_xml(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;') if s else ""

name_to_id = {name: i for i, name in enumerate(filtered_nodes.keys())}

with open("data/filtered_network.gexf", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<gexf xmlns="http://gexf.net/1.3" version="1.3">\n')
    f.write('  <graph mode="static" defaultedgetype="undirected">\n')
    
    f.write('    <nodes>\n')
    for name in filtered_nodes:
        f.write(f'      <node id="{name_to_id[name]}" label="{escape_xml(name)}"/>\n')
    f.write('    </nodes>\n')
    
    f.write('    <edges>\n')
    for i, ((a1, a2), weight) in enumerate(filtered_edges.items()):
        f.write(f'      <edge id="{i}" source="{name_to_id[a1]}" target="{name_to_id[a2]}" weight="{weight}"/>\n')
    f.write('    </edges>\n')
    
    f.write('  </graph>\n')
    f.write('</gexf>\n')

print(f"\nSaved: filtered_edges.csv, filtered_nodes.csv, filtered_network.gexf")