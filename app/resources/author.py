from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.common.util import db
from app.common.util import querycl
from app.common.util import desc


class SearchAuthor(Resource):
    def get(self):
        """
        @@@
        ### args

        | 参数名 | 是否可选 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |    words    |    false    |    string   |    检索关键词    |
        |    offset    |    true    |    int   |    偏移量    |

        ### return
        - #### data
        >  | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    list   |    检索得到作者    |

        @@@
        """
        parser = RequestParser()
        parser.add_argument("words", type=str,
                            location="args", required=True)
        parser.add_argument("offset", type=int,
                            location="args", required=False)
        req = parser.parse_args()
        words = req.get("words")
        offset = req.get("offset")
        author_ids = querycl.query(
            "author", "name", terms=words, offset=offset, limit=20)
        authors = []
        for id in author_ids:
            author = db.collection('author').document(id).get().to_dict()
            author['id'] = id
            authors.append(author)
        return{'data': authors}


class AuthorByID(Resource):
    def get(self, author_id):
        """
        @@@
        ### args

        无

        ### return
        - #### data
        > | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |    id    |    false    |    string   |    id    |
        |    name    |    false    |    string   |   姓名    |
        |    orgs    |    ture    |    string   |    所属机构    |
        |    h_index    |    true    |    int   |    H 指数    |
        |    n_pubs    |    ture    |    int   |    论文数（与论文数据库不完全匹配）    |
        |    n_citation    |    ture    |    int   |    被引量    |
        @@@
        """
        auhtor = db.collection('author').document(author_id).get()
        if auhtor.exists:
            auhtor = auhtor.to_dict()
            auhtor['id'] = author_id
            return{
                'success': True,
                'data': auhtor}
        else:
            return{
                'success': False,
                'message': '作者不存在'}, 404


class AuthorByOrg(Resource):
    def get(self):
        """
        @@@
        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    org    |    false    |    string   |    机构名称    |
        |    start_after    |    true    |    string   |    偏移游标    |

        ### return
        - #### data
        >  | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    list   |    属于该机构的作者    |
        @@@
        """
        parser = RequestParser()
        parser.add_argument("org", type=str,
                            location="args", required=True)
        parser.add_argument("start_after", type=str,
                            location="args", required=False)
        req = parser.parse_args()
        org = req.get("org")
        start_after = req.get("start_after")
        authors = []
        ref = db.collection('author').where(u'orgs', u'==', org)
        start_after = db.collection('author').document(start_after).get()
        if start_after.exists:
            ref = ref.start_after(start_after).limit(20).stream()
        else:
            ref = ref.limit(20).stream()
        for author in ref:
            a_id = author.id
            author = author.to_dict()
            author['id'] = a_id
            authors.append(author)
        return{
            'success': True,
            'data': authors
        }


class AuthorRank(Resource):
    def get(self):
        """
        @@@
        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    order_by   |    false    |    string   |   排序字段    |
        |    start_after   |    true    |    string   |    偏移游标    |
        
        排序字段可选：h_index，n_pubs，n_citation, id，orgs(一般不用)
        ### return
        - #### data
        >  | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    list   |    按照H指数排序的作者列表    |
        @@@
        """
        parser = RequestParser()
        parser.add_argument("order_by", type=str,
                            location="args", required=True)
        parser.add_argument("start_after", type=str,
                            location="args", required=False)
        req = parser.parse_args()
        order_by = req.get("order_by")
        start_after = req.get("start_after")
        authors = []
        if order_by == "id":
            ref = db.collection('author')
        else:
            ref = db.collection('author').order_by(order_by, direction=desc)
        start_after = db.collection('author').document(start_after).get()
        if start_after.exists:
            ref = ref.start_after(start_after).limit(20).stream()
        else:
            ref = ref.limit(20).stream()
        for author in ref:
            a_id = author.id
            author = author.to_dict()
            author['id'] = a_id
            authors.append(author)
        return{
            'success': True,
            'data': authors
        }
