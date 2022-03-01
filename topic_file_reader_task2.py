import csv
import xml.etree.ElementTree as ET

from Visualization.generate_html_file import HtmlGenerator


class Topic:
    """
    This class shows a topic for task 1. Each topic has an topic_id which is str, a title and question which
    is the question body and a list of tags.
    """

    def __init__(self, topic_id, formula_id, formula_latex, title, question, tags):
        self.topic_id = topic_id
        self.formula_id = formula_id
        self.formula_latex = formula_latex
        self.title = title
        self.question = question
        self.lst_tags = tags


class TopicReader:
    """
    This class takes in the topic file path and read all the topics into a map. The key in this map is the topic id
    and the values are Topic which has 4 attributes: id, title, question and list of tags for each topic.

    To see each topic, use the get_topic method, which takes the topic id and return the topic in Topic object and
    you have access to the 4 attributes mentioned above.
    """

    def __init__(self, topic_file_path):
        self.map_topics = self.__read_topics(topic_file_path)

    def __read_topics(self, topic_file_path):
        map_topics = {}
        tree = ET.parse(topic_file_path)
        root = tree.getroot()
        for child in root:
            topic_id = child.attrib['number']
            formula_id = child[0].text
            formula_latex = child[1].text
            title = child[2].text
            question = child[3].text
            tags = child[4].text.split(",")
            map_topics[topic_id] = Topic(topic_id, formula_id, formula_latex, title, question, tags)
        return map_topics

    def get_topic(self, topic_id):
        if topic_id in self.map_topics:
            return self.map_topics[topic_id]
        return None

# topic_id = "A.1"
# print(topic_reader.get_topic(topic_id).question)
# print(topic_reader.get_topic(topic_id).lst_tags)
