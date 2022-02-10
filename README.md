# ARQMath Lab at CLEF 2020 to 2022
This code provide a data reader for [ARQMath](https://www.cs.rit.edu/~dprl/ARQMath/). 

## Getting Started

To begin the code, first download and locate the ARQMath Dataset from [here](https://drive.google.com/drive/folders/1YekTVvfmYKZ8I5uiUMbs21G2mKwF9IAm?usp=sharing).

Locate the XML files in directory `ARQMath` and use this directory as `ds` parameter for ```post_reader_record.py```.

Use ```post_reader_record.py``` to read the data using a ```DataReaderRecord```. Each file in the dataset, is related to at least one entity. For instance, the `user.xml` file, contains the information for `user` entitiy. Therefore, the ```DataReaderRecord``` has different parser for each of the files and links all the related information.

The sample commands are shown in ```post_reader_record.py``` to read data such as reading questions with a specific tag, reading answers given from a specific user and generating html view files.


Note that the DataReader is used for reading the test collection. In order to read the questions, please use the ```topic_file_reader.py```. The sample commands on available in this file.

## Test Files
```run_id_fix```: this script is used for finding missing formula ids in the Posts.xml file and located formula id in `math-container` HTML tags. Pass the source directory to this command that contains the latest version of XML posts file (Posts.V1.2.xml) and the latest version of latex directory (latex_representation_v2).
This code will find the missing formula ids (missed_formula_id.txt), regenerate XML post file (Posts.V1.3.xml), and refind the missing formula ids (new_missed_post_id.txt).

## Authors

This code is provided by [ARQMath](https://www.cs.rit.edu/~dprl/ARQMath/) lab organizers. 

## Lisence 
On using this code please cite the following paper:
[Finding Old Answers to New Math Questions: The ARQMath Lab at CLEF 2020](https://link.springer.com/content/pdf/10.1007/978-3-030-45442-5_73.pdf)
