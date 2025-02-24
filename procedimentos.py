import streamlit as st
from sqlalchemy.orm import sessionmaker
from db.models import engine, Procedimento

# Cria uma sessão para interagir com o banco de dados
Session = sessionmaker(bind=engine)
session = Session()

def mostrar_pagina_procedimentos():
    st.title("SmartOdonto - Procedimentos")

    # Formulário para adicionar novo procedimento
    st.write("### Adicionar Novo Procedimento")
    procedimento_nome = st.text_input("Nome do Procedimento")
    procedimento_valor = st.number_input("Valor do Procedimento", min_value=0.0, format="%.2f")
    procedimento_status = st.text_input("Status do Procedimento", value="Ativo")

    # Botão para salvar o procedimento
    if st.button("Salvar Procedimento"):
        if procedimento_nome and procedimento_valor:
            # Converte o status para o valor numérico esperado no banco de dados
            status_num = 1 if procedimento_status == "Ativo" else 0

            # Cria um novo registro de Procedimento
            novo_procedimento = Procedimento(
                procedimento_nome=procedimento_nome,
                procedimento_valor=procedimento_valor,
                procedimento_aceitaConvenio=0,
                procedimento_tempo=30,
                procedimento_status=status_num
            )

            # Adiciona e salva no banco de dados
            try:
                session.add(novo_procedimento)
                session.commit()
                st.success("Procedimento cadastrado com sucesso!")
                st.rerun()  # Recarrega a página
            except Exception as e:
                session.rolback()
        else:
            st.error("Por favor, preencha todos os campos obrigatórios.")
    if st.checkbox("Listar procedimentos", value=True):
        # Exibe os dados cadastrados
        st.write("### Lista de Procedimentos Cadastrados")

        # Consulta todos os procedimentos no banco de dados
        procedimentos = session.query(Procedimento).all()

        # Verifica se há procedimentos cadastrados
        if procedimentos:
            # Cria uma lista de dicionários para exibir na tabela
            dados_procedimentos = []
            for procedimento in procedimentos:
                dados_procedimentos.append({
                    "ID": procedimento.procedimento_id,
                    "Nome": procedimento.procedimento_nome,
                    "Valor": f"R$ {procedimento.procedimento_valor:.2f}",
                })

            # Exibe a tabela com os dados dos procedimentos
            st.table(dados_procedimentos)

            if st.checkbox("Editar/Remover procedimento"):
                # Opções de editar e excluir
                st.write("### Opções de Editar e Excluir")

                # Seleciona um procedimento para editar ou excluir
                procedimento_id = st.selectbox(
                    "Selecione um procedimento para editar ou excluir:",
                    options=[p.procedimento_id for p in procedimentos],
                    format_func=lambda id: f"{session.query(Procedimento).filter_by(procedimento_id=id).first().procedimento_nome} (ID: {id})",
                    key="select_procedimento"
                )

                # Busca o procedimento selecionado
                procedimento_selecionado = session.query(Procedimento).filter_by(procedimento_id=procedimento_id).first()

                # Formulário de edição
                st.write(f"### Editando Procedimento: {procedimento_selecionado.procedimento_nome}")
                novo_nome = st.text_input("Nome do Procedimento", value=procedimento_selecionado.procedimento_nome, key="edit_nome")
                novo_valor = st.number_input("Valor do Procedimento", value=procedimento_selecionado.procedimento_valor, min_value=0.0, format="%.2f", key="edit_valor")
                novo_status = st.selectbox(
                    "Status do Procedimento",
                    ["Ativo", "Inativo"],
                    index=0 if procedimento_selecionado.procedimento_status == 1 else 1,
                    key="edit_status"
                )

                # Botão para salvar as edições
                if st.button("Salvar Edições", key="salvar_edicoes"):
                    procedimento_selecionado.procedimento_nome = novo_nome
                    procedimento_selecionado.procedimento_valor = novo_valor
                    procedimento_selecionado.procedimento_status = 1 if novo_status == "Ativo" else 0
                    try:
                        session.commit()
                        st.success("Procedimento atualizado com sucesso!")
                        st.rerun()  # Recarrega a página
                    except Exception as e:
                        session.rollback()

                # Botão para excluir o procedimento
                if st.button("Excluir Procedimento", key="excluir_procedimento"):
                    try:
                        session.delete(procedimento_selecionado)
                        session.commit()
                        st.success("Procedimento excluído com sucesso!")
                        st.rerun()  # Recarrega a página
                    except Exception as e:
                        session.rollback()
        else:
            st.info("Nenhum procedimento cadastrado no momento.")