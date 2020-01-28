import codecs
from bs4 import BeautifulSoup

from Entities.User import User


class UserParser:
    """
        This class reads the user file. It reads the whole file into the memory.
    """
    def __init__(self, xml_user_file_path, xml_badges_file_path):
        with codecs.open(xml_user_file_path, "r", "utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
        all_post = soup.find_all("row")
        self.map_of_user = {}
        map_user_badges = UserParser.read_badges(xml_badges_file_path)

        for post in all_post:
            attr_dic = post.attrs
            user_id = int(attr_dic["id"])
            creation_date = None
            age = None
            location = None
            reputation = None
            views = None
            about_me = None
            up_votes = None
            down_votes = None
            website_url = None
            last_access_date = None
            display_name = None

            if "creationdate" in attr_dic:
                creation_date = (attr_dic["creationdate"])
            if "age" in attr_dic:
                age = int(attr_dic["age"])
            if "location" in attr_dic:
                location = (attr_dic["location"])
            if "reputation" in attr_dic:
                reputation = int(attr_dic["reputation"])
            if "views" in attr_dic:
                last_access_date = int(attr_dic["views"])
            if "websiteurl" in attr_dic:
                website_url = (attr_dic["websiteurl"])
            if "downvotes" in attr_dic:
                down_votes = int(attr_dic["downvotes"])
            if "upvotes" in attr_dic:
                up_votes = int(attr_dic["upvotes"])
            if "aboutme" in attr_dic:
                about_me = (attr_dic["aboutme"])
            if "lastaccessdate" in attr_dic:
                last_access_date = (attr_dic["lastaccessdate"])
            if "displayname" in attr_dic:
                display_name = (attr_dic["displayname"])
            lst_badges = None
            if user_id in map_user_badges:
                lst_badges = map_user_badges[user_id]

            user = User(user_id, reputation, age, location, creation_date, views, lst_badges,
                        about_me, up_votes, down_votes, website_url, last_access_date,display_name)
            self.map_of_user[user_id] = user

    @staticmethod
    def read_badges(xml_badges_file_path):
        with codecs.open(xml_badges_file_path, "r", "utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
        all_post = soup.find_all("row")
        map_user_badges = {}
        for post in all_post:
            attr_dic = post.attrs
            user_id = int(attr_dic["userid"])
            class_type = int((attr_dic["class"][0]))
            date = (attr_dic["date"])
            if user_id in map_user_badges:
                map_user_badges[user_id].append((class_type, date))
            else:
                map_user_badges[user_id] = [(class_type, date)]
        return map_user_badges
