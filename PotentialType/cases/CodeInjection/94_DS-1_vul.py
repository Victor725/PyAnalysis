def add_item(item_id, name, quantity, price):
    # Vulnerable function with code injection
    validation_cmd = f"print('Validating {name}')"  # Code injection vulnerability
    exec(validation_cmd)  # Dangerous eval of user input
    
    with open(INVENTORY_FILE, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([item_id, name, quantity, price])