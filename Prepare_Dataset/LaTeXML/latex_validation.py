import csv
import re
import os
import subprocess
import sys
import lxml.html
from bs4 import BeautifulSoup

html_tags = ['<html>', '<base>', '<head>', '<link>', '<meta>', '<style>', '<title>', '<body>', '<address>', '<article>', '<aside>', '<footer>', '<header>', '<h1>', '<h2>', '<h3>', '<h4>', '<h5>', '<h6>', '<main>', '<nav>', '<section>', '<dd>', '<div>', '<dl>', '<dt>', '<figcaption>', '<figure>', '<hr>', '<li>', '<ol>', '<p>', '<pre>', '<ul>', '<a>', '<abbr>', '<b>', '<bdi>', '<bdo>', '<br>', '<cite>', '<code>', '<data>', '<dfn>', '<em>', '<i>', '<kbd>', '<mark>', '<q>', '<rp>', '<rt>', '<ruby>', '<s>', '<samp>', '<small>', '<span>', '<strong>', '<sub>', '<sup>', '<time>', '<u>', '<var>', '<wbr>', '<area>', '<audio>', '<img>', '<map>', '<track>', '<video>', '<embed>', '<iframe>', '<object>', '<param>', '<picture>', '<portal>', '<source>', '<svg>', '<math>', '<canvas>', '<noscript>', '<script>', '<del>', '<ins>', '<caption>', '<col>', '<colgroup>', '<table>', '<tbody>', '<td>', '<tfoot>', '<th>', '<thead>', '<tr>', '<button>', '<datalist>', '<fieldset>', '<form>', '<input>', '<label>', '<legend>', '<meter>', '<optgroup>', '<option>', '<output>', '<progress>', '<select>', '<details>', '<dialog>', '<menu>', '<summary>', '<slot>', '<template>']
temp = []
for i in range(len(html_tags)):
    temp.append("</"+html_tags[i][1:])
html_tags.extend(temp)


def read_tsv_latex_file(file_path):
    # read the given tsv file and returns dic of formula id and latex representation
    dic_formula_id_latex_str = {}
    with open(file_path, newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
        next(csv_reader)
        for row in csv_reader:
            formula_id = int(row[0])
            latex = row[5]
            dic_formula_id_latex_str[formula_id] = latex
    return dic_formula_id_latex_str


def handle_curly_bracket(latex_str):
    # handles the curly brackets unmatched
    stack = []
    i = 0
    while i < len(latex_str):
        char = latex_str[i]
        if char == '}':
            # Check if \} then pass
            if i-1 >= 0 and latex_str[i-1] == "\\":
                i += 1
                continue
            # Check if { is in stack then pop it
            if len(stack) > 0:
                stack.pop()
            else:
                # if there is mismatch, insert {. But where?
                # it goes back till it finds } and insert { right after than
                # if not found it will in beginning of the latex
                # e.g {a+b} c/d} ==> {a+b} {c/d}
                j = i - 1
                while j > 0 and latex_str[j] != '}':
                    j -= 1
                if latex_str[j] == '}':
                    j += 1
                    latex_str = latex_str[:j] + '{' + latex_str[j:]
                else:
                    latex_str = "{" + latex_str
                i += 1
        elif char == '{':
            if i - 1 < 0 or latex_str[i - 1] != "\\":
                stack.append(char)
        i += 1
    while len(stack) > 0:
        latex_str += '}'
        stack.pop()
    return latex_str


def handle_begin_end_brackets(latex_str):
    # takes in the latex string and check the \begin{env} ... \end{env} delimiters
    if "\\begin" not in latex_str and "\\end" not in latex_str:
        return latex_str

    latex_str = latex_str.replace("\\begin {", "\\begin{")
    latex_str = latex_str.replace("\\end {", "\\end{")

    # find all begin
    begin_items = re.findall(r'\\begin{(.+?)}', latex_str)
    # find all end
    end_items = re.findall(r'\\end{(.+?)}', latex_str)
    # sort by their index in latex string
    dic_index_begin_item = {}
    for item in begin_items:
        index = latex_str.find("\\begin{"+item+"}")
        dic_index_begin_item[index] = "\\begin{"+item+"}"
    for item in end_items:
        index = latex_str.find("\\end{"+item+"}")
        dic_index_begin_item[index] = "\\end{"+item+"}"

    stack = []

    for index in sorted(dic_index_begin_item):
        item = dic_index_begin_item[index]
        begin_item = re.findall(r'\\begin{(.+?)}', item)
        # if appeared item is 'begin' then push it to stack
        if len(begin_item) > 0:
            stack.append(begin_item[0])
        else:
            end = re.findall(r'\\end{(.+?)}', item)[0]
            # if the end has no begin, include begin at first
            if len(stack) == 0 or stack[-1] != end:
                latex_str = "\\begin{" + end + "}" + latex_str
            else:
                stack.pop()
    # handling those begin with no end
    while len(stack) > 0:
        latex_str += "\\end{" + stack.pop() + "}"
    return latex_str


def handle_dollar_issue(latex_str):
    if "$" not in latex_str:
        return latex_str
    stack = []
    result = ""
    # if set true, $ or $$ is seen and will start saving item between them
    save_chars = False
    i = 0
    while i < len(latex_str):
        if latex_str[i] == '$':
            # Check if there are $$
            if i+1 < len(latex_str) and latex_str[i+1] == '$':
                if len(stack) > 0 and stack[-1] == "$$":
                    return "$$"+result+"$$"
                    # stack.pop()
                else:
                    stack.append("$$")
                    save_chars = True
                i += 1
            else:
                if len(stack) > 0 and stack[-1] == "$":
                    return "$"+result+"$"
                else:
                    stack.append("$")
                    save_chars = True
        elif save_chars:
            result += latex_str[i]
        i += 1
    sign = stack.pop()
    if result == '':
        return ''
    return sign + result + sign


def handle_percentage(latex_str):
    # % sign is interpreted as ignore characters till \n is met
    if '%' not in latex_str:
        return latex_str
    stack = []
    result = ""

    ignore = False
    i = 0
    while i < len(latex_str):
        char = latex_str[i]
        if not ignore and char != '%':
            result += char
        elif ignore and char == '\n':
            ignore = False
            stack.pop()
        elif char == '%' and not ignore:
            if i-1 < 0 or latex_str[i-1] != '\\':
                ignore = True
                stack.append(char)
            else:
                result += char
        i += 1
    return result


def handle_text_string(latex_str):
    compiler = re.compile(r"\\text.*?{(.+?)}")
    lst_items = []
    for item in compiler.finditer(latex_str):
        tuple_span = item.span()
        lst_items.append(latex_str[tuple_span[0]:tuple_span[1]])
    temp_string = "".join(lst_items)
    # This shows there is additional items with text tag which makes is LaTeXML able to parse it
    if temp_string != latex_str:
        return latex_str
    if latex_str == '':
        return latex_str
    return "~"+latex_str


def handle_html_tag(latex_str):
    for html_tag in html_tags:
        if html_tag in latex_str:
            return ''
    return latex_str


def validate_latex(latex_str):
    if "\\newcommand" in latex_str or "\\def" in latex_str:
        return ''

    latex_str = handle_percentage(latex_str)
    latex_str = handle_dollar_issue(latex_str)
    latex_str = handle_curly_bracket(latex_str)
    latex_str = handle_begin_end_brackets(latex_str)
    latex_str = handle_text_string(latex_str)
    latex_str = handle_html_tag(latex_str)

    return latex_str


def validating_dic_formulas(dic_formulas):
    dic_formula_id_with_issues = {}
    lst_delete = []
    for formula_id in dic_formulas:
        latex = dic_formulas[formula_id]
        validated_str = validate_latex(latex)
        if validated_str != latex:
            if validated_str == '':
                lst_delete.append(formula_id)
            else:
                dic_formula_id_with_issues[formula_id] = (latex, validated_str)
    return dic_formula_id_with_issues, lst_delete


def la_check_testing(dic_formulas):
    # print(dic_issues)
    line = 1
    temp_dic = {}
    file = open("temp_la_check", "w", encoding="utf-8")
    for formula_id in dic_formulas:
        latex = dic_formulas[formula_id]
        latex = latex.replace("\n", " ")
        temp_dic[line] = formula_id
        file.write(latex+"\n")
        line += 1
    file.close()
    result = subprocess.run(['lacheck', 'temp_la_check'], stdout=subprocess.PIPE)
    results = result.stdout.decode('ISO-8859-1').split("\n")
    lst_issued = []
    for res in results:
        if "unmatched" in res:
            if "math begin" in res or "math end" in res:
                continue
            issued = res.split(":")[0].split("line")[1]
            line_num = int(issued.strip())
            if line_num in temp_dic:
                formula_id = temp_dic[line_num]
                latex = dic_formulas[formula_id]
                lst_issued.append((formula_id, latex, res))
    os.remove("temp_la_check")
    return set(lst_issued)


def la_check_testing_1(dic_formulas):
    # print(dic_issues)
    lst_issued = []
    for formula_id in dic_formulas:
        line = 1
        temp_dic = {}
        file = open("temp_la_check", "w", encoding="utf-8")
        latex = dic_formulas[formula_id]
        latex = latex.replace("\n", " ")
        temp_dic[line] = formula_id
        file.write(latex+"\n")
        line += 1
        file.close()
        result = subprocess.run(['lacheck', 'temp_la_check'], stdout=subprocess.PIPE)
        results = result.stdout.decode('ISO-8859-1').split("\n")

        for res in results:
            if "unmatched" in res:
                if "math begin" in res or "math end" in res:
                    continue
                issued = res.split(":")[0].split("line")[1]
                line_num = int(issued.strip())
                if line_num in temp_dic:
                    formula_id = temp_dic[line_num]
                    latex = dic_formulas[formula_id]
                    lst_issued.append((formula_id, latex, res))
        os.remove("temp_la_check")
    return set(lst_issued)


def la_check_verification(dic_formulas):
    temp_dic = generate_la_check_input(dic_formulas)
    result = subprocess.run(['lacheck', 'temp_la_check'], stdout=subprocess.PIPE)
    results = result.stdout.decode('ISO-8859-1').split("\n")
    lst_issued = []
    for res in results:
        if "unmatched" in res:
            issued = res.split(":")[0].split("line")[1]
            line_num = int(issued.strip())
            if line_num in temp_dic:
                formula_id = temp_dic[line_num]
                if formula_id not in lst_issued:
                    lst_issued.append(formula_id)
    os.remove("temp_la_check")
    return lst_issued


def generate_la_check_input(dic_formulas):
    line = 1
    temp_dic = {}
    file = open("temp_la_check", "w", encoding="utf-8")
    for formula_id in dic_formulas:
        latex = dic_formulas[formula_id]
        latex = latex.replace("\n", " ")
        temp_dic[line] = formula_id
        file.write(latex + "\n")
        line += 1
    file.close()
    return temp_dic


def apply_changes(dic_formula_id_latex, dic_formula_id_with_issues, lst_delete):
    pass_to_latex = {}
    for formula_id in dic_formula_id_latex:
        if formula_id in dic_formula_id_with_issues:
            corrected = dic_formula_id_with_issues[formula_id][1]
            corrected = corrected.strip()
            if corrected != '':
                pass_to_latex[formula_id] = corrected
        elif formula_id not in lst_delete:
            pass_to_latex[formula_id] = dic_formula_id_latex[formula_id]
    return pass_to_latex
