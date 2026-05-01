import json
from typing import Optional, Dict, Any
import ollama

class OllamaClient:
    """
    Client for local LLM communication using Ollama.
    Este módulo é puramente um "Driver" de comunicação, focado na integração Zero Trust.
    """

    def gerar_extracao_estruturada(
        self,
        model_name: str,
        system_prompt: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
        keep_alive: str = '15m'
    ) -> Optional[Dict[str, Any]]:
        """
        Gera uma extração estruturada de dados usando um modelo local no Ollama.
        
        Args:
            model_name (str): O nome do modelo a ser utilizado (ex: 'llama3').
            system_prompt (str): O prompt de sistema definindo o comportamento.
            user_prompt (str): A entrada principal do usuário/conteúdo bruto.
            json_schema (dict): Schema esperado para forçar o output estruturado.
            keep_alive (str): Tempo para manter o Prefix Cache na VRAM.
            
        Returns:
            dict | None: O dicionário JSON parseado, ou None em caso de falha.
        """
        try:
            response = ollama.chat(
                model=model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                format=json_schema,
                keep_alive=keep_alive
            )
            
            content = response.get('message', {}).get('content', '')
            if not content:
                return None
                
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"[OllamaClient] Falha ao decodificar JSON: {e}")
            return None
        except Exception as e:
            print(f"[OllamaClient] Erro na comunicação com o Ollama: {e}")
            return None
