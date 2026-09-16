-- =====================================================================
--  ASTRA — Sistema de Gestão Escolar
--  script.sql — cria o banco, as 19 tabelas e os dados iniciais do RBAC.
--  Alvo: MySQL 8.0+ (InnoDB, utf8mb4).
--
--  Este arquivo é montado no container em /docker-entrypoint-initdb.d/,
--  então roda automaticamente na PRIMEIRA inicialização do MySQL.
--  Também pode ser executado manualmente contra um MySQL existente.
-- =====================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS astra
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
USE astra;

-- =====================================================================
--  1) IDENTIDADE E CONTROLE DE ACESSO (RBAC)
-- =====================================================================

-- Conta de acesso. status_usu cobre bloquear/ativar E soft delete.
CREATE TABLE usuario (
  id_usu            INT UNSIGNED  NOT NULL AUTO_INCREMENT,
  nome_usu          VARCHAR(150)  NOT NULL,
  email_usu         VARCHAR(255)  NOT NULL,
  senha_usu         VARCHAR(255)  NOT NULL,               -- hash bcrypt/argon2
  senha_provisoria  BOOLEAN       NOT NULL DEFAULT TRUE,  -- obriga troca no 1º acesso
  status_usu        ENUM('ATIVO','BLOQUEADO','EXCLUIDO') NOT NULL DEFAULT 'ATIVO',
  created_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id_usu),
  UNIQUE KEY uq_usuario_email (email_usu)
) ENGINE=InnoDB;

-- Papel de acesso (Admin, Secretaria, Professor, Aluno, Coordenador...).
CREATE TABLE perfil (
  id_perfil    INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nome_perfil  VARCHAR(60)  NOT NULL,
  descricao    VARCHAR(255) NULL,
  ativo        BOOLEAN      NOT NULL DEFAULT TRUE,
  PRIMARY KEY (id_perfil),
  UNIQUE KEY uq_perfil_nome (nome_perfil)
) ENGINE=InnoDB;

-- Ação atômica autorizável (ex.: 'aluno.criar', 'boletim.lancar_nota').
CREATE TABLE permissao (
  id_permissao    INT UNSIGNED NOT NULL AUTO_INCREMENT,
  chave_permissao VARCHAR(80)  NOT NULL,   -- <modulo>.<acao>
  descricao       VARCHAR(255) NULL,
  PRIMARY KEY (id_permissao),
  UNIQUE KEY uq_permissao_chave (chave_permissao)
) ENGINE=InnoDB;

-- O que o PAINEL edita: quais ações cada perfil libera (N:N).
CREATE TABLE perfil_permissao (
  id_perfil     INT UNSIGNED NOT NULL,
  id_permissao  INT UNSIGNED NOT NULL,
  PRIMARY KEY (id_perfil, id_permissao),
  CONSTRAINT fk_pp_perfil    FOREIGN KEY (id_perfil)    REFERENCES perfil(id_perfil)       ON DELETE CASCADE,
  CONSTRAINT fk_pp_permissao FOREIGN KEY (id_permissao) REFERENCES permissao(id_permissao) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Quais perfis cada usuário acumula (N:N). Autorização = UNIÃO das permissões.
CREATE TABLE usuario_perfil (
  id_usu     INT UNSIGNED NOT NULL,
  id_perfil  INT UNSIGNED NOT NULL,
  PRIMARY KEY (id_usu, id_perfil),
  CONSTRAINT fk_up_usuario FOREIGN KEY (id_usu)    REFERENCES usuario(id_usu)   ON DELETE CASCADE,
  CONSTRAINT fk_up_perfil  FOREIGN KEY (id_perfil) REFERENCES perfil(id_perfil) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =====================================================================
--  2) RECURSOS HUMANOS (cargo, funcionário, vínculos)
-- =====================================================================

-- Cargo organizacional (RH). SEPARADO de perfil (autorização).
CREATE TABLE funcao (
  id_funcao    INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nome_funcao  VARCHAR(80)  NOT NULL,
  sigla_funcao VARCHAR(10)  NULL,
  ativo        BOOLEAN      NOT NULL DEFAULT TRUE,
  PRIMARY KEY (id_funcao)
) ENGINE=InnoDB;

CREATE TABLE funcionario (
  id_func           INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nome_func         VARCHAR(150) NOT NULL,
  cpf_func          VARCHAR(14)  NOT NULL,
  tel_func          VARCHAR(20)  NULL,
  sexo_func         ENUM('M','F','O') NULL,
  dt_nasc_func      DATE         NULL,
  id_funcional_func VARCHAR(30)  NULL,          -- matrícula funcional
  id_usu            INT UNSIGNED NULL,          -- conta de acesso (1:1 lógico)
  id_funcao         INT UNSIGNED NULL,          -- cargo de RH
  ativo             BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id_func),
  UNIQUE KEY uq_funcionario_cpf (cpf_func),
  UNIQUE KEY uq_funcionario_usu (id_usu),
  CONSTRAINT fk_func_usuario FOREIGN KEY (id_usu)    REFERENCES usuario(id_usu)  ON DELETE SET NULL,
  CONSTRAINT fk_func_funcao  FOREIGN KEY (id_funcao) REFERENCES funcao(id_funcao) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE vinculo (
  id_vinc     INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nome_vinc   VARCHAR(80)  NOT NULL,
  sigla_vinc  VARCHAR(10)  NULL,
  regime_vinc VARCHAR(40)  NULL,
  ativo       BOOLEAN      NOT NULL DEFAULT TRUE,
  PRIMARY KEY (id_vinc)
) ENGINE=InnoDB;

-- Vínculos de um funcionário ao longo do tempo (N:N com período).
CREATE TABLE vinc_func (
  id_vinc_func INT UNSIGNED NOT NULL AUTO_INCREMENT,
  dt_ini       DATE         NOT NULL,
  dt_fin       DATE         NULL,
  id_func      INT UNSIGNED NOT NULL,
  id_vinc      INT UNSIGNED NOT NULL,
  PRIMARY KEY (id_vinc_func),
  KEY idx_vf_func (id_func),
  KEY idx_vf_vinc (id_vinc),
  CONSTRAINT fk_vf_func FOREIGN KEY (id_func) REFERENCES funcionario(id_func) ON DELETE CASCADE,
  CONSTRAINT fk_vf_vinc FOREIGN KEY (id_vinc) REFERENCES vinculo(id_vinc)     ON DELETE RESTRICT
) ENGINE=InnoDB;

-- =====================================================================
--  3) ESTRUTURA ACADÊMICA (curso, disciplina, turma, ano letivo)
-- =====================================================================

CREATE TABLE curso (
  id_curso    INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nome_curso  VARCHAR(120) NOT NULL,
  desc_curso  VARCHAR(255) NULL,
  ch_curso    SMALLINT UNSIGNED NULL,   -- carga horária total
  sigla_curso VARCHAR(15)  NULL,
  ativo       BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id_curso)
) ENGINE=InnoDB;

-- Escopo do coordenador: quais cursos ele coordena (N:N).
CREATE TABLE coordenacao (
  id_func   INT UNSIGNED NOT NULL,
  id_curso  INT UNSIGNED NOT NULL,
  PRIMARY KEY (id_func, id_curso),
  CONSTRAINT fk_coord_func  FOREIGN KEY (id_func)  REFERENCES funcionario(id_func) ON DELETE CASCADE,
  CONSTRAINT fk_coord_curso FOREIGN KEY (id_curso) REFERENCES curso(id_curso)      ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE disciplina (
  id_disc    INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nome_disc  VARCHAR(120) NOT NULL,
  sigla_disc VARCHAR(15)  NULL,
  ch_disc    SMALLINT UNSIGNED NULL,
  etapa      TINYINT UNSIGNED NOT NULL,   -- 1..3 (semestre do curso)
  id_curso   INT UNSIGNED NOT NULL,
  ativo      BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id_disc),
  KEY idx_disc_curso (id_curso),
  CONSTRAINT fk_disc_curso FOREIGN KEY (id_curso) REFERENCES curso(id_curso) ON DELETE RESTRICT,
  CONSTRAINT ck_disc_etapa CHECK (etapa BETWEEN 1 AND 3)
) ENGINE=InnoDB;

-- Turma pertence a um curso e é reusada por ano (sem ano aqui).
CREATE TABLE turma (
  id_turma     INT UNSIGNED NOT NULL AUTO_INCREMENT,
  numero_turma VARCHAR(30)  NOT NULL,
  id_curso     INT UNSIGNED NOT NULL,
  ativo        BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id_turma),
  KEY idx_turma_curso (id_curso),
  CONSTRAINT fk_turma_curso FOREIGN KEY (id_curso) REFERENCES curso(id_curso) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Disciplinas padrão de uma turma. Base para matrícula em lote.
CREATE TABLE disc_padrao (
  id_disc   INT UNSIGNED NOT NULL,
  id_turma  INT UNSIGNED NOT NULL,
  PRIMARY KEY (id_disc, id_turma),
  KEY idx_dp_turma (id_turma),
  CONSTRAINT fk_dp_disc  FOREIGN KEY (id_disc)  REFERENCES disciplina(id_disc) ON DELETE CASCADE,
  CONSTRAINT fk_dp_turma FOREIGN KEY (id_turma) REFERENCES turma(id_turma)     ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE ano_letivo (
  id_ano_letivo INT UNSIGNED NOT NULL AUTO_INCREMENT,
  ano_letivo    SMALLINT UNSIGNED NOT NULL,   -- ex.: 2026
  dt_ini        DATE         NULL,
  dt_fim        DATE         NULL,
  ativo         BOOLEAN      NOT NULL DEFAULT TRUE,
  PRIMARY KEY (id_ano_letivo),
  UNIQUE KEY uq_ano_letivo (ano_letivo)
) ENGINE=InnoDB;

-- Ministra: quais disciplinas o professor leciona em cada turma/ano.
-- É também a fonte do ESCOPO do professor.
CREATE TABLE ministra (
  id_func       INT UNSIGNED NOT NULL,
  id_disc       INT UNSIGNED NOT NULL,
  id_turma      INT UNSIGNED NOT NULL,
  id_ano_letivo INT UNSIGNED NOT NULL,
  PRIMARY KEY (id_func, id_disc, id_turma, id_ano_letivo),
  KEY idx_min_turma_disc_ano (id_turma, id_disc, id_ano_letivo),
  CONSTRAINT fk_min_func  FOREIGN KEY (id_func)       REFERENCES funcionario(id_func)   ON DELETE CASCADE,
  CONSTRAINT fk_min_disc  FOREIGN KEY (id_disc)       REFERENCES disciplina(id_disc)    ON DELETE RESTRICT,
  CONSTRAINT fk_min_turma FOREIGN KEY (id_turma)      REFERENCES turma(id_turma)        ON DELETE RESTRICT,
  CONSTRAINT fk_min_ano   FOREIGN KEY (id_ano_letivo) REFERENCES ano_letivo(id_ano_letivo) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- =====================================================================
--  4) ALUNO, MATRÍCULA/BOLETIM E AULAS
-- =====================================================================

CREATE TABLE aluno (
  id_alu            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nome_alu          VARCHAR(150) NOT NULL,
  matricula         VARCHAR(30)  NOT NULL,
  pai_alu           VARCHAR(150) NULL,
  mae_alu           VARCHAR(150) NULL,
  rg_alu            VARCHAR(20)  NULL,
  cpf_alu           VARCHAR(14)  NULL,
  tel_alu           VARCHAR(20)  NULL,
  sexo_alu          ENUM('M','F','O') NULL,
  dt_nasc_alu       DATE         NULL,
  naturalidade_alu  VARCHAR(80)  NULL,
  nacionalidade_alu VARCHAR(80)  NULL,
  id_usu            INT UNSIGNED NULL,           -- conta de acesso do aluno
  ativo             BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id_alu),
  UNIQUE KEY uq_aluno_matricula (matricula),
  UNIQUE KEY uq_aluno_usu (id_usu),
  CONSTRAINT fk_aluno_usuario FOREIGN KEY (id_usu) REFERENCES usuario(id_usu) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Boletim: uma linha por aluno x disciplina x turma x ano.
-- Âncora da matrícula na disciplina. Faltas por bimestre; nota + recuperação.
CREATE TABLE boletim (
  id_matriculado INT UNSIGNED NOT NULL AUTO_INCREMENT,
  id_alu         INT UNSIGNED NOT NULL,
  id_disc        INT UNSIGNED NOT NULL,
  id_turma       INT UNSIGNED NOT NULL,
  id_ano_letivo  INT UNSIGNED NOT NULL,
  nota_1bim      DECIMAL(5,2) NULL,
  rec_1bim       DECIMAL(5,2) NULL,
  faltas_1bim    SMALLINT UNSIGNED NULL DEFAULT 0,
  nota_2bim      DECIMAL(5,2) NULL,
  rec_2bim       DECIMAL(5,2) NULL,
  faltas_2bim    SMALLINT UNSIGNED NULL DEFAULT 0,
  rec_final      DECIMAL(5,2) NULL,
  sit_final      ENUM('CURSANDO','APROVADO','REPROVADO','RECUPERACAO') NOT NULL DEFAULT 'CURSANDO',
  dt_matriculado DATE         NULL,
  sit_mat_disc   ENUM('MATRICULADO','TRANCADO') NOT NULL DEFAULT 'MATRICULADO',
  dependencia    BOOLEAN      NOT NULL DEFAULT FALSE,   -- matrícula em dependência
  PRIMARY KEY (id_matriculado),
  UNIQUE KEY uq_boletim (id_alu, id_disc, id_turma, id_ano_letivo),
  KEY idx_bol_aluno_ano (id_alu, id_ano_letivo),
  KEY idx_bol_turma_disc_ano (id_turma, id_disc, id_ano_letivo),
  CONSTRAINT fk_bol_aluno FOREIGN KEY (id_alu)        REFERENCES aluno(id_alu)             ON DELETE RESTRICT,
  CONSTRAINT fk_bol_disc  FOREIGN KEY (id_disc)       REFERENCES disciplina(id_disc)       ON DELETE RESTRICT,
  CONSTRAINT fk_bol_turma FOREIGN KEY (id_turma)      REFERENCES turma(id_turma)           ON DELETE RESTRICT,
  CONSTRAINT fk_bol_ano   FOREIGN KEY (id_ano_letivo) REFERENCES ano_letivo(id_ano_letivo) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Aulas previstas/dadas por (ano, turma, disciplina, bimestre).
-- Denominador do % de falta; comum a todos os alunos da turma.
CREATE TABLE alet_disc (
  id_aulas_disc   INT UNSIGNED NOT NULL AUTO_INCREMENT,
  id_ano_letivo   INT UNSIGNED NOT NULL,
  id_turma        INT UNSIGNED NOT NULL,
  id_disc         INT UNSIGNED NOT NULL,
  bimestre        TINYINT UNSIGNED NOT NULL,       -- 1 ou 2
  aulas_previstas SMALLINT UNSIGNED NULL DEFAULT 0,
  aulas_dadas     SMALLINT UNSIGNED NULL DEFAULT 0,
  PRIMARY KEY (id_aulas_disc),
  UNIQUE KEY uq_aulas (id_ano_letivo, id_turma, id_disc, bimestre),
  CONSTRAINT fk_al_ano   FOREIGN KEY (id_ano_letivo) REFERENCES ano_letivo(id_ano_letivo) ON DELETE RESTRICT,
  CONSTRAINT fk_al_turma FOREIGN KEY (id_turma)      REFERENCES turma(id_turma)           ON DELETE RESTRICT,
  CONSTRAINT fk_al_disc  FOREIGN KEY (id_disc)       REFERENCES disciplina(id_disc)       ON DELETE RESTRICT,
  CONSTRAINT ck_al_bimestre CHECK (bimestre BETWEEN 1 AND 2)
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================================
--  5) SEEDS — perfis, permissões e mapeamento base do painel
--     (Admin recebe tudo; os demais recebem o que cabe. Edite via painel.)
-- =====================================================================

INSERT INTO perfil (nome_perfil, descricao) VALUES
  ('Admin',       'Acesso total ao sistema'),
  ('Secretaria',  'Gestão de alunos e matrículas'),
  ('Professor',   'Lançamento de notas, frequência e aulas'),
  ('Aluno',       'Consulta do próprio boletim'),
  ('Coordenador', 'Acompanhamento restrito aos cursos coordenados');

INSERT INTO permissao (chave_permissao, descricao) VALUES
  ('usuario.listar','Listar usuários'),
  ('usuario.criar','Cadastrar usuário'),
  ('usuario.editar','Editar usuário'),
  ('usuario.bloquear','Bloquear/ativar usuário'),
  ('usuario.resetar_senha','Resetar senha de usuário'),
  ('usuario.excluir','Excluir usuário (soft delete)'),
  ('aluno.listar','Listar alunos'),
  ('aluno.criar','Cadastrar aluno'),
  ('aluno.editar','Editar aluno'),
  ('aluno.excluir','Excluir aluno'),
  ('aluno.detalhar','Detalhar aluno'),
  ('funcionario.listar','Listar funcionários'),
  ('funcionario.criar','Cadastrar funcionário'),
  ('funcionario.editar','Editar funcionário'),
  ('funcionario.excluir','Excluir funcionário'),
  ('funcionario.detalhar','Detalhar funcionário'),
  ('funcao.gerenciar','Gerenciar funções'),
  ('vinculo.gerenciar','Gerenciar vínculos'),
  ('vinc_func.gerenciar','Gerenciar vínculos do funcionário'),
  ('disciplina.gerenciar','Gerenciar disciplinas'),
  ('curso.gerenciar','Gerenciar cursos'),
  ('turma.gerenciar','Gerenciar turmas'),
  ('disc_padrao.gerenciar','Gerenciar disciplinas padrão da turma'),
  ('matricula.matricular','Matricular aluno em disciplinas'),
  ('matricula.trancar_disciplina','Trancar disciplina'),
  ('matricula.trancar_curso','Trancar curso'),
  ('boletim.lancar_nota','Lançar notas e frequência'),
  ('boletim.exibir','Exibir boletim'),
  ('ano_letivo.gerenciar','Gerenciar ano letivo'),
  ('aulas.lancar','Lançar aulas previstas/dadas'),
  ('ministra.definir','Definir disciplinas ministradas'),
  ('perfil.gerenciar','Gerenciar perfis'),
  ('permissao.configurar','Configurar permissões dos perfis');

-- Admin: todas as permissões.
INSERT INTO perfil_permissao (id_perfil, id_permissao)
SELECT p.id_perfil, pm.id_permissao
FROM perfil p CROSS JOIN permissao pm
WHERE p.nome_perfil = 'Admin';

-- Secretaria.
INSERT INTO perfil_permissao (id_perfil, id_permissao)
SELECT p.id_perfil, pm.id_permissao
FROM perfil p JOIN permissao pm
  ON pm.chave_permissao IN (
     'aluno.listar','aluno.criar','aluno.editar','aluno.excluir','aluno.detalhar',
     'matricula.matricular','matricula.trancar_disciplina','matricula.trancar_curso')
WHERE p.nome_perfil = 'Secretaria';

-- Professor.
INSERT INTO perfil_permissao (id_perfil, id_permissao)
SELECT p.id_perfil, pm.id_permissao
FROM perfil p JOIN permissao pm
  ON pm.chave_permissao IN ('boletim.lancar_nota','aulas.lancar')
WHERE p.nome_perfil = 'Professor';

-- Aluno.
INSERT INTO perfil_permissao (id_perfil, id_permissao)
SELECT p.id_perfil, pm.id_permissao
FROM perfil p JOIN permissao pm
  ON pm.chave_permissao IN ('boletim.exibir')
WHERE p.nome_perfil = 'Aluno';

-- Coordenador (capacidade; o ESCOPO por curso vem da tabela coordenacao).
INSERT INTO perfil_permissao (id_perfil, id_permissao)
SELECT p.id_perfil, pm.id_permissao
FROM perfil p JOIN permissao pm
  ON pm.chave_permissao IN ('aluno.listar','aluno.detalhar','boletim.exibir')
WHERE p.nome_perfil = 'Coordenador';
