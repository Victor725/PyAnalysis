@app.post("/search", response_class=HTMLResponse)
async def search_users(
    request: Request,
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None)
):
    conn = get_db_connection()
    
    # VULNERABLE FUNCTION: SQL injection through direct string concatenation
    query = "SELECT * FROM users WHERE 1=1"
    if username:
        query += f" AND username LIKE '%{username}%'"
    if email:
        query += f" AND email LIKE '%{email}%'"
    
    try:
        users = conn.execute(query).fetchall()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()
    
    return templates.TemplateResponse(
        "search_results.html",
        {"request": request, "users": users, "query": query}
    )