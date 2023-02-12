"""
記事モデル
"""
from app.models.abstract import AbstractModel


class ArticleModel(AbstractModel):
    def __init__(self, config):
        super(ArticleModel, self).__init__(config)

    def fetch_recent_articles(self, limit=200):
        """
        最新の記事を取得する．デフォルトでは最新5件まで
        :param limit: 取得する記事の数
        :return:
        """
        sql = "SELECT * FROM articles INNER JOIN profile on articles.username = profile.username ORDER BY articles.created_at DESC LIMIT %s"
        return self.fetch_all(sql, limit)

    def fetch_article_by_id(self, article_id):
        """
        指定されたIDの記事を取得
        :param article_id: 取得したい記事のID
        :return: 指定された記事のID
        """
        sql = "SELECT * FROM articles INNER JOIN profile on articles.username = profile.username WHERE articles.id=%s"
        return self.fetch_one(sql, article_id)

    def fetch_comment_by_id(self, article_id):
        """
        指定されたIDの記事を取得
        :param article_id: 取得したい記事のID
        :return: 指定された記事のID
        """
        sql = "SELECT * FROM comments INNER JOIN profile on comments.username = profile.username WHERE comments.article_id=%s ORDER BY comments.created_at DESC"
        return self.fetch_all(sql, article_id)

    def fetch_article_by_username(self, username):
        """
        指定されたIDの記事を取得
        :param article_id: 取得したい記事のID
        :return: 指定された記事のID
        """
        sql = "SELECT * FROM articles INNER JOIN profile on articles.username = profile.username WHERE articles.username=%s ORDER BY articles.created_at DESC"
        return self.fetch_all(sql, username)

    def create_article(self, user_name, title, body):
        """
        新しく記事を作成する
        :param user_name: 投稿したユーザのusername
        :param title: 記事のタイトル
        :param body: 記事の本文
        :return: None
        """
        sql = "INSERT INTO articles(username, title, body) VALUE (%s, %s, %s);"
        self.execute(sql, user_name, title, body)

    def update_article(self, title, body, article_id):
        """
        新しく記事を作成する
        :param user_name: 投稿したユーザのusername
        :param title: 記事のタイトル
        :param body: 記事の本文
        :return: None
        """
        sql = "UPDATE articles SET title = %s, body = %s WHERE id = %s;"
        self.execute(sql, title, body, article_id)

    def destory_article(self, article_id):
        sql = "DELETE from articles where id = %s;"
        self.execute(sql, article_id)

    def find_article_by_title(self, keyword):
        if keyword is None:
            sql = "SELECT * FROM articles INNER JOIN profile on articles.username = profile.username ORDER BY articles.created_at DESC LIMIT 200"
            return self.fetch_all(sql)
        else:
            args = f'%{keyword}%'
            sql = "SELECT * FROM articles INNER JOIN profile on articles.username = profile.username where articles.title like %s ORDER BY articles.created_at DESC LIMIT 200"
            return self.fetch_all(sql, args)
        

    def find_article_by_keyword(self, keyword):
        if keyword is None:
            sql = "SELECT * FROM articles INNER JOIN profile on articles.username = profile.username ORDER BY articles.created_at DESC LIMIT 200"
            return self.fetch_all(sql)
        else:
            args = f'%{keyword}%'
            sql = "SELECT * FROM articles INNER JOIN profile on articles.username = profile.username where articles.body like %s ORDER BY articles.created_at DESC LIMIT 200"
            return self.fetch_all(sql, args)

    def find_article_by_username(self, keyword):
        if keyword is None:
            sql = "SELECT * FROM articles INNER JOIN profile on articles.username = profile.username ORDER BY articles.created_at DESC LIMIT 200"
            return self.fetch_all(sql)
        else:
            args = f'%{keyword}%'
            sql = "SELECT * FROM articles INNER JOIN profile on articles.username = profile.username where profile.nickname like %s ORDER BY articles.created_at DESC LIMIT 200"
            return self.fetch_all(sql, args)

    def post_new_comment(self, user_name, article_id, body):
        sql = "INSERT INTO comments(username, article_id, comment) VALUE (%s, %s, %s);"
        self.execute(sql, user_name, article_id, body)

    
