import argparse

from post_reader_record import DataReaderRecord


def generate_all_htmls(arqmath_dir, destination_dir):
    dr = DataReaderRecord(arqmath_dir)
    lst_questions = dr.get_question_of_tag("calculus")
    lst_answers = dr.get_answers_posted_by_user(132)
    dr.get_html_pages([1, 5], "../html_files")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ad', type=str, help='ARQMath xml files directory')
    parser.add_argument('-d', type=str, help='destination directory')
    args = vars(parser.parse_args())

    arqmath_dir = args['ad']
    destination_dir = args['d']
    generate_all_htmls(arqmath_dir, destination_dir)


if __name__ == '__main__':
    main()