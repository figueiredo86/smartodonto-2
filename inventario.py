# Arquivo: inventario.py

import streamlit as st
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db.models import engine, Inventario
from fpdf import FPDF  # Biblioteca para gerar PDFs

# Cria a fábrica de sessões
Session = sessionmaker(bind=engine)

# Função para criar uma nova sessão
def criar_sessao():
    return Session()

# Função para adicionar um novo item ao inventário
def adicionar_item(nome, descricao):
    session = criar_sessao()  # Recria a sessão
    try:
        novo_item = Inventario(
            item_nome=nome,
            item_descricao=descricao,
            item_quantidade=0  # Inicia com quantidade zero
        )
        session.add(novo_item)
        session.commit()
        st.success("Item cadastrado com sucesso!")
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Erro ao cadastrar item: {e}")
    finally:
        session.close()  # Fecha a sessão após o uso

# Função para editar um item existente
def editar_item(item, novo_nome, nova_descricao):
    session = criar_sessao()  # Recria a sessão
    try:
        item.item_nome = novo_nome
        item.item_descricao = nova_descricao
        session.commit()
        st.success("Item atualizado com sucesso!")
        st.rerun()
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Erro ao atualizar item: {e}")
    finally:
        session.close()  # Fecha a sessão após o uso

# Função para atualizar a quantidade de um item
def atualizar_quantidade(item_id, nova_quantidade):
    session = criar_sessao()  # Recria a sessão
    try:
        item = session.query(Inventario).filter_by(item_id=item_id).first()
        if item:
            item.item_quantidade = nova_quantidade
            session.commit()
            st.success("Quantidade atualizada com sucesso!")
        else:
            st.error("Item não encontrado.")
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Erro ao atualizar quantidade: {e}")
    finally:
        session.close()  # Fecha a sessão após o uso

# Função para excluir um item
def excluir_item(item):
    session = criar_sessao()  # Recria a sessão
    try:
        session.delete(item)
        session.commit()
        st.success("Item excluído com sucesso!")
        st.rerun()
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"Erro ao excluir item: {e}")
    finally:
        session.close()  # Fecha a sessão após o uso

# Função para aplicar cor ao nome do item com base na quantidade
def aplicar_cor_nome(nome, quantidade):
    if quantidade > 0 and quantidade <= 5:
        return f"<span style='background-color: #FF6347;'>{nome}</span>"
    elif quantidade > 5 and quantidade <= 10:
        return f"<span style='background-color: #F0E68C;'>{nome}</span>"
    else:
        return nome

# Função para gerar PDF da tabela
def gerar_pdf_tabela(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Adiciona o título do PDF
    pdf.cell(200, 10, txt="Relatório de Itens do Inventário", ln=True, align="C")

    # Adiciona os cabeçalhos da tabela
    colunas = df.columns
    for coluna in colunas:
        pdf.cell(40, 10, txt=coluna, border=1, align="C")
    pdf.ln()

    # Adiciona os dados da tabela
    for index, row in df.iterrows():
        for coluna in colunas:
            pdf.cell(40, 10, txt=str(row[coluna]), border=1, align="C")
        pdf.ln()

    # Salva o PDF em um arquivo temporário
    pdf_output = "tabela_inventario.pdf"
    pdf.output(pdf_output)
    return pdf_output

# Função principal para exibir a página de inventário
def mostrar_pagina_inventario():
    st.title("SmartOdonto - Inventário")

    # Formulário para adicionar novo item
    st.write("### Adicionar Novo Item")
    item_nome = st.text_input("Nome do Item")
    item_descricao = st.text_area("Descrição do Item")

    if st.button("Salvar Item"):
        if item_nome:
            adicionar_item(item_nome, item_descricao)
        else:
            st.error("Por favor, preencha o nome do item.")

    # Exibe os itens cadastrados
    if st.checkbox("Exibir itens", value=True):
        session = criar_sessao()  # Recria a sessão
        try:
            itens = session.query(Inventario).all()
        except SQLAlchemyError as e:
            st.error(f"Erro ao realizar consulta: {e}")
            itens = []
        finally:
            session.close()  # Fecha a sessão após o uso

        if itens:
            # Cria um DataFrame para exibição na tabela
            dados_itens = []
            for item in itens:
                dados_itens.append({
                    "ID": item.item_id,
                    "Nome": item.item_nome,
                    "Descrição": item.item_descricao,
                    "Quantidade": item.item_quantidade,
                    "Status": "Ativo" if item.item_status == 1 else "Inativo"
                })
            df = pd.DataFrame(dados_itens)

            # Exibe a tabela com campos editáveis e botões de incremento/decremento
            st.write("### Itens Cadastrados")
            edited_df = df.copy()  # Cria uma cópia do DataFrame para edição

            # Adiciona uma coluna para ações
            edited_df["Ações"] = ""

            # Exibe cada item com campos editáveis e botões
            for index, row in edited_df.iterrows():
                col1, col2, col3, col4 = st.columns([4, 2, 2, 2])
                with col1:
                    # Aplica a cor ao nome do item com base na quantidade
                    nome_colorido = aplicar_cor_nome(row["Nome"], row["Quantidade"])
                    st.markdown(nome_colorido, unsafe_allow_html=True)
                    st.write(f"--{row['Descrição']}--")
                with col2:
                    nova_quantidade = st.number_input(
                        "Quantidade",
                        value=row["Quantidade"],
                        min_value=0,
                        key=f"quantidade_{row['ID']}"
                    )
                    edited_df.at[index, "Quantidade"] = nova_quantidade

            # Botão para salvar as alterações
            if st.button("Salvar Alterações de Quantidade"):
                for index, row in edited_df.iterrows():
                    item_id = row["ID"]
                    nova_quantidade = row["Quantidade"]
                    atualizar_quantidade(item_id, nova_quantidade)
                st.rerun()  # Recarrega a página para exibir as alterações

            # Botão para gerar e exibir o PDF
            if st.button("Gerar PDF da Tabela"):
                pdf_output = gerar_pdf_tabela(df)
                with open(pdf_output, "rb") as pdf_file:
                    st.download_button(
                        label="Baixar PDF",
                        data=pdf_file,
                        file_name="tabela_inventario.pdf",
                        mime="application/pdf"
                    )
                st.success("PDF gerado com sucesso! Clique no botão acima para baixar.")
        else:
            st.info("Nenhum item cadastrado no momento.")

        # Opções de editar e excluir
        if st.checkbox("Editar/Remover item"):
            session = criar_sessao()  # Recria a sessão
            try:
                itens = session.query(Inventario).all()
                item_id = st.selectbox(
                    "Selecione um item para editar ou excluir:",
                    options=[i.item_id for i in itens],
                    format_func=lambda id: session.query(Inventario).filter_by(item_id=id).first().item_nome,
                    key="select_item"
                )
                item_selecionado = session.query(Inventario).filter_by(item_id=item_id).first()

                # Formulário de edição
                st.write(f"### Editando Item: {item_selecionado.item_nome}")
                novo_nome = st.text_input("Nome do Item", value=item_selecionado.item_nome, key="edit_nome")
                nova_descricao = st.text_area("Descrição do Item", value=item_selecionado.item_descricao, key="edit_descricao")

                if st.button("Salvar Edições", key="salvar_edicoes"):
                    editar_item(item_selecionado, novo_nome, nova_descricao)

                if st.button("Excluir Item", key="excluir_item"):
                    excluir_item(item_selecionado)
            except SQLAlchemyError as e:
                st.error(f"Erro ao realizar consulta: {e}")
            finally:
                session.close()  # Fecha a sessão após o uso

# Executa a aplicação
if __name__ == "__main__":
    mostrar_pagina_inventario()