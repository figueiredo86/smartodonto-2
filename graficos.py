import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from db.models import engine, Convenio, Consulta
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# # Configura a URL do banco de dados
# DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PWD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_DATABASE')}"

# # Cria a engine do SQLAlchemy
# engine = create_engine(
#     DATABASE_URL,
#     pool_recycle=3600,  # Recicla a conexão após 1 hora
#     pool_timeout=30,    # Tempo máximo de espera para obter uma conexão
#     pool_pre_ping=True  # Verifica a conexão antes de usá-la
# )

# Cria a fábrica de sessões
Session = sessionmaker(bind=engine)

# Função para criar uma nova sessão
def criar_sessao():
    return Session()

# Função para obter os dados dos convênios mais listados
def obter_top_convenios(data_inicio, data_fim):
    session = criar_sessao()
    try:
        # Consulta para contar a frequência de cada convênio no período selecionado
        resultados = (
            session.query(Convenio.convenio_nome, func.count(Consulta.consulta_id).label("total"))
            .join(Consulta, Convenio.convenio_id == Consulta.consulta_convenioId)
            .filter(Consulta.consulta_data.between(data_inicio, data_fim))
            .group_by(Convenio.convenio_nome)
            .order_by(func.count(Consulta.consulta_id).desc())
            .all()
        )
        # Converte os resultados em um DataFrame
        dados = pd.DataFrame(resultados, columns=["Convênio", "Total"])
        return dados
    except SQLAlchemyError as e:
        st.error(f"Erro ao consultar o banco de dados: {e}")
        return pd.DataFrame()
    finally:
        session.close()

# Função para criar o gráfico Treemap
def criar_treemap(dados):
    if not dados.empty:
        fig = px.treemap(
            dados,
            path=["Convênio"],  # Hierarquia do gráfico (apenas convênios)
            values="Total",      # Tamanho dos blocos
            title="Top Convênios Mais Listados",
            color="Total",       # Cor dos blocos baseada no total
            color_continuous_scale="Blues"  # Escala de cores
        )
        fig.update_traces(textinfo="label+value")  # Exibe o nome e o valor no bloco
        return fig
    else:
        st.warning("Nenhum dado encontrado para o período selecionado.")
        return None

# Função principal da página
def mostrar_pagina_graficos():
    st.title("SmartOdonto - Análise de Convênios")
    st.write("### Gráfico de Top Convênios")

    # Filtros de período
    st.write("#### Selecione o Período")
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data de Início", datetime.now() - timedelta(days=30))
    with col2:
        data_fim = st.date_input("Data de Fim", datetime.now())

    # Verifica se as datas são válidas
    if data_inicio > data_fim:
        st.error("A data de início não pode ser maior que a data de fim.")
    else:
        # Obtém os dados dos convênios
        dados = obter_top_convenios(data_inicio.strftime("%Y-%m-%d"), data_fim.strftime("%Y-%m-%d"))

        # Exibe os dados brutos (opcional)
        if st.checkbox("Mostrar dados brutos"):
            st.write(dados)

        # Cria e exibe o gráfico Treemap
        if not dados.empty:
            fig = criar_treemap(dados)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

# Executa a aplicação
if __name__ == "__main__":
    mostrar_pagina_graficos()