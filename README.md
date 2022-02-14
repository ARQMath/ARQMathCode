# ARQMath Lab Test Collection and Topics Creating/Reader 
This Repo provides the codes used to create [ARQMath](https://www.cs.rit.edu/~dprl/ARQMath/) collection and topics. It also provides
the code to read the ARQMath data. 

## Requirements
To install the requirements run the following code from the root directory:
```
./bin/install
```

To extract the Presentation/Content MathML representations, we use [LaTeXML](https://math.nist.gov/~BMiller/LaTeXML/) tool
version 0.8.5.

## Reading ARQMath Data

To begin the code, first download and locate the ARQMath Dataset from [here](https://drive.google.com/drive/folders/1YekTVvfmYKZ8I5uiUMbs21G2mKwF9IAm?usp=sharing).

Locate the XML files in directory `ARQMath` and use this directory as `ds` parameter for ```post_reader_record.py```.

Use ```post_reader_record.py``` to read the data using a ```DataReaderRecord```. Each file in the dataset, is related to at least one entity. For instance, the `user.xml` file, contains the information for `user` entitiy. Therefore, the ```DataReaderRecord``` has different parser for each of the files and links all the related information.

The sample commands are shown in ```post_reader_record.py``` to read data such as reading questions with a specific tag, reading answers given from a specific user and generating html view files.


Note that the DataReader is used for reading the test collection. In order to read the questions, please use the ```topic_file_reader.py```. The sample commands on available in this file.

## Creating Test Collection
Here are set of commands to generate the dataset and run the commands.

### 1. Generating XML file for Comments. 

The goal of this command is to regenerate the Comments.xml file with formulas being correctly annotated in the file.
Each formula has a unique id and should be located in HTML span tag with class `math-container` and formula id.

There are 3 steps in this command:
- Generating `formula_comment_id.tsv` file that associates the formula id to comment id
- Regenerating the XML file with correctly locating the formula ids
- Testing the generated XML file by printing 10 examples and then looking for all the formulas in the XML file

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

### 2. Generating XML file for Posts. 

The goal of this command is to regenerate the Posts.xml file with formulas being correctly annotated in the file and also 
detect the formulas in the ARQMath TSV formula index files that are not in the XML.
Each formula has a unique id and should be located in HTML span tag with class `math-container` and formula id.

There are 3 steps in this command:
- Generating two files `missed_formulas_not_available.txt` and `missed_formulas_post_not_available.txt`
that represents the formula ids of the formula that are not in the related post and formula ids of formulas that their post
does not exist in the XML file.
- Regenerating the XML file with correctly locating the formula ids
- Testing the generated XML file by printing 10 examples (randomly chosen; 5 questions and 5 answers) and then looking for all the formulas in the XML file

**Important note:** Compared to comments, posts in ARQMath collection are longer and also higher in number. Therefore, running this
code takes more time compared to the similar code for comments. (~ 1 hour)

To run this code download the older version of Posts.xml file (Posts.V1.2.xml) from [ARQMath Google drive](https://drive.google.com/drive/folders/1YekTVvfmYKZ8I5uiUMbs21G2mKwF9IAm?usp=sharing).
Also, download the updated LaTex files (with HTML encoding fixed), `latex_representation_v3`, from [here](https://drive.google.com/drive/folders/1o0JnMlyCtNCnW4cq7xwh_btr7qM36mZz?usp=sharing).
Run the command from the *root directory* with three inputs: old posts.xml file path, new posts.xml file path and latex directory. 
Example command:
```
Prepare_Dataset/commands/generate_annotated_post_xml "./Posts.V1.2.xml" "./Posts.V1.3.xml" "./latex_representation_v3/" 
```

This code reads the older version of post file and LaTex formulas, detected the formulas that are in the post file. 
It first creates two text files containing the formula ids of those that their post do not exist, named `missed_formulas_post_not_available.txt`
and another file `missed_formulas_not_available.txt` that contains formulas that are not in their related post. These two 
files will be later used to regenerate TSV formula index files.

In the next step, the code regenerates the Posts.XML file by ignoring the unavailable formulas and checking if the formulas are correctly
located inside the `math-container` tag.

Finally, 10 formulas are randomly selected from those inside posts (answers and questions), and prints their id, latex and post body for visual (manual) testing.
It also, check all the formulas from the posts to print how many formulas are not correctly located in xml file.
The test code for preparing the dataset are in `Prepare_Dataset/commands` directory. 
## Authors

This code is provided by [ARQMath](https://www.cs.rit.edu/~dprl/ARQMath/) co-organizers Behrooz Mansouri.

## Lisence 
On using this code please cite the following paper:
[Finding Old Answers to New Math Questions: The ARQMath Lab at CLEF 2020](https://link.springer.com/content/pdf/10.1007/978-3-030-45442-5_73.pdf)
