This code provide the conversion utilities to convert LaTex representation to Presentation and Content MathML.

First run the install command to install the requirements; besides the Python requirements, you should also install LaTeXML 0.8.5.

Run the code `latexml_conversions_with_check.py` that converts the sample TSV file `1_test_latex.tsv` to its opt and slt files.

Run the code on LaTeX TSV files provided on ARQMath Google drive, [here](https://drive.google.com/drive/u/1/folders/1o0JnMlyCtNCnW4cq7xwh_btr7qM36mZz), after decompressing the file.
Here is the sample command to extract intermediate MathML representations:
```
python3 latexml_conversions_with_check.py ./latex_representation_v3  1 ./conversion_results
```
where `latex_representation_v3` is the directory having the LaTex TSV filse and `conversion_results` is the directory to save the intermediate representations.

## Note on reproducibility
Before passing formulas to LaTeXML, we have included one additional step, to verify LaTex strings validation. We use functions defined in `latex_validation.py`, that aims to first correct mal-formatted LaTex formulas. For example, we aim to fix the issues with unmatched delimeters such as `{}` or `$`. Also, there are formulas that cannot be converted using LaTeXML, those including `\newcommand` and `\def` are ignored and not passed to LaTeXML. 

Also to make sure the same order of unique formulas are passed to LaTeXML in each run, after applying the set command from Python (which place item in random order), we sort the latex strings based on alphabet and then length.
