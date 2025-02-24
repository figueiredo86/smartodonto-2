import time
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError


class Banco:
    def __init__(self):
        criar_sessao()

    def criar_sessao():
        Session = sessionmaker(bind=engine)
        session = Session()

    def run_mysql(self,query)
        try:
            session.add(query)
            session.commit()
            st.success("Consulta agendada com sucesso!")
            st.rerun()
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao agendar consulta: {e}")
            time.sleep(5)
            session.close()
            session = Session()

            