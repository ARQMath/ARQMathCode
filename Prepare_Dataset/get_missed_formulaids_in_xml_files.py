import csv
import os

from bs4 import BeautifulSoup

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


def read_arqmath_data(post_file_path, latex_dir):
    pr = PostParserRecord(post_file_path)
    dic_formulas = read_formula_file(latex_dir, False)
    return pr, dic_formulas


def get_missed_formulas(pr, dic_formulas):
    lst_missed_formula_ids = []
    for post_id in dic_formulas:
        lst_formulas = dic_formulas[post_id]
        for formulaid in lst_formulas:
            if post_id in pr.map_questions:
                post = pr.map_questions[post_id]
                if formulaid in post.title:
                    target = post.title
                else:
                    target = post.body
            elif post_id in pr.map_just_answers:
                post = pr.map_just_answers[post_id]
                target = post.body
            else:
                continue
            soup = BeautifulSoup(target)
            spans = soup.find_all('span', {'class': 'math-container', 'id': str(formulaid)})
            if spans is not None and len(spans) > 0:
                continue
            else:
                lst_missed_formula_ids.append(formulaid)
    return lst_missed_formula_ids


def missed_formulas(post_file_path, latex_dir):
    pr, dic_formulas = read_arqmath_data(post_file_path, latex_dir)
    return get_missed_formulas(pr, dic_formulas)


def get_file_missed_formulas_post_file(source_root, missed_id_file_paths):
    lst_formulas = missed_formulas(source_root + "Posts.V1.2.xml", source_root + "latex_representation_v3/")
    print(len(lst_formulas))
    file = open(source_root + missed_id_file_paths, "w")
    for formula_id in lst_formulas:
        file.write(str(formula_id)+"\n")
    file.close()


def get_file_missed_formulas_comment_file(source_root, missed_id_file_paths):
    lst_formulas = missed_formulas(source_root + "Comments.V1.2.xml", source_root + "latex_representation_v3/")
    print(len(lst_formulas))
    file = open(source_root + missed_id_file_paths, "w")
    for formula_id in lst_formulas:
        file.write(str(formula_id)+"\n")
    file.close()


def main():
    source_root = "/home/bm3302/"

    get_file_missed_formulas_post_file(source_root, "missed_formula_ids_arqmath2_post.tsv")
    get_file_missed_formulas_comment_file(source_root, "missed_formula_ids_arqmath2_comment.tsv")


if __name__ == '__main__':
    main()
