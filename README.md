# ARQMath Lab at CLEF 2020 to 2022
This code provide a simple data reader for [ARQMath](https://www.cs.rit.edu/~dprl/ARQMath/). 

## Getting Started

To begin the code, first download and locate the MSE ARQMath Dataset. Then you can simply use ```post_reader_record.py``` to read the data using a ```DataReaderRecord```. Each file in the dataset, is related to at least one entity. For instance, the '''user.xml''' file, contains the information for '''user''' entitiy. Therefore, the ```DataReaderRecord``` has different parser for each of the files and links all the related information.


Note that the DataReader is used for reading the data from 2010 to 2018. In order to read the questions, please use the ```question_entity.py'''.


## Authors

This code is provided by [ARQMath](https://www.cs.rit.edu/~dprl/ARQMath/) lab organizers. 

## Lisence 
On using this code please cite the following paper:
[Finding Old Answers to New Math Questions: The ARQMath Lab at CLEF 2020](https://link.springer.com/content/pdf/10.1007/978-3-030-45442-5_73.pdf)
