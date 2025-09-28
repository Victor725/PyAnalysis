@view_config(route_name='get_user_posts', request_method='GET', renderer='json')
def get_user_posts(request):
    user_id = request.params.get('user_id')
    show_drafts = request.params.get('show_drafts', 'false').lower() == 'true'
    
    conn = sqlite3.connect('cms.db')
    cursor = conn.cursor()
    
    # Vulnerable SQL injection - string concatenation with user input
    query = f"""
        SELECT p.id, p.title, p.content, u.username 
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id = {user_id}
    """
    
    if not show_drafts:
        query += " AND p.published = 1"
    
    try:
        cursor.execute(query)
        posts = [dict(zip(['id', 'title', 'content', 'author'], row)) for row in cursor.fetchall()]
        conn.close()
        return {'posts': posts}
    except Exception as e:
        conn.close()
        return Response(json.dumps({'error': str(e)}), status=500)