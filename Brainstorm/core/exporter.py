import json
from datetime import datetime

class ADRExporter:
    """
    Responsável por converter o estado global consolidado (JSON)
    em relatórios legíveis para humanos (Markdown, etc.).
    """
    
    @staticmethod
    def exportar_para_markdown(estado_global: dict, caminho_saida: str = None) -> str:
        """
        Gera um documento Markdown estruturado a partir do JSON de entidades.
        Se caminho_saida for fornecido, salva o arquivo no disco.
        """
        linhas = []
        
        # Cabeçalho do Documento
        linhas.append("# 🏗️ Architecture Decision Record (ADR)")
        data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
        linhas.append(f"**Documento gerado automaticamente em:** {data_atual}")
        linhas.append("\n---\n")
        
        entidades = estado_global.get("entidades", {})
        
        if not entidades:
            linhas.append("> **Aviso:** Nenhuma entidade ou decisão foi encontrada no arquivo processado.")
            return "\n".join(linhas)
            
        # Itera sobre cada entidade mapeada pela IA
        for nome_entidade, dados in entidades.items():
            # Título da Entidade
            linhas.append(f"## 🔹 {nome_entidade.upper()}")
            
            # Status
            status = dados.get("status", "Não definido")
            linhas.append(f"**Status Atual:** `{status}`\n")
            
            # 1. Decisões Finais
            decisoes = dados.get("decisoes_finais", [])
            if decisoes:
                linhas.append("### ✅ Decisões Finais (Arquitetura Aprovada)")
                for decisao in decisoes:
                    linhas.append(f"- {decisao}")
                linhas.append("")
                
            # 2. Ideias Descartadas (Racional)
            descartadas = dados.get("ideias_descartadas", [])
            if descartadas:
                linhas.append("### ❌ Ideias Descartadas (Racional de Rejeição)")
                for item in descartadas:
                    ideia = item.get("ideia", "Desconhecida")
                    motivo = item.get("motivo_descarte", "Sem justificativa")
                    linhas.append(f"- **{ideia}:** {motivo}")
                linhas.append("")
                
            # 3. Vulnerabilidades
            vulns = dados.get("vulnerabilidades", [])
            if vulns:
                linhas.append("### ⚠️ Vulnerabilidades / Pontos de Atenção")
                for v in vulns:
                    linhas.append(f"- {v}")
                linhas.append("")
                
            # 4. Dependências
            deps = dados.get("cross_dependencies", [])
            if deps:
                linhas.append("### 🔗 Dependências Cruzadas")
                for dep in deps:
                    linhas.append(f"- {dep}")
                linhas.append("")
                
            # Separador visual entre entidades
            linhas.append("---\n")
            
        markdown_final = "\n".join(linhas)
        
        # Salva em disco se o caminho foi solicitado
        if caminho_saida:
            try:
                with open(caminho_saida, 'w', encoding='utf-8') as f:
                    f.write(markdown_final)
            except Exception as e:
                print(f"[ERRO] Falha ao salvar o arquivo Markdown: {e}")
                
        return markdown_final
