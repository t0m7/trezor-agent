from .. import protocol
from .. import formats

import pytest

# pylint: disable=line-too-long

KEY = 'ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEUksojS/qRlTKBKLQO7CBX7a7oqFkysuFn1nJ6gzlR3wNuQXEgd7qb2bjmiiBHsjNxyWvH5SxVi3+fghrqODWo= ssh://localhost'  # nopep8
BLOB = b'\x00\x00\x00 !S^\xe7\xf8\x1cKN\xde\xcbo\x0c\x83\x9e\xc48\r\xac\xeb,]"\xc1\x9bA\x0eit\xc1\x81\xd4E2\x00\x00\x00\x05roman\x00\x00\x00\x0essh-connection\x00\x00\x00\tpublickey\x01\x00\x00\x00\x13ecdsa-sha2-nistp256\x00\x00\x00h\x00\x00\x00\x13ecdsa-sha2-nistp256\x00\x00\x00\x08nistp256\x00\x00\x00A\x04E$\xb2\x88\xd2\xfe\xa4eL\xa0J-\x03\xbb\x08\x15\xfbk\xba*\x16L\xac\xb8Y\xf5\x9c\x9e\xa0\xceTw\xc0\xdb\x90\\H\x1d\xee\xa6\xf6n9\xa2\x88\x11\xec\x8c\xdcrZ\xf1\xf9K\x15b\xdf\xe7\xe0\x86\xba\x8e\rj'  # nopep8
SIG = (61640221631134565789126560951398335114074531708367858563384221818711312348703, 51535548700089687831159696283235534298026173963719263249292887877395159425513)  # nopep8

LIST_MSG = b'\x0b'
LIST_REPLY = b'\x00\x00\x00\x84\x0c\x00\x00\x00\x01\x00\x00\x00h\x00\x00\x00\x13ecdsa-sha2-nistp256\x00\x00\x00\x08nistp256\x00\x00\x00A\x04E$\xb2\x88\xd2\xfe\xa4eL\xa0J-\x03\xbb\x08\x15\xfbk\xba*\x16L\xac\xb8Y\xf5\x9c\x9e\xa0\xceTw\xc0\xdb\x90\\H\x1d\xee\xa6\xf6n9\xa2\x88\x11\xec\x8c\xdcrZ\xf1\xf9K\x15b\xdf\xe7\xe0\x86\xba\x8e\rj\x00\x00\x00\x0fssh://localhost'  # nopep8

SIGN_MSG = b'\r\x00\x00\x00h\x00\x00\x00\x13ecdsa-sha2-nistp256\x00\x00\x00\x08nistp256\x00\x00\x00A\x04E$\xb2\x88\xd2\xfe\xa4eL\xa0J-\x03\xbb\x08\x15\xfbk\xba*\x16L\xac\xb8Y\xf5\x9c\x9e\xa0\xceTw\xc0\xdb\x90\\H\x1d\xee\xa6\xf6n9\xa2\x88\x11\xec\x8c\xdcrZ\xf1\xf9K\x15b\xdf\xe7\xe0\x86\xba\x8e\rj\x00\x00\x00\xd1\x00\x00\x00 !S^\xe7\xf8\x1cKN\xde\xcbo\x0c\x83\x9e\xc48\r\xac\xeb,]"\xc1\x9bA\x0eit\xc1\x81\xd4E2\x00\x00\x00\x05roman\x00\x00\x00\x0essh-connection\x00\x00\x00\tpublickey\x01\x00\x00\x00\x13ecdsa-sha2-nistp256\x00\x00\x00h\x00\x00\x00\x13ecdsa-sha2-nistp256\x00\x00\x00\x08nistp256\x00\x00\x00A\x04E$\xb2\x88\xd2\xfe\xa4eL\xa0J-\x03\xbb\x08\x15\xfbk\xba*\x16L\xac\xb8Y\xf5\x9c\x9e\xa0\xceTw\xc0\xdb\x90\\H\x1d\xee\xa6\xf6n9\xa2\x88\x11\xec\x8c\xdcrZ\xf1\xf9K\x15b\xdf\xe7\xe0\x86\xba\x8e\rj\x00\x00\x00\x00'  # nopep8
SIGN_REPLY = b'\x00\x00\x00j\x0e\x00\x00\x00e\x00\x00\x00\x13ecdsa-sha2-nistp256\x00\x00\x00J\x00\x00\x00!\x00\x88G!\x0c\n\x16:\xbeF\xbe\xb9\xd2\xa9&e\x89\xad\xc4}\x10\xf8\xbc\xdc\xef\x0e\x8d_\x8a6.\xb6\x1f\x00\x00\x00!\x00q\xf0\x16>,\x9a\xde\xe7(\xd6\xd7\x93\x1f\xed\xf9\x94ddw\xfe\xbdq\x13\xbb\xfc\xa9K\xea\x9dC\xa1\xe9'  # nopep8


def test_list():
    key = formats.import_public_key(KEY)
    h = protocol.Handler(keys=[key], signer=None)
    reply = h.handle(LIST_MSG)
    assert reply == LIST_REPLY


def signer(label, blob):
    assert label == b'ssh://localhost'
    assert blob == BLOB
    return SIG


def test_sign():
    key = formats.import_public_key(KEY)
    h = protocol.Handler(keys=[key], signer=signer)
    reply = h.handle(SIGN_MSG)
    assert reply == SIGN_REPLY


def test_sign_missing():
    h = protocol.Handler(keys=[], signer=signer)

    with pytest.raises(protocol.MissingKey):
        h.handle(SIGN_MSG)


def test_sign_wrong():
    def wrong_signature(label, blob):
        assert label == b'ssh://localhost'
        assert blob == BLOB
        return (0, 0)

    key = formats.import_public_key(KEY)
    h = protocol.Handler(keys=[key], signer=wrong_signature)

    with pytest.raises(protocol.BadSignature):
        h.handle(SIGN_MSG)