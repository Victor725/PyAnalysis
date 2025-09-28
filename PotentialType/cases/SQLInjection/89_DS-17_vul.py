@app.route('/products/search', method='GET')
def search_products():
    search_term = request.query.get('q')
    if not search_term:
        abort(400, "Search term required")
    
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    
    # Vulnerable SQL injection point
    query = f"SELECT p.id, p.name, p.price, c.name as category FROM products p JOIN categories c ON p.category_id = c.id WHERE p.name LIKE '%{search_term}%' OR c.name LIKE '%{search_term}%'"
    c.execute(query)
    
    results = []
    for row in c.fetchall():
        results.append({
            'id': row[0],
            'name': row[1],
            'price': row[2],
            'category': row[3]
        })
    
    conn.close()
    response.content_type = 'application/json'
    return json.dumps(results)