from arweave import Wallet
import arweave
import responses
from arweave.utils import winston_to_ar
import pytest

wallet = Wallet("test_jwk_file.json")

api_url = arweave.arweave_lib.API_URL


@responses.activate
def test_get_balance():
    mock_balance = "12345678"
    mock_url = '{}/wallet/{}/balance'.format(api_url, wallet.address)
    # register successful response
    responses.add(responses.GET, mock_url, body=mock_balance, status=200)
    # register unsuccessful response
    responses.add(responses.GET, mock_url, body="some error occurred", status=400)

    # execute test against mocked response
    balance = wallet.balance
    assert balance == winston_to_ar(mock_balance)
    with pytest.raises(arweave.arweave_lib.ArweaveTransactionException):
        balance = wallet.balance


@responses.activate
def test_get_last_transaction_id():
    # register successful response
    mock_tx_id = "12345678"
    mock_url = '{}/tx_anchor'.format(api_url)
    responses.add(responses.GET, mock_url, body=mock_tx_id, status=200)
    last_tx_id = wallet.get_last_transaction_id()

    assert last_tx_id == mock_tx_id
    assert wallet.last_tx == mock_tx_id


if __name__ == "__main__":
    test_get_balance()
    test_get_last_transaction_id()
