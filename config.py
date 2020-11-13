import os


#判断是否是本地环境
if "INCONTAINER" in os.environ:
    pass
else:
    os.environ['http_proxy'] = 'http://127.0.0.1:10809'
    os.environ['https_proxy'] = 'http://127.0.0.1:10809'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key/GugooScholar-4b624617fdda.json'


class Config(object):
    # 私钥
    SECRET_KEY = '\xc9ixnRb\xe40\xc4\xa5\x7f\x04\xd0y6\x02\x1f\x96\xeao+\x8a\x9f\xe4'
    TOKEN_EXPIRATION = 3600