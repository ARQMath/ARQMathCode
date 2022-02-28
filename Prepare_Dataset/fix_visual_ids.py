import os
import csv

import argparse
from tangentcft.TangentS.math_tan.math_extractor import MathExtractor
import sys

csv.field_size_limit(sys.maxsize)


def read_qrel_formula_id_file(qrel_file):
    dic_formula_id = {}
    with open(qrel_file, newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
        for row in csv_reader:
            formula_id = int(row[0])
            score = int(row[3])
            if formula_id in dic_formula_id:
                if score > dic_formula_id[formula_id]:
                    dic_formula_id[formula_id] = score
            else:
                dic_formula_id[formula_id] = score
    return dic_formula_id


def read_raw_new_slt_files(slt_intermediate_directory):
    dic_formula_id_slt = {}
    for filename in os.listdir(slt_intermediate_directory):
        if not filename.startswith("slt"):
            continue
        with open(slt_intermediate_directory + "/" + filename, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            for row in csv_reader:
                formula_id = int(row[0])
                slt = row[1]
                dic_formula_id_slt[formula_id] = slt
    return dic_formula_id_slt


def read_slt_files(slt_intermediate_directory):
    dic_formula_id_slt_string = {}
    for filename in os.listdir(slt_intermediate_directory):
        if not filename.startswith("slt"):
            continue
        with open(slt_intermediate_directory + "/" + filename, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            for row in csv_reader:
                formula_id = int(row[0])
                slt = row[1]
                try:
                    slt_string = MathExtractor.parse_from_xml_opt(slt, 1)[0].tostring()
                    dic_formula_id_slt_string[formula_id] = slt_string
                except:
                    continue
    return dic_formula_id_slt_string


def read_latex_files(latex_tsv_directory, dic_formula_id_slt_string):
    dic_formula_id_latex_string = {}
    dic_visual_id_formula_id_list = {}

    dic_slt_string_visual_id = {}
    dic_latex_visual_id = {}
    for filename in os.listdir(latex_tsv_directory):
        with open(latex_tsv_directory + "/" + filename, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            next(csv_reader)
            for row in csv_reader:
                formula_id = int(row[0])
                visual_id = int(row[4])
                latex_string = row[5]
                latex_string = latex_string.replace(" ", "")
                # Saving the correct visual ids

                if formula_id in dic_formula_id_slt_string:
                    slt_string = dic_formula_id_slt_string[slt_string]
                    dic_slt_string_visual_id[slt_string] = visual_id
                    dic_latex_visual_id[latex_string] = visual_id
                else:
                    dic_latex_visual_id[latex_string] = visual_id

                dic_formula_id_latex_string[formula_id] = latex_string
                if visual_id in dic_visual_id_formula_id_list:
                    dic_visual_id_formula_id_list[visual_id].append(formula_id)
                else:
                    dic_visual_id_formula_id_list[visual_id] = [formula_id]
    return dic_formula_id_latex_string, dic_visual_id_formula_id_list, dic_slt_string_visual_id, dic_latex_visual_id


def validate_visual_ids(dic_visual_id_formula_id_list, dic_formula_id_latex_string, dic_formula_id_slt_string,
                        result_file_path):
    lst_issues_visual_id = []
    with open(result_file_path, "w", encoding="utf-8", newline='') as result_file:
        csv_writer = csv.writer(result_file, delimiter='\t')
        csv_writer.writerow(["visual_id", "#unique_slts", "#unique_latex", "representations"])
        for visual_id in dic_visual_id_formula_id_list:
            lst_formula_ids = dic_visual_id_formula_id_list[visual_id]
            lst_slt_string = []
            lst_latex_string = []
            for formula_id in lst_formula_ids:
                if formula_id in dic_formula_id_slt_string:
                    lst_slt_string.append(dic_formula_id_slt_string[formula_id])
                elif formula_id in dic_formula_id_latex_string:
                    lst_latex_string.append(dic_formula_id_latex_string[formula_id])
            slts = set(lst_slt_string)
            latexs = set(lst_latex_string)
            has_issue = False
            if len(slts) > 0 and len(latexs) > 0:
                lst_issues_visual_id.append(visual_id)
                has_issue = True
            elif len(slts) > 1:
                lst_issues_visual_id.append(visual_id)
                has_issue = True
            elif len(latexs) > 1:
                lst_issues_visual_id.append(visual_id)
                has_issue = True
            if has_issue:
                temp_list = [str(visual_id), str(len(slts)), str(len(latexs))]
                temp_list.extend(lst_slt_string)
                temp_list.extend(lst_latex_string)
                csv_writer.writerow(temp_list)

    return lst_issues_visual_id


def write_visual_ids_with_error_to_file(converted_slt_directory, latex_files_directory, result_file_path):
    print("reading SLT files...\n")
    dic_formula_id_slt_string = read_slt_files(converted_slt_directory)
    print("reading LaTex file...\n")
    dic_formula_id_latex_string, dic_visual_id_formula_id_list, dic_slt_string_visual_id, dic_latex_visual_id = read_latex_files(
        latex_files_directory,
        dic_formula_id_slt_string)
    print("finding visual ids with wrong formula(s) in them... \n")
    lst_issues_visual_id = validate_visual_ids(dic_visual_id_formula_id_list, dic_formula_id_latex_string,
                                               dic_formula_id_slt_string, result_file_path)
    for item in dic_latex_visual_id:
        if dic_latex_visual_id[item] in lst_issues_visual_id:
            del dic_latex_visual_id[item]
    for item in dic_slt_string_visual_id:
        if dic_slt_string_visual_id[item] in lst_issues_visual_id:
            del dic_slt_string_visual_id[item]
    return lst_issues_visual_id, dic_visual_id_formula_id_list, dic_formula_id_slt_string, dic_formula_id_latex_string, dic_slt_string_visual_id, dic_latex_visual_id


def find_changing_formulas(lst_formula_ids, dic_formula_id_slt_string, dic_formula_id_latex_string,
                           qrel_formula_id_score_dic):
    """
    This functions decides which formula id should have a new visual id
    @param lst_formula_ids: list of formula ids in cluster
    @param dic_formula_id_slt_string: dict formula id: slt string
    @param dic_formula_id_latex_string: dict formula id: latex string
    @param qrel_formula_id_score_dic: formula id and max score assigned to it in the qrel file
    @return: list of formula ids that need to be assigned to a new cluster
    """
    dictionary_of_items = {}
    for formula_id in lst_formula_ids:
        # Get formula counts in each sub-cluster
        if formula_id in dic_formula_id_slt_string:
            slt_string = dic_formula_id_slt_string[formula_id]
            if slt_string in dictionary_of_items:
                dictionary_of_items[slt_string].append(formula_id)
            else:
                dictionary_of_items[slt_string] = [formula_id]
        else:
            latex = dic_formula_id_latex_string[formula_id]
            if latex in dictionary_of_items:
                dictionary_of_items[latex].append(formula_id)
            else:
                dictionary_of_items[latex] = [formula_id]

    # ############# Finding the maximum cluster
    formulas_changing = []
    # Sort sub clusters based on the number of formulas in them
    soreted_item_list = sorted(dictionary_of_items, key=lambda k: len(dictionary_of_items[k]), reverse=True)
    lst_formulas_with_max = []

    max_number = len(dictionary_of_items[soreted_item_list[0]])
    for key_item in soreted_item_list:
        # what ever is not in the maximum sub-cluster will be changed
        if len(dictionary_of_items[key_item]) != max_number:
            formulas_changing.extend(dictionary_of_items[key_item])
        else:  # if the formulas are in the maximum cluster(s) we need further tie breaking
            lst_formulas_with_max.append(key_item)
    # if there is only one maximum cluster then we are done
    if len(lst_formulas_with_max) < 2:
        return formulas_changing

    # Breaking Ties based on Qrel
    count_qrels = {}
    # Going through sub-clusters with same number of formulas (max)
    for item in lst_formulas_with_max:
        formula_lst = dictionary_of_items[item]
        for formula_id in formula_lst:
            if formula_id in qrel_formula_id_score_dic:
                score = qrel_formula_id_score_dic[formula_id]
                if item in count_qrels:
                    count_qrels[item].append(score)
                else:
                    count_qrels[item] = [score]
    # None of the formula ids in the bigger sub clusters were in QREL file so the tie is broken based on formula id
    if len(count_qrels.keys()) == 0:
        min_formula_id = 30000000
        selected_item = None
        for item in lst_formulas_with_max:
            formula_lst = dictionary_of_items[item]
            min_formula_id_temp = min(formula_lst)
            if min_formula_id_temp < min_formula_id:
                min_formula_id = min_formula_id_temp
                selected_item = item
        for item in lst_formulas_with_max:
            if item != selected_item:
                formulas_changing.extend(dictionary_of_items[item])
        return formulas_changing

    for item in count_qrels:
        count_qrels[item] = max(count_qrels[item])
    max_score = -1
    for item in lst_formulas_with_max:
        if item not in count_qrels:
            formulas_changing.extend(dictionary_of_items[item])
        else:
            score = count_qrels[item]
            if score > max_score:
                max_score = score
    for item in count_qrels:
        if count_qrels[item] != max_score:
            formulas_changing.extend(dictionary_of_items[item])
            del count_qrels[item]
    if len(count_qrels.keys()) < 2:
        return formulas_changing
    # break tie base on scores
    min_formula_id = -1
    for item in count_qrels:
        formula_lst = dictionary_of_items[item]
        min_formula_id_temp = min(formula_lst)
        if min_formula_id_temp < min_formula_id:
            min_formula_id = min_formula_id_temp
            selected_item = item
    for item in count_qrels:
        if item != selected_item:
            formulas_changing.extend(dictionary_of_items[item])
    return formulas_changing


def fix_error(lst_issues_visual_id, dic_visual_id_formula_id_list, dic_formula_id_slt_string,
              dic_formula_id_latex_string, dic_slt_string_visual_id, dic_latex_visual_id, qrel_formula_id_score_dic):
    next_visual_id = max(list(dic_visual_id_formula_id_list.keys())) + 1
    dic_new_formula_visual_ids = {}
    for visual_id in lst_issues_visual_id:
        lst_formula_ids = dic_visual_id_formula_id_list[visual_id]
        formulas_changing = find_changing_formulas(lst_formula_ids, dic_formula_id_slt_string,
                                                   dic_formula_id_latex_string, qrel_formula_id_score_dic)
        # ###############
        for formula_id in formulas_changing:
            if formula_id in dic_formula_id_slt_string:
                slt_string = dic_formula_id_slt_string[formula_id]
                # check existence
                if slt_string in dic_slt_string_visual_id:
                    new_visual_id = dic_slt_string_visual_id[slt_string]
                else:  # if not put and update visual_ids
                    new_visual_id = next_visual_id
                    dic_slt_string_visual_id[slt_string] = next_visual_id
                    next_visual_id += 1
                dic_new_formula_visual_ids[formula_id] = (new_visual_id, visual_id)
            else:
                latex = dic_formula_id_latex_string[formula_id]
                # check existence
                if latex in dic_latex_visual_id:
                    new_visual_id = dic_latex_visual_id[latex]
                else:  # if not put and update visual_ids
                    new_visual_id = next_visual_id
                    dic_latex_visual_id[latex] = next_visual_id
                    next_visual_id += 1
                dic_new_formula_visual_ids[formula_id] = (new_visual_id, visual_id)

    return dic_new_formula_visual_ids


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ldir', type=str, help='latex directory')
    parser.add_argument('-con', type=str, help='directory having MathML representations from conversions with LaTeXML')
    parser.add_argument('-qrel', type=str, help='ARQMath-2 qrel file with formula ids')
    parser.add_argument('-res', type=str, help='result file having (formula id, new visual id, old visual id)')

    args = vars(parser.parse_args())

    slt_directory = args['con']
    latex_directory = args['ldir']
    file_path_changed_visual_ids = args['res']
    qrel_file = args['qrel']
    file_path_visual_ids_with_issue = "visual_ids_with_issue.txt"

    lst_issues_visual_id, dic_visual_id_formula_id_list, dic_formula_id_slt_string, dic_formula_id_latex_string, dic_slt_string_visual_id, dic_latex_visual_id = write_visual_ids_with_error_to_file(
        slt_directory, latex_directory, file_path_visual_ids_with_issue)
    qrel_formula_id_score_dic = read_qrel_formula_id_file(qrel_file)
    print("fixing the visual ids")
    dic_new_formula_visual_ids = fix_error(lst_issues_visual_id, dic_visual_id_formula_id_list,
                                           dic_formula_id_slt_string,
                                           dic_formula_id_latex_string, dic_slt_string_visual_id, dic_latex_visual_id,
                                           qrel_formula_id_score_dic)
    # write changes to file
    with open(file_path_changed_visual_ids, "w", newline='', encoding="utf-8") as result_file:
        csv_writer = csv.writer(result_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for formula_id in dic_new_formula_visual_ids:
            csv_writer.writerow(
                [str(formula_id), dic_new_formula_visual_ids[formula_id][0], dic_new_formula_visual_ids[formula_id][1]])
    print('{} formulae have changed formula id'.format(len(dic_new_formula_visual_ids.keys())))


if __name__ == '__main__':
    main()
