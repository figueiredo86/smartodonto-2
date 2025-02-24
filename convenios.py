import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from db.models import Convenio
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configura a URL do banco de dados
DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_DATABASE')}"

# Cria a engine do SQLAlchemy com configurações de pool
engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,  # Recicla a conexão após 1 hora
    pool_timeout=30,    # Tempo máximo de espera para obter uma conexão
    pool_pre_ping=True  # Verifica a conexão antes de usá-la
)

# Cria a fábrica de sessões
Session = sessionmaker(bind=engine)

# Função para criar uma nova sessão
def criar_sessao():
    return Session()

# Função para adicionar um novo convênio
def adicionar_convenio(nome, telefone, site, status):
    session = criar_sessao()  # Recria a sessão
    try:
        status_num = 1 if status == "Ativo" else 0
        novo_convenio = Convenio(
            convenio_nome=nome,
            convenio_telefone=telefone,
            convenio_site=site,
            convenio_status=status_num
        )
        session.add(novo_convenio)
        session.commit()
        st.success("Convênio cadastrado com sucesso!")
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Erro ao cadastrar convênio: {e}")
    finally:
        session.close()  # Fecha a sessão após o uso

# Função para editar um convênio existente
def editar_convenio(convenio, novo_nome, novo_telefone, novo_site, novo_status):
    session = criar_sessao()  # Recria a sessão
    try:
        convenio.convenio_nome = novo_nome
        convenio.convenio_telefone = novo_telefone
        convenio.convenio_site = novo_site
        convenio.convenio_status = 1 if novo_status == "Ativo" else 0
        session.commit()
        st.success("Convênio atualizado com sucesso!")
        st.rerun()
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Erro ao atualizar convênio: {e}")
    finally:
        session.close()  # Fecha a sessão após o uso

# Função para excluir um convênio
def excluir_convenio(convenio):
    session = criar_sessao()  # Recria a sessão
    try:
        session.delete(convenio)
        session.commit()
        st.success("Convênio excluído com sucesso!")
        st.rerun()
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Erro ao excluir convênio: {e}")
    finally:
        session.close()  # Fecha a sessão após o uso

# Função principal para exibir a página de convênios
def mostrar_pagina_convenios():
    st.title("SmartOdonto - Convênios")

    # Formulário para adicionar novo convênio
    st.write("### Adicionar Novo Convênio")
    convenio_nome = st.text_input("Nome do Convênio")
    convenio_telefone = st.text_input("Telefone do Convênio")
    convenio_site = st.text_input("Site do Convênio")
    convenio_status = st.selectbox("Status do Convênio", ["Ativo", "Inativo"])

    if st.button("Salvar Convênio"):
        if convenio_nome and convenio_telefone and convenio_site:
            adicionar_convenio(convenio_nome, convenio_telefone, convenio_site, convenio_status)
        else:
            st.error("Por favor, preencha todos os campos obrigatórios.")

    # Exibe os convênios cadastrados
    if st.checkbox("Exibir convênios", value=True):
        session = criar_sessao()  # Recria a sessão
        try:
            convenios = session.query(Convenio).all()
        except SQLAlchemyError as e:
            st.error(f"Erro ao realizar consulta: {e}")
            convenios = []
        finally:
            session.close()  # Fecha a sessão após o uso

        if convenios:
            dados_convenios = []
            for convenio in convenios:
                dados_convenios.append({
                    "ID": convenio.convenio_id,
                    "Nome": convenio.convenio_nome,
                    "Telefone": convenio.convenio_telefone,
                    "Site": convenio.convenio_site,
                    "Status": "Ativo" if convenio.convenio_status == 1 else "Inativo"
                })
            st.table(dados_convenios)
        else:
            st.info("Nenhum convênio cadastrado no momento.")

        # Opções de editar e excluir
        if st.checkbox("Editar/Remover convênio"):
            session = criar_sessao()  # Recria a sessão
            try:
                convenios = session.query(Convenio).all()
                convenio_id = st.selectbox(
                    "Selecione um convênio para editar ou excluir:",
                    options=[c.convenio_id for c in convenios],
                    format_func=lambda id: session.query(Convenio).filter_by(convenio_id=id).first().convenio_nome,
                    key="select_convenio"
                )
                convenio_selecionado = session.query(Convenio).filter_by(convenio_id=convenio_id).first()

                # Formulário de edição
                st.write(f"### Editando Convênio: {convenio_selecionado.convenio_nome}")
                novo_nome = st.text_input("Nome do Convênio", value=convenio_selecionado.convenio_nome, key="edit_nome")
                novo_telefone = st.text_input("Telefone do Convênio", value=convenio_selecionado.convenio_telefone, key="edit_telefone")
                novo_site = st.text_input("Site do Convênio", value=convenio_selecionado.convenio_site, key="edit_site")
                novo_status = st.selectbox(
                    "Status do Convênio",
                    ["Ativo", "Inativo"],
                    index=0 if convenio_selecionado.convenio_status == 1 else 1,
                    key="edit_status"
                )

                if st.button("Salvar Edições", key="salvar_edicoes"):
                    editar_convenio(convenio_selecionado, novo_nome, novo_telefone, novo_site, novo_status)

                if st.button("Excluir Convênio", key="excluir_convenio"):
                    excluir_convenio(convenio_selecionado)
            except SQLAlchemyError as e:
                st.error(f"Erro ao realizar consulta: {e}")
            finally:
                session.close()  # Fecha a sessão após o uso

# Executa a aplicação
if __name__ == "__main__":
    mostrar_pagina_convenios()