from Bio import Entrez
import json
import time

Entrez.email = "lucienpiat33@gmail.com"

# Search for pangenome articles
search_handle = Entrez.esearch(db="pubmed", term="pangenome[Title/Abstract]", retmax=10000)
search_results = Entrez.read(search_handle)
id_list = search_results["IdList"]
print(f"Found {len(id_list)} articles")

# Fetch details for each article
articles = []
batch_size = 200
for start in range(0, len(id_list), batch_size):
    batch = id_list[start:start + batch_size]
    print(f"Fetching {start + 1} to {min(start + batch_size, len(id_list))}...")
    fetch_handle = Entrez.efetch(db="pubmed", id=batch, rettype="xml", retmode="xml")
    records = Entrez.read(fetch_handle)
    fetch_handle.close()
    
    for record in records["PubmedArticle"]:
        try:
            article_info = record["MedlineCitation"]["Article"]
            
            # Title
            title = str(article_info.get("ArticleTitle", ""))
            
            # Authors with affiliations
            authors_list = []
            for author in article_info.get("AuthorList", []):
                last_name = author.get("LastName", "")
                fore_name = author.get("ForeName", "")
                
                if last_name or fore_name:
                    author_entry = {
                        "name": f"{last_name}, {fore_name}".strip(", ")
                    }
                    
                    # Extract affiliation
                    affiliations = author.get("AffiliationInfo", [])
                    if affiliations:
                        author_entry["affiliation"] = affiliations[0].get("Affiliation", "")
                    
                    authors_list.append(author_entry)
            
            articles.append({
                "title": title,
                "authors": authors_list
            })
        
        except Exception as e:
            print(f"Error processing record: {e}")
    
    time.sleep(0.34)

# Save to JSON
with open("data/pangenome_articles.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(articles)} articles to pangenome_articles.json")