from xmlr import xmliter
from ..Entities.Vote import Vote


class VoteParserRecord:
    """
        This class is used for reading the vote file. It reads it record by record.
    """
    def __init__(self, xml_vote_file_path):
        self.map_of_votes = {}
        for attr_dic in xmliter(xml_vote_file_path, 'row'):
            id = int(attr_dic["@Id"])
            post_id = int(attr_dic["@PostId"])
            vote_type_id = int(attr_dic["@VoteTypeId"])
            user_id = None
            bounty_amount = None
            creation_date = None
            if "@UserId" in attr_dic:
                user_id = int(attr_dic["@UserId"])
            if "@BountyAmount" in attr_dic:
                bounty_amount = int(attr_dic["@BountyAmount"])
            if "@CreationDate" in attr_dic:
                creation_date = attr_dic["@CreationDate"]
            vote = Vote(id, post_id, vote_type_id, user_id, creation_date, bounty_amount)
            if post_id in self.map_of_votes:
                self.map_of_votes[post_id].append(vote)
            else:
                self.map_of_votes[post_id] = [vote]
