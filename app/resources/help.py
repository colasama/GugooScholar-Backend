from flask_restful import Resource


class Help(Resource):
    def get(self):
        """
        @@@
        ### 文档说明：
        
        1. token字段应位于header；
        2. 在返回列表的结果中一次只返回20个结果，如果要获取更多结果，请使用偏移游标和偏移量；
        3. 偏移量（offset）：为整数，表示跳过的结果数量，如不传入则默认从0开始；
        4. 偏移游标（start_after): id，查询从该id处开始（不包括该文档），如不传入则从第一个文档开始；

        @@@
        """
        return {'message': "Hello Gugoo!"}