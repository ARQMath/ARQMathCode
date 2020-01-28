import codecs
from bs4 import BeautifulSoup

from Entities.PostHistory import PostHistory


class PostHistoryParser:
    """
    This class reads the post history file. It reads the whole file into the memory.
    """
    def __init__(self, xml_post_history_file_path):
        with codecs.open(xml_post_history_file_path, "r", "utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
        all_post = soup.find_all("row")
        self.map_of_edits = {}
        for post in all_post:
            attr_dic = post.attrs
            history_id = int(attr_dic["id"])
            post_id = int(attr_dic["postid"])
            post_history_type_id = None
            revision_guid = None
            user_display_name = None
            text = None
            creation_date = None
            comment = None
            user_id = None
            close_reason_id = None
            if "revisionguid" in attr_dic:
                revision_guid = attr_dic["revisionguid"]
            if "posthistorytypeid" in attr_dic:
                post_history_type_id = int(attr_dic["posthistorytypeid"])
            if "comment" in attr_dic:
                comment = (attr_dic["comment"])
            if "userdisplayname" in attr_dic:
                user_display_name = (attr_dic["userdisplayname"])
            if "closereasonid" in attr_dic:
                close_reason_id = int(attr_dic["closereasonid"])
            if "userid" in attr_dic:
                user_id = int(attr_dic["userid"])
            if "creationdate" in attr_dic:
                creation_date = (attr_dic["creationdate"])
            if "text" in attr_dic:
                text = (attr_dic["text"])
            post_history = PostHistory(history_id, post_id, post_history_type_id, revision_guid, creation_date,
                                       user_id, user_display_name, comment, text, close_reason_id)
            if post_id in self.map_of_edits:
                self.map_of_edits[post_id].append(post_history)
            else:
                self.map_of_edits[post_id] = [post_history]
