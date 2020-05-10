import xml.etree.cElementTree as ET
import csv
import os
import codecs

from bs4 import BeautifulSoup
from xml.dom import minidom


from Entity_Parser_Record.comment_parser_record import CommentParserRecord


def read_formula_file(formula_file_path):
    """
        Takes in formula file path and read it line by line and return two dictionaries:
        dic_res:
            key: post id, value: dictionary of (formula_id, formula_value)
        dic_id_type:
            key: formula_id, formula_type (title, answer, question)
        not that this class is for post preparation so there is no type comment
    """
    dic_res = {}
    dic_id_type = {}
    for file in os.listdir(formula_file_path):
        with open(formula_file_path+"/"+file, mode='r', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            first = False
            for row in csv_reader:
                if not first:
                    first = True
                    continue
                formula_id = (row[0])
                post_id = int(row[1])
                doc_type = row[3]
                formula = row[4]
                if post_id in dic_res:
                    dic_res[post_id][formula_id] = formula
                else:
                    temp = {formula_id: formula}
                    dic_res[post_id] = temp
                dic_id_type[formula_id] = doc_type
    return dic_res, dic_id_type


def set_formulas(text, post_id, map_formulas, map_id_type, text_type):
    """
    Input:
        text: the input text that its formulas need to be converted to Arqmath notation, where each formula has an
        unique id and is in math-container tag
        post_id: the post_id of the current text, question id, answer id or the comment id
        map_formulas: the dictionary in form of (post id, dictionary of (formula id: latex))
        map_id_type: the dictionary which shows where is each of the formulas located (formula_id: type)
        text_type: shows the current text (first input) is a title, question, answer or comment
    """

    "if there is not formula to this post just return the text"
    if post_id not in map_formulas:
        return text

    result_text = ""
    text = text.replace("\r", "\n", text.count("\r"))
    dic_formulas = map_formulas[post_id]
    "Iteration on the formulas in the current text"
    for formula_id in dic_formulas:
        """
            the formula should be located in the same type of text, why we have this?
            the title and question have the same ids, so if the formula is in both title and question,
            we do not know which one to replace (replace the original formula with the math-container tag one)
        """
        if map_id_type[formula_id] != text_type:
            continue
        "the original formula"
        formula = dic_formulas[formula_id]

        "the string that will be replaced by the original formula, it has math-container tag and formula id"
        to_write_string = "<span class=\"math-container\" id=\"" + str(formula_id) + "\">"

        """Each formula can be located in the text in one this 6 form, (text6) should not happen but 
        just added for the case. Note that in the formula index file from which we created the map 
        we only have the latex of formula not how the formula was located in the text. 
        
        For example a formula can be like "<span class="math-container> $a+b$ </span>" in the original MSE dataset
        but we only keep a+b.
        
        So we check which of these 6 format was the one that the original formula was written in, and also note in the 
        map, formulas are sorted based on their order in the original, so we use these 6 format, find their first
        occurrence and replace them with our desired text.
        """
        map_index = {}
        text1 = "<span class=\"math-container\">$$" + formula + "$$</span>"
        map_index[text1] = text.find(text1)
        text2 = "<span class=\"math-container\">$" + formula + "$</span>"
        map_index[text2] = text.find(text2)
        text3 = "<span class=\"math-container\">" + formula + "</span>"
        map_index[text3] = text.find(text3)
        text4 = "$$" + formula + "$$"
        map_index[text4] = text.find(text4)
        text5 = "$" + formula + "$"
        map_index[text5] = text.find(text5)
        # text6 = formula
        # map_index[text6] = text.find(text6)
        sorted_x = sorted(map_index.items(), key=lambda kv: kv[1])
        for item in sorted_x:
            if item[1] != -1:
                find_inx = text.find(item[0]) + len(item[0])
                temp = text[0:find_inx]
                text = text[find_inx:]
                result_text += temp.replace(item[0], to_write_string + formula + "</span>")
                break

    return result_text + text


def convert_mse_arqmath_post_file(xml_post_link_file_path, formula_latex_index_directory, new_xml_file_path):
    """First reads the formulas and save
    @param xml_post_link_file_path: Original post file from Archive
    @param formula_index_file_path: the formula index file (the tsv file containing the latex)
    @param new_xml_file_path: the result post file that will be used in ARQMath containing posts from 2010 to 2018 with
    annotated formulas.
    """
    map_formulas, dic_id_type = read_formula_file(formula_latex_index_directory)

    "Creating the root for the new post file [the one for ARQMath]"
    root = ET.Element("posts")

    "reading the original post file of MSE dataset from Archive"
    with codecs.open(xml_post_link_file_path, "r", "utf-8") as file2:
        soup = BeautifulSoup(file2, "html.parser")
        all_post = soup.find_all("row")
        "reading the original mse post file, row by row"
        for post in all_post:
            attr_dic = post.attrs
            post_id = int(attr_dic["id"])
            post_type_id = int(attr_dic["posttypeid"])

            "There are 4 post with type id 7 that is not defined in the collection readme file, we just eliminated them"
            if not (post_type_id == 1 or post_type_id == 2):
                continue

            creation_date = (attr_dic["creationdate"])

            "the post from 2019 were eliminated"
            if int(creation_date.split("T")[0].split("-")[0]) == 2019:
                continue

            sub = ET.SubElement(root, "row")
            "All these attributes are common in both questions and answers"
            sub.set('Id', str(post_id))
            sub.set('PostTypeId', str(post_type_id))
            sub.set('CreationDate', creation_date)
            if "viewcount" in attr_dic:
                sub.set('ViewCount', attr_dic["viewcount"])
            if "score" in attr_dic:
                sub.set('Score', attr_dic["score"])
            if "commentcount" in attr_dic:
                sub.set('CommentCount', attr_dic["commentcount"])
            if "owneruserid" in attr_dic:
                sub.set('OwnerUserId', attr_dic["owneruserid"])
            if "lastEditDate" in attr_dic:
                sub.set('LastEditDate', attr_dic["lastEditDate"])
            if "lastActivityDate" in attr_dic:
                sub.set('LastActivityDate', attr_dic["lastActivityDate"])
            if "lastEditorUserId" in attr_dic:
                sub.set('LastEditorUserId', attr_dic["lastEditorUserId"])
            if "communityOwnedDate" in attr_dic:
                sub.set('CommunityOwnedDate', attr_dic["communityOwnedDate"])
            if "lastEditorDisplayName" in attr_dic:
                sub.set('LastEditorDisplayName', attr_dic["lastEditorDisplayName"])

            "If the post is a question"
            if post_type_id == 1:  # Question

                title = (attr_dic["title"])
                "we want to linearize both title and body so that each post can be viewed in one row when using text " \
                "editors "
                title = title.replace("\n", " ", title.count("\n"))
                title = set_formulas(title, post_id, map_formulas, dic_id_type, "title")
                title = title.replace("\n", " ", title.count("\n"))
                sub.set('Title', title)

                body = (attr_dic["body"])
                body = body.replace("\n", " ", body.count("\n"))
                "Annotating the formulas"
                body = set_formulas(body, post_id, map_formulas, dic_id_type, "question")
                body = body.replace("\n", " ", body.count("\n"))
                sub.set('Body', body)

                if "commentcount" in attr_dic:
                    sub.set('CommentCount', attr_dic["commentcount"])
                if "answercount" in attr_dic:
                    sub.set('AnswerCount', attr_dic["answercount"])
                if "favouritecount" in attr_dic:
                    sub.set('FavoriteCount', attr_dic["favouritecount"])
                if "acceptedanswerid" in attr_dic:
                    sub.set('AcceptedAnswerId', attr_dic["acceptedanswerid"])
                if "closeddate" in attr_dic:
                    sub.set('ClosedDate', attr_dic["closeddate"])

                if "tags" in attr_dic:
                    sub.set('Tags', attr_dic["tags"])
            elif post_type_id == 2:
                "If the post is an answer"
                body = (attr_dic["body"])
                body = body.replace("\n", " ", body.count("\n"))
                "Annotating the formulas"
                body = set_formulas(body, post_id, map_formulas, dic_id_type, "answer")
                body = body.replace("\n", " ", body.count("\n"))
                sub.set('Body', body)
                sub.set('ParentId', attr_dic["parentid"])

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(new_xml_file_path, "w") as f:
        f.write(xml_str)


def convert_mse_arqmath_comment_file(comments_file_path, formula_latex_index_directory, result_file_path):
    """
    Takes in the Original comment file from MSE Archive, the extracted formula tsv file and the results file path
    for the new comment file and do the conversion.
    @param comments_file_path: The original MSE comment file, from Archive.
    @param formula_index_file_path: The extracted formulas tsv file
    @param result_file_path: The new xml comment file path.
    """
    map_formulas, map_id_type = read_formula_file(formula_latex_index_directory)
    comment_parser = CommentParserRecord(comments_file_path)
    root = ET.Element("comments")
    for post_id in comment_parser.map_of_comments_for_post:
        comment_lst = comment_parser.map_of_comments_for_post[post_id]
        for comment in comment_lst:
            creation_date = comment.creation_date
            if creation_date is None:
                continue
            if int(creation_date.split("T")[0].split("-")[0]) == 2019:
                continue
            score = comment.score
            text = comment.text
            post_id = comment.related_post_id
            user_id = comment.user_id
            text = set_formulas(text, comment.id, map_formulas, map_id_type, "comment")
            sub = ET.SubElement(root, "row")
            sub.set('Id', str(comment.id))
            sub.set('PostId', str(post_id))
            sub.set('Text', text)
        if score is not None:
            sub.set('Score', str(score))
        if creation_date is not None:
            sub.set('CreationDate', creation_date)
        if user_id is not None:
            sub.set('UserId', str(user_id))

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(result_file_path, "w") as f:
        f.write(xml_str)


def main():
    "Conversion of post file"
    convert_mse_arqmath_post_file("Posts.xml", "/home/bm3302/latex_representation", "Posts.V1.1.xml")
    "Conversion of comment file"
    convert_mse_arqmath_comment_file("Comments.xml", "/home/bm3302/latex_representation", "Comments.V1.1.xml")

if __name__ == '__main__':
    main()
