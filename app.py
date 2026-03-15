import streamlit as st
import random
import base64
from pathlib import Path
import os
from dotenv import load_dotenv

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Sorteador de futebol da pelada do",
    page_icon="⚽",
    layout="wide"
)

# =========================================================
# CONFIGURAÇÕES
# =========================================================
ADMIN_PASSWORD = ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
BACKGROUND_IMAGE = "fundo.jpg"

LIMITE_GOLEIROS = 4
LIMITE_LINHA = 24
TIMES = ["Time A", "Time B", "Time C", "Time D"]

# Validação simples para evitar erro silencioso
if not ADMIN_PASSWORD:
    st.error("A variável ADMIN_PASSWORD não foi encontrada no arquivo .env")
    st.stop()


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================
def carregar_fundo(imagem_path):
    caminho = Path(imagem_path)

    if caminho.exists():
        with open(caminho, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}

            .bloco-card {{
                background: rgba(0, 0, 0, 0.58);
                padding: 18px;
                border-radius: 16px;
                color: white;
                margin-bottom: 12px;
                border: 1px solid rgba(255,255,255,0.10);
            }}

            .titulo-card {{
                margin-top: 0;
                margin-bottom: 10px;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            .stApp {
                background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                background-attachment: fixed;
            }

            .bloco-card {
                background: rgba(0, 0, 0, 0.58);
                padding: 18px;
                border-radius: 16px;
                color: white;
                margin-bottom: 12px;
                border: 1px solid rgba(255,255,255,0.10);
            }

            .titulo-card {
                margin-top: 0;
                margin-bottom: 10px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )


def inicializar_estado():
    if "admin_logado" not in st.session_state:
        st.session_state.admin_logado = False

    if "goleiros" not in st.session_state:
        st.session_state.goleiros = []

    if "linha" not in st.session_state:
        st.session_state.linha = []

    if "times_sorteados" not in st.session_state:
        st.session_state.times_sorteados = None


def resetar_tudo():
    st.session_state.goleiros = []
    st.session_state.linha = []
    st.session_state.times_sorteados = None


def normalizar_nome(nome):
    return " ".join(nome.strip().split())


def nome_ja_existe(nome):
    nome_lower = nome.lower()
    lista_total = st.session_state.goleiros + st.session_state.linha

    for jogador in lista_total:
        if jogador.lower() == nome_lower:
            return True

    return False


def adicionar_jogador(nome, tipo):
    nome = normalizar_nome(nome)

    if not nome:
        return False, "Digite um nome válido."

    if nome_ja_existe(nome):
        return False, "Esse nome já foi cadastrado."

    if tipo == "Goleiro":
        if len(st.session_state.goleiros) >= LIMITE_GOLEIROS:
            return False, "A lista de goleiros já está completa."
        st.session_state.goleiros.append(nome)
        st.session_state.times_sorteados = None
        return True, f"{nome} entrou como goleiro."

    if tipo == "Linha":
        if len(st.session_state.linha) >= LIMITE_LINHA:
            return False, "A lista de jogadores de linha já está completa."
        st.session_state.linha.append(nome)
        st.session_state.times_sorteados = None
        return True, f"{nome} entrou como jogador de linha."

    return False, "Tipo de jogador inválido."


def remover_jogador(nome, tipo):
    if tipo == "Goleiro":
        if nome in st.session_state.goleiros:
            st.session_state.goleiros.remove(nome)
            st.session_state.times_sorteados = None
            return True, f"{nome} foi removido dos goleiros."

    if tipo == "Linha":
        if nome in st.session_state.linha:
            st.session_state.linha.remove(nome)
            st.session_state.times_sorteados = None
            return True, f"{nome} foi removido dos jogadores de linha."

    return False, "Jogador não encontrado."


def sortear_times():
    goleiros = st.session_state.goleiros.copy()
    linha = st.session_state.linha.copy()

    if len(goleiros) != LIMITE_GOLEIROS:
        return None, f"É necessário ter exatamente {LIMITE_GOLEIROS} goleiros para sortear."

    if len(linha) != LIMITE_LINHA:
        return None, f"É necessário ter exatamente {LIMITE_LINHA} jogadores de linha para sortear."

    random.shuffle(goleiros)
    random.shuffle(linha)

    times_sorteados = {}

    for i, time in enumerate(TIMES):
        inicio = i * 6
        fim = inicio + 6

        times_sorteados[time] = {
            "goleiro": goleiros[i],
            "linha": linha[inicio:fim]
        }

    return times_sorteados, None


def exibir_lista_jogadores():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="bloco-card">
                <h3 class="titulo-card">🧤 Goleiros ({len(st.session_state.goleiros)}/{LIMITE_GOLEIROS})</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.goleiros:
            for nome in st.session_state.goleiros:
                st.write(f"- {nome}")
        else:
            st.write("Nenhum goleiro cadastrado.")

    with col2:
        st.markdown(
            f"""
            <div class="bloco-card">
                <h3 class="titulo-card">🏃 Linha ({len(st.session_state.linha)}/{LIMITE_LINHA})</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.linha:
            for nome in st.session_state.linha:
                st.write(f"- {nome}")
        else:
            st.write("Nenhum jogador de linha cadastrado.")


def exibir_time(nome_time, dados):
    lista_linha = "".join([f"<li>{j}</li>" for j in dados["linha"]])

    st.markdown(
        f"""
        <div class="bloco-card">
            <h3 class="titulo-card">⚽ {nome_time}</h3>
            <p><strong>Goleiro:</strong> {dados["goleiro"]}</p>
            <p><strong>Jogadores de linha:</strong></p>
            <ul>
                {lista_linha}
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


def gerar_texto_times():
    if not st.session_state.times_sorteados:
        return ""

    texto = ""

    for nome_time in TIMES:
        dados = st.session_state.times_sorteados[nome_time]
        texto += f"{nome_time}\n"
        texto += f"Goleiro: {dados['goleiro']}\n"
        texto += "Linha:\n"

        for jogador in dados["linha"]:
            texto += f"- {jogador}\n"

        texto += "\n"

    return texto.strip()


# =========================================================
# INÍCIO APP
# =========================================================
carregar_fundo(BACKGROUND_IMAGE)
inicializar_estado()

st.title("⚽ Sorteador de Futebol")
st.caption("Cadastro dos próprios jogadores + sorteio automático de 4 times")

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Goleiros", f"{len(st.session_state.goleiros)}/{LIMITE_GOLEIROS}")
with m2:
    st.metric("Linha", f"{len(st.session_state.linha)}/{LIMITE_LINHA}")
with m3:
    st.metric("Total", len(st.session_state.goleiros) + len(st.session_state.linha))

aba1, aba2, aba3 = st.tabs(["Entrar na lista", "Sorteio", "Admin"])

with aba1:
    st.subheader("Entrar na lista do futebol")

    with st.form("form_jogador"):
        nome = st.text_input("Digite seu nome")
        tipo = st.radio("Escolha sua posição", ["Linha", "Goleiro"], horizontal=True)
        enviar = st.form_submit_button("Entrar na lista")

    if enviar:
        sucesso, mensagem = adicionar_jogador(nome, tipo)
        if sucesso:
            st.success(mensagem)
        else:
            st.error(mensagem)

    st.divider()
    st.subheader("Lista atual")
    exibir_lista_jogadores()

with aba2:
    st.subheader("Sorteio dos times")

    st.info(
        f"Para sortear, é preciso ter exatamente {LIMITE_GOLEIROS} goleiros e {LIMITE_LINHA} jogadores de linha."
    )

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("🎲 Sortear times", use_container_width=True):
            resultado, erro = sortear_times()

            if erro:
                st.error(erro)
            else:
                st.session_state.times_sorteados = resultado
                st.success("Times sorteados com sucesso!")

    with col_btn2:
        if st.button("🔄 Sortear novamente", use_container_width=True):
            resultado, erro = sortear_times()

            if erro:
                st.error(erro)
            else:
                st.session_state.times_sorteados = resultado
                st.success("Novo sorteio realizado!")

    st.divider()

    if st.session_state.times_sorteados:
        c1, c2 = st.columns(2)

        with c1:
            exibir_time("Time A", st.session_state.times_sorteados["Time A"])
            exibir_time("Time B", st.session_state.times_sorteados["Time B"])

        with c2:
            exibir_time("Time C", st.session_state.times_sorteados["Time C"])
            exibir_time("Time D", st.session_state.times_sorteados["Time D"])

        st.text_area(
            "Resultado em texto",
            value=gerar_texto_times(),
            height=300
        )
    else:
        st.warning("Ainda não houve sorteio.")

with aba3:
    st.subheader("Área do administrador")

    if not st.session_state.admin_logado:
        senha = st.text_input("Senha do admin", type="password")
        if st.button("Entrar como admin"):
            if senha == ADMIN_PASSWORD:
                st.session_state.admin_logado = True
                st.success("Login realizado com sucesso.")
                st.rerun()
            else:
                st.error("Senha incorreta.")
    else:
        st.success("Admin logado.")

        st.markdown("### Reset geral")
        if st.button("♻️ Resetar lista completa", use_container_width=True):
            resetar_tudo()
            st.success("Lista resetada com sucesso.")
            st.rerun()

        st.divider()
        st.markdown("### Remover jogador")

        col_r1, col_r2 = st.columns(2)

        with col_r1:
            if st.session_state.goleiros:
                goleiro_remover = st.selectbox(
                    "Remover goleiro",
                    options=[""] + st.session_state.goleiros,
                    key="remover_goleiro"
                )
                if st.button("Remover goleiro", use_container_width=True):
                    if goleiro_remover:
                        sucesso, mensagem = remover_jogador(goleiro_remover, "Goleiro")
                        if sucesso:
                            st.success(mensagem)
                            st.rerun()
                        else:
                            st.error(mensagem)
                    else:
                        st.error("Selecione um goleiro.")
            else:
                st.write("Nenhum goleiro para remover.")

        with col_r2:
            if st.session_state.linha:
                linha_remover = st.selectbox(
                    "Remover jogador de linha",
                    options=[""] + st.session_state.linha,
                    key="remover_linha"
                )
                if st.button("Remover jogador de linha", use_container_width=True):
                    if linha_remover:
                        sucesso, mensagem = remover_jogador(linha_remover, "Linha")
                        if sucesso:
                            st.success(mensagem)
                            st.rerun()
                        else:
                            st.error(mensagem)
                    else:
                        st.error("Selecione um jogador de linha.")
            else:
                st.write("Nenhum jogador de linha para remover.")

        st.divider()
        if st.button("🚪 Sair do admin"):
            st.session_state.admin_logado = False
            st.rerun()