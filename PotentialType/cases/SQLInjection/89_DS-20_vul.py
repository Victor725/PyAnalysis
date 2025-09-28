    @cherrypy.expose
    @cherrypy.tools.json_out()
    def generate_report(self, **params):
        department = params.get('department')
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        
        conn = sqlite3.connect('reports.db')
        c = conn.cursor()
        
        # Vulnerable SQL injection point
        query = "SELECT r.id, r.title, e.name as author, d.name as department, r.created_at "
        query += "FROM reports r JOIN employees e ON r.created_by = e.id "
        query += "JOIN departments d ON e.department_id = d.id "
        
        conditions = []
        if department:
            conditions.append(f"d.name = '{department}'")
        if start_date:
            conditions.append(f"r.created_at >= '{start_date}'")
        if end_date:
            conditions.append(f"r.created_at <= '{end_date}'")
        
        if conditions:
            query += "WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY r.created_at DESC"
        
        c.execute(query)
        reports = []
        for row in c.fetchall():
            reports.append({
                'id': row[0],
                'title': row[1],
                'author': row[2],
                'department': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        return {'reports': reports}