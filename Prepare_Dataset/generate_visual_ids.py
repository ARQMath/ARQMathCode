import operator
import sys
import os
import csv
import argparse
conf_path = os.getcwd()
sys.path.append(conf_path)
from tangentcft.TangentS.math_tan.math_extractor import MathExtractor
csv.field_size_limit(sys.maxsize)


def read_all_formulas(formula_tsv_dir):
    """
    Reading all TSV files located in
    @param formula_tsv_dir: the directory in which the latex/slt representations provided by the organizers are located
    @return: dictionary (formula id, math representation)
    """
    dic_formula_id_representation = {}
    for filename in os.listdir(formula_tsv_dir):
        with open(formula_tsv_dir + filename, mode='r', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            next(csv_reader)
            for row in csv_reader:
                formula_id = row[0]
                latex = row[4]
                latex = "".join(latex.split())
                dic_formula_id_representation[formula_id] = latex
    return dic_formula_id_representation


def read_slt_file(directory_conversions):
    result_dictionary = {}
    for filename in os.listdir(directory_conversions):
        if not filename.startswith("slt"):
            continue
            with open(directory_conversions+"/"+filename, mode='r', encoding="utf-8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter='\t')
                for row in csv_reader:
                    try:
                        formula_id = row[0]
                        math_ml = row[1]
                        slt_string = MathExtractor.convert_mathml_slt_string(math_ml)
                        result_dictionary[formula_id] = slt_string
                    except:
                        continue
    return result_dictionary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ldir', type=str, help='latex directory')
    parser.add_argument('-con', type=str, help='directory having MathML representations from conversions with LaTeXML')
    parser.add_argument('-res', type=str, help='result file having (formula id, visual id)')
    args = vars(parser.parse_args())

    latex_file_path = args['ldir']
    slt_file_path = args['con']
    dic_formula_id_latex = read_all_formulas(latex_file_path)
    dic_formula_id_slt = read_slt_file(slt_file_path)

    visual_id = 1
    dic_slt_string_visual_id = {}
    dic_latex_string_visual_id = {}
    final_result = {}

    for formula_id in dic_formula_id_latex:
        if formula_id in dic_formula_id_slt:
            slt_string = dic_formula_id_slt[formula_id]
            if slt_string in dic_slt_string_visual_id:
                current_visual_id = dic_slt_string_visual_id[slt_string]
            else:
                dic_slt_string_visual_id[slt_string] = visual_id
                current_visual_id = visual_id
                latex_string = dic_formula_id_latex[formula_id]
                dic_latex_string_visual_id[latex_string] = visual_id
                visual_id += 1
        else:
            latex_string = dic_formula_id_latex[formula_id]
            if latex_string in dic_latex_string_visual_id:
                current_visual_id = dic_latex_string_visual_id[latex_string]
            else:
                dic_latex_string_visual_id[latex_string] = visual_id
                current_visual_id = visual_id
                visual_id += 1
        final_result[formula_id] = current_visual_id

    print("----------------------------------")
    print(len(dic_slt_string_visual_id.keys()))
    print(len(dic_latex_string_visual_id.keys()))
    result_file = open(args['res'], "w",
                       newline='',
                       encoding="utf-8")
    csv_writer = csv.writer(result_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)

    for formula_id in final_result:
        csv_writer.writerow([formula_id, final_result[formula_id]])
    result_file.close()


if __name__ == "__main__":
    main()
