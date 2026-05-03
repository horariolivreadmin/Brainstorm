import concurrent.futures #[cite: 1]
import json
from llm_client import invocar_modelo

def _processar_worker(chave: str, descricao_tarefa: str, conteudo_chunk: str, memoria_xml: str) -> tuple:
    """
    Função auxiliar que executa a chamada isolada para extração de uma chave específica.
    """
    prompt_sistema = (
        f"Atue como um extrator de dados rigoroso. A sua tarefa é: {descricao_tarefa}. "
        f"Responda estritamente em formato JSON contendo apenas a chave '{chave}' e o seu respectivo valor extraído."
    )
    
    prompt_usuario = (
        f"Memória Global XML:\n{memoria_xml}\n\n"
        f"Conteúdo Atual (Chunk):\n{conteudo_chunk}"
    )
    
    # Cada thread chama llm_client.invocar_modelo pedindo apenas aquela chave[cite: 1].
    resposta_str = invocar_modelo(
        modelo="ollama_default", # Placeholder para o modelo configurado
        prompt_sistema=prompt_sistema,
        prompt_usuario=prompt_usuario,
        formato_json=True,
        temperatura=0.0 # Modo determinístico conforme boas práticas da arquitetura
    )
    
    try:
        dados = json.loads(resposta_str)
        # Tenta extrair o valor da chave específica; caso o modelo retorne estruturado de outra forma, armazena o dict inteiro.
        return chave, dados.get(chave, dados)
    except json.JSONDecodeError:
        return chave, resposta_str

def executar_workers_paralelos(conteudo_chunk: str, memoria_xml: str, esquema_dinamico: dict) -> dict:
    """
    Cria uma thread para cada chave no `esquema_dinamico`[cite: 1].
    Cada thread chama `llm_client.invocar_modelo` pedindo apenas aquela chave[cite: 1].
    Retorna o `resultado_workers` unificado[cite: 1].
    """
    # Uma lista contendo apenas os nomes das chaves do esquema_dinamico[cite: 1].
    chaves_alvo = list(esquema_dinamico.keys()) 
    
    # O JSON final consolidado com as respostas de todos os workers[cite: 1].
    resultado_workers = {} 
    
    # Gerencia o pool de threads para rodar os workers paralelos[cite: 1].
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futuros = []
        for chave in chaves_alvo:
            descricao_tarefa = esquema_dinamico[chave]
            futuros.append(
                executor.submit(
                    _processar_worker, 
                    chave, 
                    descricao_tarefa, 
                    conteudo_chunk, 
                    memoria_xml
                )
            )
            
        for futuro in concurrent.futures.as_completed(futuros):
            chave_processada, valor_extraido = futuro.result()
            resultado_workers[chave_processada] = valor_extraido
            
    return resultado_workers
