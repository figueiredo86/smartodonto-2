from sqlalchemy import create_engine, Column, Integer, String, Enum, ForeignKey, Float, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_DATABASE')}"

# Cria a engine do SQLAlchemy
engine = create_engine(DATABASE_URL,pool_recycle=3600,pool_pre_ping=True)

# Base para as classes do SQLAlchemy
Base = declarative_base()

# Modelo da tabela `pacientes`
class Paciente(Base):
    __tablename__ = 'pacientes'
    
    paciente_id = Column(Integer, primary_key=True, autoincrement=True)
    paciente_nome = Column(String(100), nullable=False)
    paciente_telefone = Column(String(15), nullable=False)
    paciente_endereco = Column(String(100), default=None)
    paciente_complemento = Column(String(100), default='None')
    paciente_documento = Column(Integer, default=None)
    paciente_convenioId = Column(Integer, nullable=False)
    paciente_cep = Column(Integer, default=None)
    paciente_numero = Column(Integer, default=None)
    paciente_status = Column(Boolean, nullable=False, default=1)
    paciente_ultimaConsulta = Column(Date, default=None)

# Modelo da tabela `convenios`
class Convenio(Base):
    __tablename__ = 'convenios'
   
    convenio_id = Column(Integer, primary_key=True, autoincrement=True)
    convenio_nome = Column(String(100), nullable=False)
    convenio_telefone = Column(String(20), nullable=False, unique=True)
    convenio_site = Column(String(100), nullable=False)
    convenio_status = Column(Integer, nullable=False, default=0)

# Modelo da tabela `convenios`
class Procedimento(Base):
    __tablename__ = 'procedimentos'
    
    procedimento_id = Column(Integer, primary_key=True, autoincrement=True)
    procedimento_nome = Column(String(100), nullable=False)
    procedimento_valor = Column(Float, nullable=False, default="0.0")
    procedimento_aceitaConvenio = Column(Boolean, nullable=False, default="1")
    procedimento_tempo = Column(String(100), default=60)
    procedimento_status = Column(Integer, nullable=False, default=1)

# Modelo da tabela `convenios`
class Profissional(Base):
    __tablename__ = 'profissionais'
    
    profissional_id = Column(Integer, primary_key=True, autoincrement=True)
    profissional_nome = Column(String(50), nullable=False)
    profissional_telefone = Column(String(50), nullable=False)


class Horario(Base):
    __tablename__ = 'horarios'

    horario_id = Column(Integer, primary_key=True, autoincrement=True)
    horario_profissionalId = Column(Integer, ForeignKey('profissionais.profissional_id'), nullable=False)
    horario_data = Column(String(100), nullable=False, default='now()')
    horario_horaInicio = Column(Integer, default=9)
    horario_horaFinal = Column(Integer, default=18)

class Consulta(Base):
    __tablename__ = 'consultas'

    consulta_id = Column(Integer, primary_key=True, autoincrement=True)
    consulta_pacienteId = Column(Integer, nullable=False)
    consulta_profissionalId = Column(Integer, nullable=False)
    consulta_procedimentoId = Column(Integer, nullable=False)
    consulta_convenioId = Column(Integer, nullable=False)
    consulta_data = Column(String(100), nullable=False, default='now()')
    consulta_valor_total = Column(String(100), nullable=False)
    consulta_hora = Column(Integer, default=9)
    consulta_status = Column(Integer, default=1)

class ConsultaStatus(Base):
    __tablename__ = 'consulta_status'

    consultaStatus_id = Column(Integer, primary_key=True, autoincrement=True)
    consultaStatus_descricao = Column(String(100), nullable=False)
    consultaStatus_rgb = Column(String(100), nullable=False)

class Template(Base):
    __tablename__ = 'templates'

    template_id = Column(Integer, primary_key=True, autoincrement=True)
    template_texto = Column(String(200), nullable=False)

# Adicione o seguinte código ao arquivo `models.py`

class Inventario(Base):
    __tablename__ = 'inventario'
    
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    item_nome = Column(String(100), nullable=False)
    item_descricao = Column(String(255), nullable=True)
    item_quantidade = Column(Integer, nullable=False, default=0)
    item_status = Column(Integer, nullable=False, default=1)  # 1 para ativo, 0 para inativo


# Cria as tabelas no banco de dados (se não existirem)
Base.metadata.create_all(engine)