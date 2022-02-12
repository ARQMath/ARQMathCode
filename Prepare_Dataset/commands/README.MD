Here are set of commands to generate the dataset and run a tests.

1. Generating XML file for Comments. 

The goal of this command is to regenerate the Comments.xml file with formulas being correctly annotated in the file.
Each formula has a unique id and should be located in HTML span tag with class `math-container` and formula id.

There are 3 steps in this command:
1. Generating `formula_comment_id.tsv` file that associates the formula id to comment id
2. Regenerating the XML file with correctly locating the formula ids
3. Testing the generated XML file by printing 10 examples and then looking for all the formulas in the XML file

To run this code download the older version of Comments.xml file (Comments.V1.2.xml) from [ARQMath Google drive](https://drive.google.com/drive/folders/1YekTVvfmYKZ8I5uiUMbs21G2mKwF9IAm?usp=sharing).
Also, download the updated LaTex files (with HTML encoding fixed), `latex_representation_v3`, from [here](https://drive.google.com/drive/folders/1o0JnMlyCtNCnW4cq7xwh_btr7qM36mZz?usp=sharing).
Run the command from the *root directory* with three inputs: old comments.xml file path, new comments.xml file path and latex directory. 
Example command:
```
Prepare_Dataset/commands/generate_annotated_comment_xml "./Comments.V1.2.xml" "./Comments.V1.3.xml" "./latex_representation_v3/" 
```

This code reads the older version of comment file and LaTex formulas, detected the formulas that are in the comment file. It first creates a TSV file `formula_comment_id.tsv` that
matches that formulas to their comment ids. This file will be later used to regenerate formula TSV file with column `comment id`. The code
then regenerates newer version of comment file, with locating formulas inside the `math-container` tag.

Note that in the older version of XML file, there are formulas that are wrongly annotated. For example, formula $d$, was by mistake
annotated as letter 'd' in the word 'didn't'. Therefore, the previous annotations are removed.

Finally, 10 formulas are randomly selected from those inside comments, and prints their id, latex and comment body for visual (manual) testing.
It also, check all the formulas from the comments to print how many formulas are not correctly located in xml file.
