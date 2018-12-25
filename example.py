import logging

import tornado.ioloop
import tornado.web
from tornado import gen

from tuya_api import Tuya

ty = Tuya(client_id='your client_id', secret='your secret', schema='you schema')


class TokenHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @gen.coroutine
    def get(self):
        try:
            ret = yield ty.get_access_token()
            return self.write(ret)
        except Exception as e:
            logging.exception(e)


class UserHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @gen.coroutine
    def get(self):
        try:
            page = self.get_argument('page', '1')
            page_size = self.get_argument('pageSize', '10')
            ret = yield ty.get_users(page_no=page, page_size=page_size)
            return self.write(ret)
        except Exception as e:
            logging.exception(e)


class TestHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @gen.coroutine
    def get(self,):
        try:
            # You can run other method here to test
            ret = yield ty.add_user(country_code='86', username='test',
                                    password='123456', nick_name='test')
            return self.write(ret)
        except Exception as e:
            logging.exception(e)


def main():
    app = tornado.web.Application([
        (r"/token", TokenHandler),
        (r'/user', UserHandler),
        (r'/test', TestHandler)
    ])
    app.listen(8888)

    print("=" * 100)
    print("* Server: Success!")
    print("* Host:   http://localhost:8888")
    print("* Quit the server with Control-C")
    print("=" * 100)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
