@app.route('/rules', methods=['POST'])
def upload_rules():
    if 'rules' not in request.files:
        return jsonify({'error': 'No rules file provided'}), 400

    rules_file = request.files['rules'].read()
    if processor.load_validation_rules(rules_file):
        return jsonify({'status': 'Rules updated'}), 200
    return jsonify({'error': 'Rules update failed'}), 400