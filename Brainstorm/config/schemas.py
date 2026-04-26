# ==========================================
# CONSTANTES GERAIS
# ==========================================
ARQUIVO_CONFIG = "config.json"
MODELO_PADRAO = "qwen2.5"

# ==========================================
# PROMPTS PADRÃO
# ==========================================
PROMPT_CONSTRUTOR_PADRAO = (
    "Extraia tecnologias, decisões e racionais do turno. "
    "Classifique o que é decisão final e o que foi descartado. Retorne APENAS JSON."
)

PROMPT_AUDITOR_PADRAO = (
    "Compare o TEXTO BRUTO com o JSON. Garanta a estrutura rigorosa e corrija "
    "omissões do Construtor. Retorne o JSON final validado."
)

# ==========================================
# SCHEMA OBRIGATÓRIO (JSON FORMAT)
# ==========================================
SCHEMA_OBRIGATORIO = {
    "type": "object",
    "properties": {
        "entidades": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    # Chain-of-Thought: Força a IA a pensar antes de responder as listas
                    "raciocinio_interno": {
                        "type": "string",
                        "description": "Pense passo a passo sobre o texto fornecido antes de preencher os campos abaixo. Justifique as classificações."
                    },
                    "decisoes_finais": {
                        "type": "array", 
                        "items": {"type": "string"}
                    },
                    "ideias_descartadas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ideia": {
                                    "type": "string", 
                                    "description": "A tecnologia ou configuração descartada."
                                },
                                "motivo_descarte": {
                                    "type": "string", 
                                    "description": "Justificativa técnica do porquê foi abandonada."
                                }
                            },
                            "required": ["ideia", "motivo_descarte"]
                        }
                    },
                    "vulnerabilidades": {
                        "type": "array", 
                        "items": {"type": "string"}
                    },
                    "cross_dependencies": {
                        "type": "array", 
                        "items": {"type": "string"}
                    },
                    "status": {
                        "type": "string"
                    }
                },
                "required": ["raciocinio_interno"] # Torna o pensamento obrigatório
            }
        }
    },
    "required": ["entidades"]
}
