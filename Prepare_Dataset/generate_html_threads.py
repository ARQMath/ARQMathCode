import os
import argparse
import sys
conf_path = os.getcwd()
sys.path.append(conf_path)

from post_reader_record import DataReaderRecord


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ad', type=str, help="ARQMath directory where XML files are located", required=True)
    parser.add_argument('-td', type=str, help="Thread directory to save HTML views", required=True)
    args = vars(parser.parse_args())
    arqmath_directory = args['ad']
    thread_directory = args['td']
    dr = DataReaderRecord(arqmath_directory)
    dr.get_all_html_pages(thread_directory)


if __name__ == '__main__':
    main()
