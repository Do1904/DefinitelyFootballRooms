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

    def profile_update(self, yourclub, yourleague, yournation, profile, user_id):
        sql = "UPDATE users SET your_club = %s, your_league = %s, your_nation = %s, profile = %s WHERE users.id = %s;"
        self.execute(sql, yourclub, yourleague, yournation, profile, user_id)

    def find_rooms_by_keyword(self, keyword):
        """
        ユーザ名とパスワードからユーザを探す
        ユーザが存在しない場合，空の辞書を返す
        :param username: 検索するユーザ名
        :param password: 検索するパスワード
        :return: 検索したユーザ
        """
        args = f'%{keyword}%'
        sql = "SELECT * FROM rooms where room_comment LIKE %s"
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
        sql = "SELECT * FROM pubs where pub_comment LIKE %s"
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
        sql = "SELECT * FROM pubs where created_by=%s ORDER BY created_at DESC"
        return self.fetch_all(sql, user_name)

    def find_pub_by_id(self, pub_id):
        sql = "SELECT * FROM pubs where pub_id=%s"
        return self.fetch_one(sql, pub_id)

    
