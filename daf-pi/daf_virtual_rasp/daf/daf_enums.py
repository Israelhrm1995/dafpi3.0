from enum import Enum


class Estados(Enum):
    inativo = "INATIVO"
    pronto = "PRONTO"
    bloqueado = "BLOQUEADO"
    inutilizado = "INUTILIZADO"


class Respostas(Enum):
    sucesso = 0
    estadoIncorreto = 1
    pedidoMalFormado = 2
    assinaturaInvalida = 3
    pafDesconhecido = 4
    hmacNaoCorrespondente = 5
    autorizacaoNaoEncontrada = 6
    autorizacaoRetida = 7
    versaoSBInvalida = 8
    modeloInvalido = 9
    certificadoInvalido = 10
    erroInesperado = 11
    assinaturaFirmwareInvalida = 12



class Artefatos(Enum):
    certificado = "certificado"
    chaveAteste = "chaveAteste"
    chaveAtestePublica = "chaveAtestePublica"
    chavePrivada = "chavePrivada"
    chavePublica = "chavePublica"
    chaveSEF = "chaveSEF"
    chavePAF = "chavePAF"
    contador = "contador"
    IDDAF = "IDDAF"
    modoOperacao = "modoOperacao"



class Guardas(Enum):
    MaxDFe = "MaxDFe"
    REGOK = "REGOK"
    NumDFe = "NumDFe"
    MaxDFeModel = "MaxDFeModel"
    Violado = "Violado"
    Estado = "Estado"


class ParametrosAtualizacao(Enum):
    assinaturaSEF = "assinaturaSEF"
    versaoSB = "versaoSB"
    falhasAtualizacao = "falhasAtualizacao"
    modelo = "modelo"
    cnpj = "cnpjFab"
