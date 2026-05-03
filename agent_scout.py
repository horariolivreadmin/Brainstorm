import json
from llm_client import invocar_modelo

def gerar_esquema_para_chunk(conteudo_chunk: str, memoria_xml: str) -> dict:
    """
    Recebe o chunk e a memória. Retorna o `esquema_dinamico` (dict).
    """
    
    # System Prompt interno forçando o comportamento do LLM como analisador estrutural
    prompt_sistema = (
        "Você é um analisador estrutural de informações atuando no núcleo de uma arquitetura de IA. "
        "Sua função exclusiva é ler o trecho atual de texto (conteudo_chunk) sob a ótica do "
        "estado global do projeto fornecido (memoria_xml). "
        "Analise quais novos conceitos, decisões ou comandos precisam ser extraídos do texto atual. "
        "Retorne ESTRITAMENTE um objeto JSON onde as chaves são os tópicos a extrair e os valores "
        "são instruções curtas e diretas para os workers que farão a extração posterior. "
        "Exemplo do formato esperado: "
        "{\"comandos_luks\": \"Extraia os comandos de terminal para criptografia\"}"
    )

    # Prompt do usuário injetando as variáveis estritas do contrato
    prompt_usuario = (
        f"<memoria_xml>\n{memoria_xml}\n</memoria_xml>\n\n"
        f"<conteudo_chunk>\n{conteudo_chunk}\n</conteudo_chunk>\n\n"
        "Gere o esquema de extração agora."
    )

    # Invoca a LLM respeitando a assinatura da interface do llm_client
    # Utilizando formato_json=True e baixa temperatura para garantir o contrato de dados
    resposta_bruta = invocar_modelo(
        modelo="llama3",  # O nome do modelo pode ser ajustado conforme a configuração do Ollama
        prompt_sistema=prompt_sistema,
        prompt_usuario=prompt_usuario,
        formato_json=True,
        temperatura=0.1
    )

    # Parse seguro para garantir que a saída obedece ao contrato do esquema_dinamico
    try:
        esquema_dinamico = json.loads(resposta_bruta)
        
        # Validação extra: o contrato exige estritamente um dicionário (dict)
        if isinstance(esquema_dinamico, dict):
            return esquema_dinamico
        else:
            return {}
            
    except (json.JSONDecodeError, TypeError):
        # Se o parse falhar por qualquer motivo (alucinação ou erro de formato), 
        # devolve um dicionário vazio conforme o requisito de robustez.
        return {}
