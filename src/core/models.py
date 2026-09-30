from django.db import models
from django.utils import timezone


class Turma(models.Model):
    """Turma/horário da Catequese Infantil, gerenciável pela coordenação.

    Substitui as escolhas fixas que antes viviam em código (comentar/descomentar
    uma tupla para "desativar" um horário). Ativar, desativar, criar uma turma
    nova ou definir o limite de vagas passa a ser um cadastro, não um deploy.
    """

    nome = models.CharField(max_length=150)
    ativa = models.BooleanField(default=True)
    vagas_maximas = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Deixe em branco para não limitar o número de inscritos.",
    )
    idade_minima = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Idade projetada mínima para o ano da catequese. Deixe em branco para não restringir.",
    )
    idade_maxima = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Idade projetada máxima para o ano da catequese. Deixe em branco para não restringir.",
    )
    ordem = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["ordem", "nome"]

    def __str__(self):
        return self.nome

    @property
    def vagas_ocupadas(self):
        return self.inscritos.count()

    @property
    def vagas_disponiveis(self):
        if self.vagas_maximas is None:
            return None
        return max(self.vagas_maximas - self.vagas_ocupadas, 0)

    @property
    def lotada(self):
        return self.vagas_maximas is not None and self.vagas_ocupadas >= self.vagas_maximas


class CatequeseInfantilModel(models.Model):
    SEXO_CHOICES = (
        ("M", "Masculino"),
        ("F", "Feminino"),
    )

    nome = models.CharField(max_length=150)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    data_nascimento = models.DateField()
    naturalidade = models.CharField(max_length=100, blank=True, null=True)

    nome_pai = models.CharField(max_length=150, default='')
    nome_mae = models.CharField(max_length=150, default='')

    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)

    celular_pai = models.CharField(max_length=20, default='')
    celular_mae = models.CharField(max_length=20, default='')

    batizado = models.BooleanField(default=False)
    batizado_data = models.DateField(blank=True, null=True)
    batizado_diocese = models.CharField(max_length=150, blank=True, null=True)
    batizado_paroquia = models.CharField(max_length=150, blank=True, null=True)
    batizado_celebrante = models.CharField(max_length=150, blank=True, null=True)
    
    turma = models.ForeignKey(
        Turma, on_delete=models.PROTECT, related_name="inscritos",
    )

    possui_deficiencia = models.BooleanField(default=False)
    descricao_deficiencia = models.TextField(blank=True, null=True)

    possui_transtorno = models.BooleanField(default=False)
    descricao_transtorno = models.TextField(blank=True, null=True)

    medicamento_uso_continuo = models.BooleanField(default=False)
    descricao_medicamento = models.TextField(blank=True, null=True)
    medicamento_horario = models.CharField(max_length=100, blank=True, null=True)

    acompanhamento_psicologico = models.BooleanField(default=False)
    descricao_acompanhamento = models.TextField(blank=True, null=True)

    # Termo de uso de Imagem

    nome_responsavel = models.CharField(max_length=150)
    cpf_responsavel = models.CharField(max_length=14)
    endereco_responsavel = models.CharField(max_length=255)

    # Ficha Impressa
    ficha_impressa = models.BooleanField(default=False)
    ficha_assinada = models.BooleanField(default=False)

    criado_em = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nome


class CrismaModel(models.Model):
    SEXO_CHOICES = (
        ("M", "Masculino"),
        ("F", "Feminino"),
    )
    HORARIO_CRISMA = (
        ("1", "Quinta às 19:30h"),
        ("2", "Sábado às 09h"),
        ("3", "Sábado às 10:30h"),
    )
    
    nome = models.CharField(max_length=150)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    data_nascimento = models.DateField()
    naturalidade = models.CharField(max_length=100, blank=True, null=True)

    nome_pai = models.CharField(max_length=150, default='')
    nome_mae = models.CharField(max_length=150, default='')

    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)

    celular_pai = models.CharField(max_length=20, default='')
    celular_mae = models.CharField(max_length=20, default='')

    batizado = models.BooleanField(default=False)
    batizado_data = models.DateField(blank=True, null=True)
    batizado_diocese = models.CharField(max_length=150, blank=True, null=True)
    batizado_paroquia = models.CharField(max_length=150, blank=True, null=True)
    batizado_celebrante = models.CharField(max_length=150, blank=True, null=True)
    
    primeira_eucaristia = models.BooleanField(default=False)
    primeira_eucaristia_data = models.DateField(blank=True, null=True)
    primeira_eucaristia_diocese = models.CharField(max_length=150, blank=True, null=True)
    primeira_eucaristia_paroquia = models.CharField(max_length=150, blank=True, null=True)
    primeira_eucaristia_celebrante = models.CharField(max_length=150, blank=True, null=True)
   
    horario = models.CharField(max_length=2, choices=HORARIO_CRISMA)

    padrinho_nome = models.CharField(max_length=150, blank=True, null=True, default='')    
    padrinho_celular = models.CharField(max_length=20, blank=True, null=True, default='')

    # Apoio Especial

    possui_deficiencia = models.BooleanField(default=False)
    descricao_deficiencia = models.TextField(blank=True, null=True)
    
    possui_transtorno = models.BooleanField(default=False)
    descricao_transtorno = models.TextField(blank=True, null=True)
    
    medicamento_uso_continuo = models.BooleanField(default=False)
    descricao_medicamento = models.TextField(blank=True, null=True)
    medicamento_horario = models.CharField(max_length=100, blank=True, null=True)
    
    acompanhamento_psicologico = models.BooleanField(default=False)
    descricao_acompanhamento = models.TextField(blank=True, null=True)

    # Termo de uso de Imagem
    
    nome_responsavel = models.CharField(max_length=150,default='')
    cpf_responsavel = models.CharField(max_length=14,default='')
    endereco_responsavel = models.CharField(max_length=255,default='')
    
    # Ficha Impressa
    ficha_impressa = models.BooleanField(default=False)
    ficha_assinada = models.BooleanField(default=False)
    
    criado_em = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nome


class Perseveranca_MEJ_Model(models.Model):
    SEXO_CHOICES = (
        ("M", "Masculino"),
        ("F", "Feminino"),
    )
    
    HORARIO_PERSEVERANCA = (
        ("1", "Perseverança e MEJ - 11 a 14 anos - Quinta às 19:30h - Encontros na Capela NSGraças"),
        ("2", "MEJ - 15 a 25 anos - Quinta às 19:30h - Encontros na Capela NSGraças"),
        ("3", "Perseverança e MEJ - 11 a 14 anos - Terça às 19:30h - Encontros na Capela NSGraças"),
        ("4", "MEJ - 15 a 25 anos - Terça às 19:30h - Encontros na Capela NSGraças"),
    )

    nome = models.CharField(max_length=150)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    data_nascimento = models.DateField()
    naturalidade = models.CharField(max_length=100, blank=True, null=True)

    nome_pai = models.CharField(max_length=150, default='')
    nome_mae = models.CharField(max_length=150, default='')

    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)

    celular_pai = models.CharField(max_length=20, default='')
    celular_mae = models.CharField(max_length=20, default='')

    batizado = models.BooleanField(default=False)
    batizado_data = models.DateField(blank=True, null=True)
    batizado_diocese = models.CharField(max_length=150, blank=True, null=True)
    batizado_paroquia = models.CharField(max_length=150, blank=True, null=True)
    batizado_celebrante = models.CharField(max_length=150, blank=True, null=True)

    primeira_eucaristia = models.BooleanField(default=False)
    primeira_eucaristia_data = models.DateField(blank=True, null=True)
    primeira_eucaristia_diocese = models.CharField(max_length=150, blank=True, null=True)
    primeira_eucaristia_paroquia = models.CharField(max_length=150, blank=True, null=True)
    primeira_eucaristia_celebrante = models.CharField(max_length=150, blank=True, null=True)

    horario = models.CharField(max_length=2, choices=HORARIO_PERSEVERANCA)
    
    possui_deficiencia = models.BooleanField(default=False)
    descricao_deficiencia = models.TextField(blank=True, null=True)
    
    possui_transtorno = models.BooleanField(default=False)
    descricao_transtorno = models.TextField(blank=True, null=True)
    
    medicamento_uso_continuo = models.BooleanField(default=False)
    descricao_medicamento = models.TextField(blank=True, null=True)
    medicamento_horario = models.CharField(max_length=100, blank=True, null=True)
    
    acompanhamento_psicologico = models.BooleanField(default=False)
    descricao_acompanhamento = models.TextField(blank=True, null=True)
    
    # Termo de uso de Imagem
    
    nome_responsavel = models.CharField(max_length=150)
    cpf_responsavel = models.CharField(max_length=14)
    endereco_responsavel = models.CharField(max_length=255)
    
    # Ficha Impressa
    ficha_impressa = models.BooleanField(default=False)
    ficha_assinada = models.BooleanField(default=False)

    criado_em = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.nome


class CatequeseAdultoModel(models.Model):
    SEXO_CHOICES = (
        ("M", "Masculino"),
        ("F", "Feminino"),
    )
    HORARIO_CATEQUESE_ADULTO = (
#        ("1", "Terça às 19:30h - COM Batismo"),
#        ("3", "Quarta às 19:30h - COM Batismo"),
        ("4", "Quinta às 19:30h - SEM Batismo"),
#        ("2", "Sábado às 08h - COM Batismo"),
        ("5", "Sábado às 09h - SEM Batismo"),
    )
    
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14,default='')
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    celular = models.CharField(max_length=20, default='')
    data_nascimento = models.DateField()
    naturalidade = models.CharField(max_length=100, blank=True, null=True)

    nome_pai = models.CharField(max_length=150, default='')
    nome_mae = models.CharField(max_length=150, default='')

    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    estado_civil = models.CharField(max_length=50)

    batizado = models.BooleanField(default=False)
    batizado_data = models.DateField(blank=True, null=True)
    batizado_diocese = models.CharField(max_length=150, blank=True, null=True)
    batizado_paroquia = models.CharField(max_length=150, blank=True, null=True)
    batizado_celebrante = models.CharField(max_length=150, blank=True, null=True)
    
    primeira_eucaristia = models.BooleanField(default=False)
    primeira_eucaristia_data = models.DateField(blank=True, null=True)
    primeira_eucaristia_diocese = models.CharField(max_length=150, blank=True, null=True)
    primeira_eucaristia_paroquia = models.CharField(max_length=150, blank=True, null=True)
    primeira_eucaristia_celebrante = models.CharField(max_length=150, blank=True, null=True)

    casado_igreja = models.BooleanField(default=False)
    casado_igreja_data = models.DateField(blank=True, null=True)
    casado_igreja_diocese = models.CharField(max_length=150, blank=True, null=True)
    casado_igreja_paroquia = models.CharField(max_length=150, blank=True, null=True)
    casado_igreja_celebrante = models.CharField(max_length=150, blank=True, null=True)

    horario = models.CharField(max_length=2, choices=HORARIO_CATEQUESE_ADULTO)

    padrinho_nome = models.CharField(max_length=150, blank=True, null=True, default='')    
    padrinho_celular = models.CharField(max_length=20, blank=True, null=True, default='')
    
    # Ficha Impressa
    ficha_impressa = models.BooleanField(default=False)
    ficha_assinada = models.BooleanField(default=False)

    criado_em = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nome
    
class NoivoModel(models.Model):
    nome_noivo = models.CharField(max_length=150)
    endereco_noivo = models.CharField(max_length=255)
    celular_noivo = models.CharField(max_length=20, default='')
    data_nascimento_noivo = models.DateField()
    profissao_noivo = models.CharField(max_length=100)
    local_trabalho_noivo = models.CharField(max_length=100)
    religiao_noivo = models.CharField(max_length=100)
    restricao_alimentar_noivo = models.CharField(max_length=100)
    nome_pai_noivo = models.CharField(max_length=150, default='')
    nome_mae_noivo = models.CharField(max_length=150, default='')
    endereco_pais_noivo = models.CharField(max_length=255)
    celular_pais_noivo = models.CharField(max_length=20, default='')
    religiao_pais_noivo = models.CharField(max_length=100)

    nome_noiva = models.CharField(max_length=150)
    endereco_noiva = models.CharField(max_length=255)
    celular_noiva = models.CharField(max_length=20, default='')
    data_nascimento_noiva = models.DateField()
    profissao_noiva = models.CharField(max_length=100)
    local_trabalho_noiva = models.CharField(max_length=100)
    religiao_noiva = models.CharField(max_length=100)
    restricao_alimentar_noiva = models.CharField(max_length=100)
    nome_pai_noiva = models.CharField(max_length=150, default='')
    nome_mae_noiva = models.CharField(max_length=150, default='')
    endereco_pais_noiva = models.CharField(max_length=255)
    celular_pais_noiva = models.CharField(max_length=20, default='')
    religiao_pais_noiva = models.CharField(max_length=100)      
    
    data_provavel_casamento = models.DateField()
    paroquia_casamento = models.CharField(max_length=100)      

    # Ficha Impressa
    ficha_impressa = models.BooleanField(default=False)
    ficha_assinada = models.BooleanField(default=False)

    criado_em = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.nome_noivo + " e " + self.nome_noiva


class CoroinhaModel(models.Model):
    SEXO_CHOICES = (
        ("M", "Masculino"),
        ("F", "Feminino"),
    )
    nome = models.CharField(max_length=150)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    data_nascimento = models.DateField()
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)

    nome_pai = models.CharField(max_length=150, default='')
    celular_pai = models.CharField(max_length=20, default='')
    nome_mae = models.CharField(max_length=150, default='')
    celular_mae = models.CharField(max_length=20, default='')

    # Termo de uso de Imagem
    
    nome_responsavel = models.CharField(max_length=150)
    cpf_responsavel = models.CharField(max_length=14)
    endereco_responsavel = models.CharField(max_length=255)
    
    # Ficha Impressa
    ficha_impressa = models.BooleanField(default=False)
    ficha_assinada = models.BooleanField(default=False)

    criado_em = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.nome
