    @cherrypy.expose
    @cherrypy.tools.json_out()
    def search_books(self, **params):
        title = params.get('title', '')
        author = params.get('author', '')
        genre = params.get('genre', '')
        available_only = params.get('available_only', 'false').lower() == 'true'

        # Vulnerable SQL injection - direct string concatenation with multiple parameters
        query = f"SELECT * FROM books WHERE title LIKE '%{title}%'"
        
        if author:
            query += f" AND author LIKE '%{author}%'"
        if genre:
            query += f" AND genre LIKE '%{genre}%'"
        if available_only:
            query += " AND available_copies > 0"

        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            books = []
            for row in cursor.fetchall():
                books.append({
                    'book_id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'isbn': row[3],
                    'published_date': row[4],
                    'genre': row[5],
                    'available_copies': row[6]
                })
            return {'books': books}
        except Exception as e:
            cherrypy.response.status = 500
            return {'error': str(e)}