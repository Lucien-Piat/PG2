import json
from itertools import combinations
from collections import defaultdict

# Load articles
with open("pangenome_articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Build co-authorship network
edges = defaultdict(int)
nodes = {}  # Store author info (name -> affiliation)

for article in articles:
    authors = article.get("authors", [])
    
    # Add nodes with affiliation
    for author in authors:
        name = author.get("name", "")
        if name and name not in nodes:
            nodes[name] = author.get("affiliation", "")
    
    # Add edges between all pairs of co-authors
    author_names = [a.get("name", "") for a in authors if a.get("name")]
    for author1, author2 in combinations(author_names, 2):
        # Sort to ensure consistent edge keys
        edge = tuple(sorted([author1, author2]))
        edges[edge] += 1

print(f"Nodes (authors): {len(nodes)}")
print(f"Edges (collaborations): {len(edges)}")

# Save as GEXF (for Gephi)
with open("coauthorship_network.gexf", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<gexf xmlns="http://gexf.net/1.3" version="1.3">\n')
    f.write('  <graph mode="static" defaultedgetype="undirected">\n')
    
    # Nodes
    f.write('    <nodes>\n')
    for i, (name, affiliation) in enumerate(nodes.items()):
        # Escape XML special characters
        safe_name = name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        safe_affil = affiliation.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;') if affiliation else ""
        f.write(f'      <node id="{i}" label="{safe_name}" affiliation="{safe_affil}"/>\n')
    f.write('    </nodes>\n')
    
    # Create name to id mapping
    name_to_id = {name: i for i, name in enumerate(nodes.keys())}
    
    # Edges
    f.write('    <edges>\n')
    for i, ((author1, author2), weight) in enumerate(edges.items()):
        f.write(f'      <edge id="{i}" source="{name_to_id[author1]}" target="{name_to_id[author2]}" weight="{weight}"/>\n')
    f.write('    </edges>\n')
    
    f.write('  </graph>\n')
    f.write('</gexf>\n')

print("\nSaved to coauthorship_network.gexf")
print("Open with Gephi (https://gephi.org/)")