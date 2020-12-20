from google.cloud import firestore
from six import class_types
from app.common.util import db
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.common.util import verify_token

'''
验证是否是管理员用户
'''
def verify_admin_token(token):
    admin_name = verify_token(token)
    if admin_name == None:
        return None
    # 查询一下admin表里面是否有该用户
    #admin/admin_users/username
    admin = db.collection('admin')    
    admin_users = admin.document('admin_users').get()
    admins = admin_users.to_dict()['username']
    if admin_name in admins:
        return admin_name
    else:
        return None

'''
取消用户与作者的绑定
'''
def cancel_bind_author(author_id, username):
    author_ref = db.collection('author').document(author_id)
    user_ref = db.collection('user').document(username)
    author = author_ref.get()
    user = user_ref.get()
    if 'bind_user' in author.to_dict():
        author_ref.update({u'bind_user': firestore.DELETE_FIELD})
    if 'bind_author' in user.to_dict():
        user_ref.update({u'bind_author': firestore.DELETE_FIELD})

class AdminTest(Resource):
    def post(self):
        """
        @@@
        ## 验证是否是管理员用户
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   |  管理员的token  |

        ### return
        无data
        @@@
        """
        print('请求一下adminTest')
        parser = RequestParser()
        parser.add_argument('token', type = str, required = True, location = 'headers')
        req = parser.parse_args()
        token = req.get('token')
        admin_name = verify_admin_token(token)
        if admin_name == None:
            return{
                'success':False,
                'message':'请以管理员身份操作'
            }, 200
        else:
            return{
                'success':True,
                'message':'成功'
            },200

class ShowAllReports(Resource):
    def post(self):
        """
        @@@
        ## 显示所有的申诉信息
        包括未处理的申诉和处理过的申诉信息
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   |  管理员的token  |

        ### args
        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    start_after    |    true    |    string   |    偏移游标    |
        
        ### return
        - #### data
        > | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        > 返回所有申诉的列表（20个）
        @@@
        """
        parser = RequestParser()

        parser.add_argument('token', type = str, required = True, location = 'headers')
        parser.add_argument("start_after", type=str,
                            location="args", required=False)
        req = parser.parse_args()
        token = req.get('token')
        start_after = req.get('start_after')
        admin_name = verify_admin_token(token)
        if admin_name == None:
            return{
                'success':False,
                'message':'请以管理员身份操作'
            }, 403
        reports = []
        ref = db.collection('report')
        start_after = db.collection('report').document(start_after).get()
        if start_after.exists:
            ref = ref.start_after(start_after).limit(20).stream()
        else:
            ref = ref.limit(20).stream()
        for report in ref:
            report_id= report.id
            report = report.to_dict()
            report['report_id'] = report_id
            reports.append(report)
        return{
            'success': True,
            'data': reports
        }, 200


class ShowUnhandleReports(Resource):
    def post(self):
        """
        @@@
        ## 显示没有处理过的申诉
        只显示没有处理过的申诉信息
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   |  管理员的token  |

        ### args
        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    start_after    |    true    |    string   |    偏移游标    |
        
        ### return
        - #### data
        > | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        > 返回申诉的列表（20个）
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type = str, required = True, location = 'headers')
        parser.add_argument("start_after", type=str,
                            location="args", required=False)
        req = parser.parse_args()
        token = req.get('token')
        start_after = req.get('start_after')
        admin_name = verify_admin_token(token)
        if admin_name == None:
            return{
                'success':False,
                'message':'请以管理员身份操作'
            }, 403
        reports = []
        ref = db.collection('report').where(u'status', u'==', 0)            #未处理的状态都是0
        start_after = db.collection('report').document(start_after).get()
        if start_after.exists:
            ref = ref.start_after(start_after).limit(20).stream()
        else:
            ref = ref.limit(20).stream()
        for report in ref:
            report_id = report.id
            report = report.to_dict()
            report['report_id'] = report_id
            reports.append(report)
        return{
            'success': True,
            'data': reports
        }, 200

class DenyReport(Resource):
    def post(self):
        """
         @@@
        ## 拒绝用户的申诉请求
        **管理员拒绝用户的申请请求**
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   |  管理员的token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    report_id    |    false    |    string   |   要处理的申诉id   |

        ### return
        无data
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type = str, required = True, location = 'headers')
        parser.add_argument('report_id', type = str, required = True)
        req = parser.parse_args()
        token = req.get('token')
        report_id = req.get('report_id')
        admin_name = verify_admin_token(token)
        if admin_name == None:
            return{
                'success':False,
                'message':'请以管理员身份操作'
            }, 403
        print(report_id)
        report_ref = db.collection('report').document(report_id)
        report = report_ref.get()
        if not report.exists:
                return{
                    'success': False,
                    'message': '申诉信息不存在'}, 403
        report_dict = report.to_dict()
        print(report_dict)
        if report_dict['status'] == 1:
            return{
                'success':False,
                'message':'该申诉信息已经处理'
            }, 403
        else:
            report_ref.update({u'status': 1})
        return{
            'success': True,
            'message': '处理申诉信息成功'
        }, 200

class PassReport(Resource):
    def post(self):
        """
         @@@
        ## 同意用户的申诉请求
        **管理员同意用户的申请请求**

        ### header args
        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   |  管理员的token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    report_id    |    false    |    string   |   要处理的申诉id   |

        ### return
        无data
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type = str, required = True, location = 'headers')
        parser.add_argument('report_id', type = str, required = True)
        req = parser.parse_args()
        token = req.get('token')
        report_id = req.get('report_id')
        admin_name = verify_admin_token(token)
        if admin_name == None:
            return{
                'success':False,
                'message':'请以管理员身份操作'
            }, 403
        report_ref = db.collection('report').document(report_id)
        report = report_ref.get()
        report_dict = report.to_dict()
        if report_dict['status'] == 1:
            return{
                'success':True,
                'message':'该申诉信息已经处理'
            }, 200
        else:
            report_ref.update({u'status': 1})
            author_id = report_dict['author_id']
            author_ref = db.collection('author').document(author_id)
            author = author_ref.get()
            if not author.exists:
                return{
                    'success': False,
                    'message': '作者不存在'}, 403
            if not 'bind_user' in author.to_dict():
                return{
                    'success': False,
                    'message': '作者未被认领'}, 403
            #获得该作者绑定的用户名
            username = author.to_dict()['bind_user']
            cancel_bind_author(author_id, username)
            return{
                'success': True,
                'message': '处理申诉信息成功'
            }, 200

class CancelBindAuthor(Resource):
    def post(self):
        """
        @@@
        ## 取消用户的认证资格
        **管理员取消用户的认领资格**

        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   |  管理员的token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    author_id    |    false    |    string   |    认领的作者id   |
        |    username     |    false    |    string   |    认领的用户名   |

        ### return
        无data
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type = str, required = True, location = 'headers')
        parser.add_argument('author_id', type = str, required = True)
        parser.add_argument('username', type = str, required = True)
        req = parser.parse_args()
        token = req.get('token')
        author_id = req.get('author_id')
        username = req.get('username')
        admin_name = verify_admin_token(token)
        if admin_name == None:
            return{
                'success':False,
                'message':'请以管理员身份操作'
            }, 403
        cancel_bind_author(author_id, username) 
        return{
            'success':True,
            'message':'取消用户认领成功'
        }, 200


class ShowAllUsers(Resource):
    def post(self):
        """
        @@@
        ## 显示所有用户的列表
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   |  管理员的token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    start_after   |    true    |    string   |    偏移游标  |  

        ### return
        - #### data
        > | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        > data:用户列表
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type = str, required = True, location = 'headers')
        parser.add_argument("start_after", type=str,
                            location="args", required=False)
        req = parser.parse_args()
        token = req.get('token')
        start_after = req.get('start_after')
        admin_name = verify_admin_token(token)
        if admin_name == None:
            return{
                'success':False,
                'message':'请以管理员身份操作'
            }, 403
        users_list = []
        user_ref = db.collection('user')
        start_after = db.collection('user').document(start_after).get()
        if start_after.exists:
            users = user_ref.start_after(start_after).limit(20).stream()
        else:
            users = user_ref.limit(20).stream()
        for user in users:
            user = user.to_dict()
            user.pop('password')
            users_list.append(user)
        return{
            'success': True,
            'data': users_list
        }, 200

class DeleteUser(Resource):
    def post(self):
        """
        ## 删除用户
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   |  管理员的token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    username   |    false    |    string   |  要删除的用户名 |  

        ### return
        > 是否成功
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type = str, required = True, location = 'headers')
        parser.add_argument('username', type=str, required=True)
        req = parser.parse_args()
        username = req.get('username')
        token = req.get('token')
        admin_name = verify_admin_token(token)
        if admin_name == None:
            return{
                'success':False,
                'message':'请以管理员身份操作'
            }, 403
        user_ref = db.collection('user')
        user = user_ref.document(username).get()
        if not user.exists:
            return{
                'success': False,
                'message': '用户不存在'}, 403
        else:
            user_ref.document(username).delete()
            return{
                'success': True,
                'message': '用户删除成功'}