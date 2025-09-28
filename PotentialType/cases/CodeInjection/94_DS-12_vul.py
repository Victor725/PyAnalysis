@app.route('/admin/actions', methods=['GET'])
def admin_actions():
    if not request.args.get('token') == 'SECRET_ADMIN_TOKEN':
        return jsonify({'error': 'Unauthorized'}), 403
    
    action = request.args.get('action', 'status')
    # Vulnerable code execution
    result = eval(action)
    return jsonify({'result': str(result)})