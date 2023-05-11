import unittest
import secrets
from unittest.case import TestCase

from daf_virtual_rasp.utils.cripto_daf import ChaveCripto, CriptoDAF, Certificado
from daf_virtual_rasp.memoria.memoria_segura import MemoriaSegura
from daf_virtual_rasp.daf.daf_enums import Artefatos, Guardas

from daf_virtual_rasp.utils.base64URL_daf import Base64URLDAF
from daf_virtual_rasp.imagem import ImagemSB, ImagemSBCandidato
from daf_virtual_rasp.memoria.memoria_segura import MemoriaSegura

class TestaImagem(unittest.TestCase):

    def testaImagemSB(self):

        # with self.assertRaises(ValueError):
        #     ImagemSB()

        
        with open('daf_virtual_rasp/tests/resources/daf-registrado/sef-priv.pem') as file:
            priv_atual = ChaveCripto(file.read())

        versao      = "02.0.0".encode()
        codigo      = secrets.token_bytes(1024 * 1024)

        ass         = CriptoDAF.gera_assinatura_RSA_PKCS1_V1_5(codigo, priv_atual)
        resumoCript = CriptoDAF.gera_resumo_SHA256(codigo)

        blob = versao + resumoCript + ass + codigo
        with open('./outra-imagem.bin', "wb") as arquivo:
            arquivo.write(blob)
        
        sb = ImagemSB(blob, './daf_virtual_rasp/tests/resources/imagem/sb')

        self.assertEqual(versao     , sb.get_versao_SB())
        self.assertEqual(resumoCript, sb.get_hash_SB())
        self.assertEqual(ass        , sb.get_assinatura())
        self.assertEqual(codigo     , sb.get_codigo())

        self.assertTrue(sb.esta_integro())
        self.assertTrue(sb.esta_autentico('./daf_virtual_rasp/tests/resources/imagem/sb/ms.json'))
        
        #sb.remove_particao()

