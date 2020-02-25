# Table of Contents  
[ARQMath Clef 2020](#arqmath)  

[Collection](#collection)

[Available Tools](#tools)

[Sample Topics](#topics)

[Getting Started](#started)

<a name="arqmath"></a>
# ARQMath Clef 2020
[ARQMath](https://www.cs.rit.edu/~dprl/ARQMath/) lab at [CLEF 2020](https://clef2020.clef-initiative.eu/).  focuses on mathematical information retrieval. There will be two tasks for this lab:
  ### Task 1 
  Given a math question (a question related to some mathematical information need that contains at least one formula), participants will retrieve a list of possible answers to that question, ranked based on relevance.
  
  ### Task 2
  Given a formula as a query, participants should retrieve formulas related to the formula query.
  
 
The data available for participants covers posts from the year 2010 to 2018. The topics for both tasks are selected from posts (questions) created in 2019, which is hidden from the participants. Providing an example, for task 1, the participant will be given a real-world math question (from 2019 questions) and they will set of relevant answers that were created for other questions in the years 2010 to 2018. Further information please check the ARQMath [webpage](https://www.cs.rit.edu/~dprl/ARQMath/). You may also consider joining the discussion forum [here](https://groups.google.com/forum/#!forum/arqmath-lab).
 
<a name="collection"></a>
# Collection
In this lab, we will be using data from [Math Stack Exchange](https://math.stackexchange.com/) (MSE)The dateset for this lab is currently available on [Google Drive](https://drive.google.com/drive/folders/1ZPKIWDnhMGRaPNVLi1reQxZWTfH2R4u3?usp=sharing). This data was provided by [Archive](https://archive.org/) and several preprocessing have been done on the initial data. There are 7 files in this dataset:
  #### Users
  Users can post questions and answers and therefore each post is written by a user. Each user has a unique id along with other information such as display name, age, location, the date they created their profile and the reputations points earned based on their activities on MSE such as receiving an "up" vote on an answer given.
  #### Badges
  Besides the reputation for each user, they can have a list of badges they received. There are three classes of badges 3:bronze, 2:silver, and 1:gold. Each badge is linked to a user by user id.
  #### Votes
  Members of MSE, can give different votes to questions and answers. In the vote file, for each vote, there is a unique id, related post id, vote type [1 to 13], vote date and the user id of the voter.
  #### Tags  
  Each question on the MSE, can have different tags that are determined by the user posting the question. In tag file, one can find a list of all possible tags with their repetition count. However, in the post file, you can get the exact question tags.
 #### Comments
 Users can comment on both questions and answers. In the comment file, each comment has its own unique id, along with the related post id, the id of the user who wrote the comment, its creation date, its text, and score.
  #### PostLinks
  Each question on MSE can be associated with other questions; it can be related to another question or it can be its duplicate.
  In the post links file, each link has a unique id, the post id of the question, the post id of the related question (relatedpostid), the link type [1:related, 3:duplicate].
#### PostHistory
  It is possible that several edits have been applied to a post. While in the post file, there is only the final version of the post, in this file, one can finds edits on a post. The data provided in this file, shows edit id, type of edit, post id, revision GUI id, creation date, user id and display name, comment, text and close reason id. 
  #### Posts
  This is the main file for the task, where there are both questions and answers. Each post has a unique id, post type [1: question, 2:answer], the creation date, body, score and view count. For each answer, there is parent id which shows the question id for which the answer was provided. Each question has a title, set of tags and answer count.
  
 Here is summary of the fields in each xml file from the readme file provided by Archive:
 - Files:
   - **badges**.xml
       - UserId, e.g.: "420"
       - Name, e.g.: "Teacher"
       - Date, e.g.: "2008-09-15T08:55:03.923"
   - **comments**.xml
       - Id
       - PostId
       - Score
       - Text, e.g.: "@Stu Thompson: Seems possible to me - why not try it?"
       - CreationDate, e.g.:"2008-09-06T08:07:10.730"
       - UserId
   - **posts**.xml
       - Id
       - PostTypeId
          - 1: Question
          - 2: Answer
       - ParentID (only present if PostTypeId is 2)
       - AcceptedAnswerId (only present if PostTypeId is 1)
       - CreationDate
       - Score
       - ViewCount
       - Body
       - OwnerUserId
       - LastEditorUserId
       - LastEditorDisplayName="Jeff Atwood"
       - LastEditDate="2009-03-05T22:28:34.823"
       - LastActivityDate="2009-03-11T12:51:01.480"
       - CommunityOwnedDate="2009-03-11T12:51:01.480"
       - ClosedDate="2009-03-11T12:51:01.480"
       - Title
       - Tags
       - AnswerCount
       - CommentCount
       - FavoriteCount
   - **posthistory**.xml
	   - Id
	   - PostHistoryTypeId
			- 1: Initial Title - The first title a question is asked with.
			- 2: Initial Body - The first raw body text a post is submitted with.
			- 3: Initial Tags - The first tags a question is asked with.
			- 4: Edit Title - A question's title has been changed.
			- 5: Edit Body - A post's body has been changed, the raw text is stored here as markdown.
			- 6: Edit Tags - A question's tags have been changed.
			- 7: Rollback Title - A question's title has reverted to a previous version.
			- 8: Rollback Body - A post's body has reverted to a previous version - the raw text is stored here.
			- 9: Rollback Tags - A question's tags have reverted to a previous version.
			- 10: Post Closed - A post was voted to be closed.
			- 11: Post Reopened - A post was voted to be reopened.
			- 12: Post Deleted - A post was voted to be removed.
			- 13: Post Undeleted - A post was voted to be restored.
			- 14: Post Locked - A post was locked by a moderator.
			- 15: Post Unlocked - A post was unlocked by a moderator.
			- 16: Community Owned - A post has become community owned.
			- 17: Post Migrated - A post was migrated.
			- 18: Question Merged - A question has had another, deleted question merged into itself.
			- 19: Question Protected - A question was protected by a moderator
			- 20: Question Unprotected - A question was unprotected by a moderator
			- 21: Post Disassociated - An admin removes the OwnerUserId from a post.
			- 22: Question Unmerged - A previously merged question has had its answers and votes restored.
		- PostId
		- RevisionGUID: At times more than one type of history record can be recorded by a single action.  All of these will be grouped using the same RevisionGUID
		- CreationDate: "2009-03-05T22:28:34.823"
		- UserId
		- UserDisplayName: populated if a user has been removed and no longer referenced by user Id
		- Comment: This field will contain the comment made by the user who edited a post
		- Text: A raw version of the new value for a given revision
			- If PostHistoryTypeId = 10, 11, 12, 13, 14, or 15  this column will contain a JSON encoded string with all users who have voted for the PostHistoryTypeId
			- If PostHistoryTypeId = 17 this column will contain migration details of either "from <url>" or "to <url>"
		- CloseReasonId
			- 1: Exact Duplicate - This question covers exactly the same ground as earlier questions on this topic; its answers may be merged with another identical question.
			- 2: off-topic
			- 3: subjective
			- 4: not a real question
			- 7: too localized
   - **postlinks**.xml
     - Id
     - CreationDate
     - PostId
     - RelatedPostId
     - PostLinkTypeId
       - 1: Linked
       - 3: Duplicate
   - **users**.xml
     - Id
     - Reputation
     - CreationDate
     - DisplayName
     - EmailHash
     - LastAccessDate
     - WebsiteUrl
     - Location
     - Age
     - AboutMe
     - Views
     - UpVotes
     - DownVotes
   - **votes**.xml
     - Id
     - PostId
     - VoteTypeId
        - ` 1`: AcceptedByOriginator
        - ` 2`: UpMod
        - ` 3`: DownMod
        - ` 4`: Offensive
        - ` 5`: Favorite - if VoteTypeId = 5 UserId will be populated
        - ` 6`: Close
        - ` 7`: Reopen
        - ` 8`: BountyStart
        - ` 9`: BountyClose
        - `10`: Deletion
        - `11`: Undeletion
        - `12`: Spam
        - `13`: InformModerator
     - CreationDate
     - UserId (only for VoteTypeId 5)
     - BountyAmount (only for VoteTypeId 9)
	
<a name="tools"></a>
# Available tools
To facilitate the data loading, the lab organizer provided a python code to read all the data and iterate over it. The code is available on [github](https://github.com/ARQMath/ARQMath). Also with this code, participants can view each thread (question along with answers and other related information) as html file. The entities with their main attributes are shown in this ![Class Diagram](https://github.com/ARQMath/ARQMathDataset/blob/master/Clef_Class%20Diagram.jpg).

<a name="topics"></a>
# Sample Topics
There are 3 sample topics (questions) provided for task 1. To extract the title of the question, you can use "h1" tag. The post is located in "postcell" div. (You can also use our provided tools (read the related documentation.)) The current qrel file is created just as an example. The criteria for selecting the candidate relevant documents for now is based on the duplicate and related post links that exist in the original math stack exchange dataset (from 2010 to 2019) and relevance is determined based on the community scores for each answer. There are 4 different relevance scores as follows:

Relevance degree | Not relevant | Low | Medium | High
--- | --- | --- | --- |--- |
Score | 0 | 1 | 2 | 3


<a name="started"></a>
# Getting Started
The ARQMath google drive, contains 4 directories. All the files have version and only the version that should be used for the task is kept in the directory and the older versions are kept in Old versions directory.

The collection directory contains all the data files (2010-2018) that will be used for both tasks one and two. Each of the two tasks has its own directory. Note that these directories will be used by participants to train their model, and also the retrieval results for both tasks are from these documents.

For task one, there are three sample topics provided for now in Task1 directory. The sample qrel and query files are created for these three topics. Also, a sample retrieval file is provided which is in standard trec format and evaluation can be done with trec eval tools.

For task two, the data will be available soon.

Finally, the formula directory provides all the formulas in the collection in 2 files. The formula_latex.tsv file is showing the Latex representation of formulas.  There are 5 columns in these files showing formula id, post id, thread id, type of post they appeared in which can be question, answer, comment or title and finally formula itself which is represented accordingly. The MathMl.zip file contains two tsv files in the same format of latex file which show opt(operator tree) and slt (symbol layout tree) representation of formulas.

Note that all formulas have a unique id. In the collection, formulas are located in "math-container" tags. Using our provided tools, by defining the post id and formula id, participants are able to extract the formula, however, all the formulas are available in the tsv file. Also, it should be mention, our definition of formula is any string between two dollars ($) signs. Therefore, our dataset might contain noise (for instance, the cases that in the post, dollar sign is used as currency more than one time).

Check the [ARQMath forum](https://groups.google.com/forum/#!forum/arqmath-lab) for any further information.
