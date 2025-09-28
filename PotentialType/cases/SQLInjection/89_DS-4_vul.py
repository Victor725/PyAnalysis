@app.get("/cases/search", response_model=list[Case])
def search_cases(
    query: Optional[str] = Query(None, description="Search term for case title or description"),
    status: Optional[str] = Query(None, description="Filter by case status"),
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned attorney")
):
    conn = sqlite3.connect('legal_cases.db')
    cursor = conn.cursor()
    
    # Vulnerable SQL injection - dynamic query construction with direct interpolation
    base_query = """
        SELECT c.case_id, c.title, c.description, c.status, 
               c.client_id, c.assigned_to, c.created_at
        FROM cases c
        WHERE 1=1
    """
    
    if query:
        base_query += f" AND (c.title LIKE '%{query}%' OR c.description LIKE '%{query}%')"
    if status:
        base_query += f" AND c.status = '{status}'"
    if client_id:
        base_query += f" AND c.client_id = '{client_id}'"
    if assigned_to:
        base_query += f" AND c.assigned_to = '{assigned_to}'"
    
    try:
        cursor.execute(base_query)
        cases = []
        for row in cursor.fetchall():
            cases.append(Case(
                case_id=row[0],
                title=row[1],
                description=row[2],
                status=row[3],
                client_id=row[4],
                assigned_to=row[5],
                created_at=row[6]
            ))
        conn.close()
        return cases
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))