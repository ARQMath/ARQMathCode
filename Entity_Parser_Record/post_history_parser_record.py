from xmlr import xmliter
from Entities.PostHistory import PostHistory


class PostHistoryParserRecord:
    """
        This class is used for reading the post history file. It reads it record by record.
    """
    def __init__(self, xml_post_history_file_path):
        self.map_of_edits = {}
        for attr_dic in xmliter(xml_post_history_file_path, 'row'):
            history_id = int(attr_dic["@Id"])
            post_id = int(attr_dic["@PostId"])
            post_history_type_id = None
            revision_guid = None
            user_display_name = None
            text = None
            creation_date = None
            comment = None
            user_id = None
            close_reason_id = None
            if "@RevisionGUID" in attr_dic:
                revision_guid = attr_dic["@RevisionGUID"]
            if "@PostHistoryTypeId" in attr_dic:
                post_history_type_id = int(attr_dic["@PostHistoryTypeId"])
            if "@Comment" in attr_dic:
                comment = (attr_dic["@Comment"])
            if "@UserDisplayName" in attr_dic:
                user_display_name = (attr_dic["@UserDisplayName"])
            if "@CloseReasonId" in attr_dic:
                close_reason_id = int(attr_dic["@CloseReasonId"])
            if "@UserId" in attr_dic:
                user_id = int(attr_dic["@UserId"])
            if "@CreationDate" in attr_dic:
                creation_date = (attr_dic["@CreationDate"])
            if "@Text" in attr_dic:
                text = (attr_dic["@Text"])
            post_history = PostHistory(history_id, post_id, post_history_type_id, revision_guid, creation_date,
                                       user_id, user_display_name, comment, text, close_reason_id)
            if post_id in self.map_of_edits:
                self.map_of_edits[post_id].append(post_history)
            else:
                self.map_of_edits[post_id] = [post_history]
