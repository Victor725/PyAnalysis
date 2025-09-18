import ast

code = """
@app.get(MLFLOW_GATEWAY_CRUD_ROUTE_BASE, include_in_schema=False)
async def search_routes(page_token: str | None = None) -> SearchRoutesResponse:
    start_idx = SearchRoutesToken.decode(page_token).index if page_token is not None else 0

    end_idx = start_idx + MLFLOW_GATEWAY_SEARCH_ROUTES_PAGE_SIZE
    routes = list(app.dynamic_routes.values())
    result = {"routes": [r.to_route() for r in routes[start_idx:end_idx]]}
    if len(routes[end_idx:]) > 0:
        next_page_token = SearchRoutesToken(index=end_idx)
        result["next_page_token"] = next_page_token.encode()

    return result

# TODO: Remove deployments server URLs after deprecation window elapses
@app.get(MLFLOW_DEPLOYMENTS_LIMITS_BASE + "{endpoint}")
@app.get(MLFLOW_GATEWAY_LIMITS_BASE + "{endpoint}", include_in_schema=False)
async def get_limits(endpoint: str) -> LimitsConfig:
    raise HTTPException(status_code=501, detail="The get_limits API is not available yet.")

"""

# 解析源代码为 AST
tree = ast.parse(code)

decorated_funcs = []

# 遍历语法树，查找带装饰器的函数
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
        if node.decorator_list:  # 装饰器列表非空
            func_name = node.name
            decorators = []
            for d in node.decorator_list:
                if isinstance(d, ast.Name):  # @decorator
                    decorators.append(d.id)
                elif isinstance(d, ast.Call):  # @decorator(...)
                    if isinstance(d.func, ast.Name):
                        decorators.append(d.func.id)
                    elif isinstance(d.func, ast.Attribute):
                        decorators.append(f"{d.func.value.id}.{d.func.attr}")
                elif isinstance(d, ast.Attribute):  # @module.decorator
                    decorators.append(f"{d.value.id}.{d.attr}")
            decorated_funcs.append((func_name, decorators))

# 输出结果
for func, decos in decorated_funcs:
    print(f"函数: {func}, 装饰器: {decos}")
