@app.route('/search')
def search_books():
    search_term = request.args.get('q', '')
    conn = get_db_connection()
    
    # Another vulnerable query - user input concatenated directly
    query = f"SELECT * FROM books WHERE title LIKE '%{search_term}%' OR author LIKE '%{search_term}%'"
    results = conn.execute(query).fetchall()
    conn.close()
    
    return render_template('search_results.html', results=results, query=search_term)