import os
from typing import Optional
from google.protobuf.json_format import ParseDict, MessageToDict

from Core.Llm_client import OllamaClient
from archius_schema_pb2 import (
    ChunkContexto, ExtracaoFidelidade, RelatorioAuditoria, 
    PropostaRoteamento, EstadoSistema
)

class Agents:
    """
    Agentes determinísticos do pipeline (Actor-Critic Workflow).
    Responsáveis por montar os prompts, chamar o LLM e retornar os objetos Protobuf populados.
    NÃO gerenciam loops de retentativa, que são responsabilidade do Orchestrator.
    """

    def __init__(self, llm_client: OllamaClient, model_name: str = "llama3"):
        self.llm_client = llm_client
        self.model_name = model_name
        self.prompts_dir = "Prompts/"

    def _ler_prompt(self, filename: str) -> str:
        filepath = os.path.join(self.prompts_dir, filename)
        if not os.path.exists(filepath):
            return f"Você é o {filename.replace('.txt', '')}."
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def agente_1_extrator(self, chunk: ChunkContexto, historico_reprovacao: str = "") -> Optional[ExtracaoFidelidade]:
        """Extrai fatos puros do texto (Maker)."""
        schema = {
            "type": "object",
            "properties": {
                "fatos_brutos": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["fatos_brutos"]
        }
        
        sys_prompt = self._ler_prompt("ia1_extrator.txt")
        if historico_reprovacao:
            sys_prompt += f"\n\nATENÇÃO! A TENTATIVA ANTERIOR FOI REPROVADA. MOTIVO:\n{historico_reprovacao}"
            
        user_prompt = f"Texto Bruto:\n{chunk.texto_bruto}"
        
        resultado_dict = self.llm_client.gerar_extracao_estruturada(
            self.model_name, sys_prompt, user_prompt, schema
        )
        if not resultado_dict:
            return None
            
        extracao = ExtracaoFidelidade()
        ParseDict(resultado_dict, extracao, ignore_unknown_fields=True)
        return extracao

    def agente_3_auditor_fidelidade(self, chunk: ChunkContexto, extracao: ExtracaoFidelidade) -> Optional[RelatorioAuditoria]:
        """Audita se os fatos extraídos são fiéis ao texto (Checker)."""
        schema = {
            "type": "object",
            "properties": {
                "aprovado": {"type": "boolean"},
                "motivo_reprovacao": {"type": "string"},
                "dados_faltantes_ou_erros": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["aprovado", "motivo_reprovacao", "dados_faltantes_ou_erros"]
        }
        
        sys_prompt = self._ler_prompt("ia3_auditor_fidelidade.txt")
        user_prompt = f"Texto Bruto Original:\n{chunk.texto_bruto}\n\nFatos Extraídos pelo Agente 1:\n{list(extracao.fatos_brutos)}"
        
        resultado_dict = self.llm_client.gerar_extracao_estruturada(
            self.model_name, sys_prompt, user_prompt, schema
        )
        if not resultado_dict:
            return None
            
        auditoria = RelatorioAuditoria()
        ParseDict(resultado_dict, auditoria, ignore_unknown_fields=True)
        return auditoria

    def agente_2_arquiteto(self, extracao: ExtracaoFidelidade, estado_atual: EstadoSistema) -> Optional[PropostaRoteamento]:
        """Roteia os fatos validados para a estrutura existente ou propõe revogações (Maker)."""
        schema = {
            "type": "object",
            "properties": {
                "patch_insercao": {
                    "type": "object",
                    "properties": {
                        "dominios": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "object",
                                "properties": {
                                    "subdominios": {
                                        "type": "object",
                                        "additionalProperties": {
                                            "type": "object",
                                            "properties": {
                                                "fatos": {
                                                    "type": "array",
                                                    "items": {"type": "string"}
                                                }
                                            },
                                            "required": ["fatos"]
                                        }
                                    }
                                },
                                "required": ["subdominios"]
                            }
                        }
                    },
                    "required": ["dominios"]
                },
                "proposicoes_revogacao": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "decision": {"type": "string"},
                            "reason": {"type": "string"},
                            "revoked_in_chunk": {"type": "string"}
                        },
                        "required": ["decision", "reason", "revoked_in_chunk"]
                    }
                }
            },
            "required": ["patch_insercao", "proposicoes_revogacao"]
        }
        
        sys_prompt = self._ler_prompt("ia2_roteador.txt")
        
        estado_dict = MessageToDict(estado_atual, preserving_proto_field_name=True)
        user_prompt = f"Estado Atual:\n{estado_dict}\n\nNovos Fatos Validados a Inserir:\n{list(extracao.fatos_brutos)}"
        
        resultado_dict = self.llm_client.gerar_extracao_estruturada(
            self.model_name, sys_prompt, user_prompt, schema
        )
        if not resultado_dict:
            return None
            
        proposta = PropostaRoteamento()
        ParseDict(resultado_dict, proposta, ignore_unknown_fields=True)
        return proposta

    def agente_4_auditor_estrutural(self, proposta: PropostaRoteamento, estado_atual: EstadoSistema) -> Optional[RelatorioAuditoria]:
        """Audita se a proposta arquitetural respeita o limite de 2 níveis de aninhamento (Checker)."""
        schema = {
            "type": "object",
            "properties": {
                "aprovado": {"type": "boolean"},
                "motivo_reprovacao": {"type": "string"},
                "dados_faltantes_ou_erros": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["aprovado", "motivo_reprovacao", "dados_faltantes_ou_erros"]
        }
        
        sys_prompt = self._ler_prompt("ia4_auditor_estrutural.txt")
        
        proposta_dict = MessageToDict(proposta, preserving_proto_field_name=True)
        user_prompt = f"Proposta de Roteamento (Patch e Revogações):\n{proposta_dict}"
        
        resultado_dict = self.llm_client.gerar_extracao_estruturada(
            self.model_name, sys_prompt, user_prompt, schema
        )
        if not resultado_dict:
            return None
            
        auditoria = RelatorioAuditoria()
        ParseDict(resultado_dict, auditoria, ignore_unknown_fields=True)
        return auditoria
