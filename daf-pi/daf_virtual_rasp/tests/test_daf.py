import unittest
from daf_virtual_rasp.utils.cripto_daf import CriptoDAF, ChaveCripto, Certificado
from daf_virtual_rasp.utils.jwt_daf import JWTDAF
from daf_virtual_rasp.utils.base64URL_daf import Base64URLDAF
from daf_virtual_rasp.daf.daf_enums import Estados, Guardas, Respostas, Artefatos
from daf_virtual_rasp.daf.daf import DAF
from daf_virtual_rasp.utils.simula_sef import SEF
import json


class TestaDAFNaoRegistrado(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        cls.daf = DAF('daf_virtual_rasp/tests/resources/daf-nao-registrado/config-nao-registrado.json')
        cls.daf.ms.escrita(Artefatos.chavePrivada, ChaveCripto(""))
        cls.daf.ms.escrita(Artefatos.chavePublica, ChaveCripto(""))
        cls.daf.ms.escrita(Artefatos.chavePAF, b"")
        cls.daf.ms.escrita(Artefatos.chaveSEF, b"")
        cls.daf.ms.escrita(Guardas.Estado, Estados.inativo.value)
        cls.daf.ms.escrita(Guardas.REGOK, False)

    @classmethod
    def setUpClass(cls):
        cls.daf = DAF('daf_virtual_rasp/tests/resources/daf-nao-registrado/config-nao-registrado.json')
        cls.daf.ms.escrita(Artefatos.chavePrivada, ChaveCripto(""))
        cls.daf.ms.escrita(Artefatos.chavePublica, ChaveCripto(""))
        cls.daf.ms.escrita(Artefatos.chavePAF, b"")
        cls.daf.ms.escrita(Artefatos.chaveSEF, b"")
        cls.daf.ms.escrita(Guardas.Estado, Estados.inativo.value)
        cls.daf.ms.escrita(Guardas.REGOK, False)

    def testa_processo_registro(self):
        msg = SEF.mensagem_blob(1)
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 2)
        

        msg = SEF.iniciarRegistro()
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 0)

        msg = SEF.mensagem_blob(2)
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 2)

        msg = SEF.confirmarRegistro()
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 0)

        msg = SEF.iniciarRegistro()
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 1)

    def testa_processo_remover_registro(self):

        msg = SEF.mensagem_blob(6)
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 2)

        msg = SEF.removerRegistro()
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 0)
        
        msg = SEF.mensagem_blob(7)
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 2)

        msg = SEF.confirmarRemocaoRegistro()
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 0)

        msg = SEF.removerRegistro()
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 1)

    def testa_processo_atualizar_certificado(self):
        msg = SEF.mensagem_blob(10)
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 2)
        
        msg = SEF.atualizarCertificado()
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 0)


class TestaDAFRegistrado(unittest.TestCase):

    def setUp(self):
        self.daf = DAF('daf_virtual_rasp/tests/resources/daf-registrado/config-registrado.json')
        self.daf.ms.escrita(Artefatos.contador, 0)
        self.daf.ms.escrita(Guardas.NumDFe, 0)
        self.daf.mt.banco.truncate()

    def testa_processo_autorizacao(self):

        msg = SEF.solicitarAutenticacao()
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 0)

        msg = SEF.autorizarDFE(json.loads(res)['nonce'])
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 0)

        msg = SEF.autorizarDFE('nonce')
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 4)

        msg = SEF.mensagem_blob(4)
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 2)

    def testa_processo_remocao_dfe(self):


        msg = SEF.solicitarAutenticacao()
        res = self.daf.processa_pedido(msg)

        msg = SEF.autorizarDFE(json.loads(res)['nonce'])
        res = self.daf.processa_pedido(msg)

        msg = SEF.apagarAutorizacaoRetida(
            "oDrZggSoja9LomJHKPri_vp4Kz_nExz8hZkcyilm5U0", True)
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 5)

        msg = SEF.mensagem_blob(5)
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 2)

        msg = SEF.apagarAutorizacaoRetida(
            "oDrZggSoja9LomJHKPri_vp4Kz_nExz8hZkcyilm5U0")
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 0)

        msg = SEF.apagarAutorizacaoRetida(
            "oDrZggSoja9LomJHKPri_vp4Kz_nExz8hZkcyilm5U0")
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 6)

    def testa_processo_consultar_informacoes(self):
        msg = SEF.consultarInformacoes()
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 0)
        self.assertEqual(len(json.loads(res)), 10)

    def testa_processo_descarregar_retidos(self):
        msg = SEF.solicitarAutenticacao()
        res = self.daf.processa_pedido(msg)

        msg = SEF.autorizarDFE(json.loads(res)['nonce'])
        res = self.daf.processa_pedido(msg)

        msg = SEF.mensagem_blob(11)
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 2)

        msg = SEF.descarregarRetidos(
            "oDrZggSoja9LomJHKPri_vp4Kz_nExz8hZkcyilm5U0")
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 0)
        self.assertEqual(len(json.loads(res)['idAut']), 43)

        msg = SEF.descarregarRetidos(
            "oDrZggSoja9LomJHKPri_vp4Kz_nExz8hZkcyilm5U1")
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 6)

    def testa_processo_atualizarSB(self):
        msg = SEF.atualizarSB()
        res = self.daf.processa_pedido(msg)
        self.assertEqual(json.loads(res)['res'], 0)


if __name__ == '__main__':
    unittest.main()
