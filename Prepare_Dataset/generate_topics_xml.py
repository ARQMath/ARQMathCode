import csv
import html
import xml.etree.cElementTree as ET
from xml.dom import minidom
import os
import sys

conf_path = os.getcwd()
sys.path.append(conf_path)
import argparse
from bs4 import BeautifulSoup
from Entity_Parser_Record.post_parser_record import PostParserRecord
from Prepare_Dataset.extract_formulas_collection import get_list_of_formulas
from Prepare_Dataset.generate_post_xml import match_to_pattern
from topic_file_reader import TopicReader
from Prepare_Dataset.LaTeXML.latexml_conversions_topics import converting_latex_topics


def read_question_id_file(file_path):
    """
    Reads the list of question ids that are selected as candidates for Task 1
    """
    with open(file_path) as f:
        lst_question_ids = [int(line.rstrip('\n')) for line in f]
    return lst_question_ids


def read_topic_formulas(formula_file_path):
    """
    Read the TSV files created for Topics
    """
    dic_topic_question_id = {}
    dic_question_id_formulas = {}
    with open(formula_file_path, mode='r', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        next(csv_reader)
        for row in csv_reader:
            formula_id = (row[0])
            topic_id = row[1]
            question_id = row[2]
            doc_type = row[3]
            formula = row[4]
            dic_topic_question_id[topic_id] = question_id

            if topic_id in dic_question_id_formulas:
                dic_question_id_formulas[topic_id][formula_id] = (formula, doc_type)
            else:
                dic_question_id_formulas[topic_id] = {formula_id: (formula, doc_type)}
    return dic_topic_question_id, dic_question_id_formulas


def annotate_formulas(text, dic_formula_id_latex):
    text = text.replace("\r", "\n", text.count("\r"))
    "Iteration on the formulas in the current text"

    soreted_formula_ids = sorted(dic_formula_id_latex, key=lambda k: len(dic_formula_id_latex[k]), reverse=True)
    replacing_dic = {}
    for formula_id in soreted_formula_ids:
        """
            the formula should be located in the same type of text, why we have this?
            the title and question have the same ids, so if the formula is in both title and question,
            we do not know which one to replace (replace the original formula with the math-container tag one)
        """
        "the original formula"
        formula = dic_formula_id_latex[formula_id]

        "the string that will be replaced by the original formula, it has math-container tag and formula id"
        to_write_string = "<span class=\"math-container\" id=\"q_" + str(formula_id) + "\">"  # + formula + "</span>"

        map_index = match_to_pattern(formula, text)

        sorted_x = sorted(map_index.items(), key=lambda kv: kv[1])
        for item in sorted_x:
            if item[1] != -1:
                detected_formula = item[0]
                soup = BeautifulSoup(detected_formula, "lxml")
                temp_text = str(soup.text)
                if not temp_text.startswith("$"):
                    temp_text = "$" + temp_text + "$"
                fake_string = "FXXF_" + str(formula_id)
                replacing_dic[fake_string] = to_write_string + temp_text + "</span>"
                text = text.replace(detected_formula, fake_string, 1)
                break
    for fake_string in replacing_dic:
        text = text.replace(fake_string, replacing_dic[fake_string], 1)
    return text


def get_formula_id(dic_latex_location, latex, location):
    for key in dic_latex_location:
        t_latex, t_location = dic_latex_location[key]
        t_latex = t_latex.replace(" ", "")
        t_latex = t_latex.replace("\n", " ")
        latex = latex.replace(" ", "")
        latex = latex.replace("\n", " ")
        if (t_latex, t_location) == (latex, location):
            return key
    raise ValueError('Formula not found')


def read_candidate_formulas(formula_file_path):
    """
    Reads the candidate formulas selected for Task 2
    """
    dic_res = {}
    with open(formula_file_path, mode='r', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        next(csv_reader)
        for row in csv_reader:
            question_id = row[0]
            formula_latex = row[1]
            location = row[2]
            dic_res[question_id] = (formula_latex, location)
    return dic_res


def create_topic_files_2(topic_reader, dic_candidates_question_id_latex, dic_topic_question_id,
                         dic_question_id_formulas, xml_result):
    root = ET.Element("Topics")
    for topic_id in topic_reader.map_topics:
        topic = topic_reader.map_topics[topic_id]
        question_id = dic_topic_question_id[topic_id]
        latex, location = dic_candidates_question_id_latex[question_id]
        formula_id = get_formula_id(dic_question_id_formulas[topic_id], latex, location)
        topic_id = "B." + topic_id.split(".")[1]
        sub = ET.SubElement(root, "Topic", number=topic_id)
        ET.SubElement(sub, "Formula_Id").text = formula_id
        ET.SubElement(sub, "Latex").text = latex

        body = topic.question
        body = html.unescape(body)
        body = body.replace("\n", " ")
        title = topic.title
        title = title.replace("\n", " ")
        title = html.unescape(title)
        question_tag = topic.lst_tags
        ET.SubElement(sub, "Title").text = title
        ET.SubElement(sub, "Question").text = body
        tags = question_tag[0]
        for i in range(1, len(question_tag)):
            tags += "," + question_tag[i]
        ET.SubElement(sub, "Tags").text = tags
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(xml_result, "w", encoding="utf-8") as f:
        f.write(xmlstr)


def generate_topic_file_task_2(topic_xml_file, task2_formulas, latex_file, task2_xml_file):
    topic_reader = TopicReader(topic_xml_file)
    print("reading candidate formulas")
    dic_candidates_question_id_latex = read_candidate_formulas(task2_formulas)
    dic_topic_question_id, dic_question_id_formulas = read_topic_formulas(latex_file)
    create_topic_files_2(topic_reader, dic_candidates_question_id_latex, dic_topic_question_id,
                         dic_question_id_formulas, task2_xml_file)


def generate_topic_file_task_1(post_reader, file_question_ids, result_formula_tsv_file, result_xml_file):
    print("reading question ids")
    lst_question_ids = read_question_id_file(file_question_ids)

    formula_id = 1
    # ##
    # For ARQMath-1 this id was set to 1, and for ARQMath-2 it was set to 201, and in ARQMath-3 it starts with 301
    # ##
    topic_id = 301
    root = ET.Element("Topics")
    print("extracting formulas and generating xml and tsv files")
    "the file that will save the topic formulas"
    with open(result_formula_tsv_file, "w", encoding="utf-8", newline='') as result_file:
        csv_writer = csv.writer(result_file, delimiter='\t')
        csv_writer.writerow(["id", "topic_id", "thread_id", "type", "formula"])
        "iterating on the topics"
        for question_id in lst_question_ids:
            question = post_reader.map_questions[question_id]
            title = question.title
            title = html.unescape(title)
            body = question.body

            body = html.unescape(body)

            "extracting formulas from topic title"
            _, formula_in_title = get_list_of_formulas(title)
            dic_formula_id = {}
            for f_id in formula_in_title:
                latex = formula_in_title[f_id]
                csv_writer.writerow(["q_" + str(formula_id), "A." + str(topic_id), question_id, "title", latex])
                dic_formula_id[formula_id] = latex
                formula_id += 1
            title = annotate_formulas(title, dic_formula_id)
            "extracting formulas from topic body"
            _, formula_in_title = get_list_of_formulas(body)
            dic_formula_id = {}
            for f_id in formula_in_title:
                latex = formula_in_title[f_id]
                csv_writer.writerow(["q_" + str(formula_id), "A." + str(topic_id), question_id, "body", latex])
                dic_formula_id[formula_id] = latex
                formula_id += 1
            body = annotate_formulas(body, dic_formula_id)
            title = html.unescape(title)
            body = html.unescape(body)
            body = body.replace("\n", " ")
            title = title.replace("\n", " ")
            sub = ET.SubElement(root, "Topic", number="A." + str(topic_id))
            ET.SubElement(sub, "Title").text = title
            ET.SubElement(sub, "Question").text = body
            question_tag = question.tags
            tags = question_tag[0]
            for i in range(1, len(question_tag)):
                tags += "," + question_tag[i]
            ET.SubElement(sub, "Tags").text = tags
            topic_id += 1

        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        with open(result_xml_file, "w", encoding="utf-8") as f:
            f.write(xmlstr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-pf', type=str, help='original MSE post file path')
    parser.add_argument('-qid', type=str, help='file that contains topic question ids in each line')
    parser.add_argument('-ff', type=str, help='file that has the topics formula for task 2')
    args = vars(parser.parse_args())
    post_file_path = args['pf']
    topic_question_id_file_path = args['qid']
    topic_formula_file_path = args['ff']

    latex_formula_tsv_file = "./Topics_Formulas_Latex.v0.1.tsv"
    slt_formula_tsv_file = "./Topics_Formulas_SLT.v0.1.tsv"
    opt_formula_tsv_file = "./Topics_Formulas_OPT.v0.1.tsv"
    xml_task1 = "./Topics_Task1_v0.1.xml"
    xml_task2 = "./Topics_Task2_v0.1.xml"

    print("reading post xml file")
    post_reader = PostParserRecord(post_file_path)
    print("generation xml (TASK 1) and latex tsv files for topics")
    generate_topic_file_task_1(post_reader, topic_question_id_file_path, latex_formula_tsv_file, xml_task1)
    print("generation xml (TASK 2)")
    generate_topic_file_task_2(xml_task1, topic_formula_file_path, latex_formula_tsv_file, xml_task2)
    print("Generating SLT/OPT TSV index files")
    converting_latex_topics(latex_formula_tsv_file, slt_formula_tsv_file, opt_formula_tsv_file)
    print("Two XML files and Three TSV (Latex, SLT, OPT) files are generated")


if __name__ == '__main__':
    main()
