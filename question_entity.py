import codecs
from bs4 import BeautifulSoup


class QuestionParser:
    def __init__(self, question_html_file_path):
        """
        This class is used for reading the questions
        :param question_html_file_path: the html filepath of the question
        """
        with codecs.open(question_html_file_path, "r", "utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        # This field shows the title of question
        self.title = soup.find("title")

        # This field shows the html of question body
        self.question = soup.find("div", class_="post-text")

        # This field shows the raw text of question body
        self.question_raw_text = self.question.text


# Sample Usage
# qp = QuestionParser("../Sample_Topics_Task1/3163489.html")
# html_question(qp.question, 15)
