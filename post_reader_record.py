import os
from Entity_Parser_Record.comment_parser_record import CommentParserRecord
from Entity_Parser_Record.post_link_parser_record import PostLinkParserRecord
from Entity_Parser_Record.post_parser_record import PostParserRecord
from Entity_Parser_Record.user_parser_record import UserParserRecord
from Entity_Parser_Record.vote_parser_record import VoteParserRecord
from Visualization.generate_html_file import HtmlGenerator
import argparse
from shutil import copyfile
import csv


class DataReaderRecord:
    """
        This is the data reader class for MSE ARQMath dataset.
        In the constructor, all the data is read and the related ones are linked together.
        We have provided several functions as examples of how to work with this data reader.
        Also if the participant will to generate the html file for a given thread (question), they can use the
        get_html_pages where they specify list of questions id for which they want to get the html.


        The main difference with the other DataReader is that each file is read record by record here.
    """

    def __init__(self, root_file_path, version=""):
        """
        This class read all the data file in MSE ARQMath Dataset. The root file of data is taken as the input
        and then each of the files are read and the related data are linked together.
        :param root_file_path: The root directory of MSE ARQMath Dataset.
        """
        post_file_path = root_file_path + "/Posts"+version+".xml"
        badges_file_path = root_file_path + "/Badges"+version+".xml"
        comments_file_path = root_file_path + "/Comments"+version+".xml"
        votes_file_path = root_file_path + "/Votes"+version+".xml"
        users_file_path = root_file_path + "/Users"+version+".xml"
        post_links_file_path = root_file_path + "/PostLinks"+version+".xml"
        #post_history_file_path = root_file_path + "/PostHistory.xml"

        print("reading users")
        self.user_parser = UserParserRecord(users_file_path, badges_file_path)
        self.post_history_parser = None  # post_history_file_path
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
                                            self.vote_parser.map_of_votes, self.user_parser.map_of_user,
                                            self.post_history_parser)

    def get_list_of_questions_posted_in_a_year(self, year):
        """
        :param year: the year for which we look for its questions
        :return: return all the questions posted in input year
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
        :param question_id: the question id for which we want the list of answers given to it
        :return: the list of answers given to question with specific id
        """
        if question_id not in self.post_parser.map_questions:
            return None
        return self.post_parser.map_questions[question_id].answers

    def get_user(self, user_id):
        """
        :param user_id: the id of user that we want its profile
        :return: return user profile of user with specif id
        """
        if user_id not in self.user_parser.map_of_user:
            return None
        return self.user_parser.map_of_user[user_id]

    def get_answers_posted_by_user(self, user_id):
        """
        :param user_id: user id for which we want the list of answers given by that user
        :return: a list of answers given by user with input id
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
        Return a list of questions with a specific tag
        :param tag: tag to find questions having it
        :return: list of questions with the input tag
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
        :param lst_of_questions_id: list of question to create their html views
        :param result_directory: directory to save html files
        """
        HtmlGenerator.questions_to_html(lst_of_questions_id, self, result_directory)

    def get_all_html_pages(self, result_directory):
        """
        :param lst_of_questions_id: list of question to create their html views
        :param result_directory: directory to save html files
        """
        dic_year = {}
        dic_year_month = {}
        dic_directories = self.create_all_htmls_directories(dic_year, dic_year_month, result_directory)
        for question_id in self.post_parser.map_questions:
            question = self.post_parser.map_questions[question_id]
            date_part = question.creation_date.split("T")[0].split("-")
            year = date_part[0]
            month = date_part[1]
            dir = dic_directories[year+"-"+month]
            HtmlGenerator.questions_to_html([question_id], self, dir)

    def create_all_htmls_directories(self, dic_year, dic_year_month, result_directory):
        dic_directories = {}
        for question_id in self.post_parser.map_questions:
            question = self.post_parser.map_questions[question_id]
            date_part = question.creation_date.split("T")[0].split("-")
            year = date_part[0]
            month = date_part[1]
            if year in dic_year:
                dic_year[year].append(int(question_id))
                if month in dic_year_month[year]:
                    dic_year_month[year][month].append(int(question_id))
                else:
                    dic_year_month[year][month] = [int(question_id)]
            else:
                dic_year[year] = [int(question_id)]
                dic_year_month[year] = {month: [int(question_id)]}
        if not os.path.exists(result_directory):
            os.makedirs(result_directory)
        copyfile("./Visualization/mse.svg", result_directory+"/mse.svg")
        copyfile("./Visualization/arqmath.png", result_directory + "/arqmath.png")
        for year in dic_year:
            temp = result_directory + "/" + str(min(dic_year[year])) + "_" + str(year)
            if not os.path.exists(temp):
                os.makedirs(temp)
            for month in dic_year_month[year]:
                temp2 = temp + "/" + str(min(dic_year_month[year][month])) + "_" + str(month)
                if not os.path.exists(temp2):
                    os.makedirs(temp2)
                dic_directories[year+"-"+month] = temp2
        return dic_directories


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
