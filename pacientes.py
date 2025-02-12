import streamlit as st
import requests
from sqlalchemy.orm import sessionmaker
from db.models import engine, Paciente, Convenio

# Cria uma sessão para interagir com o banco de dados
Session = sessionmaker(bind=engine)
session = Session()

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

    # Botão para consultar o CEP
    if st.button("Consultar CEP", key="consultar_cep"):
        if cep:
            dados_cep = consultar_cep(cep)
            if dados_cep:
                st.success("CEP encontrado! Confira os dados abaixo:")
                st.write(f"**Logradouro:** {dados_cep.get('logradouro', 'N/A')}")
                st.write(f"**Bairro:** {dados_cep.get('bairro', 'N/A')}")
                st.write(f"**Cidade:** {dados_cep.get('localidade', 'N/A')}")
                st.write(f"**Estado:** {dados_cep.get('uf', 'N/A')}")
                endereco = dados_cep.get('logradouro')  # Armazena o endereço
            else:
                st.error("CEP inválido ou não encontrado.")
        else:
            st.warning("Por favor, insira um CEP para consulta.")

    # Campos para número e complemento
    numero = st.text_input("Número", key="add_numero")
    complemento = st.text_input("Complemento", key="add_complemento")

    # Botão para enviar o formulário
    if st.button("Enviar", key="enviar_paciente"):
        if nome and telefone and convenio_id and cep and numero:
            dados_cep = consultar_cep(cep)
            if dados_cep:
                # Garante que o endereço seja definido
                if endereco is None:
                    endereco = dados_cep.get('logradouro', '')

                novo_paciente = Paciente(
                    paciente_nome=nome,
                    paciente_telefone=telefone,
                    paciente_convenioId=convenio_id,  # Usa o ID do convênio
                    paciente_cep=cep,
                    paciente_endereco=endereco,
                    paciente_numero=numero,
                    paciente_complemento=complemento
                )
                session.add(novo_paciente)
                session.commit()
                st.success("Dados do paciente cadastrados com sucesso!")
            else:
                st.error("CEP inválido. Por favor, insira um CEP válido.")
        else:
            st.error("Por favor, preencha todos os campos obrigatórios.")


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
                "CEP": paciente.paciente_cep,
                "Endereço": paciente.paciente_endereco,
                "Número": paciente.paciente_numero,
                "Complemento": paciente.paciente_complemento
            })

        # Exibe a tabela
        st.table(dados_pacientes)
    
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
            novo_cep = st.text_input("CEP", value=paciente_selecionado.paciente_cep, key="edit_cep")
            novo_numero = st.text_input("Número", value=paciente_selecionado.paciente_numero, key="edit_numero")
            novo_complemento = st.text_input("Complemento", value=paciente_selecionado.paciente_complemento, key="edit_complemento")

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
                paciente_selecionado.paciente_cep = novo_cep
                paciente_selecionado.paciente_numero = novo_numero
                paciente_selecionado.paciente_complemento = novo_complemento
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