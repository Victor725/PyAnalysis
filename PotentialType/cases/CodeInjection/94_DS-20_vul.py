@app.route('/api/direct-validate', methods=['POST'])
def direct_validate():
    try:
        data = request.get_json()
        if not data or 'value' not in data or 'expression' not in data:
            return jsonify({'error': 'Value and expression required'}), 400
        
        # Vulnerable direct validation
        result = eval(data['expression'], 
                     {'value': data['value'], 're': re, 'datetime': datetime})
        return jsonify({'valid': bool(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400