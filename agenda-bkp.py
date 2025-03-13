from enum import Enum
import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db.models import engine, Horario, Profissional, Paciente, Procedimento, Consulta, Template
from datetime import datetime, timedelta
import pandas as pd

# Definir a enumeração ConsultaStatus
class ConsultaStatus(Enum):
    AGENDADO = "Agendado"
    CONFIRMADO = "Confirmado"
    CANCELADO = "Cancelado"
    REALIZADO = "Realizado"

# Criar sessão para o banco de dados
Session = sessionmaker(bind=engine)

def get_template_mensagem(paciente_nome, data, hora):
    session = Session()
    data_formatada = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
    horario_formatado = f"{hora:02d}:00"
    try:
        # Busca o template com ID 1 (ou o template desejado)
        template = session.query(Template).filter(Template.template_id == 1).first()
        if template:
            # Substitui os placeholders no template pelo conteúdo formatado
            mensagem_formatada = (
                template.template_texto
                .replace("{paciente_nome}", paciente_nome)
                .replace("{data_formatada}", data_formatada)
                .replace("{horario_formatado}", horario_formatado)
            )
            return mensagem_formatada
    except SQLAlchemyError as e:
        st.error(f"Erro ao buscar template: {e}")
    finally:
        session.close()
    
    # Retorno padrão caso o template não seja encontrado
    return f"Olá {paciente_nome}. Tudo bem? Podemos confirmar sua consulta para o dia {data_formatada} às {horario_formatado}?"

def gerar_link_whatsapp(telefone, mensagem):
    telefone_formatado = "".join(filter(str.isdigit, telefone))
    if not telefone.startswith("+"):
        telefone_formatado = f"+55{telefone_formatado}"
    # Codifica a mensagem para uso em URLs
    mensagem_codificada = mensagem.replace(' ', '%20').replace('\n', '%0A')
    return f"https://wa.me/{telefone_formatado}?text={mensagem_codificada}"

def agendar_consulta(paciente_id, profissional_id, procedimento_id, convenio_id, data_consulta, horario_selecionado, procedimento_valor):
    session = Session()
    try:
        nova_consulta = Consulta(
            consulta_pacienteId=paciente_id,
            consulta_profissionalId=profissional_id,
            consulta_procedimentoId=procedimento_id,
            consulta_convenioId=convenio_id,
            consulta_data=data_consulta.strftime("%Y-%m-%d"),
            consulta_hora=horario_selecionado.hour,
            consulta_status=ConsultaStatus.AGENDADO.value,  # Usando o valor da enumeração
            consulta_valor_total=procedimento_valor
        )
        session.add(nova_consulta)
        session.commit()
        st.success("Consulta agendada com sucesso!")
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Erro ao agendar consulta: {e}")
    finally:
        session.close()

def mostrar_pagina_agenda():
    st.title("SmartOdonto - Agenda")
    session = Session()
    
    st.write("### Selecione uma data para visualizar as consultas")
    data_selecionada = st.date_input("Escolha a data")
    
    if data_selecionada:
        data_formatada = data_selecionada.strftime("%Y-%m-%d")
        try:
            consultas = session.query(Consulta).filter(Consulta.consulta_data == data_formatada).all()
            if consultas:
                tabela_horarios = []
                for consulta in consultas:
                    paciente = session.query(Paciente).filter_by(paciente_id=consulta.consulta_pacienteId).first()
                    paciente_nome = paciente.paciente_nome if paciente else "Paciente não encontrado"
                    mensagem = get_template_mensagem(paciente_nome, data_formatada, consulta.consulta_hora)
                    link_whatsapp = gerar_link_whatsapp(paciente.paciente_telefone if paciente else "", mensagem)
                    tabela_horarios.append({
                        "Horário": f"{consulta.consulta_hora}:00",
                        "Paciente": paciente_nome,
                        "Ação": f'<a href="{link_whatsapp}" target="_blank"><button>Confirmar</button></a>'
                    })
                df_horarios = pd.DataFrame(tabela_horarios)
                st.write(df_horarios.to_html(escape=False), unsafe_allow_html=True)
            else:
                st.write("Nenhuma consulta agendada para esta data.")
        except SQLAlchemyError as e:
            st.error(f"Erro ao buscar consultas: {e}")
    
    session.close()

    if st.checkbox("Selecionar intervalo de datas para consulta"):
        st.write("### Agenda Dinâmica")
        data_inicio = st.date_input("Data de Início")
        data_fim = st.date_input("Data de Fim")
        if data_inicio and data_fim and data_inicio <= data_fim:
            datas_selecionadas = [data_inicio + timedelta(days=i) for i in range((data_fim - data_inicio).days + 1)]
            datas_formatadas = [data.strftime("%Y-%m-%d") for data in datas_selecionadas]
            
            try:
                consultas = session.query(Consulta).filter(Consulta.consulta_data.in_(datas_formatadas)).all()
                agenda_dinamica = {hora: {data: "" for data in datas_formatadas} for hora in range(9, 19)}
                
                for consulta in consultas:
                    paciente = session.query(Paciente).filter_by(paciente_id=consulta.consulta_pacienteId).first()
                    paciente_nome = paciente.paciente_nome if paciente else "Paciente não encontrado"
                    agenda_dinamica[consulta.consulta_hora][consulta.consulta_data] = paciente_nome
                
                df_agenda = pd.DataFrame.from_dict(agenda_dinamica, orient="index", columns=datas_formatadas)
                df_agenda.index = [f"{hora}:00" for hora in df_agenda.index]
                
                st.dataframe(df_agenda)
            except SQLAlchemyError as e:
                st.error(f"Erro ao buscar consultas: {e}")

    if st.checkbox("Agendar Nova Consulta"):
        st.write("### Agendar Nova Consulta")
        convenio_padrao = 1
        
        session = Session()
        try:
            pacientes = session.query(Paciente).all()
            profissionais = session.query(Profissional).all()
            procedimentos = session.query(Procedimento).all()
        finally:
            session.close()

        paciente_nome = st.selectbox("Selecione o Paciente", [p.paciente_nome for p in pacientes])
        paciente_id = next((p.paciente_id for p in pacientes if p.paciente_nome == paciente_nome), None)

        profissional_nome = st.selectbox("Selecione o Profissional", [p.profissional_nome for p in profissionais])
        profissional_id = next((p.profissional_id for p in profissionais if p.profissional_nome == profissional_nome), None)

        procedimento_nome = st.selectbox("Selecione o Procedimento", [p.procedimento_nome for p in procedimentos])
        procedimento_id = next((p.procedimento_id for p in procedimentos if p.procedimento_nome == procedimento_nome), None)
        procedimento_valor = next((p.procedimento_valor for p in procedimentos if p.procedimento_nome == procedimento_nome), 0.0)

        data_consulta = st.date_input("Data da Consulta")
        horario_selecionado = st.time_input("Horário da Consulta", step=3600)

        if st.button("Agendar"):
            agendar_consulta(paciente_id, profissional_id, procedimento_id, convenio_padrao, data_consulta, horario_selecionado, procedimento_valor)

# Executar a aplicação
if __name__ == "__main__":
    mostrar_pagina_agenda()