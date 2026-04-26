import json
import re
import os

class BrainstormDistiller:
    def __init__(self, llm_client):
        """
        Injeção de Dependência: O Engine não se importa se a IA roda via Ollama,
        OpenAI, ou se é um teste mockado. Ele apenas confia que o 'llm_client'
        tem um método 'processar_turno' que retorna um JSON validado.
        """
        self.llm_client = llm_client

    def _fatiar_markdown(self, texto_md):
        """Divide o log da conversa em turnos baseados nas falas do cliente."""
        padrao = re.compile(r'(?=^\s*\*\*Cliente\*\*:\s*)', flags=re.IGNORECASE | re.MULTILINE)
        partes = padrao.split(texto_md)
        return [p.strip() for p in partes if len(p.strip()) > 10]

    def _mesclar_json(self, estado_global, novo_estado):
        """O 'Juiz Implacável': Funde o JSON com Deep Merge e Mutação de Estado (SSOT)."""
        for entidade, dados in novo_estado.get("entidades", {}).items():
            if entidade not in estado_global.get("entidades", {}):
                if "entidades" not in estado_global:
                    estado_global["entidades"] = {}
                estado_global["entidades"][entidade] = dados
            else:
                # 1. Atualiza Status
                if dados.get("status"):
                    estado_global["entidades"][entidade]["status"] = dados["status"]
                
                # 2. Concatena Listas Simples (sem duplicar)
                para_fundir = ["vulnerabilidades", "cross_dependencies"]
                for chave in para_fundir:
                    if dados.get(chave):
                        lista_atual = estado_global["entidades"][entidade].get(chave, [])
                        lista_nova = dados[chave]
                        lista_atual.extend([item for item in lista_nova if item not in lista_atual])
                        estado_global["entidades"][entidade][chave] = lista_atual

                # 3. Adiciona Ideias Descartadas
                if dados.get("ideias_descartadas"):
                    lista_descartadas_atual = estado_global["entidades"][entidade].get("ideias_descartadas", [])
                    novas_descartadas = dados["ideias_descartadas"]
                    
                    nomes_ja_descartados = [obj.get("ideia", "") for obj in lista_descartadas_atual]
                    for nova_obsoleta in novas_descartadas:
                        if nova_obsoleta.get("ideia") not in nomes_ja_descartados:
                            lista_descartadas_atual.append(nova_obsoleta)
                    
                    estado_global["entidades"][entidade]["ideias_descartadas"] = lista_descartadas_atual

                # 4. A MÁGICA DA MUTAÇÃO: Limpeza Cruzada
                if dados.get("decisoes_finais"):
                    lista_finais = estado_global["entidades"][entidade].get("decisoes_finais", [])
                    lista_finais.extend([item for item in dados["decisoes_finais"] if item not in lista_finais])
                    estado_global["entidades"][entidade]["decisoes_finais"] = lista_finais

                # Remove das "decisões finais" qualquer coisa movida para "descartadas"
                if estado_global["entidades"][entidade].get("ideias_descartadas") and estado_global["entidades"][entidade].get("decisoes_finais"):
                    nomes_descartados = [obj.get("ideia", "").lower() for obj in estado_global["entidades"][entidade]["ideias_descartadas"]]
                    
                    estado_global["entidades"][entidade]["decisoes_finais"] = [
                        decisao for decisao in estado_global["entidades"][entidade]["decisoes_finais"]
                        if not any(descartada in decisao.lower() for descartada in nomes_descartados)
                    ]

        return estado_global

    def processar(self, caminho_arquivo, callback_log):
        """Orquestra todo o fluxo de trabalho do arquivo markdown para o JSON."""
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        chunks = self._fatiar_markdown(conteudo)
        callback_log(f"-> {len(chunks)} turnos detectados. Iniciando debate multiagente...")

        estado = {"entidades": {}}

        for i, chunk in enumerate(chunks):
            callback_log(f"\n[VRAM] TURNO {i+1}/{len(chunks)}:")
            
            # Aqui toda a complexidade de try/except, chamadas HTTP pro Ollama
            # e validações de erro foram movidas para o LLMClient!
            validado = self.llm_client.processar_turno(chunk, callback_log)

            if validado and isinstance(validado, dict) and "entidades" in validado:
                estado = self._mesclar_json(estado, validado)
            else:
                callback_log(f"   [AVISO] Turno {i+1} ignorado devido a falhas de extração.")

        # Salva o resultado final
        caminho_saida = caminho_arquivo.replace('.md', '_consolidado.json')
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(estado, f, indent=4, ensure_ascii=False)
        
        return caminho_saida
