import unittest
from daf_virtual_rasp.utils.base64URL_daf import Base64URLDAF


class TestaBase64URLDAF(unittest.TestCase):

    
    def setUp(self):
        self.msg_bytes = b'mensagem-original'
        self.msg_b64 = 'bWVuc2FnZW0tb3JpZ2luYWw'

    def testa_base64URLDecode(self):
        self.assertEqual(Base64URLDAF.base64URLDecode(
            self.msg_b64), self.msg_bytes)
        self.assertNotEqual(Base64URLDAF.base64URLDecode(
            self.msg_b64), b'mensagem-falsa')

    def testa_base64URLEncode(self):
        self.assertEqual(Base64URLDAF.base64URLEncode(
            self.msg_bytes), self.msg_b64)
        self.assertNotEqual(Base64URLDAF.base64URLEncode(
            self.msg_bytes), 'mensagem-b64')


if __name__ == '__main__':
    unittest.main()
