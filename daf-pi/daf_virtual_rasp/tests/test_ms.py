import unittest
from daf_virtual_rasp.memoria.memoria_segura import MemoriaSegura
from daf_virtual_rasp.daf.daf_enums import Artefatos, Guardas, Estados, ParametrosAtualizacao
from daf_virtual_rasp.daf.daf import DAF
from daf_virtual_rasp.utils.cripto_daf import Certificado, ChaveCripto


class TestaMemoriaSegura(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ms = MemoriaSegura(
            'daf_virtual_rasp/tests/resources/memorias/banco_de_testes_ms.json')

        cls.ms_reg = MemoriaSegura(
            'daf_virtual_rasp/tests/resources/memorias/banco_de_testes_ms.json')

    def testa_leitura(self):

        self.assertIsInstance(self.ms.leitura(Guardas.MaxDFe), int)
        self.assertIsInstance(self.ms.leitura(Guardas.REGOK), bool)
        self.assertIsInstance(self.ms.leitura(Guardas.NumDFe), int)
        self.assertIsInstance(self.ms.leitura(Guardas.MaxDFeModel), int)
        self.assertIsInstance(self.ms.leitura(Guardas.Violado), bool)
        self.assertIsInstance(self.ms.leitura(Guardas.Estado), str)

        self.assertIsInstance(self.ms.leitura(
            Artefatos.certificado), Certificado)
        self.assertIsInstance(self.ms.leitura(Artefatos.chaveAteste), ChaveCripto)
        self.assertIsInstance(self.ms.leitura(
            Artefatos.chavePrivada), ChaveCripto)
        self.assertIsInstance(self.ms.leitura(
            Artefatos.chavePublica), ChaveCripto)
        self.assertIsInstance(self.ms.leitura(Artefatos.chaveSEF), bytes)
        self.assertIsInstance(self.ms.leitura(Artefatos.chavePAF), bytes)
        self.assertIsInstance(self.ms.leitura(Artefatos.contador), int)
        self.assertIsInstance(self.ms.leitura(Artefatos.IDDAF), str)
        self.assertIsInstance(self.ms.leitura(Artefatos.modelo), str)

        self.assertIsInstance(self.ms.leitura(
            ParametrosAtualizacao.resumoSB), bytes)
        self.assertIsInstance(self.ms.leitura(
            ParametrosAtualizacao.versaoSB), str)

    def testa_escrita(self):

        self.assertTrue(self.ms_reg.escrita(Guardas.MaxDFe, 10))
        self.assertFalse(self.ms_reg.escrita(Guardas.MaxDFe, 'dez'))

        self.assertTrue(self.ms_reg.escrita(Guardas.REGOK, False))
        self.assertFalse(self.ms_reg.escrita(Guardas.REGOK, 'False'))

        self.assertTrue(self.ms_reg.escrita(Guardas.NumDFe, 0))
        self.assertFalse(self.ms_reg.escrita(Guardas.NumDFe, 'zero'))

        self.assertTrue(self.ms_reg.escrita(Guardas.MaxDFeModel, 10))
        self.assertFalse(self.ms_reg.escrita(Guardas.MaxDFeModel, 'dez'))

        self.assertTrue(self.ms_reg.escrita(Guardas.Violado, False))
        self.assertFalse(self.ms_reg.escrita(Guardas.Violado, 'False'))

        self.assertTrue(self.ms_reg.escrita(
            Guardas.Estado, Estados.inativo.value))
        self.assertFalse(self.ms_reg.escrita(Guardas.Estado, 0))

        cert = self.ms.leitura(Artefatos.certificado)
        chave_ateste = self.ms.leitura(Artefatos.chaveAteste)
        chave_priv = self.ms.leitura(Artefatos.chavePrivada)
        chave_pub = self.ms.leitura(Artefatos.chavePublica)

        self.assertTrue(self.ms_reg.escrita(Artefatos.certificado, cert))
        self.assertFalse(self.ms_reg.escrita(
            Artefatos.certificado, 'certificado'))

        self.assertFalse(self.ms_reg.escrita(
            Artefatos.chaveAteste, chave_ateste))

        self.assertTrue(self.ms_reg.escrita(
            Artefatos.chavePrivada, chave_priv))
        self.assertFalse(self.ms_reg.escrita(
            Artefatos.chavePrivada, 'chave-priv'))

        self.assertTrue(self.ms_reg.escrita(Artefatos.chavePublica, chave_pub))
        self.assertFalse(self.ms_reg.escrita(
            Artefatos.chavePublica, 'chave-pub'))

        self.assertTrue(self.ms_reg.escrita(Artefatos.chaveSEF, b'chave-sef'))
        self.assertFalse(self.ms_reg.escrita(Artefatos.chaveSEF, 'chave-sef'))

        self.assertTrue(self.ms_reg.escrita(Artefatos.chavePAF, b'chave-paf'))
        self.assertFalse(self.ms_reg.escrita(Artefatos.chavePAF, 'chave-paf'))

        self.assertTrue(self.ms_reg.escrita(Artefatos.contador, 0))
        self.assertFalse(self.ms_reg.escrita(Artefatos.contador, 'zero'))

        self.assertFalse(self.ms_reg.escrita(Artefatos.IDDAF, 'iddaf'))
        self.assertFalse(self.ms_reg.escrita(Artefatos.modelo, 'modelodaf'))

        self.assertTrue(self.ms_reg.escrita(
            ParametrosAtualizacao.resumoSB, b'resumo'))
        self.assertFalse(self.ms_reg.escrita(
            ParametrosAtualizacao.resumoSB, 'resumo'))

        self.assertTrue(self.ms_reg.escrita(
            ParametrosAtualizacao.versaoSB, 'versao'))
        self.assertFalse(self.ms_reg.escrita(
            ParametrosAtualizacao.versaoSB, 0))
