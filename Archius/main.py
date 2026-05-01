import os
import sys

from Utils.Chunker import processar_arquivos_entrada
from Core.Orchestrator import PipelineOrchestrator
from Utils.Renderer import gerar_markdown_final

# Configurações Constantes do Sistema
DIR_INPUT = "Data/1_input"
DIR_CHUNKS = "Data/2_chunks"
DIR_STATE = "Data/3_state"
DIR_OUTPUT = "Data/4_output"
DIR_DEBUG = "Data/debug_erros"

def garantir_infraestrutura():
    """Garante que todas as pastas obrigatórias existam no disco."""
    print("🛠️  Validando diretórios da esteira...")
    pastas = [DIR_INPUT, DIR_CHUNKS, DIR_STATE, DIR_OUTPUT, DIR_DEBUG]
    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)

def main():
    """Ponto central e determinístico para ignição da arquitetura de múltiplos estágios."""
    print("================================================================")
    print("🚀 INICIANDO PIPELINE DE DESTILAÇÃO DE CONHECIMENTO ZERO TRUST")
    print("================================================================\n")
    
    garantir_infraestrutura()
    
    try:
        # ===== ETAPA 1: Ingestão de Dados =====
        print("\n[ FASE 1: INGESTÃO E FATIAMENTO ]")
        processar_arquivos_entrada(pasta_input=DIR_INPUT, pasta_output=DIR_CHUNKS)
        
        # ===== ETAPA 2: Inteligência Artificial =====
        print("\n[ FASE 2: ORQUESTRAÇÃO DOS AGENTES MULTI-TURN ]")
        orchestrator = PipelineOrchestrator()
        # Nota: O orchestrator já aponta para as pastas 'Data/2_chunks/' e 'Data/debug_erros/' internamente,
        # mas mantemos a hierarquia lógica limpa e blindada no Main.
        orchestrator.executar_pipeline()
        
        # ===== ETAPA 3: Compilação de Saída =====
        print("\n[ FASE 3: RENDERIZAÇÃO DA DOCUMENTAÇÃO SSOT ]")
        gerar_markdown_final(pasta_estado=DIR_STATE, pasta_output=DIR_OUTPUT)
        
        print("\n✅ Fluxo arquitetural concluído com excelência.")
        print(f"👉 Você pode conferir a saída unificada em: {DIR_OUTPUT}/Documentacao_Oficial.md")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupção manual do usuário detectada (KeyboardInterrupt).")
        print("🛑 Desligando a esteira de forma segura...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro crítico não tratado no fluxo principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
