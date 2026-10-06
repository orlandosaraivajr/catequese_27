"""Funções compartilhadas pelos geradores de PDF em core/services/.

Os textos jurídicos (termo de consentimento LGPD e autorização de uso de
imagem de menores) são idênticos entre Catequese Infantil, Crisma (menor de
idade), Perseverança/MEJ (menor de idade) e Coroinhas — por isso vivem aqui
uma única vez, em vez de repetidos em cada arquivo.
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


def pagina_termo_consentimento_menor_catequese(c, img_path, height, ficha):
    """Página "TERMO DE CONSENTIMENTO ... DE CRIANÇAS E ADOLESCENTES".

    Texto usado, sem nenhuma alteração, por Catequese Infantil, Crisma (menor)
    e Perseverança/MEJ (menor) -- os três geram exatamente este PDF.
    """
    desenhar_cabecalho(c, img_path, height, y=140)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(100, height - 160, f"TERMO DE CONSENTIMENTO PARA TRATAMENTO DE DADOS ")
    c.drawString(120, height - 180, f"PESSOAIS SENSÍVEIS DE CRIANÇAS E ADOLESCENTES")
    style = estilo_paragrafo()

    paragrafo = Paragraph(
        f"Eu, {ficha.nome_responsavel}, CPF {ficha.cpf_responsavel} na qualidade de responsável legal pelo(a) menor "
        f"{ficha.nome}, por meio deste instrumento, <b>manifesto meu consentimento livre, informado e inequívoco para o tratamento dos dados pessoais do(a) referido"
        "menor</b>, nos seguintes termos, em conformidade com a Lei no 13.709/2018:"
        ,style
    )
    frame = Frame(50, height - 400, 500, 200)
    frame.addFromList([paragrafo], c)

    paragrafo = Paragraph(
        f"1) Autorizo o tratamento a ser realizado pela PARÓQUIA NOSSA SENHORA APARECIDA, pessoa jurídica "
        f"de direito privado, inscrita no CNPJ no 44.802.999/0011-30, situada na Rua dois, no 349, Bairro Aparecida,"
        f"Rio Claro/SP, CEP 13500-270, e e-mail: pnsarc@hotmail.com, doravante denominada CONTROLADORA."
        ,style
    )
    frame = Frame(50, height - 460, 500, 200)
    frame.addFromList([paragrafo], c)
    
    paragrafo = Paragraph(
        f"2) Os dados pessoais do(a) menor serão utilizados exclusivamente para:<br/>"
        f"    I) Inscrição e organização da Catequese;<br/>"
        f"    II) Emitir certificados de conclusão dos sacramentos;<br/>"
        f"    III) Permitir contato com pais e/ou responsáveis.<br/>"
        ,style
    )
    frame = Frame(50, height - 520, 500, 200)
    frame.addFromList([paragrafo], c)
    
    paragrafo = Paragraph(
        f"3) Autorizo o tratamento apenas dos seguintes dados pessoais: nome completo; data de nascimento;"
        f"naturalidade; documento de identificação (RG, CPF, certidão de nascimento ou equivalente); endereço completo; telefone de contato."
        f"Não haverá utilização dos dados para fins comerciais, divulgação indevida ou compartilhamento com terceiros estranhos às atividades religiosas."
        ,style
    )
    frame = Frame(50, height - 590, 500, 200)
    frame.addFromList([paragrafo], c)
    

    paragrafo = Paragraph(
        f"4) Declaro estar ciente de que o armazenamento ocorrerá:"
        f"I) Em fichas físicas e/ou sistemas informatizados da Paróquia;<br/>"
        f"II) Que o acesso será restrito a pessoas autorizadas (secretaria, coordenação da catequese, catequistas e o Pároco, quando necessário);<br/>"
        f"III) Que a CONTROLADORA adotará medidas técnicas e administrativas adequadas para proteger os dados contra acessos não autorizados, perda, divulgação indevida ou qualquer forma de tratamento inadequado.<br/>"
        ,style
    )
    frame = Frame(50, height - 670, 500, 200)
    frame.addFromList([paragrafo], c)
    
    paragrafo = Paragraph(
        f"5) Os dados serão mantidos enquanto o(a) menor estiver matriculado(a) na Catequese, pelo prazo máximo de 3 (três) anos, quando concluída as etapas sacramentais, respeitando-se a necessidade de registros paroquiais.<br/>"
        f"6) Estou ciente de que posso, a qualquer momento solicitar acesso aos dados pessoais do(a) menor; solicitar correção de dados incompletos, inexatos ou desatualizados; requerer a eliminação de dados desnecessários, excessivos ou tratados em desconformidade com a lei.<br/>"
        f"7) Declaro, ainda, estar ciente de que posso revogar este consentimento a qualquer momento, mediante solicitação formal e por escrito à Secretaria Paroquial.<br/>"
        ,style
    )
    frame = Frame(50, height - 780, 500, 200)
    frame.addFromList([paragrafo], c)
   
    paragrafo = Paragraph(
            f"Rio Claro, {data_hoje()}<br/><br/> _____________________________________________<br/> {ficha.nome_responsavel} - CPF: {ficha.cpf_responsavel}",
        style
    )
    frame = Frame(250, height - 940, 500, 200)
    frame.addFromList([paragrafo], c)
    desenhar_verificacao_secretaria(c, height - 940)



def pagina_autorizacao_imagem_menor(c, img_path, height, ficha):
    """Página "AUTORIZAÇÃO PARA USO DE IMAGEM MENORES DE 18 ANOS".

    Texto usado, sem nenhuma alteração, por Catequese Infantil, Crisma (menor),
    Perseverança/MEJ (menor) e Coroinhas.
    """
    desenhar_cabecalho(c, img_path, height, y=140)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(100, height - 160, f"AUTORIZAÇÃO PARA USO DE IMAGEM MENORES DE 18 ANOS")
    style = estilo_paragrafo()

    paragrafo = Paragraph(
        f"Eu, {ficha.nome_responsavel}, CPF {ficha.cpf_responsavel} na qualidade de responsável legal pelo(a) menor "
        f"{ficha.nome}, autorizo, de forma livre, expressa e informada, a Paróquia Nossa Senhora Aparecida, inscrita "
        f"no CNPJ sob o nº 44.802.999/0011-30, a utilizar a imagem, nome e voz do(a) menor, captados em fotografias e/ou vídeos durante atividades e eventos da paróquia, para fins de divulgação em meios impressos, digitais e redes sociais da paróquia, sem qualquer ônus."
        ,style
    )
    frame = Frame(50, height - 400, 500, 200)
    frame.addFromList([paragrafo], c)

    paragrafo = Paragraph(
        f"Declaro estar ciente de que a utilização da imagem do(a) menor será feita de acordo com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018 - LGPD), e que posso, a qualquer momento, revogar esta autorização mediante solicitação por escrito à paróquia. "
        ,style
    )
    frame = Frame(50, height - 480, 500, 200)
    frame.addFromList([paragrafo], c)

    paragrafo = Paragraph(
        f"Estou ciente de que não tenho direito a qualquer remuneração pelo uso da imagem, nome e voz do(a) menor nos termos acima mencionados, e que a presente autorização é concedida por prazo indeterminado, podendo ser revogada a qualquer momento, mediante comunicação por escrito. "
        ,style
    )
    frame = Frame(50, height - 530, 500, 200)
    frame.addFromList([paragrafo], c)
    
    paragrafo = Paragraph(
        f"Por fim, declaro que a presente autorização foi feita de forma livre, sem qualquer coação, e que fui devidamente informado(a) sobre o tratamento dos dados pessoais do(a) menor pela paróquia. "
        ,style
    )
    frame = Frame(50, height - 580, 500, 200)
    frame.addFromList([paragrafo], c)

    paragrafo = Paragraph(
            f"Rio Claro, {data_hoje()}<br/><br/> _____________________________________________<br/> {ficha.nome_responsavel} - CPF: {ficha.cpf_responsavel}",
        style
    )
    frame = Frame(250, height - 660, 500, 200)
    frame.addFromList([paragrafo], c)
    desenhar_verificacao_secretaria(c, height - 660)
    
