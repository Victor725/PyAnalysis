@app.route('/tickets/search', methods=['GET'])
async def search_tickets():
    search_term = request.args.get('q', '')
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    customer_id = request.args.get('customer_id', '')

    conn = sqlite3.connect('support.db')
    cursor = conn.cursor()

    # Vulnerable SQL injection - dynamic query construction with direct interpolation
    query = """
        SELECT t.ticket_id, t.subject, t.status, t.priority, t.created_at, 
               c.name as customer_name, c.email as customer_email
        FROM tickets t
        JOIN customers c ON t.customer_id = c.customer_id
        WHERE (t.subject LIKE '%{search_term}%' OR t.description LIKE '%{search_term}%')
    """.format(search_term=search_term)

    if status:
        query += f" AND t.status = '{status}'"
    if priority:
        query += f" AND t.priority = {priority}"
    if customer_id:
        query += f" AND t.customer_id = '{customer_id}'"

    try:
        cursor.execute(query)
        tickets = []
        for row in cursor.fetchall():
            tickets.append({
                'ticket_id': row[0],
                'subject': row[1],
                'status': row[2],
                'priority': row[3],
                'created_at': row[4],
                'customer_name': row[5],
                'customer_email': row[6]
            })
        conn.close()
        return await jsonify({'tickets': tickets})
    except Exception as e:
        conn.close()
        return await jsonify({'error': str(e)}), 500