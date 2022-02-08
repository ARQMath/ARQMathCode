import xml.etree.cElementTree as ET
import csv
import os
import codecs
import re
from bs4 import BeautifulSoup
from xml.dom import minidom
from Entity_Parser_Record.comment_parser_record import CommentParserRecord


def read_missed_ids(file_path):
    # Reading the missing formula ids file
    lst_formula_missed_lst = []
    with open(file_path, mode='r', encoding="utf-8") as file:
        line = file.readline()
        while line:
            formula_id = int(line)
            lst_formula_missed_lst.append(formula_id)
            line = file.readline()
    return lst_formula_missed_lst


def read_all_formula_files(formula_file_path):
    """
        Takes in formula file path and read it line by line and return three dictionaries:
        dic_formula_id_latex:
            key: formula id id, value: latex representation
        dic_formula_post_type:
            key: formula_id, value post type : title, answer, question, or comment
        dic_formula_id_post_id:
            key: formula id, value post or comment id
    """
    dic_formula_id_latex = {}
    dic_formula_post_type = {}
    dic_formula_id_post_id = {}
    for file in os.listdir(formula_file_path):
        with open(formula_file_path + "/" + file, mode='r', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            next(csv_reader)
            for row in csv_reader:
                formula_id = int(row[0])
                post_id = int(row[1])
                doc_type = row[3]
                formula_latex = row[5]
                dic_formula_id_post_id[formula_id] = post_id
                dic_formula_id_latex[formula_id] = formula_latex
                dic_formula_post_type[formula_id] = doc_type
    return dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id


def get_missed_ids_information(dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id,
                               lst_missed_formulas):
    # Just keep information about missing formula ids
    res_dic_formula_id_latex = {}
    res_dic_formula_post_type = {}
    res_dic_formula_id_post_id = {}
    for formula_id in lst_missed_formulas:
        res_dic_formula_id_latex[formula_id] = dic_formula_id_latex[formula_id]
        res_dic_formula_post_type[formula_id] = dic_formula_post_type[formula_id]
        post_id = dic_formula_id_post_id[formula_id]
        if post_id in res_dic_formula_id_post_id:
            res_dic_formula_id_post_id[post_id].append(formula_id)
        else:
            res_dic_formula_id_post_id[post_id] = [formula_id]
    return res_dic_formula_id_latex, res_dic_formula_post_type, res_dic_formula_id_post_id


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


def set_formulas(text, post_id, dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id, text_type,
                 dic_latex_wrong, lst_fixed_id):
    """
    Input:
        text: the input text that its formulas need to be converted to Arqmath notation, where each formula has an
        unique id and is in math-container tag
        post_id: the post_id of the current text, question id, answer id or the comment id
        map_formulas: the dictionary in form of (post id, dictionary of (formula id: latex))
        map_id_type: the dictionary which shows where is each of the formulas located (formula_id: type)
        text_type: shows the current text (first input) is a title, question, answer or comment
    """

    "This means all formulas in this post are annotated with id before"
    if post_id not in dic_formula_id_post_id:
        return text

    result_text = ""
    text = text.replace("\r", "\n", text.count("\r"))
    "Iteration on the formulas in the current text"
    for formula_id in dic_formula_id_post_id[post_id]:
        """
            the formula should be located in the same type of text, why we have this?
            the title and question have the same ids, so if the formula is in both title and question,
            we do not know which one to replace (replace the original formula with the math-container tag one)
        """
        if dic_formula_post_type[formula_id] != text_type:
            continue
        if formula_id in lst_fixed_id:
            continue
        "the original formula"
        formula = dic_formula_id_latex[formula_id]

        "the string that will be replaced by the original formula, it has math-container tag and formula id"
        to_write_string = "<span class=\"math-container\" id=\"" + str(formula_id) + "\">"

        map_index = match_to_pattern(formula, text)

        exists = check_existence(map_index)

        if exists:
            sorted_x = sorted(map_index.items(), key=lambda kv: kv[1])
            for item in sorted_x:
                if item[1] != -1:
                    find_inx = text.find(item[0]) + len(item[0])
                    temp = text[0:find_inx]
                    text = text[find_inx:]
                    result_text += temp.replace(item[0], to_write_string + formula + "</span>")
                    lst_fixed_id.append(formula_id)
                    break
        else:
            lst_not_found_formulas = get_list_not_annotated_formula(text)
            if lst_not_found_formulas is None or len(lst_not_found_formulas) == 0:
                break
            matched = check_removing_backslash_space_lower(formula, lst_not_found_formulas)
            if matched:
                dic_latex_wrong[formula_id] = (formula, matched)
                dic_formula_id_latex[formula_id] = matched
                return set_formulas(result_text + text, post_id, dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id,
                                    text_type, dic_latex_wrong, lst_fixed_id)
    return result_text + text


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
    text6 = formula
    map_index[text6] = text.find(text6)
    return map_index


def convert_mse_arqmath_post_file(xml_post_link_file_path, formula_latex_index_directory, new_xml_file_path,
                                  lst_missed_formulas):
    """First reads the formulas and save
    @param xml_post_link_file_path: Original post file from Archive
    @param formula_latex_index_directory: the formula index file (the tsv file containing the latex)
    @param new_xml_file_path: the result post file that will be used in ARQMath containing posts from 2010 to 2018 with
    annotated formulas
    @param lst_missed_formulas: list of missed formula ids
    """
    dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id = read_all_formula_files(
        formula_latex_index_directory)
    # remove uncessary information from the the dictionary and just keep information about missing formula ids
    dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id = get_missed_ids_information(
        dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id, lst_missed_formulas)

    wrong_extracted_latex = {}

    "Creating the root for the new post file [the one for ARQMath]"
    root = ET.Element("posts")

    "reading the original post file of MSE dataset from Archive"
    with codecs.open(xml_post_link_file_path, "r", "utf-8") as file2:
        soup = BeautifulSoup(file2, "html.parser")
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
            lst_fixed_id = []
            "If the post is a question"
            if post_type_id == 1:  # Question

                title = (attr_dic["title"])
                "we want to linearize both title and body so that each post can be viewed in one row when using text " \
                "editors "

                title = title.replace("\n", " ", title.count("\n"))
                title = set_formulas(title, post_id, dic_formula_id_latex, dic_formula_post_type,
                                     dic_formula_id_post_id, "title", wrong_extracted_latex, lst_fixed_id)
                title = title.replace("\n", " ", title.count("\n"))
                sub.set('Title', title)

                body = (attr_dic["body"])
                body = body.replace("\n", " ", body.count("\n"))
                "Annotating the formulas"
                body = set_formulas(body, post_id, dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id,
                                    "question", wrong_extracted_latex, lst_fixed_id)
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
                body = (attr_dic["body"])
                body = body.replace("\n", " ", body.count("\n"))
                "Annotating the formulas"
                body = set_formulas(body, post_id, dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id,
                                    "answer", wrong_extracted_latex, lst_fixed_id)
                body = body.replace("\n", " ", body.count("\n"))
                sub.set('Body', body)
                sub.set('ParentId', attr_dic["parentid"])

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(new_xml_file_path, "w", encoding="utf-8") as f:
        f.write(xml_str)

    with open("replaced_latex_post.tsv", "w", newline='', encoding="utf-8") as new_file:
        csv_writer = csv.writer(new_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for formula_id in wrong_extracted_latex:
            csv_writer.writerow(
                [str(formula_id), wrong_extracted_latex[formula_id][0], wrong_extracted_latex[formula_id][1]])


def convert_mse_arqmath_comment_file(comments_file_path, formula_latex_index_directory, result_file_path,
                                     lst_missed_formulas):
    """
    Takes in the Original comment file from MSE Archive, the extracted formula tsv file and the results file path
    for the new comment file and do the conversion.
    @param comments_file_path: The original MSE comment file, from Archive.
    @param formula_index_file_path: The extracted formulas tsv file
    @param result_file_path: The new xml comment file path.
    """
    dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id = read_all_formula_files(
        formula_latex_index_directory)
    # remove uncessary information from the the dictionary and just keep information about missing formula ids
    dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id = get_missed_ids_information(
        dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id, lst_missed_formulas)

    comment_parser = CommentParserRecord(comments_file_path)
    root = ET.Element("comments")
    wrong_extracted_latex = {}
    for comment_id in comment_parser.map_just_comments:
        lst_fixed_id = []
        comment = comment_parser.map_just_comments[comment_id]
        creation_date = comment.creation_date
        score = comment.score
        text = comment.text
        post_id = comment.related_post_id
        user_id = comment.user_id
        text = set_formulas(text, comment.id, dic_formula_id_latex, dic_formula_post_type, dic_formula_id_post_id,
                            "comment", wrong_extracted_latex, lst_fixed_id)
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
    with open(result_file_path, "w", encoding="utf-8") as f:
        f.write(xml_str)
    with open("replaced_latex_comment.tsv", "w", newline='', encoding="utf-8") as new_file:
        csv_writer = csv.writer(new_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for formula_id in wrong_extracted_latex:
            csv_writer.writerow(
                [str(formula_id), wrong_extracted_latex[formula_id][0], wrong_extracted_latex[formula_id][1]])


def regenrate_xml_files(home, missed_formula_id_path, old_post_xml, new_post_xml, latex_dir):
    #Conversion of post file
    lst_missed_formulas = read_missed_ids(missed_formula_id_path)
    convert_mse_arqmath_post_file(old_post_xml, latex_dir, new_post_xml, lst_missed_formulas)

    "Conversion of comment file"
    # lst_missed_formulas = read_missed_ids(home + "missed_formula_ids_arqmath2_comment.tsv")
    # convert_mse_arqmath_comment_file(home + "Comments.V1.2.xml", home + "latex_representation_v3", "Comments.V1.3.xml",
    #                                  lst_missed_formulas)


def main():
    regenrate_xml_files("/home/bm3302/", "/home/bm3302/missed_formula_ids_arqmath2_post.tsv",
                        "/home/bm3302/Posts.V1.2.xml", "/home/bm3302/Posts.V1.3.xml",
                        "home/bm3302/latex_representation_v3")


if __name__ == '__main__':
    main()
