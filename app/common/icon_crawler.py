import requests
import json
__url = 'https://apiv2.aminer.cn/magic?a=getPerson__personapi.get___'
__data = [
    {
        "action": "personapi.get",
        "parameters": {
            "ids": [
                "5444ce9cdabfae87074e88e6"
            ]
        },
        "schema": {
            "person": [
                "id",
                "name",
                "name_zh",
                "avatar",
                "num_view",
                "is_follow",
                "work",
                "hide",
                "nation",
                "language",
                "bind",
                "acm_citations",
                "links",
                "educations",
                "tags",
                "tags_zh",
                "num_view",
                "num_follow",
                "is_upvoted",
                "num_upvoted",
                "is_downvoted",
                "is_lock",
                {
                    "indices": [
                        "hindex",
                        "pubs",
                        "citations"
                    ]
                },
                {
                    "profile": [
                        "position",
                        "position_zh",
                        "affiliation",
                        "affiliation_zh",
                        "work",
                        "gender",
                        "lang",
                        "homepage",
                        "phone",
                        "email",
                        "fax",
                        "bio",
                        "bio_zh",
                        "edu",
                        "address",
                        "note",
                        "homepage",
                        "title",
                        "titles"
                    ]
                }
            ]
        }
    }
]

def get_avatar(author_id):

    __data[0]['parameters']['ids'][0] = author_id

    res = requests.post(__url, data=json.dumps(__data))

    data = json.loads(res.text)

    if not data['data'][0]['succeed']:
        return ''

    author_info = data['data'][0]['data'][0]
    avatar = author_info['avatar'] if 'avatar' in author_info else ''
    return avatar
