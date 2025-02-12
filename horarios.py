import streamlit as st
from sqlalchemy.orm import sessionmaker
from db.models import engine, Horario, Profissional
from datetime import datetime


# Cria uma sessão para interagir com o banco de dados
Session = sessionmaker(bind=engine)
session = Session()

def mostrar_pagina_horarios():
    st.title("SmartOdonto - Horários")

    # Consulta todos os profissionais cadastrados
    profissionais = session.query(Profissional).all()

    # Verifica se há profissionais cadastrados
    if profissionais:
        # Cria um dicionário para mapear ID do profissional -> Nome do profissional
        profissionais_dict = {p.profissional_id: p.profissional_nome for p in profissionais}

        # Formulário para adicionar novo horário
        st.write("### Adicionar Novo Horário")

        # Selectbox para escolher o profissional
        profissional_nome = st.selectbox(
            "Selecione o Profissional:",
            options=list(profissionais_dict.values()),  # Exibe os nomes dos profissionais
            format_func=lambda nome: nome  # Exibe o nome no selectbox
        )
        # Obtém o ID do profissional selecionado
        profissional_id = [k for k, v in profissionais_dict.items() if v == profissional_nome][0]

        # Campos do formulário
        data = st.date_input("Data")  # Campo de data atualizado
        hora_inicio = st.number_input("Hora de Início", min_value=0, max_value=23, value=9)
        hora_final = st.number_input("Hora de Término", min_value=0, max_value=23, value=18)

        # Botão para salvar o horário
        if st.button("Salvar Horário"):
            if data:
                novo_horario = Horario(
                    horario_profissionalId=profissional_id,  # Usa o ID do profissional selecionado
                    horario_data=data.strftime("%Y-%m-%d"),  # Formata para string no formato correto
                    horario_horaInicio=hora_inicio,
                    horario_horaFinal=hora_final
                )
                session.add(novo_horario)
                session.commit()
                st.success("Horário cadastrado com sucesso!")
                st.rerun()  # Recarrega a página
            else:
                st.error("Por favor, preencha a data.")
    else:
        st.info("Nenhum profissional cadastrado. Cadastre um profissional antes de adicionar horários.")

    if st.checkbox("Exibir horários: ", value=True):
        # Exibe os dados cadastrados
        st.write("### Lista de Horários Cadastrados")

        # Consulta todos os horários no banco de dados
        horarios = session.query(Horario).all()

        if horarios:
            # Cria uma lista de dicionários para exibir na tabela
            dados_horarios = []
            for horario in horarios:
                # Busca o nome do profissional correspondente ao horario_profissionalId
                profissional_nome = profissionais_dict.get(horario.horario_profissionalId, "Profissional não encontrado")
                
                dados_horarios.append({
                    "ID": horario.horario_id,
                    "Profissional": profissional_nome,  # Exibe o nome do profissional
                    "Data": horario.horario_data,
                    "Hora Início": horario.horario_horaInicio,
                    "Hora Término": horario.horario_horaFinal
                })

            # Exibe a tabela com os dados dos horários
            st.table(dados_horarios)

        if st.checkbox("Editar/Remover horário"):
            # Opções de editar e excluir
            st.write("### Opções de Editar e Excluir")

            # Seleciona um horário para editar ou excluir
            horario_id = st.selectbox(
                "Selecione um horário para editar ou excluir:",
                options=[h.horario_id for h in horarios],
                format_func=lambda id: f"{session.query(Horario).filter_by(horario_id=id).first().horario_data} (ID: {id})",
                key="select_horario"
            )

            # Busca o horário selecionado
            horario_selecionado = session.query(Horario).filter_by(horario_id=horario_id).first()

            # Formulário de edição
            st.write(f"### Editando Horário: {horario_selecionado.horario_data}")

            # Selectbox para escolher o profissional
            profissional_nome_edit = st.selectbox(
                "Profissional:",
                options=list(profissionais_dict.values()),  # Exibe os nomes dos profissionais
                index=list(profissionais_dict.values()).index(profissionais_dict.get(horario_selecionado.horario_profissionalId, "Profissional não encontrado")),
                key="edit_profissional"
            )
            # Obtém o ID do profissional selecionado
            novo_profissional_id = [k for k, v in profissionais_dict.items() if v == profissional_nome_edit][0]

            # Campos do formulário
            nova_data = st.date_input("Data", value=datetime.strptime(horario_selecionado.horario_data, "%Y-%m-%d"), key="edit_data")
            nova_hora_inicio = st.number_input("Hora de Início", value=horario_selecionado.horario_horaInicio, min_value=0, max_value=23, key="edit_hora_inicio")
            nova_hora_final = st.number_input("Hora de Término", value=horario_selecionado.horario_horaFinal, min_value=0, max_value=23, key="edit_hora_final")

            # Botão para salvar as edições
            if st.button("Salvar Edições", key="salvar_edicoes"):
                horario_selecionado.horario_profissionalId = novo_profissional_id
                horario_selecionado.horario_data = nova_data.strftime("%Y-%m-%d")  # Formata para string correta
                horario_selecionado.horario_horaInicio = nova_hora_inicio
                horario_selecionado.horario_horaFinal = nova_hora_final
                session.commit()
                st.success("Horário atualizado com sucesso!")
                st.rerun()  # Recarrega a página

            # Botão para excluir o horário
            if st.button("Excluir Horário", key="excluir_horario"):
                session.delete(horario_selecionado)
                session.commit()
                st.success("Horário excluído com sucesso!")
                st.rerun()  # Recarrega a página
    else:
        st.info("Nenhum horário cadastrado no momento.")
