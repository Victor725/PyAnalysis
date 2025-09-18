from sanic import Sanic
from sanic.views import CompositionView  # 合成视图
from sanic.views import HTTPMethodView  # http协议方法视图
from sanic.views import stream as stream_decorator  # 流媒体装饰
from sanic.blueprints import Blueprint  # 蓝图
from sanic.response import stream, text


bq = Blueprint("blueprint_request_stream")  # 实例化蓝图对象(把蓝图请求流传到蓝图对象中)
# 实例化一个Sanic对象
app = Sanic("request_stream")  # 把请求媒体传到Sanic对象


class SimpleView(HTTPMethodView):  # 简单的视图,继承HTTPMethodView这个类
    # 流媒体装饰器
    @stream_decorator
    # 异步提交强求的处理函数
    async def post(self, request):
        # 当以一个空的result
        result = ""
        while 1:
            # 从请求的流媒体中读取请求体
            body = await request.stream.read()
            # 判断读取的请求体是空(无值)
            if body is None:
                break  # 停止循环
            print(body, type(body))
            result += body.decode("utf-8")  # 读取到的body是一个bytes


@app.post("/stream", stream=True)  # 提交请求的路由
async def handler(request):
    async def streaming(response):
        while 1:
            # 从请求的stream中读取请求体
            body = await request.stream.read()
            # 如果body是空值
            if body is None:
                break  # 停止循环
            body = body.decode("utf-8").replace("1", "A")  # 把body中的字符串1,替换成A
            await response.write(body)  # 阻塞的把请求体写入到响应的response中
    return stream(streaming)  # 调用streaming异步函数


# put请求,修改数据
@app.put("/bq_stream", stream=True)
async def bq_put_handler(request):
    result = ""
    while 1:
        body = await request.stream.read()
        if body is None:
            break
        print(body, type(body))
        result += body.decode("utf-8").replace("1", "A")
    return text("result")


# 你可以在流媒体参数中使用bq_add_route()方法
async def bq_post_handler(request):
    result = ""  # 定义一个空的result
    while 1:
        body = await request.stream.read()
        if body is None:
            break
        result += body.decode("utf-8").replace("1", "A")
    return text(result)  # 返回请求体中获取到的内容

bq.add_route(bq_post_handler, "/bq_stream", methods=["POST"], stream=True)  # 我自己测试的add_route没有stream=None这个关键字
# bp.add_route(bp_post_handler, '/bp_stream', methods=['POST'], stream=True)


# 异步处理post请求的方法
async def post_handler(request):
    result = ""
    while 1:
        body = await request.read()
        if not body:
            break
        result += body.decode("utf-8")
    return text(result)  # 此时的result是个字符串


app.blueprint(bq)  # 把实例化的蓝图注册进来
app.add_route(SimpleView.as_view(), "/method_view")
view = CompositionView()  # 实例化合成视图对象
view.add(["POST"], post_handler, stream=True)
app.add_route(view, "/composition_view")

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000, debug=True)