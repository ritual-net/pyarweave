import json

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from jose import jwk
from jose.utils import base64url_decode

from . import DEFAULT_API_URL
from .peer import Peer
from .utils import (
    owner_to_address,
    winston_to_ar,
)


class Wallet(object):
    HASH = 'sha256'

    def __init__(self, jwk_file='jwk_file.json', api_url=DEFAULT_API_URL, jwk_data=None):
        if jwk_data is not None:
            self.jwk_data = jwk_data
        else:
            with open(jwk_file, 'r') as j_file:
                self.jwk_data = json.loads(j_file.read())

        self.jwk_data['p2s'] = ''
        self.jwk = jwk.construct(self.jwk_data, algorithm=jwk.ALGORITHMS.RS256)
        self.rsa = RSA.importKey(self.jwk.to_pem())

        self.owner = self.jwk_data.get('n')
        self.address = owner_to_address(self.owner)

        self.peer = Peer(api_url)

    @classmethod
    def generate(cls, bits = 4096, jwk_file = None):
        assert bits == 4096 # i'm not sure whether arweave is intended to handle non-4096-bit keys   2022-07-06
        key = RSA.generate(bits)
        jwk_data = jwk.RSAKey(key.export_key(), jwk.ALGORITHMS.RS256).to_dict()
        if jwk_file is not None:
            with open(jwk_file, 'xt') as jwk_fh:
                json.dump(jwk_data, jwk_fh)
        return cls(jwk_file = jwk_file, jwk_data = jwk_data)

    @classmethod
    def from_data(cls, jwk_data):
        return cls(jwk_data = jwk_data)

    @property
    def api_url(self):
        return self.peer.api_url
    
    @api_url.setter
    def api_url(self, api_url):
        self.peer.api_url = api_url

    @property
    def balance(self):
        balance = self.peer.wallet_balance(self.address)
        return winston_to_ar(balance)

    @property
    def raw_owner(self):
        return base64url_decode(self.jwk_data['n'].encode())

    def sign(self, message):
        h = SHA256.new(message)
        signed_data = PKCS1_PSS.new(self.rsa).sign(h)
        return signed_data

    def verify(self, message, signed_data):
        h = SHA256.new(message)
        status = PKCS1_PSS.new(self.rsa).verify(h, signed_data)
        return status

    def get_last_transaction_id(self):
        self.last_tx = self.peer.tx_anchor()
        return self.last_tx
