from daf_virtual_rasp.utils.cripto_daf import CriptoDAF, Certificado, ChaveCripto
from daf_virtual_rasp.utils.base64URL_daf import Base64URLDAF
from daf_virtual_rasp.utils.jwt_daf import JWTDAF
from daf_virtual_rasp.memoria.memoria_segura import MemoriaSegura
from daf_virtual_rasp.memoria.mt import MemoriaDeTrabalho
from daf_virtual_rasp.daf.daf_enums import Estados, Respostas, Artefatos, Guardas, ParametrosAtualizacao
import json
from typing import Tuple, Union
from daf_virtual_rasp.imagem import ImagemSB, ImagemSBCandidato
import uuid
from daf_virtual_rasp.com.layer import Layer
from daf_virtual_rasp.com.enq_enum import TIPO_t
from jwcrypto import jwk, jwe

class DAF(Layer):

    def __init__(self):
        """ 
            Classe para representar um DAF. 
        """ 
        
        self.ms = MemoriaSegura('./ms.json')        # adiciona arquivo de memoria segura
        self.mt = MemoriaDeTrabalho('./mt.json')    # adiciona arquivo de memoria de trabalho
        self.operacao = False  
        self.nonce = None
        self.imagem_atual = ImagemSB()
        self.last_msg = None                        # ultima mensagem recebida pelo DAF
        self.timeout = 120.0
        Layer.__init__(self, None, self.timeout)
        self.enable()
        self.disable_timeout()          # Desativa o Timeout
        
       
    def __padrao_fabrica(self) -> str:
        """ Método para processar o pedido de reiniciar o DAF para o "padrão de fábrica". Pode ser utilizado para auxilio no desenvolvimento do PAF

        Returns:
            str: Resposta do DAF para o pedido


        """
        self.operacao = False
        self.mt.reinicia_memoria()
        self.ms.reinicia_memoria()
        self.nonce = None
        return json.dumps({"res": 0},separators=(',', ':'))
    
    def __novo_iddaf(self) -> str:
        """ Método para processar o pedido de reiniciar o DAF para o "padrão de fábrica", gerando um novo IDDAF. Pode ser utilizado para auxilio no desenvolvimento do PAF

        Returns:
            str: Resposta do DAF para o pedido
        """
        self.operacao = False
        self.ms.escrita(Artefatos.IDDAF, Base64URLDAF.base64URLEncode(uuid.uuid4().bytes))
        self.mt.reinicia_memoria()
        self.ms.reinicia_memoria()
        self.nonce = None
        return json.dumps({"res": 0},separators=(',', ':'))
    


    def __vai_para_violado(self) -> str:
        """ Método para processar o pedido de mudança de estado do DAF para inutilizado. Pode ser utilizado para auxilio no desenvolvimento do PAF

        Returns:
            str: Resposta do DAF para o pedido
        """
        self.ms.escrita(Guardas.Violado, True)
        return json.dumps({"res": 0},separators=(',', ':'))

    def __get_codigo_mensagem(self, msg: str) -> Tuple[int, str]:
        """ Método interno para retornar o código da mensagem recebida

        Args:
            msg (str): Mensagem JSON recebida pelo DAF

        Returns:
            Tuple[int,str]: Código da mensagem recebida. 0 se mensagem inválida
        """
        msg = json.loads(msg)

        try:
            if 'msg' in msg:
                return msg['msg'], msg
        except Exception:
            return 0

    def __valida_mensagem(self, msg) -> bool:
        """ Método interno para validação da mensagem JSON recebida pelo DAF

        Args:
            msg (str): Mensagem JSON recebida pelo DAF

        Returns:
            bool: Verdadeiro se mensagem válida, falso se mensagem inválida
        """

        if 'msg' in msg:
            cod = msg['msg']

            if cod == 1 or cod == 2 or cod == 6 or cod == 7 or cod == 12 or cod == 13:
                chaves = ['jwt']
                if(self.__verifica_chaves_mensagem(msg, chaves, 2)):
                    return True
                else:
                    return False

            elif cod == 3 or cod == 8 or cod == 9 or cod == 14 or cod == 15:
                return True

            elif cod == 4:
                chaves = ['fdf', 'hdf', 'pdv', 'red']
                if (self.__verifica_chaves_mensagem(msg, chaves, 5)):
                    return True
                else:
                    return False

            elif cod == 5:
                chaves = ['aut', 'apg']
                if (self.__verifica_chaves_mensagem(msg, chaves, 3)):
                    return True
                else:
                    return False

            elif cod == 10:
                chaves = ['crt', 'sig']
                if (self.__verifica_chaves_mensagem(msg, chaves, 3)):
                    return True
                else:
                    return False

            elif cod == 11:
                chaves = ['aut']
                if (self.__verifica_chaves_mensagem(msg, chaves, 2)):
                    return True
                else:
                    return False
            
            elif cod == 16:
                chaves = ['ini', 'fim']
                if (self.__verifica_chaves_mensagem(msg, chaves, 3)):
                    return True
                else:
                    return False           
            else:
                pass
        else:
            return False

    def processa_pedido(self, msg: str) -> Union[str, None]:
        """ Método para processar o pedido recebido pelo DAF. Assume que a mensagem já fora validade anteriormente

        Args:
            msg (int): Código da mensagem

        Returns:
            Union(str,None): Retorna a resposta do DAF ou None caso a mensagem recebida seja de um processo que não fora iniciado ou o código da mensagem recebida não seja conhecido
        """
        
        cod, msg = self.__get_codigo_mensagem(msg)

        if self.esta_violado() and cod != 9999:
            return self.modo_inutilizado()
        else:
            if self.operacao == True:
                if self.last_msg == 1:
                    if cod == 14:
                         return self.__processa_cancelarProcesso()
                    elif cod != 2:
                        return self.__gera_json_resposta_insucesso(
                    Respostas.pedidoMalFormado.value)
                    
                elif self.last_msg == 3:
                    if cod == 14:
                         return self.__processa_cancelarProcesso()
                    elif cod != 4:
                        return self.__gera_json_resposta_insucesso(
                    Respostas.pedidoMalFormado.value)
                elif self.last_msg == 6:
                    if cod == 14:
                         return self.__processa_cancelarProcesso()
                    elif cod != 7:
                        return self.__gera_json_resposta_insucesso(
                    Respostas.pedidoMalFormado.value)
                elif self.last_msg == 12:
                    if cod == 14:
                         return self.__processa_cancelarProcesso()
                    elif cod != 13:
                        return self.__gera_json_resposta_insucesso(
                    Respostas.pedidoMalFormado.value)
                elif self.last_msg == 9:
                    if cod == 14:
                         return self.__processa_cancelarProcesso()
                    return self.__gera_json_resposta_insucesso(
                    Respostas.pedidoMalFormado.value)
           
            if cod == 1:
                self.recarrega_timeout(self.timeout)
                return self.__processa_registrar(msg)
            elif cod == 2:
                self.disable_timeout()
                return self.__processa_confirmarRegistro(msg)
            elif cod == 3:
                self.recarrega_timeout(self.timeout)
                return self.__processa_solicitarAutenticacao(msg)
            elif cod == 4:
                self.disable_timeout()
                return self.__processa_autorizarDFE(msg)
            elif cod == 5:
                return self.__processa_apagarAutorizacaoRetida(msg)
            elif cod == 6:
                self.recarrega_timeout(self.timeout)
                return self.__processa_removerRegistro(msg)
            elif cod == 7:
                self.disable_timeout()
                return self.__processa_confirmarRemocaoRegistro(msg)
            elif cod == 8:
                return self.__processa_consultarInformacoes()
            elif cod == 9:
                self.recarrega_timeout(self.timeout)
                return self.__processa_atualizarSB()
            elif cod == 10:
                return self.__processa_atualizarCertificado(msg)
            elif cod == 11:
                return self.__processa_descarregarRetidos(msg)
            elif cod == 12:
                self.recarrega_timeout(self.timeout)
                return self.__processa_alterarModoOperacao(msg)
            elif cod == 13:
                self.disable_timeout()
                return self.__processa_confirmarAlterarModoOperacao(msg)
            elif cod == 14:
                return self.__processa_cancelarProcesso()
            elif cod == 15:
                return self.__processa_obterImpressaoDigital(msg)
            elif cod == 16:
                return self.__processa_consultarAutorizacoes(msg)
            elif cod == 9997:
                return self.__novo_iddaf()
            elif cod == 9998:
                return self.__vai_para_violado()
            elif cod == 9999:
                return self.__padrao_fabrica()
            
    def __verifica_chaves_mensagem(self, msg: str, chaves: list, lenDic: int) -> bool:
        """ Método interno para verificar se o JSON recebido pelo DAF possui as chaves corretas da mensagem

        Args:
            msg (string): Mensagem JSON recebida pelo DAF
            chaves (list): Lista com as chaves necessárias
            lenDic (int): Número de chaves que o dicionário deve ter

        Returns:
            bool: Resultado da verificação
        """
        if len(msg) != (lenDic):
            return False

        for chave in chaves:
            if not chave in msg:
                return False
        return True

    def __processa_registrar(self, msg: str) -> str:
        """ Método interno para processar o pedido inicial de registro do DAF 
        
        Args:
            msg (str): Mensagem JSON recebida pelo DAF

        Returns:
            str: Resposta do DAF para o pedido
        """
       
        if not self.ms.leitura(Guardas.Estado) == Estados.inativo.value:
            return self.__gera_json_resposta_insucesso(Respostas.estadoIncorreto.value)
            
        
        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(                 Respostas.pedidoMalFormado.value)
            

        certificado = self.ms.leitura(Artefatos.certificado)
              
        payload = JWTDAF.verificaJWT(msg['jwt'], certificado.chave_publica, 'ES384')

        if not payload:
            return self.__gera_json_resposta_insucesso(Respostas.assinaturaInvalida.value)
            
        

        if not 'nnc' in payload or len(payload) != 1:
            return self.__gera_json_resposta_insucesso(             Respostas.pedidoMalFormado.value)
            
        
        priv, pub = CriptoDAF.gera_chave_EC_p256()

        self.ms.escrita(
            Artefatos.chavePrivada, priv)
        self.ms.escrita(
            Artefatos.chavePublica, pub)
        payload_resposta = {}
        payload_resposta['daf'] = self.ms.leitura(
            Artefatos.IDDAF)
        payload_resposta['cnt'] = self.ms.leitura(
            Artefatos.contador)
        payload_resposta['nnc'] = payload['nnc']
        payload_resposta['vsb'] = self.ms.leitura(
            ParametrosAtualizacao.versaoSB)

        token_int = JWTDAF.geraJWT(payload_resposta, 'ES256', self.ms.leitura(Artefatos.chavePrivada), self.ms.leitura(Artefatos.chavePublica))

        
        payload_final = {}
        payload_final["jwt"] = token_int

        token_final = JWTDAF.geraJWT(payload_final, 'ES384', self.ms.leitura(Artefatos.chaveAteste), self.ms.leitura(Artefatos.chaveAtestePublica))

        self.operacao = True
        self.last_msg = 1

        return json.dumps({'res': 0, 'jwt': token_final}, separators=(',', ':'))

        

    def __processa_confirmarRegistro(self, msg: str) -> str:
        """ Método interno para processar o pedido final do registro do DAF 

        Args:
            msg (str): Mensagem JSON recebida pelo DAF

        Returns:
            str: Resposta do DAF para o pedido
        """
        if not self.operacao:
            return self.__gera_json_resposta_insucesso(                   Respostas.pedidoMalFormado.value)
              
        
        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(                    Respostas.pedidoMalFormado.value)
        
        certificado = self.ms.leitura(Artefatos.certificado)

        payload = JWTDAF.verificaJWT(msg['jwt'], certificado.chave_publica, 'ES384')

        if not payload:
            return self.__gera_json_resposta_insucesso(Respostas.assinaturaInvalida.value)

        if not 'chs' in payload or not 'chp' in payload or not 'mop' in payload or len(payload) != 3:
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
        
        chave_privada_daf = jwk.JWK()
        chave_privada_daf.import_from_pem(self.ms.leitura(Artefatos.chavePrivada).chave_bytes)
        jwetoken = jwe.JWE()
        jwetoken.deserialize(payload['chs'],key=chave_privada_daf)
        chSEF = jwetoken.payload
    
        self.ms.escrita(
            Artefatos.chaveSEF, chSEF)
        self.ms.escrita(
            Artefatos.chavePAF, Base64URLDAF.base64URLDecode(payload['chp']))
        self.ms.escrita(Artefatos.modoOperacao, payload["mop"])

        self.ms.escrita(
            Guardas.Estado, Estados.pronto.value)
        self.ms.escrita(Guardas.REGOK, True)
        self.operacao = False
        self.last_msg = 2
        return json.dumps({"res": 0}, separators=(',', ':'))


    def __processa_solicitarAutenticacao(self, msg: str) -> str:
        """ Método interno para processar o pedido inicial de autorização do DAF

        Returns:
            str: Resposta do DAF ao pedido
        """
        if not self.ms.leitura(Guardas.Estado) == Estados.pronto.value:
            return self.__gera_json_resposta_insucesso(Respostas.estadoIncorreto.value)
        
        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(                    Respostas.pedidoMalFormado.value)

        self.nonce = Base64URLDAF.base64URLEncode(CriptoDAF.gera_numero_aleatorio(16))
        self.last_msg = 3
        self.operacao = True
        return json.dumps({'res': 0, "nnc": self.nonce},separators=(',', ':'))
        
    def __processa_autorizarDFE(self, msg: str) -> str:
        """ Método interno para processar o pedido final de autorização do DAF 

        Args:
            msg (str): Mensagem JSON recebida pelo DAF

        Returns:
            str: Resposta do DAF ao pedido
        """
        
        if not self.ms.leitura(Guardas.Estado) == Estados.pronto.value:
            return self.__gera_json_resposta_insucesso(Respostas.estadoIncorreto.value)
        
        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
        
        chPAF = self.ms.leitura(Artefatos.chavePAF)

        hashDFE = Base64URLDAF.base64URLDecode(
            msg['hdf'])
        respDes = Base64URLDAF.base64URLDecode(
            msg['red'])

        msg_para_verificar = b"".join([Base64URLDAF.base64URLDecode(self.nonce), hashDFE])
        
        if not (CriptoDAF.verifica_HMAC_SHA256(chPAF, msg_para_verificar, respDes)):
            return self.__gera_json_resposta_insucesso(                       Respostas.pafDesconhecido.value)
        
        self.nonce = ""

        if not (self.mt.existe_autorizacao_DFE(msg['hdf'], 'hdf')):

            cont = self.ms.leitura(Artefatos.contador)

            self.ms.escrita(Artefatos.contador, cont+1)

            payload = {}

            payload['daf'] = self.ms.leitura(
                Artefatos.IDDAF)
            payload['vsb'] = self.ms.leitura(
                ParametrosAtualizacao.versaoSB)
            payload['mop'] = self.ms.leitura(Artefatos.modoOperacao)
            payload['pdv'] = msg["pdv"]
            payload['cnt'] = self.ms.leitura(Artefatos.contador)

            fragDFE = msg['fdf']
            fragDFE_raw = Base64URLDAF.base64URLDecode(fragDFE)
            cont = self.ms.leitura(Artefatos.contador)

            msg_para_hmac = cont.to_bytes(4,'big') + fragDFE_raw + hashDFE

            chSEF = self.ms.leitura(Artefatos.chaveSEF)
            idAut = CriptoDAF.gera_HMAC_SHA256(
                chSEF, msg_para_hmac)
            idAut = Base64URLDAF.base64URLEncode(idAut)
            payload['aut'] = idAut

            token = JWTDAF.geraJWT(payload, 'HS256', chSEF)

            self.mt.add_autorizacao_DFE(self.ms.leitura(
                Artefatos.IDDAF), self.ms.leitura(Artefatos.modoOperacao), msg['pdv'],  self.ms.leitura(ParametrosAtualizacao.versaoSB), cont, idAut, fragDFE, msg['hdf'])

            NumDFe = self.ms.leitura(Guardas.NumDFe)

            self.ms.escrita(Guardas.NumDFe, NumDFe+1)
            if self.ms.leitura(Guardas.NumDFe) == min(self.ms.leitura(Guardas.MaxDFe),self.ms.leitura(Guardas.MaxDFeModel)):
                # Vai para bloqueado se NumDFe == MaxDFeModel
                self.ms.escrita(
                    Guardas.Estado, Estados.bloqueado.value)

            self.last_msg = 4
            self.operacao = False
            return json.dumps({'res': 0, 'jwt': token},separators=(',', ':'))

        else:
            aut = self.mt.get_autorizacao_DFE(
                msg['hdf'], 'hdf')
            payload = {}

            payload['daf'] = aut['daf']
            payload['vsb'] = aut['vsb']
            payload['mop'] = aut['mop']
            payload['pdv'] = aut['pdv']
            payload['cnt'] = aut['cnt']                      
            payload['aut'] = aut['aut']

            chSEF = self.ms.leitura(Artefatos.chaveSEF)
            token = JWTDAF.geraJWT(payload, 'HS256', chSEF)

            self.last_msg = 4
            self.operacao = False
            return json.dumps({'res': 0, 'jwt': token},separators=(',', ':'))
      

    def __processa_apagarAutorizacaoRetida(self, msg: str) -> str:
        """Método interno para processar o pedido de eliminação de uma autorização retida no DAF 

        Args:
            msg (str): Mensagem JSON recebida pelo DAF

        Returns:
            str: Resposta do DAF ao pedido
        """

        if not self.ms.leitura(Guardas.Estado) == Estados.pronto.value and not self.ms.leitura(Guardas.Estado) == Estados.bloqueado.value:
            return self.__gera_json_resposta_insucesso(Respostas.estadoIncorreto.value)
        
        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
        
        if not self.mt.existe_autorizacao_DFE(msg['aut'], 'aut'):
            return self.__gera_json_resposta_insucesso(                       Respostas.autorizacaoNaoEncontrada.value)
        
        chSEF = self.ms.leitura(Artefatos.chaveSEF)
        
        autApag = Base64URLDAF.base64URLDecode(
            msg['apg'])
        
        if not CriptoDAF.verifica_HMAC_SHA256(chSEF, Base64URLDAF.base64URLDecode(msg["aut"]), autApag):
            return self.__gera_json_resposta_insucesso(                Respostas.hmacNaoCorrespondente.value)

        self.mt.remove_autorizacao_DFE(msg['aut'])
        numDFE = self.ms.leitura(Guardas.NumDFe)
        numDFE = numDFE - 1
        self.ms.escrita(Guardas.NumDFe, numDFE)
        self.ms.escrita(
            Guardas.Estado, Estados.pronto.value)
        self.last_msg = 5

        return json.dumps({"res": 0},separators=(',', ':'))

    def __processa_removerRegistro(self, msg: str) -> str:
        """Método interno para processar o pedido inicial de remoção de registro do DAF 

        Args:
            msg (str): Mensagem JSON recebida pelo DAF

        Returns:
            str: Resposta do DAF ao pedido
        """
        if not self.ms.leitura(Guardas.Estado) == Estados.pronto.value:
            return self.__gera_json_resposta_insucesso(Respostas.estadoIncorreto.value)
        
        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
        
        if not self.ms.leitura(Guardas.NumDFe) == 0:
            return self.__gera_json_resposta_insucesso(                       Respostas.autorizacaoRetida.value)
        
        certificado = self.ms.leitura(Artefatos.certificado)
                    
        payload = JWTDAF.verificaJWT(
            msg['jwt'], certificado.chave_publica, 'ES384')
        
        if not payload:
            return self.__gera_json_resposta_insucesso(Respostas.assinaturaInvalida.value)
        
        if not 'nnc' in payload:
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
            
        payload_r = {}
        payload_r['daf'] = self.ms.leitura(
            Artefatos.IDDAF)
        payload_r['cnt'] = self.ms.leitura(
            Artefatos.contador)
        payload_r['nnc'] = payload['nnc']

        token = JWTDAF.geraJWT(payload_r, 'ES256', self.ms.leitura(Artefatos.chavePrivada))

        self.operacao = True
        self.last_msg = 6
        
        return json.dumps({"res": 0, "jwt": token},separators=(',', ':'))

    def __processa_confirmarRemocaoRegistro(self, msg: str) -> str:
        """Método interno para processar o pedido final de remoção de registro do DAF 

        Args:
            msg (str): Mensagem JSON recebida pelo DAF

        Returns:
            str: Resposta do DAF ao pedido
        """
        if not self.operacao:
            return self.__gera_json_resposta_insucesso(                   Respostas.pedidoMalFormado.value)
        
        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
        
        certificado = self.ms.leitura(
                    Artefatos.certificado)
               
        payload = JWTDAF.verificaJWT(msg['jwt'], certificado.chave_publica, 'ES384')

        if not payload:
            return self.__gera_json_resposta_insucesso(Respostas.assinaturaInvalida.value)
        
        if not 'evn' in payload or not payload['evn'] == 'REMOVER':
            return self.__gera_json_resposta_insucesso(                       Respostas.pedidoMalFormado.value)
        
        self.ms.escrita(Artefatos.chavePrivada, ChaveCripto(""))
        self.ms.escrita(Artefatos.chavePublica,  ChaveCripto(""))
        self.ms.escrita(Artefatos.chaveSEF, "")
        self.ms.escrita(Artefatos.chavePAF, "")
        self.ms.escrita(Guardas.Estado, Estados.inativo.value)
        self.ms.escrita(Guardas.REGOK, False)
        self.operacao = False
        self.last_msg = 7

        return json.dumps({"res": 0},separators=(',', ':'))


    def __processa_consultarInformacoes(self) -> str:
        """Método interno para processar o pedido de consulta de informações do DAF 

        Returns:
            str: Resposta do DAF ao pedido
        """
        if not self.ms.leitura(Guardas.Estado) == Estados.inativo.value and not self.ms.leitura(Guardas.Estado) == Estados.pronto.value and not self.ms.leitura(Guardas.Estado) == Estados.bloqueado.value:
            return self.__gera_json_resposta_insucesso(Respostas.estadoIncorreto.value)

        certificado = Certificado(self.ms.leitura(Artefatos.certificado).certificado_str) 

        res = {}
        res['res'] = 0
        res['daf'] = self.ms.leitura(Artefatos.IDDAF)
        res['mop'] = self.ms.leitura(Artefatos.modoOperacao)
        res['vsb'] = self.ms.leitura(ParametrosAtualizacao.versaoSB)
        res['sig'] = self.ms.leitura(ParametrosAtualizacao.assinaturaSEF)
        res['fab'] = self.ms.leitura(ParametrosAtualizacao.cnpj)
        res['mdl'] = self.ms.leitura(ParametrosAtualizacao.modelo)
        res['cnt'] = self.ms.leitura(Artefatos.contador)     
        res['cfp'] = Base64URLDAF.base64URLEncode(certificado.fingerprint_SHA256)
        res['est'] = self.ms.leitura(Guardas.Estado)
        res["mxd"] = min(self.ms.leitura(Guardas.MaxDFe),self.ms.leitura(Guardas.MaxDFeModel))
        res["ndf"] = self.ms.leitura(Guardas.NumDFe)

        self.last_msg = 8

        return json.dumps(res,separators=(',', ':'))
      
    def __processa_atualizarSB(self) -> str:
        """Método interno para processar o pedido de atualização de SB do DAF 

        Returns:
            str: Resposta do DAF ao pedido
        """
        if not self.ms.leitura(Guardas.Estado) == Estados.inativo.value and not self.ms.leitura(Guardas.Estado) == Estados.pronto.value:
            return self.__gera_json_resposta_insucesso(                Respostas.estadoIncorreto.value)

        if not self.ms.leitura(Guardas.NumDFe) == 0:
            return self.__gera_json_resposta_insucesso(                  Respostas.autorizacaoRetida.value)

        self.atualizacao = True
        self.operacao = True
        self.last_msg = 9
        return json.dumps({"res": 0},separators=(',', ':'))

    def __processa_atualizarCertificado(self, msg: str) -> str:
        """Método interno para processar o pedido de atualização de certificado do DAF 

        Args:
            msg (str): Mensagem JSON recebida pelo DAF

        Returns:
            str: Resposta do DAF ao pedido
        """
        estado_atual = self.ms.leitura(Guardas.Estado)
        if estado_atual not in [Estados.inativo.value, Estados.pronto.value, Estados.bloqueado.value]:
            return self.__gera_json_resposta_insucesso(                Respostas.estadoIncorreto.value)
        
        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)

        certificado = self.ms.leitura(Artefatos.certificado)
        certNovo = Certificado(msg['crt'])
        assinauraSef = msg['sig']


        if not (CriptoDAF.verifica_assinatura_EC_P384(certNovo.conteudo_assinado, certNovo.assinatura, certificado.chave_publica)):
            return self.__gera_json_resposta_insucesso(Respostas.certificadoInvalido.value)

        if not (CriptoDAF.verifica_assinatura_EC_P384(self.imagem_atual.get_assinatura_ateste(), Base64URLDAF.base64URLDecode(assinauraSef), certNovo.chave_publica)):
            return self.__gera_json_resposta_insucesso(Respostas.assinaturaFirmwareInvalida.value)
             
        self.ms.escrita(Artefatos.certificado, certNovo)
        self.ms.escrita(ParametrosAtualizacao.assinaturaSEF, Base64URLDAF.base64URLDecode(assinauraSef))

        return json.dumps({'res': 0},separators=(',', ':'))


    def __processa_descarregarRetidos(self, msg: str) -> str:
        """Método interno para processar o pedido de descarregar autorizações retidas do DAF 

        Args:
            msg (str): Mensagem JSON recebida pelo DAF

        Returns:
            str: Resposta do DAF ao pedido
        """
        if not self.ms.leitura(Guardas.Estado) == Estados.pronto.value and not self.ms.leitura(Guardas.Estado) == Estados.bloqueado.value:
            return self.__gera_json_resposta_insucesso(Respostas.estadoIncorreto.value)
        
        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
        
        idAut = msg['aut']

        if not self.mt.existe_autorizacao_DFE(idAut, 'aut'):
            return self.__gera_json_resposta_insucesso(                       Respostas.autorizacaoNaoEncontrada.value)

        aut = self.mt.get_autorizacao_DFE(idAut, 'aut')

        payload = {}

        payload['daf'] = aut['daf']
        payload['vsb'] = aut['vsb']
        payload['mop'] = aut['mop']
        payload['pdv'] = aut['pdv']
        payload['cnt'] = aut['cnt']                      
        payload['aut'] = aut['aut']

        chSEF = self.ms.leitura(Artefatos.chaveSEF)
        token = JWTDAF.geraJWT(payload, 'HS256', chSEF)

        res = {}
        res['res'] = 0
        res['jwt'] = token
        res['fdf'] = aut['fdf']
        res['hdf'] = aut['hdf']
        self.last_msg = 11
        return json.dumps(res,separators=(',', ':'))
         

    def __processa_alterarModoOperacao(self, msg: str) -> str:
        """Método interno para processar o pedido de alterar modo de operação

        Args:
            msg (str): Mensagem JSON recebida pelo DAF

        Returns:
            str: Resposta do DAF ao pedido
        """
        if not self.ms.leitura(Guardas.Estado) == Estados.pronto.value:
            return self.__gera_json_resposta_insucesso(Respostas.estadoIncorreto.value)
        
        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
            
        if not self.ms.leitura(Guardas.NumDFe) == 0:
            return self.__gera_json_resposta_insucesso(Respostas.autorizacaoRetida.value)
        
        chSEF = self.ms.leitura(Artefatos.chaveSEF)
        payload = JWTDAF.verificaJWT(msg["jwt"],chSEF,'HS256')

        if not payload:
            return self.__gera_json_resposta_insucesso(Respostas.hmacNaoCorrespondente.value)

        if  not 'nnc' in payload or not (len(payload)) == 1:
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)

        payload_dic = {}
        payload_dic["daf"] = self.ms.leitura(Artefatos.IDDAF)
        payload_dic["cnt"] = self.ms.leitura(Artefatos.contador)
        payload_dic["nnc"] = payload["nnc"]

        token = JWTDAF.geraJWT(payload_dic, 'HS256', chSEF)
        self.operacao = True
        self.last_msg = 12

        return json.dumps({'res': 0, 'jwt': token}, separators=(',', ':'))

       
    def __processa_confirmarAlterarModoOperacao(self, msg:str) ->str:
        """Método interno para processar o pedido de confirmar alteração do modo de operação

        Args:
            msg (str): Mensagem JSON recebida pelo DAF

        Returns:
            str: Resposta do DAF ao pedido
        """
        if not self.operacao == True:
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
        
        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
        
        chSEF = self.ms.leitura(Artefatos.chaveSEF)
        payload = JWTDAF.verificaJWT(msg["jwt"],chSEF,'HS256')
        
        if not payload:
            return self.__gera_json_resposta_insucesso(Respostas.hmacNaoCorrespondente.value)

        if not 'mop' in payload or not (len(payload)) == 1 or not isinstance(payload['mop'], int):
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
        
        if not payload["mop"] == 0 and not payload["mop"] == 1:
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado)

        self.ms.escrita(Artefatos.modoOperacao, payload["mop"])
        self.operacao = False
        self.last_msg = 13
        
        return json.dumps({'res': 0},separators=(',', ':'))
        
    def __processa_cancelarProcesso(self) -> str:
        """Método interno para processar o pedido de cancelamento de um processo iniciado pelo DAF 

        Returns:
            str: Resposta do DAF ao pedido
        """
        if not self.ms.leitura(Guardas.Estado) == Estados.inativo.value and not self.ms.leitura(Guardas.Estado) == Estados.pronto.value:
            return self.__gera_json_resposta_insucesso(Respostas.estadoIncorreto.value)
        
        self.operacao = False
        self.nonce = None
        self.last_msg = 14
        self.disable_timeout()
    
        return json.dumps({"res": 0},separators=(',', ':'))
    
    def __processa_obterImpressaoDigital(self, msg:str) -> str:
        """Método interno para processar o pedido de obter a impressão digital do certificado digital da SEF

        Returns:
            str: Resposta do DAF ao pedido
        """
        if not self.ms.leitura(Guardas.Estado) == Estados.pronto.value and not self.ms.leitura(Guardas.Estado) == Estados.bloqueado.value:
          return self.__gera_json_resposta_insucesso(Respostas.estadoIncorreto.value)

        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
        
        payload = {} 
        certificado = Certificado(self.ms.leitura(Artefatos.certificado).certificado_str) 
        
        payload['daf'] = self.ms.leitura(
            Artefatos.IDDAF)
        payload['cfp'] = Base64URLDAF.base64URLEncode(certificado.fingerprint_SHA256)
        chSEF = self.ms.leitura(Artefatos.chaveSEF)
        
        token = JWTDAF.geraJWT(payload, 'HS256', chSEF)
        
        self.last_msg = 15
        self.operacao = False
        return json.dumps({'res': 0, 'jwt': token},separators=(',', ':'))
    
    def __processa_consultarAutorizacoes(self, msg:str) -> str:
        """Método interno para processar o pedido de consultar autorizações do DAF
         
        Args:
            msg (str): Mensagem JSON recebida pelo DAF
            
        Returns:
            str: Resposta do DAF ao pedido
        """
        if not self.ms.leitura(Guardas.Estado) == Estados.pronto.value and not self.ms.leitura(Guardas.Estado) == Estados.bloqueado.value:
          return self.__gera_json_resposta_insucesso(Respostas.estadoIncorreto.value)

        if not self.__valida_mensagem(msg):
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)
 
        if not msg['ini'] > 0:
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value)      
        
        if not msg['ini'] <= msg['fim']:
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value) 
        
        if not msg['fim'] <= self.ms.leitura(Guardas.NumDFe):
            return self.__gera_json_resposta_insucesso(Respostas.pedidoMalFormado.value) 
        
        res = {}
        autorizacoes = self.mt.get_autorizacoes_DFE()
        vetorIdAut = []
                
        for autorizacao in autorizacoes[msg['ini']-1:msg['fim']]:
            vetorIdAut.append(autorizacao['aut'])

        res['res'] = 0
        res['rts'] = vetorIdAut
        self.operacao = False
        self.last_msg = 16
        return json.dumps(res,separators=(',', ':'))

    def __gera_json_resposta_insucesso(self, res: int) -> str:
        """ Método interno para geração de respostas de insucesso do DAF

        Args:
            res (int): Código da resposta

        Returns:
            str: Resposta do DAF
        """
        self.last_msg = None
        resposta = {'res': res}
        self.disable_timeout()
        return json.dumps(resposta,separators=(',', ':'))

    def atualizar_sb(self, novaImagem:bytes) -> str:
        """ Método para "atualizar" o "SB" do DAF

        Args:
            novaImagem (bytes): código da nova imagem recebido via USB

        Returns:
            str: Resultado da atualização
        """
        certificado = self.ms.leitura(Artefatos.certificado)
        ateste = self.ms.leitura(Artefatos.chaveAtestePublica)
        imagem_candidata = ImagemSBCandidato(novaImagem)
        resposta = None
        if (self.ms.leitura(ParametrosAtualizacao.falhasAtualizacao) <= 10 and not self.esta_violado()):
            if self.ms.leitura(Guardas.NumDFe) > 0:
                resposta = self.__gera_json_resposta_insucesso(
                    Respostas.autorizacaoRetida.value)
            else:
                resultado = self.imagem_atual.atualizar(imagem_candidata, certificado, ateste)

                if resultado == 3:
                    resposta = self.__gera_json_resposta_insucesso(
                        Respostas.assinaturaFirmwareInvalida.value)
                    numAtualizacoes = self.ms.leitura(ParametrosAtualizacao.falhasAtualizacao)
                    self.ms.escrita(ParametrosAtualizacao.falhasAtualizacao, numAtualizacoes+1)
                elif resultado == 8:
                    
                    
                    resposta = self.__gera_json_resposta_insucesso(
                        Respostas.versaoSBInvalida.value)
                    numAtualizacoes = self.ms.leitura(ParametrosAtualizacao.falhasAtualizacao)
                    self.ms.escrita(ParametrosAtualizacao.falhasAtualizacao, 
                    numAtualizacoes+1)                 
                    
                elif resultado == 9:
                    resposta = self.__gera_json_resposta_insucesso(Respostas.modeloInvalido.value)
                    numAtualizacoes = self.ms.leitura(ParametrosAtualizacao.falhasAtualizacao)
                    self.ms.escrita(ParametrosAtualizacao.falhasAtualizacao, numAtualizacoes+1)
                else:
                    self.ms.escrita(ParametrosAtualizacao.assinaturaSEF,
                                    imagem_candidata.get_assinatura())
                    self.ms.escrita(ParametrosAtualizacao.versaoSB,imagem_candidata.get_versao_SB().hex())                                    
                    resposta = {'res': 0}
                    resposta = json.dumps(resposta,separators=(',', ':'))
                   
                    self.ms.escrita(ParametrosAtualizacao.falhasAtualizacao, 0)
                    self.last_msg = None
                    self.disable_timeout()
            if self.ms.leitura(ParametrosAtualizacao.falhasAtualizacao) <= 10:
                return resposta
            else:
                self.ms.escrita(Guardas.Violado, True)
                return self.modo_inutilizado()
        else:
            self.ms.escrita(Guardas.Violado, True)
            return self.modo_inutilizado()


    def esta_violado(self) -> bool:
        """ Método para verificar se o DAF está violado

        Returns:
            bool: Resultado da verificação. True se o DAF está violado
        """
        violado = self.ms.leitura(Guardas.Violado)
        return violado

    def modo_inutilizado(self) -> str:
        """ Método para simular o comportamento do modo inutilizado do DAF

        Returns:
            str: dados que o DAF deve fornecer ao PAF quando no modo inutilizado
        """
        self.ms.escrita(Guardas.Violado, True)
        self.ms.escrita(Guardas.Estado, Estados.inutilizado.value)

        # Retorna as informações com exceção de:
        # - Conteúdo da partição do SB
        # - Conteúdo da MT
        MaxDFeModel = self.ms.leitura(Guardas.MaxDFeModel)
        maxDFe = self.ms.leitura(Guardas.MaxDFe)
        regOK = self.ms.leitura(Guardas.REGOK)
        numDfe = self.ms.leitura(Guardas.NumDFe)
        contador = self.ms.leitura(Artefatos.contador)
        iddaf = self.ms.leitura(Artefatos.IDDAF)
        mop = self.ms.leitura(Artefatos.modoOperacao)
        resumo = self.ms.leitura(ParametrosAtualizacao.assinaturaSEF)
        versao = self.ms.leitura(ParametrosAtualizacao.versaoSB)
        numAtualizacoes = self.ms.leitura(ParametrosAtualizacao.falhasAtualizacao)
        cnpj = self.ms.leitura(ParametrosAtualizacao.cnpj)
        modelo = self.ms.leitura(ParametrosAtualizacao.modelo)

        data = str(MaxDFeModel) + '|' + str(maxDFe) + '|' + str(int(regOK)) + str(numDfe) + '|' + str(contador) + '|' + iddaf.encode('utf-8').hex() + '|' + str(mop) + '|' + resumo.encode('utf-8').hex() + '|' + str(versao) + '|' + str(numAtualizacoes) + '|' + cnpj + '|' + modelo

        return data

    def notifica(self, comando, dados):
        """
            Recebe a mensagem da camada de garantia de entrega

            comando(bytes): Campo tipo
            dados(bytes): Objeto JSON com mensagem do PAF ou binário do novo SB
        """
        if comando == b'\x01':
            resposta = self.processa_pedido(dados)
            if resposta is not None:
                self.inferior.envia(bytearray(resposta.encode()), TIPO_t.ENVIARMSG.value)
        else:
            resposta = self.atualizar_sb(dados)
            if resposta is not None:
                self.inferior.envia(bytearray(resposta.encode()), TIPO_t.ENVIARMSG.value)

    def handle_timeout(self):
        self.__processa_cancelarProcesso()

    def recarrega_timeout(self, timeout:int):
        """ Define um novo valor de timeout e o recarrega

        Args:
            timeout (int): tempo de espera.
        """
        self.timeout = timeout
        self.enable_timeout()
        self.reload_timeout()
