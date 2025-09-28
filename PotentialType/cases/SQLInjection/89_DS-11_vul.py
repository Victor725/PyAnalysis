@app.route('/books/search', methods=['GET'])
def search_books():
    search_term = request.args.get('query')
    if not search_term:
        return jsonify({"error": "Query parameter required"}), 400
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Vulnerable SQL injection point
    query = f"SELECT * FROM books WHERE title LIKE '%{search_term}%' OR author LIKE '%{search_term}%'"
    c.execute(query)
    
    books = []
    for row in c.fetchall():
        books.append({
            'id': row[0],
            'title': row[1],
            'author': row[2],
            'genre': row[3],
            'price': row[4]
        })
    
    conn.close()
    return jsonify(books)