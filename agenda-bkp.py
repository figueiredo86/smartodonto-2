import streamlit as st
from sqlalchemy.orm import sessionmaker
from db.models import engine, Horario, Profissional, Paciente, Procedimento, Consulta, ConsultaStatus, Template
from datetime import datetime, timedelta
import pandas as pd

# Criar sessão para o banco de dados
Session = sessionmaker(bind=engine)
session = Session()

def get_template_mensagem(paciente_nome, data, hora):
    """
    Retorna a mensagem do template com o nome do paciente, data e horário formatados.
    """
    template = session.query(Template).first()
    if template:
        # Formata a data no padrão DD/MM/AAAA
        data_formatada = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
        # Formata o horário no padrão HH:MM
        horario_formatado = f"{hora:02d}:00"  # Adiciona zero à esquerda se necessário
        return (
            template.template_texto
            .replace("{nome}", paciente_nome)
            .replace("{data}", data_formatada)
            .replace("{hora}", horario_formatado)
        )
    # Template padrão caso não haja um template no banco de dados
    return f"Olá {paciente_nome}. Tudo bem? Podemos confirmar sua consulta para o dia {data_formatada} às {horario_formatado}?"

def gerar_link_whatsapp(telefone, mensagem):
    """
    Gera o link do WhatsApp com o número de telefone e a mensagem formatada.
    O telefone deve estar no formato internacional (ex: +5511999999999).
    """
    # Remove caracteres especiais do telefone (ex: espaços, parênteses, hífens)
    telefone_formatado = "".join(filter(str.isdigit, telefone))
    # Adiciona o código do país (+55 para Brasil) se não estiver presente
    if not telefone_formatado.startswith("+"):
        telefone_formatado = f"+55{telefone_formatado}"
    # Gera o link do WhatsApp
    return f"https://wa.me/{telefone_formatado}?text={mensagem.replace(' ', '%20')}"

def mostrar_pagina_agenda():
    st.title("SmartOdonto - Agenda")

    # Exibição da agenda do dia
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
                        "Cor de Fundo": cor_fundo,
                        "Ação": link_whatsapp  # Renomeado para "Ação"
                    })

            df_horarios = pd.DataFrame(tabela_horarios)

            # Função para aplicar estilos ao DataFrame
            def apply_styles(row):
                return [f"background-color: {row['Cor de Fundo']};"] * len(df_horarios.columns)

            # Adiciona botões de WhatsApp na coluna "Ação"
            df_horarios["Ação"] = df_horarios.apply(
                lambda row: f'<a href="{row["Ação"]}" target="_blank"><button>Confirmar</button></a>'
                if row["Ação"] else "",
                axis=1
            )

            # Aplica os estilos ao DataFrame
            styled_df = df_horarios.style.apply(apply_styles, axis=1)
            st.write(styled_df.to_html(escape=False), unsafe_allow_html=True)

    # Agenda Dinâmica
    st.write("### Selecione um intervalo de datas para visualizar e gerenciar consultas")
    col1, col2 = st.columns(2)

    with col1:
        data_inicio = st.date_input("Data de Início", key="data_inicio")
    with col2:
        data_fim = st.date_input("Data de Fim", key="data_fim")

    if data_inicio and data_fim and data_inicio <= data_fim:
        datas_selecionadas = [data_inicio + timedelta(days=i) for i in range((data_fim - data_inicio).days + 1)]
        datas_formatadas = [data.strftime("%Y-%m-%d") for data in datas_selecionadas]

        horarios = list(range(9, 19))  # De 9h às 18h
        agenda_dinamica = {hora: {data: "" for data in datas_formatadas} for hora in horarios}
        cores = {data: {hora: "white" for hora in horarios} for data in datas_formatadas}

        consultas = session.query(Consulta).filter(Consulta.consulta_data.in_(datas_formatadas)).all()

        for consulta in consultas:
            paciente = session.query(Paciente).filter_by(paciente_id=consulta.consulta_pacienteId).first()
            paciente_nome = paciente.paciente_nome if paciente else "Paciente não encontrado"

            status = session.query(ConsultaStatus).filter_by(consultaStatus_id=consulta.consulta_status).first()
            cor_fundo = f"rgb({status.consultaStatus_rgb})" if status else "white"

            agenda_dinamica[consulta.consulta_hora][consulta.consulta_data] = paciente_nome
            cores[consulta.consulta_data][consulta.consulta_hora] = cor_fundo

        df_agenda = pd.DataFrame.from_dict(agenda_dinamica, orient="index", columns=datas_formatadas)
        df_agenda.index = [f"{hora}:00" for hora in df_agenda.index]

        # Função para aplicar estilos ao DataFrame
        def apply_styles(row):
            hora = int(row.name.split(":")[0])  # Extrai a hora do índice
            return [f"background-color: {cores[col][hora]};" for col in df_agenda.columns]

        st.write("### Agenda Dinâmica")
        st.dataframe(df_agenda.style.apply(apply_styles, axis=1))

    # Formulário para agendar nova consulta
    if st.checkbox("Agendar Nova Consulta"):
        st.write("### Agendar Nova Consulta")

        profissionais_com_horarios = session.query(Profissional).join(Horario).distinct().all()
        pacientes = session.query(Paciente).all()
        procedimentos = session.query(Procedimento).all()

        if not profissionais_com_horarios:
            st.warning("Nenhum profissional com horários cadastrados.")
            return

        profissional_nome = st.selectbox("Selecione o Profissional:", [p.profissional_nome for p in profissionais_com_horarios])
        profissional_id = next((p.profissional_id for p in profissionais_com_horarios if p.profissional_nome == profissional_nome), None)

        paciente_nome = st.selectbox("Selecione o Paciente:", [p.paciente_nome for p in pacientes])
        paciente_id = next((p.paciente_id for p in pacientes if p.paciente_nome == paciente_nome), None)

        procedimento_nome = st.selectbox("Selecione o Procedimento:", [p.procedimento_nome for p in procedimentos])
        procedimento_id = next((p.procedimento_id for p in procedimentos if p.procedimento_nome == procedimento_nome), None)

        horarios_disponiveis = [f"{hora}:00" for hora in range(9, 19) if not session.query(Consulta).filter(
            Consulta.consulta_data == data_formatada,
            Consulta.consulta_hora == hora,
            Consulta.consulta_profissionalId == profissional_id
        ).first()]

        horario_selecionado = st.selectbox("Selecione o Horário:", horarios_disponiveis)

        if st.button("Agendar"):
            nova_consulta = Consulta(
                consulta_pacienteId=paciente_id,
                consulta_profissionalId=profissional_id,
                consulta_procedimentoId=procedimento_id,
                consulta_data=data_formatada,
                consulta_hora=int(horario_selecionado.split(":")[0]),
                consulta_status=1
            )
            session.add(nova_consulta)
            session.commit()
            st.success("Consulta agendada com sucesso!")
            st.rerun()