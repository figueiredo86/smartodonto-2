import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db.models import engine, Profissional

# Cria uma sessão para interagir com o banco de dados
Session = sessionmaker(bind=engine)

def mostrar_pagina_profissionais():
    st.title("Profissionais")

    # Formulário para adicionar novo profissional
    st.write("### Adicionar Novo Profissional")
    profissional_nome = st.text_input("Nome do Profissional")
    profissional_telefone = st.text_input("Telefone")

    # Botão para salvar o profissional
    if st.button("Salvar Profissional"):
        if profissional_nome and profissional_telefone:
            try:
                # Cria uma nova sessão
                session = Session()

                # Cria um novo registro de Profissional
                novo_profissional = Profissional(
                    profissional_nome=profissional_nome,
                    profissional_telefone=profissional_telefone,
                )

                # Adiciona e salva no banco de dados
                session.add(novo_profissional)
                session.commit()

                st.success("Profissional cadastrado com sucesso!")
                st.rerun()  # Recarrega a página
            except SQLAlchemyError as e:
                session.rollback()  # Desfaz a transação em caso de erro
                st.error(f"Erro ao cadastrar profissional: {e}")
            finally:
                session.close()  # Fecha a sessão
        else:
            st.error("Por favor, preencha todos os campos obrigatórios.")

    # Exibe os dados cadastrados
    st.write("### Lista de Profissionais Cadastrados")

    try:
        # Cria uma nova sessão
        session = Session()

        # Consulta todos os profissionais no banco de dados
        profissionais = session.query(Profissional).all()

        # Verifica se há profissionais cadastrados
        if st.checkbox("Listar profissionais cadastrados: ", value=True):
            if profissionais:
                # Cria uma lista de dicionários para exibir na tabela
                dados_profissionais = []
                for profissional in profissionais:
                    dados_profissionais.append({
                        "ID": profissional.profissional_id,
                        "Nome": profissional.profissional_nome,
                        "Telefone": profissional.profissional_telefone,
                    })

                # Exibe a tabela com os dados dos profissionais
                st.table(dados_profissionais)

                if st.checkbox("Editar/Remover profissional"):
                    # Opções de editar e excluir
                    st.write("### Opções de Editar e Excluir")

                    # Seleciona um profissional para editar ou excluir
                    profissional_id = st.selectbox(
                        "Selecione um profissional para editar ou excluir:",
                        options=[p.profissional_id for p in profissionais],
                        format_func=lambda id: f"{session.query(Profissional).filter_by(profissional_id=id).first().profissional_nome} (ID: {id})",
                        key="select_profissional"
                    )

                    # Busca o profissional selecionado
                    profissional_selecionado = session.query(Profissional).filter_by(profissional_id=profissional_id).first()

                    # Formulário de edição
                    st.write(f"### Editando Profissional: {profissional_selecionado.profissional_nome}")
                    novo_nome = st.text_input("Nome do Profissional", value=profissional_selecionado.profissional_nome, key="edit_nome")
                    novo_telefone = st.text_input("Telefone", value=profissional_selecionado.profissional_telefone, key="edit_telefone")

                    # Botão para salvar as edições
                    if st.button("Salvar Edições", key="salvar_edicoes"):
                        profissional_selecionado.profissional_nome = novo_nome
                        profissional_selecionado.profissional_telefone = novo_telefone
                        try:
                            session.commit()
                            st.success("Profissional atualizado com sucesso!")
                            st.rerun()
                        except SQLAlchemyError as e:
                            session.rollback()
                            st.error(f"Erro ao atualizar profissional: {e}")

                    # Botão para excluir o profissional
                    if st.button("Excluir Profissional", key="excluir_profissional"):
                        try:
                            session.delete(profissional_selecionado)
                            session.commit()
                            st.success("Profissional excluído com sucesso!")
                            st.rerun()  # Recarrega a página
                        except SQLAlchemyError as e:
                            session.rollback()
                            st.error(f"Erro ao excluir profissional: {e}")
            else:
                st.info("Nenhum profissional cadastrado no momento.")
    except SQLAlchemyError as e:
        st.error(f"Erro ao consultar profissionais: {e}")
    finally:
        session.close()  # Fecha a sessão