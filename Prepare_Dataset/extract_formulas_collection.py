import csv
import re

from post_reader_record import DataReaderRecord


def find_patterns_in_text(formula_double_dollar, input_text, formula_counter, formula_index_map):
    for string in formula_double_dollar:
        if "FXXF_" in string:
            continue

        original_formula = "<span class=\"math-container\">$$" + string + "$$</span>"
        fake_text = "FXXF_" + str(formula_counter)
        formula_index_map[fake_text] = original_formula
        input_text = input_text.replace(original_formula, " " + fake_text + " ", 1)
        formula_counter += 1
    return input_text, formula_counter, formula_index_map


def get_list_of_formulas(input_text):
    """
    This method takes in a text and extract all the formulas inside it in a list of file.
    """

    "first removes the new lines all tne \n in the text"
    input_text = input_text.replace("\n", " ", input_text.count("\n"))
    latex_formulas = []

    "Formulas are located between 2 dollar signs in latex, so if there no or only one we have no formula in the text"
    if input_text.count("$") == 0 or input_text.count("$") == 1:
        return latex_formulas

    """
    There are 5 patterns in MSE dataset for latex formula; considering a+b we can have one of these:
    '<span class="math-container">$$a+b$$</span>'
    '<span class="math-container">$a+b$</span>'
    '<span class="math-container">a+b</span>'
    $$a+b$$
    $a+b$
    We start from the top to the bottom of these 5 types and use 're' library to find the patterns. As you can 
    see the patterns in bottom, are inside patterns in top, therefore after extracting each formula, we
    replace them with 'FXXF_formula id' to avoid double extraction. 
    The way we did the pattern matching was from top to bottom patterns and we find all of them (all of the formulas 
    with pattern 1 (<span class="math-container">$$a+b$$</span>) then all of pattern 2 and so on). 
    We assign to each formula an unique id.
    """

    "Formula ids"
    counter = 1

    """
    As we use fake text of 'FXXF_formula_id' to avoid mismatching, we have a map of original text and fake one as;
    FXXF_1 : $a+b$ named formula_index_map. 
    """
    formula_index_map = {}
    """
    Here we check the 5 patterns
    """
    formula_double_dollar = re.findall('<span class="math-container">\$\$(.+?)\$\$</span>', input_text)
    input_text, counter, formula_index_map = find_patterns_in_text(formula_double_dollar,
                                                                   input_text, counter, formula_index_map)
    formula_double_dollar = re.findall('<span class="math-container">\$(.+?)\$</span>', input_text)
    input_text, counter, formula_index_map = find_patterns_in_text(formula_double_dollar,
                                                                   input_text, counter, formula_index_map)
    formula_double_dollar = re.findall('<span class="math-container">(.+?)</span>', input_text)
    input_text, counter, formula_index_map = find_patterns_in_text(formula_double_dollar,
                                                                   input_text, counter, formula_index_map)
    formula_double_dollar = re.findall('\$\$(.+?)\$\$', input_text)
    input_text, counter, formula_index_map = find_patterns_in_text(formula_double_dollar,
                                                                   input_text, counter, formula_index_map)
    formula_double_dollar = re.findall('\$(.+?)\$', input_text)
    input_text, counter, formula_index_map = find_patterns_in_text(formula_double_dollar,
                                                                   input_text, counter, formula_index_map)
    """
    formula_index_map now contains all the formula, we should sort them based on their order appearance in the text; 
    e.g.: 
        original text: $a+b$ is similar to $$a+b$$
        converted text: FXXF_2 is similar to FXXF_1
    we want to know $a+b$ has appeared first, because when we want to convert the original stack exchange to arqmath
    one [where all the formulas are in math-container and has id], we need to put all the formulas in math-container 
    tags, and for that we begin from top to end and sort the formulas based on their relative position to the beginning
    of the text and replace the formula (from MSE) with formula with math-container.
    """
    sorted_by_index = {}
    for formula in formula_index_map:
        sorted_by_index[formula] = re.search(r' (' + formula + ') ', input_text).start()
    sorted_by_index = sorted(sorted_by_index.items(), key=lambda kv: kv[1])

    for formula in sorted_by_index:
        latex_formulas.append(formula_index_map[formula[0]])
    """What is returned here is a list of formulas recognized in the text in the format they are in MSE which can
    be one of the five above."""
    return latex_formulas


def extract_formulas_from_MSE_dataset(clef_home_directory_file_path):
    "data reader to read the posts"
    dr = DataReaderRecord(clef_home_directory_file_path)

    "Formula ids"
    formula_id = 1

    "where we save the formulas"
    result_file = open("Formula_topics_latex.tsv", "w", encoding="utf-8", newline='')
    csv_writer = csv.writer(result_file, delimiter='\t')
    csv_writer.writerow(["id", "post_id", "thread_id", "type", "formula"])

    "iterating through each of the files"
    for question_id in dr.post_parser.map_questions:
        question = dr.post_parser.map_questions[question_id]

        "we decided to leave the 2019 corpus out"
        if question.creation_date.split("T")[0].split("-")[0] == "2019":
            continue

        "formulas can be both in title and body so we check both of them"
        title = question.title
        body = question.body

        "extracting the formulas from question title and writing them on the file"
        formula_in_title = get_list_of_formulas(title)
        for formula in formula_in_title:
            csv_writer.writerow([str(formula_id), str(question_id), str(question_id), "title", formula])
            formula_id += 1

        "extracting the formulas from question body and writing them on the file"
        formulas_in_body = get_list_of_formulas(body)
        for formula in formulas_in_body:
            csv_writer.writerow([str(formula_id), str(question_id), str(question_id), "question", formula])
            formula_id += 1

        "extracting the formulas from question comments and writing them on the file"
        if question_id in dr.comment_parser.map_of_comments_for_post:
            comment_list = dr.comment_parser.map_of_comments_for_post[question_id]
            "iteration on the comments for the question"
            for comment in comment_list:
                formulas_in_comment = get_list_of_formulas(comment.text)
                for formula in formulas_in_comment:
                    csv_writer.writerow([str(formula_id), str(comment.id), str(question_id), "comment", formula])
                    formula_id += 1

        "extracting the formulas from the answers given to the question and writing them on the file"
        answer_list = dr.post_parser.map_questions[question_id].answers
        if answer_list is not None:
            for answer in answer_list:
                "answer body"
                formulas_in_body = get_list_of_formulas(answer.body)
                for formula in formulas_in_body:
                    csv_writer.writerow([str(formula_id), str(answer.post_id), str(question_id), "answer", formula])
                    formula_id += 1
                "answer comment"
                if answer.post_id in dr.comment_parser.map_of_comments_for_post:
                    comment_list = dr.comment_parser.map_of_comments_for_post[answer.post_id]
                    for comment in comment_list:
                        formulas_in_comment = get_list_of_formulas(comment.text)
                        for formula in formulas_in_comment:
                            csv_writer.writerow(
                                [str(formula_id), str(comment.id), str(question_id), "comment", formula])
                            formula_id += 1


def read_question_id(file_path):
    """
    This input file contains list of question ids that represents the question ids of topics for
    task one.
    """
    file = open(file_path)
    line = file.readline().strip()
    lst_ids = []
    while line:
        lst_ids.append(int(line))
        line = file.readline().strip()
    return lst_ids


def extract_formulas_from_topics(clef_home_directory_file_path):
    dr = DataReaderRecord(clef_home_directory_file_path)

    """
    This list will have the question ids [post id] of each of the topics.
    """
    lst_question_ids = read_question_id("queries.txt")

    formula_id = 1
    topic_id = 1

    "the file that will save the topic formulas"
    result_file = open("Formula_topics_latex.tsv", "w", encoding="utf-8", newline='')
    csv_writer = csv.writer(result_file, delimiter='\t')
    csv_writer.writerow(["id", "topic_id", "thread_id", "type", "formula"])

    "iterating on the topics"
    for question_id in lst_question_ids:
        question = dr.post_parser.map_questions[question_id]
        title = question.title
        body = question.body

        "extracting formulas from topic title"
        formula_in_title = get_list_of_formulas(title)
        for formula in formula_in_title:
            csv_writer.writerow(["q_" + str(formula_id), "A." + str(topic_id), question_id, "title", formula])
            formula_id += 1

        "extracting formulas from topic body"
        formulas_in_body = get_list_of_formulas(body)
        for formula in formulas_in_body:
            csv_writer.writerow(["q_" + str(formula_id), "A." + str(topic_id), question_id, "question", formula])
            formula_id += 1
        topic_id += 1


def main():
    "Extracting formulas from collection"
    original_arqmath_dataset_directory = "Clef" #"C:/Users/Behrooz/Desktop/Clef"
    extract_formulas_from_MSE_dataset(original_arqmath_dataset_directory)
    "Extracting formulas from topics"
    extract_formulas_from_topics(original_arqmath_dataset_directory)


if __name__ == '__main__':
    main()
