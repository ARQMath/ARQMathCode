import csv
import html
import os
import sys

from tqdm import tqdm

csv.field_size_limit(sys.maxsize)


def read_conversion_file(file_path):
    """
    Read math file and apply cleaning
    @param file_path:
    @return:
    """
    dic_formula_id_representation = {}
    with open(file_path, encoding="utf-8", newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
        for row in csv_reader:
            formula_id = int(row[0])
            math_ml = row[1]
            math_ml = math_ml.replace("<?xml version=\'1.0\' encoding=\'UTF-8\'?>", "")
            math_ml = math_ml.replace("<mpadded lspace=\"3.3pt\" width=\"+3.3pt\">", "")
            math_ml = math_ml.replace("~{}\\text", "\\text")
            math_ml = math_ml.replace("</mpadded>", "")
            dic_formula_id_representation[formula_id] = math_ml
    return dic_formula_id_representation


def real_all_latex_files(latex_tsv_directory):
    """
    Read Latex files
    @param latex_tsv_directory:
    @return:
    """
    dic_formula_id_latex = {}
    for filename in os.listdir(latex_tsv_directory):
        with open(latex_tsv_directory + "/" + filename, encoding="utf-8", newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            next(csv_reader)
            for row in csv_reader:
                formula_id = int(row[0])
                latex_string = row[5]
                latex_string = latex_string.replace(" ", "")
                dic_formula_id_latex[formula_id] = latex_string
    return dic_formula_id_latex


def read_files_in_result_dir(result_dir, representation):
    dic_formula_representations = {}
    for filename in os.listdir(result_dir):
        if not filename.startswith(representation):
            continue
        temp_dic = read_conversion_file(result_dir + "/" + filename)
        dic_formula_representations.update(temp_dic)
    return dic_formula_representations


def read_slt_files_write_with_cleaning(round_one_result, round_two_result, latex_dir):
    print("read LaTex files")
    dic_formula_id_latex = real_all_latex_files(latex_dir)

    # Read SLT conversion files
    print("read SLT files")
    dic_formula_slt_representation = read_files_in_result_dir(round_one_result, "slt")
    if round_one_result != round_two_result:
        temp = read_files_in_result_dir(round_two_result, "slt")
        dic_formula_slt_representation.update(temp)
    # Read OPT conversion files
    print("read OPT files")
    dic_formula_opt_representation = read_files_in_result_dir(round_one_result, "opt")
    if round_one_result != round_two_result:
        temp = read_files_in_result_dir(round_two_result, "opt")
        dic_formula_opt_representation.update(temp)

    # Build dictionaries based on LaTex String
    print("matching LaTex to representations")
    dic_latex_representations_slt = {}
    for formula_id in dic_formula_slt_representation:
        representation = dic_formula_slt_representation[formula_id]
        latex = dic_formula_id_latex[formula_id]
        if representation != '':
            dic_latex_representations_slt[latex] = representation
    dic_latex_representations_opt = {}
    for formula_id in dic_formula_opt_representation:
        representation = dic_formula_opt_representation[formula_id]
        latex = dic_formula_id_latex[formula_id]
        if representation != '':
            dic_latex_representations_opt[latex] = representation

    print("checking if representations are extracted by other batches")
    final_slt_rep = {}
    final_opt_rep = {}
    for formula_id in dic_formula_id_latex:
        if formula_id not in dic_formula_slt_representation:
            slt = ''
        else:
            slt = dic_formula_slt_representation[formula_id]
        if formula_id not in dic_formula_opt_representation:
            opt = ''
        else:
            opt = dic_formula_opt_representation[formula_id]
        if slt == '':
            latex = dic_formula_id_latex[formula_id]
            if latex in dic_latex_representations_slt:
                slt = dic_latex_representations_slt[latex]
        if opt == '':
            latex = dic_formula_id_latex[formula_id]
            if latex in dic_latex_representations_opt:
                opt = dic_latex_representations_opt[latex]
        final_slt_rep[formula_id] = slt
        final_opt_rep[formula_id] = opt
    return final_slt_rep, final_opt_rep


def read_failed_file(conversion_result_dir):
    dic_failed_formulas = {}
    for filename in os.listdir(conversion_result_dir):
        if not filename.startswith("failed"):
            continue
        with open(conversion_result_dir+"/"+filename, "r", encoding="utf-8") as file:
            file_id = filename.split(".")[0].split("_")[1]
            lst_failed_formulas = []
            line = file.readline()
            while line:
                line = line.strip()
                lst_failed_formulas.append(int(line))
                line = file.readline()
            dic_failed_formulas[file_id] = lst_failed_formulas
    return dic_failed_formulas


def read_not_passed_formulas(conversion_result_dir):
    lst_failed_formulas = []
    for filename in os.listdir(conversion_result_dir):
        if not filename.startswith("not_"):
            continue
        with open(conversion_result_dir + "/" + filename, "r", encoding="utf-8") as file:

            line = file.readline()
            while line:
                line = line.strip()
                lst_failed_formulas.append(int(line))
                line = file.readline()
    return lst_failed_formulas


def combine_results(round_one_result, round_two_result, combined_result, latex_dir):
    dic_formula_id_slt, dic_formula_id_opt = read_slt_files_write_with_cleaning(round_one_result, round_two_result, latex_dir)
    final_failed_count = 0
    final_formula_count = 0
    for filename in os.listdir(latex_dir):
        file_id = filename.split(".")[0]
        result_file_slt = open(combined_result + "/slt_" + file_id + ".tsv", "w", newline='', encoding="utf-8")
        csv_writer_slt = csv.writer(result_file_slt, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        result_file_opt = open(combined_result + "/opt_" + file_id + ".tsv", "w", newline='', encoding="utf-8")
        csv_writer_opt = csv.writer(result_file_opt, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        result_file_failed = open(combined_result + "/failed_" + file_id + ".tsv", "w", newline='', encoding="utf-8")
        csv_writer_failed = csv.writer(result_file_failed, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        with open(latex_dir + "/" + filename, newline='', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            next(csv_file)
            for row in csv_reader:
                formula_id = int(row[0])
                if formula_id not in dic_formula_id_slt:
                    slt = ''
                else:
                    slt = dic_formula_id_slt[formula_id]
                if formula_id not in dic_formula_id_opt:
                    opt = ''
                else:
                    opt = dic_formula_id_opt[formula_id]
                csv_writer_slt.writerow([str(formula_id), slt])
                csv_writer_opt.writerow([str(formula_id), opt])
                if slt == '':
                    final_failed_count += 1
                    csv_writer_failed.writerow([str(formula_id)])
                final_formula_count += 1
        result_file_slt.close()
        result_file_opt.close()
        result_file_failed.close()
    print("there are total of " + str(final_formula_count) + " formulas")
    print(str(final_failed_count) + " formulas failed during conversion")
    return final_formula_count, final_failed_count


def get_first_round_failures(conversion_result_dir, latex_tsv_directory, final_round_1):
    lst_not_pass_formula_ids = read_not_passed_formulas(conversion_result_dir)
    print("not passed count: " + str(len(lst_not_pass_formula_ids)))
    dic_formula_representations = read_slt_files_write_with_cleaning(conversion_result_dir, conversion_result_dir, latex_tsv_directory)

    dic_failed_formulas = read_failed_file(conversion_result_dir)
    remained = 0

    for filename in os.listdir(latex_tsv_directory):
        print(filename)
        failed_file_id = open(final_round_1 + "failed/" + filename, "w", newline='', encoding="utf-8")
        csv_writer_failed = csv.writer(failed_file_id, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        lst_failed_formulas = dic_failed_formulas[filename.split(".")[0]]
        for formula_id in lst_failed_formulas:
            presentation = dic_formula_representations[formula_id]
            if presentation == '':
                csv_writer_failed.writerow([formula_id, presentation])
                remained += 1
        failed_file_id.close()
    print(str(remained)+" formulas are failed during conversion")
