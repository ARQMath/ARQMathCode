from .Entity_Parser_Record.comment_parser_record import CommentParserRecord
from .Entity_Parser_Record.post_link_parser_record import PostLinkParserRecord
from .Entity_Parser_Record.post_parser_record import PostParserRecord
from .Entity_Parser_Record.user_parser_record import UserParserRecord
from .Entity_Parser_Record.vote_parser_record import VoteParserRecord
from .Visualization.generate_html_file import HtmlGenerator
import argparse


class DataReaderRecord:
    """
        This is the data reader class for MSE ARQMath dataset.
        In the constructor, all the data is read and the related ones are linked together.
        We have provided several functions as examples of how to work with this data reader.
        Also if the participant will to generate the html file for a given thread (question), they can use the
        get_html_pages where they specify list of questions id for which they want to get the html.


        The main difference with the other DataReader is that each file is read record by record here.
    """

    def __init__(self, root_file_path):
        """
        This class read all the data file in MSE ARQMath Dataset. The root file of data is taken as the input
        and then each of the files are read and the related data are linked together.
        :param root_file_path: The root directory of MSE ARQMath Dataset.
        """
        post_file_path = root_file_path + "/Posts_V1_0.xml"
        badges_file_path = root_file_path + "/Badges.V1.0.xml"
        comments_file_path = root_file_path + "/Comments.V1.0.xml"
        votes_file_path = root_file_path + "/Votes.V1.0.xml"
        users_file_path = root_file_path + "/Users.V1.0.xml"
        post_links_file_path = root_file_path + "/PostLinks.V1.0.xml"

        print("reading users")
        self.user_parser = UserParserRecord(users_file_path, badges_file_path)
        print("reading comments")
        self.comment_parser = CommentParserRecord(comments_file_path)
        print("reading votes")
        self.vote_parser = VoteParserRecord(votes_file_path)
        print("reading post links")
        self.post_link_parser = PostLinkParserRecord(post_links_file_path)
        print("reading posts")
        self.post_parser = PostParserRecord(post_file_path, self.comment_parser.map_of_comments_for_post,
                                            self.post_link_parser.map_related_posts,
                                            self.post_link_parser.map_duplicate_posts,
                                            self.vote_parser.map_of_votes, self.user_parser.map_of_user)

    def get_list_of_questions_posted_in_a_year(self, year):
        """

        :param year:
        :return:
        """
        lst_of_question = []
        for question_id in self.post_parser.map_questions:
            question = self.post_parser.map_questions[question_id]
            if question.creation_date is None:
                continue
            creation_year = int(question.creation_date.split("T")[0].split("-")[0])
            if creation_year == year:
                lst_of_question.append(question)
        return lst_of_question

    def get_answers_for_question(self, question_id):
        """

        :param question_id:
        :return:
        """
        if question_id not in self.post_parser.map_questions:
            return None
        return self.post_parser.map_questions[question_id].answers

    def get_user(self, user_id):
        """

        :param user_id:
        :return:
        """
        if user_id not in self.user_parser.map_of_user:
            return None
        return self.user_parser.map_of_user[user_id]

    def get_answers_posted_by_user(self, user_id):
        """

        :param user_id:
        :return:
        """
        lst_of_answers = []
        for parent_id in self.post_parser.map_answers:
            lst_answer = self.post_parser.map_answers[parent_id]
            for answer in lst_answer:
                if answer.owner_user_id is not None:
                    if answer.owner_user_id == user_id:
                        lst_of_answers.append(answer)
        return lst_of_answers

    def get_question_of_tag(self, tag):
        """

        :param tag:
        :return:
        """
        lst_of_questions = []
        for question_id in self.post_parser.map_questions:
            question = self.post_parser.map_questions[question_id]
            lst_tags = question.tags
            if tag in lst_tags:
                lst_of_questions.append(tag)
        return lst_of_questions

    def get_html_pages(self, lst_of_questions_id, result_directory):
        """

        :param lst_of_questions_id:
        :param result_directory:
        :return:
        """
        HtmlGenerator.questions_to_html(lst_of_questions_id, self, result_directory)


def main():
    parser = argparse.ArgumentParser(description='By setting the file path for MSE ARQMath Dataset,'
                                                 'One can iterate read the related data and go through questions')
    parser.add_argument('-ds', type=str, help="File path for the MSE ARQMath Dataset.", required=True)

    args = vars(parser.parse_args())
    clef_home_directory_file_path = (args['ds'])
    dr = DataReaderRecord(clef_home_directory_file_path)
    lst_questions = dr.get_question_of_tag("calculus")
    lst_answers = dr.get_answers_posted_by_user(132)
    dr.get_html_pages([1, 5], "../html_files")


if __name__ == "__main__":
    main()
