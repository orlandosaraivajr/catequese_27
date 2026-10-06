from reportlab.lib import colors
from reportlab.platypus import Frame, Paragraph

from ._common import CABECALHO_PATH, novo_canvas, desenhar_cabecalho, estilo_paragrafo, data_hoje, desenhar_verificacao_secretaria


def gerar_ficha_noivos(ficha):
    img_path = CABECALHO_PATH
    c, height, filename = novo_canvas(f"ficha_noivos_{ficha.id}.pdf")

    desenhar_cabecalho(c, img_path, height, y=200)
    c.setFont("Helvetica", 16)
    c.drawString(130, height - 210, f"INSCRIÇÃO PARA CURSO DE NOIVOS")

    c.setFillColor(colors.red)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(420, height - 230, f"Pagamento realizado")
    c.drawString(420, height - 240, f"no ato da inscrição.")
    c.setFillColor(colors.black)
            
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 250, f"Noivo:")
    c.drawString(50, height - 265, f"Data Nascimento:")
    c.drawString(50, height - 280, f"Endereço:")
    c.drawString(50, height - 295, f"Celular:")
    c.drawString(50, height - 310, f"Profissão:")
    c.drawString(50, height - 325, f"Local Trabalho:")
    c.drawString(50, height - 340, f"Religião:")
    c.drawString(50, height - 355, f"Pai:")
    c.drawString(50, height - 370, f"Mãe:")
    c.drawString(50, height - 385, f"Endereço Pais:")
    c.drawString(50, height - 400, f"Contato Pais:")
    c.drawString(50, height - 415, f"Religião Pais:")
    
    
    c.drawString(50, height - 465, f"Noiva:")
    c.drawString(50, height - 480, f"Data Nascimento:")
    c.drawString(50, height - 495, f"Endereço:")
    c.drawString(50, height - 510, f"Celular:")
    c.drawString(50, height - 525, f"Profissão:")
    c.drawString(50, height - 540, f"Local Trabalho:")
    c.drawString(50, height - 555, f"Religião:")
    c.drawString(50, height - 570, f"Pai:")
    c.drawString(50, height - 585, f"Mãe:")
    c.drawString(50, height - 600, f"Endereço Pais:")
    c.drawString(50, height - 615, f"Contato Pais:")
    c.drawString(50, height - 630, f"Religião Pais:")
    
    c.drawString(50, height - 700, f"Restrição alimentar noivo:")
    c.drawString(50, height - 715, f"Restrição alimentar noiva:")

    c.drawString(150, height - 660, f"Data casamento:")
    c.drawString(150, height - 675, f"Paróquia:")
    
    c.setFont("Helvetica", 11)
    c.drawString(150, height - 250, f"{ficha.nome_noivo}")
    c.drawString(150, height - 265, f"{ficha.data_nascimento_noivo.strftime("%d/%m/%Y")}")
    c.drawString(150, height - 280, f"{ficha.endereco_noivo}")
    c.drawString(150, height - 295, f"{ficha.celular_noivo}")
    c.drawString(150, height - 310, f"{ficha.profissao_noivo}")
    c.drawString(150, height - 325, f"{ficha.local_trabalho_noivo}")
    c.drawString(150, height - 340, f"{ficha.religiao_noivo}")
    c.drawString(150, height - 355, f"{ficha.nome_pai_noivo}")
    c.drawString(150, height - 370, f"{ficha.nome_mae_noivo}")
    c.drawString(150, height - 385, f"{ficha.endereco_pais_noivo}")
    c.drawString(150, height - 400, f"{ficha.celular_pais_noivo}")
    c.drawString(150, height - 415, f"{ficha.religiao_pais_noivo}")
    c.drawString(200, height - 700, f"{ficha.restricao_alimentar_noivo}")
    

    c.drawString(150, height - 465, f"{ficha.nome_noiva}")
    c.drawString(150, height - 480, f"{ficha.data_nascimento_noiva.strftime("%d/%m/%Y")}")
    c.drawString(150, height - 495, f"{ficha.endereco_noiva}")
    c.drawString(150, height - 510, f"{ficha.celular_noiva}")
    c.drawString(150, height - 525, f"{ficha.profissao_noiva}")
    c.drawString(150, height - 540, f"{ficha.local_trabalho_noiva}")
    c.drawString(150, height - 555, f"{ficha.religiao_noiva}")
    c.drawString(150, height - 570, f"{ficha.nome_pai_noiva}")
    c.drawString(150, height - 585, f"{ficha.nome_mae_noiva}")
    c.drawString(150, height - 600, f"{ficha.endereco_pais_noiva}")
    c.drawString(150, height - 615, f"{ficha.celular_pais_noiva}")
    c.drawString(150, height - 630, f"{ficha.religiao_pais_noiva}")
    c.drawString(200, height - 715, f"{ficha.restricao_alimentar_noiva}")
    
    c.drawString(270, height - 660, f"{ficha.data_provavel_casamento.strftime("%d/%m/%Y")}")
    c.drawString(270, height - 675, f"{ficha.paroquia_casamento}")

    style = estilo_paragrafo()

    
    paragrafo = Paragraph(f"Rio Claro, {data_hoje()}",style)
    frame = Frame(250, height - 940, 500, 200)
    frame.addFromList([paragrafo], c)

    # Três colunas: noivo, noiva e a conferência da secretaria
    paragrafo = Paragraph(f"_________________________<br/>{ficha.nome_noivo}", style)
    frame = Frame(50, height - 980, 170, 200)
    frame.addFromList([paragrafo], c)

    paragrafo = Paragraph(f"_________________________<br/>{ficha.nome_noiva}", style)
    frame = Frame(220, height - 980, 170, 200)
    frame.addFromList([paragrafo], c)

    desenhar_verificacao_secretaria(c, height - 980, linhas_antes=0, x=390, largura=170, tracos=25)
    
    c.showPage()  # Página 2
    

    desenhar_cabecalho(c, img_path, height, y=140)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(100, height - 160, f"TERMO DE CONSENTIMENTO PARA TRATAMENTO ")
    c.drawString(150, height - 180, f"DE DADOS PESSOAIS SENSÍVEIS")
    


    paragrafo = Paragraph(
        f"Nós, {ficha.nome_noivo} e {ficha.nome_noiva}, por meio deste instrumento, <b>manifestamos nosso consentimento livre, informado e inequívoco para o tratamento dos nossos dados pessoais"
        "</b>, nos seguintes termos, em conformidade com a Lei no 13.709/2018:"
        ,style
    )
    frame = Frame(50, height - 400, 500, 200)
    frame.addFromList([paragrafo], c)

    paragrafo = Paragraph(
        f"1) Autorizamos o tratamento a ser realizado pela PARÓQUIA NOSSA SENHORA APARECIDA, pessoa jurídica "
        f"de direito privado, inscrita no CNPJ no 44.802.999/0011-30, situada na Rua dois, no 349, Bairro Aparecida,"
        f"Rio Claro/SP, CEP 13500-270, e e-mail: pnsarc@hotmail.com, doravante denominada CONTROLADORA."
        ,style
    )
    frame = Frame(50, height - 460, 500, 200)
    frame.addFromList([paragrafo], c)
    
    paragrafo = Paragraph(
        f"2) Nossos dados serão utilizados exclusivamente para:<br/>"
        f"    I) O tratamento dos dados pessoais será realizado especificamente para a inscrição, organização e acompanhamento do Curso de Noivos, a fim de atender às exigências pastorais e administrativas relacionadas à preparação para o matrimônio.;<br/>"
        f"    II) Declaramos ciência de que não haverá utilização dos dados para fins comerciais, divulgação indevida ou acompanhamento com terceiros estranhos às atividades religiosas.<br/>"
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
    frame = Frame(50, height - 610, 500, 200)
    frame.addFromList([paragrafo], c)
    

    paragrafo = Paragraph(
        f"4) Declaro estar ciente de que o armazenamento ocorrerá:"
        f"I) Em fichas físicas e/ou sistemas informatizados da Paróquia;<br/>"
        f"II) Que o acesso será restrito a pessoas autorizadas (secretaria, coordenação da catequese, catequistas e o Pároco, quando necessário);<br/>"
        f"III) Que a CONTROLADORA adotará medidas técnicas e administrativas adequadas para proteger os dados contra acessos não autorizados, perda, divulgação indevida ou qualquer forma de tratamento inadequado.<br/>"
        ,style
    )
    frame = Frame(50, height - 690, 500, 200)
    frame.addFromList([paragrafo], c)
    
    paragrafo = Paragraph(
        f"5) Os dados serão mantidos enquanto estiver matriculado(a) na Catequese, pelo prazo máximo de 3 (três) anos, quando concluída o curso de noivos, respeitando-se a necessidade de registros paroquiais.<br/>"
        f"6) Estamos cientes de que podemos, a qualquer momento solicitar acesso aos nossos dados pessoais; solicitar correção de dados incompletos, inexatos ou desatualizados; requerer a eliminação de dados desnecessários, excessivos ou tratados em desconformidade com a lei.<br/>"
        f"7) Declaramos, ainda, estarmos cientes de que podemos revogar este consentimento a qualquer momento, mediante solicitação formal e por escrito à Secretaria Paroquial.<br/>"
        ,style
    )
    frame = Frame(50, height - 800, 500, 200)
    frame.addFromList([paragrafo], c)
   
    paragrafo = Paragraph(f"Rio Claro, {data_hoje()}",style)
    frame = Frame(250, height - 940, 500, 200)
    frame.addFromList([paragrafo], c)

    # Três colunas: noivo, noiva e a conferência da secretaria
    paragrafo = Paragraph(f"_________________________<br/>{ficha.nome_noivo}", style)
    frame = Frame(50, height - 980, 170, 200)
    frame.addFromList([paragrafo], c)

    paragrafo = Paragraph(f"_________________________<br/>{ficha.nome_noiva}", style)
    frame = Frame(220, height - 980, 170, 200)
    frame.addFromList([paragrafo], c)

    desenhar_verificacao_secretaria(c, height - 980, linhas_antes=0, x=390, largura=170, tracos=25)
    
    c.showPage()  # Página 3 
    
    desenhar_cabecalho(c, img_path, height, y=140)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(160, height - 160, f"AUTORIZAÇÃO PARA USO DE IMAGEM")
    
    style = estilo_paragrafo()

    paragrafo = Paragraph(
        f"Nós, <b>{ficha.nome_noivo}</b> e <b>{ficha.nome_noiva}</b>,  "
        f", autorizamos, de forma livre, expressa e informada, a Paróquia Nossa Senhora Aparecida, inscrita "
        f"no CNPJ sob o nº 44.802.999/0011-30, a utilizar a minha imagem, nome e voz, captados em fotografias e/ou vídeos durante atividades e eventos da paróquia, para fins de divulgação em meios impressos, digitais e redes sociais da paróquia, sem qualquer ônus."
        ,style
    )
    frame = Frame(50, height - 400, 500, 200)
    frame.addFromList([paragrafo], c)

    paragrafo = Paragraph(
        f"Declaramos estar cientes de que a utilização da nossa imagem será feita de acordo com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018 - LGPD), e que podemos, a qualquer momento, revogar esta autorização mediante solicitação por escrito à paróquia. "
        ,style
    )
    frame = Frame(50, height - 480, 500, 200)
    frame.addFromList([paragrafo], c)

    paragrafo = Paragraph(
        f"Estamos cientes de que não temos direito a qualquer remuneração pelo uso da nossa imagem, nome e voz nos termos acima mencionados, e que a presente autorização é concedida por prazo indeterminado, podendo ser revogada a qualquer momento, mediante comunicação por escrito. "
        ,style
    )
    frame = Frame(50, height - 530, 500, 200)
    frame.addFromList([paragrafo], c)
    
    paragrafo = Paragraph(
        f"Por fim, declaramos que a presente autorização foi feita de forma livre, sem qualquer coação, e que fomos devidamente informados sobre o tratamento dos dados pessoais pela paróquia. "
        ,style
    )
    frame = Frame(50, height - 580, 500, 200)
    frame.addFromList([paragrafo], c)

    paragrafo = Paragraph(f"Rio Claro, {data_hoje()}",style)
    frame = Frame(250, height - 630, 500, 200)
    frame.addFromList([paragrafo], c)

    # Três colunas: noivo, noiva e a conferência da secretaria
    paragrafo = Paragraph(f"_________________________<br/>{ficha.nome_noivo}", style)
    frame = Frame(50, height - 670, 170, 200)
    frame.addFromList([paragrafo], c)

    paragrafo = Paragraph(f"_________________________<br/>{ficha.nome_noiva}", style)
    frame = Frame(220, height - 670, 170, 200)
    frame.addFromList([paragrafo], c)

    desenhar_verificacao_secretaria(c, height - 670, linhas_antes=0, x=390, largura=170, tracos=25)

    
    

    c.save()

    return filename
