@app.route('/api/rules/math', methods=['POST'])
def evaluate_math():
    try:
        data = request.get_json()
        if 'expression' not in data:
            return jsonify({'error': 'Expression required'}), 400
        
        # Vulnerable math expression evaluation
        result = eval(data['expression'], {'__builtins__': None}, {
            'math': math,
            'datetime': datetime
        })
        
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400