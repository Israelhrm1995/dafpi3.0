from daf_virtual_rasp.utils.cripto_daf import ChaveCripto
from authlib.jose import jwk
import jwt
from typing import Union


class JWTDAF:

    def __init__(self):
        pass

    @staticmethod
    def geraJWT(payload: dict, alg: str, privkey: Union[ChaveCripto, bytes], pubkey: ChaveCripto = None) -> str:
        """ Método para geração de tokens JWT

        Args:
            payload (dict): Dicionário python com as chaves e valores do Payload do token
            alg (str): Algoritmo de assinatura digital
            privkey (bytes): Chave privada para geração da assinatura digital no formato PEM
            pubkey (bytes, optional): Chave pública para geração do header do token no formato PEM. Se não for passado, tem None com padrão.

        Returns:
            str: Token JWT gerado
        """
        tokenJWT = None
        if pubkey == None:
            if alg == 'RS256':
                header = {'typ': 'JWT', 'alg': alg}
                tokenJWT = jwt.encode(
                    payload, privkey.chave_bytes, algorithm=alg, headers=header)
                
            elif alg == 'HS256':
                header = {'typ': 'JWT', 'alg': alg}
                tokenJWT = jwt.encode(
                    payload, privkey, algorithm=alg, headers=header)
            elif alg=='ES384':
                header = {'typ': 'JWT', 'alg': alg}
                tokenJWT = jwt.encode(
                    payload, privkey.chave_bytes, algorithm=alg, headers=header)
            elif alg == 'ES256':
                header = {'typ': 'JWT', 'alg': alg}
                tokenJWT = jwt.encode(payload, privkey.chave_bytes, algorithm='ES256',headers=header)
            else:
                raise Exception(
                    "Algoritmo de assinatura digital não suportado")
        else:
            if alg == 'RS256':
                key_jwk = jwk.dumps(pubkey.chave_bytes, kty='RSA')
                header = {'jwk': key_jwk}
                tokenJWT = jwt.encode(
                    payload, privkey.chave_bytes, algorithm='RS256', headers=header)
            elif alg == 'ES256':
                key_jwk = jwk.dumps(pubkey.chave_bytes, kty = 'EC')
                header = {'jwk': key_jwk}
                tokenJWT = jwt.encode(payload, privkey.chave_bytes, algorithm='ES256',headers=header)
            elif alg == 'ES384':
                key_jwk = jwk.dumps(pubkey.chave_bytes, kty = 'EC')
                header = {'jwk': key_jwk}
                tokenJWT = jwt.encode(payload, privkey.chave_bytes, algorithm='ES384',headers=header)
            else:
                raise Exception(
                    "Algoritmo de assinatura digital não suportado")
        return tokenJWT

    @staticmethod
    def getJWTHeader(token: str) -> dict:
        """ Método para retorno do header do token JWT

        Args:
            token (str): Token JWT

        Returns:
            dict: Header do token JWT
        """

        header = jwt.get_unverified_header(token)
        return header

    @staticmethod
    def verificaJWT(tokenJWT: str, pubkey: Union[bytes,ChaveCripto], alg: str) -> dict:
        """ Método para verificação de tokens JWT

        Args:
            tokenJWT (str): Token JWT a ser verificado
            pubkey (bytes): Chave pública par da chave privada que gerou a assinatura do token JWT
            alg (str): Algoritmo de assinatura digital

        Returns:
            dict: Payload do token JWT
        """
        chave = None
        if isinstance(pubkey, bytes):
            chave = pubkey
        if isinstance(pubkey, ChaveCripto):
            chave = pubkey.chave_bytes
        try:
            payload = jwt.decode(tokenJWT, chave,
                                 algorithms=alg, verify=True)
            return payload
        except jwt.exceptions.InvalidSignatureError:
            return False
        except jwt.exceptions.InvalidAlgorithmError:
            return False
