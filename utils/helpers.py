from flask import session, make_response, redirect
from functools import wraps

def htmx_redirect(to: str, **kwargs):
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

def get_data_control(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)[0]

        if not result:
            return None
        return result[0]
    return wrapper