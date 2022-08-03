import sanic
import jwt
import importlib

from . import settings
from . import exceptions


app = sanic.Sanic('secure-walletauth')
app.static("/static", './static')

# Register Blueprints
BLUEPRINTS = [
    ('backend.blueprints.auth', 'blueprint'),
    ('backend.blueprints.examples', 'blueprint')
]

# Load Blueprints
for want_module, want_bp in BLUEPRINTS:
    try:
        # Load and blueprint
        loaded_module = importlib.import_module(want_module)
        loaded_bp = getattr(loaded_module, want_bp, None)
        if not loaded_bp: raise exceptions.InvalidBlueprint()

        # Register Blueprint
        app.blueprint(loaded_bp)

    except (ModuleNotFoundError, exceptions.InvalidBlueprint) as err:
        raise err

# Attach user model
@app.middleware('request')
async def _attach_user(request):
    if settings.COOKIE_NAME in request.cookies: 
        auth_jwt = request.cookies.get(settings.COOKIE_NAME)

        try:
            auth_decoded = jwt.decode(auth_jwt, settings.SECRET_KEY, algorithms=settings.JWT_KEY_ALG)
            authorized_wallet = auth_decoded['authorized_wallet']
            user = {
                'authorized_wallet': authorized_wallet,
                'role': 'user'
            }
            request.ctx.user = user
        except jwt.exceptions.InvalidSignatureError as err: 
            return

# Update cookie max-age after each response
@app.middleware('response')
async def _update_cookie_max_age(request, response):
    if settings.COOKIE_NAME in request.cookies:
        response.cookies[settings.COOKIE_NAME] = request.cookies[settings.COOKIE_NAME]
        response.cookies[settings.COOKIE_NAME]['domain'] = settings.COOKIE_DOMAIN
        response.cookies[settings.COOKIE_NAME]['max-age'] = settings.COOKIE_LIFESPAN


if __name__ == "__main__":
    try:
        ssl = dict(cert=settings.SSL_CERT_PATH, key=settings.SSL_KEY_PATH)

        app.run(
            host='0.0.0.0',
            port=8088, 
            ssl=ssl,
            debug=True,
            auto_reload=True,
            workers=1,
        )
        
    except KeyboardInterrupt:
        print("Got quit signal. Shutting down.")

