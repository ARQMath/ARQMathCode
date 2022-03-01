import html
import xml.etree.cElementTree as ET
import csv
import os
import codecs
import argparse

from bs4 import BeautifulSoup
from xml.dom import minidom
import sys
conf_path = os.getcwd()
sys.path.append(conf_path)
from Entity_Parser_Record.post_parser_record import PostParserRecord


def read_formula_file(directory):
    """
        read the formula files and returns a dictionary of post id and the formulas in the post
    """
    dic_question_title = {}
    dic_question_body = {}
    dic_answer = {}
    dic_formula_id_latex = {}
    for file in os.listdir(directory):
        with open(directory + "/" + str(file), 'r', newline='', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            next(csv_reader)
            for row in csv_reader:
                formula_id = int(row[0])
                post_id = int(row[1])
                doc_type = row[3]
                latex_representation = row[5]
                if doc_type == "comment":
                    continue
                dic_formula_id_latex[formula_id] = latex_representation
                if doc_type == "title":
                    if post_id in dic_question_title:
                        dic_question_title[post_id].append(formula_id)
                    else:
                        dic_question_title[post_id] = [formula_id]
                elif doc_type == "question":
                    if post_id in dic_question_body:
                        dic_question_body[post_id].append(formula_id)
                    else:
                        dic_question_body[post_id] = [formula_id]
                elif doc_type == "answer":
                    if post_id in dic_answer:
                        dic_answer[post_id].append(formula_id)
                    else:
                        dic_answer[post_id] = [formula_id]
    return dic_question_title, dic_question_body, dic_answer, dic_formula_id_latex


def read_arqmath_data_post(post_file_path, latex_dir):
    """
    return the post readers and dictionary of post id: list of formulas in the post
    """
    pr = PostParserRecord(post_file_path)
    dic_question_title, dic_question_body, dic_answer, dic_formula_id_latex = read_formula_file(latex_dir)
    return pr, dic_question_title, dic_question_body, dic_answer, dic_formula_id_latex


def check_existence(dic_find_id):
    lst_index = list(set(dic_find_id.values()))
    if len(lst_index) > 1:
        return True
    elif lst_index[0] == -1:
        return False
    return True


def get_sorted_dic_formulas(lst_formula, dic_formula_id_latex):
    temp_dic = {}
    for formula_id in lst_formula:
        temp_dic[formula_id] = dic_formula_id_latex[formula_id]
    soreted_formula_ids = sorted(temp_dic, key=lambda k: len(temp_dic[k]), reverse=True)
    return soreted_formula_ids


def set_formulas(text, lst_formula, dic_latex, replaceing_dic):
    """
    Input:
        text: the input text that its formulas need to be converted to Arqmath notation, where each formula has an
        unique id and is in math-container tag
        post_id: the post_id of the current text, question id, answer id or the comment id
        map_formulas: the dictionary in form of (post id, dictionary of (formula id: latex))
        map_id_type: the dictionary which shows where is each of the formulas located (formula_id: type)
        text_type: shows the current text (first input) is a title, question, answer or comment
    """
    lst_not_found_formulas = []
    lst_found = []
    text = text.replace("\r", "\n", text.count("\r"))
    "Iteration on the formulas in the current text"

    soreted_formula_ids = get_sorted_dic_formulas(lst_formula, dic_latex)

    for formula_id in soreted_formula_ids:
        """
            the formula should be located in the same type of text, why we have this?
            the title and question have the same ids, so if the formula is in both title and question,
            we do not know which one to replace (replace the original formula with the math-container tag one)
        """
        "the original formula"
        formula = dic_latex[formula_id]

        "the string that will be replaced by the original formula, it has math-container tag and formula id"
        to_write_string = "<span class=\"math-container\" id=\"" + str(formula_id) + "\">" + formula + "</span>"

        map_index = match_to_pattern(formula, text)

        exists = check_existence(map_index)

        if exists:
            sorted_x = sorted(map_index.items(), key=lambda kv: kv[1])
            for item in sorted_x:
                if item[1] != -1:
                    detected_formula = item[0]
                    fake_string = "FXXF_" + str(formula_id)
                    replaceing_dic[fake_string] = to_write_string
                    text = text.replace(detected_formula, fake_string, 1)
                    lst_found.append(formula_id)
                    break
        else:
            lst_not_found_formulas.append(formula_id)
    return text, lst_found, lst_not_found_formulas


def match_to_pattern(formula, text):
    """Each formula can be located in the text in one this 6 form, (text6) should not happen but
        just added for the case. Note that in the formula index file from which we created the map
        we only have the latex of formula not how the formula was located in the text.

        For example a formula can be like "<span class="math-container> $a+b$ </span>" in the original MSE dataset
        but we only keep a+b.

        So we check which of these 6 format was the one that the original formula was written in, and also note in the
        map, formulas are sorted based on their order in the original, so we use these 6 format, find their first
        occurrence and replace them with our desired text.
        """
    # text = text.replace("\n", "")
    map_index = {}
    text1 = "<span class=\"math-container\">$$ " + formula + " $$</span>"
    map_index[text1] = text.find(text1)
    text7 = "<span class=\"math-container\">$$" + formula + "$$</span>"
    map_index[text7] = text.find(text7)
    text2 = "<span class=\"math-container\">$" + formula + "$</span>"
    map_index[text2] = text.find(text2)
    text8 = "<span class=\"math-container\">$$" + formula + "$$</span>"
    map_index[text8] = text.find(text8)
    text3 = "<span class=\"math-container\">" + formula + "</span>"
    map_index[text3] = text.find(text3)
    text4 = "$$" + formula + "$$"
    map_index[text4] = text.find(text4)
    text5 = "$" + formula + "$"
    map_index[text5] = text.find(text5)
    text6 = " " + formula + " "
    map_index[text6] = text.find(text6)
    return map_index


def extract_missed_formulas_from_text(text, lst_formulas_in_text):
    lst_missed_formula_ids = []
    soup = BeautifulSoup(text, features="lxml")
    for formula_id in lst_formulas_in_text:
        spans = soup.find_all('span', {'class': 'math-container', 'id': str(formula_id)})
        if spans is not None and len(spans) > 0:
            continue
        else:
            lst_missed_formula_ids.append(formula_id)
    return lst_missed_formula_ids


def get_missed_formulas_in_post(text, lst_formulas_in_text, dic_formula_id_latex):
    temp_missed_formula_ids = extract_missed_formulas_from_text(text, lst_formulas_in_text)
    if len(temp_missed_formula_ids) == 0:
        return text, [], []
    replacing_dic = {}
    soup = BeautifulSoup(text, features="lxml")
    spans = soup.find_all('span', {'class': 'math-container'})
    for span in spans:
        if span.has_attr('id'):
            formula_id = str(span['id'])
            text = text.replace(str(span), "FXXF_" + str(formula_id), 1)
            replacing_dic["FXXF_" + str(formula_id)] = str(span)
    text = html.unescape(text)
    text, lst_found, lst_not_found_formulas = set_formulas(text, temp_missed_formula_ids, dic_formula_id_latex,
                                                           replacing_dic)

    for fake_text in replacing_dic:
        text = text.replace(fake_text, replacing_dic[fake_text], 1)

    return text, lst_found, lst_not_found_formulas


def write_missed_formula_id(lst_formulas_missed_post_not_available, lst_formulas_not_in_post):
    with open("missed_formulas_post_not_available.txt", "w", encoding="utf-8") as file:
        for formula_id in lst_formulas_missed_post_not_available:
            file.write(str(formula_id) + "\n")
    with open("missed_formulas_not_available.txt", "w", encoding="utf-8") as file:
        for formula_id in lst_formulas_not_in_post:
            file.write(str(formula_id) + "\n")


def fix_post_files(old_post_xml, latex_dir):
    # Conversion of post file
    print("Reading XML and TSV files")
    pr, dic_question_title, dic_question_body, dic_answer, dic_formula_id_latex = read_arqmath_data_post(old_post_xml,
                                                                                                         latex_dir)
    lst_formulas_missed_post_not_available = []
    lst_formulas_not_in_post = []
    lst_fixed_formulas = []
    ###############################################################################################################
    # # Fixing Question Title
    print("Fixing Questions Title")
    for post_id in dic_question_title:
        lst_formulas_in_title = dic_question_title[post_id]
        if post_id not in pr.map_questions:
            lst_formulas_missed_post_not_available.extend(lst_formulas_in_title)
            continue
        else:
            final_text, lst_fixed, lst_not_existing_formulas = get_missed_formulas_in_post(
                pr.map_questions[post_id].title,
                lst_formulas_in_title,
                dic_formula_id_latex)
            pr.map_questions[post_id].title = final_text
            lst_formulas_not_in_post.extend(lst_not_existing_formulas)
            lst_fixed_formulas.extend(lst_fixed)
    # ###############################################################################################################
    # # Fixing Question Body
    print("Fixing Questions Body")
    for post_id in dic_question_body:
        lst_formulas_in_body = dic_question_body[post_id]
        if post_id not in pr.map_questions:
            lst_formulas_missed_post_not_available.extend(lst_formulas_in_body)
            continue
        else:
            final_text, lst_fixed, lst_not_existing_formulas = get_missed_formulas_in_post(
                pr.map_questions[post_id].body,
                lst_formulas_in_body,
                dic_formula_id_latex)
            pr.map_questions[post_id].body = final_text
            lst_formulas_not_in_post.extend(lst_not_existing_formulas)
            lst_fixed_formulas.extend(lst_fixed)
    ################################################################################################################
    # # Fixing Answer
    print("Fixing Answers Body")
    for post_id in dic_answer:
        lst_formulas_in_answer = dic_answer[post_id]
        if post_id not in pr.map_just_answers:
            lst_formulas_missed_post_not_available.extend(lst_formulas_in_answer)
            continue
        else:
            final_text, lst_fixed, lst_not_existing_formulas = get_missed_formulas_in_post(
                pr.map_just_answers[post_id].body,
                lst_formulas_in_answer,
                dic_formula_id_latex)
            pr.map_just_answers[post_id].body = final_text
            lst_formulas_not_in_post.extend(lst_not_existing_formulas)
            lst_fixed_formulas.extend(lst_fixed)

    write_missed_formula_id(lst_formulas_missed_post_not_available, lst_formulas_not_in_post)

    print("-------------------------------------------------------")
    print("After applying fixes: \n")
    print(str(len(lst_fixed_formulas)) + " formulas are fix and located in post XML file")
    print(str(len(lst_formulas_not_in_post)) + " formulas were not found in XML file")
    print(str(len(lst_formulas_missed_post_not_available)) + " formulas were in unavailable post files")
    return pr


def convert_mse_arqmath_post_file(old_xml_file, old_post_reader, new_xml_file_path):
    """First reads the formulas and save
    @param xml_post_link_file_path: Original post file from Archive
    @param formula_latex_index_directory: the formula index file (the tsv file containing the latex)
    @param new_xml_file_path: the result post file that will be used in ARQMath containing posts from 2010 to 2018 with
    annotated formulas
    @param lst_missed_formulas: list of missed formula ids
    """

    "Creating the root for the new post file [the one for ARQMath]"
    root = ET.Element("posts")

    "reading the original post file of MSE dataset from Archive"
    with codecs.open(old_xml_file, "r", "utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
        all_post = soup.find_all("row")
        "reading the original mse post file, row by row"
        for post in all_post:
            attr_dic = post.attrs
            post_id = int(attr_dic["id"])
            post_type_id = int(attr_dic["posttypeid"])
            creation_date = (attr_dic["creationdate"])
            sub = ET.SubElement(root, "row")
            "All these attributes are common in both questions and answers"
            sub.set('Id', str(post_id))
            sub.set('PostTypeId', str(post_type_id))
            sub.set('CreationDate', creation_date)
            if "viewcount" in attr_dic:
                sub.set('ViewCount', attr_dic["viewcount"])
            if "score" in attr_dic:
                sub.set('Score', attr_dic["score"])
            if "commentcount" in attr_dic:
                sub.set('CommentCount', attr_dic["commentcount"])
            if "owneruserid" in attr_dic:
                sub.set('OwnerUserId', attr_dic["owneruserid"])
            if "lastEditDate" in attr_dic:
                sub.set('LastEditDate', attr_dic["lastEditDate"])
            if "lastActivityDate" in attr_dic:
                sub.set('LastActivityDate', attr_dic["lastActivityDate"])
            if "lastEditorUserId" in attr_dic:
                sub.set('LastEditorUserId', attr_dic["lastEditorUserId"])
            if "communityOwnedDate" in attr_dic:
                sub.set('CommunityOwnedDate', attr_dic["communityOwnedDate"])
            if "lastEditorDisplayName" in attr_dic:
                sub.set('LastEditorDisplayName', attr_dic["lastEditorDisplayName"])
            "If the post is a question"
            if post_type_id == 1:  # Question
                "we want to linearize both title and body so that each post can be viewed in one row when using text " \
                "editors "
                title = old_post_reader.map_questions[post_id].title
                title = title.replace("\n", " ", title.count("\n"))
                sub.set('Title', title)

                body = old_post_reader.map_questions[post_id].body
                body = body.replace("\n", " ", body.count("\n"))
                sub.set('Body', body)

                if "commentcount" in attr_dic:
                    sub.set('CommentCount', attr_dic["commentcount"])
                if "answercount" in attr_dic:
                    sub.set('AnswerCount', attr_dic["answercount"])
                if "favouritecount" in attr_dic:
                    sub.set('FavoriteCount', attr_dic["favouritecount"])
                if "acceptedanswerid" in attr_dic:
                    sub.set('AcceptedAnswerId', attr_dic["acceptedanswerid"])
                if "closeddate" in attr_dic:
                    sub.set('ClosedDate', attr_dic["closeddate"])

                if "tags" in attr_dic:
                    sub.set('Tags', attr_dic["tags"])
            elif post_type_id == 2:
                "If the post is an answer"
                body = old_post_reader.map_just_answers[post_id].body
                body = body.replace("\n", " ", body.count("\n"))
                sub.set('Body', body)
                sub.set('ParentId', attr_dic["parentid"])

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(new_xml_file_path, "w", encoding="utf-8") as f:
        f.write(xml_str)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-op', type=str, help='old post file path')
    parser.add_argument('-np', type=str, help='new post file path')
    parser.add_argument('-ldir', type=str, help='laTex TSV files directory')
    args = vars(parser.parse_args())

    old_post_file = args['op']
    new_por_file = args['np']
    latex_dir = args['ldir']
    post_reader = fix_post_files(old_post_file, latex_dir)
    convert_mse_arqmath_post_file(old_post_file, post_reader, new_por_file)


if __name__ == '__main__':
    main()
