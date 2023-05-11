from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from typing import Tuple
import random
import hmac
import hashlib


class ChaveCripto():

    def __init__(self, chave: str):
        """ Encapsula uma chave criptográfica

        Args:
            chave (str): chave criptográfica na forma de string
        """
        self.chave_str = chave
        self.chave_bytes = chave.encode('utf-8')


class Certificado():


    def __init__(self, cert: str):
        """ Encapsula um certificado

        Args:
            cert (str): certificado na forma de string
        """
        certificado_x509 = x509.load_pem_x509_certificate(cert.encode('utf-8'))

        self.assinatura = certificado_x509.signature

        self.chave_publica = ChaveCripto(certificado_x509.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8'))

        self.certificado_str = cert
        self.certificado_bytes = certificado_x509.public_bytes(
            serialization.Encoding.PEM)
        self.conteudo_assinado = certificado_x509.tbs_certificate_bytes

        self.fingerprint_SHA256 = certificado_x509.fingerprint(hashes.SHA256())


class CriptoDAF:
    ''' 
        Classe para operações criptográficas do DAF Virtual
    '''

    def __init__(self):
        pass

    @staticmethod
    def gera_chave_RSA(len: int) -> Tuple[ChaveCripto, ChaveCripto]:
        """ Método para geração de chaves RSA

        Args:
            len (int): Tamanho da chave

        Returns:
            Tuple[ChaveCripto,ChaveCripto]: Chave privada e chave pública 
        """
        key = RSA.generate(len)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        private_key = ChaveCripto(private_key.decode('utf-8'))
        public_key = ChaveCripto(public_key.decode('utf-8'))

        return private_key, public_key

    @staticmethod
    def gera_chave_EC_p256():
        private_key = ec.generate_private_key(ec.SECP256R1)
        public_key = private_key.public_key()
        private_key = private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption())

        public_key = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)

        private_key = ChaveCripto(private_key.decode('utf-8'))
        public_key = ChaveCripto(public_key.decode('utf-8'))
        return private_key, public_key

    @staticmethod
    def gera_assinatura_RSA_PKCS1_V1_5(msg: bytes, privkey: ChaveCripto) -> bytes:
        """ Método para geração de assinatura digital com o esquema PKCS1-v1_5 (RFC 8017)

        Args:
            msg (bytes): Mensagem a ser assinada
            privkey (bytes): Chave privada (PEM)

        Returns:
            bytes: Assinatura digital
        """
        key = RSA.import_key(privkey.chave_bytes)
        hashed = SHA256.new(msg)
        return PKCS1_v1_5.pkcs1_15.new(key).sign(hashed)

    @staticmethod
    def verifica_assinatura_EC_P384(msg:bytes, sig:bytes, pubkey:ChaveCripto) -> bool:
        """ Método para verificação de assinatura digital com chaves EC P-384

        Args:
            msg (bytes): Mensagem que foi assinada
            sig (bytes): Assinatura digital
            pubkey (bytes): Chave pública par da chave privada que gerou a assinatura (PEM)

        Returns:
            bool: Sucesso ou falha na verificação
        """

        try:
            pubkey = serialization.load_pem_public_key(pubkey.chave_bytes)
            pubkey.verify(sig, msg, ec.ECDSA(hashes.SHA384()))
            return True
        except:
            return False


    @staticmethod
    def verifica_assinatura_RSA_PKCS1_V1_5(msg: bytes, sig: bytes, pubkey: ChaveCripto) -> bool:
        """ Método para verificação de assinatura digital com o esquema PKCS1-v1_5 (RFC 8017)

        Args:
            msg (bytes): Mensagem que foi assinada
            sig (bytes): Assinatura digital
            pubkey (bytes): Chave pública par da chave privada que gerou a assinatura (PEM)

        Returns:
            bool: Sucesso ou falha na verificação
        """
        try:
            key = RSA.import_key(pubkey.chave_bytes)
            hashed = SHA256.new(msg)
            PKCS1_v1_5.pkcs1_15.new(key).verify(hashed, sig)
            return True
        except:
            return False

    @staticmethod
    def cifra_RSAAES_OAEP(pubkey: ChaveCripto, msg: bytes) -> bytes:
        """ Método para cifragem de uma mensagem no esquema de cifragem RSAAES_OAEP

        Args:
            pubkey (bytes): Chave pública RSA no formato PEM
            msg (bytes): Mensagem a ser cifrada

        Returns:
            bytes: Mensagem cifrada
        """

        sha = SHA256.new()
        key = RSA.importKey(pubkey.chave_bytes)
        cipher = PKCS1_OAEP.new(key, sha)
        return cipher.encrypt(msg)

    @staticmethod
    def decifra_RSAAES_OAEP(privkey: ChaveCripto, msg: bytes) -> bytes:
        """ Método para decifragem de uma mensagem no esquema de cifragem RSAAES_OAEP

        Args:
            privkey (bytes): Chave privada RSA no formato PEM
            msg (bytes): Mensagem a ser decifrada

        Returns:
            bytes: Mensagem decifrada
        """
        sha = SHA256.new()
        key = RSA.importKey(privkey.chave_bytes)
        cipher = PKCS1_OAEP.new(key, sha)
        return cipher.decrypt(msg)

    @staticmethod
    def gera_HMAC_SHA256(key: bytes, msg: bytes) -> bytes:
        """ Método para geração de resumo HMAC-SHA256

        Args:
            key (bytes): Chave para a geração do resumo
            msg (bytes): Mensagem a ser resumida

        Returns:
            bytes: Resumo criptográfico
        """
        return hmac.new(key, msg, hashlib.sha256).digest()

    @staticmethod
    def verifica_HMAC_SHA256(key: bytes, msg: bytes, resumo: bytes) -> bool:
        """ Método para verificação de HMAC-SHA256

        Args:
            key (bytes): Chave para o resumo criptográfico
            msg (bytes): Mensagem a ser resumida
            resumo (bytes): Resumo criptográfico a ser verificado

        Returns:
            bool: Resultado da comparação
        """
        return CriptoDAF.gera_HMAC_SHA256(key, msg) == resumo

    @staticmethod
    def gera_resumo_SHA256(msg: bytes) -> bytes:
        """ Método para geração de resumo criptográfico SHA-256

        Args:
            msg (bytes): Mensagem a ser resumida
        Returns:
            bytes: Resumo criptográfico
        """
        return hashlib.sha256(msg).digest()

    @staticmethod
    def verifica_resumo_SHA256(msg: bytes, resumo: bytes) -> bytes:
        """ Método para verificação de SHA-256
        Args:
            msg (bytes): Mensagem a ser resumida
            resumo (bytes): Resumo a ser verificado

        Returns:
            bytes: Resultado da comparação
        """
        return CriptoDAF.gera_resumo_SHA256(msg) == resumo
        
    @staticmethod
    def verifica_resumo_SHA256(msg: bytes, resumo: bytes) -> bytes:
        """ Método para verificação de SHA-256
        Args:
            msg (bytes): Mensagem a ser resumida
            resumo (bytes): Resumo a ser verificado

        Returns:
            bytes: Resultado da comparação
        """
        return CriptoDAF.gera_resumo_SHA256(msg) == resumo

    @staticmethod
    def gera_numero_aleatorio(len: int) -> bytes:
        """Método para geração de bytes aleatórios

        Args:
            len (int): Número de bytes a serem gerados

        Returns:
            bytes: Bytes gerados aleatóriamente
        """
        rand = bytearray(random.getrandbits(8) for i in range(len))
        return rand
