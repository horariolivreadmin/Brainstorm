import os
import shutil
from typing import Optional

from Core.Llm_client import OllamaClient
from Core.State_manager import StateManager
from Core.Agents import Agents
from archius_schema_pb2 import ChunkContexto

class PipelineOrchestrator:
    """
    Maestro do pipeline de dados Zero Trust.
    Orquestra o fluxo '1-3-2-4' delegando tarefas para Agentes e State Manager.
    NÃO executa LLMs diretamente e NÃO escreve em arquivos de estado diretamente.
    """

    def __init__(self, model_name: str = "llama3"):
        self.chunks_dir = "Data/2_chunks/"
        self.erros_dir = "Data/debug_erros/"
        
        os.makedirs(self.chunks_dir, exist_ok=True)
        os.makedirs(self.erros_dir, exist_ok=True)

        self.llm_client = OllamaClient()
        self.state_manager = StateManager()
        self.agents = Agents(llm_client=self.llm_client, model_name=model_name)

    def executar_pipeline(self):
        """Inicia a varredura da pasta de chunks e processa cada um com Circuit Breaker."""
        print("🚀 Iniciando Pipeline Zero Trust (Fluxo 1-3-2-4)...")
        
        arquivos_chunks = sorted([f for f in os.listdir(self.chunks_dir) if f.endswith('.md')])
        if not arquivos_chunks:
            print("📭 Nenhum chunk encontrado para processar na pasta Data/2_chunks/.")
            return

        for idx, filename in enumerate(arquivos_chunks, start=1):
            filepath = os.path.join(self.chunks_dir, filename)
            print(f"\n📄 Processando Chunk {idx}/{len(arquivos_chunks)}: {filename}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                texto_bruto = f.read()
                
            chunk_contexto = ChunkContexto(
                arquivo_origem=filename,
                texto_bruto=texto_bruto,
                index_sequencia=idx
            )
            
            # ===== ESTÁGIO 1: Extração e Auditoria de Fidelidade =====
            extracao_aprovada = None
            motivo_reprovacao = ""
            
            print("  ↳ 🛡️  Iniciando Estágio 1 (Circuit Breaker: 3 tentativas)")
            for tentativa in range(1, 4):
                print(f"    ↳ 🔄 Tentativa {tentativa}/3: Agente 1 (Extrator)...")
                extracao = self.agents.agente_1_extrator(chunk_contexto, motivo_reprovacao)
                
                if not extracao:
                    print("    ↳ ❌ Agente 1 falhou ao gerar um output estruturado válido.")
                    motivo_reprovacao = "Falha de comunicação ou estruturação JSON na extração."
                    continue
                    
                print(f"    ↳ 🔄 Tentativa {tentativa}/3: Agente 3 (Auditor de Fidelidade)...")
                auditoria1 = self.agents.agente_3_auditor_fidelidade(chunk_contexto, extracao)
                
                if not auditoria1:
                    print("    ↳ ❌ Agente 3 falhou ao gerar um output estruturado válido.")
                    motivo_reprovacao = "Falha de comunicação ou estruturação JSON na auditoria de fidelidade."
                    continue
                    
                if auditoria1.aprovado:
                    print("    ↳ ✅ Estágio 1 Aprovado com Sucesso!")
                    extracao_aprovada = extracao
                    break
                else:
                    print(f"    ↳ ⚠️  Reprovado pelo Auditor 3: {auditoria1.motivo_reprovacao}")
                    motivo_reprovacao = auditoria1.motivo_reprovacao
                    
            if not extracao_aprovada:
                print(f"  ↳ ❌ Chunk {filename} falhou 3 vezes no Estágio 1. Movendo para debug_erros/.")
                self._mover_para_erros(filepath, filename)
                continue
                
            # ===== ESTÁGIO 2: Arquitetura e Auditoria Estrutural =====
            estado_atual = self.state_manager.carregar_ultimo_estado()
            proposta_aprovada = None
            
            print("  ↳ 🏗️  Iniciando Estágio 2 (Circuit Breaker: 3 tentativas)")
            for tentativa in range(1, 4):
                print(f"    ↳ 🔄 Tentativa {tentativa}/3: Agente 2 (Arquiteto)...")
                proposta = self.agents.agente_2_arquiteto(extracao_aprovada, estado_atual)
                
                if not proposta:
                    print("    ↳ ❌ Agente 2 falhou ao gerar um output estruturado válido.")
                    continue
                    
                print(f"    ↳ 🔄 Tentativa {tentativa}/3: Agente 4 (Auditor Estrutural)...")
                auditoria2 = self.agents.agente_4_auditor_estrutural(proposta, estado_atual)
                
                if not auditoria2:
                    print("    ↳ ❌ Agente 4 falhou ao gerar um output estruturado válido.")
                    continue
                    
                if auditoria2.aprovado:
                    print("    ↳ ✅ Estágio 2 Aprovado com Sucesso!")
                    proposta_aprovada = proposta
                    break
                else:
                    print(f"    ↳ ⚠️  Reprovado pelo Auditor 4: {auditoria2.motivo_reprovacao}")
                    
            if not proposta_aprovada:
                print(f"  ↳ ❌ Chunk {filename} falhou 3 vezes no Estágio 2. Movendo para debug_erros/.")
                self._mover_para_erros(filepath, filename)
                continue
                
            # ===== FINALIZAÇÃO: Salvar Estado =====
            print("  ↳ 💾 Delegando salvamento do estado ao StateManager...")
            self.state_manager.salvar_novo_estado(proposta_aprovada, filename)
            print(f"  ↳ 🎉 Chunk '{filename}' integrado ao SSOT com sucesso!")
            
        print("\n🏁 Pipeline Zero Trust finalizada.")

    def _mover_para_erros(self, filepath: str, filename: str):
        """Move o arquivo problemático para a pasta de debug."""
        destino = os.path.join(self.erros_dir, filename)
        shutil.move(filepath, destino)
