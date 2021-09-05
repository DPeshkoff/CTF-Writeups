from flask import Flask, session, redirect
import datetime
from flask import render_template, send_from_directory, request, abort
from functools import wraps
import requests
import sms
import re

from flask_apscheduler import APScheduler

app = Flask(__name__, static_url_path='/static/')

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
import db_functions

db = db_functions.Database()

db.ShopItem().add_number(number='+7777-(777)-777777', amount=9999, price=999999)

# Sessions
app.permanent_session_lifetime = datetime.timedelta(days=365)
app.secret_key = 'seirjtxdlreirughsoeiughseorgusherg'
app.config['SESSION_TYPE'] = 'filesystem'


class add_money_to_login_obj:

    def __init__(self, login, money):
        db.User().add_money_to_login(login,money)


# update shop
def shop_info_update():
    db.ShopItem().update_shop()


scheduler = APScheduler()
scheduler.add_job(id='Scheduled Task', func=shop_info_update, trigger="interval", seconds=1)
scheduler.start()


def require_authorization(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if 'user_id' in session and session['user_id']:
            user_obj = db.User().get_user_by_id(session['user_id'])
            if user_obj:
                kwargs['current_user'] = user_obj
                return fn(*args, **kwargs)

        return redirect('/login/')

    return decorated_view


@app.route('/<path:path>')
def send_js(path):
    # return send_from_directory('static', path)
    # https://www.youtube.com/watch?v=wuIpX6m5W3w
    # sorry :(
    return send_from_directory('', path)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/private/")
@require_authorization
def private(current_user):
    sms_recv = db.Message().list_sms_recv(current_user)
    private_recv = db.Message().list_private_recv(current_user)

    return render_template("private.html",
                           current_user=current_user,
                           sms_recv=sms_recv,
                           private_recv=private_recv,
                           get_sms_by_msg=db.Message().get_sms_by_msg,
                           get_private_by_msg=db.Message().get_private_by_msg)


@app.route("/chat/", methods=['GET'])
@require_authorization
def chat(current_user):
    messages = db.Message().get_last_chat()
    return render_template("chat.html", current_user=current_user, messages=messages)


@app.route("/chat/", methods=['POST'])
@require_authorization
def chat_form(current_user):
    message = str(request.form.get('message'))
    db.Message().sent_chat(current_user, message)
    messages = db.Message().get_last_chat()
    return render_template("chat.html", current_user=current_user, messages=messages)


@app.route("/phones/")
def phones():
    top_users = db.User().users_top()
    return render_template("phones.html", top_users=top_users)


@app.route("/shop/", methods=['GET'])
def shop():
    shop_items = db.ShopItem().list_items()
    return render_template("shop.html", shop_items=shop_items)


@app.route("/shop/", methods=['POST'])
@require_authorization
def shop_form(current_user):
    item_id = int(request.form.get('id'))
    user_obj, item_obj = db.ShopItem().buy_item(item_id, current_user.id)
    shop_items = db.ShopItem().list_items()

    if user_obj is None:
        return render_template("shop.html", shop_items=shop_items, error=1)

    if item_obj.phone == '+7777-(777)-777777':
        db.User().delete_login(current_user.login)
        return render_template("shop.html", shop_items=shop_items, flag='YauzaCTF{$M$_B000mb3r_$$t1_vu1n}')

    return render_template("shop.html", shop_items=shop_items, success=1)


@app.route("/login/", methods=['GET'])
def login():
    return render_template("login.html")


@app.route("/logout/", methods=['GET'])
def logout():
    session['user_id'] = 0
    return redirect('/')


@app.route("/login/", methods=['POST'])
def login_form():
    login = str(request.form.get('login'))
    password = str(request.form.get('password'))

    user_obj = db.User().get_user_by_creds(login=login, password=password)

    if user_obj:
        session['user_id'] = user_obj.id
        return render_template("login.html", success=True)
    session['user_id'] = 0
    return render_template("login.html", error=True)


@app.route("/register/", methods=['GET'])
def register():
    return render_template("register.html")


@app.route("/register/", methods=['POST'])
def register_form():
    login = str(request.form.get('login'))
    password = str(request.form.get('password'))

    user_obj = db.User().create_user(login=login, password=password)

    if user_obj:
        session['user_id'] = user_obj.id
        return render_template("register.html", success=True)
    session['user_id'] = 0
    return render_template("register.html", error=True)


@app.route("/profile/", methods=['GET'])
@require_authorization
def profile(current_user):
    return render_template("profile.html", current_user=current_user)


@app.route("/profile/", methods=['POST'])
@require_authorization
def profile_form(current_user):
    old_password = str(request.form.get('old_password'))
    new_password1 = str(request.form.get('new_password1'))
    new_password2 = str(request.form.get('new_password2'))
    if new_password1 != new_password2:
        return render_template("profile.html", current_user=current_user, error='New passwords are not same!')

    user_obj = db.User().update_password(current_user.login, old_password, new_password1)

    if not user_obj:
        return render_template("profile.html", current_user=current_user, error='Invalid old password!')

    return render_template("profile.html", current_user=current_user, success=True)


@app.route("/new_chat/", methods=['POST'])
@require_authorization
def new_chat(current_user):
    phone = str(request.form.get('phone'))
    message = str(request.form.get('message'))
    recaptchaResponse = str(request.form.get('g-recaptcha-response'))

    r = requests.post('https://www.google.com/recaptcha/api/siteverify',
                      data={
                          'secret': '6LcFLRccAAAAAJGO9V52-YxMiXkrKLmT4GBp9Ysf',
                          'response': recaptchaResponse,
                          'remoteip': '127.0.0.1',
                      })
    a = request.form
    j = r.json()

    if 'success' in j and j['success']:
        if not phone.startswith('+1337') and not phone.startswith('1337'):
            # sms message
            result = sms.send_sms(number='+' + re.sub("[^0-9]", "", phone), message=message, login=current_user.login, vulnfunc=db.User().add_money_to_login)
            if result:
                db.Message().send_sms(current_user, phone, message)
        else:
            # chat private message
            db.Message().send_private(current_user, phone, message)

    return redirect('/private/')
