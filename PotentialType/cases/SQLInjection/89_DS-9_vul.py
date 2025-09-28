@app.route('/records/search', methods=['GET'])
async def search_patient_records(request):
    first_name = request.args.get('first_name', '')
    last_name = request.args.get('last_name', '')
    diagnosis = request.args.get('diagnosis', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    conn = sqlite3.connect('medical.db')
    cursor = conn.cursor()
    
    # Vulnerable SQL injection - direct string interpolation with multiple parameters
    query = f"""
        SELECT p.patient_id, p.first_name, p.last_name, p.dob, 
               r.visit_date, r.diagnosis, r.treatment, r.physician
        FROM patients p
        JOIN records r ON p.patient_id = r.patient_id
        WHERE p.first_name LIKE '%{first_name}%' 
        AND p.last_name LIKE '%{last_name}%'
    """
    
    if diagnosis:
        query += f" AND r.diagnosis LIKE '%{diagnosis}%'"
    if start_date:
        query += f" AND r.visit_date >= '{start_date}'"
    if end_date:
        query += f" AND r.visit_date <= '{end_date}'"
    
    try:
        cursor.execute(query)
        records = []
        for row in cursor.fetchall():
            records.append({
                'patient_id': row[0],
                'patient_name': f"{row[1]} {row[2]}",
                'dob': row[3],
                'visit_date': row[4],
                'diagnosis': row[5],
                'treatment': row[6],
                'physician': row[7]
            })
        conn.close()
        return json({'records': records})
    except Exception as e:
        conn.close()
        return json({'error': str(e)}, status=500)