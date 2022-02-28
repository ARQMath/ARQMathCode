import argparse
import csv
import os
import sys

conf_path = os.getcwd()
sys.path.append(conf_path)


def read_visual_file(visual_file_path):
    dic_formula_visual_id = {}
    with open(visual_file_path, 'r', newline='', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quoting=csv.QUOTE_ALL)
        for row in csv_reader:
            formula_id = row[0]
            visual_id = row[1]
            dic_formula_visual_id[formula_id] = visual_id
    return dic_formula_visual_id


def read_intermediate_files(intermediate_conversion_directory):
    dic_formula_id_slt = {}
    dic_formula_id_opt = {}
    for file in os.listdir(intermediate_conversion_directory):
        with open(intermediate_conversion_directory + "/" + str(file), 'r', newline='', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quoting=csv.QUOTE_ALL)
            for row in csv_reader:
                formula_id = row[0]
                math_ml = row[1]
                if file.startswith("slt"):
                    dic_formula_id_slt[formula_id] = math_ml
                else:
                    dic_formula_id_opt[formula_id] = math_ml
    return dic_formula_id_slt, dic_formula_id_opt


def read_latex_tsvs(latex_tsv_directory, dic_formula_id_slt, dic_formula_id_opt, dic_formula_visual_id, result_dir):
    os.mkdir(result_dir)
    latex_sub_dir = result_dir+"/latex_representation"
    slt_sub_dir = result_dir+"/slt_representation"
    opt_sub_dir = result_dir+"/opt_representation"
    os.mkdir(latex_sub_dir)
    os.mkdir(slt_sub_dir)
    os.mkdir(opt_sub_dir)

    dic_formula_id_latex = {}
    dic_formula_id_info = {}
    for file in os.listdir(latex_tsv_directory):
        result_latex = open(latex_sub_dir+"/"+file,"w", newline='', encoding="utf-8")
        result_slt = open(slt_sub_dir+"/"+file,"w", newline='', encoding="utf-8")
        result_opt = open(opt_sub_dir+"/"+file,"w", newline='', encoding="utf-8")
        csv_writer_latex = csv.writer(result_latex, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        csv_writer_slt = csv.writer(result_slt, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        csv_writer_opt = csv.writer(result_opt, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        with open(latex_tsv_directory + "/" + str(file), 'r', newline='', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quoting=csv.QUOTE_ALL)
            next(csv_reader)
            csv_writer_latex.writerow(["id", "post_id", "thread_id", "type", "visual_id", "formula"])
            csv_writer_slt.writerow(["id", "post_id", "thread_id", "type", "visual_id", "formula"])
            csv_writer_opt.writerow(["id", "post_id", "thread_id", "type", "visual_id", "formula"])
            for row in csv_reader:
                formula_id = row[0]
                other_info = row[1:4]
                latex = row[4]
                dic_formula_id_latex[formula_id] = latex
                dic_formula_id_info[formula_id] = other_info
            for formula_id in sorted(dic_formula_id_latex):
                visual_id = dic_formula_visual_id[formula_id]
                if formula_id in dic_formula_id_slt:
                    slt = dic_formula_id_slt[formula_id]
                else:
                    slt = ''
                if formula_id in dic_formula_id_opt:
                    opt = dic_formula_id_opt[formula_id]
                else:
                    opt = ''
                csv_writer_latex.writerow(
                    [formula_id, dic_formula_id_info[0], dic_formula_id_info[1], dic_formula_id_info[2], visual_id,
                     latex])

                csv_writer_slt.writerow(
                    [formula_id, dic_formula_id_info[0], dic_formula_id_info[1], dic_formula_id_info[2], visual_id,
                     slt])

                csv_writer_opt.writerow(
                    [formula_id, dic_formula_id_info[0], dic_formula_id_info[1], dic_formula_id_info[2], visual_id,
                     opt])

        result_latex.close()
        result_slt.close()
        result_opt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ldir', type=str, help='latex directory')
    parser.add_argument('-v', type=str, help='visual id file')
    parser.add_argument('-con', type=str, help='directory of intermediate MathML conversion results')
    parser.add_argument('-res', type=str, help='results directory where the results are saved in')
    args = vars(parser.parse_args())

    latex_directory = args['ldir']
    visual_id_file = args['v']
    intermediate_conversion_directory = args['con']
    result_dir = args['res']
    print("reading visual id file")
    dic_formula_visual_id = read_visual_file(visual_id_file)
    print("reading intermediate conversion files")
    dic_formula_id_slt, dic_formula_id_opt = read_intermediate_files(intermediate_conversion_directory)
    print("generating index TSV files")
    read_latex_tsvs(latex_directory, dic_formula_id_slt, dic_formula_id_opt, dic_formula_visual_id, result_dir)


if __name__ == "__main__":
    main()
