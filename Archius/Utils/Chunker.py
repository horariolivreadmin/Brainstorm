import os
import shutil
import re

def processar_arquivos_entrada(pasta_input: str, pasta_output: str):
    """
    Lê os arquivos markdown de input, divide-os em pedaços determinísticos 
    e salva os chunks na pasta de output para consumo dos agentes.
    """
    print(f"🧹 Limpando diretório de chunks antigo: {pasta_output}")
    if os.path.exists(pasta_output):
        shutil.rmtree(pasta_output)
    os.makedirs(pasta_output, exist_ok=True)
    
    if not os.path.exists(pasta_input):
        print(f"⚠️ Diretório de input '{pasta_input}' não encontrado. Nenhuma ação tomada.")
        return

    arquivos = sorted([f for f in os.listdir(pasta_input) if f.endswith('.md') or f.endswith('.txt')])
    
    if not arquivos:
        print(f"📭 Nenhum arquivo encontrado em '{pasta_input}'.")
        return

    chunk_counter = 1
    
    # Regex lookahead para manter o delimitador na string separada
    padrao_delimitador = r'(?=\*\*(?:Cliente|Usuário|Usuaria|Client)\*\*:|##\s+(?:Cliente|Usuário))'
    
    for filename in arquivos:
        filepath = os.path.join(pasta_input, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            texto = f.read()
            
        # Detectar se há turnos de conversa claros
        if re.search(padrao_delimitador, texto, flags=re.IGNORECASE):
            blocos = re.split(padrao_delimitador, texto, flags=re.IGNORECASE)
            # Filtrar blocos vazios e remover espaços excedentes
            pedacos = [b.strip() for b in blocos if b.strip()]
        else:
            # Corte fallback por quebra de linhas duplas (aprox 2000 palavras)
            paragrafos = texto.split('\n\n')
            pedacos = []
            chunk_atual = []
            palavras_atual = 0
            
            for p in paragrafos:
                contagem_p = len(p.split())
                if palavras_atual + contagem_p > 2000 and chunk_atual:
                    pedacos.append('\n\n'.join(chunk_atual))
                    chunk_atual = [p]
                    palavras_atual = contagem_p
                else:
                    chunk_atual.append(p)
                    palavras_atual += contagem_p
                    
            if chunk_atual:
                pedacos.append('\n\n'.join(chunk_atual))
                
        # Salvar pedaços extraídos sequencialmente
        for pedaco in pedacos:
            if not pedaco.strip():
                continue
                
            nome_chunk = f"chunk_{chunk_counter:03d}.md"
            out_path = os.path.join(pasta_output, nome_chunk)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(pedaco)
                
            chunk_counter += 1

    print(f"✂️ Fatiamento concluído! {chunk_counter - 1} chunks determinísticos gerados.")
