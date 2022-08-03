import sanic
import algosdk
import base64
import jwt
import nacl

from datetime import datetime, timedelta

from ..templating import render
from ..helpers import *

from .. import settings


blueprint = sanic.Blueprint('auth')


@blueprint.route('/', name='connect', methods=['GET'])
async def connect_wallet(request):
    """
    Landing page for users to connect their wallets
    """
    template = render('/connect.html', request)
    response = sanic.response.html(template)
    return response


@blueprint.route('/disconnect', name='disconnect', methods=['GET'])
async def disconnect_wallet(request):
    """
    Disconnect user's wallet and terminate session
    """
    response = sanic.response.redirect(request.app.url_for('auth.connect'))
    if request.form:
        response = ok_response()

    response.cookies[settings.COOKIE_NAME] = ''
    response.cookies[settings.COOKIE_NAME]['max-age'] = 0
    return response



@blueprint.route('/verify', name='verify', methods=['POST'])
async def verify_signature(request):
    """
    Verify a user's signature
    """
    try:
        if not request.form: raise InvalidFormData('no form');
        if 'blob' not in request.form: raise InvalidFormData('no blob');
        if 'addr' not in request.form: raise InvalidFormData('no addr');
        blob_txn = request.form.get('blob')
        auth_address = request.form.get('addr')            

        signed_txn = algosdk.encoding.future_msgpack_decode(blob_txn)
        message = base64.b64decode(algosdk.encoding.msgpack_encode(signed_txn.transaction))
        prefixed_message = algosdk.constants.txid_prefix + message

        vkey = nacl.signing.VerifyKey(algosdk.encoding.decode_address(auth_address))
        vkey.verify(prefixed_message, base64.b64decode(signed_txn.signature))

    except (InvalidFormData, nacl.exceptions.BadSignatureError) as err:
        return fail_response(message=err.message)

    response = ok_response()
    payload = { 'authorized_wallet': auth_address }
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_KEY_ALG)
    response.cookies[settings.COOKIE_NAME] = access_token
    response.cookies[settings.COOKIE_NAME]['domain'] = settings.COOKIE_DOMAIN
    response.cookies[settings.COOKIE_NAME]['max-age'] = settings.COOKIE_LIFESPAN

    return response

