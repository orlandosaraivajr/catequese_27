from django.utils.timezone import localtime
import openpyxl

from core.models import CatequeseInfantilModel, SementinhaModel, CrismaModel, Perseveranca_MEJ_Model, CatequeseAdultoModel, CoroinhaModel, NoivoModel


def _planilha_infantil(ws, qs, coluna_horario):
    """Catequese Infantil e Sementinha têm os mesmos campos; muda só a coluna do horário."""
    list_header = ['Nome','Sexo','Data de Nascimento','Naturalidade','Nome do Pai','Nome da Mãe','Endereço','Cidade','UF','Celular do Pai','Celular da Mãe',]
    list_header += ['Batizado','Data do Batismo','Diocese do Batismo','Paróquia do Batismo','Celebrante do Batismo']
    list_header += [coluna_horario]
    list_header += ['Possui Deficiência', 'Descrição da Deficiência', 'Possui Transtorno', 'Descrição do Transtorno']
    list_header += ['Medicamento de Uso Contínuo',  'Descrição do Medicamento', 'Horário do Medicamento']
    list_header += ['Acompanhamento Psicológico','Descrição do Acompanhamento',]
    list_header += ['Nome do Responsável','CPF do Responsável','Endereço do Responsável']
    list_header += ['Ficha Impressa','Ficha Assinada','Data de Registro']
    ws.append(list_header)
    for registro in qs:
        ws.append([
            registro.nome,
            registro.sexo,
            registro.data_nascimento.strftime('%d/%m/%Y') if registro.data_nascimento else '',
            registro.naturalidade,
            registro.nome_pai,
            registro.nome_mae,
            registro.endereco,
            registro.cidade,
            registro.uf,
            registro.celular_pai,
            registro.celular_mae,
            'Sim' if registro.batizado else 'Não',
            registro.batizado_data.strftime('%d/%m/%Y') if registro.batizado_data else 'NÃO BATIZADO',
            registro.batizado_diocese,
            registro.batizado_paroquia,
            registro.batizado_celebrante,
            registro.turma.nome,
            'Sim' if registro.possui_deficiencia else 'Não',
            registro.descricao_deficiencia,
            'Sim' if registro.possui_transtorno else 'Não',
            registro.descricao_transtorno,
            'Sim' if registro.medicamento_uso_continuo else 'Não',
            registro.descricao_medicamento,
            registro.medicamento_horario,
            'Sim' if registro.acompanhamento_psicologico else 'Não',
            registro.descricao_acompanhamento,
            registro.nome_responsavel,
            registro.cpf_responsavel,
            registro.endereco_responsavel,
            "Sim" if registro.ficha_impressa else "Não",
            "Sim" if registro.ficha_assinada else "Não",    
            localtime(registro.criado_em).strftime('%d/%m/%Y - %H:%M:%S') if registro.criado_em else '',
        ])


def gerar_Workbook():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Catequese Infantil"
    _planilha_infantil(ws, CatequeseInfantilModel.objects.all().order_by('id'), 'Horário da Catequese')

    ws = wb.create_sheet(title="Sementinha")
    _planilha_infantil(ws, SementinhaModel.objects.all().order_by('id'), 'Horário da Sementinha')

    ws = wb.create_sheet(title="Crisma")
    
    qs = CrismaModel.objects.all().order_by('id')
    list_header = [
        'Nome',
        'Sexo',
        'Data de Nascimento',
        'Naturalidade',
        'Nome do Pai',
        'Nome da Mãe',
        'Endereço',
        'Cidade',
        'UF',
        'Celular do Pai',
        'Celular da Mãe',
]

    list_header += [
        'Batizado',
        'Data do Batismo',
        'Diocese do Batismo',
        'Paróquia do Batismo',
        'Celebrante do Batismo',
    ]

    list_header += [
        'Primeira Eucaristia',
        'Data da Primeira Eucaristia',
        'Diocese da Primeira Eucaristia',
        'Paróquia da Primeira Eucaristia',
        'Celebrante da Primeira Eucaristia',
    ]

    list_header += [
        'Horário da Crisma',
        'Nome do Padrinho',
        'Celular do Padrinho',
    ]

    list_header += [
        'Possui Deficiência',
        'Descrição da Deficiência',
        'Possui Transtorno',
        'Descrição do Transtorno',
    ]

    list_header += [
        'Medicamento de Uso Contínuo',
        'Descrição do Medicamento',
        'Horário do Medicamento',
    ]

    list_header += [
        'Acompanhamento Psicológico',
        'Descrição do Acompanhamento',
    ]

    list_header += [
        'Nome do Responsável',
        'CPF do Responsável',
        'Endereço do Responsável',
    ]

    list_header += [
        'Ficha Impressa',
        'Ficha Assinada',
        'Data de Registro',
    ]

    ws.append(list_header)

    for registro in qs:
        ws.append([
            registro.nome,
            registro.sexo,
            registro.data_nascimento.strftime('%d/%m/%Y') if registro.data_nascimento else '',
            registro.naturalidade,
            registro.nome_pai,
            registro.nome_mae,
            registro.endereco,
            registro.cidade,
            registro.uf,
            registro.celular_pai,
            registro.celular_mae,

            'Sim' if registro.batizado else 'Não',
            registro.batizado_data.strftime('%d/%m/%Y') if registro.batizado_data else 'NÃO BATIZADO',
            registro.batizado_diocese,
            registro.batizado_paroquia,
            registro.batizado_celebrante,

            'Sim' if registro.primeira_eucaristia else 'Não',
            registro.primeira_eucaristia_data.strftime('%d/%m/%Y') if registro.primeira_eucaristia_data else 'NÃO REALIZADA',
            registro.primeira_eucaristia_diocese,
            registro.primeira_eucaristia_paroquia,
            registro.primeira_eucaristia_celebrante,

            registro.turma.nome,
            registro.padrinho_nome,
            registro.padrinho_celular,

            'Sim' if registro.possui_deficiencia else 'Não',
            registro.descricao_deficiencia,

            'Sim' if registro.possui_transtorno else 'Não',
            registro.descricao_transtorno,

            'Sim' if registro.medicamento_uso_continuo else 'Não',
            registro.descricao_medicamento,
            registro.medicamento_horario,

            'Sim' if registro.acompanhamento_psicologico else 'Não',
            registro.descricao_acompanhamento,

            registro.nome_responsavel,
            registro.cpf_responsavel,
            registro.endereco_responsavel,

            'Sim' if registro.ficha_impressa else 'Não',
            'Sim' if registro.ficha_assinada else 'Não',

            localtime(registro.criado_em).strftime('%d/%m/%Y - %H:%M:%S') if registro.criado_em else '',
        ])
    
    ws = wb.create_sheet(title="Perseverança MEJ")
    
    qs = Perseveranca_MEJ_Model.objects.all().order_by('id')
    list_header = [
        'Nome',
        'Sexo',
        'Data de Nascimento',
        'Naturalidade',
        'Nome do Pai',
        'Nome da Mãe',
        'Endereço',
        'Cidade',
        'UF',
        'Celular do Pai',
        'Celular da Mãe',
    ]

    list_header += [
        'Batizado',
        'Data do Batismo',
        'Diocese do Batismo',
        'Paróquia do Batismo',
        'Celebrante do Batismo',
    ]

    list_header += [
        'Primeira Eucaristia',
        'Data da Primeira Eucaristia',
        'Diocese da Primeira Eucaristia',
        'Paróquia da Primeira Eucaristia',
        'Celebrante da Primeira Eucaristia',
    ]

    list_header += [
        'Horário da Perseverança / MEJ',
    ]

    list_header += [
        'Possui Deficiência',
        'Descrição da Deficiência',
        'Possui Transtorno',
        'Descrição do Transtorno',
    ]

    list_header += [
        'Medicamento de Uso Contínuo',
        'Descrição do Medicamento',
        'Horário do Medicamento',
    ]

    list_header += [
        'Acompanhamento Psicológico',
        'Descrição do Acompanhamento',
    ]

    list_header += [
        'Nome do Responsável',
        'CPF do Responsável',
        'Endereço do Responsável',
    ]

    list_header += [
        'Ficha Impressa',
        'Ficha Assinada',
        'Data de Registro',
    ]

    ws.append(list_header)

    for registro in qs:
        ws.append([
            registro.nome,
            registro.sexo,
            registro.data_nascimento.strftime('%d/%m/%Y') if registro.data_nascimento else '',
            registro.naturalidade,
            registro.nome_pai,
            registro.nome_mae,
            registro.endereco,
            registro.cidade,
            registro.uf,
            registro.celular_pai,
            registro.celular_mae,

            'Sim' if registro.batizado else 'Não',
            registro.batizado_data.strftime('%d/%m/%Y') if registro.batizado_data else 'NÃO BATIZADO',
            registro.batizado_diocese,
            registro.batizado_paroquia,
            registro.batizado_celebrante,

            'Sim' if registro.primeira_eucaristia else 'Não',
            registro.primeira_eucaristia_data.strftime('%d/%m/%Y') if registro.primeira_eucaristia_data else 'NÃO REALIZADA',
            registro.primeira_eucaristia_diocese,
            registro.primeira_eucaristia_paroquia,
            registro.primeira_eucaristia_celebrante,

            registro.turma.nome,

            'Sim' if registro.possui_deficiencia else 'Não',
            registro.descricao_deficiencia,

            'Sim' if registro.possui_transtorno else 'Não',
            registro.descricao_transtorno,

            'Sim' if registro.medicamento_uso_continuo else 'Não',
            registro.descricao_medicamento,
            registro.medicamento_horario,

            'Sim' if registro.acompanhamento_psicologico else 'Não',
            registro.descricao_acompanhamento,

            registro.nome_responsavel,
            registro.cpf_responsavel,
            registro.endereco_responsavel,

            'Sim' if registro.ficha_impressa else 'Não',
            'Sim' if registro.ficha_assinada else 'Não',

            localtime(registro.criado_em).strftime('%d/%m/%Y - %H:%M:%S') if registro.criado_em else '',
        ])
    ws = wb.create_sheet(title="Catequese Adulto")
    qs = CatequeseAdultoModel.objects.all().order_by('id')
    
    list_header = [
        'Nome',
        'Sexo',
        'Data de Nascimento',
        'Naturalidade',
        'CPF',
        'Celular',
        'Nome do Pai',
        'Nome da Mãe',
        'Endereço',
        'Cidade',
        'UF',
        'Estado Civil',
    ]

    list_header += [
        'Batizado',
        'Data do Batismo',
        'Diocese do Batismo',
        'Paróquia do Batismo',
        'Celebrante do Batismo',
    ]

    list_header += [
        'Primeira Eucaristia',
        'Data da Primeira Eucaristia',
        'Diocese da Primeira Eucaristia',
        'Paróquia da Primeira Eucaristia',
        'Celebrante da Primeira Eucaristia',
    ]

    list_header += [
        'Casado na Igreja',
        'Data do Casamento',
        'Diocese do Casamento',
        'Paróquia do Casamento',
        'Celebrante do Casamento',
    ]

    list_header += [
        'Horário da Catequese (Adulto)',
        'Nome do Padrinho',
        'Celular do Padrinho',
    ]

    list_header += [
        'Ficha Impressa',
        'Ficha Assinada',
        'Data de Registro',
    ]

    ws.append(list_header)

    for registro in qs:
        ws.append([
            registro.nome,
            registro.sexo,
            registro.data_nascimento.strftime('%d/%m/%Y') if registro.data_nascimento else '',
            registro.naturalidade,
            registro.cpf,
            registro.celular,
            registro.nome_pai,
            registro.nome_mae,
            registro.endereco,
            registro.cidade,
            registro.uf,
            registro.estado_civil,

            'Sim' if registro.batizado else 'Não',
            registro.batizado_data.strftime('%d/%m/%Y') if registro.batizado_data else 'NÃO BATIZADO',
            registro.batizado_diocese,
            registro.batizado_paroquia,
            registro.batizado_celebrante,

            'Sim' if registro.primeira_eucaristia else 'Não',
            registro.primeira_eucaristia_data.strftime('%d/%m/%Y') if registro.primeira_eucaristia_data else 'NÃO REALIZADA',
            registro.primeira_eucaristia_diocese,
            registro.primeira_eucaristia_paroquia,
            registro.primeira_eucaristia_celebrante,

            'Sim' if registro.casado_igreja else 'Não',
            registro.casado_igreja_data.strftime('%d/%m/%Y') if registro.casado_igreja_data else 'NÃO INFORMADO',
            registro.casado_igreja_diocese,
            registro.casado_igreja_paroquia,
            registro.casado_igreja_celebrante,

            registro.turma.nome,
            registro.padrinho_nome,
            registro.padrinho_celular,

            'Sim' if registro.ficha_impressa else 'Não',
            'Sim' if registro.ficha_assinada else 'Não',

            localtime(registro.criado_em).strftime('%d/%m/%Y - %H:%M:%S') if registro.criado_em else '',
        ])
    return wb


def gerar_Workbook_coroinhas():
    """Relatório próprio do fluxo Coroinhas (não faz parte do relatório da catequese)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Coroinhas"
    list_header = ['Nome','Sexo','Data de Nascimento','Endereço','Cidade','UF']
    list_header += ['Nome do Pai','Celular do Pai','Nome da Mãe','Celular da Mãe']
    list_header += ['Nome do Responsável','CPF do Responsável','Endereço do Responsável']
    list_header += ['Ficha Impressa','Ficha Assinada','Data de Registro']
    ws.append(list_header)
    for registro in CoroinhaModel.objects.all().order_by('id'):
        ws.append([
            registro.nome,
            registro.sexo,
            registro.data_nascimento.strftime('%d/%m/%Y') if registro.data_nascimento else '',
            registro.endereco,
            registro.cidade,
            registro.uf,
            registro.nome_pai,
            registro.celular_pai,
            registro.nome_mae,
            registro.celular_mae,
            registro.nome_responsavel,
            registro.cpf_responsavel,
            registro.endereco_responsavel,
            "Sim" if registro.ficha_impressa else "Não",
            "Sim" if registro.ficha_assinada else "Não",
            localtime(registro.criado_em).strftime('%d/%m/%Y - %H:%M:%S') if registro.criado_em else '',
        ])
    return wb


# Colunas repetidas para o noivo e para a noiva: (título, sufixo do campo no modelo).
CAMPOS_NOIVOS = [
    ('Nome', 'nome'), ('Endereço', 'endereco'), ('Celular', 'celular'),
    ('Data de Nascimento', 'data_nascimento'), ('Profissão', 'profissao'),
    ('Local de Trabalho', 'local_trabalho'), ('Religião', 'religiao'),
    ('Restrição Alimentar', 'restricao_alimentar'), ('Nome do Pai', 'nome_pai'),
    ('Nome da Mãe', 'nome_mae'), ('Endereço dos Pais', 'endereco_pais'),
    ('Celular dos Pais', 'celular_pais'), ('Religião dos Pais', 'religiao_pais'),
]


def gerar_Workbook_casamento():
    """Relatório próprio do fluxo Casamento (curso de noivos)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Casamento"
    list_header = []
    for pessoa in ('Noivo', 'Noiva'):
        list_header += [f'{titulo} ({pessoa})' for titulo, _ in CAMPOS_NOIVOS]
    list_header += ['Data Provável do Casamento', 'Paróquia do Casamento']
    list_header += ['Ficha Impressa', 'Ficha Assinada', 'Data de Registro']
    ws.append(list_header)
    for registro in NoivoModel.objects.all().order_by('id'):
        linha = []
        for pessoa in ('noivo', 'noiva'):
            for _, campo in CAMPOS_NOIVOS:
                valor = getattr(registro, f'{campo}_{pessoa}')
                linha.append(valor.strftime('%d/%m/%Y') if campo == 'data_nascimento' and valor else valor)
        linha += [
            registro.data_provavel_casamento.strftime('%d/%m/%Y') if registro.data_provavel_casamento else '',
            registro.paroquia_casamento,
            "Sim" if registro.ficha_impressa else "Não",
            "Sim" if registro.ficha_assinada else "Não",
            localtime(registro.criado_em).strftime('%d/%m/%Y - %H:%M:%S') if registro.criado_em else '',
        ]
        ws.append(linha)
    return wb
