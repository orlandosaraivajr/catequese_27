from reportlab.lib import colors
from reportlab.platypus import Frame, Paragraph

from ._common import CABECALHO_PATH, novo_canvas, desenhar_cabecalho, estilo_paragrafo, data_hoje, desenhar_verificacao_secretaria
from ._common import (
    pagina_autorizacao_imagem, desenhar_assinatura, desenhar_texto_em_fluxo, clausula_revogacao_consentimento,
    abertura_autorizacao_imagem_adulto, endereco_completo, TITULO_AUTORIZACAO_IMAGEM,
)


def gerar_ficha_catequese_adulto(ficha):
    img_path = CABECALHO_PATH
    c, height, filename = novo_canvas(f"ficha_catequese_adulto_{ficha.id}.pdf")

    desenhar_cabecalho(c, img_path, height, y=200)
    c.setFont("Helvetica", 16)
    c.drawString(130, height - 220, f"INSCRIÇÃO PARA CATEQUESE ADULTO")
    
    # Nome
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 250, f"Nome:")
    c.setFont("Helvetica", 11)
    c.drawString(150, height - 250, f"{ficha.nome}")

    # Sexo
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 265, f"Sexo:")
    c.setFont("Helvetica", 11)
    if ficha.sexo == 'M':
        c.drawString(150, height - 265, f"Masculino")
    else:
        c.drawString(150, height - 265, f"Feminino")
    
    # Data de Nascimento
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 280, f"Data Nascimento:")
    c.drawString(300, height - 280, f"Telefone:")
    c.setFont("Helvetica", 11)
    c.drawString(150, height - 280, f"{ficha.data_nascimento.strftime("%d/%m/%Y")}")
    c.drawString(350, height - 280, f"{ficha.celular}")
    
    # Naturalidade
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 295, f"Naturalidade:")
    c.setFont("Helvetica", 11)
    c.drawString(150, height - 295, f"{ficha.naturalidade}")
    
    # Nome dos Pais
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 310, f"Pai:")
    c.setFont("Helvetica", 11)
    if ficha.nome_pai:
        c.drawString(150, height - 310, f"{ficha.nome_pai}")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 325, f"Mãe:")
    c.setFont("Helvetica", 11)
    if ficha.nome_mae:
        c.drawString(150, height - 325, f"{ficha.nome_mae}")

    # Endereço
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 340, f"Endereço:")
    c.setFont("Helvetica", 11)
    c.drawString(150, height - 340, f"{ficha.endereco}")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 355, f"Cidade:")
    c.setFont("Helvetica", 11)
    c.drawString(150, height - 355, f"{ficha.cidade}  -  {ficha.uf}")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 370, f"Estado Civil:")
    c.setFont("Helvetica", 11)
    c.drawString(150, height - 370, f"{ficha.estado_civil}")
    
    # Batizado
    c.setFont("Helvetica", 11)
    if ficha.batizado:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, height - 400, f"Batizado na Data: {ficha.batizado_data.strftime("%d/%m/%Y") if ficha.batizado_data else ''}")
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 415, f"Diocese: {ficha.batizado_diocese}")
        c.drawString(50, height - 430, f"Paróquia: {ficha.batizado_paroquia}")
        c.drawString(50, height - 445, f"Celebrante: {ficha.batizado_celebrante}")
    else:
        c.setFillColor(colors.red)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, height - 400, f"Não Batizado")
        c.setFillColor(colors.black)

# Primeira Eucaristia
    if ficha.primeira_eucaristia:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, height - 500, f"Primeira Eucaristia - Data: {ficha.primeira_eucaristia_data.strftime("%d/%m/%Y") if ficha.primeira_eucaristia_data else ''}")
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 515, f"Diocese: {ficha.primeira_eucaristia_diocese}")
        c.drawString(50, height - 530, f"Paróquia: {ficha.primeira_eucaristia_paroquia}")
        c.drawString(50, height - 545, f"Celebrante: {ficha.primeira_eucaristia_celebrante} ")
    else:
        c.setFillColor(colors.red)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, height - 500, f"Não Fez Primeira Eucaristia")
        c.setFillColor(colors.black)


# Casamento
    
    if ficha.casado_igreja:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, height - 600, f"Casado na Igreja - Data: {ficha.casado_igreja_data.strftime("%d/%m/%Y") if ficha.casado_igreja_data else ''}")
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 615, f"Diocese: {ficha.casado_igreja_diocese}")
        c.drawString(50, height - 630, f"Paróquia: {ficha.casado_igreja_paroquia}")
        c.drawString(50, height - 645, f"Celebrante: {ficha.casado_igreja_celebrante} ")
    else:
        c.setFillColor(colors.red)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, height - 600, f"Não casou na Igreja ")
        c.setFillColor(colors.black)

    c.setFont("Helvetica", 11)
    c.drawString(50, height - 700, f"Horário:")
    c.drawString(150, height - 700, f"{ficha.turma.nome}")
    
   
    style = estilo_paragrafo()

    
    paragrafo = Paragraph(
            f"Rio Claro, {data_hoje()}<br/><br/> _____________________________________________<br/> {ficha.nome} <br/>CPF: {ficha.cpf}",
        style
    )
    frame = Frame(250, height - 940, 500, 200)
    frame.addFromList([paragrafo], c)
    desenhar_verificacao_secretaria(c, height - 940)
    
    c.showPage()  # Página 2
    

    desenhar_cabecalho(c, img_path, height, y=140)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(100, height - 160, f"TERMO DE CONSENTIMENTO PARA TRATAMENTO ")
    c.drawString(120, height - 180, f"DE DADOS PESSOAIS SENSÍVEIS")
    


    textos = [
        f"Eu, {ficha.nome}, CPF {ficha.cpf}, por meio deste instrumento, <b>manifesto meu consentimento livre, informado e inequívoco para o tratamento dos meus dados pessoais"
        "</b>, nos seguintes termos, em conformidade com a Lei no 13.709/2018:",

        f"1) Autorizo o tratamento a ser realizado pela PARÓQUIA NOSSA SENHORA APARECIDA, pessoa jurídica "
        f"de direito privado, inscrita no CNPJ no 44.802.999/0011-30, situada na Rua dois, no 349, Bairro Aparecida, "
        f"Rio Claro/SP, CEP 13500-270, e e-mail: pnsarc@hotmail.com, doravante denominada CONTROLADORA.",

        f"2) Meus dados serão utilizados exclusivamente para:<br/>"
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

        f"5) Os dados serão mantidos enquanto estiver matriculado(a) na Catequese, pelo prazo máximo de 3 (três) anos, quando concluída as etapas sacramentais, respeitando-se a necessidade de registros paroquiais.",
        f"6) Estou ciente de que posso, a qualquer momento solicitar acesso aos meus dados pessoais; solicitar correção de dados incompletos, inexatos ou desatualizados; requerer a eliminação de dados desnecessários, excessivos ou tratados em desconformidade com a lei.",
        clausula_revogacao_consentimento(7),
    ]
    y = desenhar_texto_em_fluxo(c, textos, height - 190)
    desenhar_assinatura(c, y, ficha.nome, ficha.cpf, separador=" <br/>")

    c.showPage()  # Página 3

    y = pagina_autorizacao_imagem(
        c, img_path, height, TITULO_AUTORIZACAO_IMAGEM,
        abertura_autorizacao_imagem_adulto(ficha.nome, ficha.cpf, endereco_completo(ficha)),
    )
    desenhar_assinatura(c, y, ficha.nome, ficha.cpf)

    

    c.save()

    return filename
