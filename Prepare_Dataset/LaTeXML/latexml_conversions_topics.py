#!/usr/bin/env python

# -*- coding:utf-8 -*-
import html
import os
import sys
import csv
conf_path = os.getcwd()
sys.path.append(conf_path)
from Prepare_Dataset.LaTeXML.latexml_conversions import get_conversion_results


def converting_latex_topics(latex_file_path, slt_file, opt_file):
    slt_file_res = open(slt_file, "w", newline='', encoding="utf-8")
    opt_file_res = open(opt_file, "w", newline='', encoding="utf-8")
    csv_writer_slt = csv.writer(slt_file_res, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    csv_writer_opt = csv.writer(opt_file_res, delimiter='\t', quoting=csv.QUOTE_MINIMAL)

    with open(latex_file_path, newline='', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
        header = next(csv_reader)
        csv_writer_slt.writerow(header)
        csv_writer_opt.writerow(header)
        for row in csv_reader:
            other_rows = row[0:4]
            latex = row[4]
            if not latex.startswith("$"):
                latex = "$" + latex + "$"
                try:
                    pmml_dict, cmml_dict = get_conversion_results([latex])
                    slt = pmml_dict[latex]
                    opt = cmml_dict[latex]
                    slt = slt.replace("<?xml version=\'1.0\' encoding=\'UTF-8\'?>", "")
                    opt = opt.replace("<?xml version=\'1.0\' encoding=\'UTF-8\'?>", "")

                except:
                    slt = ''
                    opt = ''
                    print(latex)

                slt = slt.replace("\n", " ")
                slt = html.unescape(str(slt))
                opt = opt.replace("\n", " ")
                opt = html.unescape(str(opt))
                slt = slt.strip()
                opt = opt.strip()
                csv_writer_slt.writerow(other_rows+[slt])
                csv_writer_opt.writerow(other_rows + [opt])
    slt_file_res.close()
    opt_file_res.close()
