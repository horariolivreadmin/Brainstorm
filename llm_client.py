"""
Módulo llm_client.py
Responsável por gerenciar todas as interações com a biblioteca ollama e 
aplicar as regras de inferência do sistema baseadas em contratos rigorosos.
"""

import time
import logging
import re
import ollama

# Configuração básica de log para monitorar o comportamento do cliente
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _limpar_retorno(texto: str) -> str:
    """
    Remove blocos de formatação markdown (ex: ```json ... ```) frequentemente 
    injetados por LLMs, garantindo o retorno de uma string limpa.
    """
    texto = texto.strip()
    # Remove a tag de abertura de blocos de código
    texto = re.sub(r'^```(?:json)?\s*', '', texto, flags=re.IGNORECASE)
    # Remove a tag de fechamento de blocos de código
    texto = re.sub(r'\s*```$', '', texto)
    return texto.strip()

def invocar_modelo(modelo: str, prompt_sistema: str, prompt_usuario: str, formato_json: bool = False, temperatura: float = 0.3) -> str:
    """
    Envia uma requisição para o servidor local do Ollama.
    
    Regra de Ouro do Cliente: Se a temperatura for 0.0 (modo determinístico),
    o cliente NÃO DEVE implementar lógicas de retry (tentativas automáticas).
    Se falhar, deve estourar o erro imediatamente para ser tratado na origem[cite: 1].
    """
    
    # Define o número máximo de tentativas com base na temperatura
    max_tentativas = 1 if temperatura == 0.0 else 3
    atraso_entre_tentativas = 2  # segundos
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            logging.debug(f"Invocando modelo '{modelo}' (Tentativa {tentativa}/{max_tentativas} | Temperatura: {temperatura})")
            
            # Montagem das opções e do formato conforme a biblioteca oficial ollama
            opcoes_modelo = {'temperature': temperatura}
            formato_saida = 'json' if formato_json else ''
            
            resposta = ollama.chat(
                model=modelo,
                messages=[
                    {'role': 'system', 'content': prompt_sistema},
                    {'role': 'user', 'content': prompt_usuario}
                ],
                options=opcoes_modelo,
                format=formato_saida
            )
            
            conteudo_bruto = resposta.get('message', {}).get('content', '')
            
            # Garante o retorno de uma string limpa, especialmente para JSON
            conteudo_limpo = _limpar_retorno(conteudo_bruto)
            
            return conteudo_limpo

        except Exception as e:
            logging.error(f"Erro de conexão/execução no Ollama na tentativa {tentativa}: {str(e)}")
            
            # Se for a última tentativa (ou a única, no caso de temperatura 0.0), repassa o erro
            if tentativa == max_tentativas:
                logging.critical("Falha definitiva. Estourando erro para tratamento na origem.")
                raise RuntimeError(f"Falha ao invocar o modelo '{modelo}' após {max_tentativas} tentativa(s). Erro original: {e}") from e
            
            # Aguarda antes da próxima tentativa (retry)
            logging.warning(f"Aguardando {atraso_entre_tentativas} segundos antes de tentar novamente...")
            time.sleep(atraso_entre_tentativas)
            
    # Fallback de segurança (teoricamente inatingível devido ao raise no bloco except)
    raise RuntimeError("Falha inesperada no ciclo de invocação do modelo.")
