from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.common.util import db
from app.common.util import querycl
from app.common.util import desc

import json


def get_authors(authors: list):
    authors_ref = []
    for i in range(min(10, len(authors))):
        authors_ref.append(db.collection('author').document(authors[i]))
    authors_ref = db.get_all(authors_ref)
    authors_temp = {}
    for author in authors_ref:
        a_id = author.id
        author = author.to_dict()
        if author != None:
            author['id'] = a_id
        else:
            author = {'name': a_id}
        authors_temp[a_id] = author
    for i in range(min(10, len(authors))):
        authors[i] = authors_temp[authors[i]]


def get_venue(paper: dict):
    if 'venue' in paper and isinstance(paper['venue'], str):
        if paper['venue'].isalnum():
            venue = db.collection('venue').document(paper['venue']).get()
            if venue.exists:
                v_id = paper['venue']
                paper['venue'] = venue.to_dict()
                paper['venue']['id'] = v_id
            else:
                name = paper['venue']
                paper['venue'] = {'name': name}
        else:
            name = paper['venue']
            paper['venue'] = {'name': name}
    elif 'venue' in paper:
        paper.pop('venue')


class PaperByID(Resource):
    def get(self, paper_id):
        """
        @@@
        ## 根据ID获取论文
        ### args

        无

        ### return
        - #### data
        > | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |    id    |    false    |    string   |    id    |
        |    title    |    false    |    string   |   标题    |
        |    authors    |    false    |    list   |    作者列表    |
        |    abstract    |    false    |    string   |    摘要    |
        |    venue    |    ture    |    string   |    所属期刊/会议，ID/名称    |
        |    year    |    ture    |    int   |    发表年份    |
        |    n_citation    |    ture    |    int   |    被引量    |
        |    keywords    |    true    |    list   |    关键词    |
        |    doi    |    true    |    string   |    doi号    |
        |    lang    |    ture    |    string   |   语言   |
        |    page_start    |    ture    |    int   |        |
        |    page_end    |    ture    |    int   |        |
        |    volume    |    ture    |    string   |   所属卷数    |
        |    issue    |    ture    |    string   |    所属期数   |
        |    issn    |    ture    |    string   |        |
        |    isbn    |    ture    |    string   |        |
        |    pdf    |    ture    |    string   |    原文链接    |
        |    url    |    ture    |    list   |    相关链接    |

        注意作者列表中仅前十个为详细信息，之后的仅有作者id或姓名

        @@@
        """
        paper = db.collection('paper').document(paper_id).get()
        if paper.exists:
            paper = paper.to_dict()
            paper['id'] = paper_id
            get_venue(paper)
            get_authors(paper['authors'])
            return{
                'success': True,
                'data': paper}
        else:
            return{
                'success': False,
                'message': '论文不存在'}, 404


class PaperRank(Resource):
    def get(self):
        """
        @@@
        ## 获取排序的论文列表
        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    order_by   |    false    |    string   |   排序字段    |
        |    start_after   |    true    |    string   |    偏移游标    |

        排序字段可选：n_citation, year, id
        ### return
        - #### data
        >  | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    list   |    排好序的的论文列表    |
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
        papers = []
        if order_by == "id":
            ref = db.collection('paper')
        else:
            ref = db.collection('paper').order_by(order_by, direction=desc)
        start_after = db.collection('paper').document(start_after).get()
        if start_after.exists:
            ref = ref.start_after(start_after).limit(20).get()
        else:
            ref = ref.limit(20).get()
        for paper in ref:
            a_id = paper.id
            paper = paper.to_dict()
            paper['id'] = a_id
            get_venue(paper)
            get_authors(paper['authors'])
            papers.append(paper)
        return{
            'success': True,
            'data': papers
        }


class SearchPaper(Resource):
    def get(self):
        """
        @@@
        ## 搜索论文
        ### args

        | 参数名 | 是否可选 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |    words    |    false    |    string   |    检索关键词    |
        |    type    |    false    |    string   |    检索类别    |
        |    offset    |    true    |    int   |    偏移量    |

        type可选 title keywords abstract

        ### return
        - #### data
        >  | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    list   |    检索结果    |

        @@@
        """
        parser = RequestParser()
        parser.add_argument("words", type=str,
                            location="args", required=True)
        parser.add_argument("type", type=str,
                            location="args", required=True)
        parser.add_argument("offset", type=int,
                            location="args", required=False)
        req = parser.parse_args()
        words = req.get("words")
        search_type = req.get("type")
        search_db = ""
        offset = req.get("offset")
        if search_type == 'title':
            search_db = "paperT"
        elif search_type == 'keywords':
            search_db = 'paperK'
        elif search_type == 'abstract':
            search_db = 'paperA'
        else:
            return {
                'success': False,
                'message': '检索类型错误'}, 400
        if words == '' or words.isspace():
            return{'success': True,'data': []}
        paper_ids = querycl.query(
            search_db, search_type, terms=words, offset=offset, limit=20)
        papers_ref = []
        for id in paper_ids:
            paper = db.collection('paper').document(id)
            papers_ref.append(paper)
        papers_ref = db.get_all(papers_ref)
        papers = []
        for paper in papers_ref:
            if paper != None:
                p_id = paper.id
                paper = paper.to_dict()
                paper['id'] = p_id
                get_venue(paper)
                get_authors(paper['authors'])
                papers.append(paper)
        return{'success': True,'data': papers}


class PaperDoi(Resource):
    def get(self):
        """
        @@@
        ## 根据DOI获取论文
        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    doi    |    false    |    string   |    doi号    |

        ### return
        - #### data
        >  | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    list   |    一般情况只会有一个或0个    |
        @@@
        """
        parser = RequestParser()
        parser.add_argument("doi", type=str,
                            location="args", required=True)
        req = parser.parse_args()
        doi = req.get("doi")
        ref = db.collection('paper').where(
            u'doi', u'==', doi).limit(1).get()
        papers = []
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


class PaperVenue(Resource):
    def get(self):
        """
        @@@
        ## 根据出版物获取论文
        ### args

        | 参数名 | 是否可选 | type | remark |
        |--------|--------|--------|--------|
        |    venue    |    false    |    string   |    venue id    |
        |    start_after   |    true    |    string   |    偏移游标    |

        ### return
        - #### data
        >  | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    list   |    该出版物下属的论文    |
        @@@
        """
        parser = RequestParser()
        parser.add_argument("venue", type=str,
                            location="args", required=True)
        parser.add_argument("start_after", type=str,
                            location="args", required=False)
        req = parser.parse_args()
        venue = req.get("venue")
        start_after = req.get("start_after")
        ref = db.collection('paper').where(u'venue', u'==', venue)
        start_after = db.collection('paper').document(start_after).get()
        if start_after.exists:
            ref = ref.start_after(start_after).limit(20).get()
        else:
            ref = ref.limit(20).get()
        papers = []
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


class GetField(Resource):
    def get(self):
        """
        @@@
        ## 获取所有领域（其实就是一部分关键词）
        ### args

        无

        ### return
        - #### data
        >  | 字段 | 可能不存在 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |   \   |    false    |    list   |    所有领域    |
        @@@
        """
        fields = db.collection('field').document('all_field').get()
        if fields.exists:
            fields = fields.to_dict()
            fields = json.loads(fields['data'])
            return{
                'success': True,
                'data': fields}
