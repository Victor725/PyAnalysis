@app.route('/config', methods=['POST'])
def update_config():
    config_data = request.data
    try:
        # Additional vulnerable deserialization point
        config = yaml.load(config_data, Loader=yaml.Loader)
        return jsonify({'status': 'Config updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400