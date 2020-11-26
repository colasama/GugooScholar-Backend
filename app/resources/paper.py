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
        |    keywords    |    true    |    list   |    关键词    |
        |    doi    |    true    |    string   |    doi号    |
        |    lang    |    ture    |    string   |   语言   |
        |    page_start    |    ture    |    int   |        |
        |    page_end    |    ture    |    int   |        |
        |    volume    |    ture    |    string   |        |
        |    issue    |    ture    |    string   |        |
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