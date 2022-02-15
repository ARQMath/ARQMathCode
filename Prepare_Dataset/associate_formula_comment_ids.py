"""
The goal of this code is to associate each formula in the TSV file to its related comment id
It reads the TSV formula files and select the formulas in the comments.
In the released versions of ARQMath-1 and -2, the column post id showed what post this formula was located in and
not exactly which comment. This code creates a TSV file first column showing the formula id and the second column
showing the comment id.
"""
import html
import os
import csv
import argparse
import sys
conf_path = os.getcwd()
sys.path.append(conf_path)

from Prepare_Dataset.generate_comment_xml import match_to_pattern, check_existence
from bs4 import BeautifulSoup
from Entity_Parser_Record.comment_parser_record import CommentParserRecord


def read_formula_file(directory):
    """
    This method reads the formula files and returns a dictionary of post id: dictionary of formula id, latex
    """
    dic_post_id_formula = {}
    counter = 0
    for file in os.listdir(directory):
        with open(directory + "/" + str(file), 'r', newline='', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            next(csv_reader)
            for row in csv_reader:
                doc_type = row[3]
                if doc_type != "comment":
                    continue
                counter += 1
                formula_id = int(row[0])
                post_id = int(row[1])
                latex = row[5]
                if post_id in dic_post_id_formula:
                    dic_post_id_formula[post_id][formula_id] = latex
                else:
                    dic_post_id_formula[post_id] = {formula_id: latex}
    return dic_post_id_formula


def find_already_assigned_formula_ids(cr):
    """
    Some of the formulas that were previously annotated with math-container in Comment.xml file, were wrongly annotated
    For example for formula `d`, a letter from the word didn't was in math-container. This method, removed previously
    annotated formulas
    """
    for comment_id in cr.map_just_comments:
        comment_body = cr.map_just_comments[comment_id].text
        soup = BeautifulSoup(comment_body)
        spans = soup.find_all('span', {'class': 'math-container'})
        for span in spans:
            if span.has_attr('id'):
                cr.map_just_comments[comment_id].text = comment_body.replace(str(span), span.text, 1)
    return


def associate_formula_id_with_comment_id(comment_file_path, directory, accociation_file):
    # this method associate formula ids to comment ids (as tsv file)
    # reading xml comment file
    cr = CommentParserRecord(comment_file_path)

    # find the formulas that are already assigned to comments (in comment xml file they are in math-container tag
    # with id)
    find_already_assigned_formula_ids(cr)
    dic_formula_id_comment_id = {}
    # reading formulas ids from tsv; those in comments
    # dictionary --> post id : list tuples (formula id, latex)
    dic_post_id_formula = read_formula_file(directory)

    lst_not_found_formula = []
    for post_id in dic_post_id_formula:
        if post_id not in cr.map_of_comments_for_post:
            lst_not_found_formula.extend(list(dic_post_id_formula[post_id].keys()))
            continue

        # sort by length
        dic_formulas_in_comments = dic_post_id_formula[post_id]
        sorted_keys = sorted(dic_formulas_in_comments, key=lambda k: len(dic_formulas_in_comments[k]), reverse=True)

        # list comments
        for formula_id in sorted_keys:
            # formula already assigned
            if formula_id in dic_formula_id_comment_id:
                continue
            latex = dic_formulas_in_comments[formula_id]
            find = False
            for comment in cr.map_of_comments_for_post[post_id]:
                comment.text = html.unescape(comment.text)
                map_index = match_to_pattern(latex, comment.text)
                exists = check_existence(map_index)

                if exists:
                    sorted_x = sorted(map_index.items(), key=lambda kv: kv[1])
                    for item in sorted_x:
                        if item[1] != -1:
                            detected_formula = item[0]
                            dic_formula_id_comment_id[formula_id] = comment.id
                            comment.text = comment.text.replace(detected_formula, "XFXFX_" + str(formula_id), 1)
                            find = True
                            break
                    if find:
                        break
            if not find:
                lst_not_found_formula.append(formula_id)

    with open(accociation_file, mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for formula_id in dic_formula_id_comment_id:
            csv_writer.writerow([str(formula_id), str(dic_formula_id_comment_id[formula_id])])

    with open("missed_formulas_comment_before_correction.txt", "w", encoding="utf-8") as file:
        for formula_id in lst_not_found_formula:
            file.write(str(formula_id) + "\n")

    print(str(len(lst_not_found_formula)) + " formulas in TSV are not in comment file")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-oc', type=str, help='comment file path')
    parser.add_argument('-ldir', type=str, help='laTex TSV files directory')
    args = vars(parser.parse_args())

    comment_file = args['oc']
    latex_dir = args['ldir']
    association_file = "formula_comment_id.tsv"
    associate_formula_id_with_comment_id(comment_file, latex_dir, association_file)


if __name__ == '__main__':
    main()
