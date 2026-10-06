from reportlab.lib import colors
from reportlab.platypus import Frame, Paragraph

from ._common import (
    desenhar_verificacao_secretaria,
    CABECALHO_PATH,
    novo_canvas,
    desenhar_cabecalho,
    estilo_paragrafo,
    data_hoje,
    pagina_autorizacao_imagem_menor,
)


def gerar_ficha_coroinhas(ficha):
    img_path = CABECALHO_PATH
    c, height, filename = novo_canvas(f"ficha_coroinha_{ficha.id}.pdf")

    desenhar_cabecalho(c, img_path, height, y=200)
    c.setFont("Helvetica", 16)
    c.drawString(130, height - 220, f"INSCRIÇÃO PARA COROINHAS")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 250, f"Nome:")
    c.drawString(50, height - 265, f"Sexo:")
    c.drawString(50, height - 280, f"Data Nascimento:")
    c.drawString(50, height - 310, f"Pai:")
    c.drawString(50, height - 325, f"Mãe:")
    c.drawString(50, height - 370, f"Endereço:")
    c.drawString(50, height - 385, f"Cidade:")
    
    c.setFont("Helvetica", 11)
    c.drawString(150, height - 250, f"{ficha.nome}")
    if ficha.sexo == 'M':
        c.drawString(150, height - 265, f"Masculino")
    else:
        c.drawString(150, height - 265, f"Feminino")
    c.drawString(150, height - 280, f"{ficha.data_nascimento.strftime("%d/%m/%Y")}")
    if ficha.nome_pai:
        c.drawString(150, height - 310, f"{ficha.nome_pai}  -  {ficha.celular_pai}")
    if ficha.nome_mae:
        c.drawString(150, height - 325, f"{ficha.nome_mae}  -  {ficha.celular_mae}")    
    c.drawString(150, height - 370, f"{ficha.endereco}")
    c.drawString(150, height - 385, f"{ficha.cidade}  {ficha.uf}")
    
    style = estilo_paragrafo()
    paragrafo = Paragraph(
            f"Rio Claro, {data_hoje()}<br/><br/> _____________________________________________<br/> {ficha.nome_responsavel} <br/>CPF: {ficha.cpf_responsavel}",
        style
    )
    frame = Frame(250, height - 700, 500, 200)
    frame.addFromList([paragrafo], c)
    desenhar_verificacao_secretaria(c, height - 700)
    
    
    
    c.showPage()  # Página 2

    desenhar_cabecalho(c, img_path, height, y=140)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(100, height - 160, f"TERMO DE CONSENTIMENTO PARA TRATAMENTO DE DADOS ")
    c.drawString(120, height - 180, f"PESSOAIS SENSÍVEIS DE CRIANÇAS E ADOLESCENTES")
    
    style = estilo_paragrafo()

    paragrafo = Paragraph(
        f"Eu, {ficha.nome_responsavel}, CPF {ficha.cpf_responsavel} na qualidade de responsável legal pelo(a) menor "
        f"{ficha.nome}, por meio deste instrumento, <b>manifesto meu consentimento livre, informado e inequívoco para o tratamento dos dados pessoais do(a) referido "
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
        f"    I) Inscrição e organização da pastoral de Coroinhas;<br/>"
        f"    II) Permitir contato com pais e/ou responsáveis.<br/>"
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
        f"5) Os dados serão mantidos enquanto o(a) menor estiver no serviço da pastoral dos coroinhas, pelo prazo máximo de 3 (três) anos sacramentais, respeitando-se a necessidade de registros paroquiais.<br/>"
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


    c.showPage()  # Página 3
    pagina_autorizacao_imagem_menor(c, img_path, height, ficha)

    c.save()

    return filename
