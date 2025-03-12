import streamlit as st
from pacientes import mostrar_pagina_pacientes
from convenios import mostrar_pagina_convenios
from procedimentos import mostrar_pagina_procedimentos
from profissionais import mostrar_pagina_profissionais
from agenda import mostrar_pagina_agenda
from horarios import mostrar_pagina_horarios
from inventario import mostrar_pagina_inventario

# Sidebar com menu
st.sidebar.title("Menu")
opcao = st.sidebar.radio(
    "Selecione uma opção:",
    ("Pacientes", "Convênios", "Procedimentos", "Profissionais", "Agenda", "Horários", "Inventário")
)


st.title("SmartOdonto")

# Navegação entre páginas
if opcao == "Pacientes":
    mostrar_pagina_pacientes()
elif opcao == "Convênios":
    mostrar_pagina_convenios()
elif opcao == "Procedimentos":
    mostrar_pagina_procedimentos()
elif opcao == "Profissionais":
    mostrar_pagina_profissionais()
elif opcao == "Horários":
    mostrar_pagina_horarios()
elif opcao == "Agenda":
    mostrar_pagina_agenda()
elif opcao == "Inventário":
    mostrar_pagina_inventario()