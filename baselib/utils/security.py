from passlib.hash import pbkdf2_sha256
import base64


def encrypt_password(passwd):
    return pbkdf2_sha256.using(salt_size=16, rounds=200000).hash(passwd)
    # return pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)


def verify_password(passwd, encrypted_password):
    return pbkdf2_sha256.verify(passwd, encrypted_password)


def encrypt(key, password):
    encoded = []
    for value in range(len(password)):
        key_c = key[value % len(key)]
        enc_c = (ord(password[value]) + ord(key_c)) % 256
        encoded.append(enc_c)
    return str(base64.urlsafe_b64encode(bytes(encoded)), encoding='utf-8')


def decrypt(key, encoded):
    enc = bytes(encoded, encoding='utf-8')
    decoded = []
    enc = base64.urlsafe_b64decode(enc)
    for value in range(len(enc)):
        key_c = key[value % len(key)]
        dec_c = chr((256 + enc[value] - ord(key_c)) % 256)
        decoded.append(dec_c)
    return "".join(decoded)
