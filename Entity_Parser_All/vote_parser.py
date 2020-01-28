import codecs
from bs4 import BeautifulSoup

from Entities.Vote import Vote


class VoteParser:
    """
        This class reads the vote file. It reads the whole file into the memory.
    """
    def __init__(self, xml_vote_file_path):
        with codecs.open(xml_vote_file_path, "r", "utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
        all_post = soup.find_all("row")
        self.map_of_votes = {}
        for post in all_post:
            attr_dic = post.attrs
            id = int(attr_dic["id"])
            post_id = int(attr_dic["postid"])
            vote_type_id = int(attr_dic["votetypeid"])
            user_id = None
            bounty_amount = None
            creation_date = None
            if "userid" in attr_dic:
                user_id = int(attr_dic["userid"])
            if "bountyamount" in attr_dic:
                bounty_amount = int(attr_dic["bountyamount"])
            if "creationdate" in attr_dic:
                creation_date = attr_dic["creationdate"]
            vote = Vote(id, post_id, vote_type_id, user_id, creation_date, bounty_amount)
            if post_id in self.map_of_votes:
                self.map_of_votes[post_id].append(vote)
            else:
                self.map_of_votes[post_id] = [vote]
