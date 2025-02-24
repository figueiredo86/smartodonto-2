import time
from db.models import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError


class Banco:
    def __init__(self):
        print("iniciando sessão com mysql")
        self.criar_sessao()

    def criar_sessao(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def encerrar_session():
        session.remove()

    def selectAll(self, table):
        tabela = table
        print(f"Pesquisando na tabela: {tabela}")
        horarios = self.session.query(tabela).all()
        print(horarios)


    def run_mysql(self,query, msg):
        try:
            session.add(query)
            session.commit()
            st.success(msg)
            st.rerun()
        except Exception as e:
            session.rollback()
            st.error(f"Erro ao agendar consulta: {e}")
            time.sleep(5)
            session.close()
            session = Session()

            