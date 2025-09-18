import tornado.web
'''
tornado 的基础web框架模块
'''
import tornado.ioloop
'''
tornado 的核心IO循环模块， 封装了Linux的epoll和BSD的kqueue,是tornado高效的基础
'''
import tornado.httpserver


# 类比Django 中的视图
class IndexHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        # 对应http 请求的方法
        # 给浏览器响应信息
        self.write("hello world.....")



if __name__ == '__main__':
    # 转化命令行参数，并保存到tornado.options.options
    tornado.options.parse_command_line()
    # tornado.options.options.parse_config_file("config")
    app = tornado.web.Application([
        # 路由
        (r"/",IndexHandler),
        (r"/hello", func)
    ])
    print("list",tornado.options.options.list)
    httpServer = tornado.httpserver.HTTPServer(app)

    httpServer.bind(tornado.options.options.port)
    httpServer.start()
    tornado.ioloop.IOLoop.current().start()