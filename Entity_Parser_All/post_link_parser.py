import codecs
from bs4 import BeautifulSoup


class PostLinkParser:
    """
    This class reads the whole Post Link file.
    """
    def __init__(self, xml_post_link_file_path):
        with codecs.open(xml_post_link_file_path, "r", "utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
        all_post = soup.find_all("row")
        self.map_duplicate_posts = {}
        self.map_related_posts = {}
        for post in all_post:
            attr_dic = post.attrs
            post_id = int(attr_dic["postid"])
            related_post_id = int(attr_dic["relatedpostid"])
            link_type_id = int(attr_dic["linktypeid"])

            if link_type_id == 3:  # Duplicate
                if post_id in self.map_duplicate_posts:
                    self.map_duplicate_posts[post_id].append(related_post_id)
                else:
                    self.map_duplicate_posts[post_id] = [related_post_id]
            elif link_type_id == 1:  # Related
                if post_id in self.map_related_posts:
                    self.map_related_posts[post_id].append(related_post_id)
                else:
                    self.map_related_posts[post_id] = [related_post_id]
