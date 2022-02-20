This code provide the conversion utilities to convert LaTex representation to Presentation and Content MathML.

First run the install command to install the requirements; besides the Python requirements, you should also install LaTeXML 0.8.5.
As an alternative to the install command, you can also build a Docker image using the `Dockerfile` in this directory, which will install all python requirements as well as LaTeXML.

Run the code `latexml_conversions.py` that converts the sample TSV file `1_test_latex.tsv` to its opt and slt files.

Run the code on LaTeX TSV files provided on ARQMath Google drive, [here](https://drive.google.com/drive/u/1/folders/1o0JnMlyCtNCnW4cq7xwh_btr7qM36mZz), after decompressing the file.
Here is the sample command to extract intermediate MathML representations:
```
python3 latexml_conversions.py ./latex_representation_v3  1 ./conversion_results
```
where `latex_representation_v3` is the directory having the LaTex TSV filse and `conversion_results` is the directory to save the intermediate representations.

## Note on reproducibility

TeX makes it difficult to detect whether an error has occured during the conversion of a formula from LaTeX to XML.
Therefore, we made the `latexml_conversions.py` code non-deterministic in that it will pass formulae to LaTeXML in different order every time you run it.
Running `latexml_conversions.py` several times will produce several sets of results, where different formulae failed to convert.
Combining the different sets of results will therefore greatly improve your conversion rates.
In our experiments, we received ca 15K failures (5%) per a TSV file in a single run. Combining two runs reduced the failures to ca 6K (2%) per a TSV file.

For a more technically advanced approach that is fully deterministic and with higher conversion rate, please see the [latexml-runner](https://github.com/dginev/latexml-runner/releases/tag/0.1.1) by @dginev.
