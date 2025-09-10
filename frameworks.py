frameworks = {
    "fastapi":{
        'regx': r'''@(app|router)\.(get|post|put|delete|patch|options|head|api_route|route|websocket)\s*\(|(add_api_route|add_websocket_route|add_route|include_router)\s*\(''',
        'examples': ''''''
    },
    'django':{
        'regx': r'''(?:\bpath\s*\(|\bre_path\s*\(|\binclude\s*\(|\.as_view\s*\(|router\.register\s*\(|@action\s*\(|consumers\..*\.as_asgi\s*\(|admin\.site\.urls)''',
        'examples': ''''''
    },
    'flask':{
        'regx': r'''(@app\.(route|get|post|put|delete|patch)\s*\()|(\.add_url_rule\s*\()|(\.register_blueprint\s*\()|(\.as_view\s*\()|(api\.add_resource\s*\()''',
        'examples': ''''''
    }
    # 'bottle':{
    #     'regx': r'''(@\s*(route|get|post|put|delete|patch|error)\s*\()|(\broute\s*\()|(\b\w+\.route\s*\()|(\b\w+\.add_route\s*\()''',
    #     'examples': ''''''
    # },
    # 'web2py':{
    #     'regx': r'''(?:\bpath\s*\(|\bre_path\s*\(|\binclude\s*\(|\.as_view\s*\(|router\.register\s*\(|@action\s*\(|consumers\..*\.as_asgi\s*\(|admin\.site\.urls)''',
    #     'examples': ''''''
    # }
}