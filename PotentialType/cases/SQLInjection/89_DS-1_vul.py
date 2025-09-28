@app.route('/search_product', methods=['GET'])
def search_product():
    search_term = request.args.get('query', '')
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        # Vulnerable SQL injection - concatenating user input directly
        query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%' OR category LIKE '%{search_term}%'"
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        products = []
        for row in results:
            products.append({
                'id': row[0],
                'name': row[1],
                'price': row[2],
                'quantity': row[3],
                'category': row[4]
            })
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500