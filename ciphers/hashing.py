import hashlib


def get_str_hash(input: str):
    result = {}

    if input != "":
        map = {
            "md5": hashlib.md5,  # 128 bit, not for secure apps
            "sha1": hashlib.sha1,  # 160-bit, weak for secure apps
            "sha224": hashlib.sha224,  # 224-bit, part of SHA-2
            "sha256": hashlib.sha256,  # 256-bit, very common, SHA-2
            "sha384": hashlib.sha384,  # 384-bit, SHA-2
            "sha512": hashlib.sha512,  # 512-bit, SHA-2
            "sha3_224": hashlib.sha3_224,  # 224-bit,strong, SHA-3
            "sha3_256": hashlib.sha3_256,  # 256-bit,strong, SHA-3
            "sha3_384": hashlib.sha3_384,  # 384-bit,strong, SHA-3
            "sha3_512": hashlib.sha3_512,  # 512-bit,strong, SHA-3
            "blake2b": hashlib.blake2b,  # High security, 1-64 bytes output
            "blake2s": hashlib.blake2s,  # High security, 1-32 bytes output
        }
        # converting into input into bytes as hash function operate on bytes not on str
        data = input.encode("utf-8")
        for name, ctor in map.items():
            hash_obj = ctor()
            # updating into byte value
            hash_obj.update(data)
            result[name] = hash_obj.hexdigest()

    return result


def get_file_hash(file_obj, algo=["md5", "sha256"], chunk_size=8192):
    hashers = {name: hashlib.new(name) for name in algo}

    while True:
        chunk = file_obj.read(chunk_size)
        if not chunk:
            break
        for h in hashers.values():
            h.update(chunk)

    file_obj.seek(0)  # rewind for later use
    return {name: h.hexdigest() for name, h in hashers.items()}
