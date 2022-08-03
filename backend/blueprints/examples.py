import sanic
import algosdk

from .. import templating
from .. import helpers

from .. import settings


blueprint = sanic.Blueprint('examples', url_prefix='/ex')


@blueprint.route('/', name='index', methods=['GET'])
@helpers.require_auth()
async def example_index(request):
    """
    Display a list of examples
    """
    template = templating.render('/examples/index.html', request)
    response = sanic.response.html(template)
    return response


@blueprint.route('/payment', name='payment', methods=['GET'])
@helpers.require_auth()
async def payment(request):
    """
    Display a button that when clicked sends a transaction to be signed
    """
    template = templating.render('/examples/payment.html', request)
    response = sanic.response.html(template)
    return response


@blueprint.route('/get_payment_txn', name='get_payment_txn', methods=['POST'])
@helpers.require_auth()
async def get_payment_txn(request):
    """
    Create a single payment transaction and return it in msgpack format
    """
    algodclient = helpers.build_algo_client()
    params = algodclient.suggested_params()
    algo_txn = algosdk.future.transaction.PaymentTxn(
        request.ctx.user['authorized_wallet'], 
        params,
        request.ctx.user['authorized_wallet'], 
        algosdk.util.algos_to_microalgos(1)
    )
    msgpack_algo_txn = algosdk.encoding.msgpack_encode(algo_txn)

    return helpers.ok_response(algo_txn=msgpack_algo_txn)


@blueprint.route('/process_payment_txn', name='process_payment_txn', methods=['POST'])
@helpers.require_auth()
async def process_payment_txn(request):
    """
    Sends payment to the algorand node and waits for confirmation
    """
    if 'signed_algo_txn_b64' not in request.form: 
        return helpers.fail_response(message='No transaction specified.')
    signed_algo_txn_b64 = request.form.get('signed_algo_txn_b64')
    signed_algo_txn = algosdk.encoding.future_msgpack_decode(signed_algo_txn_b64)

    # Send to node
    algodclient = helpers.build_algo_client()
    txn_id = algodclient.send_transaction(signed_algo_txn)

    try:
        algosdk.future.transaction.wait_for_confirmation(algodclient, txn_id)
    except algosdk.error.ConfirmationTimeoutError as err:
        return helpers.fail_response(message='Waiting for confirmation timed out.', txn_id=txn_id)
    return helpers.ok_response(txn_id=txn_id)


@blueprint.route('/grouped_txns', name='grouped_txns', methods=['GET'])
@helpers.require_auth()
async def grouped_txns(request):
    """
    Display a button that when clicked sends a group of transactions to be signed
    """
    template = templating.render('/examples/grouped.html', request)
    response = sanic.response.html(template)
    return response


@blueprint.route('/get_grouped_txns', name='get_grouped_txns', methods=['POST'])
@helpers.require_auth()
async def get_grouped_txns(request):
    """
    Create a group of payment transactions and return them in msgpack format
    """
    algodclient = helpers.build_algo_client()
    params = algodclient.suggested_params()

    grouped_algo_txns = algosdk.future.transaction.assign_group_id([
        algosdk.future.transaction.PaymentTxn(
            request.ctx.user['authorized_wallet'], 
            params,
            request.ctx.user['authorized_wallet'], 
            algosdk.util.algos_to_microalgos(0)
        ),
        algosdk.future.transaction.PaymentTxn(
            request.ctx.user['authorized_wallet'], 
            params,
            request.ctx.user['authorized_wallet'], 
            algosdk.util.algos_to_microalgos(1)
        )
    ])

    return helpers.ok_response(
        grouped_txns = [algosdk.encoding.msgpack_encode(txn) for txn in grouped_algo_txns]
    )


@blueprint.route('/process_grouped_txns', name='process_grouped_txns', methods=['POST'])
@helpers.require_auth()
async def process_grouped_txns(request):
    """
    Sends a group of transactions to the algorand node and waits for confirmation
    """
    if 'signed_grouped_txns_b64[]' not in request.form: 
        return helpers.fail_response(message='Invalid transaction group specified. a')
    signed_grouped_txns_b64 = request.form.getlist('signed_grouped_txns_b64[]')

    if len(signed_grouped_txns_b64) < 2:
        return helpers.fail_response(message='Invalid transaction group specified. b')

    signed_grouped_txns = [algosdk.encoding.future_msgpack_decode(txn) for txn in signed_grouped_txns_b64]

    # Send to node
    algodclient = helpers.build_algo_client()
    txn_id = signed_grouped_txns[0].get_txid()
    algodclient.send_transactions(signed_grouped_txns)

    try:
        algosdk.future.transaction.wait_for_confirmation(algodclient, txn_id)
    except algosdk.error.ConfirmationTimeoutError as err:
        return helpers.fail_response(message='Waiting for confirmation timed out.', txn_id=txn_id)
    return helpers.ok_response(txn_id=txn_id)

