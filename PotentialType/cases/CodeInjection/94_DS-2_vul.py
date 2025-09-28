def vulnerable_filter(data, filter_expr):
    """Vulnerable function with code injection"""
    filtered = []
    for item in data:
        try:
            # Dangerous eval of user-controlled filter expression
            if eval(filter_expr, {}, {'item': item}):  # Code injection point
                filtered.append(item)
        except:
            continue
    return filtered