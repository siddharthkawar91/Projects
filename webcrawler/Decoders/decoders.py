from io import BytesIO

import gzip
import brotli
import zlib



def decode_gzip(content):
    decompress_content = gzip.GzipFile(fileobj=BytesIO(content))
    try:
        return decompress_content.read()
    except (IOError, EOFError):
        return None


def decode_br(content):
    decompress_content = brotli.decompress(content)
    try:
        return decompress_content
    except (IOError, EOFError):
        return None


def decode_identity(content):
    return content


def decode_deflate(content):
    try:
        try:
            return zlib.decompress(content)
        except zlib.error:
            return zlib.decompress(content, -15)
    except zlib.error:
        return None

decompress_dict = {
    "gzip": decode_gzip,
    "br": decode_br,
    "deflate": decode_deflate,
    "identity": decode_identity
}
