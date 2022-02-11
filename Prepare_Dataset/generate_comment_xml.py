import xml.etree.cElementTree as ET
import csv
import os
import sys
import re
import argparse
conf_path = os.getcwd()
sys.path.append(conf_path)
from bs4 import BeautifulSoup
from xml.dom import minidom
from Entity_Parser_Record.comment_parser_record import CommentParserRecord


def read_intermediate_tsv(file_path):
    # Reading the intermediate file showing formula id comment id into dictionary of comment id and list of formula ids
    # in this comment
    dic_comment_id_list_formula_ids = {}
    with open(file_path, mode='r', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        for row in csv_reader:
            formula_id = int(row[0])
            comment_id = int(row[1])
            if comment_id in dic_comment_id_list_formula_ids:
                dic_comment_id_list_formula_ids[comment_id].append(formula_id)
            else:
                dic_comment_id_list_formula_ids[comment_id] = [formula_id]
    return dic_comment_id_list_formula_ids


def read_all_formula_files(formula_file_path):
    """
        Takes in formula file path and read it line by line and return three dictionaries:
        dic_formula_id_latex:
            key: formula id id, value: latex representation
        dic_formula_id_post_id:
            key: formula id, value post id
    """
    dic_formula_id_latex = {}
    dic_formula_id_post_id = {}
    for file in os.listdir(formula_file_path):
        with open(formula_file_path + "/" + file, mode='r', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            next(csv_reader)
            for row in csv_reader:
                doc_type = row[3]
                if doc_type != "comment":
                    continue
                formula_id = int(row[0])
                post_id = int(row[1])
                formula_latex = row[5]
                dic_formula_id_post_id[formula_id] = post_id
                dic_formula_id_latex[formula_id] = formula_latex
    return dic_formula_id_latex, dic_formula_id_post_id


def check_removing_backslash_space_lower(formula, lst_not_found_formulas):
    """
    For some of the formulas in the xml file, the correct LaTex was not extracted having extra space or backslash
    This method seeks to find if removing these characters will find the similar formulas
    """
    formula = formula.replace(" ", "", formula.count(" "))
    formula = formula.replace("\\", "", formula.count("\\"))
    for i in range(0, len(lst_not_found_formulas)):
        not_found_formula = lst_not_found_formulas[i]
        not_found_formula = not_found_formula.replace(" ", "", formula.count(" "))
        not_found_formula = not_found_formula.replace("\\", "", formula.count("\\"))
        if formula == not_found_formula:
            return lst_not_found_formulas[i]
    return None


def check_existence(dic_find_id):
    lst_index = list(set(dic_find_id.values()))
    if len(lst_index) > 1:
        return True
    elif lst_index[0] == -1:
        return False
    return True


def replace_formula_with_token(formula_double_dollar, input_text, formula_counter, formula_index_map, start_pattern,
                               end_pattern):
    for string in formula_double_dollar:
        if "FXXF_" in string:
            continue
        original_formula = start_pattern + string + end_pattern
        fake_text = "FXXF_" + str(formula_counter)
        formula_index_map[fake_text] = original_formula
        input_text = input_text.replace(original_formula, " " + fake_text + " ", 1)
        formula_counter += 1
    return input_text, formula_counter, formula_index_map


def get_list_not_annotated_formula(input_text):
    """
    This method takes in a text and extract all the formulas that are not annotated with id in the file
    """

    "first removes the new lines all tne \n in the text"
    input_text = input_text.replace("\n", " ", input_text.count("\n"))
    latex_formulas = []

    "Formulas are located between 2 dollar signs in latex, so if there no or only one we have no formula in the text"
    if input_text.count("$") == 0 or input_text.count("$") == 1:
        return latex_formulas

    """
    There are 5 patterns in MSE dataset for latex formula; considering a+b we can have one of these:
    '<span class="math-container">$$a+b$$</span>'
    '<span class="math-container">$a+b$</span>'
    '<span class="math-container">a+b</span>'
    $$a+b$$
    $a+b$
    We start from the top to the bottom of these 5 types and use 're' library to find the patterns. As you can 
    see the patterns in bottom, are inside patterns in top, therefore after extracting each formula, we
    replace them with 'FXXF_formula id' to avoid double extraction. 
    The way we did the pattern matching was from top to bottom patterns and we find all of them (all of the formulas 
    with pattern 1 (<span class="math-container">$$a+b$$</span>) then all of pattern 2 and so on). 
    We assign to each formula an unique id.
    """

    "Formula ids"
    counter = 1

    """
    As we use fake text of 'FXXF_formula_id' to avoid mismatching, we have a map of original text and fake one as;
    FXXF_1 : $a+b$ named formula_index_map. 
    """
    formula_index_map = {}
    """
    Here we check the 5 patterns
    """
    formula_double_dollar = re.findall('<span class="math-container">\$\$(.+?)\$\$</span>', input_text)
    input_text, counter, formula_index_map = replace_formula_with_token(formula_double_dollar,
                                                                        input_text, counter, formula_index_map,
                                                                        '<span class="math-container">$$', "$$</span>")
    formula_double_dollar = re.findall('<span class="math-container">\$(.+?)\$</span>', input_text)
    input_text, counter, formula_index_map = replace_formula_with_token(formula_double_dollar,
                                                                        input_text, counter, formula_index_map,
                                                                        '<span class="math-container">$', '$</span>')
    formula_double_dollar = re.findall('<span class="math-container">(.+?)</span>', input_text)
    input_text, counter, formula_index_map = replace_formula_with_token(formula_double_dollar,
                                                                        input_text, counter, formula_index_map,
                                                                        '<span class="math-container">', '</span>')
    """
    formula_index_map now contains all the formula, we should sort them based on their order appearance in the text; 
    e.g.: 
        original text: $a+b$ is similar to $$a+b$$
        converted text: FXXF_2 is similar to FXXF_1
    we want to know $a+b$ has appeared first, because when we want to convert the original stack exchange to arqmath
    one [where all the formulas are in math-container and has id], we need to put all the formulas in math-container 
    tags, and for that we begin from top to end and sort the formulas based on their relative position to the beginning
    of the text and replace the formula (from MSE) with formula with math-container.
    """
    sorted_by_index = {}
    for formula in formula_index_map:
        sorted_by_index[formula] = re.search(r' (' + formula + ') ', input_text).start()
    sorted_by_index = sorted(sorted_by_index.items(), key=lambda kv: kv[1])

    for formula in sorted_by_index:
        latex_formulas.append(formula_index_map[formula[0]])
    """What is returned here is a list of formulas recognized in the text in the format they are in MSE which can
    be one of the five above."""
    return latex_formulas


def handle_already_exists(spans, text):
    for span in spans:
        if span.has_attr('id'):
            text = text.replace(str(span), span.text, 1)
    return text


def handle_detected_formula(detected_formula, formula_id, to_write_string, text, temp_dic):
    fake_string = "FXXF_"+str(formula_id)
    text = text.replace(detected_formula, fake_string, 1)
    temp_dic[fake_string] = to_write_string
    return text


def set_formulas(text, dic_formula_id_latex, list_formula_ids):
    """
    Takes in a comment text and annotate its math formulas
    @param text: text: the input text that its formulas need to be converted to Arqmath notation, where each formula has
    a unique id and is in math-container tag
    @param comment_id: the comment_id of the current text
    @param dic_formula_id_latex: dictionary of formula id and their laTex representation
    @param list_formula_ids: list of formula ids in the comment
    """

    "This means all formulas in this post are annotated with id before"

    temp_dic = {}
    text = text.replace("\r", "\n", text.count("\r"))
    soup_text = BeautifulSoup(text)
    spans = soup_text.find_all('span', {'class': 'math-container'})
    text = handle_already_exists(spans, text)
    lst_not_found = []

    "Iteration on the formulas in the current text"
    for formula_id in list_formula_ids:
        "the original formula"
        formula = dic_formula_id_latex[formula_id]

        "the string that will be replaced by the original formula, it has math-container tag and formula id"
        to_write_string = "<span class=\"math-container\" id=\"" + str(formula_id) + "\">" + formula + "</span>"

        map_index = match_to_pattern(formula, text)

        exists = check_existence(map_index)

        if exists:
            sorted_x = sorted(map_index.items(), key=lambda kv: kv[1])
            for item in sorted_x:
                if item[1] != -1:
                    detected_formula = item[0]
                    text = handle_detected_formula(detected_formula, formula_id, to_write_string, text, temp_dic)
                    break
        else:
            lst_not_found.append(formula_id)
    for item in temp_dic:
        real_value = temp_dic[item]
        text = text.replace(item, real_value, 1)
    return text, lst_not_found


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
    map_index = {}
    text1 = "<span class=\"math-container\">$$" + formula + "$$</span>"
    map_index[text1] = text.find(text1)
    text2 = "<span class=\"math-container\">$" + formula + "$</span>"
    map_index[text2] = text.find(text2)
    text3 = "<span class=\"math-container\">" + formula + "</span>"
    map_index[text3] = text.find(text3)
    text4 = "$$" + formula + "$$"
    map_index[text4] = text.find(text4)
    text5 = "$" + formula + "$"
    map_index[text5] = text.find(text5)
    text6 = " " + formula + " "
    map_index[text6] = text.find(text6)
    return map_index


def convert_mse_arqmath_comment_file(old_post_xml, new_post_xml, latex_dir, dic_comment_id_list_formula_ids):
    """
    Takes in the Original comment file from MSE Archive, the extracted formula tsv file and the results file path
    for the new comment file and do the conversion.
    @param old_post_xml: The older version of comment XML file
    @param new_post_xml: The new version of comment XML file (to be generated)
    @param latex_dir: The directory where TSV latex files are located in
    @param dic_comment_id_list_formula_ids: dictionary of comment id and list of formula ids in the comment
    """
    dic_formula_id_latex, dic_formula_id_post_id = read_all_formula_files(latex_dir)

    comment_parser = CommentParserRecord(old_post_xml)
    root = ET.Element("comments")
    list_not_found = []
    for comment_id in comment_parser.map_just_comments:
        comment = comment_parser.map_just_comments[comment_id]
        creation_date = comment.creation_date
        score = comment.score
        text = comment.text
        post_id = comment.related_post_id
        user_id = comment.user_id
        if comment_id in dic_comment_id_list_formula_ids:
            text, temp_not_found = set_formulas(text, dic_formula_id_latex, dic_comment_id_list_formula_ids[comment_id])
            list_not_found.extend(temp_not_found)
        sub = ET.SubElement(root, "row")
        sub.set('Id', str(comment.id))
        sub.set('PostId', str(post_id))
        sub.set('Text', text)
        if score is not None:
            sub.set('Score', str(score))
        if creation_date is not None:
            sub.set('CreationDate', creation_date)
        if user_id is not None:
            sub.set('UserId', str(user_id))

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(new_post_xml, "w", encoding="utf-8") as f:
        f.write(xml_str)

    with open("not_found_comment_formulas.txt", "w", encoding="utf-8") as f:
        for formula_id in list_not_found:
            f.write(str(formula_id) + "\n")


def regenerate_comment_xml_file(old_comment_xml, new_comment_xml, latex_dir, association_file):
    dic_comment_id_list_formula_ids = read_intermediate_tsv(association_file)
    convert_mse_arqmath_comment_file(old_comment_xml, new_comment_xml, latex_dir, dic_comment_id_list_formula_ids)
    print("conversion done")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ocom', type=str, help='old comment file path')
    parser.add_argument('-ncom', type=str, help='new comment file path')
    parser.add_argument('-ldir', type=str, help='laTex TSV files directory')
    args = vars(parser.parse_args())

    old_comment_file = args['ocom']
    new_comment_file = args['ncom']
    latex_dir = args['ldir']
    association_file = "formula_comment_id.tsv"
    regenerate_comment_xml_file(old_comment_file, new_comment_file, latex_dir, association_file)


if __name__ == '__main__':
    main()
