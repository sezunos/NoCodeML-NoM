from flask import render_template, request, Blueprint, session, redirect
from db import db
from utils import helpers
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from os import urandom


auth_bp = Blueprint("auth", __name__)

def generate_hash(password: str):
    salt = urandom(16)
    hashed_password = pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000
    )

    return salt + b':' + hashed_password

def check_password(candidate_password: str, hash_from_db: bytes):
    salt, hashed_password = hash_from_db.split(b':')
    hashed_candidate_password = pbkdf2_hmac(
        "sha256",
        candidate_password.encode("utf-8"),
        salt,
        100_000
    )

    return compare_digest(hashed_password, hashed_candidate_password)

def set_session(id: int, username: str):
    session["id"] = id
    session["username"] = username

#-------ROUTES-------

@auth_bp.route("/")
@helpers.session_required
def root_page():
    return redirect("/account")

@auth_bp.route("/auth", methods=["get", "post"])
def auth_page():
    if request.headers.get("HX-Request") and request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        data = db.get_user_data(username)
        if not data or not check_password(password, data[2]):
            return "Неверные данные"

        set_session(data[0], data[1])
        return helpers.htmx_redirect("/account")

    return render_template("auth.html")

@auth_bp.route("/registration", methods=["get", "post"])
def registration_page():
    if request.headers.get("HX-Request") and request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if db.get_user_data(username):
            return "Пользователь с таким логином уже существует"
        
        hashed_password = generate_hash(password)
        lastrowid = db.add_user(username, hashed_password)

        set_session(lastrowid, username)
        return helpers.htmx_redirect("/account")

    return render_template("registration.html")