# 🏛️ Archius: Destilador de Conhecimento Zero Trust

O **Archius** é uma arquitetura avançada de *pipeline* de dados local focada na extração e destilação de conhecimento técnico a partir de transcrições brutas, documentações cruas e logs textuais de reuniões. 

Construído sob os mais estritos princípios de Engenharia de Software, o sistema emprega uma rede de **Multi-Agentes Determinísticos (Actor-Critic)** alimentada por LLMs locais (via Ollama), e orquestrada por uma infraestrutura **Zero Trust**, garantindo precisão matemática, tipagem forte e a eliminação de alucinações.

---

## 🚀 Diferenciais e Metodologia

A arquitetura do Archius afasta-se de chamadas "mágicas" e super-confiantes de IA em favor de um ecossistema blindado:

1. **Zero Trust (Maker-Checker):** Nenhuma Inteligência Artificial toma decisões finais sozinha. O sistema opera em pares antagonistas. Para cada Agente criador e propositor (*Maker*), existe um Agente auditor implacável (*Checker*) treinado apenas para procurar falhas, omissões e alucinações.
2. **Single Source of Truth (SSOT) & Protobuf:** Todo o transporte de dados, desde a resposta do LLM até a persistência no disco, é regido por schemas estritos e gerados por **Protocol Buffers** (`archius_schema.proto`). Isso garante tipagem estática rigorosa; se a LLM desviar do formato de schema, a execução falha de forma controlada.
3. **Estado Append-Only (Snapshotting):** O estado da árvore de conhecimento nunca é sobrescrito, apenas evoluído. O sistema salva *snapshots* imutáveis (`estado_v1.json`, `estado_v2.json`), e possui mecanismos de *Revogação de Decisões*, mapeando como a arquitetura do seu projeto evoluiu ao longo do tempo.
4. **Separation of Concerns (SoC) em Nível de Prompt:** Para evitar o temido *Context Drift* (onde a IA mistura restrições de domínios diferentes), cada agente tem um arquivo de texto individualizado de "Leis da Robótica" (*System Prompt*). O módulo de rede (`Llm_client`) não sabe nada sobre os Prompts, e o cérebro macro (`Orchestrator`) não executa a sintaxe do modelo, apenas gerencia o fluxo de controle de falhas (Circuit Breakers).

---

## ⚙️ Como a Esteira Funciona: O Fluxo 1-3-2-4

O "Cérebro" do Archius opera quebrando o teto de complexidade da IA por meio de 4 Agentes hiper-focados. Quando o arquivo principal (`Main.py`) é iniciado, o ciclo de vida do seu dado textual bruto é este:

### Fase 1: Ingestão Mecânica (Pré-IA)
- O **`Chunker.py`** lê os seus logs gigantes na pasta `1_input/` e fatias os arquivos em pedaços palatáveis (chunks) usando cortes inteligentes de conversação ou divisões seguras por limite de palavras. Ele previne que a IA sofra apagões por estourar o limite de janela de contexto (*Context Window*).

### Fase 2: O Pipeline Zero Trust (Estágios 1-3-2-4)
O Maestro orquestra a linha de montagem com retentativas limitadas de segurança (*Circuit Breaker de 3 vidas*):
1. 👷‍♂️ **Agente 1 (Extrator - Maker):** Lê o Chunk bruto e "purifica" o texto. Sua única missão é extrair comandos, tecnologias, arquitetura e regras, listando tudo como fatos estáticos. Ele é estritamente **proibido** de estruturar ou tentar categorizar esses dados.
2. 🕵️‍♂️ **Agente 3 (Auditor de Fidelidade - Checker):** Bate de frente com o Agente 1. Ele compara matematicamente os fatos extraídos com o texto original cru. Se o Agente 1 omitiu um endereço IP ou inventou uma biblioteca que não existe no texto base, o Agente 3 devolve um "tapa na mão", reprova o pacote e passa os motivos exatos para forçar a correção.
3. 📐 **Agente 2 (Arquiteto - Maker):** Recebendo apenas fatos purificados e verdadeiros, ele os encaixa na topologia oficial do conhecimento (SSOT). Se um fato novo entrar em contradição com uma decisão antiga do passado, ele tira o fato velho e documenta as motivações na camada de "Decisões Revogadas".
4. 👨‍⚖️ **Agente 4 (Auditor Estrutural - Checker):** Ignora verdades e fatos, focando unicamente no *Compliance*. Se o Agente 2 quebrou a "Regra de Ouro" tentando criar dicionários profundos no Nível 3, ou usando nomenclatura incorreta em português invés de `snake_case`, ele derruba o pacote e impede a escrita no disco.

### Fase 3 e Fase 4: Persistência e Renderização (Pós-IA)
- O **`State_manager.py`** pega o patch validado e comita uma cópia perfeita incremental (Append-Only) no banco de estados (`3_state`).
- O **`Renderer.py`** extrai a mais recente versão aprovada, lida com a formatação e empilha em cabeçalhos bonitos e semânticos no arquivo `Documentacao_Oficial.md` para o seu deleite visual.

---

## 📂 Estrutura de Diretórios e Componentes

O Archius respeita limites severos de diretórios, de modo a prevenir o vazamento de responsabilidades.

```text
Archius/
├── Main.py                  # Botão de ignição do projeto. Inicia e interconecta todas as macro-fases.
├── archius_schema.proto     # "A Constituição": dita fortemente os moldes do JSON que a LLM deve cuspir.
│
├── Core/                    # Camada de Negócios LLM e Orquestração do Estado
│   ├── Llm_client.py        # Driver Zero Trust isolado. Acopla estritamente com a API nativa do Ollama.
│   ├── Agents.py            # Instancia e conecta Prompts aos Outputs estruturados (ParseDict de Protobuf).
│   ├── Orchestrator.py      # O Maestro de Retentativas. Gerencia o fluxo ping-pong (Maker-Checker) com o log de terminal.
│   └── State_manager.py     # O Cofre. Único ser na face da terra com acesso I/O de escrita à pasta de Estados (SSOT).
│
├── Utils/                   # Funções de preparação e conversão (Mecânicas de 0% de Alucinação)
│   ├── Chunker.py           # Prepara a cama para as IAs fatiando os documentos gigantes.
│   └── Renderer.py          # Puxa o JSON purificado e constrói um Documentacao_Oficial.md.
│
├── Prompts/                 # A cabeça da esteira ("Leis da Robótica" para combater o Context Drift)
│   ├── ia1_extrator.txt             # "Purifica a sujeira em fatos."
│   ├── ia3_auditor_fidelidade.txt   # "Reprove se ele inventar fatos falsos."
│   ├── ia2_roteador.txt             # "Acomode os fatos no conhecimento seguindo Nível 1 e Nível 2."
│   └── ia4_auditor_estrutural.txt   # "Reprove se ele não usar snake_case ou quebrar o Nível 2."
│
└── Data/                    # Pipeline de Arquivos do Projeto (Criado de forma automatizada)
    ├── 1_input/             # Onde VOCÊ joga os arquivos brutos, transcrições e descritivos (.md, .txt).
    ├── 2_chunks/            # Trabalhos pendentes para os Agentes lerem.
    ├── 3_state/             # Histórico snapshot imutável do conhecimento corporativo formatado em JSON puro.
    ├── 4_output/            # Seu troféu. Documentação final compilada e limpa.
    └── debug_erros/         # Onde Chunks reprovados após as 3 retentativas vão parar para investigação humana.
```

---

## 🕹️ Como Usar (Guia de Início Rápido)

### 1. Requisitos do Sistema
- **Python 3.10+** instalado.
- Servidor e biblioteca nativa do **Ollama** rodando modelos de IA Locais (`pip install ollama`).
- Compilador oficial **Protobuf** (`protoc`) e pacote Python correspondente (`pip install protobuf`).
- Um LLM decente puxado no seu terminal Ollama (A recomendação para outputs JSON nativos é usar `llama3` ou `llama3.1`).

### 2. Passo a Passo Inicial
A primeira coisa que seu projeto precisa para existir formalmente é que o arquivo Python derivado do `archius_schema.proto` seja gerado.

1. Navegue até a raiz do projeto (onde está o `.proto`) e execute o comando de build:
   ```bash
   protoc -I=. --python_out=. archius_schema.proto
   ```
   *Este comando gerará o arquivo `archius_schema_pb2.py` lido pelo núcleo em todos os scripts do projeto.*

2. Certifique-se de baixar as dependências Python (Ollama Client e Protobuf):
   ```bash
   pip install -r requirements.txt
   ```
   *(Crie um ambiente virtual `.venv` se desejar manter a limpeza estrutural).*

### 3. Rodando a Esteira
1. Rode o orquestrador pela primeira vez apenas para que ele crie toda a arvore do `Data/`.
   ```bash
   python Main.py
   ```
2. Após ele inicializar as pastas, arraste suas atas de reunião, transcrições de Discord, chamados de ticket ou logs técnicos brutais para dentro da pasta `Data/1_input/`.
3. Inicie o destilador no terminal da raiz:
   ```bash
   python Main.py
   ```
4. Sente-se, tome um café, e acompanhe o log de console em tempo real. Você verá explicitamente as inteligências extraindo o texto, se digladiando pelas revisões de qualidade e comitando na master de segurança.
5. Quando o script finalizar `(✅ Fluxo arquitetural concluído...)`, corra na pasta `Data/4_output/` e abra o seu resplandescente arquivo `Documentacao_Oficial.md`.

---
*Archius foi destilado pela mente conjunta entre Engenharia Humana de Sistemas e IAs Generativas, construído não com super-confiança algorítmica, mas sob sólidas arquiteturas de desconfiança e auditoria.*
