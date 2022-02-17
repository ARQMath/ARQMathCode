This code provide the conversion utilities to convert LaTex representation to Presentation and Content MathML.
First run the install command to install the requirements.
Run the code `latexml_conversions.py` that converts the sample TSV file 1_test_latex.tsv to its opt and slt files.
Run the code on LaTex TSV files provided on ARQMath Google drive, [here](https://drive.google.com/drive/u/1/folders/1o0JnMlyCtNCnW4cq7xwh_btr7qM36mZz), after decompressing the file.
Here is the sample command to extract intermediate MathML representations:
```
python3 latexml_conversions.py ./latex_representation_v3  1 ./conversion_results
```

where `latex_representation_v3` is the directory having the LaTex TSV filse and `conversion_results` is the directory to save the intermediate representations.
