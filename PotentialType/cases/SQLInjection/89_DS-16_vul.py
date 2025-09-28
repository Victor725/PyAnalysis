@view_config(route_name='search_users', request_method='GET')
def search_users_view(request):
    search_term = request.params.get('q', '')
    
    if not search_term:
        return Response(json.dumps({'error': 'Search term required'}),
                      status=400, content_type='application/json')
    
    conn = sqlite3.connect('user_profiles.db')
    cursor = conn.cursor()
    
    # Vulnerable SQL injection point
    query = f"SELECT id, username, email, bio FROM users WHERE username LIKE '%{search_term}%' OR bio LIKE '%{search_term}%'"
    cursor.execute(query)
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'bio': row[3]
        })
    
    return Response(json.dumps(results), content_type='application/json')