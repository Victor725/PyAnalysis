@app.route('/api/execute', methods=['POST'])
def execute_operation():
    if not request.is_json:
        return jsonify({'error': 'JSON data required'}), 400
    
    data = request.get_json()
    if 'operation' not in data:
        return jsonify({'error': 'Operation required'}), 400
    
    try:
        # Another vulnerable code execution point
        result = eval(data['operation'])
        return jsonify({'result': str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400