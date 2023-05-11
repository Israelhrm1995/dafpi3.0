import typing
import os
from daf_virtual_rasp.utils.cripto_daf import ChaveCripto, CriptoDAF
from daf_virtual_rasp.daf.daf_enums import Artefatos
from daf_virtual_rasp.utils.base64URL_daf import Base64URLDAF

class ImagemSB:

    # todos tamanhos em bytes
    VERSAO_TAMANHO = 2
    MAXDFE_TAMANHO = 2
    HASH_TAMANHO = 32  # 256 bits
    ASSINATURA_TAMANHO = 103 #102
    ASSINATURA_ATESTE_TAMANHO = 103 #103
    CODIGO_TAMANHO = 2048 

    def __init__(self, raw_binario: bytes = b'', path_arquivos: str = './daf_virtual_rasp/resources/imagem/sb'):
        """Inicialização da imagem do SB.

        Args:
            raw_binario (bytes, optional): Preencher com a imagem caso deseja-se inserir uma nova imagem na partição do SB. Defaults to b''.
            path_arquivos (str, optional): Local da partição, isto é, onde a imagem será salva. Defaults to './daf_virtual_rasp/resources/imagem/sb'.

        Raises:
            ValueError: Se a partição do SB estiver vazia e o parâmetro raw_binario não for especificado. Teoricamente, essa partição não deve estar vazia em nenhuma situação, pois o SB é inserido em tempo de manufatura e depois disso essa partição ou é apenas atualizada/sobreescrita.
        """

        self.path_arquivos = path_arquivos

        # cria pasta se nao existe ainda
        if not os.path.isdir(self.path_arquivos):
            os.makedirs(self.path_arquivos)

        if len(raw_binario) == 0:
            # então a imagem já foi adicionada anteriormente
            
            if self.particao_vazia() == True:
                raise ValueError(
                    "Partição está vázia e parâmetro raw_binario está vázio.")

        else:
            # imagem sendo adicionada agora

            versao = self._extrai_versao(raw_binario)
            print("Versão recebida: " ,int.from_bytes(versao,byteorder='big'), "\n")
            maxdfe = self._extrai_maxdfe(raw_binario)
            hash = self._extrai_hash(raw_binario)
            assinatura = self._extrai_assinatura(raw_binario)
            assinatura_ateste = self._extrai_assinatura_ateste(raw_binario)
            codigo = self._extrai_codigo(raw_binario)

            self._set_versao(versao)
            self._set_maxdfe(maxdfe)
            self._set_hash(hash)
            self._set_assinatura(assinatura)
            self._set_assinatura_ateste(assinatura_ateste)
            self._set_codigo(codigo)

    # extração de campos da imagem cru

    def _extrai_versao(self, raw_binario: bytes) -> bytes:
        offset = 0
        return raw_binario[offset: offset + self.VERSAO_TAMANHO]

    def _extrai_maxdfe(self, raw_binario: bytes) -> bytes:
        offset = self.VERSAO_TAMANHO
        return raw_binario[offset: offset + self.MAXDFE_TAMANHO]

    def _extrai_hash(self, raw_binario: bytes) -> bytes:
        offset = self.VERSAO_TAMANHO + self.MAXDFE_TAMANHO
        return raw_binario[offset: offset + self.HASH_TAMANHO]

    def _extrai_assinatura(self, raw_binario: bytes) -> bytes:
        offset = self.VERSAO_TAMANHO + self.MAXDFE_TAMANHO + self.HASH_TAMANHO 
        return raw_binario[offset: offset + self.ASSINATURA_TAMANHO]

    def _extrai_assinatura_ateste(self, raw_binario: bytes) -> bytes:
        offset = self.VERSAO_TAMANHO + self.MAXDFE_TAMANHO + self.HASH_TAMANHO + self.ASSINATURA_TAMANHO 
        return raw_binario[offset: offset + self.ASSINATURA_ATESTE_TAMANHO]

    def _extrai_codigo(self, raw_binario: bytes) -> bytes:
        offset = self.VERSAO_TAMANHO + self.MAXDFE_TAMANHO + self.HASH_TAMANHO + self.ASSINATURA_TAMANHO + self.ASSINATURA_ATESTE_TAMANHO 
        return raw_binario[offset:]

    # get/set versao

    def _arquivo_versao(self) -> str:
        return f"{self.path_arquivos}/versao.str"

    def _set_versao(self, versao: bytes) -> None:
        with open(self._arquivo_versao(), "wb") as arquivo:
            arquivo.write(versao)

    def get_versao_SB(self) -> bytes:
        with open(self._arquivo_versao(), "rb") as arquivo:
            versao = arquivo.read()
        return versao

    # get/set maxfde

    def _arquivo_maxdfe(self) -> str:
        return f"{self.path_arquivos}/maxdfe.str"

    def _set_maxdfe(self, maxdfe: bytes) -> None:
        with open(self._arquivo_maxdfe(), "wb") as arquivo:
            arquivo.write(maxdfe)

    def get_maxdfe(self) -> bytes:
        with open(self._arquivo_maxdfe(), "rb") as arquivo:
            maxdfe = arquivo.read()
        return maxdfe        

    # get/set hash

    def _arquivo_hash(self) -> str:
        return f"{self.path_arquivos}/hash.bin"

    def _set_hash(self, hash: bytes) -> None:
        with open(self._arquivo_hash(), "wb") as arquivo:
            arquivo.write(hash)

    def get_hash_SB(self) -> bytes:
        with open(self._arquivo_hash(), "rb") as arquivo:
            hash = arquivo.read()
        return hash

    # get/set assinatura

    def _arquivo_assinatura(self) -> str:
        return f"{self.path_arquivos}/assinatura.bin"

    def _set_assinatura(self, assinatura: bytes) -> None:
        with open(self._arquivo_assinatura(), "wb") as arquivo:
            arquivo.write(assinatura)

    def get_assinatura(self) -> bytes:
        with open(self._arquivo_assinatura(), "rb") as arquivo:
            assinatura = arquivo.read()
        return assinatura

    # get/set assinatura ateste

    def _arquivo_assinatura_ateste(self)-> str:
        return f"{self.path_arquivos}/assinatura_ateste.bin"

    def _set_assinatura_ateste(self, assinatura: bytes)-> None:
        with open(self._arquivo_assinatura_ateste(), "wb") as arquivo:
            arquivo.write(assinatura)
    
    def get_assinatura_ateste(self)->bytes:
        with open(self._arquivo_assinatura_ateste(), "rb") as arquivo:
            assinatura = arquivo.read()
        return assinatura

    # get/set codigo

    def _arquivo_codigo(self) -> str:
        return f"{self.path_arquivos}/codigo.bin"

    def _set_codigo(self, codigo: bytes) -> None:
        with open(self._arquivo_codigo(), "wb") as arquivo:
            arquivo.write(codigo)

    def get_codigo(self) -> bytes:
        
        with open(self._arquivo_codigo(), "rb") as arquivo:
            codigo = arquivo.read()
        
        return codigo

    # particao

    def remove_particao(self) -> None:
        os.remove(self._arquivo_codigo())

    def particao_vazia(self) -> bool:
        particaoExiste = os.path.isfile(self._arquivo_codigo())
        return not particaoExiste

    # verificacoes

    def esta_integro(self) -> bool:
        res = CriptoDAF.verifica_resumo_SHA256((self.get_versao_SB()+self.get_codigo()+self.get_maxdfe()) ,self.get_hash_SB())
        return res

    def esta_autentico(self, certificado) -> bool:
        msg = self.get_assinatura_ateste()
        return CriptoDAF.verifica_assinatura_EC_P384(msg, self.get_assinatura(), certificado.chave_publica)

    def esta_autentico_ateste(self, chave) ->bool:       
        msg = self.get_hash_SB()
        return CriptoDAF.verifica_assinatura_EC_P384(msg, self.get_assinatura_ateste(), chave)

    # ---

    def atualizar(self, novaImagem: 'ImagemSB', certificado, ateste) -> int:
      
        if not novaImagem.esta_integro() or not novaImagem.esta_autentico(certificado):
            return 3

        if not novaImagem.esta_autentico_ateste(ateste):
            return 9
     
        elif novaImagem.get_versao_SB() <= self.get_versao_SB():
            return 8

        # Deixar comentado para não fazer a alteração da imagem, apenas fazer as validações. 
        # Caso atualize, pode usar a imagem imagem-default que está no resources pra voltar para versão 2

        # self._set_versao(novaImagem.get_versao_SB())
        # self._set_maxdfe(novaImagem.get_maxdfe())
        # self._set_hash(novaImagem.get_hash_SB())
        # self._set_assinatura(novaImagem.get_assinatura())
        # self._set_assinatura_ateste(novaImagem.get_assinatura_ateste())
        # self._set_codigo(novaImagem.get_codigo())

        return 0


class ImagemSBCandidato(ImagemSB):

    def __init__(self, raw_binario: bytes = b'', pathArquivos: str = './daf_virtual_rasp/resources/outra-imagem/sb'):

        super().__init__(raw_binario, pathArquivos)
