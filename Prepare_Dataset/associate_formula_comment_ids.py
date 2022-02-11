"""
The goal of this code is to associate each formula in the TSV file to its related comment id
It reads the TSV formula files and select the formulas in the comments.
In the released versions of ARQMath-1 and -2, the column post id showed what post this formula was located in and
not exactly which comment. This code creates a TSV file first column showing the formula id and the second column
showing the comment id.
"""

import os
import csv
import argparse
import sys
conf_path = os.getcwd()
sys.path.append(conf_path)
from bs4 import BeautifulSoup
from Prepare_Dataset.re_generate_post import match_to_pattern, check_existence
from Entity_Parser_Record.comment_parser_record import CommentParserRecord


def read_formula_file(directory):
    """
    This method reads the formula files and returns a dictionary of post id: dictionary of formula id, latex
    """
    dic_post_id_formula = {}
    counter = 0
    for file in os.listdir(directory):
        with open(directory +"/"+ str(file), 'r', newline='', encoding="utf-8") as csv_file:
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
    In the previous XML files released in ARQMath-1 and -2 some formulas were already assigned
    to comment and were inside a math-container tag. This method finds these formulas and returns
    dictionary of formula id: comment id
    """
    dic_formula_comment_id = {}
    for comment_id in cr.map_just_comments:
        comment_body = cr.map_just_comments[comment_id].text
        soup = BeautifulSoup(comment_body)
        spans = soup.find_all('span', {'class': 'math-container'})
        for span in spans:
            if span.has_attr('id'):
                cr.map_just_comments[comment_id].text = comment_body.replace(str(span), span.text, 1)
    return dic_formula_comment_id


def associate_formula_id_with_comment_id(comment_file_path, directory, accociation_file):
    # this method associate formula ids to comment ids (as tsv file)
    # reading xml comment file
    cr = CommentParserRecord(comment_file_path)

    # find the formulas that are already assigned to comments (in comment xml file they are in math-container tag with id)
    find_already_assigned_formula_ids(cr)
    dic_formula_id_comment_id = {}
    # reading formulas ids from tsv; those in comments
    # dictionary --> post id : list tuples (formula id, latex)
    dic_post_id_formula = read_formula_file(directory)

    not_found_count = 0
    for post_id in dic_post_id_formula:
        if post_id not in cr.map_of_comments_for_post:
            not_found_count += len(dic_post_id_formula[post_id])
            continue


        #sort by length
        dic_formulas_in_comments = dic_post_id_formula[post_id]
        sorted_keys = sorted(dic_formulas_in_comments, key=lambda k: len(dic_formulas_in_comments[k]), reverse=True)

        # list comments
        lst_comments = cr.map_of_comments_for_post[post_id]
        for formula_id in sorted_keys:
            # formula already assigned
            if formula_id in dic_formula_id_comment_id:
                continue

            latex = dic_formulas_in_comments[formula_id]
            find = False
            for comment in lst_comments:
                if check_existence(match_to_pattern(latex, comment.text)):
                    dic_formula_id_comment_id[formula_id] = comment.id
                    comment.text = comment.text.replace(latex, "XFXFX", 1)
                    find = True
                    break
            if not find:
                not_found_count += 1

    with open(accociation_file, mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for formula_id in dic_formula_id_comment_id:
            csv_writer.writerow([str(formula_id), str(dic_formula_id_comment_id[formula_id])])

    print(str(not_found_count) + " formulas in TSV are not in comment file")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-com', type=str, help='comment file path')
    parser.add_argument('-ldir', type=str, help='laTex TSV files directory')
    args = vars(parser.parse_args())

    comment_file = args['com']
    latex_dir = args['ldir']
    association_file = "formula_comment_id.tsv"
    associate_formula_id_with_comment_id(comment_file, latex_dir, association_file)


if __name__ == '__main__':
    main()
