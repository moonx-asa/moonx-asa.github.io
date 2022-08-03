import sanic
import functools
import algosdk

from . import settings


def basic_json(status, **kwargs):
    """
    Build and return a basic json message
    """
    return {"status": status, **kwargs}


def fail_response(message='Invalid Request', **kwargs):
    """
    Build and return a json fail message.
    """
    json_response = basic_json("fail", message=message, **kwargs)
    return sanic.response.json(json_response)


def ok_response(**kwargs):
    """
    Build and return a json fail message.
    """
    json_response = basic_json("ok", **kwargs)
    return sanic.response.json(json_response)


# Cookie Helpers
def require_auth():
    """
    This decorator checks if the requesting user is logged in
    """
    def decorator(func):
        @functools.wraps(func)
        async def _require_auth(request, *args, **kwargs):
            if not hasattr(request.ctx, 'user'): raise sanic.exceptions.Unauthorized('User not logged in')
            if not request.ctx.user: raise sanic.exceptions.Unauthorized('User not logged in')

            response = await func(request, *args, **kwargs)
            return response
        return _require_auth
    return decorator


def build_algo_client():
    return algosdk.v2client.algod.AlgodClient(
        "", 
        settings.ALGOD_NODE_URL, 
        headers={'X-API-Key': settings.ALGOD_NODE_TOKEN}
    )

