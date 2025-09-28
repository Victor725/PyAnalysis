@app.route('/upload_module', methods=['POST'])
def upload_module():
    if 'module' not in request.files:
        return jsonify({'error': 'No module file provided'}), 400

    module_file = request.files['module'].read()
    module_id = analyzer.load_analysis_module(module_file)

    if module_id:
        return jsonify({'module_id': module_id}), 200
    return jsonify({'error': 'Module upload failed'}), 400