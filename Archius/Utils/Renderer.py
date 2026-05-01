import os
import glob
from google.protobuf.json_format import Parse
from archius_schema_pb2 import EstadoSistema

def _snake_to_title(snake_str: str) -> str:
    """Converte padrão snake_case do JSON para Title Case legível."""
    if not snake_str:
        return ""
    return " ".join(word.capitalize() for word in snake_str.split("_"))

def gerar_markdown_final(pasta_estado: str, pasta_output: str):
    """
    Lê o JSON do estado mais recente validado pelo sistema e o converte 
    em um documento Markdown formatado com exatos 2 níveis de aninhamento.
    """
    os.makedirs(pasta_output, exist_ok=True)
    
    arquivos_estado = glob.glob(os.path.join(pasta_estado, "estado_v*.json"))
    if not arquivos_estado:
        print(f"📭 Nenhum arquivo de estado encontrado em '{pasta_estado}'. O pipeline não rodou corretamente?")
        return
        
    def extrair_versao(filepath: str) -> int:
        filename = os.path.basename(filepath)
        try:
            v_str = filename.split('_v')[1].split('.json')[0]
            return int(v_str)
        except (IndexError, ValueError):
            return -1
            
    ultimo_arquivo = max(arquivos_estado, key=extrair_versao)
    
    # Garantia estrita de tipagem (SSOT via Schema)
    estado = EstadoSistema()
    try:
        with open(ultimo_arquivo, 'r', encoding='utf-8') as f:
            json_data = f.read()
        Parse(json_data, estado, ignore_unknown_fields=True)
    except Exception as e:
        print(f"❌ Erro crítico ao carregar a estrutura do Protobuf '{ultimo_arquivo}': {e}")
        return
        
    print(f"📜 Renderizando a documentação Markdown usando '{os.path.basename(ultimo_arquivo)}'...")
    
    linhas_md = [
        "# Documentação Oficial (Single Source of Truth)",
        f"> **Atualizado em:** {estado._meta.updated_at}",
        f"> **Último log processado:** {estado._meta.last_processed_chunk}",
        f"> **Versão interna:** {estado._meta.version}\n",
        "---",
        ""
    ]
    
    # Renderização da topologia de conhecimento (active_topics)
    dominios = estado.active_topics.dominios
    if dominios:
        # Sort keys para manter a renderização determinística e imutável quando possível
        for dominio_key in sorted(dominios.keys()):
            titulo_h1 = _snake_to_title(dominio_key)
            linhas_md.append(f"# {titulo_h1}")
            
            mapa_subdominios = dominios[dominio_key].subdominios
            for subdominio_key in sorted(mapa_subdominios.keys()):
                titulo_h2 = _snake_to_title(subdominio_key)
                linhas_md.append(f"## {titulo_h2}")
                
                fatos = mapa_subdominios[subdominio_key].fatos
                for fato in fatos:
                    linhas_md.append(f"- {fato}")
                linhas_md.append("") # Quebra de linha semântica
                
    # Renderização das Decisões Revogadas no final do documento
    if estado.revoked_decisions:
        linhas_md.append("---")
        linhas_md.append("# 🗑️ Decisões Revogadas e Antigas")
        for decisao in estado.revoked_decisions:
            linhas_md.append(f"- **{decisao.decision}**")
            linhas_md.append(f"  - *Justificativa/Motivo:* {decisao.reason}")
            linhas_md.append(f"  - *Revogado durante leitura de:* {decisao.revoked_in_chunk}")
            
    # Commit para o disco
    filepath_saida = os.path.join(pasta_output, "Documentacao_Oficial.md")
    with open(filepath_saida, 'w', encoding='utf-8') as f:
        f.write("\n".join(linhas_md))
        
    print(f"✅ Renderização impecável. Arquivo salvo em: {filepath_saida}")
