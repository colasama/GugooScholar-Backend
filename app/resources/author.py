from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from google import auth

from app.common.util import db
from app.common.util import querycl
from app.common.util import desc
from app.common.icon_crawler import get_avatar
from app.resources.paper import get_authors, get_venue


class SearchAuthor(Resource):
    def get(self):
        """
        @@@
        # 搜索作者
        # args

        | 参数名 | 是否可选 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |    words    |    false    |    string   |    检索关键词    |
        |    offset    |    true    |    int   |    偏移量    |

        # return
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
        if words == '' or words.isspace():
            return{'success': True, 'data': []}
        offset = req.get("offset")
        author_ids = querycl.query(
            "author", "name", terms=words, offset=offset, limit=20)
        authors_ref = []
        for id in author_ids:
            author = db.collection('author').document(id)
            authors_ref.append(author)
        authors_ref = db.get_all(authors_ref)
        authors = []
        for author in authors_ref:
            id = author.id
            author = author.to_dict()
            author['id'] = id
            authors.append(author)
        return{'success': True, 'data': authors}


class AuthorByID(Resource):
    def get(self, author_id):
        """
        @@@
        # 根据ID获取作者
        # args

        无

        # return
        - #### data
        > | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |    id    |    false    |    string   |    id    |
        |    name    |    false    |    string   |   姓名    |
        |    orgs    |    ture    |    string   |    所属机构    |
        |    h_index    |    true    |    int   |    H 指数    |
        |    n_pubs    |    ture    |    int   |    论文数（与论文数据库不完全匹配）    |
        |    n_citation    |    ture    |    int   |    被引量    |
        |    avatar    |    ture    |    str   |    头像链接    |
        @@@
        """
        auhtor = db.collection('author').document(author_id).get()
        if auhtor.exists:
            auhtor = auhtor.to_dict()
            auhtor['id'] = author_id
            auhtor['avatar'] = get_avatar(author_id)
            return{
                'success': True,
                'data': auhtor}
        else:
            return{
                'success': False,
                'message': '作者不存在'}, 404


class AuthorAvatar(Resource):
    def get(self, author_id):
        """
        @@@
        # 根据ID实时爬取作者头像
        # args

        无

        # return
        - #### data
        > | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |    avatar    |    ture    |    str   |    头像链接    |
        @@@
        """
        data = {}
        data['avatar'] = get_avatar(author_id)
        return{
            'success': True,
            'data': data}


class AuthorDoc(Resource):
    def get(self, author_id):
        """
        @@@
        # 获取该作者的论文
        # args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    start_after   |    true    |    string   |    偏移游标    |


        # return
        - #### data
        >  | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    list   |        |
        @@@
        """
        parser = RequestParser()
        parser.add_argument("start_after", type=str,
                            location="args", required=False)
        req = parser.parse_args()
        start_after = req.get("start_after")
        ref = db.collection('paper').where(
            u'authors', u'array_contains', author_id)
        papers = []
        start_after = db.collection('paper').document(start_after).get()
        if start_after.exists:
            ref = ref.start_after(start_after).limit(20).get()
        else:
            ref = ref.limit(20).get()
        for paper in ref:
            p_id = paper.id
            paper = paper.to_dict()
            paper['id'] = p_id
            get_venue(paper)
            get_authors(paper['authors'])
            papers.append(paper)
        return{
            'success': True,
            'data': papers
        }


class AuthorFund(Resource):
    def get(self, author_id):
        """
        @@@
        # 获取该作者的项目
        # args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    start_after   |    true    |    string   |    偏移游标    |


        # return
        - #### data
        >  | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    list   |        |
        @@@
        """
        parser = RequestParser()
        parser.add_argument("start_after", type=str,
                            location="args", required=False)
        req = parser.parse_args()
        start_after = req.get("start_after")
        ref = db.collection('fund').where(
            u'author_id', u'==', author_id)
        funds = []
        start_after = db.collection('fund').document(start_after).get()
        if start_after.exists:
            ref = ref.start_after(start_after).limit(20).get()
        else:
            ref = ref.limit(20).get()
        for fund in ref:
            p_id = fund.id
            fund = fund.to_dict()
            fund['id'] = p_id
            author = db.collection('author').document(
                fund['author_id']).get().to_dict()
            author['id'] = fund['author_id']
            fund['author'] = author
            fund.pop('author_id')
            funds.append(fund)
        return{
            'success': True,
            'data': funds
        }


class AuthorByOrg(Resource):
    def get(self):
        """
        @@@
        # 根据机构获取作者
        # args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    org    |    false    |    string   |    机构名称    |
        |    start_after    |    true    |    string   |    偏移游标    |

        # return
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
            ref = ref.start_after(start_after).limit(20).get()
        else:
            ref = ref.limit(20).get()
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
        # 获取排序的作者列表
        # args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    order_by   |    false    |    string   |   排序字段    |
        |    start_after   |    true    |    string   |    偏移游标    |

        排序字段可选：h_index，n_pubs，n_citation, id，orgs(一般不用)
        # return
        - #### data
        >  | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    list   |    排好序的的作者列表    |
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
            ref = ref.start_after(start_after).limit(20).get()
        else:
            ref = ref.limit(20).get()
        for author in ref:
            a_id = author.id
            author = author.to_dict()
            author['id'] = a_id
            authors.append(author)
        return{
            'success': True,
            'data': authors
        }


class AuthorRelation(Resource):
    def get(self, author_id):
        """
        @@@
        # 根据ID获取作者关系图谱
        # args

        无

        # return
        - #### data
        > | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    列表   |    有合作关系的作者，仅保留前20位    |

        相比与一般的作者数据，返回地数据中增加了weight，表示合作篇数
        @@@
        """
        ref = db.collection('paper').where(
            u'authors', u'array_contains', author_id)
        weight = {}
        ref = ref.limit(100).get()
        for paper in ref:
            paper = paper.to_dict()
            authors = paper['authors']
            for author in authors:
                if author == author_id:
                    continue
                if author in weight:
                    weight[author] += 1
                else:
                    weight[author] = 1
        weight = sorted(weight.items(), key=lambda x: x[1], reverse=True)
        auhtors = []
        for author in weight[0:10]:
            doc = db.collection('author').document(author[0]).get()
            if doc.exists:
                doc = doc.to_dict()
                doc['id'] = author[0]
                doc['weight'] = author[1]
            else:
                doc = {
                    'name': author[0],
                    'weight': author[1],
                }
            auhtors.append(doc)
        return{
            'success': True,
            'data': auhtors,
        }


class FieldAuthor(Resource):
    def get(self, field):
        """
        @@@
        # 根据领域获取作者（该接口最多返回前40个作者）
        # args

        无（url传参）

        # return
        - #### data
        >  | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    list   |    属于该领域的作者    |
        @@@
        """
        paper_ids = querycl.query(
            'paperK', 'keywords', terms=field, limit=40)
        authors_ref = []
        papers_ref = []
        for id in paper_ids:
            papers_ref.append(db.collection('paper').document(id))
        papers_ref = db.get_all(papers_ref)
        for paper in papers_ref:
            paper = paper.to_dict()
            if 'authors' in paper and len(paper['authors']) > 0:
                authors_ref.append(db.collection('author').document(paper['authors'][0]))
        authors_ref = db.get_all(authors_ref)
        authors = []
        for author in authors_ref:
            a_id = author.id
            author = author.to_dict()
            if author != None:
                author['id'] = a_id
                authors.append(author)
        return{
            'success': True,
            'data': authors,
        }
