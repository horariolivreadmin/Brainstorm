import os
import glob

# 1. Importações estritas conforme a Arquitetura de Arquivos (SoC)[cite: 1]
import agent_scout
import agent_swarm
import memory_manager

def executar_esteira_dinamica():
    """
    Função principal do maestro. Lê arquivos, chama os agentes e controla o fluxo.[cite: 1]
    Mantém o controle estrito de logs no terminal.
    """
    print("[ORCHESTRATOR] Iniciando Esteira Dinâmica...")
    pasta_blocos = "blocos_conversa"
    
    if not os.path.exists(pasta_blocos):
        print(f"[ORCHESTRATOR] ERRO: Diretório '{pasta_blocos}' não encontrado. Encerrando.")
        return

    print("[ORCHESTRATOR] Carregando estado global do checkpoint...")
    # Assume-se que o memory_manager possui estas funções auxiliares de I/O para o checkpoint.
    # O estado_global contém as chaves 'arquivos_processados' e 'memoria_xml'[cite: 1]
    estado_global = memory_manager.carregar_estado_global() 
    
    arquivos_processados = estado_global.get("arquivos_processados", [])
    memoria_xml = estado_global.get("memoria_xml", "<projeto></projeto>")

    arquivos_md = sorted(glob.glob(os.path.join(pasta_blocos, "*.md")))
    arquivos_pendentes = [f for f in arquivos_md if os.path.basename(f) not in arquivos_processados]
    
    print(f"[ORCHESTRATOR] Encontrados {len(arquivos_md)} arquivos (.md). {len(arquivos_pendentes)} pendentes.")

    for caminho_arquivo in arquivos_pendentes:
        nome_arquivo = os.path.basename(caminho_arquivo)
        
        print(f"\n{'-'*60}")
        print(f"[ORCHESTRATOR] >> PROCESSANDO: {nome_arquivo}")
        
        # Leitura do texto bruto do pedaço da conversa[cite: 1]
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo_chunk = f.read()
            
        print(f"[ORCHESTRATOR] Tamanho do conteudo_chunk: {len(conteudo_chunk)} caracteres.")
        
        # ---------------------------------------------------------
        # ETAPA 1: SCOUT (Geração de Esquema Dinâmico)
        # ---------------------------------------------------------
        print("[ORCHESTRATOR] Invocando agent_scout...")
        # Assinatura estrita: gerar_esquema_para_chunk(conteudo_chunk, memoria_xml) -> dict[cite: 1]
        esquema_dinamico = agent_scout.gerar_esquema_para_chunk(conteudo_chunk, memoria_xml)
        
        if not esquema_dinamico:
            print("[ORCHESTRATOR] INFO: Scout retornou esquema_dinamico vazio. Nenhum dado a extrair.")
            _salvar_checkpoint_e_avancar(nome_arquivo, arquivos_processados, memoria_xml)
            continue
            
        # Lista contendo apenas os nomes das chaves[cite: 1]
        chaves_alvo = list(esquema_dinamico.keys()) 
        print(f"[ORCHESTRATOR] Scout gerou esquema com {len(chaves_alvo)} chaves_alvo: {chaves_alvo}")
        
        # ---------------------------------------------------------
        # ETAPA 2: SWARM (Execução Paralela)
        # ---------------------------------------------------------
        print("[ORCHESTRATOR] Invocando agent_swarm para pool de threads...")
        # Assinatura estrita: executar_workers_paralelos(conteudo_chunk, memoria_xml, esquema_dinamico) -> dict[cite: 1]
        resultado_workers = agent_swarm.executar_workers_paralelos(conteudo_chunk, memoria_xml, esquema_dinamico)
        
        if not resultado_workers:
            print("[ORCHESTRATOR] ERRO: Swarm falhou ou retornou resultado_workers vazio. Abortando arquivo.")
            continue
            
        print(f"[ORCHESTRATOR] Swarm finalizado com sucesso.")
        
        # ---------------------------------------------------------
        # ETAPA 3: MEMORY MANAGER (Atualização do XML)
        # ---------------------------------------------------------
        print("[ORCHESTRATOR] Invocando memory_manager para merge XML...")
        # Assinatura estrita: atualizar_memoria_xml(memoria_atual_xml, resultado_workers) -> str[cite: 1]
        memoria_xml = memory_manager.atualizar_memoria_xml(memoria_xml, resultado_workers)
        
        # ---------------------------------------------------------
        # ETAPA 4: CHECKPOINT
        # ---------------------------------------------------------
        _salvar_checkpoint_e_avancar(nome_arquivo, arquivos_processados, memoria_xml)
        print(f"[ORCHESTRATOR] << CONCLUÍDO: {nome_arquivo}")

    print(f"\n{'-'*60}")
    print("[ORCHESTRATOR] Esteira Dinâmica executada com sucesso. Todos os chunks processados.")

def _salvar_checkpoint_e_avancar(nome_arquivo: str, arquivos_processados: list, memoria_xml: str):
    """
    Função auxiliar interna para atualizar o controle e persistir o estado global[cite: 1].
    """
    arquivos_processados.append(nome_arquivo)
    estado_global_atualizado = {
        "arquivos_processados": arquivos_processados,
        "memoria_xml": memoria_xml
    }
    print("[ORCHESTRATOR] Salvando estado_global no disco...")
    memory_manager.salvar_checkpoint(estado_global_atualizado)

if __name__ == "__main__":
    executar_esteira_dinamica()
