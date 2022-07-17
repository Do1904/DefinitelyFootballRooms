"""
ログイン関連の処理をここに書く
"""
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

    def create_user(self, username, nickname, password):
        """
        新規ユーザ作成
        :param username: ユーザ名
        :param password: パスワード
        :return:
        """
        hashed_password = self.hash_password(password)
        sql = "INSERT INTO users(username, nickname, password) VALUE (%s, %s, %s);"
        self.execute(sql, username, nickname, hashed_password)

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

    # def find_profile_by_user_id(self, user_id):
    #     """
    #     ユーザ名とパスワードからユーザを探す
    #     ユーザが存在しない場合，空の辞書を返す
    #     :param username: 検索するユーザ名
    #     :param password: 検索するパスワード
    #     :return: 検索したユーザ
    #     """
    #     sql = "SELECT * FROM profile where user_id=%s"
    #     return self.fetch_one(sql, user_id)

    def logout(self):
        pass

    def hash_password(self, password: str):
        """
        パスワードを安全に保存するためにハッシュ化する．
        :param password: パスワード
        :return: ハッシュ化されたパスワード
        """
        return sha256(password.encode()).hexdigest()

    def profile_update(self, nickname, yourclub, yourleague, yournation, profile, user_name):
        sql = "UPDATE users SET nickname  = %s, your_club = %s, your_league = %s, your_nation = %s, profile = %s WHERE users.username = %s;"
        self.execute(sql, nickname, yourclub, yourleague, yournation, profile, user_name)

    def find_rooms_by_keyword(self, keyword):
        """
        ユーザ名とパスワードからユーザを探す
        ユーザが存在しない場合，空の辞書を返す
        :param username: 検索するユーザ名
        :param password: 検索するパスワード
        :return: 検索したユーザ
        """
        args = f'%{keyword}%'
        sql = "SELECT * FROM rooms INNER JOIN users on rooms.created_by = users.username where room_comment LIKE %s"
        return self.fetch_all(sql,args)

    def find_pubs_by_keyword(self, keyword):
        """
        ユーザ名とパスワードからユーザを探す
        ユーザが存在しない場合，空の辞書を返す
        :param username: 検索するユーザ名
        :param password: 検索するパスワード
        :return: 検索したユーザ
        """
        args = f'%{keyword}%'
        sql = "SELECT * FROM pubs INNER JOIN users on pubs.created_by = users.username where pub_comment LIKE %s"
        return self.fetch_all(sql, args)

    def find_users_by_keyword(self, keyword):
        """
        ユーザ名とパスワードからユーザを探す
        ユーザが存在しない場合，空の辞書を返す
        :param username: 検索するユーザ名
        :param password: 検索するパスワード
        :return: 検索したユーザ
        """
        args = f'%{keyword}%'
        sql = "SELECT * FROM users where profile LIKE %s"
        return self.fetch_all(sql, args)

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

    def find_your_community_by_user_name(self, user_name):
        sql = "SELECT * FROM pub_members INNER JOIN pubs on pub_members.pub_id = pubs.pub_id where username=%s"
        return self.fetch_all(sql, user_name)

    def find_pub_by_id(self, pub_id):
        sql = "SELECT * FROM pubs where pub_id=%s"
        return self.fetch_one(sql, pub_id)

    def find_pub_by_created_by(self, created_by):
        sql = "SELECT * FROM pubs where created_by=%s"
        return self.fetch_all(sql, created_by)

    def join_chat_member(self, pub_id, user_name):
        sql = "INSERT IGNORE INTO pub_members(pub_id, username) VALUE (%s, %s);" 
        self.execute(sql, pub_id, user_name)

    def find_chat_member_by_pub_id_username(self, pub_id, user_name):
        sql = "SELECT * FROM pub_members where pub_id=%s AND username=%s;"
        return self.fetch_one(sql, pub_id, user_name)

    def find_chat_members_by_pub_id(self, pub_id):
        sql = "SELECT * FROM pub_members where pub_id=%s"
        return self.fetch_all(sql, pub_id)

    def find_chats_by_pub_id(self, pub_id):
        sql = "SELECT * FROM message where pub_id=%s ORDER BY created_at DESC"
        return self.fetch_all(sql, pub_id)

    def send_message(self, pub_id, user_name, context):
        sql = "INSERT INTO message(pub_id, username, context) VALUE (%s, %s, %s);"
        self.execute(sql, pub_id, user_name, context)

    def find_other_users_by_username(self, username):
        sql = "SELECT * FROM users where username=%s"
        return self.fetch_one(sql, username)

    # def pub_update(self, pub_name, pub_comment, pub_id):
    #     sql = "UPDATE pubs SET pub_name = %s, pub_comment = %s WHERE pubs.pub_id = %s;"
    #     self.execute(sql, pub_name, pub_comment, pub_id)



    
