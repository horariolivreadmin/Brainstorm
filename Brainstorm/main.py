import os
import sys

# Garante que o Python reconheça a pasta raiz do projeto para os imports funcionarem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa a classe principal da interface gráfica (que vamos isolar depois)
from ui.app_window import DistillerApp

def main():
    """
    Ponto de entrada (Entry Point) da aplicação.
    Responsável apenas por instanciar a Janela e iniciar o loop principal.
    """
    print("[SISTEMA] Iniciando o Brainstorm Distiller...")
    
    # Cria a instância da nossa interface gráfica
    app = DistillerApp()
    
    # Inicia o loop que mantém a janela aberta
    app.mainloop()

if __name__ == "__main__":
    main()
