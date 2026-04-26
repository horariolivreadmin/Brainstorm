import customtkinter as ctk
from tkinter import filedialog
import threading
import json
import os

class AppWindow(ctk.CTk):
    def __init__(self, run_pipeline_callback):
        """
        Inicia a Interface Gráfica.
        :param run_pipeline_callback: Função do backend que será chamada ao clicar no botão INICIAR.
        """
        super().__init__()
        
        self.run_pipeline_callback = run_pipeline_callback
        
        # Caminho absoluto para salvar a config na raiz do projeto (um nível acima da pasta ui/)
        self.arquivo_config = os.path.join(os.path.dirname(__file__), "..", "config.json")

        # ==========================================
        # CONFIGURAÇÕES DA JANELA
        # ==========================================
        self.title("Brainstorm Distiller - Consensus Edition")
        self.geometry("1100x850")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.salvar_e_fechar)

        # ==========================================
        # SIDEBAR
        # ==========================================
        self.sidebar = ctk.CTkFrame(self, width=280)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="Pipeline", font=("Arial", 20, "bold")).pack(pady=20)
        
        self.model_entry = ctk.CTkEntry(self.sidebar)
        self.model_entry.insert(0, "qwen2.5")
        self.model_entry.pack(padx=20, pady=10, fill="x")

        # ==========================================
        # ÁREA PRINCIPAL
        # ==========================================
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(2, weight=1)
        self.main.grid_rowconfigure(4, weight=1)

        self.file_path = ctk.StringVar(value="Selecione o log .md")
        ctk.CTkButton(self.main, text="📂 Selecionar Log", command=self.select_file).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.main, textvariable=self.file_path).grid(row=1, column=0, sticky="w")

        # Prompts
        ctk.CTkLabel(self.main, text="Prompt 1: O Construtor (Geração)", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="sw")
        self.txt_construtor = ctk.CTkTextbox(self.main, height=120)
        self.txt_construtor.grid(row=3, column=0, sticky="ew", pady=(0,10))

        ctk.CTkLabel(self.main, text="Prompt 2: O Auditor (Red Team / Checksum)", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="sw")
        self.txt_auditor = ctk.CTkTextbox(self.main, height=150)
        self.txt_auditor.grid(row=5, column=0, sticky="ew")

        # Terminal
        self.terminal = ctk.CTkTextbox(self.main, height=180, fg_color="#000", text_color="#0f0", font=("Courier", 12))
        self.terminal.grid(row=6, column=0, pady=20, sticky="ew")

        # Botão de Ação
        self.btn_run = ctk.CTkButton(self.main, text="🚀 INICIAR TRIBUNAL DE IA", height=50, command=self.start)
        self.btn_run.grid(row=7, column=0, sticky="ew")

        self.carregar_configuracoes()

    # ==========================================
    # LÓGICA DE INTERFACE
    # ==========================================
    def carregar_configuracoes(self):
        """Carrega os prompts salvos na última sessão do arquivo config.json."""
        if os.path.exists(self.arquivo_config):
            try:
                with open(self.arquivo_config, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    
                self.model_entry.delete(0, "end")
                self.model_entry.insert(0, config.get("modelo", "qwen2.5"))
                self.txt_construtor.insert("0.0", config.get("prompt_construtor", ""))
                self.txt_auditor.insert("0.0", config.get("prompt_auditor", ""))
                return
            except Exception as e:
                self.log(f"[AVISO] Falha ao ler config.json: {e}. Usando padrões.")

        self.txt_construtor.insert("0.0", "Extraia tecnologias, decisões e racionais do turno. Classifique o que é decisão final e o que foi descartado. Retorne APENAS JSON.")
        self.txt_auditor.insert("0.0", "Compare o TEXTO BRUTO com o JSON. Garanta a estrutura rigorosa e corrija omissões do Construtor. Retorne o JSON final validado.")

    def salvar_e_fechar(self):
        """Salva o estado atual antes de destruir a janela."""
        config = {
            "modelo": self.model_entry.get(),
            "prompt_construtor": self.txt_construtor.get("0.0", "end").strip(),
            "prompt_auditor": self.txt_auditor.get("0.0", "end").strip()
        }
        with open(self.arquivo_config, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        self.destroy()

    def select_file(self):
        p = filedialog.askopenfilename(filetypes=[("Markdown", "*.md")])
        if p: self.file_path.set(p)

    def log(self, m):
        """Adiciona mensagens ao terminal da interface."""
        # Garante que as chamadas de log feitas por threads atualizem a UI corretamente
        self.after(0, self._inserir_log, m)

    def _inserir_log(self, m):
        self.terminal.insert("end", f"{m}\n")
        self.terminal.see("end")

    def start(self):
        """Prepara a interface e dispara a thread de processamento."""
        if self.file_path.get() == "Selecione o log .md":
            self.log("[ERRO] Por favor, selecione um arquivo Markdown primeiro.")
            return

        self.btn_run.configure(state="disabled")
        
        # Executa em uma thread separada para não travar a janela
        threading.Thread(target=self._executar_backend, daemon=True).start()

    def _executar_backend(self):
        """Chama a função externa passando os dados coletados da tela."""
        try:
            # Passa a bola para a função fornecida pelo main.py
            self.run_pipeline_callback(
                modelo=self.model_entry.get(),
                prompt_construtor=self.txt_construtor.get("0.0", "end").strip(),
                prompt_auditor=self.txt_auditor.get("0.0", "end").strip(),
                caminho_arquivo=self.file_path.get(),
                logger=self.log # Passamos a função log da UI para que o Backend consiga "falar" com a tela
            )
        except Exception as e:
            self.log(f"[ERRO CRÍTICO] Falha na execução do pipeline: {e}")
        finally:
            # Reativa o botão no final (com after para thread safety no Tkinter)
            self.after(0, lambda: self.btn_run.configure(state="normal"))
