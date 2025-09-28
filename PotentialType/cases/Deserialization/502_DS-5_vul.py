@app.route('/upload_plugin', methods=['POST'])
def upload_plugin():
    if 'plugin' not in request.files:
        return jsonify({'error': 'No plugin file provided'}), 400

    plugin_file = request.files['plugin'].read()
    plugin_id = processor.load_processing_plugin(plugin_file)

    if plugin_id:
        return jsonify({'plugin_id': plugin_id}), 200
    return jsonify({'error': 'Plugin upload failed'}), 400