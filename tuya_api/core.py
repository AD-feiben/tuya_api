import hashlib
import json
import logging
import time

from tornado import httpclient


def current_milli_time():
    return int(round(time.time() * 1000))


class Tuya(object):
    def __init__(self,
                 client_id: str,
                 secret: str,
                 schema: str,
                 threshold: int=300,
                 region: str='cn'):
        """
        :param client_id: 云 API 授权中的 AccessId
        :param secret: 云 API 授权中的 AccessKey
        :param schema: 应用包名
        :param threshold: 刷新 access_token 的临界值，默认提前 300s
        :param region: 根据环境切换接口地址，['cn', 'us', 'eu'] 默认为 cn
        """

        self.sign = None
        self.access_token = None
        self.refresh_token = None
        # 刷新 token 的临界值，默认为提前 300s 刷新token
        self.token_threshold = threshold
        self.expire_time = 0
        self.timestamp = 0

        if region not in ['cn', 'us', 'eu']:
            raise ValueError('region value is no expect')

        self.url = 'https://openapi.tuya{region}.com'.format(region=region)

        self.client_id = client_id
        self.secret = secret
        self.schema = schema

        self.http_client = httpclient.AsyncHTTPClient()

    # 计算签名
    def __calc_sign(self, has_token: bool=False):
        # has_token 为 True 时，access_token 必须存在
        hl = hashlib.md5()
        self.timestamp = str(current_milli_time())

        if has_token is True:
            if self.access_token is None:
                raise Exception('Tuya.__calc_sign: access token is None!')
            token = self.access_token
        else:
            token = ''

        s = self.client_id + token + self.secret + self.timestamp
        hl.update(s.encode(encoding='utf-8'))
        self.sign = hl.hexdigest().upper()

    # 获取请求头
    async def __get_header(self):
        if self.access_token is None or (current_milli_time() > self.timestamp + self.expire_time):
            # token 不存在或已过期，重新获取 token
            await self.get_access_token()
        elif current_milli_time() > self.timestamp + self.expire_time + (self.token_threshold * 1000):
            # token 过期时间大于临界值时
            await self.refresh_token()

        self.__calc_sign(has_token=True)
        header = {
            'client_id': self.client_id,
            'access_token': self.access_token,
            'sign': self.sign,
            't': self.timestamp
        }
        return header

    # token 相关
    async def get_access_token(self, grant_type: int=1, code: str=None):
        """
        获取 access_token
        :param grant_type: 授权模式 1-简易模式 2-授权码模式
        :param code: 授权码
        :return:
        """
        try:
            self.__calc_sign()
            url = '{url}/v1.0/token?grant_type={grant_type}&code={code}' \
                .format(url=self.url, grant_type=grant_type, code=code)

            headers = {
                'client_id': self.client_id,
                'sign': self.sign,
                't': self.timestamp
            }

            response = await self.http_client.fetch(
                request=url,
                headers=headers,
                validate_cert=False
            )
            if response.error:
                logging.exception('get access token error: ', response.error)
                return None
            else:
                body_str = response.body
                body = json.loads(body_str)

                if body['success'] is True:
                    self.access_token = body['result']['access_token']
                    self.refresh_token = body['result']['refresh_token']
                    self.expire_time = body['result']['expire_time']
                    return body
                else:
                    raise Exception(body['msg'])
        except Exception as e:
            logging.exception('get access token error: ', e)
            return None

    async def refresh_token(self, grant_type: int=1, code: str=None):
        """
        刷新 access_token, 如果 access_token 不存在等同于 access_token
        :param grant_type: 授权模式 1-简易模式 2-授权码模式
        :param code: 授权码
        :return:
        """
        try:
            if self.access_token is None or self.refresh_token is None:
                return await self.get_access_token_async(grant_type=grant_type, code=code)
            self.__calc_sign(False)
            url = '{url}/v1.0/token/{refresh_token}'.format(url=self.url, refresh_token=self.refresh_token)
            headers = {
                'client_id': self.client_id,
                'sign': self.sign,
                't': self.timestamp
            }

            response = await self.http_client.fetch(
                request=url,
                headers=headers,
                validate_cert=False
            )
            if response.error:
                logging.exception('refresh token error: ', response.error)
                return None
            else:
                body_str = response.body
                body = json.loads(body_str)

                if body['success'] is True:
                    self.access_token = body['result']['access_token']
                    self.refresh_token = body['result']['refresh_token']
                    self.expire_time = body['result']['expire_time']
                    return body
                else:
                    raise Exception(body['msg'])
        except Exception as e:
            logging.exception('refresh token error: ', e)
            return None

    # 用户相关接口
    async def get_users(self, page_no: int or str=1, page_size: int or str=10):
        """
        获取用户列表
        :param page_no: 当前页
        :param page_size: 页大小
        :return:
        """
        try:
            page_no = int(page_no)
            page_size = int(page_size)
            headers = await self.__get_header()
            url = '{url}/v1.0/apps/{schema}/users?page_no={page_no}&page_size={page_size}'\
                .format(url=self.url, schema=self.schema, page_no=page_no, page_size=page_size)

            response = await self.http_client.fetch(
                request=url,
                headers=headers,
                validate_cert=False
            )

            body = json.loads(response.body)
            return body
        except Exception as e:
            logging.exception('get users error: ', e)
            return None

    async def add_user(self, country_code: str, username: str,
                       password: str, nick_name: str, username_type: str='3'):
        """
        注册用户
        :param country_code: 国家码
        :param username: 用户名
        :param password: 用户密码
        :param nick_name: 昵称
        :param username_type: 用户名类型
        :return:
        """
        try:
            headers = await self.__get_header()
            headers['Content-Type'] = 'application/json'
            url = '{url}/v1.0/apps/{schema}/user'.format(url=self.url, schema=self.schema)

            data = {
                'country_code': country_code,
                'username': username,
                'password': password,
                'nick_name': nick_name,
                'username_type': username_type
            }
            body = json.dumps(data)
            response = await self.http_client.fetch(
                request=url,
                method='POST',
                headers=headers,
                body=body
            )
            res = json.loads(response.body)
            return res

        except Exception as e:
            logging.exception('post user error: ', e)

    async def get_user_devices_by_uid(self, uid: str):
        """
        根据用户 id 获取账号下的设备
        :param uid: 用户 id
        :return:
        """
        try:
            url = '{url}/v1.0/users/{uid}/devices'.format(url=self.url, uid=uid)
            response =  await self.http_client.fetch(
                request=url,
                headers=await self.__get_header(),
                validate_cert=False
            )
            body = json.loads(response.body)
            return body
        except Exception as e:
            logging.exception('get user devices error: ', e)
            return None

    # 设备相关接口
    async def generate_device_token(self, uid: str, time_zone_id: str,
                                    lon: str=None, lat: str=None, lang: str='zh'):
        """
        生成设备配网 token
        :param uid: 用户 id
        :param time_zone_id: 用户所在时区 id, 州/省份(Asia/Shanghai)
        :param lon: 经度
        :param lat: 纬度
        :param lang: 系统语言
        :return:
        """
        try:
            url = '{url}/v1.0/devices/token'.format(url=self.url)
            headers = await self.__get_header()
            headers['Content-Type'] = 'application/json'
            data = {
                'uid': uid,
                'timeZoneId': time_zone_id,
                'lon': lon,
                'lat': lat,
                'lang': lang
            }
            body = json.dumps(data)
            response = await self.http_client.fetch(
                request=url,
                method='POST',
                headers=headers,
                body=body
            )

            body = json.loads(response.body)
            return body
        except Exception as e:
            logging.exception('post devices token error: ', e)

    async def get_devices_by_token(self, token: str):
        """
        根据配网 token 获取设备列表
        :param token: 配网 token
        :return:
        """
        try:
            url = '{url}/v1.0/devices/tokens/{token}'.format(url=self.url, token=token)
            response = await self.http_client.fetch(
                request=url,
                headers=await self.__get_header(),
                validate_cert=False
            )
            body = json.loads(response.body)
            return body
        except Exception as e:
            logging.exception('get devices token error: ', e)

    async def get_device_by_id(self, device_id: str):
        """
        根据设备 id 获取设备信息
        :param device_id: 设备 id
        :return:
        """
        try:
            url = '{url}/v1.0/devices/{device_id}'.format(url=self.url, device_id=device_id)
            response = await self.http_client.fetch(
                request=url,
                headers=await self.__get_header(),
                validate_cert=False
            )
            body = json.loads(response.body)
            return body
        except Exception as e:
            logging.exception('get device error', e)

    async def get_devices_by_ids(self, device_ids: list):
        """
        批量获取设备信息
        :param device_ids: 设备 id list
        :return:
        """
        try:
            url = '{url}/v1.0/devices?device_ids={device_ids}'.format(url=self.url, device_ids=','.join(device_ids))
            response = await self.http_client.fetch(
                request=url,
                headers=await self.__get_header(),
                validate_cert=False
            )
            body = json.loads(response.body)
            return body
        except Exception as e:
            logging.exception('get devices error: ', e)

    async def get_functions_by_category(self, category: str):
        """
        根据分类获取 functions 列表
        :param category: 设备分类
        :return:
        """
        try:
            url = '{url}/v1.0/functions/{category}'.format(url=self.url, category=category)
            response = await self.http_client.fetch(
                request=url,
                headers=await self.__get_header(),
                validate_cert=False
            )
            body = json.loads(response.body)
            return body
        except Exception as e:
            logging.exception('get functions by category error: ', e)

    async def get_functions_by_id(self, device_id: str):
        """
        根据设备 id 获取 functions 列表
        :param device_id: 设备 id
        :return:
        """
        try:
            url = '{url}/v1.0/devices/{deviceId}/functions'.format(url=self.url, deviceId=device_id)
            response = await self.http_client.fetch(
                request=url,
                headers=await self.__get_header(),
                validate_cert=False
            )
            body = json.loads(response.body)
            return body
        except Exception as e:
            logging.exception('get functions by device id error: ', e)

    async def get_device_status_by_id(self, device_id: str):
        """
        根据设备 id 获取设备状态
        :param device_id: 设备 id
        :return:
        """
        try:
            url = '{url}/v1.0/devices/{device_id}/status'.format(url=self.url, device_id=device_id)
            response = await self.http_client.fetch(
                request=url,
                headers=await self.__get_header(),
                validate_cert=False
            )
            body = json.loads(response.body)
            return body
        except Exception as e:
            logging.exception('get device status error: ', e)

    async def get_devices_status_by_ids(self, device_ids: list):
        """
        批量获取设备状态
        :param device_ids: 设备 id list
        :return:
        """
        try:
            url = '{url}/v1.0/devices/status?device_ids={device_ids}'\
                .format(url=self.url, device_ids=','.join(device_ids))
            response = await self.http_client.fetch(
                request=url,
                headers=await self.__get_header(),
                validate_cert=False
            )
            body = json.loads(response.body)
            return body
        except Exception as e:
            logging.exception('get devices status error: ', e)

    async def post_commands(self, device_id: str, commands: list):
        """
        根据设备 id 对设备下发指令
        :param device_id: 设备 id
        :param commands: 命令集
        :return:
        """
        try:
            url = '{url}/v1.0/devices/{device_id}/commands'.format(url=self.url, device_id=device_id)
            headers = await self.__get_header()
            headers['Content-Type'] = 'application/json'
            body = json.dumps({'commands': commands})
            response = await self.http_client.fetch(
                request=url,
                method='POST',
                headers=headers,
                body=body
            )
            body = json.loads(response.body)
            return body
        except Exception as e:
            logging.exception('post commands error:', e)

    async def delete_device_by_id(self, device_id: str):
        """
        根据设备 id 移除设备
        :param device_id: 设备 id
        :return:
        """
        try:
            url = '{url}/v1.0/devices/{device_id}'.format(url=self.url, device_id=device_id)
            response = await self.http_client.fetch(
                request=url,
                method="DELETE",
                headers= await self.__get_header()
            )
            body = json.loads(response.body)
            return body
        except Exception as e:
            logging.exception('delete device error: ', e)

