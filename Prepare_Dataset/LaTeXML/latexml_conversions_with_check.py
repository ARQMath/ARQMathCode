#!/usr/bin/env python

# -*- coding:utf-8 -*-
import html
import os
import shutil
from copy import copy
from os.path import dirname, join
import sys

import argparse
conf_path = os.getcwd()
sys.path.append(conf_path)



import subprocess
from bs4 import BeautifulSoup
from tangentcft.TangentS.math_tan import latex_mml
from tangentcft.TangentS.math_tan.math_extractor import MathExtractor
from lxml import etree
import csv
import xml.etree.ElementTree as ET
# from tqdm import tqdm
from Prepare_Dataset.LaTeXML.post_processing_conversion_results import combine_results
from Prepare_Dataset.LaTeXML.latexml_conversions_with_check_secondary import convert_tsv_latex_write_output_secondary
from latex_validation import validating_dic_formulas
from tqdm import tqdm

csv.field_size_limit(sys.maxsize)
destination_root_1 = "./temp_round1_intermediate"
destination_root_2 = "./temp_round2_intermediate"
destination_root_3 = "./temp_round3_intermediate"
combined_1 = "./temp_round1_combined"
combined_2 = "./temp_round12_combined"
combined_3 = "./temp_round123_combined"

LATEXMLC = [
    'latexmlc',
    '--preload=amsmath',
    '--preload=amsfonts',
    '--preload={}'.format(join(dirname(latex_mml.__file__), "mws.sty.ltxml")),
    # '--preload=amssymb',
    '--pmml',
    '--cmml',
    '--profile=fragment',
  # '--whatsin=fragment',
  # '--whatsout=fragment',
  # '--format=html5',
    '-',
]
XML_NAMESPACES = {
    'xhtml': 'http://www.w3.org/1999/xhtml',
    'mathml': 'http://www.w3.org/1998/Math/MathML',
    'ntcir-math': 'http://ntcir-math.nii.ac.jp/',
}

ETREE_TOSTRING_PARAMETERS = {
    'xml_declaration': True,
    'encoding': 'UTF-8',
    'with_tail': False,
}
SUBPROCESS_TIMEOUT = 3600


def unicode_to_tree(text):
    xml_parser = etree.XMLParser(huge_tree=True)
    return etree.XML(text.encode(ETREE_TOSTRING_PARAMETERS['encoding']), xml_parser)


def tree_to_unicode(tree):
    return etree.tostring(tree, **ETREE_TOSTRING_PARAMETERS).decode(ETREE_TOSTRING_PARAMETERS['encoding'])


def remove_noise(xx):
    tree = etree.XML(str(xx))
    for el in tree.xpath("//*"):
        for attr in el.attrib:
            if attr.startswith("id") or attr.startswith("xref"):
                el.attrib.pop(attr)
    return ET.tostring(tree, encoding='unicode', method='xml')


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def latexml(latex_input):
    xml_input = execute(LATEXMLC, latex_input)
    xml_output = resolve_share_elements(xml_input)
    return xml_output


def resolve_share_elements(xml_tokens):
    xml_document = BeautifulSoup(xml_tokens, 'lxml')
    for math_element in xml_document.find_all('math'):
        for share_element in math_element.find_all('share'):
            if 'href' not in share_element:
                share_element.decompose()
                continue
            assert share_element['href'].startswith('#')
            shared_element = math_element.find(id=share_element['href'][1:])
            if shared_element:
                share_element.replace_with(copy(shared_element))
            else:
                share_element.decompose()
    return str(xml_document)


def execute(command, unicode_input):
    str_input = unicode_input.encode('utf-8')
    process = subprocess.Popen(
        command,
        shell=False,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    try:
        str_output = process.communicate(
            str_input,
            timeout=SUBPROCESS_TIMEOUT,
        )[0]
    except subprocess.TimeoutExpired as e:
        process.kill()
        raise e
    unicode_output = str_output.decode('utf-8')
    return unicode_output


def read_failed_formulas(failed_file):
    lst_formula_id = []
    file = open(failed_file, "r", encoding="utf-8")
    line = file.readline()
    while line:
        line = line.strip()
        lst_formula_id.append(line)
        line = file.readline()
    return lst_formula_id


def _get_conversion_results_worker(latex_list):
    latex_paragraphs = '\n\n'.join(
        'Formula #{}:\n\\[{}\\]'.format(formula_number, latex)
        for formula_number, latex
        in enumerate(latex_list)
    )
    cmml_list = []
    pmml_list = []
    try:
        xml_output = latexml(latex_paragraphs)
        try:
            xml_document = unicode_to_tree(xml_output)
            for formula_number, _ in enumerate(latex_list):
                math_elements = xml_document.xpath(
                    '//xhtml:div[@class = "ltx_para" and xhtml:p[@class = "ltx_p" and normalize-space(text()) = "Formula #{}:"]]//mathml:math'.format(formula_number),
                    namespaces=XML_NAMESPACES
                )
                if len(math_elements) >= 1:
                    math_element = math_elements[0]
                    math_tokens = tree_to_unicode(math_element)
                    try:
                        cmml_math_tokens = MathExtractor.isolate_cmml(math_tokens)
                        cmml_math_tokens = remove_noise(cmml_math_tokens)
                        cmml_math_element = unicode_to_tree(cmml_math_tokens)
                        pmml_math_tokens = MathExtractor.isolate_pmml(math_tokens)
                        pmml_math_tokens = remove_noise(pmml_math_tokens)
                        pmml_math_element = unicode_to_tree(pmml_math_tokens)

                        # if cmml_math_element.xpath('//mathml:cerror', namespaces=XML_NAMESPACES):
                        #     cmml_math_tokens = ''
                        #     cmml_failure = ValueError('LaTeXML output contains <cerror> elements')
                        # else:
                        #     etree.strip_tags(cmml_math_element, '{{{}}}semantics'.format(XML_NAMESPACES['mathml']))
                        #     cmml_math_tokens = tree_to_unicode(cmml_math_element)
                        #     cmml_failure = None
                        # if pmml_math_element.xpath('//mathml:cerror', namespaces=XML_NAMESPACES):
                        #     pmml_math_tokens = ''
                        #     pmml_failure = ValueError('LaTeXML output contains <cerror> elements')
                        # else:
                        #     pmml_math_tokens = tree_to_unicode(pmml_math_element)
                        #     pmml_failure = None

                        etree.strip_tags(cmml_math_element, '{{{}}}semantics'.format(XML_NAMESPACES['mathml']))
                        cmml_math_tokens = tree_to_unicode(cmml_math_element)
                        cmml_failure = None
                        pmml_math_tokens = tree_to_unicode(pmml_math_element)
                        pmml_failure = None

                    except Exception as e:
                        cmml_math_tokens = ''
                        pmml_math_tokens = ''
                        cmml_failure = e
                        pmml_failure = e
                else:
                    cmml_math_tokens = ''
                    pmml_math_tokens = ''
                    cmml_failure = ValueError('Formula not found in LaTeXML output')
                    pmml_failure = ValueError('Formula not found in LaTeXML output')
                cmml_list.append((cmml_failure, cmml_math_tokens))
                pmml_list.append((pmml_failure, pmml_math_tokens))
        except etree.Error as e:  # LaTeXML conversion failed, try halving latex_rows
            assert len(latex_list) > 0
            if len(latex_list) > 1:
                latex_list_head = latex_list[:len(latex_list) // 2]
                latex_list_tail = latex_list[len(latex_list) // 2:]
                cmml_list_head, pmml_list_head = _get_conversion_results_worker(latex_list_head)
                cmml_list_tail, pmml_list_tail = _get_conversion_results_worker(latex_list_tail)
                cmml_list.extend(cmml_list_head + cmml_list_tail)
                pmml_list.extend(pmml_list_head + pmml_list_tail)
            else:
                cmml_math_tokens = ''
                pmml_math_tokens = ''
                cmml_failure = ValueError(e.msg)
                pmml_failure = ValueError(e.msg)
                cmml_list.append((cmml_failure, cmml_math_tokens))
                pmml_list.append((pmml_failure, pmml_math_tokens))
    except subprocess.SubprocessError as e:
        cmml_math_tokens = ''
        pmml_math_tokens = ''
        cmml_failure = e
        pmml_failure = e
        for _ in latex_list:
            cmml_list.append((cmml_failure, cmml_math_tokens))
            pmml_list.append((pmml_failure, pmml_math_tokens))
    return (cmml_list, pmml_list)


def get_conversion_results(latex_list):
    cmml_dict, pmml_dict = dict(), dict()
    cmml_list, pmml_list = _get_conversion_results_worker(latex_list)
    assert len(cmml_list) == len(latex_list)
    assert len(pmml_list) == len(latex_list)
    for latex, (cmml_failure, cmml), (pmml_failure, pmml) in zip(latex_list, cmml_list, pmml_list):
        if cmml_failure is not None or pmml_failure is not None:
            continue
        cmml_dict[latex] = cmml
        pmml_dict[latex] = pmml
    return pmml_dict, cmml_dict


def get_latex_list(file_path, formula_id_index, latex_index, lst_formula_id=None):
    dic_formulas = {}
    with open(file_path, newline='', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
        next(csv_reader)
        for row in csv_reader:
            formula_id = row[formula_id_index]
            if lst_formula_id is not None and formula_id in lst_formula_id:
                continue
            latex_string = row[latex_index]
            # if not latex_string.startswith("$"):
            #     latex_string = "$" + latex_string + "$"
            soup = BeautifulSoup(latex_string, 'html.parser')
            latex_string = html.unescape(str(soup))
            dic_formulas[formula_id] = latex_string
    return dic_formulas


def convert_latex_strings(unique_latex_strings, FORMULA_BATCH_SIZE):
    dic_slt = {}
    dic_opt = {}

    list_list_latex = list(chunks(unique_latex_strings, FORMULA_BATCH_SIZE))

    for list_latex in tqdm(list_list_latex):
        present_dic, content_dic = get_conversion_results(list_latex)
        dic_slt.update(present_dic)
        dic_opt.update(content_dic)

    return dic_slt, dic_opt


def extract_slt_opt_from_latex_file(file_path, formula_id_index, formula_latex_index, FORMULA_BATCH_SIZE):
    # read formula_id: latex file
    dic_formula_id_formula_latex = get_latex_list(file_path, formula_id_index, formula_latex_index)
    # check the validity of latex strings with lacheck tool
    # list_formula_not_passed = la_check_verification(dic_formula_id_formula_latex)
    dic_formula_id_with_issues, lst_delete = validating_dic_formulas(dic_formula_id_formula_latex)

    for formula_id in lst_delete:
        del dic_formula_id_formula_latex[formula_id]
    for formula_id in dic_formula_id_with_issues:
        dic_formula_id_formula_latex[formula_id] = dic_formula_id_with_issues[formula_id][1]

    for formula_id in dic_formula_id_formula_latex:
        latex_string = dic_formula_id_formula_latex[formula_id]
        if not latex_string.startswith("$"):
            latex_string = "$" + latex_string + "$"
        dic_formula_id_formula_latex[formula_id] = latex_string

    # find all the unique latex strings to pass to LaTeXML
    unique_latex_strings = list(set(dic_formula_id_formula_latex.values()))
    # sort by alphabet and then length
    unique_latex_strings.sort()
    unique_latex_strings.sort(key=len)
    # extract slt and opt
    dic_slt, dic_opt = convert_latex_strings(unique_latex_strings, FORMULA_BATCH_SIZE)
    lst_failed = []
    conversion_result_slt = {}
    conversion_result_opt = {}
    for formula_id in dic_formula_id_formula_latex:
        latex = dic_formula_id_formula_latex[formula_id]
        if latex in dic_slt:
            slt = dic_slt[latex]
            opt = dic_opt[latex]
        else:
            slt = ''
            opt = ''
            lst_failed.append(formula_id)
        conversion_result_slt[formula_id] = slt
        conversion_result_opt[formula_id] = opt

    for formula_id in lst_delete:
        conversion_result_slt[formula_id] = ''
        conversion_result_opt[formula_id] = ''
    return dic_formula_id_formula_latex, conversion_result_slt, conversion_result_opt, lst_failed, lst_delete, dic_formula_id_with_issues


def convert_tsv_latex_write_output(latex_file_path, file_id, destination_root, FORMULA_BATCH_SIZE):
    formula_id_index = 0
    formula_latex_index = 5
    dic_formula_id_formula_latex, conversion_result_slt, conversion_result_opt, lst_failed, lst_delete, dic_formula_id_with_issues = \
        extract_slt_opt_from_latex_file(latex_file_path + "/" + file_id + ".tsv", formula_id_index, formula_latex_index, FORMULA_BATCH_SIZE)

    with open(destination_root+"/slt_"+file_id+".tsv", "w", newline='', encoding="utf-8") as result_file:
        csv_writer = csv.writer(result_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for formula_id in conversion_result_slt:
            slt = conversion_result_slt[formula_id]
            slt = slt.replace("\n", " ", slt.count("\n"))
            soup = BeautifulSoup(slt, 'html.parser')
            slt = html.unescape(str(soup))
            csv_writer.writerow([str(formula_id), slt])
    with open(destination_root+"/opt_"+file_id+".tsv", "w", newline='', encoding="utf-8") as result_file:
        csv_writer = csv.writer(result_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for formula_id in conversion_result_opt:
            opt = conversion_result_opt[formula_id]
            opt = opt.replace("\n", " ", opt.count("\n"))
            soup = BeautifulSoup(opt, 'html.parser')
            opt = html.unescape(str(soup))
            csv_writer.writerow([str(formula_id), opt])
    with open(destination_root+"/failed_"+file_id+".tsv", "w", newline='', encoding="utf-8") as result_file:
        csv_writer = csv.writer(result_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for formula_id in lst_failed:
            csv_writer.writerow([str(formula_id)])
    with open(destination_root+"/not_passed_"+file_id+".tsv", "w", newline='', encoding="utf-8") as result_file:
        csv_writer = csv.writer(result_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for formula_id in lst_delete:
            csv_writer.writerow([str(formula_id)])
    with open(destination_root+"/modified_"+file_id+".tsv", "w", newline='', encoding="utf-8") as result_file:
        csv_writer = csv.writer(result_file, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        for formula_id in dic_formula_id_with_issues:
            csv_writer.writerow([str(formula_id), str(dic_formula_id_with_issues[formula_id][0]),
                                 str(dic_formula_id_with_issues[formula_id][1])])
    return lst_failed


def round_1(source_root, file_id):
    if not os.path.exists(destination_root_1):
        os.makedirs(destination_root_1)

    FORMULA_BATCH_SIZE = 100
    lst_failed_ids = convert_tsv_latex_write_output(source_root, file_id, destination_root_1, FORMULA_BATCH_SIZE)
    print('{} formulae failed to convert'.format(len(lst_failed_ids)))


def secondary(source_root, file_id, destination_root, FORMULA_BATCH_SIZE, previous_round):
    if not os.path.exists(destination_root):
        os.makedirs(destination_root)
    lst_failed_ids = convert_tsv_latex_write_output_secondary(source_root, file_id, destination_root, previous_round, FORMULA_BATCH_SIZE)
    print('{} formulae failed to convert'.format(len(lst_failed_ids)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-com', type=str, help='command to do')
    parser.add_argument('-ldir', type=str, help='latex directory')
    parser.add_argument('-fid', type=str, help='latex_file_id')

    args = vars(parser.parse_args())

    command = args['com']

    if command == "r1":
        latex_directory = args['ldir']
        file_id = args['fid']
        round_1(latex_directory, file_id)
    elif command == "p1":
        latex_directory = args['ldir']
        combine_results(destination_root_1, destination_root_1, combined_1, latex_directory)
    elif command == "r2":
        latex_directory = args['ldir']
        file_id = args['fid']
        secondary(latex_directory, file_id, destination_root_2, 10, combined_1)
    elif command == "p2":
        latex_directory = args['ldir']
        combine_results(combined_1, destination_root_2, combined_2, latex_directory)
    elif command == "r3":
        latex_directory = args['ldir']
        file_id = args['fid']
        secondary(latex_directory, file_id, destination_root_3, 1, combined_2)
    elif command == "p3":
        latex_directory = args['ldir']
        combine_results(combined_2, destination_root_3, combined_3, latex_directory)
    elif command == "c":
        if os.path.exists(destination_root_2):
            shutil.rmtree(destination_root_2)
        if os.path.exists(destination_root_3):
            shutil.rmtree(destination_root_3)
        if os.path.exists(combined_1):
            shutil.rmtree(combined_1)
        if os.path.exists(combined_2):
            shutil.rmtree(combined_2)


if __name__ == "__main__":
    main()
