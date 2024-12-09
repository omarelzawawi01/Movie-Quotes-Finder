# def search_script(query):
#     with ix.searcher() as searcher:
#         query_parser = QueryParser("content", ix.schema)
#         parsed_query = query_parser.parse(query)

#         # Run the search
#         results = searcher.search(parsed_query, terms=True, limit=10)  # Set limit for top results
#         results_list = []

#         for result in results:
#             title = result['title']
#             content = result['content']
            
#             # Highlight matches
#             highlighted_content = result.highlights("content")
#             results_list.append({
#                 'title': title,
#                 'match_snippet': highlighted_content
#             })
            
#         return results_list

# # Example search
# search_query = "I'll be back"
# matches = search_script(search_query)
# for match in matches:
#     print(f"Title: {match['title']}")
#     print(f"Snippet with Match: {match['match_snippet']}\n")
import sqlite3
import os
import re

# Set up SQLite database
DB_PATH = "scripts.db"

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create FTS5 table for storing scripts
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS scripts USING fts5(
            title,
            content
        )
    ''')
    conn.commit()
    return conn

# Insert a script into the database
def insert_script(conn, title, content):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO scripts (title, content) VALUES (?, ?)', (title, content))
    conn.commit()

# Load all scripts from directory and insert into database
def load_scripts_to_db(script_dir):
    conn = setup_database()
    for filename in os.listdir(script_dir):
        if filename.endswith('.txt'):
            title = filename.replace('.txt', '')
            with open(os.path.join(script_dir, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                content = re.sub(r'[^\w\s]', '', content)  # Remove punctuation for consistent matching
                insert_script(conn, title, content)
    conn.close()

# Load scripts once into SQLite
load_scripts_to_db('movie_scripts')

