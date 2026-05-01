import os
import glob
from datetime import datetime
from google.protobuf.json_format import MessageToJson, Parse
# Assume-se que o protobuf foi compilado para archius_schema_pb2
from archius_schema_pb2 import EstadoSistema, TopicosAtivos, PropostaRoteamento

class StateManager:
    """
    Gerenciador de Estado do Sistema (SSOT - Single Source of Truth).
    Este é o ÚNICO arquivo com permissão para ler e escrever os arquivos JSON de estado no disco.
    """

    def __init__(self, state_dir: str = "Data/3_state/"):
        self.state_dir = state_dir
        os.makedirs(self.state_dir, exist_ok=True)

    def carregar_ultimo_estado(self) -> EstadoSistema:
        """
        Lê a pasta de estado e retorna a versão mais alta.
        Retorna um EstadoSistema vazio (version=0) se não houver estado anterior.
        """
        estado = EstadoSistema()
        estado._meta.version = 0

        arquivos_estado = glob.glob(os.path.join(self.state_dir, "estado_v*.json"))
        if not arquivos_estado:
            return estado

        def extrair_versao(filepath: str) -> int:
            filename = os.path.basename(filepath)
            try:
                # Extrai o número 'N' de 'estado_vN.json'
                v_str = filename.split('_v')[1].split('.json')[0]
                return int(v_str)
            except (IndexError, ValueError):
                return -1
                
        ultimo_arquivo = max(arquivos_estado, key=extrair_versao)
        
        try:
            with open(ultimo_arquivo, 'r', encoding='utf-8') as f:
                json_data = f.read()
            Parse(json_data, estado, ignore_unknown_fields=True)
        except Exception as e:
            print(f"[StateManager] Erro ao carregar o estado {ultimo_arquivo}: {e}")
            
        return estado

    def salvar_novo_estado(self, proposta_roteamento: PropostaRoteamento, chunk_name: str):
        """
        Gera um novo snapshot (append-only) do estado com a proposta de roteamento aplicada.
        """
        estado = self.carregar_ultimo_estado()
        
        # Incrementar metadados
        nova_versao = estado._meta.version + 1
        estado._meta.version = nova_versao
        estado._meta.last_processed_chunk = chunk_name
        estado._meta.updated_at = datetime.utcnow().isoformat() + "Z"
        
        # Merge de proposições de revogação
        if proposta_roteamento.proposicoes_revogacao:
            estado.revoked_decisions.extend(proposta_roteamento.proposicoes_revogacao)
            
        # Merge seguro de patch de inserção (TopicosAtivos)
        for dominio_key, mapa_subdominios in proposta_roteamento.patch_insercao.dominios.items():
            if dominio_key not in estado.active_topics.dominios:
                estado.active_topics.dominios[dominio_key].CopyFrom(mapa_subdominios)
            else:
                for subdominio_key, subdominio in mapa_subdominios.subdominios.items():
                    if subdominio_key not in estado.active_topics.dominios[dominio_key].subdominios:
                        estado.active_topics.dominios[dominio_key].subdominios[subdominio_key].CopyFrom(subdominio)
                    else:
                        estado.active_topics.dominios[dominio_key].subdominios[subdominio_key].fatos.extend(subdominio.fatos)
                        
        # Converter para JSON forçando snake_case para exportação nativa do protobuf
        json_out = MessageToJson(estado, preserving_proto_field_name=True, indent=2)
        
        novo_arquivo = os.path.join(self.state_dir, f"estado_v{nova_versao}.json")
        with open(novo_arquivo, 'w', encoding='utf-8') as f:
            f.write(json_out)
            
        print(f"✅ [StateManager] Novo estado salvo: {novo_arquivo}")
