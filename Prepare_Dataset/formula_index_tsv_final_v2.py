import argparse
import csv
import os
import sys

from tqdm import tqdm

conf_path = os.getcwd()
sys.path.append(conf_path)
csv.field_size_limit(sys.maxsize)


def read_visual_file(visual_file_path):
    dic_formula_visual_id = {}
    with open(visual_file_path, 'r', newline='', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quoting=csv.QUOTE_ALL)
        for row in csv_reader:
            formula_id = int(row[0])
            new_visual_id = row[1]
            old_visual_id = row[2]
            dic_formula_visual_id[formula_id] = (new_visual_id, old_visual_id)
    return dic_formula_visual_id


def read_intermediate_files(intermediate_conversion_directory, file_id):
    dic_formula_id_slt = {}
    dic_formula_id_opt = {}

    with open(intermediate_conversion_directory + "/slt_" + str(file_id) + ".tsv", 'r', newline='',
              encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quoting=csv.QUOTE_ALL)
        for row in csv_reader:
            formula_id = int(row[0])
            math_ml = row[1]
            dic_formula_id_slt[formula_id] = math_ml
    with open(intermediate_conversion_directory + "/opt_" + str(file_id) + ".tsv", 'r', newline='',
              encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quoting=csv.QUOTE_ALL)
        for row in csv_reader:
            formula_id = int(row[0])
            math_ml = row[1]
            dic_formula_id_opt[formula_id] = math_ml
    return dic_formula_id_slt, dic_formula_id_opt


def read_latex_tsvs(latex_tsv_directory, dic_formula_id_slt, dic_formula_id_opt, dic_corrected_formula_visual_id,
                    lst_not_found_formula_post, dic_formula_id_comment_id, file_id, result_dir):
    latex_sub_dir = result_dir + "/latex_representation"
    slt_sub_dir = result_dir + "/slt_representation"
    opt_sub_dir = result_dir + "/opt_representation"

    dic_formula_id_latex = {}
    dic_formula_id_info = {}
    dic_formula_id_visual_id = {}

    result_latex = open(latex_sub_dir + "/" + file_id + ".tsv", "w", newline='', encoding="utf-8")
    result_slt = open(slt_sub_dir + "/" + file_id + ".tsv", "w", newline='', encoding="utf-8")
    result_opt = open(opt_sub_dir + "/" + file_id + ".tsv", "w", newline='', encoding="utf-8")
    csv_writer_latex = csv.writer(result_latex, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    csv_writer_slt = csv.writer(result_slt, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    csv_writer_opt = csv.writer(result_opt, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    with open(latex_tsv_directory + "/" + file_id + ".tsv", 'r', newline='', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quoting=csv.QUOTE_ALL)
        next(csv_reader)
        csv_writer_latex.writerow(
            ["id", "post_id", "thread_id", "type", "comment_id", "old_visual_id", "visual_id", "issue", "formula"])
        csv_writer_slt.writerow(
            ["id", "post_id", "thread_id", "type", "comment_id", "old_visual_id", "visual_id", "issue", "formula"])
        csv_writer_opt.writerow(
            ["id", "post_id", "thread_id", "type", "comment_id", "old_visual_id", "visual_id", "issue", "formula"])

        for row in csv_reader:
            formula_id = int(row[0])
            other_info = row[1:4]
            old_visual_id = row[4]
            latex = row[5]
            dic_formula_id_latex[formula_id] = latex
            dic_formula_id_info[formula_id] = other_info
            dic_formula_id_visual_id[formula_id] = old_visual_id
        correct_formulas_list = list(set(dic_formula_id_latex.keys()) - set(lst_not_found_formula_post))
        print("correct formula ids: " + str(len(dic_formula_id_latex.keys())))
        print("correct formula ids: " + str(len(correct_formulas_list)))
        # for item in dic_formula_id_latex:
        #     if item not in lst_not_found_formula_post:
        #         print(item)
        #         input("wait")
        print("generating index TSV files")
        for formula_id in tqdm(sorted(dic_formula_id_latex)):
            not_found = False
            changed = False
            latex = dic_formula_id_latex[formula_id]
            old_visual_id = dic_formula_id_visual_id[formula_id]
            new_visual_id = old_visual_id
            if formula_id in dic_corrected_formula_visual_id:
                new_visual_id = dic_corrected_formula_visual_id[formula_id][0]
                changed = True

            if formula_id not in correct_formulas_list:
                not_found = True

            if formula_id in dic_formula_id_slt:
                slt = dic_formula_id_slt[formula_id]
            else:
                slt = ''
            if formula_id in dic_formula_id_opt:
                opt = dic_formula_id_opt[formula_id]
            else:
                opt = ''

            if formula_id in dic_formula_id_comment_id:
                comment_id = dic_formula_id_comment_id[formula_id]
            else:
                comment_id = ''
            if changed and not_found:
                issue = 'dv'
            elif changed:
                issue = 'v'
            elif not_found:
                issue = 'd'
            else:
                issue = ''
            csv_writer_latex.writerow(
                [formula_id, dic_formula_id_info[formula_id][0], dic_formula_id_info[formula_id][1], dic_formula_id_info[formula_id][2], comment_id, old_visual_id, new_visual_id, issue,
                 latex])
            csv_writer_slt.writerow(
                [formula_id, dic_formula_id_info[formula_id][0], dic_formula_id_info[formula_id][1], dic_formula_id_info[formula_id][2], comment_id, old_visual_id, new_visual_id, issue,
                 slt])

            csv_writer_opt.writerow(
                [formula_id, dic_formula_id_info[formula_id][0], dic_formula_id_info[formula_id][1], dic_formula_id_info[formula_id][2], comment_id, old_visual_id, new_visual_id, issue,
                 opt])

    result_latex.close()
    result_slt.close()
    result_opt.close()


def read_not_found(file_path):
    lst_not_found_formula = []
    file = open(file_path, 'r', encoding="utf-8")
    line = file.readline()
    while line:
        line = line.strip()
        lst_not_found_formula.append(int(line))
        line = file.readline()
    file.close()
    return lst_not_found_formula


def read_formula_comment_id_file(comment_formula_association):
    dic_formula_comment_id = {}
    with open(comment_formula_association, 'r', newline='', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quoting=csv.QUOTE_ALL)
        for row in csv_reader:
            dic_formula_comment_id[int(row[0])] = row[1]
    return dic_formula_comment_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ldir', type=str, help='latex directory')
    parser.add_argument('-v', type=str, help='visual id file that has new visual ids for wrongly assigned formulas')
    parser.add_argument('-con', type=str, help='directory of intermediate MathML conversion results')
    parser.add_argument('-nc', type=str, help='file having the ids for formula in the comment not in the collection')
    parser.add_argument('-np', type=str, help='file having the ids for formula where post was not available')
    parser.add_argument('-nf', type=str, help='file having formulas not in the post')
    parser.add_argument('-c', type=str, help='file associating formula and comment ids')
    parser.add_argument('-res', type=str, help='results directory where the results are saved in')
    args = vars(parser.parse_args())

    latex_directory = args['ldir']
    visual_id_file = args['v']
    intermediate_conversion_directory = args['con']
    not_in_comment = args['nc']
    not_in_post = args['np']
    not_found_formula = args['nf']
    comment_formula_association = args['c']
    result_dir = args['res']

    print("reading visual id file")
    dic_corrected_formula_visual_id = read_visual_file(visual_id_file)

    print("reading missed formulas")
    lst_not_found_formula_post = read_not_found(not_found_formula)
    lst_not_found_formula_post.extend(read_not_found(not_in_post))
    lst_not_found_formula_post.extend(read_not_found(not_in_comment))
    print("formula_not_found:" + str(len(lst_not_found_formula_post)))
    print("reading formula comment association file")
    dic_formula_id_comment_id = read_formula_comment_id_file(comment_formula_association)


    print("reading intermediate conversion files")
    for file in os.listdir(latex_directory):
        f_id = file.split(".")[0]
        dic_formula_id_slt, dic_formula_id_opt = read_intermediate_files(intermediate_conversion_directory, str(f_id))
        read_latex_tsvs(latex_directory, dic_formula_id_slt, dic_formula_id_opt, dic_corrected_formula_visual_id,
                        lst_not_found_formula_post, dic_formula_id_comment_id, str(f_id), result_dir)


if __name__ == "__main__":
    main()
