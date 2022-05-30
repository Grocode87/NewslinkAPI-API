import functools
from flask import request

from app import app, supabase


def verify_page_size(page_size, user_data):
    plan_name = user_data["plan_name"]

    if plan_name == "Basic":
        if page_size > 10:
            return False
    else:
        if page_size > 100:
            return False

    return True


def verify_api_key(api_key, user_data):
    if app.config["REQUIRE_API_KEY"]:
        if not api_key or not user_data:
            return False

    return True


def get_user_data_from_key(api_key):
    if not api_key:
        return None

    data = (
        supabase.table("profile")
        .select("id", "api_key", "plan_name")
        .eq("api_key", api_key)
        .execute()
    )
    if data[0]:
        return data[0][0]

    return data[0]


def api_required(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        print("checking API key")

        # verify api_key
        api_key = request.args.get("apiKey")
        user_data = get_user_data_from_key(api_key)

        if not verify_api_key(api_key, user_data):
            return {
                "status": "error",
                "message": "Unauthorized request. API key is either missing or invalid",
                "code": 401,
            }, 401

        # verify page size
        page_size = request.args.get("pageSize", default=10, type=int)
        if not verify_page_size(page_size, user_data):
            return {
                "status": "error",
                "message": "Bad Request. Page size is larger than plan allows.",
                "code": 400,
            }, 400

        return func(*args, **kwargs)

    return decorator


def log_request(req_type):
    """
    Decorator that logs the request type and the parameters used
    """

    def wrap(func):
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            user_data = get_user_data_from_key(request.args.get("apiKey"))

            data = (
                supabase.table("requests")
                .insert(
                    {
                        "user_id": user_data["id"],
                        "type": {"type": req_type, "args": request.args},
                    }
                )
                .execute()
            )

            print("logging request. type: " + req_type)
            return func(*args, **kwargs)

        return decorator

    return wrap