from ..Entities.User import User
from xmlr import xmliter


class UserParserRecord:
    """
        This class is used for reading the user file. It reads it record by record.
    """
    def __init__(self, xml_user_file_path, xml_badges_file_path):
        self.map_of_user = {}
        map_user_badges = UserParserRecord.read_badges(xml_badges_file_path)

        for attr_dic in xmliter(xml_user_file_path, 'row'):
            user_id = int(attr_dic["@Id"])
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

            if "@CreationDate" in attr_dic:
                creation_date = (attr_dic["@CreationDate"])
            if "@Age" in attr_dic:
                age = int(attr_dic["@Age"])
            if "@Location" in attr_dic:
                location = (attr_dic["@Location"])
            if "@Reputation" in attr_dic:
                reputation = int(attr_dic["@Reputation"])
            if "@Views" in attr_dic:
                last_access_date = int(attr_dic["@Views"])
            if "@WebsiteUrl" in attr_dic:
                website_url = (attr_dic["@WebsiteUrl"])
            if "@DownVotes" in attr_dic:
                down_votes = int(attr_dic["@DownVotes"])
            if "@UpVotes" in attr_dic:
                up_votes = int(attr_dic["@UpVotes"])
            if "@AboutMe" in attr_dic:
                about_me = (attr_dic["@AboutMe"])
            if "@LastAccessDate" in attr_dic:
                last_access_date = (attr_dic["@LastAccessDate"])
            if "@DisplayName" in attr_dic:
                display_name = (attr_dic["@DisplayName"])
            lst_badges = None
            if user_id in map_user_badges:
                lst_badges = map_user_badges[user_id]

            user = User(user_id, reputation, age, location, creation_date, views, lst_badges,
                        about_me, up_votes, down_votes, website_url, last_access_date,display_name)
            self.map_of_user[user_id] = user

    @staticmethod
    def read_badges(xml_badges_file_path):
        map_user_badges = {}
        if xml_badges_file_path is not None:
            for attr_dic in xmliter(xml_badges_file_path, 'row'):
                user_id = int(attr_dic["@UserId"])
                class_type = int((attr_dic["@Class"][0]))
                date = (attr_dic["@Date"])
                if user_id in map_user_badges:
                    map_user_badges[user_id].append((class_type, date))
                else:
                    map_user_badges[user_id] = [(class_type, date)]
        return map_user_badges
