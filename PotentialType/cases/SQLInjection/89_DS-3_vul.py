@csrf_exempt
def search_products(request):
    if request.method == 'GET':
        search_term = request.GET.get('q', '')
        try:
            with connection.cursor() as cursor:
                # Vulnerable SQL injection - direct string interpolation
                query = f"""
                    SELECT * FROM products 
                    WHERE name LIKE '%{search_term}%' 
                    OR description LIKE '%{search_term}%'
                    OR category LIKE '%{search_term}%'
                    ORDER BY price DESC
                """
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                products = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return JsonResponse({'products': products})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)