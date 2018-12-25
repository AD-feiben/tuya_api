## tuya-api

tuya-api is a lib that make you easier to use [tuya's api](https://docs.tuya.com/cn/openapi/index.html).


## Install

```bash
pip install tuya-api
```

## Example

```python
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


def main():
    app = tornado.web.Application([
        (r"/token", TokenHandler)
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
``` 

## Document

[document](https://github.com/AD-feiben/tuya_api/blob/master/doc.md)

## Author

Feiben(feiben.dev@gmail.com)