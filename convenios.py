import streamlit as st
from sqlalchemy.orm import sessionmaker
from db.models import engine, Convenio

# Cria uma sessão para interagir com o banco de dados
Session = sessionmaker(bind=engine)
session = Session()

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
            status_num = 1 if convenio_status == "Ativo" else 0
            novo_convenio = Convenio(
                convenio_nome=convenio_nome,
                convenio_telefone=convenio_telefone,
                convenio_site=convenio_site,
                convenio_status=status_num
            )
            try:
                session.add(novo_convenio)
                session.commit()
                st.success("Convênio cadastrado com sucesso!")
            except Exception as e:
                session.rollback()
        else:
            st.error("Por favor, preencha todos os campos obrigatórios.")

    if st.checkbox("Exibir convênios", value=True):
        # Exibe os dados cadastrados
        st.write("### Lista de Convênios Cadastrados")
        convenios = session.query(Convenio).all()

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
        if st.checkbox("Editar/Remover convênio"):
            # Opções de editar e excluir
            st.write("### Opções de Editar e Excluir")
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
                convenio_selecionado.convenio_nome = novo_nome
                convenio_selecionado.convenio_telefone = novo_telefone
                convenio_selecionado.convenio_site = novo_site
                convenio_selecionado.convenio_status = 1 if novo_status == "Ativo" else 0
                try:
                    session.commit()
                    st.success("Convênio atualizado com sucesso!")
                    st.rerun()
                except Exception as e:
                    session.rollback()

            if st.button("Excluir Convênio", key="excluir_convenio"):
                session.delete(convenio_selecionado)
                try:
                    session.commit()
                    st.success("Convênio excluído com sucesso!")
                    st.rerun()
                except Exception as e:
                    session.rollback()
    else:
        st.info("Nenhum convênio cadastrado no momento.")