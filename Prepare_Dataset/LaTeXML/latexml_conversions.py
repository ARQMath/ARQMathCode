#!/usr/bin/env python
# -*- coding:utf-8 -*-
import html
import os
from copy import copy
from os.path import dirname, join
import sys
import subprocess
from bs4 import BeautifulSoup
from tangentcft.TangentS.math_tan import latex_mml
from tangentcft.TangentS.math_tan.math_extractor import MathExtractor
from lxml import etree
import csv
import time
csv.field_size_limit(sys.maxsize)
import xml.etree.ElementTree as ET


LATEXMLC = [
    'latexmlc',
    '--preload=amsmath',
    '--preload=amsfonts',
    '--preload={}'.format(join(dirname(latex_mml.__file__), "mws.sty.ltxml")),
    '--pmml',
    '--cmml',
    '--whatsin=fragment',
    '--whatsout=fragment',
    '--format=html5',
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
    result = execute(LATEXMLC, latex_input)
    temp = resolve_share_elements(result)
    soup = BeautifulSoup(temp, 'lxml')
    mydivs = soup.find_all("div", {"class": "ltx_para"})
    presentation_result = []
    content_result = []
    for div_tag in mydivs:
        math_tag = div_tag.findAll("math")

        for item in math_tag:
            presentation = MathExtractor.isolate_pmml(str(item))
            presentation = remove_noise(presentation)
            presentation_result.append(presentation)
            content = MathExtractor.isolate_cmml(str(item))
            content = remove_noise(content)
            content_result.append(content)
    return presentation_result, content_result


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


def get_conversion_results(latex_list):
    temp = "\n"
    temp = temp.join(latex_list)
    present_lsit, content_lsit = latexml(temp)
    if len(latex_list) == len(present_lsit) and len(latex_list) == len(content_lsit):
        all_content = {}
        all_presentaion = {}
        for i in range(len(latex_list)):
            all_content[latex_list[i]] = content_lsit[i]
            all_presentaion[latex_list[i]] = present_lsit[i]
        return all_presentaion, all_content
    if len(latex_list) == 1:
        return {}, {}
    latex_rows_head = latex_list[:len(latex_list) // 2]
    latex_rows_tail = latex_list[len(latex_list) // 2:]
    all_presentaion_head, all_content_head = get_conversion_results(latex_rows_head)
    all_presentaion_tail, all_content_tail = get_conversion_results(latex_rows_tail)
    all_presentaion_head.update(all_presentaion_tail)
    all_content_head.update(all_content_tail)
    return all_presentaion_head, all_content_head


def get_latex_list(file_path, formula_id_index, latex_index):
    dic_formulas = {}
    with open(file_path, newline='', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
        next(csv_reader)
        for row in csv_reader:
            formula_id = row[formula_id_index]
            latex_string = row[latex_index]
            if not latex_string.startswith("$"):
                latex_string = "$" + latex_string + "$"
            soup = BeautifulSoup(latex_string, 'html.parser')
            latex_string = html.unescape(str(soup))
            dic_formulas[formula_id] = latex_string
    return dic_formulas


def convert_latex_strings(unique_latex_strings):
    dic_slt = {}
    dic_opt = {}

    list_list_latex = list(chunks(unique_latex_strings, 100))

    for list_latex in list_list_latex:
        present_dic, content_dic = get_conversion_results(list_latex)
        dic_slt.update(present_dic)
        dic_opt.update(content_dic)
    return dic_slt, dic_opt


def extract_slt_opt_from_latex_file(file_path, formula_id_index, formula_latex_index):
    # read formula_id: latex file
    dic_formula_id_formula_latex = get_latex_list(file_path, formula_id_index, formula_latex_index)
    # find all the unique latex strings to pass to LaTeXML
    unique_latex_strings = list(set(dic_formula_id_formula_latex.values()))
    # extract slt and opt
    dic_slt, dic_opt = convert_latex_strings(unique_latex_strings)
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
    return conversion_result_slt, conversion_result_opt, lst_failed


def convert_tsv_latex_write_ouput(latex_file_path, file_id, destination_root):
    formula_id_index = 0
    formula_latex_index = 5
    conversion_result_slt, conversion_result_opt, lst_failed = \
        extract_slt_opt_from_latex_file(latex_file_path+"/"+file_id+".tsv", formula_id_index, formula_latex_index)

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
    return lst_failed


def main():
    # source root were latex tsv files are located
    source_root = sys.argv[1]
    # tsv file id
    file_id = sys.argv[2]
    # destination to save slt/opt/failure files
    destination_root = sys.argv[3]
    lst_failed_ids = convert_tsv_latex_write_ouput(source_root, file_id, destination_root)
    print(len(lst_failed_ids))


if __name__ == '__main__':
    main()