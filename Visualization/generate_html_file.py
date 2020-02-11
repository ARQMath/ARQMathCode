template_file = "Visualization/template.html"


class HtmlGenerator:
    @staticmethod
    def normalize_html_xml(text):
        count = text.count("&quot;")
        text = text.replace("&quot;", "\"", count)
        count = text.count("&apos;")
        text = text.replace("&apos;", "'", count)
        count = text.count("&lt;")
        text = text.replace("&lt;", "<", count)
        count = text.count("&gt;")
        text = text.replace("&gt;", ">", count)
        count = text.count("&amp;")
        text = text.replace("&amp;", "&", count)
        count = text.count("&#A;")
        text = text.replace("&#A;", "\n", count)
        return text

    @staticmethod
    def read_html(html_template):
        file = open(html_template)
        line = file.readline()
        content = ""
        while line:
            content += line
            line = file.readline()
        return content

    @staticmethod
    def replace_item(pattern, item, content_string):
        return content_string.replace(pattern, item)

    @staticmethod
    def generate_post(html, title, qid, qscore, post, answer_count, tag_lst, rel_dic,
                      user_html, comment_html, answer_html):
        temp = HtmlGenerator.replace_item("#TITLE#", title, html)
        temp = HtmlGenerator.replace_item("#QID#", str(qid), temp)
        temp = HtmlGenerator.replace_item("#QSCORE#", str(qscore), temp)
        temp = HtmlGenerator.replace_item("#POST#", post, temp)
        temp = HtmlGenerator.replace_item("#ANSWERCOUNT#", str(answer_count), temp)
        temp = HtmlGenerator.generate_tags(temp, tag_lst)
        temp = HtmlGenerator.generate_related(temp, rel_dic)
        temp = HtmlGenerator.replace_item("#ASKERINFO#", user_html, temp)
        temp = HtmlGenerator.replace_item("#QCOMMENTS#", comment_html, temp)
        temp = HtmlGenerator.replace_item("#ANSWERS#", answer_html, temp)
        return temp

    @staticmethod
    def generate_tags(html, tag_lst):
        if tag_lst is None:
            return HtmlGenerator.replace_item("#TAGS#", "", html)
        temp = ""
        for tag in tag_lst:
            temp += "<span class=\"post-tag\" rel=\"tag\">" + tag + "</span>\n"
        return HtmlGenerator.replace_item("#TAGS#", temp, html)

    @staticmethod
    def generate_related(html, rel_dic):
        temp = "<h4 id=\"h-linked\">Related Posts<hr></h4>"
        temp += "<div class=\"linked\" data-tracker=\"lq=1\">\n"

        if rel_dic is None or len(rel_dic) == 0:
            temp += "No Related Post Found\n"
        else:
            for item in rel_dic:
                temp += "[" + str(item) + "] " + rel_dic[item] + "\n"
        temp += "</div> <hr>\n"
        return HtmlGenerator.replace_item("#RELATEDS#", temp, html)

    @staticmethod
    def get_badge(type_badge, count_badge, html_str):
        html_str += "<span\" aria-hidden=\"true\">"
        html_str += "<span class=\"badge" + str(type_badge) + "\"> </span>"
        html_str += "<span class=\"badgecount\">" + str(count_badge) + "</span>"
        html_str += "</span><span class=\"v-visible-sr\">" + str(count_badge)
        if type_badge == 1:
            html_str += "gold "
        elif type_badge == 2:
            html_str += "silver "
        else:
            html_str += "bronze "
        html_str += "badges</span>\n"
        return html_str

    @staticmethod
    def generate_user(user_name, post_date, user_reputation, gold_b, silver_b, bronze_b):
        temp = "<div class=\"post-signature owner grid--cell\">\n"
        temp += "<div class=\"user-info\"> \n <div class=\"user-action-time\">"
        temp += "asked <span title=\"" + post_date + "\">" + post_date + "</span>\n</div>"
        temp += "<div class=\"user-details\" itemprop=\"author\" itemscope itemtype=\"http://schema.org/Person\">"
        temp += "<span>" + user_name + "</span>"

        if user_reputation is not None:
            temp += "<div class=\"-flair\">\n"
            rep = str(user_reputation)
            if user_reputation >= 1000:
                user_reputation = round(user_reputation / 1000.0)
                rep = str(user_reputation) + "k"
            if user_reputation == 0:
                rep = ""
            temp += "<span class=\"reputation-score\" dir=\"ltr\">" + rep + "</span><br> </div>\n"
        if gold_b != 0:
            temp = HtmlGenerator.get_badge(1, gold_b, temp)
        if silver_b != 0:
            temp = HtmlGenerator.get_badge(2, silver_b, temp)
        if bronze_b != 0:
            temp = HtmlGenerator.get_badge(3, bronze_b, temp)

        temp += "</div>\n</div></div>\n"
        return temp

    @staticmethod
    def generate_answer_header(is_accepted, answer_id, score):
        result = "<div id=\"answer-" + str(answer_id) + "\" class=\""

        if is_accepted:
            result += "answer accepted-answer\"data-answerid=\"" + str(answer_id) + "\"  itemprop=\"acceptedAnswer\">\n"
        else:
            result += "answer accepted-answer\"data-answerid=\"" + str(answer_id) + "\"  itemprop=\"acceptedAnswer\">\n"

        result += "<div class=\"post-layout\">\n<div class=\"votecell post-layout--left\">\n"
        result += "<div class=\"js-voting-container grid fd-column ai-stretch gs4 fc-black-200\" " \
                  "data-post-id=\"" + str(answer_id) + "\">\n"
        result += "<div class=\"js-vote-count grid--cell fc-black-500 fs-title grid fd-column ai-center\" " \
                  "itemprop=\"upvoteCount\" data-value=\"" + str(score) + "\">" + str(score) + "</div>\n"

        result += "<div class=\"js-accepted-answer-indicator grid--item fc-green-500 ta-center p4 "
        if not is_accepted:
            result += " d-none"
        result += "\" aria-label=\"accepted\">\n"

        result += "<svg aria-hidden=\"true\" class=\"svg-icon iconCheckmarkLg\" width=\"36\" height=\"36\" " \
                  "viewBox=\"0 0 36 36\"><path d=\"M6 14l8 8L30 6v8L14 30l-8-8v-8z\"/></svg>\n"
        result += "</div>\n</div>\n</div>\n"
        return result

    @staticmethod
    def generate_answer(is_accepted, answer_id, score, answer_body, answerer_html, comments_html):
        temp = HtmlGenerator.generate_answer_header(is_accepted, answer_id, score)
        temp += "<div class=\"answercell post-layout--right\">\n<div class=\"post-text\" itemprop=\"text\">\n" + answer_body \
                + "\n </div>"
        temp += "<div class=\"grid mb0 fw-wrap ai-start jc-end gs8 gsy\">"
        temp += answerer_html + "</div>\n</div>\n"
        temp += comments_html + "</div>\n</div>\n"
        return temp

    @staticmethod
    def generate_comments(comment_lst, post_id):
        result = ""
        for tuple_item in comment_lst:
            temp = "<li id=\"comment-" + str(tuple_item[0]) + "\" class=\"comment js-comment \" data-comment-id=\"" + \
                   str(tuple_item[0]) + "\">\n"
            temp += "<div class=\"js-comment-actions comment-actions\">\n"
            temp += " <div class=\"comment-score js-comment-edit-hide\">\n <span class=\"cool\">{0}</span></div>\n</div>" \
                .format(str(tuple_item[1]))
            temp += "<div class=\"comment-text js-comment-text-and-form\">\n<div class=\"comment-body " \
                    "js-comment-edit-hide\">\n "
            temp += "<span class=\"comment-copy\">" + tuple_item[2] + "</span> – "
            temp += "<span class=\"comment-date\" dir=\"ltr\"><span class=\"relativetime-clean\">" + tuple_item[3] + \
                    "</span></span>\n "
            temp += "</div>\n</div></li>\n"
            result += temp
        temp = "<div class=\"post-layout--right\">\n"
        temp += "<div id=\"comments-" + str(
            post_id) + "\" class=\"comments js-comments-container bt bc-black-2 mt12 \" " \
                       "data-post-id=\"" + str(post_id) + "\">\n"
        temp += "<ul class=\"comments-list js-comments-list\">\n"
        temp += result
        temp += "</ul>\n</div>\n</div>\n"
        return temp

    @staticmethod
    def save_html(result_file, html):
        file = open(result_file, "w")
        html = HtmlGenerator.normalize_html_xml(html)
        file.write(html)
        file.close()

    @staticmethod
    def process_user(user, post_date):
        if user is None:
            return HtmlGenerator.generate_user("user id: user", post_date.split("T")[0], 0,
                                               0, 0, 0)
        badges = [0, 0, 0]
        if user.lst_badges is not None:
            for badge in user.lst_badges:
                badges[badge[0] - 1] += 1
        return HtmlGenerator.generate_user("user id:" + str(user.id), post_date.split("T")[0], user.reputation,
                                           badges[0], badges[1],
                                           badges[2])

    @staticmethod
    def process_comments(comments, post_id):
        if comments is None:
            return ""
        comment_lst = []
        for comment in comments:
            comment_lst.append((comment.id, comment.score, comment.text, comment.creation_date.split("T")[0]))
        return HtmlGenerator.generate_comments(comment_lst, post_id)

    @staticmethod
    def process_answers(data_reader, answers, accepted_answer_id):
        temp = ""
        if answers is None:
            return temp
        for answer in answers:
            is_selected = False
            if answer.post_id == accepted_answer_id:
                is_selected = True
            user = None
            if answer.owner_user_id in data_reader.user_parser.map_of_user:
                user = data_reader.user_parser.map_of_user[answer.owner_user_id]
            answer_html = HtmlGenerator.generate_answer(is_selected, answer.post_id, answer.score, answer.body,
                                                        HtmlGenerator.process_user(
                                                            user,
                                                            answer.creation_date),
                                                        HtmlGenerator.process_comments(answer.comments, answer.post_id))
            temp += answer_html
        return temp

    @staticmethod
    def questions_to_html(lst_question_id, data_reader, html_directory):
        for question_id in lst_question_id:
            try:
                html = HtmlGenerator.read_html(template_file)
                question = data_reader.post_parser.map_questions[question_id]
                title = question.title
                post_id = question.post_id
                post_score = question.score
                post_body = question.body
                post_answer_count = question.answer_count
                tag_lst = question.tags
                rel_dic = {}
                if question.related_post is not None:
                    for rel_id in question.related_post:
                        if rel_id[0] not in data_reader.post_parser.map_questions:
                            continue
                        rel_dic[rel_id[0]] = data_reader.post_parser.map_questions[rel_id[0]].title
                questioner = None
                if question.owner_user_id in data_reader.user_parser.map_of_user:
                    questioner = data_reader.user_parser.map_of_user[question.owner_user_id]
                post_date = question.creation_date
                user_html = HtmlGenerator.process_user(questioner, post_date)
                comment_html = HtmlGenerator.process_comments(question.comments, post_id)
                answer_html = HtmlGenerator.process_answers(data_reader, question.answers, question.accepted_answer_id)
                html = HtmlGenerator.generate_post(html, title, post_id, post_score, post_body, post_answer_count,
                                                   tag_lst, rel_dic, user_html, comment_html, answer_html)
                HtmlGenerator.save_html(html_directory+str(question_id)+".html", html)
            except Exception as er:
                print("issue generating html file for query:" + str(question_id))
                print(str(er))
