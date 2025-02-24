from db.commands import Banco

banco = Banco()

listaHorarios = banco.selectAll('horarios')