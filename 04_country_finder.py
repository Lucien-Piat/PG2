import csv
import sys
import re

# Check for pycountry
try:
    import pycountry
except ImportError:
    print("Error: pycountry not installed. Run: sudo apt-get install python3-pycountry")
    sys.exit(1)

INPUT_FILE = "data/filtered_nodes.csv"
OUTPUT_FILE = "data/author_countries.csv"

# Enhanced Country Mapping
COUNTRY_MAPPING = {
    "USA": "United States", "US": "United States", "United States of America": "United States",
    "UK": "United Kingdom", "U.K.": "United Kingdom", "Great Britain": "United Kingdom",
    "Korea": "South Korea", "Republic of Korea": "South Korea", 
    "China": "China", "P.R. China": "China",
    "Russia": "Russian Federation", 
    "Vietnam": "Viet Nam", 
    "Brasil": "Brazil", 
    "Deutschland": "Germany", 
    "Italia": "Italy", 
    "España": "Spain",
    "Netherlands": "Netherlands", "The Netherlands": "Netherlands",
    "Malaysia": "Malaysia",
    "New Zealand": "New Zealand",
    "Australia": "Australia"
}

def clean_affiliation(text):
    """Removes emails and extra whitespace."""
    if not text: return ""
    # Remove emails (e.g. user@domain.com)
    text = re.sub(r'\S*@\S*\s?', '', text)
    # Replace newlines and tabs with space
    text = text.replace('\n', ' ').replace('\r', '').replace('\t', ' ')
    return text.strip()

def get_country(text):
    clean_text = clean_affiliation(text)
    if not clean_text: return "Unknown"
    
    # 1. Keyword Scan (Most reliable for messy strings)
    # We check the END of the string first by reversing the text chunks
    parts = [p.strip(" .,;") for p in clean_text.split(",")]
    
    if parts:
        last_part = parts[-1]
        # specific check for USA/UK at end
        if last_part.upper() in ["USA", "US", "UK", "U.K."]:
            return COUNTRY_MAPPING[last_part.upper().replace(".", "")]
        
        try:
            found = pycountry.countries.search_fuzzy(last_part)
            if found: return found[0].name
        except: pass

    # 2. Full Text Scan for Keywords
    for key, val in COUNTRY_MAPPING.items():
        # exact word match to avoid "USA" matching inside "Jerusalem"
        if re.search(r'\b' + re.escape(key) + r'\b', clean_text, re.IGNORECASE):
            return val

    # 3. Pycountry Scan
    try:
        for country in pycountry.countries:
            if country.name in clean_text:
                return country.name
    except: pass

    return "Unknown"

def parse_custom_format(filename):
    """
    Parses the specific format: Name;Affiliation
    Handles multiline entries where lines without ';' belong to previous entry.
    """
    entries = {} # Name -> Affiliation
    current_name = None
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Check if line looks like "Name;Affiliation"
        if ';' in line:
            # It's a new entry
            parts = line.split(';', 1) # Split on first semicolon only
            name = parts[0].strip()
            aff = parts[1].strip()
            
            entries[name] = aff
            current_name = name
        else:
            # It's likely a continuation of the previous affiliation (broken line)
            if current_name:
                entries[current_name] += " " + line
                
    return entries

def main():
    print(f"Reading {INPUT_FILE}...")
    
    # 1. Parse the messy file
    author_data = parse_custom_format(INPUT_FILE)
    
    print(f"Found {len(author_data)} authors. Extracting countries...")
    
    # 2. Extract Countries
    rows_out = []
    for name, aff in author_data.items():
        country = get_country(aff)
        rows_out.append([name, country])
        
    # 3. Write CSV
    print(f"Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["id", "country"])
        writer.writerows(rows_out)
        
    # Stats
    unknowns = sum(1 for r in rows_out if r[1] == "Unknown")
    print(f"Done. {len(rows_out)} authors processed. {unknowns} are Unknown (no affiliation or failed detection).")

if __name__ == "__main__":
    main()
