from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.common.util import db
from app.common.util import querycl


class FundByID(Resource):
    def get(self, fund_id):
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
        |    author    |    false    |    json   |    项目作者    |
        |    abstract    |    false    |    string   |    摘要    |
        |    desc    |    ture    |    string   |    描述    |
        |    start_year    |    ture    |    int   |    开始年份    |
        |    end_year    |    ture    |    int   |    结束年份    |
        |    end_date    |    ture    |    string   |    结束日期    |
        |    src    |    ture    |    string   |    数据来源    |
        |    type    |    ture    |    string   |    项目类型    |
        @@@
        """
        fund = db.collection('fund').document(fund_id).get()
        if fund.exists:
            fund = fund.to_dict()
            fund['id'] = fund_id
            author = db.collection('author').document(fund['author_id']).get().to_dict()
            author['id'] = fund['author_id']
            fund['author'] = author
            fund.pop('author_id')
            return{
                'success': True,
                'data': fund}
        else:
            return{
                'success': False,
                'message': '项目不存在'}, 404


class Searchfund(Resource):
    def get(self):
        """
        @@@
        ## 搜索项目
        ### args

        | 参数名 | 是否可选 | 类型 | 备注 |
        |--------|--------|--------|--------|
        |    words    |    false    |    string   |    检索关键词    |
        |    type    |    false    |    string   |    检索类别    |
        |    offset    |    true    |    int   |    偏移量    |

        type可选 title desc abstract

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
        search_db = "fund"
        offset = req.get("offset")
        if search_type not in ['title','desc','abstract']:
            return {
                'success': False,
                'message': '检索类型错误'}, 400
        fund_ids = querycl.query(
            search_db, search_type, terms=words, offset=offset, limit=20)
        funds_ref = []
        for id in fund_ids:
            fund = db.collection('fund').document(id)
            funds_ref.append(fund)
        funds_ref = db.get_all(funds_ref)
        funds = []
        for fund in funds_ref:
            if fund != None:
                id = fund.id
                fund = fund.to_dict()
                fund['id'] = id
                author = db.collection('author').document(fund['author_id']).get().to_dict()
                author['id'] = fund['author_id']
                fund['author'] = author
                fund.pop('author_id')
                funds.append(fund)
        return{'data': funds}
