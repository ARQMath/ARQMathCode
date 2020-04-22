from xmlr import xmliter
from ..Entities.Post import Answer, Question


class PostParserRecord:
    """
        This class is used for reading the post file. It reads it record by record.
    """
    def __init__(self, xml_post_link_file_path, map_comments=None, map_related_post=None, map_duplicate_post=None,
                 map_votes=None, map_users=None):
        self.map_questions = {}
        self.map_answers = {}
        self.map_just_answers = {}
        for attr_dic in xmliter(xml_post_link_file_path, 'row'):
            post_id = int(attr_dic['@Id'])
            post_type_id = int(attr_dic['@PostTypeId'])
            creation_date = (attr_dic["@CreationDate"])
            body = (attr_dic["@Body"])
            view_count = None
            comment_count = None
            owner_user_id = None
            last_edit_date = None
            last_activity_date = None
            last_editor_user_id = None
            community_owned_date = None
            last_editor_display_name = None
            score = None
            user = None

            if "@ViewCount" in attr_dic:
                view_count = int(attr_dic["@ViewCount"])
            if "@Score" in attr_dic:
                score = int(attr_dic["@Score"])
            if "@CommentCount" in attr_dic:
                comment_count = int(attr_dic["@CommentCount"])
            if "@OwnerUserId" in attr_dic:
                owner_user_id = int(attr_dic["@OwnerUserId"])
                if map_users is not None and owner_user_id in map_users:
                    user = map_users[owner_user_id]
            if "@LastEditDate" in attr_dic:
                last_edit_date = (attr_dic["@LastEditDate"])
            if "@LastActivityDate" in attr_dic:
                last_activity_date = (attr_dic["@LastActivityDate"])
            if "@LastEditorUserId" in attr_dic:
                last_editor_user_id = int(attr_dic["@LastEditorUserId"])
            if "@CommunityOwnedDate" in attr_dic:
                community_owned_date = (attr_dic["@CommunityOwnedDate"])
            if "@LastEditorDisplayName" in attr_dic:
                last_editor_display_name = (attr_dic["@LastEditorDisplayName"])

            comment_list = None
            vote_list = None
            if map_comments is not None and post_id in map_comments:
                comment_list = map_comments[post_id]
            if map_votes is not None and post_id in map_votes:
                vote_list = map_votes[post_id]

            if post_type_id == 1:  # Question
                title = (attr_dic["@Title"])
                favourite_count = None
                closed_date = None
                accepted_answer_id = None
                related_post = []

                if map_related_post is not None and post_id in map_related_post:
                    for related_post_id in map_related_post[post_id]:
                        related_post.append((related_post_id, False))

                if map_duplicate_post is not None and post_id in map_duplicate_post:
                    for related_post_id in map_duplicate_post[post_id]:
                        related_post.append((related_post_id, True))

                if "@CommentCount" in attr_dic:
                    comment_count = int(attr_dic["@CommentCount"])
                if "@AnswerCount" in attr_dic:
                    answer_count = int(attr_dic["@AnswerCount"])
                if "@FavoriteCount" in attr_dic:
                    favourite_count = int(attr_dic["@FavoriteCount"])
                if "@AcceptedAnswerId" in attr_dic:
                    accepted_answer_id = int(attr_dic["@AcceptedAnswerId"])
                if "@ClosedDate" in attr_dic:
                    closed_date = (attr_dic["@ClosedDate"])
                if "@Tags" in attr_dic:
                    tags = (attr_dic["@Tags"]).split(">")
                    lst_tags = []
                    for i in range(0, len(tags) - 1):
                        tag = tags[i][1:]
                        lst_tags.append(tag)
                self.map_questions[post_id] = Question(post_id, creation_date, score, view_count, body, owner_user_id,
                                                       comment_count, last_edit_date, last_activity_date,
                                                       last_editor_user_id, community_owned_date,
                                                       last_editor_display_name, related_post, comment_list, vote_list,
                                                       user, title, lst_tags,
                                                       accepted_answer_id, answer_count, favourite_count, closed_date)

            elif post_type_id == 2:
                parent_id = int(attr_dic["@ParentId"])
                answer = Answer(post_id, creation_date, score, view_count, body, owner_user_id, comment_count,
                                last_edit_date, last_activity_date, last_editor_user_id, community_owned_date,
                                last_editor_display_name, parent_id, comment_list, vote_list, user)

                if parent_id in self.map_answers:
                    self.map_answers[parent_id].append(answer)
                else:
                    self.map_answers[parent_id] = [answer]
                self.map_just_answers[answer.post_id] = answer
        self.__set_answers()

    def __set_answers(self):
        for question_id in self.map_questions:
            if question_id in self.map_answers:
                self.map_questions[question_id].set_answers(self.map_answers[question_id])
