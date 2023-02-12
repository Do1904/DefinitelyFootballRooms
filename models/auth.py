"""
ログイン関連の処理をここに書く
"""
from gettext import find
from .abstract import AbstractModel

from hashlib import sha256


class AuthModel(AbstractModel):
    """
    ログイン，セッションなどの情報はここに書く
    """

    def __init__(self, config):
        super().__init__(config)

    def login(self, username, password):
        """
        :param username: ログインするユーザのユーザ名
        :param password: ログインするユーザのパスワード
        :return bool:ログインが成功したか
        """
        user = self.find_user_by_name_and_password(username, password)
        # 該当するユーザがいなければFalseを返す
        if not user:
            return False, None
        # TODO: セッションに情報を追加
        return True, user

    def create_user(self, username, password):
        """
        新規ユーザ作成
        :param username: ユーザ名
        :param password: パスワード
        :return:
        """
        hashed_password = self.hash_password(password)
        sql = "INSERT INTO users(username, password) VALUE (%s, %s);"
        self.execute(sql, username, hashed_password)

    def find_user_by_name_and_password(self, username, password):
        """
        ユーザ名とパスワードからユーザを探す
        ユーザが存在しない場合，空の辞書を返す
        :param username: 検索するユーザ名
        :param password: 検索するパスワード
        :return: 検索したユーザ
        """
        hashed_password = self.hash_password(password)
        sql = "SELECT * FROM users where username=%s AND password=%s"
        return self.fetch_one(sql, username, hashed_password)

        

    def find_profile_by_user_id(self, user_name):
        """
        ユーザ名とパスワードからユーザを探す
        ユーザが存在しない場合，空の辞書を返す
        :param username: 検索するユーザ名
        :param password: 検索するパスワード
        :return: 検索したユーザ
        """
        sql = "SELECT * FROM users INNER JOIN profile on users.username = profile.username where profile.username=%s"
        return self.fetch_one(sql, user_name)

    def add_profile_info(self, username):
        sql = "INSERT INTO profile(username) VALUE (%s)"
        self.execute(sql, username)

    def logout(self):
        pass

    def hash_password(self, password: str):
        """
        パスワードを安全に保存するためにハッシュ化する．
        :param password: パスワード
        :return: ハッシュ化されたパスワード
        """
        return sha256(password.encode()).hexdigest()

    def profile_update(self, nickname, yourclub, yourleague, yournation, profile, twitter, instagram, socialmedia, user_name):
        sql = "UPDATE profile SET nickname  = %s, your_club = %s, your_league = %s, your_nation = %s, profile = %s, twitter = %s, instagram = %s, SNS = %s WHERE username = %s;"
        self.execute(sql, nickname, yourclub, yourleague, yournation, profile, twitter, instagram, socialmedia, user_name)

    def find_rooms_by_keyword(self, keyword):
        """
        ユーザ名とパスワードからユーザを探す
        ユーザが存在しない場合，空の辞書を返す
        :param username: 検索するユーザ名
        :param password: 検索するパスワード
        :return: 検索したユーザ
        """
        status = "room"
        args = f'%{keyword}%'
        sql = "SELECT * FROM rooms INNER JOIN users on rooms.created_by = users.username where room_comment LIKE %s"
        return self.fetch_all(sql,args),status

    def find_pubs_by_keyword(self, keyword, findenAus):
        status = "pub"
        sql_id = "SELECT * FROM pubs INNER JOIN profile on pubs.created_by = profile.username where pubs.pub_id LIKE %s"
        sql_name = "SELECT * FROM pubs INNER JOIN profile on pubs.created_by = profile.username where pubs.pub_name LIKE %s"
        sql_comment = "SELECT * FROM pubs INNER JOIN profile on pubs.created_by = profile.username where pubs.pub_comment LIKE %s"
        sql_none = "SELECT * FROM pubs INNER JOIN profile on pubs.created_by = profile.username ORDER BY pubs.created_at DESC LIMIT 200"
        
        if keyword is None:
            return self.fetch_all(sql_none),status
        else:
            args = f'%{keyword}%'
            if findenAus == "id":
                return self.fetch_all(sql_id, args),status
            elif findenAus == "name":
                return self.fetch_all(sql_name, args),status
            elif findenAus == "explanation":
                return self.fetch_all(sql_comment, args),status

    def fetch_all_fans(self):
        sql = "SELECT * FROM users INNER JOIN profile on users.username = profile.username"
        return self.fetch_all(sql)

    def fetch_fans(self, your_club, your_league, your_nation):
        sql = "SELECT * FROM users INNER JOIN profile on users.username = profile.username where profile.your_club = %s"
        sql2 = "SELECT * FROM users INNER JOIN profile on users.username = profile.username where profile.your_league = %s"
        sql3 = "SELECT * FROM users INNER JOIN profile on users.username = profile.username where profile.your_nation = %s"
        return self.fetch_all(sql, your_club), self.fetch_all(sql2, your_league), self.fetch_all(sql3, your_nation)

    def find_users_by_keyword(self, keyword, findenAus):
        status = "user"
        sql_username = "SELECT * FROM users INNER JOIN profile on users.username = profile.username where profile.username LIKE %s ORDER BY users.created_at DESC LIMIT 200"
        sql_nickname = "SELECT * FROM users INNER JOIN profile on users.username = profile.username where profile.nickname LIKE %s ORDER BY users.created_at DESC LIMIT 200"
        sql_profile = "SELECT * FROM users INNER JOIN profile on users.username = profile.username where profile.profile LIKE %s ORDER BY users.created_at DESC LIMIT 200"
        sql_none = "SELECT * FROM users INNER JOIN profile on users.username = profile.username ORDER BY users.created_at DESC LIMIT 200"

        if keyword is None:
            return self.fetch_all(sql_none),status
        else:
            args = f'%{keyword}%'
            if findenAus == "id":
                return self.fetch_all(sql_username, args),status
            elif findenAus == "name":
                return self.fetch_all(sql_nickname, args),status
            elif findenAus == "explanation":
                return self.fetch_all(sql_profile, args),status
            

    def validate_pub(self,community_id) -> bool:
        sql = "SELECT * FROM pubs WHERE pub_id=%s"
        result = self.fetch_all(sql,community_id)
        if len(result) > 0:
            return True
        else:
            return False

    def clubs_list(self):
        sql = "SELECT * FROM clubs"
        return self.fetch_all(sql)

    def leagues_list(self):
        sql = "SELECT * FROM leagues"
        return self.fetch_all(sql)

    def nations_list(self):
        sql = "SELECT * FROM nations"
        return self.fetch_all(sql)


    def create_new_pub(self, community_id, community_name, community_comment, user_name):
        """
        ユーザ名とパスワードからユーザを探す
        ユーザが存在しない場合，空の辞書を返す
        :param username: 検索するユーザ名
        :param password: 検索するパスワード
        :return: 検索したユーザ
        """
        is_exist = self.validate_pub(community_id)
        if is_exist == False:
            sql = "INSERT INTO pubs(pub_id, pub_name, pub_comment, created_by) VALUE (%s, %s, %s, %s);" 
            # ID
            self.execute(sql, community_id, community_name, community_comment, user_name)
            return True
        else:
            return False

    def find_your_following_community(self, user_name):
        sql = "SELECT * FROM followpub INNER JOIN pubs on followpub.pub = pubs.pub_id where followpub.user=%s"
        return self.fetch_all(sql, user_name)

    def find_pub_by_id(self, pub_id):
        sql = "SELECT * FROM pubs where pub_id=%s"
        return self.fetch_one(sql, pub_id)

    def find_pub_by_created_by(self, created_by):
        sql = "SELECT * FROM pubs where created_by=%s"
        return self.fetch_all(sql, created_by)

    # def join_pub_member(self, pub_id, user_name):
    #     sql = "INSERT IGNORE INTO pub_members(pub_id, username) VALUE (%s, %s);" 
    #     self.execute(sql, pub_id, user_name)

    # def find_chat_member_by_pub_id_username(self, pub_id, user_name):
    #     sql = "SELECT * FROM pub_members where pub_id=%s AND username=%s;"
    #     return self.fetch_one(sql, pub_id, user_name)

    # def find_chat_members_by_pub_id(self, pub_id):
    #     sql = "SELECT * FROM pub_members where pub_id=%s"
    #     return self.fetch_all(sql, pub_id)

    def find_discussion_by_pub_id(self, pub_id):
        sql = "SELECT * FROM message INNER JOIN profile on message.username = profile.username where message.pub_id=%s ORDER BY message.created_at DESC"
        return self.fetch_all(sql, pub_id)

    def create_new_discussion(self, pub_id, user_name, status, discuss_title, body):
        sql = "INSERT INTO message(pub_id, username, status, title, body) VALUE (%s, %s, %s, %s, %s);"
        self.execute(sql, pub_id, user_name, status, discuss_title, body)

    def find_other_users_by_username(self, username):
        sql = "SELECT * FROM users INNER JOIN profile on users.username = profile.username where profile.username=%s"
        return self.fetch_one(sql, username)


    def find_discussion_by_title(self, pub_id, keyword):
        if keyword is None:
            sql = "SELECT * FROM message INNER JOIN profile on message.username = profile.username where message.pub_id = %s ORDER BY message.created_at DESC LIMIT 200"
            return self.fetch_all(sql, pub_id)
        else:
            args = f'%{keyword}%'
            sql = "SELECT * FROM message INNER JOIN profile on message.username = profile.username where message.pub_id = %s AND message.title like %s ORDER BY message.created_at DESC LIMIT 200"
            return self.fetch_all(sql, pub_id, args)
        

    def find_discussion_by_keyword(self, pub_id, keyword):
        if keyword is None:
            sql = "SELECT * FROM message INNER JOIN profile on message.username = profile.username where message.pub_id = %s ORDER BY message.created_at DESC LIMIT 200"
            return self.fetch_all(sql, pub_id)
        else:
            args = f'%{keyword}%'
            sql = "SELECT * FROM message INNER JOIN profile on message.username = profile.username where message.pub_id = %s AND message.body like %s ORDER BY message.created_at DESC LIMIT 200"
            return self.fetch_all(sql, pub_id, args)
        

    def find_discussion_by_username(self, pub_id, keyword):
        if keyword is None:
            sql = "SELECT * FROM message INNER JOIN profile on message.username = profile.username where message.pub_id = %s ORDER BY message.created_at DESC LIMIT 200"
            return self.fetch_all(sql, pub_id)
        else:
            args = f'%{keyword}%'
            sql = "SELECT * FROM message INNER JOIN profile on message.username = profile.username where message.pub_id = %s AND profile.nickname like %s ORDER BY message.created_at DESC LIMIT 200"
            return self.fetch_all(sql, pub_id, args)

    def find_discussion_by_id(self, id):
        sql = "SELECT * FROM message INNER JOIN profile on message.username = profile.username where message.id=%s"
        return self.fetch_one(sql, id)

    def find_discussion_comment_by_id(self, id):
        sql = "SELECT * FROM discuss_comments INNER JOIN profile on discuss_comments.username = profile.username where discuss_comments.id=%s"
        return self.fetch_one(sql, id)

    def fetch_discussion_commnets_by_id(self, id):
        sql = "SELECT * FROM discuss_comments INNER JOIN profile on discuss_comments.username = profile.username where discuss_comments.message_id=%s"
        return self.fetch_all(sql, id)

    def pub_member_by_id(self, pub_id):
        sql = "SELECT * FROM followpub INNER JOIN profile on followpub.user = profile.username where followpub.pub = %s"
        return self.fetch_all(sql, pub_id)

    def fetch_discussion_commnet_comments_by_id(self, commeid):
        sql = "SELECT * FROM discuss_comment_comments INNER JOIN profile on discuss_comment_comments.username = profile.username where discuss_comment_comments.discussion_id=%s"
        return self.fetch_all(sql, commeid)

    def post_discussion_comment(self, user_name, topic_id, body):
        sql = "INSERT INTO discuss_comments(username, message_id, context) VALUE (%s, %s, %s);"
        self.execute(sql, user_name, topic_id, body)

    def update_discussion_page(self, status, title, body, discussion_id):
        sql = "UPDATE message SET status = %s, title = %s, body = %s WHERE id = %s;"
        self.execute(sql, status, title, body, discussion_id)

    def update_discussion_comment_page(self, context, discussion_comment_id):
        sql = "UPDATE discuss_comments SET context = %s WHERE id = %s;"
        self.execute(sql, context, discussion_comment_id)

    def post_discussion_comment_comment(self, user_name, comment_id, body):
        sql = "INSERT INTO discuss_comment_comments(username, discussion_comment_id, context) VALUE (%s, %s, %s);"
        self.execute(sql, user_name, comment_id, body)

    def follow_user(self, username, user_name, follow_id):
        sql = "INSERT IGNORE INTO follow(to_user_id, from_user_id, id) VALUE (%s, %s, %s);"
        self.execute(sql, username, user_name, follow_id)

    def unfollow_user(self, username, user_name):
        sql = "DELETE FROM follow WHERE to_user_id = %s AND from_user_id = %s"
        self.execute(sql, username, user_name)

    def get_followings(self, username):
        sql = "SELECT * FROM follow WHERE from_user_id = %s"
        return self.fetch_all(sql, username)

    def get_followers(self, username):
        sql = "SELECT * FROM follow WHERE to_user_id = %s"
        return self.fetch_all(sql, username)

    def detect_follow(self, follow_id):
        sql = "SELECT * FROM follow WHERE id = %s"
        return self.fetch_all(sql, follow_id)


    def follow_pub(self, pub_id, user_name, follow_id):
        sql = "INSERT IGNORE INTO followpub(pub, user, id) VALUE (%s, %s, %s);"
        self.execute(sql, pub_id, user_name, follow_id)

    def unfollow_pub(self, pub_id, user_name):
        sql = "DELETE FROM followpub WHERE pub = %s AND user = %s"
        self.execute(sql, pub_id, user_name)

    def get_pub_followings(self, username):
        sql = "SELECT * FROM followpub WHERE user = %s"
        return self.fetch_all(sql, username)

    def get_pub_followers(self, pub_id):
        sql = "SELECT * FROM followpub WHERE pub = %s"
        return self.fetch_all(sql, pub_id)

    def detect_pub_follow(self, follow_id):
        sql = "SELECT * FROM followpub WHERE id = %s"
        return self.fetch_all(sql, follow_id)

    # def pub_update(self, pub_name, pub_comment, pub_id):
    #     sql = "UPDATE pubs SET pub_name = %s, pub_comment = %s WHERE pubs.pub_id = %s;"
    #     self.execute(sql, pub_name, pub_comment, pub_id)



    
