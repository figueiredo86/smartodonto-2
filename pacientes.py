import streamlit as st
import requests
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db.models import engine, Paciente, Convenio

# Cria uma sessão para interagir com o banco de dados
Session = sessionmaker(bind=engine)

def consultar_cep(cep):
    # Verifica se o CEP tem 8 dígitos
    if len(cep) != 8 or not cep.isdigit():
        st.error("CEP inválido. O CEP deve conter exatamente 8 dígitos.")
        return None

    url = f"https://viacep.com.br/ws/{cep}/json/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

        dados = response.json()
        if "erro" in dados:
            st.error("CEP não encontrado.")
            return None
        return dados
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao consultar o CEP: {e}")
        return None

def mostrar_pagina_pacientes():
    st.title("Cadastro de Pacientes")
    try:
        session = Session()
        # Consulta todos os convênios cadastrados
        convenios = session.query(Convenio).all()
        convenios_dict = {c.convenio_id: c.convenio_nome for c in convenios}

        # Consulta todos os pacientes cadastrados
        pacientes = session.query(Paciente).all()

        # Opções de editar ou remover paciente
        st.write("### Editar ou Remover Paciente")

        # Formulário para adicionar novo paciente
        st.write("### Adicionar Novo Paciente")

        # Campos do formulário
        nome = st.text_input("Nome", key="add_nome")
        telefone = st.text_input("Telefone", key="add_telefone")
        
        # Selectbox para escolher o convênio (exibe o nome, mas retorna o ID)
        convenio_nome = st.selectbox(
            "Convênio",
            options=list(convenios_dict.values()),  # Exibe os nomes dos convênios
            key="add_convenio"
        )
        # Obtém o ID do convênio selecionado
        convenio_id = [k for k, v in convenios_dict.items() if v == convenio_nome][0]

        cep = st.text_input("CEP", key="add_cep")

        # Variável para armazenar o endereço
        endereco = None

        # Botão para consultar o CEP (só aparece se o CEP não estiver vazio)
        if cep:  # Verifica se o campo de CEP não está vazio
            if st.button("Consultar CEP", key="consultar_cep"):
                dados_cep = consultar_cep(cep)
                if dados_cep:  # Verifica se dados_cep não é None
                    st.success("CEP encontrado! Confira os dados abaixo:")
                    st.write(f"**Logradouro:** {dados_cep.get('logradouro', 'N/A')}")
                    st.write(f"**Bairro:** {dados_cep.get('bairro', 'N/A')}")
                    st.write(f"**Cidade:** {dados_cep.get('localidade', 'N/A')}")
                    st.write(f"**Estado:** {dados_cep.get('uf', 'N/A')}")
                    endereco = dados_cep.get('logradouro', '')  # Armazena o endereço
                else:
                    st.error("CEP inválido ou não encontrado.")
        else:
            st.info("O campo de CEP é opcional. Se não for preenchido, o endereço não será consultado.")

        # Campos para número e complemento
        numero = st.text_input("Número", key="add_numero")
        complemento = st.text_input("Complemento", key="add_complemento")

        # Botão para enviar o formulário
        if st.button("Enviar", key="enviar_paciente"):
            if nome and telefone and convenio_id:  # CEP não é mais obrigatório
                # Se o CEP foi fornecido, consulta os dados do CEP
                if cep:
                    dados_cep = consultar_cep(cep)
                    if dados_cep:
                        endereco = dados_cep.get('logradouro', '')
                    else:
                        st.error("CEP inválido. Por favor, insira um CEP válido.")
                        return  # Impede a inserção no banco de dados se o CEP for inválido
                else:
                    endereco = None  # Se o CEP não foi fornecido, o endereço será NULL

                # Cria o novo paciente
                novo_paciente = Paciente(
                    paciente_nome=nome,
                    paciente_telefone=telefone,
                    paciente_convenioId=convenio_id,  # Usa o ID do convênio
                    paciente_cep=cep if cep else None,  # Insere NULL se o CEP estiver vazio
                    paciente_endereco=endereco,  # Pode ser None
                    paciente_numero=numero,
                    paciente_complemento=complemento
                )

                try:
                    session.add(novo_paciente)
                    session.commit()
                    st.success("Dados do paciente cadastrados com sucesso!")
                except Exception as e:
                    session.rollback()
                    st.error(f"Erro ao cadastrar paciente: {e}")
            else:
                st.error("Por favor, preencha todos os campos obrigatórios (Nome, Telefone, Convênio e Número).")

        # Exibe os dados cadastrados em uma tabela
        if st.checkbox("Mostrar pacientes cadastrados", key="mostrar_pacientes", value=True):
            pacientes = session.query(Paciente).all()

            # Cria uma lista de dicionários com os dados dos pacientes
            dados_pacientes = []
            for paciente in pacientes:
                # Busca o nome do convênio correspondente ao paciente_convenioId
                nome_convenio = convenios_dict.get(paciente.paciente_convenioId, "Convênio não encontrado")
                
                dados_pacientes.append({
                    "ID": paciente.paciente_id,
                    "Nome": paciente.paciente_nome,
                    "Telefone": paciente.paciente_telefone,
                    "Convênio": nome_convenio,  # Exibe o nome do convênio
                    "CEP": paciente.paciente_cep if paciente.paciente_cep else "Não informado",
                    "Endereço": paciente.paciente_endereco if paciente.paciente_endereco else "Não informado",
                    "Número": paciente.paciente_numero,
                    "Complemento": paciente.paciente_complemento if paciente.paciente_complemento else "Não informado"
                })

            # Exibe a tabela
            st.table(dados_pacientes)
        
        # Opção de editar ou remover paciente
        if st.checkbox("Editar/Remover paciente"):
            if pacientes:
                # Selectbox para escolher um paciente
                paciente_id = st.selectbox(
                    "Selecione um paciente:",
                    options=[p.paciente_id for p in pacientes],
                    format_func=lambda id: f"{session.query(Paciente).filter_by(paciente_id=id).first().paciente_nome} (ID: {id})",
                    key="select_paciente"
                )

                # Busca o paciente selecionado
                paciente_selecionado = session.query(Paciente).filter_by(paciente_id=paciente_id).first()

                # Formulário de edição
                st.write(f"### Editando Paciente: {paciente_selecionado.paciente_nome}")
                novo_nome = st.text_input("Nome", value=paciente_selecionado.paciente_nome, key="edit_nome")
                novo_telefone = st.text_input("Telefone", value=paciente_selecionado.paciente_telefone, key="edit_telefone")
                novo_cep = st.text_input("CEP", value=paciente_selecionado.paciente_cep if paciente_selecionado.paciente_cep else "", key="edit_cep")
                novo_numero = st.text_input("Número", value=paciente_selecionado.paciente_numero, key="edit_numero")
                novo_complemento = st.text_input("Complemento", value=paciente_selecionado.paciente_complemento if paciente_selecionado.paciente_complemento else "", key="edit_complemento")

                # Selectbox para escolher o convênio (exibe o nome, mas retorna o ID)
                convenio_nome = st.selectbox(
                    "Convênio",
                    options=list(convenios_dict.values()),  # Exibe os nomes dos convênios
                    index=list(convenios_dict.values()).index(convenios_dict.get(paciente_selecionado.paciente_convenioId, "Convênio não encontrado")),
                    key="edit_convenio"
                )
                # Obtém o ID do convênio selecionado
                novo_convenio_id = [k for k, v in convenios_dict.items() if v == convenio_nome][0]

                # Botão para salvar as edições
                if st.button("Salvar Edições", key="salvar_edicoes"):
                    paciente_selecionado.paciente_nome = novo_nome
                    paciente_selecionado.paciente_telefone = novo_telefone
                    paciente_selecionado.paciente_cep = novo_cep if novo_cep else None
                    paciente_selecionado.paciente_numero = novo_numero
                    paciente_selecionado.paciente_complemento = novo_complemento if novo_complemento else None
                    paciente_selecionado.paciente_convenioId = novo_convenio_id

                    session.commit()
                    st.success("Paciente atualizado com sucesso!")
                    st.rerun()

                # Botão para remover o paciente
                if st.button("Remover Paciente", key="remover_paciente"):
                    session.delete(paciente_selecionado)
                    session.commit()
                    st.success("Paciente removido com sucesso!")
                    st.rerun()
            else:
                st.info("Nenhum paciente cadastrado no momento.")
    except SQLAlchemyError as e:
        st.error(f"Erro ao consultar profissionais: {e}")
    finally:
        session.close()  # Fecha a sessão