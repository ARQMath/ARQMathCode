class Comment:
    def __init__(self, comment_id, related_post_id, text, score, user_id, creation_date):
        self.id = comment_id
        self.related_post_id = related_post_id
        self.text = text
        self.score = score
        self.user_id = user_id
        self.creation_date = creation_date
