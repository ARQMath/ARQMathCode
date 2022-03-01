import html
import os
import sys

import argparse
from shutil import copyfile

conf_path = os.getcwd()
sys.path.append(conf_path)
from Visualization.generate_html_file import HtmlGenerator
from topic_file_reader import TopicReader
import topic_file_reader_task2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tx1', type=str, help='topic xml file for task 1')
    parser.add_argument('-hd1', type=str, help='html directory result for task 1')
    parser.add_argument('-tx2', type=str, help='topic xml file for task 2')
    parser.add_argument('-hd2', type=str, help='html directory result for task 2')
    args = vars(parser.parse_args())
    topic_xml_file_1 = args['tx1']
    html_directory_1 = args['hd1']
    topic_xml_file_2 = args['tx2']
    html_directory_2 = args['hd2']

    topic_reader = TopicReader(topic_xml_file_1)
    if not os.path.exists(html_directory_1):
        os.makedirs(html_directory_1)
    copyfile("Visualization/mse.svg", html_directory_1 + "/mse.svg")
    copyfile("Visualization/arqmath.png", html_directory_1 + "/arqmath.png")

    for topic_id in topic_reader.map_topics:
        title = topic_reader.map_topics[topic_id].title
        question_body = topic_reader.map_topics[topic_id].question
        lst_tags = topic_reader.map_topics[topic_id].lst_tags
        HtmlGenerator.task1_html_view(topic_id, title, question_body, lst_tags, html_directory_1)

    if not os.path.exists(html_directory_2):
        os.makedirs(html_directory_2)
    copyfile("Visualization/mse.svg", html_directory_2 + "/mse.svg")
    copyfile("Visualization/arqmath.png", html_directory_2 + "/arqmath.png")
    topic_reader = topic_file_reader_task2.TopicReader(topic_xml_file_2)
    for topic_id in topic_reader.map_topics:
        topic = topic_reader.map_topics[topic_id]
        formula_id = topic.formula_id
        title = topic_reader.get_topic(topic_id).title
        question = topic_reader.get_topic(topic_id).question
        title = html.unescape(title)
        question = html.unescape(question)
        tag_list = topic_reader.get_topic(topic_id).lst_tags
        HtmlGenerator.task2_html_view(topic_id, title, question, formula_id, tag_list, html_directory_2)


if __name__ == '__main__':
    main()
