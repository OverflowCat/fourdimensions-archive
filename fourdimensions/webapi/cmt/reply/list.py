from itertools import count
import json
import logging
import requests
from typing import List

from fourdimensions.webapi.const import DEFAULT_HEADER

# 参考格式 https://bcy.net/apiv3/cmt/reply/list?page=1&item_id=()&limit=15&sort=hot


class reply_list:

    class PageOutOfRangeError(Exception):
        pass
    class NoCommentError(Exception):
        pass

    @staticmethod
    def get(item_id: int, page: int=1, limit:int =15, sort:str ='time', sess: requests.Session = None):
        """ query https://bcy.net/apiv3/cmt/reply/list
        
        Args:
            item_id: 需要爬取评论的主楼/动态本身的编号
            page: 评论页码
            limit: 每页最大评论数量（还没试过最大能到多少）
            sort: 排序方式，可选 time/hot (时间/热度)
        
        Returns:
            r.json()

        Raises:
            reply_list.NoCommentError: 该动态没有评论 （当 page == 1 且没有评论时）
            reply_list.PageOutOfRangeError: 评论页码超出范围 （当 page > 1 且该页没有评论时）

        """

        assert sort in ['time', 'hot']

        url = "https://bcy.net/apiv3/cmt/reply/list"
        params = {
            "page": page,
            "item_id": item_id,
            "limit": limit,
            "sort": sort
        }
        r = sess.get(url,params=params)
        r.raise_for_status()

        response_json: dict = r.json()
        assert response_json.get('code') == 0, response_json.get('msg')
        if response_json.get('data', {}).get('data'):
            return response_json
        
        if page == 1:
            logging.info(f"该 item 没有评论: {r.text}")
            raise reply_list.NoCommentError("该 item 没有评论")
        
        logging.info(f"页码超出范围: {r.text}")
        raise reply_list.PageOutOfRangeError("页码超出范围")
        


if __name__ == "__main__":
    sess = requests.session()
    sess.headers.update(DEFAULT_HEADER)
    try:
        reply = reply_list.get(7240818866773826618, sess=sess, page=1)
    except reply_list.NoCommentError:
        print("该 item 没有评论")
    else:
        with open(__file__.replace(__file__.split("/")[-1], "reply_list-demo.json"), "w", encoding="utf-8") as f:
            json.dump(reply, f, indent=4, ensure_ascii=False)
    
    def loop_demo():
        sess = requests.session()
        sess.headers.update(DEFAULT_HEADER)
        replies: List[dict] = []
        for page in count(1):
            try:
                logging.info(f"正在爬取第 {page} 页评论")
                reply = reply_list.get(7240818866773826618, sess=sess, page=page)
                replies.append(reply)
            except reply_list.NoCommentError:
                pass
            except reply_list.PageOutOfRangeError:
                logging.info("评论爬取完毕")
                break
        
        return replies
    
    replies = loop_demo()