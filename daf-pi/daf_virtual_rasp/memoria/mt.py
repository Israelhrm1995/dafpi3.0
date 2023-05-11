from typing import Dict, List, Union
from tinydb import TinyDB, Query
import os

from daf_virtual_rasp.utils.base64URL_daf import Base64URLDAF

class MemoriaDeTrabalho:
    """Classe que deve ser usada para gerenciar as autorizações de DFes na memória do DAF Virtual.
    """

    def __init__(self, arquivo : str = './mt.json'):
        """Inicializa a memória de trabalho, criando arquivo do banco de dados caso não exista.

        Args:
            arquivo (str, optional): Nome do arquivo onde será salvo o banco de dados. Defaults to './mt.json'.
        """
        self.arquivo = arquivo

        # cria pasta se não existe ainda
        dirname = os.path.dirname(self.arquivo)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        self.banco = TinyDB(self.arquivo)
        self.query = Query()

    def __del__(self):

        self.banco.close()

    def existe_autorizacao_DFE(self, info : str, campo : str) -> bool:
        """Verifica se existe autorização na memória de trabalho (MT)

        Args:
            info (str): conteúdo da informação que deve ser verificada.
            campo (str): o campo que deve ser usado para verificar a info

        Returns:
            bool: existe a autorização?
        """
        busca = self.query[campo]
        
        result = self.banco.search(busca == info)

        if len(result) == 1:
            return True
        else:
            return False
            
    def remove_autorizacao_DFE(self, idAut : str) -> bool:
        """ Remove uma autorização do banco

        Args:
            idAut (str): Identificador da autorização

        Returns:
            bool: Resultado do processo
        """
        
        result = self.banco.remove(self.query.aut == idAut)

        if len(result) == 1:
            return True
        else:
            return False

    def get_numero_de_autorizacoes_DFE(self) -> int:
        return len(self.banco.all())
    
    def add_autorizacao_DFE(self, idDAF : str, mop:int, pdv:str,versaoSB : str, cont : int, idAut : str, fragDFE : str, hashDFE : str) -> bool:
        """ Adiciona uma autorização no banco

        Args:
            idDAF (str): identificador único do daf
            versaoSB (str): versão do SB
            cont (int): valor do contador
            idAut (str): Identificador da autorização
            fragDFE (str): Fragmento com informações essenciais do DFe
            hashDFE (str): Resumo do DFe

        Returns:
            bool: resultado do processo
        """

        documento = {
            "daf"        : idDAF,
            "vsb"     : versaoSB,
            "mop"          : mop,
            "pdv"          : pdv,
            "cnt"         : cont,
            "aut"        : idAut,
            "fdf"      : fragDFE,
            "hdf"      : hashDFE
        }

        # verifica se existe autorizacao com mesmo idAut, cont ou hash
        result = self.banco.search((self.query.idAut == documento['aut']) | (self.query.cont == documento['cnt']) | (self.query.hashDFE == documento['hdf']))

        # se existir, nao adiciona autorizacao!
        if len(result) > 0:
            return False

        self.banco.insert(documento)
        return True

    def get_autorizacoes_DFE(self) -> list:
        """ Método para obter todas as autorizações gravadas

        Returns:
            list: Autorizações
        """

        autorizacoes = self.banco.all()

        return autorizacoes

    def get_autorizacao_DFE(self, info : str, campo:str ) -> Union[dict, None]:
        """ Método para obter autorização
        
        Args:
            info (str): conteúdo da informação que deve ser verificada.
            campo (str): o campo que deve ser usado para verificar a info

        Returns:
            Union[dict, None]: autorização
        """
        busca = self.query[campo]

        result = self.banco.search(busca == info)

        if len(result) == 0:
            return None

        return result[0]
    
    def reinicia_memoria(self):
        self.banco.truncate()