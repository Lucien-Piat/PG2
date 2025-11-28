import json
import csv
from itertools import combinations
from collections import defaultdict

# Load articles
with open("data/pangenome_articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Build co-authorship network
edges = defaultdict(int)
nodes = {}

for article in articles:
    authors = article.get("authors", [])
    
    for author in authors:
        name = author.get("name", "")
        if name and name not in nodes:
            nodes[name] = author.get("affiliation", "")
    
    author_names = [a.get("name", "") for a in authors if a.get("name")]
    for author1, author2 in combinations(author_names, 2):
        edge = tuple(sorted([author1, author2]))
        edges[edge] += 1

print(f"Nodes: {len(nodes)}")
print(f"Edges: {len(edges)}")

# --- CYTOSCAPE: CSV files ---
with open("data/cytoscape_edges.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(["source", "target", "weight"])
    for (author1, author2), weight in edges.items():
        writer.writerow([author1, author2, weight])

with open("data/cytoscape_nodes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(["id", "affiliation"])
    for name, affiliation in nodes.items():
        writer.writerow([name, affiliation])

print("Cytoscape: cytoscape_edges.csv + cytoscape_nodes.csv")

# --- GEPHI: GEXF file ---
def escape_xml(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;') if s else ""

name_to_id = {name: i for i, name in enumerate(nodes.keys())}

with open("data/gephi_network.gexf", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<gexf xmlns="http://gexf.net/1.3" version="1.3">\n')
    f.write('  <graph mode="static" defaultedgetype="undirected">\n')
    
    f.write('    <nodes>\n')
    for name, affiliation in nodes.items():
        f.write(f'      <node id="{name_to_id[name]}" label="{escape_xml(name)}"/>\n')
    f.write('    </nodes>\n')
    
    f.write('    <edges>\n')
    for i, ((a1, a2), weight) in enumerate(edges.items()):
        f.write(f'      <edge id="{i}" source="{name_to_id[a1]}" target="{name_to_id[a2]}" weight="{weight}"/>\n')
    f.write('    </edges>\n')
    
    f.write('  </graph>\n')
    f.write('</gexf>\n')

print("Gephi: gephi_network.gexf")