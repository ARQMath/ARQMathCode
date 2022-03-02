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


Note that the DataReader is used for reading the test collection. 
In order to read the questions, please use the ```topic_file_reader.py```. For task 2, use `topic_file_reader_task2.py`
The sample commands on available in this file.

## Creating Test Collection
Here are the steps to build ARQMath test collection. In each step we explain the commands use to achieve the goal.

### 1. Extracting Formulas from MathStackExchange
This command is used to generate TSV index file for the formulas inside the MathStackExchange Snapshot available in the 
[Internet Archive](https://archive.org/download/stackexchange/math.stackexchange.com.7z). 

**Data.** Download the Raw Math Stack Exchange XML file located on the Internet Archive. This data includes the XML files
used in the ARQMath test collection. (Note that only the posts from 2010 to 2018 are included from *01-March-2020 snapshot*)
The output of this command is list of TSV files containing the LaTex representations of formulas, which will be used to extract visual ids and MathML presentations.

**Run Command.** From the root directory, run the command `extract_formulas_from_collection` similar to example below:
```
Prepare_Dataset/commands/extract_formulas_from_collection ./archive_mse ./latex_dir
```
### 2. Generating Presentation (SLT) and Content (OPT) MathML from Latex TSV Files
This command is used to generate TSV index file for Presentation and content MathML from the LaTex TSV files.
First run the `install` command to install the requirements; besides the Python requirements, you should also install LaTeXML 0.8.5.

Before passing formulas to LaTeXML, we have included one additional step,
to verify LaTex strings validation. We use functions defined in `latex_validation.py`, 
that aims to first correct mal-formatted LaTex formulas. 
For example, we aim to fix the issues with unmatched delimiters such as `{}` or `$`. We record these changes, in files named `modified`. 
Also, there are formulas that cannot be converted using LaTeXML, those including `\newcommand` and `\def` are ignored and not passed to LaTeXML. 

We also noted that, in some cases, a failure in the batch of formulas passed to LaTeXML, can cause failure
for other formulas in that batch. Therefore, we did 3 steps of conversions, first passing formulas in batch size of 100.
We then used this result for two purposes. One, we check if a formulas such as $m$ was converted in one batch and not another one. If the formula was
converted in other batch, we would use that representation. Two, we list the failed formulas and passed them in the second round
of conversion, this time with batch size of 10. Finally, in the third, round, we used batch size of 1 on the failed formulas.
Overall, out of 28,320,920 formulas in the ARQMath Test Collection, we have 53,610 failed cases.

##### Round 1
Run the command to get MathML intermediate representations on LaTeX TSV files provided on [ARQMath Google Dirve](https://drive.google.com/drive/folders/18bHlAWkhIJkLeS9CHvBQQ-BLSn4rrlvE?usp=sharing)
as follows:
```
Prepare_Dataset/commands/extract_mathml r1 ./latex_dir 1
```
Running this command will generate directory `./temp_round1_intermediate` and saves 5 TSV files related to TSV LaTex file with index 1
that was passed to this command: slt, opt, failed, modified, not_passed.

* The slt file contains the SLT representation of formulas and empty string if conversion has failed. This file is TSV with
two column first having formula id and the second the slt representation. 
* The similar file is created for opt.
* The failed file contains the list of formula id (in each line) that LaTeXML produced no MathML for them.
* The not_passed file contains the list of formulas that were not passed to LaTeXML as we knew they would cause issue. This included the formulas with \newcommand, \def, and HTML tags. 
* The modified file is a TSV having formula id, the original formula representation and the modified version of the formula.

**Notes**
1. This command should be ran on all the TSV files, first.
2. The location of formula LaTex representation can be different in TSV input files.
The formula index in the TSV files is set inside `latexml_conversions_with_check.py --> round_1` method. 

After for all the 101 TSV files the intermediate SLT/OPT conversions are done, 
run the following code to post-process the results and save the results in directory `./temp_round1_combined`.
```
Prepare_Dataset/commands/extract_mathml p1 ./latex_dir
```
This step is useful as it is possible that a formula has failed in one file but not the other, and by running 
this command we check if for a LaTex representation, the conversion results is available in other files or not.
In the result directory for each source LaTeX file, there will be SLT, OPT and failed files.
The failed files will be passed to round 2 for another attempt for conversion.
##### Round 2
The second round uses the failure files from post-processed results of round 1 and provide conversion results in the 
same exact format as round 1 in the directory `./temp_round2_intermediate`. **Note** that in this round we use batch sie of 10
and also only pass the formulas with failure after post-processing round 1 results. For conversion use the similar command
as for round 1 by changing `r1` to `r2`.

After for all the 101 TSV files the intermediate SLT/OPT conversions are done, 
run the similar command for post-processing used in round 1, and replace `p1` with `p2`
to post-process the results from this round and combine it with round one and save them in directory `./temp_round12_combined`.

##### Round 3
The last round uses batch size of 1 and passes the formulas failed after combining the first two round results.
Run the command similar to round 1, by replacing `r1` with `r3` on all the LaTeX TSV files. The conversion results will be saved in 
directory `./temp_round3_intermediate`. Then use the post-processing command same as round 1 by changing `p1` to `p3`.
This will produce the final SLT/OPT representations in directory `./temp_round123_combined`.

After conversions, you may run following command to remove the previous intermediate index files created:
```
Prepare_Dataset/commands/extract_mathml d
```

### 3. Generating Visual Ids
##### ARQMath-2
Visual Ids are used for clustering and deduplication of retrieval results for formula search task (Task 2).
The formulas with similar appearance are assigned a unique visual id. This is determined by first considering the SLT representation
of formulas and if SLT is not available based on LaTex string representation. For SLT, Tangent-S system was used to generate
SLT strings and for LaTeX, spaces in the formulas were ignored.

**Data.** To generate the TSV file that has (formula id, visual id), the intermediate SLT representations from Step 2 and LaTex 
TSV files from Step 1 are required. Run the following command:

```
Prepare_Dataset/commands/generate_visual_ids ./latex_dir ./temp_round123_combined ./formula_visual_id.tsv
```
where the first input is path to directory having LaTex TSV files, second input is where the intermediate
SLT representations are located and the last input save the mapping of formula ids to their visual id.
##### ARQMath-3 Fix
After ARQMath-2, the organizer were notified that some formulas have wrong visual id.
For fixing this issue, first the visual ids with wrong instances in them were detected and saved in file
`visual_ids_with_issue.txt`. This was done based on number of unique SLT string and LaTex string in that cluster.
Then, for each cluster with issue, the formula with maximum number of instances would keep the current
visual id and the rest of the formulas would get a new visual id (if the cluster not existing.)

To break the ties, we first consider the qrel file from ARQMath-2. Sub-cluster with formulas with higher
score in qrel will keep their visual ids. In the tie was not broken, then the formulas in the cluster with the lowest formula id 
will keep its visual id.

**Data** Download the ARQMath-2 Task-2 qrel file with formula ids (`qrel_task2_2021_formula_id_all.tsv`) from [here](https://drive.google.com/drive/folders/1iucnTr9ZaI0tXyqfzC_8NB8DfE8Y0emm?usp=sharing).
Also get the previous version of LaTeX TSV files [v2](https://drive.google.com/drive/folders/1kZeaLlwV5ARXesmTNORNh8Bz2QcSb3m8?usp=sharing).
Note that we apply the fix, you need to run the commands from the previous step to have the intermediate SLT representations.

Run the following command:
```
Prepare_Dataset/commands/fix_visual_ids ./latex_representation_v2 ./temp_round123_combined ./qrel_task2_2021_formula_id_all.tsv ./changed_visual_ids
```
where the first input is the directory having TSV files, the second input is the directory for intermediate SLT representations
, the third input is the path to ARQMath-2 qrel and finally the last input specifies where to save the result.

The result file is TSV in form of (formula id, old visual id, new visual id). 

### 4. Generating Formula TSV Index Files 
Steps 1 to 3 will provide information needed for the final index files.

##### ARQMath-2
To generate the final TSV index files, run the following command:
```
Prepare_Dataset/commands/generate_index_files ./latex_rep ./formula_visual_id.tsv ./temp_round123_combined ./index_dir
```
The first input is the directory having LaTeX TSV files from step 1. The second input, is the visual id map file generated from step 3.
The third input has the intermediate representations from step 2. Finally, the last input is the directory that generates
three subdirectory for LaTex, SLT and OPT representations. The TSV files in all three subdirectories have similar format and information
only the representations of formulas are different.

##### ARQMath-3 
ARQMath-3 aims to provide a cleaner version of TSV index files and solve the issues detected in the previous years.
While the incorrect visual ids and representations assigned to formulas can be fixed with the previous steps,
there are additional steps that should be addressed. 

First, there are set of formulas in the previous version of TSV index files that do not exist in the collection (XML file).
To detect these formulas, commands from steps 5 and 6 should be run to detected formulas that are not in the post or comment files.
Second, for the formulas in the comment, we need to save the comment ids in another column. This information
can be obtained after running the commands from step 5. 

Run the following command from the root directory to generate index files:
```
Prepare_Dataset/formula_index_tsv_final_v2.py ./latex_representation_v2 ./changed_visual_ids ./temp_round123_combined ./missed_formulas_comment_before_correction ./missed_formulas_post_not_available.txt ./missed_formulas_not_available.txt ./formula_comment_id.tsv ./index_dir
```
Here are the descriptions of the sample input:
* ./latex_representation_v2: the previous version of latex formula index directory 
* ./changed_visual_ids: TSV file from step 3 recording formula id, old visual id and new visual id
* ./temp_round123_combined: intermediate conversion results from step 2 
* ./missed_formulas_comment_before_correction: file from step 5, that list missed formula id that were not detected in comment XML files
* ./missed_formulas_post_not_available.txt: this file is generated in step 6, having list of formulas that their post was not in the collection 
* ./missed_formulas_not_available.txt: this file is created from step 6, having list of formulas that are not inside the post
* ./formula_comment_id.tsv: 
this file is generated from step 5, where each formula id is assigned to a comment id if the formula is in the collection and is in a comment post
* ./index_dir: final result will be saved here. There will be 3 sub-directories for latex, slt and opt
representations

### 5. Generating XML file for Comments.
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
matches that formulas to their comment ids. Also, for the comments not available in the post it creates a list of missed formula ids in the 
file named `missed_formulas_comment_before_correction`. This file will be later used to regenerate formula TSV file with column `comment id`. The code
then regenerates newer version of comment file, with locating formulas inside the `math-container` tag.

Note that in the older version of XML file, there are formulas that are wrongly annotated. For example, formula $d$, was by mistake
annotated as letter 'd' in the word 'didn't'. Therefore, the previous annotations are removed.

Finally, 10 formulas are randomly selected from those inside comments, and prints their id, latex and comment body for visual (manual) testing.
It also, check all the formulas from the comments to print how many formulas are not correctly located in xml file.

### 6. Generating XML file for Posts. 

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

### 7. Generating HTML Thread Files
This command generates the supplementary HTML thread files, that can be used for viewing question in a format similar to MathStackExchange.
**Note** that these files are not used for the tasks and are just as a mean of visualization for analysis purposes.

**Data.** Download all the XML files in ARQMath test collection and locate them in a single directory.
(at the moment, use this [link](https://drive.google.com/drive/folders/1Ge8P7iAkEZQWseHuRR1Yhzn_aS7H9U4s?usp=sharing) which
is the draft for the latest version of dataset, having correct math-container tags and formula ids).

**Run Command.** Run the command from the root directory with two inputs: ARQMath directory path, Destination Directory path.
ARQMath directory contains all the XML files and Destination directory is where the threads are generated.
Example command:
```
Prepare_Dataset/commands/generate_html_threads ./ARQMath_Data ./CollectionByYear
```
**Outputs.** As the test collection has questions from 2010 to 2018, the threads are created in separate directories, based on 
the question post year, each directory containing the questions from that year. For each year, questions from different 
months are separated in their associated directory. Finally, each directory, start with the lowest question id in that month
and year. For example, the directory `16020_2011` has the questions posted in `2011` and questions in this year, start with 
id 16020. Inside this directory, there are 12 subdirectories for each month. For example, directory `24324_03` contains
questions posted in March and question ids in this month starts from `24324`.

### 8. Generating Topic Files
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
### 9. Generating Thread Files for Topics
This command is used to generate HTML views for Topics in task 1/3 and 2. To run this command first download
the XML topic files from [here](https://drive.google.com/drive/folders/1ZPKIWDnhMGRaPNVLi1reQxZWTfH2R4u3?usp=sharing), from the topics
directories. 

**Run Command.** From the root directory, run the command `generate_topics_html_threads` similar to example below:
```
Prepare_Dataset/commands/generate_topics_html_threads Topics_Task1_2022_V0.1.xml  Task1  Topics_Task2_2022_V0.1.xml  Task2
```

The html files will be generated in Task1 and Task2 directories accordingly. 
## Authors

This code is provided by [ARQMath](https://www.cs.rit.edu/~dprl/ARQMath/) co-organizers Behrooz Mansouri.

## Lisence 
On using this code please cite the following paper:
[Finding Old Answers to New Math Questions: The ARQMath Lab at CLEF 2020](https://link.springer.com/content/pdf/10.1007/978-3-030-45442-5_73.pdf)
