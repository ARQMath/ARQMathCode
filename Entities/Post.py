class Post:
    def __init__(self, post_id, creation_date, score, view_count, body, owner_user_id, comment_count,
                 last_edit_date, last_activity_date, last_editor_user_id, community_owned_date, last_editor_display_name
                 , comments, votes, revisions, user):
        self.post_id = post_id
        self.post_type = 0
        self.creation_date = creation_date
        self.score = score
        self.view_count = view_count
        self.creation_date = creation_date
        self.body = body
        self.owner_user_id = owner_user_id
        self.comment_count = comment_count
        self.last_edit_date = last_edit_date
        self.last_activity_date = last_activity_date
        self.last_editor_user_id = last_editor_user_id
        self.community_owned_date = community_owned_date
        self.last_editor_display_name = last_editor_display_name
        self.comments = comments
        self.votes = votes
        self.revisions = revisions
        self.user = user


class Answer(Post):
    """
    Each answer is a post, with a parent id which shows the id of the question it belongs to.
    All the answers have the post_type of two.
    """
    def __init__(self, post_id, creation_date, score, view_count, body, owner_user_id, comment_count, last_edit_date,
                 last_activity_date, last_editor_user_id, community_owned_date, last_editor_display_name, parent_id,
                 comments, votes, revisions, user):
        Post.__init__(self, post_id, creation_date, score, view_count, body, owner_user_id, comment_count,
                      last_edit_date, last_activity_date, last_editor_user_id, community_owned_date,
                      last_editor_display_name, comments, votes, revisions, user)
        self.post_type = 2
        self.parent_id = parent_id


class Question(Post):
    """
    Each question is a post, with list of posssible answers (if there are any). All the questions have post type of 1.
    There is a title for each question and set of tags. The other attributes can be None if they don't exist.
    """
    def __init__(self, post_id, creation_date, score, view_count, body, owner_user_id, comment_count,
                 last_edit_date, last_activity_date, last_editor_user_id, community_owned_date,
                 last_editor_display_name, related_post, comments, votes, revisions, user, title, tags,
                 accepted_answer_id, answer_count, favourite_count, closed_date):
        Post.__init__(self, post_id, creation_date, score, view_count, body, owner_user_id, comment_count,
                      last_edit_date, last_activity_date, last_editor_user_id, community_owned_date,
                      last_editor_display_name, comments, votes, revisions, user)

        self.related_post = related_post
        self.post_type = 1
        self.title = title
        self.tags = tags
        self.accepted_answer_id = accepted_answer_id
        self.answer_count = answer_count
        self.favourite_count = favourite_count
        self.closed_date = closed_date
        self.answers = None

    def set_answers(self, answers):
        answers.sort(key=lambda x: x.score, reverse=True)
        if self.accepted_answer_id is not None:
            res = [i if self.accepted_answer_id == x.post_id else -1 for i, x in enumerate(answers)][0]
            answers.insert(0, answers.pop(res))
        self.answers = answers
