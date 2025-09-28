@app.get("/employees/filter/")
def get_employee_by_filter(
    filter_type: str = Query(..., description="Filter type (name, position, department)"),
    filter_value: str = Query(..., description="Value to filter by")
):
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    
    # Vulnerable SQL injection - direct string interpolation
    query = f"SELECT * FROM employees WHERE {filter_type} = '{filter_value}'"
    
    try:
        cursor.execute(query)
        employees = cursor.fetchall()
        conn.close()
        if not employees:
            raise HTTPException(status_code=404, detail="No employees found")
        return [dict(zip(['id', 'name', 'position', 'department', 'salary'], emp)) for emp in employees]
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))