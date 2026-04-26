import json
import subprocess
import time
import urllib.request
import urllib.error
import ollama

class OllamaClient:
    def __init__(self, primary_model="qwen2.5", fallback_model="llama3.2", max_retries=3):
        """
        Inicializa o cliente LLM, garantindo que o servidor local esteja rodando.
        """
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.max_retries = max_retries
        self._ensure_daemon()

    def _ensure_daemon(self):
        """
        Movemos a lógica de 'acordar' o Ollama da Interface (GUI) para cá.
        Faz muito mais sentido que o Cliente de IA gerencie a própria infraestrutura.
        """
        try:
            urllib.request.urlopen("http://localhost:11434", timeout=2)
        except Exception:
            # O servidor está offline. Tenta iniciar silenciosamente.
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(5) # Aguarda o daemon subir

    def _estimate_tokens(self, text):
        """
        Estimativa rudimentar de tokens. 
        Em média, 1 token equivale a ~3.5 ou 4 caracteres.
        Isso serve como uma camada inicial de segurança contra estouro de contexto.
        """
        return int(len(text) / 3.5)

    def request_json(self, system_prompt, user_prompt, schema, callback_log, agent_name="IA"):
        """
        O coração do cliente. Envia o prompt, exige formatação em JSON e
        lida com as retentativas (retries) e fallback de modelos automaticamente.
        
        Retorna:
            (dict_validado, string_bruta) ou (None, None) em caso de falha.
        """
        # 1. Defesa de Contexto
        estimated_tokens = self._estimate_tokens(user_prompt + system_prompt)
        if estimated_tokens > 25000:
            callback_log(f"   [AVISO] Carga muito alta detectada (~{estimated_tokens} tokens). Pode causar alucinações ou lentidão.")

        # 2. Configura a fila de execução (Modelo Principal -> Modelo de Emergência)
        modelos_para_tentar = [self.primary_model]
        if self.fallback_model and self.fallback_model != self.primary_model:
            modelos_para_tentar.append(self.fallback_model)

        # 3. Loop de Tentativas e Fallback
        for modelo in modelos_para_tentar:
            for tentativa in range(self.max_retries):
                try:
                    resposta = ollama.chat(
                        model=modelo,
                        messages=[
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': user_prompt}
                        ],
                        format=schema,
                        options={"temperature": 0.0} # Sempre 0 para garantir previsibilidade lógica
                    )
                    
                    conteudo_bruto = resposta['message']['content']
                    
                    # Validação de integridade do JSON
                    json_validado = json.loads(conteudo_bruto)
                    
                    # Mensagem de sucesso (caso tenha precisado de retry ou fallback)
                    if tentativa > 0 or modelo != self.primary_model:
                        callback_log(f"   [{agent_name}] Sucesso ao gerar JSON com modelo '{modelo}'!")
                    
                    # Retornamos ambos: o JSON limpo (para o Python) e a String (para passar ao Auditor)
                    return json_validado, conteudo_bruto

                except json.JSONDecodeError:
                    callback_log(f"   [AVISO] {agent_name} corrompeu a estrutura (Tentativa {tentativa+1}/{self.max_retries} no modelo {modelo}). Autocorrigindo...")
                    if tentativa == self.max_retries - 1:
                        callback_log(f"   [ALERTA] Esgotadas as tentativas com o modelo '{modelo}'.")
                
                except Exception as e:
                    callback_log(f"   [ERRO DE API] Falha de comunicação usando '{modelo}': {e}")
                    break # Sai do loop de tentativas e vai direto para o modelo de fallback (se houver)

        # 4. Falha Crítica
        callback_log(f"   [FALHA CRÍTICA] {agent_name} falhou em todos os modelos. Pulando este turno.")
        return None, None
