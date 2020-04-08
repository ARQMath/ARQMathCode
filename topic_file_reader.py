import xml.etree.ElementTree as ET


class Topic:
    """
    This class shows a topic for task 1. Each topic has an topic_id which is str, a title and question which
    is the question body and a list of tags.
    """

    def __init__(self, topic_id, title, question, tags):
        self.topic_id = topic_id
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
        self.__map_topics = self.__read_topics(topic_file_path)

    def __read_topics(self, topic_file_path):
        map_topics = {}
        tree = ET.parse(topic_file_path)
        root = tree.getroot()
        for child in root:
            topic_id = child.attrib['number']
            title = child[0].text
            question = child[1].text
            lst_tag = child[2].text.split(",")
            map_topics[topic_id] = Topic(topic_id, title, question, lst_tag)
        return map_topics

    def get_topic(self, topic_id):
        if topic_id in self.__map_topics:
            return self.__map_topics[topic_id]
        return None


"In this example, the title and the question body of topic with id A.1 is printed."
topic_file_path = "Topics_V2.0.xml"
topic_reader = TopicReader(topic_file_path)
topic_id = "A.1"
print(topic_reader.get_topic(topic_id).title)
print(topic_reader.get_topic(topic_id).question)
print(topic_reader.get_topic(topic_id).lst_tags)
