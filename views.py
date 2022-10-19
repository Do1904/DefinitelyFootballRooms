from typing import List, Optional
from fastapi import FastAPI, Request, Form, Cookie, WebSocket, WebSocketDisconnect 
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from fastapi.staticfiles import StaticFiles
from app.configs import Config
from app.utilities.session import Session
from app.models.auth import AuthModel
from app.models.articles import ArticleModel
from app.utilities.check_login import check_login
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.mount("/app/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="/app/templates")
config = Config()
session = Session(config)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

active_ws_connections: List[WebSocket] = []

@app.websocket("/chaaaaaat")
async def chat(websocket: WebSocket, nickname: Optional[str] = None):
    # 接続を受け取る
    await websocket.accept()
    # 接続中のclientを保持
    active_ws_connections.append(websocket)

    # クエリーの中のnicknameを取得
    # ない場合はunknown_{ipアドレス}にする
    if nickname is None:
        nickname = f'unknown_{websocket.client.host}'

    try:
        while True:
            # メッセージが送られるのを待つ
            # 形は{ "message": "contents" }
            data = await websocket.receive_json()
            # 受け取ったメッセージにnicknameを付与
            data['nickname'] = nickname
            # 全てのclientに送信
            # 形は{ "nickname": "nickname",　"message": "contents" }
            for connection in active_ws_connections:
                await connection.send_json(data)
    except WebSocketDisconnect:
        # 接続を切断された場合WebSocketDisconnectと言うエラーを吐くので
        # それを捕捉して接続リストから該当のもの削除する
        active_ws_connections.remove(websocket)





@app.get("/")
def index(request: Request):
    """
    トップページを返す
    :param request: Request object
    :return:
    """
    return templates.TemplateResponse("introduction.html", {"request": request})

@app.get("/signin")
def signin(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/introduction")
def introduce(request: Request):
    """
    新規登録ページ
    :param request:
    :return:
    """
    return templates.TemplateResponse("introduction.html", {"request": request})

@app.get("/register")
def register(request: Request):
    """
    新規登録ページ
    :param request:
    :return:
    """
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    ログイン処理
    :param request:
    :param username:
    :param password:
    :return:
    """
    auth_model = AuthModel(config)
    [result, user] = auth_model.login(username, password)
    if not result:
        # ユーザが存在しなければトップページへ戻す
        return templates.TemplateResponse("index.html", {"request": request, "error": "ユーザ名またはパスワードが間違っています"})
    response = RedirectResponse("/FooTTownTop", status_code=HTTP_302_FOUND)
    session_id = session.set("user", user)
    response.set_cookie("session_id", session_id)
    return response


@app.post("/register")
def create_user(username: str = Form(...), password: str = Form(...)):
    """
    ユーザ登録をおこなう
    フォームから入力を受け取る時は，`username=Form(...)`のように書くことで受け取れる
    :param username: 登録するユーザ名
    :param nickname: 登録するサイトでの表示名
    :param password: 登録するパスワード
    :return: 登録が完了したら/blogへリダイレクト
    """
    auth_model = AuthModel(config)
    auth_model.create_user(username, password)
    user = auth_model.find_user_by_name_and_password(username, password)
    auth_model.add_profile_info(username)
    response = RedirectResponse(url="/articles", status_code=HTTP_302_FOUND)
    session_id = session.set("user", user)
    response.set_cookie("session_id", session_id)
    return response

@app.get("/FooTTownTop")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def top(request: Request, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    return templates.TemplateResponse("top.html", {
        "request": request,
        "user": user,
    })

@app.get("/profile_update")
@check_login
def profile_update_page(request: Request, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    clubs = auth_model.clubs_list()
    leagues = auth_model.leagues_list()
    nations = auth_model.nations_list()
    return templates.TemplateResponse("profile.html", {
        "request": request, 
        "user": user,
        "clubs": clubs,
        "leagues": leagues,
        "nations": nations
    })

@app.post("/profile_update")
@check_login
def profile_update(nickname: str = Form(...), twitter: str = Form(...), instagram: str = Form(...), socialmedia: str = Form(...), yourclub: str = Form(...), yourleague: str = Form(...), yournation: str = Form(...), profile: str = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config) # auth.pyを使うために必要
    auth_model.profile_update(nickname, yourclub, yourleague, yournation, profile, twitter, instagram, socialmedia, user_name) # auth.pyの中にある関数を使うために必要
    return RedirectResponse("/user/%s" % (user_name), status_code=HTTP_302_FOUND)

@app.get("/matching")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def user_finden(request: Request, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    your_club = user["your_club"]
    your_league = user["your_league"]
    your_nation = user["your_nation"]
    auth_model = AuthModel(config)
    users = auth_model.fetch_all_fans()
    [clubfan, leaguefan, nationfan] = auth_model.fetch_fans(your_club, your_league, your_nation)
    return templates.TemplateResponse("matching.html", {
        "request": request,
        "users": users,
        "user": user,
        "clubfan": clubfan,
        "leaguefan": leaguefan,
        "nationfan": nationfan
    })


@app.get("/articles")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def articles_index(request: Request, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    article_model = ArticleModel(config)
    articles = article_model.fetch_recent_articles()
    return templates.TemplateResponse("article-index.html", {
        "request": request,
        "articles": articles,
        "user": user,
    })

@app.post("/articles")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def articles_finden(request: Request, keyword: str = Form(...), search_by: str = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    article_model = ArticleModel(config)
    if search_by == "titles":
        articles = article_model.find_article_by_title(keyword)
    elif search_by == "words":
        articles = article_model.find_article_by_keyword(keyword)
    elif search_by == "users":
        articles = article_model.find_article_by_username(keyword)
    return templates.TemplateResponse("article-index.html", {
        "request": request,
        "articles": articles,
        "user": user,
    })


@app.get("/article/create")
@check_login
def create_article_page(request: Request, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    return templates.TemplateResponse("create-article.html", {"request": request, "user": user})


@app.post("/article/create")
@check_login
def post_article(title: str = Form(...), body: str = Form(...), session_id=Cookie(default=None)):
    article_model = ArticleModel(config)
    user_name = session.get(session_id).get("user").get("username")
    article_model.create_article(user_name, title, body)
    return RedirectResponse("/articles", status_code=HTTP_302_FOUND)


@app.get("/article/{article_id}")
@check_login
def article_detail_page(request: Request, article_id: int, session_id=Cookie(default=None)):
    article_model = ArticleModel(config)
    article = article_model.fetch_article_by_id(article_id)
    comments = article_model.fetch_comment_by_id(article_id)
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    return templates.TemplateResponse("article-detail.html", {
        "request": request,
        "article": article,
        "comments": comments,
        "user": user
    })

@app.get("/article/{article_id}/comment")
@check_login
def comment_page(request: Request, article_id: int, session_id=Cookie(default=None)):
    article_model = ArticleModel(config)
    article = article_model.fetch_article_by_id(article_id)
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    return templates.TemplateResponse("comment.html", {
        "request": request,
        "article": article,
        "user": user
    })

@app.post("/article/comment")
@check_login
def post_comment(body: str = Form(...), article_id: int = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    article_model = ArticleModel(config)
    article_model.post_new_comment(user_name, article_id, body)
    return RedirectResponse("/article/%s" % (article_id), status_code=HTTP_302_FOUND)

@app.get("/logout")
@check_login
def logout(session_id=Cookie(default=None)):
    session.destroy(session_id)
    response = RedirectResponse(url="/")
    response.delete_cookie("session_id")
    return response

@app.get("/community")
@check_login
def find_community(request: Request, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    return templates.TemplateResponse("community.html", {"request": request, "user": user})





@app.post("/community")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def pubs_finden(request: Request, keyword: str = Form(...), search_from: str = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    if search_from == "Rooms":
        [search_list, status] = auth_model.find_rooms_by_keyword(keyword)
        return templates.TemplateResponse("community.html", {
        "request": request,
        "search_list": search_list,
        "user": user,
        "status": status
        })
    elif search_from == "Pubs":
        [search_list, status] = auth_model.find_pubs_by_keyword(keyword)
        return templates.TemplateResponse("community.html", {
        "request": request,
        "search_list": search_list,
        "user": user,
        "status": status
        })
    elif search_from == "Users":
        [search_list, status] = auth_model.find_users_by_keyword(keyword)
        return templates.TemplateResponse("community.html", {
        "request": request,
        "search_list": search_list,
        "user": user,
        "status": status
        })


@app.get("/new_community")
@check_login
def create_community(request: Request, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    return templates.TemplateResponse("create-community.html", {"request": request, "user": user})

@app.post("/new_community")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def create_pub(community_name: str = Form(...), community_comment: str = Form(...), community_id: str = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    auth_model.create_new_pub(community_id, community_name, community_comment, user_name)
    pub_id = community_id
    return RedirectResponse("/your_community", status_code=HTTP_302_FOUND)

@app.get("/your_community")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def show_community_list(request: Request, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    your_community = auth_model.find_your_following_community(user_name)
    return templates.TemplateResponse("your-community.html", {
        "request": request,
        "your_community": your_community,
        "user": user
    })


@app.get("/your_community/{pub_id}")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def go_pub_home(request: Request, pub_id: str, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    pub = auth_model.find_pub_by_id(pub_id)
    # response = RedirectResponse(url="/articles", status_code=HTTP_302_FOUND)
    # session_id = session.set("user", user)
    # response.set_cookie("session_id", session_id)
    return templates.TemplateResponse("pub-home.html", {
        "request": request,
        "user": user,
        "pub": pub
    })

    
@app.get("/community/{pub_id}")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def pub_detail_page(request: Request, pub_id: str, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    pub = auth_model.find_pub_by_id(pub_id)
    followers = auth_model.get_pub_followers(pub_id)
    follow_id = user_name + "--" + pub_id
    follow_or_not = auth_model.detect_pub_follow(follow_id)
    return templates.TemplateResponse("pub-home.html", {
        "request": request,
        "user": user,
        "pub": pub,
        "follower": followers,
        "follow_or_not": follow_or_not
    })

@app.get("/community/{pub_id}/discuss")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def go_pub_discussion(request: Request, pub_id: str, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    pub = auth_model.find_pub_by_id(pub_id)
    topics = auth_model.find_discussion_by_pub_id(pub_id)
    return templates.TemplateResponse("pub-discuss.html", {
        "user": user,
        "request": request,
        "pub": pub,
        "topics": topics
    })

@app.get("/community/{pub_id}/newdiscussion")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def create_new_discussion(request: Request, pub_id: str, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    pub = auth_model.find_pub_by_id(pub_id)
    return templates.TemplateResponse("discuss.html", {
        "user": user,
        "request": request,
        "pub": pub
    })

@app.post("/community/newdiscussion")
@check_login
def create_discussion(pub_id: str = Form(...), status: str = Form(...), discuss_title: str = Form(...), body: str = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    auth_model.create_new_discussion(pub_id, user_name, status, discuss_title, body)
    return RedirectResponse("/community/%s/discuss" % (pub_id), status_code=HTTP_302_FOUND)

@app.post("/search_discussion")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def discussion_finden(request: Request, keyword: str = Form(...), search_by: str = Form(...), pub_id: str = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    pub = auth_model.find_pub_by_id(pub_id)
    if search_by == "titles":
        topics = auth_model.find_discussion_by_title(pub_id, keyword)
    elif search_by == "words":
        topics = auth_model.find_discussion_by_keyword(pub_id, keyword)
    elif search_by == "users":
        topics = auth_model.find_discussion_by_username(pub_id, keyword)
    return templates.TemplateResponse("pub-discuss.html", {
        "user": user,
        "request": request,
        "pub": pub,
        "topics": topics
    })

@app.get("/community/discussion/{id}")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def discussion_detail_page(request: Request, id: int, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    topic = auth_model.find_discussion_by_id(id)
    comments = auth_model.fetch_discussion_commnets_by_id(id)
    pub = auth_model.find_pub_by_id(topic["pub_id"])
    return templates.TemplateResponse("discussion-detail.html", {
        "request": request,
        "user": user,
        "topic": topic,
        "comments": comments,
        "pub": pub
    })

@app.get("/discussioncomment/{id}")
@check_login
def post_discuss_comment(request: Request, id: int, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    topic = auth_model.find_discussion_by_id(id)
    return templates.TemplateResponse("discuss-comment.html", {
        "request": request,
        "topic": topic,
        "user": user
    })

@app.post("/discussion/comment")
@check_login
def post_comment(body: str = Form(...), topic_id: int = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    auth_model.post_discussion_comment(user_name, topic_id, body)
    return RedirectResponse("/community/discussion/%s" % (topic_id), status_code=HTTP_302_FOUND)

@app.get("/discussioncomment/{comment_id}/comment")
@check_login
def post_discussion_comment_comment_page(request: Request, comment_id: int, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    topic = auth_model.find_discussion_comment_by_id(comment_id)
    return templates.TemplateResponse("discuss-comment-comment.html", {
        "request": request,
        "topic": topic,
        "user": user
    })

@app.post("/discussion/comment/comment")
@check_login
def post_comment(body: str = Form(...), message_id: int = Form(...), comment_id: int = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    auth_model.post_discussion_comment_comment(user_name, comment_id, body)
    return RedirectResponse("/community/discussion/%s" % (message_id), status_code=HTTP_302_FOUND)




@app.get("/user/{username}")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def user_detail_page(request: Request, username: str, session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    user = auth_model.find_profile_by_user_id(user_name)
    article_model = ArticleModel(config)
    other_user = auth_model.find_other_users_by_username(username)
    articles = article_model.fetch_article_by_username(username)
    created_by = username
    pubs = auth_model.find_pub_by_created_by(created_by)
    followings = auth_model.get_followings(username)
    followers = auth_model.get_followers(username)
    follow_id = user_name + "--" + username
    follow_or_not = auth_model.detect_follow(follow_id)
    return templates.TemplateResponse("user-home.html", {
        "request": request,
        "user": user,
        "other_user": other_user,
        "articles": articles,
        "pubs": pubs,
        "following": followings,
        "follower": followers,
        "follow_or_not": follow_or_not
    })

@app.post("/follow")
@check_login
def follow_user(username: str = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    follow_id = user_name + "--" + username
    auth_model = AuthModel(config)
    auth_model.follow_user(username, user_name, follow_id)
    return RedirectResponse("/user/%s" % (username), status_code=HTTP_302_FOUND)

@app.post("/unfollow")
@check_login
def unfollow_user(username: str = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    auth_model.unfollow_user(username, user_name)
    return RedirectResponse("/user/%s" % (username), status_code=HTTP_302_FOUND)

@app.post("/followpub")
@check_login
def follow_user(pub_id: str = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    follow_id = user_name + "--" + pub_id
    auth_model = AuthModel(config)
    auth_model.follow_pub(pub_id, user_name, follow_id)
    return RedirectResponse("/community/%s" % (pub_id), status_code=HTTP_302_FOUND)

@app.post("/unfollowpub")
@check_login
def unfollow_user(pub_id: str = Form(...), session_id=Cookie(default=None)):
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    auth_model.unfollow_pub(pub_id, user_name)
    return RedirectResponse("/community/%s" % (pub_id), status_code=HTTP_302_FOUND)









