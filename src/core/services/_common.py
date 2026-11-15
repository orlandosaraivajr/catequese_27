"""Funções compartilhadas pelos geradores de PDF em core/services/.

Os textos jurídicos vivem aqui uma única vez, em vez de repetidos em cada arquivo:
o termo de consentimento LGPD de menores (Catequese Infantil, Crisma e
Perseverança/MEJ menores de idade) e o termo de autorização de uso de imagem
e voz, usado por todas as fichas.
"""
import os
from datetime import datetime

from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Frame, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

CABECALHO_PATH = os.path.join(settings.BASE_DIR, 'static', 'pdf', 'cabecalho.png')


def data_hoje():
    meses = { 1: "janeiro",2: "fevereiro",3: "março",
    4: "abril",5: "maio", 6: "junho",7: "julho",
    8: "agosto",9: "setembro",10: "outubro",
    11: "novembro",12: "dezembro" }
    hoje = datetime.today()
    return f"{hoje.day} de {meses[hoje.month]} de {hoje.year}"


def novo_canvas(nome_arquivo):
    """Abre um Canvas A4 já salvando dentro de MEDIA_ROOT; devolve (canvas, height, filename)."""
    # MEDIA_ROOT não é versionado: cria a pasta caso ainda não exista (ex.: clone novo)
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    filename = os.path.join(settings.MEDIA_ROOT, nome_arquivo)
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    return c, height, filename


def desenhar_cabecalho(c, img_path, height, y=200):
    """Imagem do brasão/cabeçalho no topo da página (mesmo bloco repetido em toda página)."""
    c.drawImage(
        img_path,
        x=50,           # posição X
        y=height - y,   # posição Y
        width=500,      # ajuste como preferir
        height=150,
        preserveAspectRatio=True,
        mask='auto'
    )


def estilo_paragrafo():
    """Estilo "Normal" usado em todo Paragraph dos PDFs (mesmo bloco repetido em toda página)."""
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = "Helvetica"
    style.fontSize = 11
    style.leading = 15
    return style


def desenhar_verificacao_secretaria(c, y, linhas_antes=2, x=50, largura=190, tracos=28):
    """Campo "Documento verificado por", onde a secretaria assina após conferir a ficha.

    Fica ao lado da assinatura do responsável. ``y`` é o mesmo do Frame da
    assinatura; ``linhas_antes`` é quantas linhas o bloco da assinatura tem antes
    do traço (data + linha em branco = 2), para que os dois traços fiquem alinhados.
    """
    paragrafo = Paragraph(
        "&nbsp;<br/>" * linhas_antes + "_" * tracos + "<br/>Documento verificado por",
        estilo_paragrafo(),
    )
    frame = Frame(x, y, largura, 200)
    frame.addFromList([paragrafo], c)


def desenhar_texto_em_fluxo(c, textos, topo, base=100, style=None):
    """Desenha os parágrafos um após o outro num único Frame, sem sobreposição.

    Devolve o ``y`` logo abaixo do último parágrafo, onde quem chamou desenha
    a(s) assinatura(s). Se o texto não couber entre ``topo`` e ``base``, lança
    ValueError em vez de cortar parágrafos em silêncio.
    """
    if style is None:
        style = estilo_paragrafo()
        style.leading = 14
        style.spaceAfter = 3
    paragrafos = [Paragraph(t, style) for t in textos]
    frame = Frame(50, base, 500, topo - base)
    frame.addFromList(paragrafos, c)
    if paragrafos:
        raise ValueError("O texto do termo não coube na página.")
    return frame._y


def desenhar_assinatura(c, y, nome, cpf, separador=" - "):
    """Local/data, linha de assinatura e o campo da secretaria, começando em ``y``."""
    paragrafo = Paragraph(
        f"Rio Claro, {data_hoje()}<br/><br/> _____________________________________________<br/> {nome}{separador}CPF: {cpf}",
        estilo_paragrafo(),
    )
    frame = Frame(250, y - 200, 500, 200)
    frame.addFromList([paragrafo], c)
    desenhar_verificacao_secretaria(c, y - 200)


# ------------------------------------------------------------------
# Termos de consentimento LGPD (Paróquia Nossa Senhora Aparecida)
# ------------------------------------------------------------------
REVOGACAO_SEM_EFEITO_RETROATIVO = (
    "A revogação não terá efeito retroativo, não implicando a obrigatoriedade de retirada de materiais já "
    "publicados ou distribuídos até a data da notificação, mas impedindo novas utilizações."
)


def clausula_revogacao_consentimento(numero, plural=False):
    """Cláusula de revogação do consentimento, sem efeito retroativo."""
    if plural:
        inicio = "Declaramos, ainda, estarmos cientes de que podemos"
    else:
        inicio = "Declaro, ainda, estar ciente de que posso"
    return (
        f"{numero}) {inicio} revogar este consentimento a qualquer momento, mediante solicitação formal e por "
        f"escrito à Secretaria Paroquial. {REVOGACAO_SEM_EFEITO_RETROATIVO}"
    )


def clausula_eca_consentimento(numero):
    """Compromisso com o ECA — apenas nos termos de menores de idade, como no termo da Diocese."""
    return (
        f"{numero}) A CONTROLADORA se compromete a zelar pela proteção integral de crianças e adolescentes, "
        f"em cumprimento ao Estatuto da Criança e do Adolescente – ECA (Lei nº 8.069/90)."
    )


def pagina_termo_consentimento_menor_catequese(c, img_path, height, ficha):
    """Página "TERMO DE CONSENTIMENTO ... DE CRIANÇAS E ADOLESCENTES".

    Texto usado, sem nenhuma alteração, por Catequese Infantil, Crisma (menor)
    e Perseverança/MEJ (menor) -- os três geram exatamente este PDF.
    """
    desenhar_cabecalho(c, img_path, height, y=140)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(100, height - 160, f"TERMO DE CONSENTIMENTO PARA TRATAMENTO DE DADOS ")
    c.drawString(120, height - 180, f"PESSOAIS SENSÍVEIS DE CRIANÇAS E ADOLESCENTES")
    textos = [
        f"Eu, {ficha.nome_responsavel}, CPF {ficha.cpf_responsavel} na qualidade de responsável legal pelo(a) menor "
        f"{ficha.nome}, por meio deste instrumento, <b>manifesto meu consentimento livre, informado e inequívoco para o tratamento dos dados pessoais do(a) referido "
        "menor</b>, nos seguintes termos, em conformidade com a Lei no 13.709/2018:",

        f"1) Autorizo o tratamento a ser realizado pela PARÓQUIA NOSSA SENHORA APARECIDA, pessoa jurídica "
        f"de direito privado, inscrita no CNPJ no 44.802.999/0011-30, situada na Rua dois, no 349, Bairro Aparecida, "
        f"Rio Claro/SP, CEP 13500-270, e e-mail: pnsarc@hotmail.com, doravante denominada CONTROLADORA.",

        f"2) Os dados pessoais do(a) menor serão utilizados exclusivamente para:<br/>"
        f"    I) Inscrição e organização da Catequese;<br/>"
        f"    II) Emitir certificados de conclusão dos sacramentos;<br/>"
        f"    III) Permitir contato com pais e/ou responsáveis.",

        f"3) Autorizo o tratamento apenas dos seguintes dados pessoais: nome completo; data de nascimento; "
        f"naturalidade; documento de identificação (RG, CPF, certidão de nascimento ou equivalente); endereço completo; telefone de contato. "
        f"Não haverá utilização dos dados para fins comerciais, divulgação indevida ou compartilhamento com terceiros estranhos às atividades religiosas.",

        f"4) Declaro estar ciente de que o armazenamento ocorrerá:<br/>"
        f"I) Em fichas físicas e/ou sistemas informatizados da Paróquia;<br/>"
        f"II) Que o acesso será restrito a pessoas autorizadas (secretaria, coordenação da catequese, catequistas e o Pároco, quando necessário);<br/>"
        f"III) Que a CONTROLADORA adotará medidas técnicas e administrativas adequadas para proteger os dados contra acessos não autorizados, perda, divulgação indevida ou qualquer forma de tratamento inadequado.",

        f"5) Os dados serão mantidos enquanto o(a) menor estiver matriculado(a) na Catequese, pelo prazo máximo de 3 (três) anos, quando concluída as etapas sacramentais, respeitando-se a necessidade de registros paroquiais.",
        f"6) Estou ciente de que posso, a qualquer momento solicitar acesso aos dados pessoais do(a) menor; solicitar correção de dados incompletos, inexatos ou desatualizados; requerer a eliminação de dados desnecessários, excessivos ou tratados em desconformidade com a lei.",
        clausula_revogacao_consentimento(7),
        clausula_eca_consentimento(8),
    ]
    y = desenhar_texto_em_fluxo(c, textos, height - 190)
    desenhar_assinatura(c, y, ficha.nome_responsavel, ficha.cpf_responsavel)



# ------------------------------------------------------------------
# Autorização de uso de imagem e voz
#
# Texto baseado no modelo da Diocese de Piracicaba ("Termo de Autorização de
# Uso de Imagem e Voz"). É o mesmo para todas as pastorais; muda apenas o
# parágrafo de abertura (quem autoriza) e o fechamento (singular/plural).
# ------------------------------------------------------------------
TITULO_AUTORIZACAO_IMAGEM = "TERMO DE AUTORIZAÇÃO DE USO DE IMAGEM E VOZ"
TITULO_AUTORIZACAO_IMAGEM_MENOR = "TERMO DE AUTORIZAÇÃO DE USO DE IMAGEM E VOZ DE MENORES DE IDADE"

OUTORGADA_DIOCESE = (
    "a <b>DIOCESE DE PIRACICABA</b>, pessoa jurídica de direito privado, inscrita no CNPJ sob o "
    "nº 44.802.999/0001-68, com sede na Avenida Independência, nº 1146, Bairro Alto, CEP 13419-155, "
    "na cidade de Piracicaba/SP, bem como suas paróquias, seminários diocesanos ou quaisquer outras "
    "instituições a ela vinculadas (doravante OUTORGADA)"
)

CLAUSULA_USO = (
    "A presente autorização é concedida a título gratuito e abrange o direito de uso da imagem e voz "
    "em fotografias e documentos, vídeos, gravações de áudio e outros formatos de mídia digital ou impressa."
)
CLAUSULA_DIVULGACAO = (
    "As imagens e sons poderão ser utilizados para fins de divulgação institucional e documental de suas "
    "atividades, sem fins lucrativos diretos. A utilização inclui, mas não se limita, a publicação em meios "
    "impressos e em plataformas digitais (sites, Instagram, Facebook, YouTube, entre outros), por prazo "
    "indeterminado, em todo o território nacional."
)
CLAUSULA_ECA = (  # só nos termos de menores de idade
    "A OUTORGADA se compromete a zelar pela proteção integral de crianças e adolescentes, em cumprimento "
    "ao Estatuto da Criança e do Adolescente – ECA (Lei nº 8.069/90)."
)
CLAUSULA_LGPD = (
    "Todas as informações, baseadas no uso ou tratamento de dados pessoais, seguirão as disposições da "
    "Lei Geral de Proteção de Dados Pessoais – LGPD (Lei nº 13.709/2018)."
)
CLAUSULA_REVOGACAO = (
    "A presente autorização poderá ser revogada a qualquer tempo e não terá efeito retroativo, não "
    "implicando a obrigatoriedade de retirada de materiais já publicados ou distribuídos até a data da "
    "notificação, mas impedindo novas utilizações."
)
CLAUSULA_TERCEIROS = (
    "Fica ainda autorizada a cessão dos direitos de veiculação das imagens para terceiros, desde que para "
    "os mesmos fins e de forma gratuita, não recebendo a OUTORGADA qualquer tipo de remuneração por tal cessão."
)


def clausulas_autorizacao_imagem(menor):
    """Cláusulas numeradas do termo; a do ECA entra apenas quando quem é retratado é menor de idade."""
    clausulas = [CLAUSULA_USO, CLAUSULA_DIVULGACAO]
    if menor:
        clausulas.append(CLAUSULA_ECA)
    clausulas += [CLAUSULA_LGPD, CLAUSULA_REVOGACAO, CLAUSULA_TERCEIROS]
    return [f"{i}) {texto}" for i, texto in enumerate(clausulas, start=1)]

FECHAMENTO_AUTORIZACAO_IMAGEM = (
    "Por estar de acordo com os termos aqui dispostos, declaro que autorizo o uso acima descrito "
    "e assino o presente termo."
)
FECHAMENTO_AUTORIZACAO_IMAGEM_PLURAL = (
    "Por estarmos de acordo com os termos aqui dispostos, declaramos que autorizamos o uso acima descrito "
    "e assinamos o presente termo."
)


def _residente(endereco):
    """Trecho ", residente em <endereço>" — omitido quando o endereço não foi informado."""
    endereco = (endereco or '').strip()
    return f", residente em {endereco}" if endereco else ""


def abertura_autorizacao_imagem_menor(ficha):
    """Responsável legal autoriza o uso da imagem e voz do(a) menor."""
    nascimento = f", nascido(a) em {ficha.data_nascimento:%d/%m/%Y}" if ficha.data_nascimento else ""
    return (
        f"Eu, <b>{ficha.nome_responsavel}</b>, inscrito(a) no CPF sob o nº {ficha.cpf_responsavel}"
        f"{_residente(ficha.endereco_responsavel)}, na qualidade de pai/mãe ou responsável legal do(a) menor "
        f"<b>{ficha.nome}</b>{nascimento}, <b>AUTORIZO</b> {OUTORGADA_DIOCESE}, a utilizar a imagem e a voz "
        f"do(a) menor acima identificado(a), nas condições que seguem descritas:"
    )


def abertura_autorizacao_imagem_adulto(nome, cpf, endereco):
    """A própria pessoa (maior de idade) autoriza o uso da sua imagem e voz."""
    return (
        f"Eu, <b>{nome}</b>, inscrito(a) no CPF sob o nº {cpf}{_residente(endereco)}, "
        f"<b>AUTORIZO</b> {OUTORGADA_DIOCESE}, a utilizar a minha imagem e a minha voz, "
        f"nas condições que seguem descritas:"
    )


def abertura_autorizacao_imagem_noivos(ficha):
    """Os noivos autorizam o uso das suas imagens e vozes."""
    return (
        f"Nós, <b>{ficha.nome_noivo}</b> e <b>{ficha.nome_noiva}</b>, <b>AUTORIZAMOS</b> {OUTORGADA_DIOCESE}, "
        f"a utilizar as nossas imagens e as nossas vozes, nas condições que seguem descritas:"
    )


def endereco_completo(ficha):
    """Endereço da própria ficha no formato "Rua X, 1 - Cidade/UF"."""
    cidade_uf = "/".join(p for p in (ficha.cidade, ficha.uf) if p)
    return " - ".join(p for p in (ficha.endereco, cidade_uf) if p)


def pagina_autorizacao_imagem(c, img_path, height, titulo, abertura, plural=False, menor=False):
    """Desenha cabeçalho, título e o texto do termo de uso de imagem e voz.

    Todo o texto corre num único Frame, um parágrafo após o outro, para que
    nada se sobreponha. Devolve o ``y`` logo abaixo do último parágrafo, onde
    quem chamou desenha a(s) assinatura(s).
    """
    desenhar_cabecalho(c, img_path, height, y=140)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(A4[0] / 2, height - 160, titulo)

    style = estilo_paragrafo()
    style.alignment = 4  # justificado
    style.spaceAfter = 6
    fechamento = FECHAMENTO_AUTORIZACAO_IMAGEM_PLURAL if plural else FECHAMENTO_AUTORIZACAO_IMAGEM
    textos = (abertura, *clausulas_autorizacao_imagem(menor), fechamento)
    return desenhar_texto_em_fluxo(c, textos, height - 170, base=150, style=style)


def pagina_autorizacao_imagem_menor(c, img_path, height, ficha):
    """Termo de uso de imagem e voz de menores de idade, assinado pelo responsável.

    Usado por Catequese Infantil, Crisma (menor), Perseverança/MEJ (menor) e Coroinhas.
    """
    y = pagina_autorizacao_imagem(
        c, img_path, height, TITULO_AUTORIZACAO_IMAGEM_MENOR, abertura_autorizacao_imagem_menor(ficha),
        menor=True,
    )
    desenhar_assinatura(c, y, ficha.nome_responsavel, ficha.cpf_responsavel)

