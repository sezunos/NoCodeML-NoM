from functools import wraps

from flask import session, make_response, redirect, request


def htmx_redirect(to: str):
    redirect_response = make_response("", 200)
    redirect_response.headers["HX-Redirect"] = to
    return redirect_response

def session_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect("/auth")
        
        return func(*args, **kwargs)
    return wrapper

def is_htmx_req():
    return request.headers.get("HX-Request") and request.method == "POST"