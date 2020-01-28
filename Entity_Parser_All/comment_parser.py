import codecs
from bs4 import BeautifulSoup

from Entities.Comment import Comment


class CommentParser:
    """
    This class is used for reading the comment file. It reads the whole file into the memory.
    """
    def __init__(self, xml_comment_file_path):
        with codecs.open(xml_comment_file_path, "r", "utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
        all_post = soup.find_all("row")
        self.map_of_comments_for_post = {}
        for post in all_post:
            attr_dic = post.attrs
            comment_id = int(attr_dic["id"])
            post_id = int(attr_dic["postid"])
            text = (attr_dic["text"])
            creation_date = None
            score = None
            user_id = None

            if "score" in attr_dic:
                score = int(attr_dic["score"])
            if "userid" in attr_dic:
                user_id = int(attr_dic["userid"])
            if "creationdate" in attr_dic:
                creation_date = (attr_dic["creationdate"])

            comment = Comment(comment_id, post_id, text, score, user_id, creation_date)
            if post_id in self.map_of_comments_for_post:
                self.map_of_comments_for_post[post_id].append(comment)
            else:
                self.map_of_comments_for_post[post_id] = [comment]
