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
    TOKEN_EXPIRATION = 7200
    # 使用 CDN
    #API_DOC_CDN = True
    # 禁用文档页面
    #API_DOC_ENABLE = False
    # 需要显示文档的 Api
    API_DOC_MEMBER = ['api', 'platform']
    # 需要排除的 RESTful Api 文档
    RESTFUL_API_DOC_EXCLUDE = []

    ##邮件相关
    MAIL_SERVER = 'smtpdm.aliyun.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'noreply@gugoo.xyz'
    MAIL_PASSWORD = 'ALyzy981227'
    MAIL_DEFAULT_SENDER = 'noreply@gugoo.xyz'