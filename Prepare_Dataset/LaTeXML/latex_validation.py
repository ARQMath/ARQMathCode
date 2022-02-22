import csv
import re
import subprocess


def read_tsv_latex_file(file_path):
    # read the given tsv file and returns dic of formula id and latex representation
    dic_formula_id_latex = {}
    with open(file_path, newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
        for row in csv_reader:
            formula_id = int(row[0])
            latex = row[5]
            dic_formula_id_latex[formula_id] = latex
    return dic_formula_id_latex


def check_curly_bracket(latex_str):
    # handles the curly brackets unmatched
    stack = []
    i = 0
    while i < len(latex_str):
        char = latex_str[i]
        if char == '}':
            if len(stack) > 0:
                stack.pop()
            else:
                # if there is mismatch insert {
                # this code decides where to insert { -- it goes back till it finds } or beginning of the latex
                # if } is found the { is inserted after }
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
            stack.append(char)
        i += 1
    while len(stack) > 0:
        latex_str += '}'
        stack.pop()
    return latex_str


def check_begin_end_brackets(latex_str):
    # takes in the latex string and check the \begin{env} ... \end{env} delimiters
    if "\\begin" not in latex_str and "end" not in latex_str:
        return latex_str

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
        begin_item = re.findall(r'\\begin{(.+?)}', item)[0]
        # if appeared item is 'begin' then push it to stack
        if len(begin_item) > 0:
            stack.append(begin_item)
        else:
            end = re.findall(r'\\end{(.+?)}', latex_str)[0]
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
    for i in range(len(latex_str)):
        if latex_str[i] == '$':
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
                    # stack.pop()
                else:
                    stack.append("$")
                    save_chars = True
        elif save_chars:
            result += latex_str[i]
    sign = stack.pop()
    return sign + result + sign


def handle_percentage(latex_str):
    # handling the formula having % in them
    # Replacing it with empty
    return latex_str.replace("%", "")

    # stack = []
    # result = ""
    # if '%' not in latex_str:
    #     return latex_str
    # ignore = False
    # for char in latex_str:
    #     if char != '%' and not ignore:
    #         result += char
    #     else:
    #         if stack[-1] == char:
    #             ignore = False
    #             stack.pop()
    #         else:
    #             ignore = True
    #             stack.append(char)
    # return char


def validate_latex(latex_str):
    if "\\newcommand" in latex_str: #"\\text" in latex_str or
        return None
    latex_str = latex_str.replace("<p>", " ")
    latex_str = latex_str.replace("</p>", " ")

    latex_str = handle_percentage(latex_str)
    latex_str = check_begin_end_brackets(latex_str)
    latex_str = check_curly_bracket(latex_str)
    latex_str = handle_dollar_issue(latex_str)

    return latex_str


def validating_dic_formulas(dic_formulas):
    dic_formula_id_with_issues = {}
    for formula_id in dic_formulas:
        latex = dic_formulas[formula_id]
        validate = validate_latex(latex)
        if validate != latex:
            dic_formula_id_with_issues[formula_id] = (latex, validate)
    return dic_formula_id_with_issues


def la_check(dic_formulas):
    print(dic_issues)
    line = 1
    temp_dic = {}
    file = open("temp_la_check", "w", encoding="utf-8")
    for formula_id in dic_issues:
        latex = dic_issues[formula_id][1]
        latex = latex.replace("\n", " ")
        temp_dic[line] = formula_id
        file.write(latex+"\n")
        line += 1
    file.close()
    result = subprocess.run(['lacheck', 'temp_la_check'], stdout=subprocess.PIPE)
    results = result.stdout.decode('utf-8').split("\n")
    lst_issued = []
    for res in results:
        if "unmatched" in res:
            issued = res.split(":")[0].split("line")[1]
            if int(issued.strip()) in dic_formulas:
                lst_issued.append(formula_id)
    return lst_issued


dic_temp = {1: "$a+v{", 2: "\\begin{cases}a+v}", 3: "{a+b} c/d}"}
dic_issues = validating_dic_formulas(dic_temp)
print(la_check(dic_issues))
