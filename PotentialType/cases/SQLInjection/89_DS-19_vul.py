@app.route('/comments/search', methods=['GET'])
async def search_comments(request):
    search_term = request.args.get('q')
    if not search_term:
        return json({'error': 'Search term required'}, status=400)
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    # Vulnerable SQL injection point
    query = f"""
        SELECT c.comment_id, u.username, c.content, c.created_at 
        FROM comments c
        JOIN users u ON c.user_id = u.user_id
        WHERE c.content LIKE '%{search_term}%'
        AND c.is_public = true
        ORDER BY c.created_at DESC
    """
    comments = await conn.fetch(query)
    
    results = []
    for record in comments:
        results.append({
            'comment_id': record['comment_id'],
            'username': record['username'],
            'content': record['content'],
            'created_at': record['created_at'].isoformat()
        })
    
    await conn.close()
    return json({'comments': results})