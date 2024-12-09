from flask import Flask, request, jsonify
import sqlite3
import re

# Initialize Flask app
app = Flask(__name__)

# Path to the SQLite database
DB_PATH = "scripts.db"

# Function to search for a sentence in the scripts
def search_sentence(query):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Sanitize query to remove punctuation
    sanitized_query = re.sub(r'[^\w\s]', '', query)

    # Perform the search with FTS5 exact match
    results = cursor.execute(
        "SELECT title, content FROM scripts WHERE content MATCH ?",
        (sanitized_query,)
    ).fetchall()
    conn.close()

    # Process results
    results_list = []
    for title, content in results:
        # Find the exact match and extract context
        match_start = content.lower().find(sanitized_query.lower())
        if match_start != -1:
            context_length = 400
            start = max(0, match_start - context_length)
            end = min(len(content), match_start + len(sanitized_query) + context_length)
            snippet = content[start:end]

            # Highlight the match
            highlighted_snippet = re.sub(
                re.escape(sanitized_query),
                f"**{sanitized_query}**",
                snippet,
                flags=re.IGNORECASE
            )
            results_list.append({'title': title, 'match_snippet': highlighted_snippet})
    return results_list

# Define the API route for searching
@app.route('/search', methods=['GET'])
def search():
    # Get the query parameter
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    # Search for the sentence
    results = search_sentence(query)
    return jsonify(results)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
