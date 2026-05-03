import json
import os
import xml.etree.ElementTree as ET
import re

def atualizar_memoria_xml(memoria_atual_xml: str, resultado_workers: dict) -> str:
    """
    Faz o merge dos dados recém extraídos (resultado_workers) para dentro da estrutura XML.
    Retorna a nova string XML atualizada.
    """
    # Garante uma raiz padrão caso a memória atual esteja vazia ou corrompida
    if not memoria_atual_xml or memoria_atual_xml.strip() == "":
        memoria_atual_xml = "<projeto></projeto>"
    
    try:
        # Faz o parse da string XML atual para uma árvore de elementos
        root = ET.fromstring(memoria_atual_xml)
    except ET.ParseError:
        # Fallback de segurança para garantir o determinismo em caso de XML malformado
        root = ET.fromstring("<projeto></projeto>")

    # Cria um bloco para a atualização atual (opcional, mas ajuda na organização do estado_global)
    # Aqui, inserimos as novas chaves diretamente na raiz para manter a simplicidade do contrato
    for chave, valor in resultado_workers.items():
        # Sanitiza o nome da tag para garantir que seja um XML válido (remove espaços, etc)
        tag_limpa = re.sub(r'[^a-zA-Z0-9_]', '_', chave)
        
        # Cria o novo nó
        novo_elemento = ET.Element(tag_limpa)
        
        # A atribuição via .text sanitiza automaticamente os caracteres especiais do texto extraído
        if isinstance(valor, str):
            novo_elemento.text = valor
        else:
            # Caso algum worker retorne um dicionário ou lista por engano, converte para string
            novo_elemento.text = json.dumps(valor, ensure_ascii=False)
            
        root.append(novo_elemento)

    # Converte a árvore de volta para string sem a declaração xml (<?xml ...?>) para manter o formato enxuto
    nova_memoria_xml = ET.tostring(root, encoding='unicode', method='xml')
    return nova_memoria_xml


def carregar_checkpoint(caminho_arquivo: str) -> dict:
    """
    Carrega o estado_global salvo em disco. 
    Se o arquivo não existir, retorna a estrutura inicial padrão baseada no contrato.
    """
    estado_padrao = {
        "arquivos_processados": [],
        "memoria_xml": "<projeto></projeto>"
    }

    if not os.path.exists(caminho_arquivo):
        return estado_padrao

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            estado_global = json.load(f)
            
            # Validação mínima de contrato estrutural
            if "arquivos_processados" not in estado_global or "memoria_xml" not in estado_global:
                return estado_padrao
                
            return estado_global
    except (json.JSONDecodeError, IOError):
        return estado_padrao


def salvar_checkpoint(caminho_arquivo: str, estado_global_dict: dict) -> None:
    """
    Salva o estado_global atualizado no disco em formato JSON.
    O dicionário encapsula a lista de arquivos e a string XML.
    """
    # Garante que o diretório base exista antes de tentar salvar
    diretorio = os.path.dirname(caminho_arquivo)
    if diretorio:
        os.makedirs(diretorio, exist_ok=True)

    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        # ensure_ascii=False mantém os caracteres UTF-8 (acentos) nativos no JSON salvo
        json.dump(estado_global_dict, f, ensure_ascii=False, indent=2)
