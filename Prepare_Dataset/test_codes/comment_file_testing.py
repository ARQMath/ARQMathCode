import csv
import os
import random
import argparse
import sys

conf_path = os.getcwd()
sys.path.append(conf_path)
from Entity_Parser_Record.comment_parser_record import CommentParserRecord


def read_comment_intermediate_file(file_path):
    dic_formula_comment_id = {}
    with open(file_path, mode='r', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        for row in csv_reader:
            formula_id = int(row[0])
            comment_id = int(row[1])
            dic_formula_comment_id[formula_id] = comment_id
    return dic_formula_comment_id


def read_all_formula_files(latex_formula_dir):
    """
        Takes in formula file path and read it line by line and return three dictionaries:
        dic_formula_id_latex:
            key: formula id id, value: latex representation
    """
    dic_formula_id_latex = {}
    for file in os.listdir(latex_formula_dir):
        with open(latex_formula_dir + "/" + file, mode='r', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            next(csv_reader)
            for row in csv_reader:
                doc_type = row[3]
                if doc_type != "comment":
                    continue
                formula_id = int(row[0])
                formula_latex = row[5]
                dic_formula_id_latex[formula_id] = formula_latex
    return dic_formula_id_latex


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ncom', type=str, help='new comment file path')
    parser.add_argument('-ldir', type=str, help='laTex TSV files directory')
    args = vars(parser.parse_args())

    formula_comment_id = "./formula_comment_id.tsv"
    new_xml = args['ncom']
    latex_dir = args['ldir']
    dic_formula_comment_id = read_comment_intermediate_file(formula_comment_id)
    comment_parser = CommentParserRecord(new_xml)
    dic_formula_id_latex = read_all_formula_files(latex_dir)
    list_formula_ids = list(dic_formula_comment_id.keys())
    random.shuffle(list_formula_ids)
    list_formula_ids = list_formula_ids[:10]
    print("formula\tformula id\tcomment")
    for formula_id in list_formula_ids:
        latex = dic_formula_id_latex[formula_id]
        comment_id = dic_formula_comment_id[formula_id]
        comment = comment_parser.map_just_comments[comment_id]
        text = comment.text
        print(str(latex)+"\t"+str(formula_id)+"\t"+str(text)+"\n\n")


if __name__ == '__main__':
    main()
