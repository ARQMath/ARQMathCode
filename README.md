# ARQMath Clef 2020
This code provide a simple data reader for [ARQMath](https://www.cs.rit.edu/~dprl/ARQMath/) lab at [CLEF 2020](https://clef2020.clef-initiative.eu/). 

## Getting Started

To begin the code, first download and locate the MSE ARQMath Dataset. Then you can simply use ```post_reader_record.py``` to read the data using a ```DataReaderRecord```. Each file in the dataset, is related to at least one entity. For instance, the '''user.xml''' file, contains the information for '''user''' entitiy. Therefore, the ```DataReaderRecord``` has different parser for each of the files and links all the related information.


Note that the DataReader is used for reading the data from 2010 to 2018. In order to read the questions, please use the ```question_entity.py'''.


## Authors

This code is provided by [ARQMath](https://www.cs.rit.edu/~dprl/ARQMath/) lab organizers. 

## Lisence 
On using this code please cite the following paper:
@inproceedings{mansouri2020finding,
  title={Finding Old Answers to New Math Questions: The ARQMath Lab at CLEF 2020},
  author={Mansouri, Behrooz and Agarwal, Anurag and Oard, Douglas and Zanibbi, Richard},
  booktitle={Advances in Information Retrieval: 42nd European Conference on IR Research, ECIR 2020, Lisbon, Portugal, April 14--17, 2020, Proceedings, Part II 42},
  pages={564--571},
  year={2020},
  organization={Springer}
}
