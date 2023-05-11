import unittest
from daf_virtual_rasp.utils.cripto_daf import CriptoDAF, ChaveCripto, Certificado


class TestaCriptoDAF(unittest.TestCase):

    
    def setUp(self):
        self.msg = b'mensagem'
        self.priv, self.pub = CriptoDAF.gera_chave_RSA(2048)
        self.msg_hmac = CriptoDAF.gera_HMAC_SHA256(b'chave', self.msg)
        self.cifrado = CriptoDAF.cifra_RSAAES_OAEP(self.pub, self.msg)
        self.assinatura = CriptoDAF.gera_assinatura_RSA_PKCS1_V1_5(
            self.msg, self.priv)
        self.resumo = CriptoDAF.gera_resumo_SHA256(self.msg)

    def testa_geraChaveCripto(self):
        self.assertIsInstance(CriptoDAF.gera_chave_RSA(2048)[0], ChaveCripto)
        self.assertIsInstance(CriptoDAF.gera_chave_RSA(2048)[1], ChaveCripto)

    def testa_geraAssinaturaRSA_PKCS1_V1_5(self):

        self.assertIsInstance(
            CriptoDAF.gera_assinatura_RSA_PKCS1_V1_5(self.msg, self.priv), bytes)
        self.assertIs(
            len(CriptoDAF.gera_assinatura_RSA_PKCS1_V1_5(self.msg, self.priv)), 256)

    def testa_verificaAssinaturaRSA_PKCS1_V1_5(self):

        self.assertTrue(CriptoDAF.verifica_assinatura_RSA_PKCS1_V1_5(
            self.msg, self.assinatura, self.pub))
        self.assertFalse(CriptoDAF.verifica_assinatura_RSA_PKCS1_V1_5(
            self.msg+bytes([1]), self.assinatura, self.pub))

    def testa_cifraRSAAES_OAEP(self):

        self.assertIsInstance(
            CriptoDAF.cifra_RSAAES_OAEP(self.pub, self.msg), bytes)
        self.assertIs(len(CriptoDAF.cifra_RSAAES_OAEP(self.pub, self.msg)), 256)

    def testa_decifraRSAAES_OAEP(self):

        self.assertTrue(CriptoDAF.decifra_RSAAES_OAEP(
            self.priv, self.cifrado) == self.msg)

    def testa_geraHMAC_SHA256(self):

        self.assertTrue(CriptoDAF.gera_HMAC_SHA256(
            b'chave', self.msg) == self.msg_hmac)
        self.assertFalse(CriptoDAF.gera_HMAC_SHA256(
            b'outra-chave', self.msg) == self.msg_hmac)

    def testa_verificaHMAC_SHA256(self):

        self.assertTrue(CriptoDAF.verifica_HMAC_SHA256(
            b'chave', self.msg, self.msg_hmac))
        self.assertFalse(CriptoDAF.verifica_HMAC_SHA256(
            b'chave', self.msg, b'outro-resumo'))

    def testa_geraResumoSHA256(self):

        self.assertTrue(len(CriptoDAF.gera_resumo_SHA256(self.msg)) == 32)
        self.assertIsInstance(CriptoDAF.gera_resumo_SHA256(self.msg), bytes)

    def testa_verificaResumoSHA256(self):

        self.assertTrue(CriptoDAF.verifica_resumo_SHA256(self.msg, self.resumo))
        self.assertFalse(CriptoDAF.verifica_resumo_SHA256(
            self.msg, b'outro-resumo'))

    def testa_geraNumeroAleatorio(self):
        self.assertTrue(len(CriptoDAF.gera_numero_aleatorio(10)) == 10)
        self.assertTrue(len(CriptoDAF.gera_numero_aleatorio(16)) == 16)
        self.assertFalse(len(CriptoDAF.gera_numero_aleatorio(15)) == 10)


if __name__ == '__main__':
    unittest.main()
