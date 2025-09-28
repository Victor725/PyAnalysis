@app.route('/api/calculate', methods=['POST'])
def calculate_endpoint():
    try:
        data = request.get_json()
        if not data or 'expression' not in data:
            return jsonify({'error': 'Expression required'}), 400
        
        # Vulnerable calculation evaluation
        result = eval(data['expression'], 
                     {'__builtins__': None},
                     {'np': np, 'math': __import__('math'), 'datetime': datetime})
        
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400