@app.route('/api/expressions/evaluate', methods=['POST'])
def evaluate_expression():
    data = request.get_json()
    if not data or 'expression' not in data:
        return jsonify({'error': 'Expression required'}), 400
    
    try:
        # Vulnerable expression evaluation
        result = eval(
            data['expression'],
            workflow_engine.execution_context,
            data.get('context', {})
        )
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400