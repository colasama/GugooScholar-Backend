from app.resources.paper import get_authors, get_venue
from app.common.util import db
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.common.util import verify_token

class SubscribeAuthor(Resource):
    def post(self):
        """
        @@@
        ## 订阅科研人员
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   | token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    author_id    |    false    |    string   |    订阅的作者id   |

        ### return
        data
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type=str,
                            required=True, location='headers')
        parser.add_argument('author_id', type=str, required=True)
        req = parser.parse_args()
        token = req.get('token')
        author_id = req.get('author_id')
        username = verify_token(token)
        if username == None:
            return{
                'success': False,
                'message': 'token无效'}, 403
        author_ref = db.collection('author').document(author_id)
        author = author_ref.get()
        if not author.exists:
            return{
                'success': False,
                'message': '作者不存在'}, 403
        data = {
            'username': username,
            'author_id':author_id
        }
        subscribes = db.collection('subscribe').where(u'username', u'==', username).where(u'author_id', u'==', author_id).get()
        for subscribe in subscribes:
            if subscribe.to_dict()['author_id'] == author_id:
                return{
                        'success':False,
                        'message':'您已订阅该作者'
                    }, 403
        db.collection('subscribe').add(data)
        return{
            'success': True,
            'data': data}

class SubscribePaper(Resource):
    def post(self):
        """
        @@@
        ## 订阅论文
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   | token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    paper_id    |    false    |    string   |    订阅的论文id   |

        ### return
        data
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type=str,
                            required=True, location='headers')
        parser.add_argument('paper_id', type=str, required=True)
        req = parser.parse_args()
        token = req.get('token')
        paper_id = req.get('paper_id')
        username = verify_token(token)
        if username == None:
            return{
                'success': False,
                'message': 'token无效'}, 403
        paper_ref = db.collection('paper').document(paper_id)
        paper = paper_ref.get()
        if not paper.exists:
            return{
                'success': False,
                'message': '论文不存在'}, 403
        data = {
            'username': username,
            'paper_id':paper_id
        }
        subscribes = db.collection('subscribe').where(u'username', u'==', username).where(u'paper_id', u'==', paper_id).get()
        for subscribe in subscribes:
            if subscribe.to_dict()['paper_id'] == paper_id:
                return{
                        'success':False,
                        'message':'您已订阅该论文'
                    }, 403
        db.collection('subscribe').add(data)
        return{
            'success': True,
            'data': data}

class CancelSubscribeAuthor(Resource):
    def post(self):
        """
        @@@
        ## 取消订阅科研人员
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   | token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    author_id    |    false    |    string   |    订阅的作者id   |

        ### return
        无data
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type=str,
                            required=True, location='headers')
        parser.add_argument('author_id', type=str, required=True)
        req = parser.parse_args()
        token = req.get('token')
        author_id = req.get('author_id')
        username = verify_token(token)
        if username == None:
            return{
                'success': False,
                'message': 'token无效'}, 403
        subscribes = db.collection('subscribe').where(u'username', u'==', username).where(u'author_id', u'==', author_id).get()
        for subscribe in subscribes:
            db.collection('subscribe').document(subscribe.id).delete()
            return{
                'success':True,
                'message':'取消订阅成功'
            }
        return{
            'success':False,
            'message':'您未订阅该作者'
        }, 403
        

class CancelSubscribePaper(Resource):
    def post(self):
        """
        @@@
        ## 取消订阅论文
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   | token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    paper_id    |    false    |    string   |    订阅的论文id   |

        ### return
        无data
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type=str,
                            required=True, location='headers')
        parser.add_argument('paper_id', type=str, required=True)
        req = parser.parse_args()
        token = req.get('token')
        paper_id = req.get('paper_id')
        username = verify_token(token)
        if username == None:
            return{
                'success': False,
                'message': 'token无效'}, 403
        subscribes = db.collection('subscribe').where(u'username', u'==', username).where(u'paper_id', u'==', paper_id).get()
        for subscribe in subscribes:
            db.collection('subscribe').document(subscribe.id).delete()
            return{
                'success':True,
                'message':'取消订阅成功'
            }
        return{
            'success':False,
            'message':'您未订阅该论文'
        }, 403

class ShowSubscribeAuthor(Resource):
    def post(self):
        """
        @@@
        ## 显示订阅的科研人员
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   | token  |

        ### return
        data 订阅的作者列表
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type = str, required = True, location = 'headers')
        req = parser.parse_args()
        token = req.get('token')
        username = verify_token(token)
        if username == None:
            return{
                'success':False,
                'message':'token无效'
            }, 403
        author_ids = []
        ref = db.collection('subscribe').where(u'username', u'==', username).get()
        for author in ref:
            if 'author_id' in author.to_dict():
                author_ids.append(author.to_dict()['author_id'])
        authors = []
        for author_id in author_ids:
            author = db.collection('author').document(author_id).get()
            if author.exists:
                author = author.to_dict()
                author['id'] = author_id
                authors.append(author)
        return{
            'success': True,
            'data': authors
        }, 200

class ShowSubscribePaper(Resource):
    def post(self):
        """
        @@@
        ## 显示订阅的论文
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   | token  |

        ### return
        data 订阅的论文
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type = str, required = True, location = 'headers')
        req = parser.parse_args()
        token = req.get('token')
        username = verify_token(token)
        if username == None:
            return{
                'success':False,
                'message':'token无效'
            }, 403
        paper_ids = []
        ref = db.collection('subscribe').where(u'username', u'==', username).get()
        for paper in ref:
            if 'paper_id' in paper.to_dict():
                paper_ids.append(paper.to_dict()['paper_id'])
        print(paper_ids)
        papers = []
        for paper_id in paper_ids:
            paper = db.collection('paper').document(paper_id).get()
            if paper.exists:
                paper = paper.to_dict()
                paper['id'] = paper_id
                get_venue(paper)
                get_authors(paper['authors'])
                papers.append(paper)
        return{
            'success': True,
            'data': papers
        }, 200

class AuthorIsSubscribed(Resource):
    def post(self):
        """
        @@@
        ## 判断是否已经订阅科研人员
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   | token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    author_id    |    false    |    string   |    订阅的作者id   |

        ### return
        是否订阅
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type=str,
                            required=True, location='headers')
        parser.add_argument('author_id', type=str, required=True)
        req = parser.parse_args()
        token = req.get('token')
        author_id = req.get('author_id')
        username = verify_token(token)
        if username == None:
            return{
                'success': False,
                'message': 'token无效'}
        author_ref = db.collection('author').document(author_id)
        author = author_ref.get()
        if not author.exists:
            return{
                'success': False,
                'message': '作者不存在'}
        subscribes = db.collection('subscribe').where(u'username', u'==', username).where(u'author_id', u'==', author_id).get()
        for subscribe in subscribes:
            if subscribe.to_dict()['author_id'] == author_id:
                return{
                        'success':True,
                        'message':'您已订阅该作者'
                    }
        return{
            'success': False,
            'data': '您未订阅该作者'}


class PaperIsSubscribed(Resource):
    def post(self):
        """
        @@@
        ## 是否订阅论文
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   | token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    paper_id    |    false    |    string   |    订阅的论文id   |

        ### return
        是否订阅
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type=str,
                            required=True, location='headers')
        parser.add_argument('paper_id', type=str, required=True)
        req = parser.parse_args()
        token = req.get('token')
        paper_id = req.get('paper_id')
        username = verify_token(token)
        if username == None:
            return{
                'success': False,
                'message': 'token无效'}
        paper_ref = db.collection('paper').document(paper_id)
        paper = paper_ref.get()
        if not paper.exists:
            return{
                'success': False,
                'message': '论文不存在'}
        subscribes = db.collection('subscribe').where(u'username', u'==', username).where(u'paper_id', u'==', paper_id).get()
        for subscribe in subscribes:
            if subscribe.to_dict()['paper_id'] == paper_id:
                return{
                        'success':True,
                        'message':'您已订阅该论文'
                    }
        return{
            'success': False,
            'data': '您未订阅改论文'}
class SubscribeFund(Resource):
    def post(self):
        """
        @@@
        ## 订阅项目
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   | token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    fund_id    |    false    |    string   |    订阅的项目id   |

        ### return
        data
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type=str,
                            required=True, location='headers')
        parser.add_argument('fund_id', type=str, required=True)
        req = parser.parse_args()
        token = req.get('token')
        fund_id = req.get('fund_id')
        username = verify_token(token)
        if username == None:
            return{
                'success': False,
                'message': 'token无效'}, 403
        fund_ref = db.collection('fund').document(fund_id)
        fund = fund_ref.get()
        if not fund.exists:
            return{
                'success': False,
                'message': '项目不存在'}, 403
        data = {
            'username': username,
            'fund_id':fund_id
        }
        subscribes = db.collection('subscribe').where(u'username', u'==', username).where(u'fund_id', u'==', fund_id).get()
        for subscribe in subscribes:
            if subscribe.to_dict()['fund_id'] == fund_id:
                return{
                        'success':False,
                        'message':'您已订阅该项目'
                    }, 403
        db.collection('subscribe').add(data)
        return{
            'success': True,
            'data': data}

class CancelSubscribeFund(Resource):
    def post(self):
        """
        @@@
        ## 取消订阅项目
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   | token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    fund_id    |    false    |    string   |    订阅的项目id   |

        ### return
        无data
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type=str,
                            required=True, location='headers')
        parser.add_argument('fund_id', type=str, required=True)
        req = parser.parse_args()
        token = req.get('token')
        fund_id = req.get('fund_id')
        username = verify_token(token)
        if username == None:
            return{
                'success': False,
                'message': 'token无效'}, 403
        subscribes = db.collection('subscribe').where(u'username', u'==', username).where(u'fund_id', u'==', fund_id).get()
        for subscribe in subscribes:
            db.collection('subscribe').document(subscribe.id).delete()
            return{
                'success':True,
                'message':'取消订阅成功'
            }
        return{
            'success':False,
            'message':'您未订阅该项目'
        }, 403
    
class ShowSubscribeFund(Resource):
    def post(self):
        """
        @@@
        ## 显示订阅的项目
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   | token  |

        ### return
        data 订阅的项目
        @@@
        """
        print("显示订阅的项目")
        parser = RequestParser()
        parser.add_argument('token', type = str, required = True, location = 'headers')
        req = parser.parse_args()
        token = req.get('token')
        username = verify_token(token)
        if username == None:
            return{
                'success':False,
                'message':'token无效'
            }, 403
        fund_ids = []
        ref = db.collection('subscribe').where(u'username', u'==', username).get()
        for fund in ref:
            if 'fund_id' in fund.to_dict():
                fund_ids.append(fund.to_dict()['fund_id'])
        print(fund_ids)
        funds = []
        print(fund_ids)
        for fund_id in fund_ids:
            fund = db.collection('fund').document(fund_id).get()
            if fund.exists:
                fund = fund.to_dict()
                fund['id'] = fund_id
                author = db.collection('author').document(fund['author_id']).get().to_dict()
                author['id'] = fund['author_id']
                fund['author'] = author
                fund.pop('author_id')
                funds.append(fund)
        print(funds)
        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        return{
            'success': True,
            'data': funds
        }, 200

class FundIsSubscribed(Resource):
    def post(self):
        """
        @@@
        ## 是否订阅项目
        ### header args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    token    |    false    |    string   | token  |

        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    fund_id    |    false    |    string   |    订阅的项目id   |

        ### return
        是否订阅项目
        @@@
        """
        parser = RequestParser()
        parser.add_argument('token', type=str,
                            required=True, location='headers')
        parser.add_argument('fund_id', type=str, required=True)
        req = parser.parse_args()
        token = req.get('token')
        fund_id = req.get('fund_id')
        username = verify_token(token)
        if username == None:
            return{
                'success': False,
                'message': 'token无效'}
        fund_ref = db.collection('fund').document(fund_id)
        fund = fund_ref.get()
        if not fund.exists:
            return{
                'success': False,
                'message': '项目不存在'}
        subscribes = db.collection('subscribe').where(u'username', u'==', username).where(u'fund_id', u'==', fund_id).get()
        for subscribe in subscribes:
            if subscribe.to_dict()['fund_id'] == fund_id:
                return{
                        'success':True,
                        'message':'您已订阅该项目'
                    }
        return{
            'success': False,
            'data': '您未订阅该项目'}