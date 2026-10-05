import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Simulador de Integridade de Votação",
    page_icon="🗳️",
    layout="wide"
)

CANDIDATOS = [
    "Candidato Alfa",
    "Candidato Beta",
    "Candidato Gama",
    "Candidato Delta",
]

# ID da planilha informado pelo usuário
SPREADSHEET_ID = "1t9oa9a5rUvDlkEudLdoJrdQQUA13PxV7Vp17VX0oSzY"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ============================================================
# CONEXÃO COM GOOGLE SHEETS
# ============================================================

@st.cache_resource
def conectar_google_sheets():
    """
    Conecta ao Google Sheets usando as credenciais salvas
    nos Secrets do Streamlit Cloud.
    """
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES
        )

        cliente = gspread.authorize(credentials)
        planilha = cliente.open_by_key(SPREADSHEET_ID)

        return planilha

    except Exception as erro:
        st.error(
            "Não foi possível conectar ao Google Sheets. "
            "Verifique os Secrets do Streamlit e o compartilhamento "
            "da planilha com a conta de serviço."
        )
        st.exception(erro)
        st.stop()


@st.cache_resource
def obter_abas():
    planilha = conectar_google_sheets()

    nomes = [aba.title for aba in planilha.worksheets()]

    if "Votos" not in nomes:
        aba_votos = planilha.add_worksheet(
            title="Votos",
            rows=1000,
            cols=6
        )
        aba_votos.append_row(
            ["ID", "Data/Hora", "Sistema", "Candidato", "Status", "Sessão"]
        )
    else:
        aba_votos = planilha.worksheet("Votos")

    if "Configuracao" not in nomes:
        aba_config = planilha.add_worksheet(
            title="Configuracao",
            rows=20,
            cols=2
        )
        aba_config.update(
            "A1:B4",
            [
                ["Parametro", "Valor"],
                ["Candidato favorecido", "Candidato Alfa"],
                ["Percentual", "35"],
                ["Ultima atualização", ""],
            ]
        )
    else:
        aba_config = planilha.worksheet("Configuracao")

    if "Resumo" not in nomes:
        aba_resumo = planilha.add_worksheet(
            title="Resumo",
            rows=20,
            cols=4
        )
        aba_resumo.update(
            "A1:D2",
            [
                ["Sistema", "Candidato", "Votos", "Atualizado em"],
                ["A", "", 0, ""],
            ]
        )
    else:
        aba_resumo = planilha.worksheet("Resumo")

    return aba_votos, aba_config, aba_resumo


# ============================================================
# LEITURA DOS DADOS
# ============================================================

def carregar_votos():
    aba_votos, _, _ = obter_abas()

    registros = aba_votos.get_all_records()

    votos_a = {candidato: 0 for candidato in CANDIDATOS}
    votos_b = {candidato: 0 for candidato in CANDIDATOS}
    historico = []

    for registro in registros:
        sistema = str(registro.get("Sistema", "")).strip()
        candidato = str(registro.get("Candidato", "")).strip()
        status = str(registro.get("Status", "")).strip()

        if status != "Confirmado":
            continue

        if candidato not in CANDIDATOS:
            continue

        if sistema == "A":
            votos_a[candidato] += 1
        elif sistema == "B":
            votos_b[candidato] += 1

        historico.append(
            {
                "ID": registro.get("ID", ""),
                "Data/Hora": registro.get("Data/Hora", ""),
                "Sistema": sistema,
                "Candidato": candidato,
                "Status": status,
            }
        )

    return votos_a, votos_b, historico


def carregar_configuracao():
    _, aba_config, _ = obter_abas()

    registros = aba_config.get_all_records()

    configuracao = {
        "candidato": "Candidato Alfa",
        "percentual": 35,
    }

    for registro in registros:
        parametro = str(registro.get("Parametro", "")).strip()
        valor = registro.get("Valor", "")

        if parametro == "Candidato favorecido" and valor in CANDIDATOS:
            configuracao["candidato"] = valor

        elif parametro == "Percentual":
            try:
                configuracao["percentual"] = int(float(valor))
            except (TypeError, ValueError):
                pass

    return configuracao


# ============================================================
# GRAVAÇÃO
# ============================================================

def proximo_id(aba_votos):
    valores = aba_votos.col_values(1)

    ids = []

    for valor in valores[1:]:
        try:
            ids.append(int(valor))
        except (TypeError, ValueError):
            continue

    return max(ids, default=0) + 1


def salvar_voto(sistema, candidato):
    aba_votos, _, _ = obter_abas()

    novo_id = proximo_id(aba_votos)

    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    aba_votos.append_row(
        [
            novo_id,
            data_hora,
            sistema,
            candidato,
            "Confirmado",
            st.session_state.get("session_id", ""),
        ],
        value_input_option="USER_ENTERED"
    )


def salvar_configuracao(candidato, percentual):
    _, aba_config, _ = obter_abas()

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    aba_config.update(
        "A1:B4",
        [
            ["Parametro", "Valor"],
            ["Candidato favorecido", candidato],
            ["Percentual", percentual],
            ["Ultima atualização", agora],
        ]
    )


def atualizar_resumo(votos_a, votos_b):
    _, _, aba_resumo = obter_abas()

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    linhas = [
        ["Sistema", "Candidato", "Votos", "Atualizado em"]
    ]

    for candidato in CANDIDATOS:
        linhas.append(
            ["A", candidato, votos_a[candidato], agora]
        )

    for candidato in CANDIDATOS:
        linhas.append(
            ["B", candidato, votos_b[candidato], agora]
        )

    aba_resumo.clear()
    aba_resumo.update(
        f"A1:D{len(linhas)}",
        linhas
    )


# ============================================================
# REINICIALIZAÇÃO
# ============================================================

def reiniciar_votacao():
    aba_votos, _, aba_resumo = obter_abas()

    # Mantém o cabeçalho e remove apenas os registros de votos.
    aba_votos.batch_clear(["A2:F"])

    aba_resumo.clear()
    aba_resumo.update(
        "A1:D1",
        [["Sistema", "Candidato", "Votos", "Atualizado em"]]
    )


# ============================================================
# ESTADO INICIAL
# ============================================================

if "dados_carregados" not in st.session_state:
    votos_a, votos_b, historico = carregar_votos()
    configuracao = carregar_configuracao()

    st.session_state.votos_a = votos_a
    st.session_state.votos_b = votos_b
    st.session_state.historico = historico

    st.session_state.voto_pendente_a = None
    st.session_state.voto_pendente_b = None

    st.session_state.candidato_configurado = configuracao["candidato"]
    st.session_state.percentual_configurado = configuracao["percentual"]

    st.session_state.session_id = (
        datetime.now().strftime("%Y%m%d%H%M%S%f")
    )

    st.session_state.dados_carregados = True


# ============================================================
# FUNÇÕES DO SIMULADOR
# ============================================================

def registrar_voto(sistema, candidato):
    if sistema == "A":
        st.session_state.voto_pendente_a = candidato
    else:
        st.session_state.voto_pendente_b = candidato


def confirmar_voto(sistema):
    if sistema == "A":
        candidato = st.session_state.voto_pendente_a

        if candidato:
            st.session_state.votos_a[candidato] = (
                st.session_state.votos_a.get(candidato, 0) + 1
            )

            st.session_state.historico.append(
                {
                    "Sistema": "A",
                    "Candidato": candidato,
                    "Status": "Confirmado",
                }
            )

            salvar_voto("A", candidato)
            atualizar_resumo(
                st.session_state.votos_a,
                st.session_state.votos_b
            )

            st.session_state.voto_pendente_a = None
            return True

    if sistema == "B":
        candidato = st.session_state.voto_pendente_b

        if candidato:
            st.session_state.votos_b[candidato] = (
                st.session_state.votos_b.get(candidato, 0) + 1
            )

            st.session_state.historico.append(
                {
                    "Sistema": "B",
                    "Candidato": candidato,
                    "Status": "Confirmado",
                }
            )

            salvar_voto("B", candidato)
            atualizar_resumo(
                st.session_state.votos_a,
                st.session_state.votos_b
            )

            st.session_state.voto_pendente_b = None
            return True

    return False


def resultado_integro(votos):
    return {candidato: votos.get(candidato, 0) for candidato in CANDIDATOS}


def resultado_manipulado(votos, favorecido, percentual_transferencia):
    """
    Simulação educacional explícita.

    Até 9 votos no Sistema A, o resultado apresentado é igual
    ao registro original.

    A partir de 10 votos, uma fração dos votos dos demais
    candidatos é transferida apenas para o resultado apresentado.

    O registro original permanece intacto no Google Sheets.
    """

    original = resultado_integro(votos)

    total_votos = sum(original.values())

    if total_votos < 10:
        return original

    if percentual_transferencia <= 0:
        return original

    total_outros = sum(
        quantidade
        for candidato, quantidade in original.items()
        if candidato != favorecido
    )

    if total_outros <= 0:
        return original

    transferencia = int(
        total_outros * percentual_transferencia / 100
    )

    if transferencia <= 0:
        return original

    resultado = original.copy()

    resultado[favorecido] += transferencia

    restante = transferencia

    outros = [
        candidato
        for candidato in CANDIDATOS
        if candidato != favorecido
        and resultado[candidato] > 0
    ]

    for candidato in outros:
        if restante <= 0:
            break

        retirada = min(
            resultado[candidato],
            max(
                1,
                round(
                    transferencia
                    * original[candidato]
                    / max(total_outros, 1)
                )
            )
        )

        retirada = min(retirada, restante)
        resultado[candidato] -= retirada
        restante -= retirada

    if restante > 0:
        for candidato in outros:
            if restante <= 0:
                break

            retirada = min(
                resultado[candidato],
                restante
            )

            resultado[candidato] -= retirada
            restante -= retirada

    return resultado


def tabela_resultado(votos):
    total = sum(votos.values())

    dados = []

    for candidato in CANDIDATOS:
        quantidade = votos.get(candidato, 0)

        percentual_resultado = (
            quantidade / total * 100
            if total
            else 0
        )

        dados.append(
            {
                "Candidato": candidato,
                "Votos": quantidade,
                "%": round(percentual_resultado, 1),
            }
        )

    return pd.DataFrame(dados)


# ============================================================
# INTERFACE
# ============================================================

st.markdown(
    """
    <style>
    .titulo {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitulo {
        color: #666;
        margin-bottom: 1.2rem;
    }

    .caixa-alerta {
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0a800;
        background-color: #fff8e1;
        margin-bottom: 1rem;
    }

    .caixa-ok {
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #198754;
        background-color: #eaf7ee;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="titulo">🗳️ Simulador de Integridade de Votação</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Demonstração educacional de como a integridade de um sistema pode ser comprometida.'
    '</div>',
    unsafe_allow_html=True
)

st.warning(
    "DEMONSTRAÇÃO EDUCACIONAL: todos os candidatos e votos são fictícios. "
    "O Sistema A contém uma alteração proposital para demonstrar uma falha "
    "de integridade. O registro original permanece armazenado na planilha."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("Configuração da demonstração")

    indice_candidato = CANDIDATOS.index(
        st.session_state.candidato_configurado
    )

    candidato_preferido = st.selectbox(
        "Candidato favorecido no sistema manipulado",
        CANDIDATOS,
        index=indice_candidato
    )

    percentual = st.slider(
        "Percentual artificial transferido",
        min_value=0,
        max_value=80,
        value=int(st.session_state.percentual_configurado),
        step=5,
        format="%d%%"
    )

    if (
        candidato_preferido != st.session_state.candidato_configurado
        or percentual != st.session_state.percentual_configurado
    ):
        st.session_state.candidato_configurado = candidato_preferido
        st.session_state.percentual_configurado = percentual

        salvar_configuracao(
            candidato_preferido,
            percentual
        )

    st.divider()

    total_a = sum(st.session_state.votos_a.values())
    total_b = sum(st.session_state.votos_b.values())
    total_geral = total_a + total_b

    st.metric(
        "Total de votos computados",
        total_geral
    )

    st.caption(f"Sistema A: {total_a} votos")
    st.caption(f"Sistema B: {total_b} votos")

    st.divider()

    st.link_button(
        "📊 Abrir planilha no Google Sheets",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit",
        use_container_width=True
    )

    st.divider()

    if st.button(
        "🔄 Reiniciar votação",
        use_container_width=True
    ):
        reiniciar_votacao()

        st.session_state.votos_a = {
            candidato: 0 for candidato in CANDIDATOS
        }

        st.session_state.votos_b = {
            candidato: 0 for candidato in CANDIDATOS
        }

        st.session_state.historico = []
        st.session_state.voto_pendente_a = None
        st.session_state.voto_pendente_b = None

        st.success("Votação reiniciada.")
        st.rerun()

    st.caption(
        "O percentual é aplicado somente ao resultado apresentado "
        "pelo Sistema A. O registro original não é alterado."
    )


# ============================================================
# SISTEMA A
# ============================================================

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🔴 Sistema A")
    st.caption(
        "Sistema de demonstração com alteração proposital do resultado"
    )

    st.markdown(
        '<div class="caixa-alerta">'
        '<b>Manipulação ativada para fins educacionais.</b><br>'
        f'O resultado apresentado pode favorecer: '
        f'<b>{candidato_preferido}</b>.'
        '</div>',
        unsafe_allow_html=True
    )

    escolha_a = st.radio(
        "Escolha um candidato:",
        CANDIDATOS,
        key="escolha_a"
    )

    if st.button(
        "Registrar voto no Sistema A",
        use_container_width=True
    ):
        registrar_voto("A", escolha_a)

    if st.session_state.voto_pendente_a:
        st.info(
            f"Você selecionou **{st.session_state.voto_pendente_a}**. "
            "Confirme o voto abaixo."
        )

        if st.button(
            "✅ Confirmar voto no Sistema A",
            use_container_width=True
        ):
            if confirmar_voto("A"):
                st.success("Voto confirmado e salvo no Google Sheets.")
                st.rerun()

    st.divider()

    votos_a_originais = resultado_integro(
        st.session_state.votos_a
    )

    votos_a_apresentados = resultado_manipulado(
        st.session_state.votos_a,
        candidato_preferido,
        percentual
    )

    st.markdown("**Registro original dos votos:**")

    st.dataframe(
        tabela_resultado(votos_a_originais),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("**Resultado apresentado pelo sistema:**")

    st.dataframe(
        tabela_resultado(votos_a_apresentados),
        use_container_width=True,
        hide_index=True
    )

    total_original_a = sum(votos_a_originais.values())
    total_apresentado_a = sum(votos_a_apresentados.values())

    if total_original_a < 10:
        st.info(
            f"Com {total_original_a} voto(s), o Sistema A ainda "
            "apresenta exatamente o resultado registrado. "
            "A demonstração da alteração começa a partir de 10 votos."
        )

    st.caption(
        f"Votos registrados: {total_original_a} | "
        f"Votos apresentados: {total_apresentado_a}"
    )


# ============================================================
# SISTEMA B
# ============================================================

with col_b:
    st.subheader("🟢 Sistema B")
    st.caption(
        "Sistema de referência sem alteração do resultado"
    )

    st.markdown(
        '<div class="caixa-ok">'
        '<b>Integridade preservada.</b><br>'
        'O resultado apresentado corresponde aos votos registrados.'
        '</div>',
        unsafe_allow_html=True
    )

    escolha_b = st.radio(
        "Escolha um candidato:",
        CANDIDATOS,
        key="escolha_b"
    )

    if st.button(
        "Registrar voto no Sistema B",
        use_container_width=True
    ):
        registrar_voto("B", escolha_b)

    if st.session_state.voto_pendente_b:
        st.info(
            f"Você selecionou **{st.session_state.voto_pendente_b}**. "
            "Confirme o voto abaixo."
        )

        if st.button(
            "✅ Confirmar voto no Sistema B",
            use_container_width=True
        ):
            if confirmar_voto("B"):
                st.success("Voto confirmado e salvo no Google Sheets.")
                st.rerun()

    st.divider()

    votos_b = resultado_integro(
        st.session_state.votos_b
    )

    st.markdown("**Resultado registrado e apresentado:**")

    st.dataframe(
        tabela_resultado(votos_b),
        use_container_width=True,
        hide_index=True
    )

    total_b = sum(votos_b.values())

    st.caption(
        f"Total de votos registrados: {total_b}"
    )


# ============================================================
# COMPARAÇÃO
# ============================================================

st.divider()
st.header("📊 Comparação dos dois sistemas")

votos_a_originais = resultado_integro(
    st.session_state.votos_a
)

votos_a_apresentados = resultado_manipulado(
    st.session_state.votos_a,
    candidato_preferido,
    percentual
)

votos_b = resultado_integro(
    st.session_state.votos_b
)

comparacao = pd.DataFrame(
    {
        "Candidato": CANDIDATOS,
        "Sistema A - registrado": [
            votos_a_originais[c]
            for c in CANDIDATOS
        ],
        "Sistema A - apresentado": [
            votos_a_apresentados[c]
            for c in CANDIDATOS
        ],
        "Sistema B - íntegro": [
            votos_b[c]
            for c in CANDIDATOS
        ],
    }
)

st.dataframe(
    comparacao,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# AUDITORIA
# ============================================================

total_registrado_a = sum(
    votos_a_originais.values()
)

if total_registrado_a > 0:
    diferencas = {
        candidato:
            votos_a_apresentados[candidato]
            - votos_a_originais[candidato]
        for candidato in CANDIDATOS
    }

    st.subheader("🔎 Auditoria da demonstração")

    alteracoes = [
        {
            "Candidato": candidato,
            "Registrado": votos_a_originais[candidato],
            "Apresentado": votos_a_apresentados[candidato],
            "Diferença": diferencas[candidato],
        }
        for candidato in CANDIDATOS
        if diferencas[candidato] != 0
    ]

    if alteracoes:
        st.dataframe(
            pd.DataFrame(alteracoes),
            use_container_width=True,
            hide_index=True
        )

        st.warning(
            "A diferença acima é proposital e serve para demonstrar "
            "uma falha de integridade. O registro original dos votos "
            "permanece armazenado no Google Sheets."
        )
    else:
        st.success(
            "Nenhuma diferença foi detectada no resultado apresentado."
        )


# ============================================================
# HISTÓRICO
# ============================================================

if st.session_state.historico:
    with st.expander("📜 Histórico de votos confirmados"):
        st.dataframe(
            pd.DataFrame(st.session_state.historico),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "Projeto educacional. Candidatos, votos e resultados são fictícios. "
    "Não utilizar para eleições reais ou para interferir em processos eleitorais."
)
