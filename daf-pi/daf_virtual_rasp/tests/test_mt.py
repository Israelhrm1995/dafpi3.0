from random import choice
from string import ascii_uppercase, ascii_lowercase, digits
import secrets
import unittest

from daf_virtual_rasp.memoria.mt import MemoriaDeTrabalho
from daf_virtual_rasp.utils.base64URL_daf import Base64URLDAF


class TestaMT(unittest.TestCase):
    
    def testaOperacoes(self):

        mt = MemoriaDeTrabalho('daf_virtual_rasp/tests/resources/memorias/banco_de_testes_mt.json')
        
        # limpa banco
        mt.banco.drop_tables()

        cont = 0
        idDAF = "3210321093"
        versaoSB = "01.0.0."
        idAut = "89r8h92h89(H*WADh98AH"
        fragDFE = Base64URLDAF.base64URLEncode(secrets.token_bytes(1024*10))
        hashDFE = Base64URLDAF.base64URLEncode(secrets.token_bytes(256))

        self.assertTrue(mt.add_autorizacao_DFE(idDAF, versaoSB, cont, idAut, fragDFE, hashDFE))
        self.assertTrue(mt.existe_autorizacao_DFE(hashDFE, 'hashDFE'))
        self.assertFalse(mt.existe_autorizacao_DFE(hashDFE, 'blabla'))
        self.assertFalse(mt.existe_autorizacao_DFE('fdsfdsafsdafblabla', 'hashDFE'))
        self.assertIsNotNone(mt.get_autorizacao_DFE(hashDFE, 'hashDFE'))
        self.assertIsNone(mt.get_autorizacao_DFE(hashDFE, 'blabla'))

        # idAut existente e mcounter existente! então deve falhar ao inserir no banco
        self.assertFalse(mt.add_autorizacao_DFE(idDAF, versaoSB, cont, idAut, fragDFE, hashDFE))

        # apenas idAut existente, deve falhar
        cont = cont + 1
        self.assertFalse(mt.add_autorizacao_DFE(idDAF, versaoSB, cont, idAut, fragDFE, hashDFE))

        # apenas cont existente, deve falhar
        idAut = "$*U(##@$H@#F@fsdfsaf"
        cont = cont - 1
        self.assertFalse(mt.add_autorizacao_DFE(idDAF, versaoSB, cont, idAut, fragDFE, hashDFE))

        # apenas hashDFE existente, deve falhar
        cont = cont + 1
        self.assertFalse(mt.add_autorizacao_DFE(idDAF, versaoSB, cont, idAut, fragDFE, hashDFE))

        # idAut, cont e  hashDFE novos, deve suceder
        hashDFE = Base64URLDAF.base64URLEncode(secrets.token_bytes(256))
        self.assertTrue(mt.add_autorizacao_DFE(idDAF, versaoSB, cont, idAut, fragDFE, hashDFE))
        

        # remove
        self.assertTrue(mt.remove_autorizacao_DFE(idAut))
        # nao existe mais a autorizacao
        self.assertIsNone(mt.get_autorizacao_DFE(hashDFE, 'hashDFE'))
        # nao pode remover de novo
        self.assertFalse(mt.remove_autorizacao_DFE(idAut))

        # testa objeto retornado
        idAut = "42#@(Y#$Y*(@!"
        cont = cont + 1
        hashDFE = Base64URLDAF.base64URLEncode(secrets.token_bytes(256))

        self.assertTrue(mt.add_autorizacao_DFE(idDAF, versaoSB, cont, idAut, fragDFE, hashDFE))
        aut = mt.get_autorizacao_DFE(hashDFE, 'hashDFE')
        
        self.assertIsNotNone(aut)
        self.assertIsInstance(aut, dict)

        self.assertEqual(aut['idAut'], idAut)
        self.assertEqual(aut['cont'], cont)
        self.assertEqual(aut['versaoSB'], versaoSB)
        self.assertEqual(aut['fragDFE'], fragDFE)
        self.assertEqual(aut['idDAF'], idDAF)
        self.assertEqual(aut['hashDFE'], hashDFE)

        ####

        idDAF = "432432423"
        idAut = "42#FDSFDSFDS@(Y#$Y*(@!"
        cont = cont + 1
        hashDFE = Base64URLDAF.base64URLEncode(secrets.token_bytes(256))

        self.assertTrue(mt.add_autorizacao_DFE(idDAF, versaoSB, cont, idAut, fragDFE, hashDFE))