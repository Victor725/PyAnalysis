@app.route('/api/products/dynamic_filter', methods=['POST'])
def dynamic_filter():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['field', 'operator', 'value']):
            return jsonify({"error": "Invalid filter format"}), 400
        
        field = data['field']
        operator = data['operator']
        value = data['value']
        
        # Another vulnerable code injection point
        condition = f"item['{field}'] {operator} {value}"
        filtered = [p for p in products if eval(condition, {'item': p})]
        
        return jsonify({"count": len(filtered), "results": filtered})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500