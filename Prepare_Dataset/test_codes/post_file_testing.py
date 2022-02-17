import csv
import os
import random
import argparse
import sys

from bs4 import BeautifulSoup
from Entity_Parser_Record.post_parser_record import PostParserRecord

conf_path = os.getcwd()
sys.path.append(conf_path)


def read_missed_ids(file_path):
    lst_missed_ids = []
    with open(file_path, mode='r', encoding="utf-8") as file:
        line = file.readline()
        while line:
            lst_missed_ids.append(int(line))
            line = file.readline()
    return lst_missed_ids


def read_all_formula_files(latex_formula_dir, lst_missed_formulas):
    """
        Takes in formula file path and read it line by line and return three dictionaries:
        dic_formula_id_latex:
            key: post id: list valid formula ids in the post
    """
    dic_formula_id_post_id = {}
    dic_formula_id_latex = {}
    for file in os.listdir(latex_formula_dir):
        with open(latex_formula_dir + "/" + file, mode='r', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            next(csv_reader)
            for row in csv_reader:
                doc_type = row[3]
                if doc_type == "comment":
                    continue
                formula_id = int(row[0])
                post_id = int(row[1])
                formula = row[5]
                dic_formula_id_post_id[formula_id] = post_id
                dic_formula_id_latex[formula_id] = (formula, doc_type)
    # Removing formulas id that were not detected
    for formula_id in lst_missed_formulas:
        del dic_formula_id_post_id[formula_id]
        del dic_formula_id_latex[formula_id]
    dic_post_id_formula_ids = {}
    for formula_id in dic_formula_id_post_id:
        post_id = dic_formula_id_post_id[formula_id]
        if post_id in dic_post_id_formula_ids:
            dic_post_id_formula_ids[post_id].append(formula_id)
        else:
            dic_post_id_formula_ids[post_id] = [formula_id]
    return dic_post_id_formula_ids, dic_formula_id_latex


def check_all_formulas_located(post_parser, dic_post_id_formula_ids):
    lst_not_located = []
    for question_id in post_parser.map_questions:
        question = post_parser.map_questions[question_id]
        text = question.title + " " + question.body
        # question has no formula
        if question_id not in dic_post_id_formula_ids:
            continue
        list_formulas = dic_post_id_formula_ids[question_id]
        find_not_located(list_formulas, lst_not_located, text)
    for answer_id in post_parser.map_just_answers:
        text = post_parser.map_just_answers[answer_id].body
        # answer has no formula
        if answer_id not in dic_post_id_formula_ids:
            continue
        list_formulas = dic_post_id_formula_ids[answer_id]
        find_not_located(list_formulas, lst_not_located, text)

    return lst_not_located


def find_not_located(list_formulas, lst_not_located, text):
    soup = BeautifulSoup(text, features="lxml")
    spans = soup.find_all('span', {'class': 'math-container'})
    for formula_id in list_formulas:
        found = False
        for span in spans:
            if span.has_attr('id') and int(span['id']) == formula_id:
                found = True
                break
        if not found:
            if str(formula_id) not in text:
                lst_not_located.append(formula_id)


def generate_visual_test(pr, dic_post_id_formula_ids, dic_formula_id_latex, lst_random_questions, lst_random_answers):
    print("formula\tformula id\tpost")
    for question_id in lst_random_questions:
        if question_id not in dic_post_id_formula_ids:
            print("No formula in this question: \t" + pr.map_questions[question_id].body + "\n\n")
            continue
        lst_formulas = dic_post_id_formula_ids[question_id]
        random.shuffle(lst_formulas)
        formula_id = lst_formulas[0]
        latex = dic_formula_id_latex[formula_id][0]
        doc_type = dic_formula_id_latex[formula_id][1]
        if doc_type == "title":
            text = pr.map_questions[question_id].title
        else:
            text = pr.map_questions[question_id].body
        print(str(latex) + "\t" + str(formula_id) + "\t" + str(text) + "\n\n")
    for answer_id in lst_random_answers:
        if answer_id not in dic_post_id_formula_ids:
            print("No formula in this answer: \t" + pr.map_just_answers[answer_id].body + "\n\n")
            continue
        lst_formulas = dic_post_id_formula_ids[answer_id]
        random.shuffle(lst_formulas)
        formula_id = lst_formulas[0]
        latex = dic_formula_id_latex[formula_id][0]
        text = pr.map_just_answers[answer_id].body
        print(str(latex) + "\t" + str(formula_id) + "\t" + str(text) + "\n\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ncom', type=str, help='new comment file path')
    parser.add_argument('-ldir', type=str, help='laTex TSV files directory')
    args = vars(parser.parse_args())

    missed_formula_post_issue = "./missed_formulas_post_not_available.txt"
    missed_formula_issue = "./missed_formulas_not_available.txt"
    new_xml = args['ncom']
    latex_dir = args['ldir']

    print("Reading Files")
    lst_missed_formulas = read_missed_ids(missed_formula_post_issue)
    lst_missed_formulas.extend(read_missed_ids(missed_formula_issue))
    dic_post_id_formula_ids, dic_formula_id_latex = read_all_formula_files(latex_dir, lst_missed_formulas)

    post_parser = PostParserRecord(new_xml)

    # print("Visual Samples")
    # # Printing 10 random formulas from questions and answers for visual (manual) checking
    # lst_random_questions = list(post_parser.map_questions.keys())
    # random.shuffle(lst_random_questions)
    # lst_random_questions = lst_random_questions[:5]
    # lst_random_answers = list(post_parser.map_just_answers.keys())
    # random.shuffle(lst_random_answers)
    # lst_random_answers = lst_random_answers[:5]
    # generate_visual_test(post_parser, dic_post_id_formula_ids, dic_formula_id_latex, lst_random_questions,
    #                      lst_random_answers)

    print("\nChecking all the formulas located correctly")
    #
    lst_missed_ids = check_all_formulas_located(post_parser, dic_post_id_formula_ids)
    print(str(len(set(lst_missed_ids)))+" formulas are in TSV files and not located in math-container tag in XML file")


if __name__ == '__main__':
    main()
