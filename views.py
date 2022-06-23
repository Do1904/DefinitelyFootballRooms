from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from fastapi.staticfiles import StaticFiles
from app.configs import Config
from app.utilities.session import Session
from app.models.auth import AuthModel
from app.models.articles import ArticleModel
from app.utilities.check_login import check_login

app = FastAPI()
app.mount("/app/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="/app/templates")
config = Config()
session = Session(config)



@app.get("/")
def index(request: Request):
    """
    トップページを返す
    :param request: Request object
    :return:
    """
    return templates.TemplateResponse("index.html", {"request": request})


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
    response = RedirectResponse("/articles", status_code=HTTP_302_FOUND)
    session_id = session.set("user", user)
    response.set_cookie("session_id", session_id)
    return response


@app.post("/register")
def create_user(username: str = Form(...), password: str = Form(...)):
    """
    ユーザ登録をおこなう
    フォームから入力を受け取る時は，`username=Form(...)`のように書くことで受け取れる
    :param username: 登録するユーザ名
    :param password: 登録するパスワード
    :return: 登録が完了したら/blogへリダイレクト
    """
    auth_model = AuthModel(config)
    auth_model.create_user(username, password)
    user = auth_model.find_user_by_name_and_password(username, password)
    response = RedirectResponse(url="/articles", status_code=HTTP_302_FOUND)
    session_id = session.set("user", user)
    response.set_cookie("session_id", session_id)
    return response

@app.get("/profile_update")
@check_login
def profile_update_page(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

@app.post("/profile_update")
@check_login
def profile_update(yourclub: str = Form(...), yourleague: str = Form(...), yournation: str = Form(...), profile: str = Form(...), session_id=Cookie(default=None)):
    user_id = session.get(session_id).get("user").get("id")
    auth_model = AuthModel(config) # auth.pyを使うために必要
    auth_model.profile_update(yourclub, yourleague, yournation, profile, user_id) # auth.pyの中にある関数を使うために必要
    return RedirectResponse("/articles", status_code=HTTP_302_FOUND)


@app.get("/articles")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def articles_index(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    auth_model = AuthModel(config)
    # user_profile = auth_model.find_profile_by_user_id(user["id"])
    article_model = ArticleModel(config)
    articles = article_model.fetch_recent_articles()
    return templates.TemplateResponse("article-index.html", {
        "request": request,
        "articles": articles,
        "user": user,
    })


@app.get("/article/create")
@check_login
def create_article_page(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("create-article.html", {"request": request, "user": user})


@app.post("/article/create")
@check_login
def post_article(title: str = Form(...), body: str = Form(...), session_id=Cookie(default=None)):
    article_model = ArticleModel(config)
    user_id = session.get(session_id).get("user").get("id")
    article_model.create_article(user_id, title, body)
    return RedirectResponse("/articles", status_code=HTTP_302_FOUND)


@app.get("/article/{article_id}")
@check_login
def article_detail_page(request: Request, article_id: int, session_id=Cookie(default=None)):
    article_model = ArticleModel(config)
    article = article_model.fetch_article_by_id(article_id)
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("article-detail.html", {
        "request": request,
        "article": article,
        "user": user
    })

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
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("community.html", {"request": request, "user": user})

@app.post("/community")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def pubs_finden(request: Request, keyword: str = Form(...), search_from: str = Form(...), session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    auth_model = AuthModel(config)
    if search_from == "Rooms":
        search_list = auth_model.find_rooms_by_keyword(keyword)
        found_id = "room_id"
        found_name = "room_name"
        found_comment = "room_comment"
    elif search_from == "Pubs":
        search_list = auth_model.find_pubs_by_keyword(keyword)
        found_id = "pub_id"
        found_name = "pub_name"
        found_comment = "pub_comment"
    elif search_from == "Users":
        search_list = auth_model.find_users_by_keyword(keyword)
        found_id = "id"
        found_name = "username"
        found_comment = "profile"
    return templates.TemplateResponse("community.html", {
        "request": request,
        "search_list": search_list,
        "user": user,
        "found_id":found_id,
        "found_name": found_name,
        "found_comment": found_comment
    })

@app.get("/new_community")
@check_login
def create_community(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("create-community.html", {"request": request, "user": user})

@app.post("/new_community")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def create_pub(request: Request, community_name: str = Form(...), community_comment: str = Form(...), community_id: str = Form(...), session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    user_name = session.get(session_id).get("user").get("username")
    auth_model = AuthModel(config)
    new_community = auth_model.create_new_pub(community_id, community_name, community_comment, user_name)
    return RedirectResponse("/community", status_code=HTTP_302_FOUND)

@app.get("/see_community")
@check_login
def your_community(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("your-community.html", {"request": request, "user": user})
