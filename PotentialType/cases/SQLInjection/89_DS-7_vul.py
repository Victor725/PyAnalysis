@app.route('/rooms/search', method='GET')
def search_rooms():
    room_type = request.query.get('room_type', '')
    max_price = request.query.get('max_price', '')
    check_date = request.query.get('check_date', '')
    
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    
    # Vulnerable SQL injection - direct string interpolation with multiple parameters
    query = f"SELECT * FROM rooms WHERE room_type LIKE '%{room_type}%'"
    
    if max_price:
        query += f" AND price_per_night <= {max_price}"
    
    if check_date:
        query += f""" AND room_id NOT IN (
            SELECT room_id FROM bookings 
            WHERE '{check_date}' BETWEEN check_in_date AND check_out_date
        )"""
    
    try:
        cursor.execute(query)
        rooms = []
        for row in cursor.fetchall():
            rooms.append({
                'room_id': row[0],
                'room_number': row[1],
                'room_type': row[2],
                'price_per_night': row[3],
                'max_occupancy': row[4],
                'amenities': row[5].split(',') if row[5] else []
            })
        conn.close()
        response.content_type = 'application/json'
        return json.dumps({'rooms': rooms})
    except Exception as e:
        conn.close()
        response.status = 500
        return json.dumps({'error': str(e)})