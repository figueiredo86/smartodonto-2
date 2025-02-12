import streamlit as st
from sqlalchemy.orm import sessionmaker
from db.models import engine, Horario, Profissional, Paciente, Procedimento, Consulta, ConsultaStatus, Template
from datetime import datetime, timedelta
import pandas as pd

# Criar sessão para o banco de dados
Session = sessionmaker(bind=engine)
session = Session()

def get_template_mensagem(paciente_nome, data, hora):
    template = session.query(Template).first()
    if template and template.template_texto:
        data_formatada = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
        horario_formatado = f"{hora:02d}:00"
        return (
            template.template_texto
            .replace("{nome}", paciente_nome)
            .replace("{data}", data_formatada)
            .replace("{hora}", horario_formatado)
        )
    return f"Olá {paciente_nome}. Tudo bem? Podemos confirmar sua consulta para o dia {data_formatada} às {horario_formatado}?"

def gerar_link_whatsapp(telefone, mensagem):
    telefone_formatado = "".join(filter(str.isdigit, telefone))
    if not telefone.startswith("+"):
        telefone_formatado = f"+55{telefone_formatado}"
    return f"https://wa.me/{telefone_formatado}?text={mensagem.replace(' ', '%20')}"

def mostrar_pagina_agenda():
    st.title("SmartOdonto - Agenda")

    st.write("### Selecione uma data específica para visualizar as consultas")
    data_selecionada = st.date_input("Escolha a data", key="data_selecionada_unica")

    if data_selecionada:
        data_formatada = data_selecionada.strftime("%Y-%m-%d")
        horarios = session.query(Horario).filter(Horario.horario_data == data_formatada).all()

        if horarios:
            st.write("### Agenda do Dia")
            tabela_horarios = []

            for horario in horarios:
                profissional = session.query(Profissional).filter_by(profissional_id=horario.horario_profissionalId).first()
                profissional_nome = profissional.profissional_nome if profissional else "Desconhecido"

                for hora in range(horario.horario_horaInicio, horario.horario_horaFinal + 1):
                    consulta = session.query(Consulta).filter(
                        Consulta.consulta_data == data_formatada,
                        Consulta.consulta_hora == hora,
                        Consulta.consulta_profissionalId == horario.horario_profissionalId
                    ).first()

                    paciente_nome = "Disponível"
                    cor_fundo = "white"
                    link_whatsapp = ""

                    if consulta:
                        paciente = session.query(Paciente).filter_by(paciente_id=consulta.consulta_pacienteId).first()
                        paciente_nome = paciente.paciente_nome if paciente else "Paciente não encontrado"

                        status = session.query(ConsultaStatus).filter_by(consultaStatus_id=consulta.consulta_status).first()
                        if status:
                            cor_fundo = f"rgb({status.consultaStatus_rgb})"

                        if consulta.consulta_status == 1:
                            mensagem = get_template_mensagem(paciente_nome, data_formatada, hora)
                            telefone_paciente = paciente.paciente_telefone if paciente else ""
                            link_whatsapp = gerar_link_whatsapp(telefone_paciente, mensagem)

                    tabela_horarios.append({
                        "Horário": f"{hora}:00",
                        "Profissional": profissional_nome,
                        "Paciente": paciente_nome,
                        "Ação": link_whatsapp,
                        "_cor_fundo": cor_fundo
                    })

            df_horarios = pd.DataFrame(tabela_horarios)

            def apply_styles(row):
                return [f"background-color: {row['_cor_fundo']};"] * len(row)

            styled_df = df_horarios.style.apply(apply_styles, axis=1)

            df_horarios = df_horarios.drop(columns=["_cor_fundo"])

            df_horarios["Ação"] = df_horarios.apply(
                lambda row: f'<a href="{row["Ação"]}" target="_blank"><button>Confirmar</button></a>'
                if row["Ação"] else "",
                axis=1
            )

            st.write(styled_df.to_html(escape=False), unsafe_allow_html=True)

    st.write("### Selecione um intervalo de datas para visualizar e gerenciar consultas")
    col1, col2 = st.columns(2)

    with col1:
        data_inicio = st.date_input("Data de Início", key="data_inicio")
    with col2:
        data_fim = st.date_input("Data de Fim", key="data_fim")

    if data_inicio and data_fim and data_inicio <= data_fim:
        datas_selecionadas = [data_inicio + timedelta(days=i) for i in range((data_fim - data_inicio).days + 1)]
        datas_formatadas = [data.strftime("%Y-%m-%d") for data in datas_selecionadas]

        horarios = list(range(9, 19))
        agenda_dinamica = {hora: {data: "" for data in datas_formatadas} for hora in horarios}

        consultas = session.query(Consulta).filter(Consulta.consulta_data.in_(datas_formatadas)).all()
        for consulta in consultas:
            paciente = session.query(Paciente).filter_by(paciente_id=consulta.consulta_pacienteId).first()
            paciente_nome = paciente.paciente_nome if paciente else "Paciente não encontrado"
            agenda_dinamica[consulta.consulta_hora][consulta.consulta_data] = paciente_nome

        df_agenda = pd.DataFrame.from_dict(agenda_dinamica, orient="index", columns=datas_formatadas)
        df_agenda.index = [f"{hora}:00" for hora in df_agenda.index]

        st.write("### Agenda Dinâmica")
        st.dataframe(df_agenda)

    if st.checkbox("Agendar Nova Consulta"):
        st.write("### Agendar Nova Consulta")
        pacientes = session.query(Paciente).all()
        profissionais = session.query(Profissional).all()
        procedimentos = session.query(Procedimento).all()

        paciente_nome = st.selectbox("Paciente", [p.paciente_nome for p in pacientes])
        profissional_nome = st.selectbox("Profissional", [p.profissional_nome for p in profissionais])
        procedimento_nome = st.selectbox("Procedimento", [p.procedimento_nome for p in procedimentos])
        data_consulta = st.date_input("Data da Consulta")
        hora_consulta = st.time_input("Horário da Consulta")

        if st.button("Agendar"):
            nova_consulta = Consulta(
                consulta_pacienteId=[p.paciente_id for p in pacientes if p.paciente_nome == paciente_nome][0],
                consulta_profissionalId=[p.profissional_id for p in profissionais if p.profissional_nome == profissional_nome][0],
                consulta_procedimentoId=[p.procedimento_id for p in procedimentos if p.procedimento_nome == procedimento_nome][0],
                consulta_data=data_consulta.strftime("%Y-%m-%d"),
                consulta_hora=hora_consulta.hour,
                consulta_status=1
            )
            session.add(nova_consulta)
            session.commit()
            st.success("Consulta agendada com sucesso!")
            st.rerun()
