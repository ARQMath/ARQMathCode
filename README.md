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
Also, download the updated LaTex files (with HTML encoding fixed), `latex_representation_v3`, from [here](https://drive.google.com/drive/folders/1o0JnMlyCtNCnW4cq7xwh_btr7qM36mZz?usp=sharing) and unzip it.
Run the command from the *root directory* with three inputs: old comments.xml file path, new comments.xml file path and latex directory. 
Example command:
```
Prepare_Dataset/commands/generate_annotated_comment_xml ./Comments.V1.2.xml ./Comments.V1.3.xml ./latex_representation_v3/ 
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
Prepare_Dataset/commands/generate_annotated_post_xml ./Posts.V1.2.xml ./Posts.V1.3.xml ./latex_representation_v3/ 
```

This code reads the older version of post file and LaTex formulas, detected the formulas that are in the post file. 
It first creates two text files containing the formula ids of those that their post do not exist, named `missed_formulas_post_not_available.txt`
and another file `missed_formulas_not_available.txt` that contains formulas that are not in their related post. These two 
files will be later used to regenerate TSV formula index files.

In the next step, the code regenerates the Posts.XML file by ignoring the unavailable formulas and checking if the formulas are correctly
located inside the `math-container` tag.

Finally, 10 formulas are randomly selected from those inside posts (answers and questions), and prints their id, latex and post body for visual (manual) testing.
It also, check all the formulas from the posts to print how many formulas are not correctly located in xml file.

### 3. Generating HTML Thread Files
This command generates the supplementary HTML thread files, that can be used for viewing question in a format similar to MathStackExchange.
**Note** that these files are not used for the tasks and are just as a mean of visualization for analysis purposes.

**Result File Structure.** As the test collection has questions from 2010 to 2018, the threads are created in separate directories, based on 
the question post year, each directory containing the questions from that year. For each year, questions from different 
months are separated in their associated directory. Finally, each directory, start with the lowest question id in that month
and year. For example, the directory `16020_2011` has the questions posted in `2011` and questions in this year, start with 
id 16020. Inside this directory, there are 12 subdirectories for each month. For example, directory `24324_03` contains
questions posted in March and question ids in this month starts from `24324`.

**Data.** Download all the XML files in ARQMath test collection and locate them in a single directory.
(at the moment, use this [link](https://drive.google.com/drive/folders/1Ge8P7iAkEZQWseHuRR1Yhzn_aS7H9U4s?usp=sharing) which
is the draft for the latest version of dataset, having correct math-container tags and formula ids).

**Run Command.** Run the command from the root directory with two inputs: ARQMath directory path, Destination Directory path.
ARQMath directory contains all the XML files and Destination directory is where the threads are generated.
Example command:
```
Prepare_Dataset/commands/generate_html_threads ./ARQMath_Data ./CollectionByYear
```

### 4. Generating Topic Files
This command is used to generate the topics XML files for task 1 and 2 with the TSV index files of formulas latex/slt/opt representations.
**Data.** Download the Raw Math Stack Exchange XML file located [here](https://drive.google.com/drive/folders/1AJ41HKqGthixfmBMKphxXXU31goNLLGk?usp=sharing), named `Posts_cut2021.xml`.
You need two other files one having the topic question ids for task 1 and the other having the topic formulas for task 2.
They can be downloaded from [here](https://drive.google.com/drive/folders/1AJ41HKqGthixfmBMKphxXXU31goNLLGk?usp=sharing).

**Run Command.** From the root directory, run the command `generate_topic_files` similar to example below:
```
Prepare_Dataset/commands/generate_topic_files ./Posts_cut_2021.xml ./task1_2022_topics.tsv ./task2_2022_formula_topics.tsv
```

**Outputs.** Two XML files for task 1 and 2 will be generated in the root directory with names `Topics_Task1_v0.1.xml` and `Topics_Task2_v0.1.xml`, accordingly.
Also, the TSV index files for the formulas in the topics will be generated in the files `Topics_Formulas_Latex.v0.1.tsv`, 
`Topics_Formulas_SLT.v0.1.tsv`, and `Topics_Formulas_OPT.v0.1.tsv`.
## Authors

This code is provided by [ARQMath](https://www.cs.rit.edu/~dprl/ARQMath/) co-organizers Behrooz Mansouri.

## Lisence 
On using this code please cite the following paper:
[Finding Old Answers to New Math Questions: The ARQMath Lab at CLEF 2020](https://link.springer.com/content/pdf/10.1007/978-3-030-45442-5_73.pdf)
