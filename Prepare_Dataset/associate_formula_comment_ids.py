import os
import csv

from bs4 import BeautifulSoup
from os.path import exists
from Entity_Parser_Record.comment_parser_record import CommentParserRecord
from Prepare_Dataset.re_generate_post import match_to_pattern, check_existence


def read_formula_file(directory):
    dic_post_id_formula = {}
    counter = 0
    for file in os.listdir(directory):
        with open(directory + str(file), 'r', newline='', encoding="utf-8") as csv_file:
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
    print(counter)
    return dic_post_id_formula


def find_already_assigned_formula_ids(cr):
    dic_formula_comment_id = {}
    for comment_id in cr.map_just_comments:
        comment_body = cr.map_just_comments[comment_id].text
        soup = BeautifulSoup(comment_body)
        spans = soup.find_all('span', {'class': 'math-container'})
        for span in spans:
            if span.has_attr('id'):
                dic_formula_comment_id[int(span['id'])] = int(comment_id)
    return dic_formula_comment_id


def manage_already_associated_formulas(cr, csv_writer):
    dic_formula_id_comment_id = find_already_assigned_formula_ids(cr)
    for formula_id in dic_formula_id_comment_id:
        csv_writer.writerow([formula_id, dic_formula_id_comment_id[formula_id]])
    return dic_formula_id_comment_id


def associate_formula_id_with_comment_id(comment_file_path, directory, accociation_file):
    # this method associate formula ids to comment ids (as tsv file)
    with open(accociation_file, mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # reading xml comment file
        cr = CommentParserRecord(comment_file_path)

        # find the formulas that are already assigned to comments (in comment xml file they are in math-container tag with id)
        dic_formula_id_comment_id = manage_already_associated_formulas(cr, csv_writer)

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
                        csv_writer.writerow([formula_id, comment.id])
                        # dic_formula_id_comment_id[formula_id] = comment.id
                        comment.text = comment.text.replace(latex, "XFXFX", 1)
                        find = True
                        break
                if not find:
                    not_found_count += 1

        print(not_found_count)


comment_file = "/home/bm3302/Comments.V1.2.xml"
latex_dir = "/home/bm3302/latex_representation_v3/"
accociation_file = "formula_comment_id.tsv"
associate_formula_id_with_comment_id(comment_file, latex_dir, accociation_file)
