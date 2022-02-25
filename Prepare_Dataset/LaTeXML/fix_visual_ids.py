import os
import csv
from tangentcft.TangentS.math_tan.math_extractor import MathExtractor
import sys

csv.field_size_limit(sys.maxsize)


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


def read_latex_files(latex_tsv_directory, dic_formula_id_slt_string, lst_visual_id):
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
                if visual_id not in lst_visual_id:
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


def validate_visual_ids(dic_visual_id_formula_id_list, dic_formula_id_latex_string, dic_formula_id_slt_string):
    lst_issues_visual_id = []
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
        if len(slts) > 0 and len(latexs) > 0:
            lst_issues_visual_id.append(visual_id)
        elif len(slts) > 1:
            lst_issues_visual_id.append(visual_id)
        elif len(latexs) > 1:
            lst_issues_visual_id.append(visual_id)
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
                                               dic_formula_id_slt_string)
    with open(result_file_path, "w", encoding="utf-8") as file:
        for visual_id in lst_issues_visual_id:
            file.write(str(visual_id) + "\n")
    return lst_issues_visual_id, dic_visual_id_formula_id_list, dic_formula_id_slt_string, dic_formula_id_latex_string, dic_slt_string_visual_id, dic_latex_visual_id


def find_changing_formulas(lst_formula_ids, dic_formula_id_slt_string, dic_formula_id_latex_string):
    dic_slt_strings = {}
    dic_latex_strings = {}
    for formula_id in lst_formula_ids:
        # Get formula counts
        if formula_id in dic_formula_id_slt_string:
            slt_string = dic_formula_id_slt_string[formula_id]
            if slt_string in dic_slt_strings:
                dic_slt_strings[slt_string].append(formula_id)
            else:
                dic_slt_strings[slt_string] = [formula_id]
        else:
            latex = dic_formula_id_latex_string[formula_id]
            if latex in dic_latex_strings:
                dic_latex_strings[latex].append(formula_id)
            else:
                dic_latex_strings[latex] = [formula_id]
    # ############# Getting the majority formula
    temp_dic = dic_slt_strings.copy()
    temp_dic.update(dic_latex_strings)
    max_counter = -1
    selected_item = None
    formulas_changing = []
    for item in temp_dic:
        if max_counter < len(temp_dic[item]):
            selected_item = item
            max_counter = len(temp_dic[item])
    for item in temp_dic:
        if item != selected_item:
            formulas_changing.extend(dic_latex_strings[item])
    return formulas_changing


def fix_error(lst_issues_visual_id, dic_visual_id_formula_id_list, dic_formula_id_slt_string,
              dic_formula_id_latex_string, dic_slt_string_visual_id, dic_latex_visual_id):
    next_visual_id = max(list(dic_visual_id_formula_id_list.keys())) + 1
    dic_new_formula_visual_ids = {}
    for visual_id in lst_issues_visual_id:
        lst_formula_ids = dic_visual_id_formula_id_list[visual_id]
        formulas_changing = find_changing_formulas(lst_formula_ids, dic_formula_id_slt_string,
                                                   dic_formula_id_latex_string)
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
    slt_directory = sys.argv[1]
    latex_directory = sys.argv[2]
    file_path_visual_ids_with_issue = "visual_ids_with_issue.txt"
    file_path_changed_visual_ids = sys.argv[3]
    lst_issues_visual_id, dic_visual_id_formula_id_list, dic_formula_id_slt_string, dic_formula_id_latex_string, dic_slt_string_visual_id, dic_latex_visual_id = write_visual_ids_with_error_to_file(
        slt_directory, latex_directory, file_path_visual_ids_with_issue)

    print("fixing the visual ids")
    dic_new_formula_visual_ids = fix_error(lst_issues_visual_id, dic_visual_id_formula_id_list, dic_formula_id_slt_string,
              dic_formula_id_latex_string, dic_slt_string_visual_id, dic_latex_visual_id)
    # write changes to file
    with open(file_path_changed_visual_ids, "w", newline='', encoding="utf-8") as result_file:
        csv_writer = csv.writer(result_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for formula_id in dic_new_formula_visual_ids:
            csv_writer.writerow([str(formula_id), dic_new_formula_visual_ids[formula_id][0], dic_new_formula_visual_ids[formula_id][1]])
    print('{} formulae have changed formula id'.format(len(dic_new_formula_visual_ids.keys())))


if __name__ == '__main__':
    main()