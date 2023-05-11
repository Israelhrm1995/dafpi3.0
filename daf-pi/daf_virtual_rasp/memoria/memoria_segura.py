from daf_virtual_rasp.daf.daf_enums import Guardas, Artefatos, ParametrosAtualizacao, Estados
from daf_virtual_rasp.utils.cripto_daf import CriptoDAF, Certificado, ChaveCripto
from tinydb import TinyDB, Query
from typing import Union
import os
import json
from daf_virtual_rasp.imagem import ImagemSB
from daf_virtual_rasp.utils.base64URL_daf import Base64URLDAF
import uuid

class MemoriaSegura:

    def __init__(self, path_ms: str = './ms.json'):
        """ Classe para iniciar um banco de dados com a classe
        TinyDB

        Args:
            path_ms (str, optional): caminho para o arquivo .json que representa o banco. Defaults to './ms.json'.
        """
       
        self.arquivo = path_ms
        
        # cria pasta se não existe ainda
        dirname = os.path.dirname(self.arquivo)
        
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        self.banco = TinyDB(self.arquivo)
        self.query = Query()
     
       
        with open('daf_virtual_rasp/resources/sef-cert-ec.pem') as file:
            cer = file.read()

        with open('daf_virtual_rasp/resources/ateste-priv-ec.pem') as file:
            ateste = file.read()
        
        with open('daf_virtual_rasp/resources/ateste-pub-ec.pem') as file:
            ateste_pub = file.read()
        
        modelo = 'daf-pi'


        imagem = ImagemSB(path_arquivos='./daf_virtual_rasp/resources/imagem/sb')
        
        ateste = ChaveCripto(ateste)
        ateste_pub = ChaveCripto(ateste_pub)
        versao = imagem.get_versao_SB().hex()
        assinaturaSEF = imagem.get_assinatura()
       
        daf_info = {
            Guardas.MaxDFe.value: 1000,
            Guardas.REGOK.value: False,
            Guardas.NumDFe.value: 0,
            Guardas.MaxDFeModel.value: 1000,
            Guardas.Violado.value: False,
            Guardas.Estado.value: Estados.inativo.value,
            Artefatos.certificado.value: cer,
            Artefatos.chaveAteste.value: ateste.chave_str,
            Artefatos.chaveAtestePublica.value: ateste_pub.chave_str,
            Artefatos.chavePrivada.value: "",
            Artefatos.chavePublica.value: "",
            Artefatos.chaveSEF.value: "",
            Artefatos.chavePAF.value: "",
            Artefatos.contador.value: 0,
            Artefatos.IDDAF.value: Base64URLDAF.base64URLEncode(uuid.uuid4().bytes),
            Artefatos.modoOperacao.value: 0,
            ParametrosAtualizacao.modelo.value: modelo,
            ParametrosAtualizacao.cnpj.value: "86096781000185",
            ParametrosAtualizacao.versaoSB.value: versao,
            ParametrosAtualizacao.assinaturaSEF.value: Base64URLDAF.base64URLEncode(assinaturaSEF),
            ParametrosAtualizacao.falhasAtualizacao.value: 0
        }
        self.iniciaBanco(daf_info)

    def __del__(self):
        self.banco.close()

    def iniciaBanco(self, dic: dict) -> bool:
        """ Método para iniciar o banco de dados

        Args:
            dic (dict): Dicionário python com as chaves e valores iniciais do banco

        Returns:
            bool: Sucesso ou falha na criação
        """
        data = self.banco.all()

        if len(data) == 0:
            try:
                self.banco.insert(dic)
                return True
            except:
                return False

    def reinicia_memoria(self) -> bool:
        """ Método para reiniciar o banco

        Returns:
            bool: Sucesso ou falha na operação
        """
       
        iddaf = self.leitura(Artefatos.IDDAF)
        self.banco.truncate()
        
        if not iddaf:
            iddaf = Base64URLDAF.base64URLEncode(uuid.uuid4().bytes)


        with open('daf_virtual_rasp/resources/sef-cert-ec.pem') as file:
            cer = file.read()

        with open('daf_virtual_rasp/resources/ateste-priv-ec.pem') as file:
            ateste = file.read()
        
        with open('daf_virtual_rasp/resources/ateste-pub-ec.pem') as file:
            ateste_pub = file.read()
        
        modelo = 'daf-pi'


        imagem = ImagemSB(path_arquivos='./daf_virtual_rasp/resources/imagem/sb')
        
        ateste = ChaveCripto(ateste)
        ateste_pub = ChaveCripto(ateste_pub)
        versao = imagem.get_versao_SB().hex()
        assinaturaSEF = imagem.get_assinatura()
       
        daf_info = {
            Guardas.MaxDFe.value: 1000,
            Guardas.REGOK.value: False,
            Guardas.NumDFe.value: 0,
            Guardas.MaxDFeModel.value: 1000,
            Guardas.Violado.value: False,
            Guardas.Estado.value: Estados.inativo.value,
            Artefatos.certificado.value: cer,
            Artefatos.chaveAteste.value: ateste.chave_str,
            Artefatos.chaveAtestePublica.value: ateste_pub.chave_str,
            Artefatos.chavePrivada.value: "",
            Artefatos.chavePublica.value: "",
            Artefatos.chaveSEF.value: "",
            Artefatos.chavePAF.value: "",
            Artefatos.contador.value: 0,
            Artefatos.IDDAF.value: iddaf,
            Artefatos.modoOperacao.value :0,
            ParametrosAtualizacao.modelo.value: modelo,
            ParametrosAtualizacao.cnpj.value: "86096781000185",
            ParametrosAtualizacao.versaoSB.value: versao,
            ParametrosAtualizacao.assinaturaSEF.value: Base64URLDAF.base64URLEncode(assinaturaSEF),
            ParametrosAtualizacao.falhasAtualizacao.value: 0
        }

        return self.iniciaBanco(daf_info)

    def leitura(self, obj: Union[Artefatos, Guardas, ParametrosAtualizacao]) -> Union[Certificado, ChaveCripto, bytes, str]:
        """ Método para fazer a leitura de uma informação armazenada no banco

        Args:
            obj (Union[Artefatos, Guardas, ParametrosAtualizacao]): Informação a ser lida no banco. 

        Returns:
            Union[Certificado, ChaveCripto, bytes]: Informação obtida do banco
        """
        banco_inteiro = self.banco.all()
        if obj == Artefatos.certificado:
            return Certificado(banco_inteiro[0][obj.value])

        if obj == Artefatos.chavePrivada or obj == Artefatos.chavePublica or obj == Artefatos.chaveAteste or obj == Artefatos.chaveAtestePublica:
            return ChaveCripto(banco_inteiro[0][obj.value])

        if obj == Artefatos.chaveSEF or obj == Artefatos.chavePAF:
            return bytes.fromhex(banco_inteiro[0][obj.value])
        if obj == ParametrosAtualizacao.versaoSB:
            return int(banco_inteiro[0][obj.value],16)
        if obj == ParametrosAtualizacao.assinaturaSEF:
            return str(banco_inteiro[0][obj.value])
        return banco_inteiro[0][obj.value]

    def escrita(self, obj: Union[Artefatos, Guardas, ParametrosAtualizacao], valor: Union[int, str, bool, bytes, Certificado, ChaveCripto]) -> bool:
        """ Método para armazenar/atualizar uma informação do banco

        Args:
            obj (Union[Artefatos, Guardas, ParametrosAtualizacao]): Informação a ser alterada
            valor (Union[int, str, bool, bytes]): Valor da informação

        Returns:
            bool: Sucesso ou falha na operação
        """
        if isinstance(obj, Artefatos):
            if obj == Artefatos.certificado:
                if isinstance(valor, Certificado):
                    try:
                        self.banco.update({obj.value: valor.certificado_str})
                        return True
                    except:
                        return False
                else:
                    return False
            elif obj == Artefatos.IDDAF:
                if isinstance(valor, str):
                    try:
                        self.banco.update({obj.value: valor})
                        return True
                    except:
                        return False
                else:
                    return False
            elif obj == Artefatos.chavePrivada or obj == Artefatos.chavePublica:
                if isinstance(valor, ChaveCripto):
                    try:
                        self.banco.update({obj.value: valor.chave_str})
                        return True
                    except:
                        return False
                else:
                    return False

            elif obj == Artefatos.chavePAF or obj == Artefatos.chaveSEF:
                if isinstance(valor, bytes):
                    try:
                        self.banco.update({obj.value: valor.hex()})
                        return True
                    except:
                        return False
                else:
                    return False
            elif obj == Artefatos.contador or obj == Artefatos.modoOperacao:
                if isinstance(valor, int):
                    try:
                        self.banco.update({obj.value: valor})
                        return True
                    except:
                        return False
                else:
                    return False
            else:
                return False
        elif isinstance(obj, Guardas):
            if obj == Guardas.Estado:
                if isinstance(valor, str):
                    try:
                        self.banco.update({obj.value: valor})
                        return True
                    except:
                        return False
                else:
                    return False
            elif obj == Guardas.MaxDFe or obj == Guardas.NumDFe or obj == Guardas.MaxDFeModel:
                if isinstance(valor, int):
                    try:
                        self.banco.update({obj.value: valor})
                        return True
                    except:
                        return False
                else:
                    return False
            else:
                if isinstance(valor, bool):
                    try:
                        self.banco.update({obj.value: valor})
                        return True
                    except:
                        return False
                else:
                    return False
        elif isinstance(obj, ParametrosAtualizacao):
            if obj == ParametrosAtualizacao.versaoSB:
                if isinstance(valor, str):
                    try:
                        self.banco.update({obj.value: valor})
                        return True
                    except:
                        return False
                else:
                    return False
            elif obj == ParametrosAtualizacao.assinaturaSEF:
                if isinstance(valor, bytes):
                    try:
                        self.banco.update({obj.value: Base64URLDAF.base64URLEncode(valor)})
                        return True
                    except:
                        return False
                else:
                    return False
            elif obj == ParametrosAtualizacao.falhasAtualizacao:
                if isinstance(valor, int):
                    try:
                        self.banco.update({obj.value: valor})
                        return True
                    except:
                        return False
                else:
                    return False
        else:
            return False
