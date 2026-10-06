from reportlab.lib import colors
from reportlab.platypus import Frame, Paragraph

from ._common import (
    desenhar_verificacao_secretaria,
    CABECALHO_PATH,
    novo_canvas,
    desenhar_cabecalho,
    estilo_paragrafo,
    data_hoje,
    pagina_termo_consentimento_menor_catequese,
    pagina_autorizacao_imagem_menor,
)


def gerar_ficha_catequese(ficha):
    img_path = CABECALHO_PATH
    c, height, filename = novo_canvas(f"ficha_catequese_{ficha.id}.pdf")

    desenhar_cabecalho(c, img_path, height, y=200)
    c.setFont("Helvetica", 16)
    c.drawString(130, height - 220, f"INSCRIÇÃO PARA CATEQUESE INFANTIL")
    
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
    c.setFont("Helvetica", 11)
    c.drawString(150, height - 280, f"{ficha.data_nascimento.strftime("%d/%m/%Y")}")
    
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
        c.drawString(150, height - 310, f"{ficha.nome_pai}  -  {ficha.celular_pai}")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 325, f"Mãe:")
    c.setFont("Helvetica", 11)
    if ficha.nome_mae:
        c.drawString(150, height - 325, f"{ficha.nome_mae}  -  {ficha.celular_mae}")

    # Endereço
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 340, f"Endereço:")
    c.setFont("Helvetica", 11)
    c.drawString(150, height - 340, f"{ficha.endereco}")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 355, f"Cidade:")
    c.setFont("Helvetica", 11)
    c.drawString(150, height - 355, f"{ficha.cidade}  -  {ficha.uf}")
    
    # Batizado
    c.setFont("Helvetica-Bold", 11)
    if ficha.batizado:
        c.drawString(50, height - 375, f"Batizado")
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 390, f"Data: {ficha.batizado_data.strftime("%d/%m/%Y") if ficha.batizado_data else ''}")
        c.drawString(50, height - 405, f"Diocese: {ficha.batizado_diocese}   Paróquia: {ficha.batizado_paroquia}")
        c.drawString(50, height - 420, f"Celebrante: {ficha.batizado_celebrante} ")
        
    else:
        c.setFillColor(colors.red)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, height - 375, f"Não Batizado")
        c.setFillColor(colors.black)
    
    
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 440, f"Horário:")
    c.setFillColor(colors.blue)
    c.drawString(150, height - 440, f"{ficha.turma.nome} ")
    c.setFillColor(colors.black)
    
# Cuidado e Acolhimento da Criança
    c.setFont("Helvetica-Bold", 16)
    c.drawString(170, height - 480, "Cuidado e Acolhimento da Criança")   
    c.setFont("Helvetica", 11)
    
    style = estilo_paragrafo()

    paragrafo = Paragraph(
        "Para que possamos receber seu filho(a) com todo carinho, atenção e segurança, "
        "pedimos que compartilhe conosco algumas informações importantes. "
        "Tudo será tratado com sigilo e usado apenas para ajudar no bem-estar "
        "da criança durante as atividades.",
        style
    )

    frame = Frame(50, height - 700, 500, 200)  # x, y, largura, altura
    frame.addFromList([paragrafo], c)
    
# 1 Deficiência ou Necessidade Especial
    paragrafo = Paragraph(
        "1. Seu filho(a) possui alguma deficiência que devemos conhecer para acolhê-lo(a) "
        "da melhor forma?",
        style
    )
    frame = Frame(50, height - 750, 500, 200)
    frame.addFromList([paragrafo], c)
    if ficha.possui_deficiencia:
        paragrafo = Paragraph(
            f"Sim. Descrição: {ficha.descricao_deficiencia}",
            style
        )
    else:
        paragrafo = Paragraph(
            "Não.",
            style
        )
    frame = Frame(50, height - 780, 500, 200)
    frame.addFromList([paragrafo], c)

# 2 Transtornos
    paragrafo = Paragraph(
        "2. Há algum transtorno ou diagnóstico que ajude nossa pastoral a compreender melhor as necessidades da criança?",
        style
    )
    frame = Frame(50, height - 795, 500, 200)
    frame.addFromList([paragrafo], c)    
    if ficha.possui_transtorno:
        paragrafo = Paragraph(
            f"Sim. Descrição: {ficha.descricao_transtorno}",
            style
        )
    else:
        paragrafo = Paragraph(
            "Não.",
            style
        )
    frame = Frame(50, height - 825, 500, 200)
    frame.addFromList([paragrafo], c)
    
# 3 Medicamentos
    paragrafo = Paragraph(
        "3. Seu filho(a) faz uso de algum medicamento contínuo?",
        style
    )
    frame = Frame(50, height - 840, 500, 200)
    frame.addFromList([paragrafo], c)    
    if ficha.medicamento_uso_continuo:
        paragrafo = Paragraph(
            f"Sim. Descrição: {ficha.descricao_medicamento}. Horário: {ficha.medicamento_horario}",
            style
        )
    else:
        paragrafo = Paragraph(
            "Não.",
            style
        )
    frame = Frame(50, height - 855, 500, 200)
    frame.addFromList([paragrafo], c)   
    
# 4 Acompanhamento Psicológico
    paragrafo = Paragraph(
        "4. A criança faz acompanhamento psicológico, psiquiátrico ou terapêutico?",
        style
    )
    frame = Frame(50, height - 870, 500, 200)
    frame.addFromList([paragrafo], c)    
    if ficha.acompanhamento_psicologico:
        paragrafo = Paragraph(
            f"Sim. Descrição: {ficha.descricao_acompanhamento}",
            style
        )
    else:
        paragrafo = Paragraph(
            "Não.",
            style
        )
    frame = Frame(50, height - 885, 500, 200)
    frame.addFromList([paragrafo], c)

    paragrafo = Paragraph(
            "Agradecemos de coração pela confiança. Nosso desejo é caminhar juntos para que a criança viva cada momento com alegria, segurança e acolhimento.",
        style
    )
    frame = Frame(50, height - 900, 500, 200)
    frame.addFromList([paragrafo], c)
    paragrafo = Paragraph(
            f"Rio Claro, {data_hoje()}<br/><br/> _____________________________________________<br/> Assinatura do Responsável",
        style
    )
    frame = Frame(250, height - 940, 500, 200)
    frame.addFromList([paragrafo], c)
    desenhar_verificacao_secretaria(c, height - 940)
    
    
    

    c.showPage()  # Página 2
    pagina_termo_consentimento_menor_catequese(c, img_path, height, ficha)

    c.showPage()  # Página 3
    pagina_autorizacao_imagem_menor(c, img_path, height, ficha)

    c.save()

    return filename
