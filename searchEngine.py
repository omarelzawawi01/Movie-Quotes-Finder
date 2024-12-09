'''
import os
import re
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh.analysis import RegexTokenizer, LowercaseFilter

# Directory for Whoosh index
INDEX_DIR = "script_index"

# Define schema and analyzer for punctuation removal and lowercase matching
custom_analyzer = RegexTokenizer(r"\w+") | LowercaseFilter()
schema = Schema(title=ID(stored=True), content=TEXT(stored=True, analyzer=custom_analyzer))

# Set up the Whoosh index
def setup_index():
    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)
        ix = index.create_in(INDEX_DIR, schema)
    else:
        ix = index.open_dir(INDEX_DIR)
    return ix

# Clean and index scripts (strips punctuation and special characters)
def clean_text(text):
    return re.sub(r'[^\w\s]', '', text)  # Removes punctuation

def index_scripts(script_dir, ix):
    with ix.searcher() as searcher:
        if searcher.doc_count() == 0:
            writer = ix.writer()
            for filename in os.listdir(script_dir):
                if filename.endswith('.txt'):
                    title = filename.replace('.txt', '')
                    with open(os.path.join(script_dir, filename), 'r', encoding='utf-8') as f:
                        content = f.read()
                        cleaned_content = clean_text(content)  # Remove punctuation from content
                        writer.add_document(title=title, content=cleaned_content)
                        print(f"Indexed: {title}")
            writer.commit()
            print("Indexing completed.")
        else:
            print("Index already exists. Skipping indexing.")

# Setup index and only index if necessary
ix = setup_index()
index_scripts('movie_scripts', ix)

# Function to sanitize the query for punctuation removal
def sanitize_query(query):
    return re.sub(r'[^\w\s]', '', query)

# Function to extract context and highlight the matched phrase
def highlight_and_context(content, phrase, context_length=400):
    # Locate the phrase (case insensitive)
    match_start = content.lower().find(phrase.lower())
    if match_start == -1:
        return "Exact phrase match not found in content."

    # Define the context window around the match
    start = max(0, match_start - context_length)
    end = min(len(content), match_start + len(phrase) + context_length)
    snippet = content[start:end]

    # Use re.sub() for case-insensitive replacement to highlight the phrase
    highlighted_snippet = re.sub(re.escape(phrase), f"**{phrase}**", snippet, flags=re.IGNORECASE)
    return highlighted_snippet

# Search function with keyword-based search and post-filtering
def search_script(query, ix):
    sanitized_query = sanitize_query(query)
    with ix.searcher() as searcher:
        # Use a broad keyword search initially
        query_parser = QueryParser("content", ix.schema)
        parsed_query = query_parser.parse(sanitized_query)

        # Run the search
        results = searcher.search(parsed_query, terms=True, limit=50)
        results_list = []

        for result in results:
            title = result['title']
            content = result['content']

            # Post-filtering to check for the exact phrase in the original file content
            with open(os.path.join("movie_scripts", f"{title}.txt"), "r", encoding="utf-8") as f:
                original_content = f.read()
                original_content_cleaned = clean_text(original_content)

                if sanitized_query.lower() in original_content_cleaned.lower():
                    # Highlight the exact phrase in context
                    match_snippet = highlight_and_context(original_content, query)
                    results_list.append({
                        'title': title,
                        'match_snippet': match_snippet
                    })
            
        return results_list

# Example search
search_query = "You can't handle the truth"
print("Searching for:", search_query)
print("-" * 50)
matches = search_script(search_query, ix)
print(f"Found {len(matches)} matches:")
for match in matches:
    print(f"Title: {match['title']}")
    print(f"Snippet with Match: \n{match['match_snippet']}\n")
    print("-" * 50)
'''
import sqlite3
import os
import re
DB_PATH = "scripts.db"
def search_sentence(query):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Sanitize query to remove punctuation for consistent matching
    sanitized_query = re.sub(r'[^\w\s]', '', query)
    
    # Perform the search with FTS5 exact match
    results = cursor.execute("SELECT title, content FROM scripts WHERE content MATCH ?", (sanitized_query,)).fetchall()
    results_list = []

    for title, content in results:
        # Find the exact match and extract context
        match_start = content.lower().find(sanitized_query.lower())
        if match_start != -1:
            context_length = 400
            start = max(0, match_start - context_length)
            end = min(len(content), match_start + len(sanitized_query) + context_length)
            snippet = content[start:end]
            
            # Use re.sub() for case-insensitive replacement to highlight the phrase
            highlighted_snippet = re.sub(re.escape(sanitized_query), f"**{sanitized_query}**", snippet, flags=re.IGNORECASE)
            results_list.append({'title': title, 'match_snippet': highlighted_snippet})
    
    conn.close()
    return results_list

# Example search
search_query = "we're running out of time"
print("Searching for:", search_query)
print("-" * 50)
matches = search_sentence(search_query)
print(f"Found {len(matches)} matches:")
for match in matches:
    print(f"Title: {match['title']}")
    print(f"Snippet with Match: \n{match['match_snippet']}\n")
    print("-" * 50)
