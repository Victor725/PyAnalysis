@app.get("/employees/search/")
def search_employees(request: Request, db: sqlite3.Connection = Depends(get_db)):
    search_query = request.query_params.get("query", "")
    
    if not search_query:
        raise HTTPException(status_code=400, detail="Search query parameter is required")

    cursor = db.cursor()
    
    # Vulnerable SQL injection point
    query = f"SELECT * FROM employees WHERE name LIKE '%{search_query}%' OR email LIKE '%{search_query}%'"
    cursor.execute(query)
    
    employees = []
    for row in cursor.fetchall():
        employees.append(dict(row))
    
    return JSONResponse(content=employees)