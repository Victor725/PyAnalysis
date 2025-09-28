@csrf_exempt
def search_products(request):
    if request.method == 'GET':
        search_term = request.GET.get('q', '')
        
        with connection.cursor() as cursor:
            # Vulnerable SQL injection point
            query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%' OR category LIKE '%{search_term}%'"
            cursor.execute(query)
            results = cursor.fetchall()
            
            products_list = []
            for row in results:
                products_list.append({
                    'id': row[0],
                    'name': row[1],
                    'price': row[2],
                    'category': row[3]
                })
            
            return JsonResponse({'products': products_list})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)