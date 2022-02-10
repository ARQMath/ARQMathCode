import csv
import os

from bs4 import BeautifulSoup

from Entity_Parser_Record.comment_parser_record import CommentParserRecord
from Entity_Parser_Record.post_parser_record import PostParserRecord


def read_formula_file(directory, is_comment):
    """
        read the formula files and if is_comment is True, just read the comment files otherwise read answer and questions
    """
    dic_res = {}
    for file in os.listdir(directory):
        with open(directory + str(file), 'r', newline='', encoding="utf-8" ) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            next(csv_reader)
            for row in csv_reader:
                formula_id = row[0]
                post_id = int(row[1])
                doc_type = row[3]
                if not is_comment and doc_type == "comment":
                    continue
                if doc_type != "comment" and is_comment:
                    continue
                if post_id in dic_res:
                    dic_res[post_id].append(formula_id)
                else:
                    dic_res[post_id] = [formula_id]
    return dic_res


def read_arqmath_data_post(post_file_path, latex_dir):
    pr = PostParserRecord(post_file_path)
    dic_formulas = read_formula_file(latex_dir, is_comment=False)
    return pr, dic_formulas


def read_arqmath_data_comment(comment_file_path, latex_dir):
    cr = CommentParserRecord(comment_file_path)
    dic_formulas = read_formula_file(latex_dir, is_comment=True)
    return cr, dic_formulas


def extract_missed_formulas_from_text(lst_formulas, lst_missed_formula_ids, target):
    for formula_id in lst_formulas:
        soup = BeautifulSoup(target, features="lxml")
        spans = soup.find_all('span', {'class': 'math-container', 'id': str(formula_id)})
        if spans is not None and len(spans) > 0:
            continue
        else:
            lst_missed_formula_ids.append(formula_id)
    return lst_missed_formula_ids


def find_missed_formulas_post(post_file_path, latex_dir):
    pr, dic_formulas = read_arqmath_data_post(post_file_path, latex_dir)
    print("read arqmath data")
    lst_missed_formula_ids = []
    lst_missed_post_ids = []
    for post_id in dic_formulas:
        lst_formulas = dic_formulas[post_id]
        for formula_id in lst_formulas:
            if post_id in pr.map_questions:
                post = pr.map_questions[post_id]
                if formula_id in post.title:
                    target = post.title
                else:
                    target = post.body
            elif post_id in pr.map_just_answers:
                post = pr.map_just_answers[post_id]
                target = post.body
            else:
                lst_missed_post_ids.append(post_id)
                continue
            lst_missed_formula_ids = extract_missed_formulas_from_text(lst_formulas, lst_missed_formula_ids, target)
    return lst_missed_formula_ids, list(set(lst_missed_post_ids))


def find_missed_formulas_comments(comment_file_path, latex_dir):
    cr, dic_formulas = read_arqmath_data_comment(comment_file_path, latex_dir)

    lst_missed_formula_ids = []
    for comment_id in dic_formulas:
        if comment_id not in cr.map_just_comments:
            continue
        lst_formulas = dic_formulas[comment_id]
        comment = cr.map_just_comments[comment_id]
        target = comment.text
        lst_missed_formula_ids = extract_missed_formulas_from_text(lst_formulas, lst_missed_formula_ids, target)
    return lst_missed_formula_ids


def write_missed_ids_to_file(lst_formulas, missed_id_file_path):
    """
    Writing the missed formula ids to file with each line showing one formula id
    @param lst_formulas: list of missed formula ids
    @param missed_id_file_paths: file to save the missed ids
    @param source_root: directory to save the file
    """
    file = open(missed_id_file_path, "w")
    for formula_id in lst_formulas:
        file.write(str(formula_id) + "\n")
    file.close()


def get_file_missed_formulas_post_file(post_xml_file, latex_dir, missed_id_file_path, missed_post_file_path):
    # Get list of missed formula ids from post file and write to file
    lst_missed_formula_ids, missed_post_ids = find_missed_formulas_post(post_xml_file,latex_dir)
    print("writing missing formula ids to a file")
    write_missed_ids_to_file(lst_missed_formula_ids, missed_id_file_path)
    write_missed_ids_to_file(missed_post_ids, missed_post_file_path)


def get_file_missed_formulas_comment_file(comment_xml_file, latex_dir, missed_id_file_path):
    # Get list of missed formula ids from comment file and write to file
    lst_missed_formula_ids = find_missed_formulas_comments(comment_xml_file, latex_dir)
    write_missed_ids_to_file(lst_missed_formula_ids, missed_id_file_path)
