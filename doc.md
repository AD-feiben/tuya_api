## Initialize

| parameter | type | description                                  | requirements         |
| --------- | ---- | -------------------------------------------- | -------------------- |
| client_id | str  |                                              | True                 |
| secret    | str  |                                              | True                 |
| schema    | str  |                                              | True                 |
| threshold | int  | refresh token {threshold} seconds in advance | False (default: 300) |
| region    | str  | choose one of them [cn, us, eu]              | False (default: cn)  |



## Methods



### Tuya.get_access_token

[tuya's official document](https://docs.tuya.com/cn/openapi/api/get_token_1.0.html)

| parameter  | type | requirements       |
| ---------- | ---- | ------------------ |
| grant_type | int  | False (default: 1) |
| code       | str  | False              |



### Tuya.refresh_token

[tuya's official document](https://docs.tuya.com/cn/openapi/api/get_token.refresh_token_1.0.html)

> parameter is same as Tuya.get_access_token



### Tuya.get_users

[tuya's official document](https://docs.tuya.com/cn/openapi/api/get_apps.schema.users_1.0.html)

| parameter | type       | requirements        |
| --------- | ---------- | ------------------- |
| page_no   | int or str | False (default: 1)  |
| page_size | int or str | False (default: 10) |



### Tuya.add_user

[tuya's official document](https://docs.tuya.com/cn/openapi/api/post_apps.schema.user_1.0.html)

| parameter     | type | requirements       |
| ------------- | ---- | ------------------ |
| country_code  | str  | True               |
| username      | str  | True               |
| password      | str  | True               |
| nick_name     | str  | True               |
| username_type | str  | False (default: 3) |

> **The password is automatically encrypted using MD5** 


### Tuya.get_user_devices_by_uid

[tuya's official document](https://docs.tuya.com/cn/openapi/api/get_users.uid.devices_1.0.html)

| parameter | type | requirements |
| --------- | ---- | ------------ |
| uid       | str  | True         |



### Tuya.generate_device_token

[tuya's official document](https://docs.tuya.com/cn/openapi/api/post_devices.token_1.0.html)

| parameter    | type | requirements          |
| ------------ | ---- | --------------------- |
| uid          | str  | True                  |
| time_zone_id | str  | True                  |
| lon          | str  | False (defalut: None) |
| lat          | str  | False (default: None) |
| lang         | str  | False (default: zh)   |



### Tuya.get_devices_by_token

[tuya's officical document](https://docs.tuya.com/cn/openapi/api/get_devices.tokens.token_1.0.html)

| parameter | type | requirements |
| --------- | ---- | ------------ |
| token     | str  | True         |



### Tuya.get_device_by_id

[tuya's official document](https://docs.tuya.com/cn/openapi/api/get_devices.deviceId_1.0.html)

| parameter | type | requirements |
| --------- | ---- | ------------ |
| device_id | str  | True         |



### Tuya.get_devices_by_ids

[tuya's official document](https://docs.tuya.com/cn/openapi/api/get_devices_1.0.html)

| parameter  | type      | requirements |
| ---------- | --------- | ------------ |
| device_ids | list<str> | True         |

example

```python
device_ids = ['device_id1', 'device_id2']
```



### Tuya.get_functions_by_category

[tuya's official document](https://docs.tuya.com/cn/openapi/api/get_functions.category_1.0.html)

| parameter | type | requirements |
| --------- | ---- | ------------ |
| category  | str  | True         |



### Tuya.get_functions_by_id

[tuya's official document](https://docs.tuya.com/cn/openapi/api/get_devices.deviceId.functions_1.0.html)

| parameter | type | requirements |
| --------- | ---- | ------------ |
| device_id | str  | True         |



### Tuya.get_device_status_by_id

[tuya's official document](https://docs.tuya.com/cn/openapi/api/get_devices.deviceId.status_1.0.html)

| parameter | type | requirements |
| --------- | ---- | ------------ |
| device_id | str  | True         |



### Tuya.get_devices_status_by_ids

[tuya's official document](https://docs.tuya.com/cn/openapi/api/get_devices.status_1.0.html)

| parameter  | type      | requirements |
| ---------- | --------- | ------------ |
| device_ids | list<str> | True         |

example

```python
device_ids = ['device_id1', 'device_id2']
```



### Tuya.post_commands

[tuya's official document](https://docs.tuya.com/cn/openapi/api/post_devices.deviceId.commands_1.0.html)

| parameter | type         | requirements |
| --------- | ------------ | ------------ |
| device_id | str          | True         |
| commands  | list<object> | True         |

example

```python
commands = [
    {
        "code": "switch_led",
        "value": True
    },
    {
        "code": "bright",
        "value": 30
    }
]
```



### Tuya.delete_device_by_id

[tuya's official document](https://docs.tuya.com/cn/openapi/api/delete_devices.deviceId_1.0.html)

| parameter | type | requirements |
| --------- | ---- | ------------ |
| device_id | str  | True         |

