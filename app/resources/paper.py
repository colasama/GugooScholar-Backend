from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.common.util import db
from app.common.util import querycl
from app.common.util import desc


class PaperByID(Resource):
    def get(self,paper_id):
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
        |    authors    |    false    |    list   |    作者列表，ID/姓名    |
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
        @@@
        """
        paper = db.collection('paper').document(paper_id).get()
        if paper.exists:
            auhtor = paper.to_dict()
            auhtor['id'] = paper_id
            return{
                'success': True,
                'data': paper.to_dict()}
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

        排序字段可选：n_citation，year，id
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
            ref = ref.start_after(start_after).limit(20).stream()
        else:
            ref = ref.limit(20).stream()
        for paper in ref:
            a_id = paper.id
            paper = paper.to_dict()
            paper['id'] = a_id
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
        if search_type == 'title' :
            search_db = "paperT"
        elif search_type == 'keywords':
            search_db = 'paperK'
        elif search_type == 'abstract':
            search_db = 'paperA'
        else:
            return {
                'success': False,
                'message': '检索类型错误'}, 400
        paper_ids = querycl.query(
            search_db, search_type, terms=words, offset=offset, limit=20)
        papers = []
        for id in paper_ids:
            paper = db.collection('paper').document(id).get().to_dict()
            papers['id'] = id
            papers.append(paper)
        return{'data': papers}
