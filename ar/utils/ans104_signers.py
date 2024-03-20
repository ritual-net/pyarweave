from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from Crypto.Util.number import bytes_to_long, long_to_bytes


class Signer:
    owner_length = None
    signature_length = None
    owner_structpack = 'generated later'
    signature_structpack = 'generated later'

    @classmethod
    def sign(cls, private_key, raw_data):
        raise NotImplementedError(cls.__name__ + '.sign')

    @classmethod
    def verify(cls, public_key, raw_data, raw_signature):
        raise NotImplementedError(cls.__name__ + '.verify')

    @classmethod
    def raw_owner(cls, key):
        raise NotImplementedError(cls.__name__ + '.raw_owner')

    @classmethod
    def public_key(cls, raw_owner):
        raise NotImplementedError(cls.__name__ + '.public_key')

class Arweave(Signer): # rsa4096pss
    type = 1
    owner_length = 512
    signature_length = 512
    name = 'arweave'

    @classmethod
    def sign(cls, private_key, databytes):
        hash = SHA256.new(databytes)
        # arweave-js on node sets the maximum salt length by leaving it at node's default
        # if salt_bytes isn't correct verification can fail
        return pss.new(private_key, salt_bytes=cls.owner_length - SHA256.digest_size - 2).sign(hash)

    @classmethod
    def verify(cls, public_key, raw_data, raw_signature):
        hash = SHA256.new(raw_data)
        # arweave-js on node sets the maximum salt length by leaving it at node's default
        # if salt_bytes isn't correct verification can fail
        verifier = pss.new(public_key, salt_bytes=cls.owner_length - SHA256.digest_size - 2)
        try:
            verifier.verify(hash, raw_signature)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def raw_owner(key):
        return long_to_bytes(key.n)

    @staticmethod
    def public_key(raw_owner, consistency_check = True):
        return RSA.construct((bytes_to_long(raw_owner), 65537), consistency_check=consistency_check)

Rsa4096Pss = Arweave

class Ed25519(Signer):
    type = 2
    owner_length = 32
    signature_length = 64
    name = 'ed25519'

Curve25519 = Ed25519

class Ethereum(Signer):
    type = 3
    owner_length = 65
    signature_length = 65
    name = 'ethereum'

Secp256k1 = Ethereum

class Solana(Signer):
    type = 4
    owner_length = 32
    signature_length = 64
    name = 'solana'

class InjectedAptos(Signer):
    type = 5
    owner_length = 32
    signature_length = 64
    name = 'injectedAptos'

class MultiAptos(Signer):
    type = 6
    owner_length = 32 * 32 + 1
    signature_length = 64 * 32 + 4
    name = 'multiAptos'

class TypedEthereum(Signer):
    type = 7
    owner_length = 42
    signature_length = 65
    name = 'typedEthereum'

BY_TYPE = {
    keycfg.type: keycfg
    for keycfg in (Rsa4096Pss, Curve25519, Secp256k1, Solana)
}

for signer in BY_TYPE.values():
    signer.owner_structpack = str(signer.owner_length) + 's'
    signer.signature_structpack = str(signer.signature_length) + 's'

DEFAULT = Rsa4096Pss
