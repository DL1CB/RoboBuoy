class BTFailure(Exception):
    pass


def decode_int(x, f):
    f += 1
    newf = x.index(bytes("e", "utf-8"), f)
    n = int(x[f:newf])

    if x[f] == ord("-"):
        if x[f + 1] == ord("0"):
            raise ValueError

    elif x[f] == ord("0") and newf != f + 1:
        raise ValueError

    return (n, newf + 1)


def decode_bool(x, f):
    f += 1
    newf = x.index(bytes("e", "utf-8"), f)
    n = int(x[f:newf])

    if n == 1:
        n = True
    else:
        n = False

    if x[f] == ord("-"):
        if x[f + 1] == ord("0"):
            raise ValueError

    elif x[f] == ord("0") and newf != f + 1:
        raise ValueError

    return (n, newf + 1)


def decode_bytes(x, f):

    colon = x.index(bytes(":", "utf-8"), f)
    n = int(x[f:colon])

    if x[f] == ord("0") and colon != f + 1:
        raise ValueError

    colon += 1

    # return (x[colon:colon + n], colon + n)
    rawbytes = x[colon:colon + n]
    return (rawbytes.decode('utf-8'), colon + n)


def decode_string(x, f):
    r, l = decode_bytes(x, f)
    # return str(r, "utf-8"), l
    return (r, l)


def decode_list(x, f):
    r, f = [], f + 1
    while x[f] != ord("e"):
        v, f = decode_func[x[f]](x, f)
        r.append(v)

    return (r, f + 1)


def decode_dict(x, f):
    r, f = {}, f + 1
    while x[f] != ord("e"):
        k, f = decode_string(x, f)
        r[k], f = decode_func[x[f]](x, f)

    return (r, f + 1)


decode_func = {
    ord("l"): decode_list,
    ord("d"): decode_dict,
    ord("i"): decode_int,
    ord("j"): decode_bool,
    ord("0"): decode_bytes,
    ord("1"): decode_bytes,
    ord("2"): decode_bytes,
    ord("3"): decode_bytes,
    ord("4"): decode_bytes,
    ord("5"): decode_bytes,
    ord("6"): decode_bytes,
    ord("7"): decode_bytes,
    ord("8"): decode_bytes,
    ord("9"): decode_bytes
}


def bdecode(x):
    try:
        r, l = decode_func[x[0]](x, 0)
    except (IndexError, KeyError, ValueError):
        return False
        #raise BTFailure("not a valid bencoded string")

    if l != len(x):
        pass
        raise BTFailure("invalid bencoded value (data after valid prefix)")

    return r


def encode_int(x):
    result = bytearray()

    result.append(ord("i"))

    result.extend(bytes(str(x), "utf-8"))
    result.append(ord("e"))

    return result


def encode_bool(x):
    result = bytearray()

    result.append(ord("j"))

    if x:
        result.extend(bytes(str(1), "utf-8"))
    else:
        result.extend(bytes(str(0), "utf-8"))

    result.append(ord("e"))

    return result


def encode_bytes(x):
    result = bytearray()
    result.extend(bytes("{}:".format(len(x)), "utf-8"))
    result.extend(x)
    return result


def encode_string(x):
    return encode_bytes(bytes(x, "utf-8"))


def encode_list(x):
    result = bytearray()

    result.append(ord("l"))

    for i in x:
        result.extend(encode_func[type(i)](i))

    result.append(ord("e"))

    return result


def encode_dict(x):
    result = bytearray()

    result.append(ord("d"))

    # for k, v in sorted(x.items()):
    for k, v in x.items():
        result.extend(encode_string(str(k)))
        result.extend(encode_func[type(v)](v))

    result.append(ord("e"))

    return result


encode_func = {
    int: encode_int,
    bool: encode_bool,
    bytes: encode_bytes,
    str: encode_string,
    list: encode_list,
    tuple: encode_list,
    dict: encode_dict
}


def bencode(x):
    return bytes(encode_func[type(x)](x))



def encodeTransformer(mtu, x):
    """ 
    encodes x and returns a generator yielding 
    the maximum transmission unit number of bytes
    @mtu Int: the maximum number of bytes per yield
    @x Obj: python obj to be encoded
    @returns: a generator
    """
    source = bencode(x)
    for i in range(0, len(source), mtu):
        yield source[i:i+mtu]


def decodeTransformer(successHandler, conn_handle=None):
    """
    The decodeTransformer allows a stream of 
    bytes to be accumulated, the successHandler
    is called with the sucessful result
    """
    accumulator = b''
    
    def decodeChunk( chunk ):
        nonlocal accumulator
        accumulator = accumulator + chunk
    
        try:
            result = bdecode(accumulator)
            if result:
                successHandler( result, conn_handle)
        except BTFailure:
            pass
    
    return decodeChunk 
       