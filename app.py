import streamlit as st
import pandas as pd


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Simulador de Integridade de Votação",
    page_icon="🗳️",
    layout="wide"
)


# ============================================================
# ESTADO DA APLICAÇÃO
# ============================================================

if "votos_a" not in st.session_state:
    st.session_state.votos_a = {}

if "votos_b" not in st.session_state:
    st.session_state.votos_b = {}

if "voto_pendente_a" not in st.session_state:
    st.session_state.voto_pendente_a = None

if "voto_pendente_b" not in st.session_state:
    st.session_state.voto_pendente_b = None

if "historico" not in st.session_state:
    st.session_state.historico = []


# ============================================================
# CANDIDATOS
# ============================================================

CANDIDATOS = [
    "Candidato Alfa",
    "Candidato Beta",
    "Candidato Gama",
    "Candidato Delta",
]


# ============================================================
# ESTILO
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


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    '<div class="titulo">'
    '🗳️ Simulador de Integridade de Votação'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Demonstração educacional de como a integridade de um sistema '
    'pode ser comprometida.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# CONTADOR GERAL DA URNA
# ============================================================

total_votos_a = sum(
    st.session_state.votos_a.values()
)

total_votos_b = sum(
    st.session_state.votos_b.values()
)

total_votos_urna = (
    total_votos_a +
    total_votos_b
)


st.metric(
    label="🗳️ Total de votos computados na urna",
    value=total_votos_urna
)


# ============================================================
# AVISO EDUCACIONAL
# ============================================================

st.warning(
    "DEMONSTRAÇÃO EDUCACIONAL: todos os candidatos e votos são fictícios. "
    "O sistema manipulado abaixo existe apenas para demonstrar uma falha "
    "de integridade e identifica claramente quando a alteração ocorre."
)


# ============================================================
# CONFIGURAÇÃO DA DEMONSTRAÇÃO
# ============================================================

with st.sidebar:

    st.header(
        "Configuração da demonstração"
    )

    candidato_preferido = st.selectbox(
        "Candidato favorecido no sistema manipulado",
        CANDIDATOS,
        index=0
    )

    percentual = st.slider(
        "Percentual artificial transferido para o candidato favorecido",
        min_value=0,
        max_value=80,
        value=35,
        step=5,
        format="%d%%"
    )

    st.divider()

    if st.button(
        "🔄 Reiniciar votação",
        use_container_width=True
    ):

        st.session_state.votos_a = {}
        st.session_state.votos_b = {}
        st.session_state.voto_pendente_a = None
        st.session_state.voto_pendente_b = None
        st.session_state.historico = []

        st.rerun()

    st.caption(
        "A alteração do resultado do Sistema A "
        "começa somente quando a votação atingir "
        "10 votos registrados."
    )


# ============================================================
# FUNÇÃO PARA REGISTRAR VOTO PENDENTE
# ============================================================

def registrar_voto(sistema, candidato):

    if sistema == "A":

        st.session_state.voto_pendente_a = candidato

    elif sistema == "B":

        st.session_state.voto_pendente_b = candidato


# ============================================================
# FUNÇÃO PARA CONFIRMAR VOTO
# ============================================================

def confirmar_voto(sistema):

    if sistema == "A":

        candidato = (
            st.session_state.voto_pendente_a
        )

        if candidato:

            st.session_state.votos_a[candidato] = (
                st.session_state.votos_a.get(
                    candidato,
                    0
                ) + 1
            )

            st.session_state.historico.append(
                {
                    "Sistema": "A",
                    "Candidato": candidato,
                    "Status": "Confirmado"
                }
            )

            st.session_state.voto_pendente_a = None

            return True


    elif sistema == "B":

        candidato = (
            st.session_state.voto_pendente_b
        )

        if candidato:

            st.session_state.votos_b[candidato] = (
                st.session_state.votos_b.get(
                    candidato,
                    0
                ) + 1
            )

            st.session_state.historico.append(
                {
                    "Sistema": "B",
                    "Candidato": candidato,
                    "Status": "Confirmado"
                }
            )

            st.session_state.voto_pendente_b = None

            return True


    return False


# ============================================================
# RESULTADO ÍNTEGRO
# ============================================================

def resultado_integro(votos):

    return {
        candidato: votos.get(
            candidato,
            0
        )
        for candidato in CANDIDATOS
    }


# ============================================================
# RESULTADO DO SISTEMA A
# ============================================================

def resultado_manipulado(
    votos,
    favorecido,
    percentual_transferencia
):

    """
    Demonstração educacional.

    Até 9 votos:
        o resultado apresentado é igual ao registro original.

    A partir de 10 votos:
        uma parcela dos votos dos demais candidatos é
        transferida para o candidato favorecido.

    O registro original permanece preservado.
    """

    original = resultado_integro(
        votos
    )

    total_votos = sum(
        original.values()
    )


    # --------------------------------------------------------
    # LIMITE DE 10 VOTOS
    # --------------------------------------------------------

    if total_votos < 10:

        return original


    # --------------------------------------------------------
    # PERCENTUAL ZERO
    # --------------------------------------------------------

    if percentual_transferencia <= 0:

        return original


    # --------------------------------------------------------
    # VOTOS DOS DEMAIS CANDIDATOS
    # --------------------------------------------------------

    total_outros = sum(
        quantidade
        for candidato, quantidade
        in original.items()
        if candidato != favorecido
    )


    if total_outros <= 0:

        return original


    # --------------------------------------------------------
    # CALCULA A TRANSFERÊNCIA
    # --------------------------------------------------------

    transferencia = int(
        total_outros
        * percentual_transferencia
        / 100
    )


    if transferencia <= 0:

        return original


    resultado = original.copy()


    # Adiciona os votos ao candidato favorecido
    resultado[ favorecido ] += transferencia


    restante = transferencia


    # Lista dos demais candidatos
    outros = [
        candidato
        for candidato in CANDIDATOS
        if candidato != favorecido
        and resultado[candidato] > 0
    ]


    # --------------------------------------------------------
    # RETIRADA PROPORCIONAL
    # --------------------------------------------------------

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


        retirada = min(
            retirada,
            restante
        )


        resultado[candidato] -= retirada

        restante -= retirada


    # --------------------------------------------------------
    # AJUSTE FINAL
    # --------------------------------------------------------

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


# ============================================================
# TABELA DE RESULTADOS
# ============================================================

def tabela_resultado(votos):

    total = sum(
        votos.values()
    )

    dados = []


    for candidato in CANDIDATOS:

        quantidade = votos.get(
            candidato,
            0
        )


        percentual_resultado = (
            quantidade / total * 100
        ) if total else 0


        dados.append(
            {
                "Candidato": candidato,
                "Votos": quantidade,
                "%": round(
                    percentual_resultado,
                    1
                )
            }
        )


    return pd.DataFrame(
        dados
    )


# ============================================================
# DUAS COLUNAS
# ============================================================

col_a, col_b = st.columns(2)


# ============================================================
# SISTEMA A
# ============================================================

with col_a:

    st.subheader(
        "🔴 Sistema A"
    )

    st.caption(
        "Sistema de demonstração com alteração proposital "
        "do resultado a partir de 10 votos."
    )


    total_atual_a = sum(
        st.session_state.votos_a.values()
    )


    # --------------------------------------------------------
    # STATUS DA MANIPULAÇÃO
    # --------------------------------------------------------

    if total_atual_a < 10:

        votos_faltantes = (
            10 - total_atual_a
        )

        st.info(
            f"Manipulação ainda não ativada. "
            f"Faltam {votos_faltantes} voto(s) "
            f"para atingir 10 votos."
        )

    else:

        st.warning(
            "Manipulação ativada para fins educacionais. "
            f"O resultado apresentado pode favorecer "
            f"**{candidato_preferido}**."
        )


    st.markdown(
        '<div class="caixa-alerta">'
        '<b>Comportamento simulado.</b><br>'
        f'Candidato favorecido: '
        f'<b>{candidato_preferido}</b>.<br>'
        'A alteração começa somente após 10 votos registrados.'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # ESCOLHA DO CANDIDATO
    # --------------------------------------------------------

    escolha_a = st.radio(
        "Escolha um candidato:",
        CANDIDATOS,
        key="escolha_a"
    )


    # --------------------------------------------------------
    # REGISTRAR VOTO
    # --------------------------------------------------------

    if st.button(
        "Registrar voto no Sistema A",
        use_container_width=True
    ):

        registrar_voto(
            "A",
            escolha_a
        )


    # --------------------------------------------------------
    # CONFIRMAR VOTO
    # --------------------------------------------------------

    if st.session_state.voto_pendente_a:

        st.info(
            f"Você selecionou "
            f"**{st.session_state.voto_pendente_a}**. "
            "Confirme o voto abaixo."
        )


        if st.button(
            "✅ Confirmar voto no Sistema A",
            use_container_width=True
        ):

            if confirmar_voto("A"):

                st.success(
                    "Voto confirmado."
                )

                st.rerun()


    st.divider()


    # --------------------------------------------------------
    # RESULTADOS SISTEMA A
    # --------------------------------------------------------

    votos_a_originais = resultado_integro(
        st.session_state.votos_a
    )


    votos_a_apresentados = resultado_manipulado(
        st.session_state.votos_a,
        candidato_preferido,
        percentual
    )


    st.markdown(
        "**Registro original dos votos:**"
    )


    st.dataframe(
        tabela_resultado(
            votos_a_originais
        ),
        use_container_width=True,
        hide_index=True
    )


    st.markdown(
        "**Resultado apresentado pelo sistema:**"
    )


    st.dataframe(
        tabela_resultado(
            votos_a_apresentados
        ),
        use_container_width=True,
        hide_index=True
    )


    total_original_a = sum(
        votos_a_originais.values()
    )


    total_apresentado_a = sum(
        votos_a_apresentados.values()
    )


    st.caption(
        f"Votos registrados no Sistema A: "
        f"{total_original_a} | "
        f"Votos apresentados: "
        f"{total_apresentado_a}"
    )


# ============================================================
# SISTEMA B
# ============================================================

with col_b:

    st.subheader(
        "🟢 Sistema B"
    )

    st.caption(
        "Sistema de referência sem alteração do resultado."
    )


    st.markdown(
        '<div class="caixa-ok">'
        '<b>Integridade preservada.</b><br>'
        'O resultado apresentado corresponde aos votos registrados.'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # ESCOLHA DO CANDIDATO
    # --------------------------------------------------------

    escolha_b = st.radio(
        "Escolha um candidato:",
        CANDIDATOS,
        key="escolha_b"
    )


    # --------------------------------------------------------
    # REGISTRAR VOTO
    # --------------------------------------------------------

    if st.button(
        "Registrar voto no Sistema B",
        use_container_width=True
    ):

        registrar_voto(
            "B",
            escolha_b
        )


    # --------------------------------------------------------
    # CONFIRMAR VOTO
    # --------------------------------------------------------

    if st.session_state.voto_pendente_b:

        st.info(
            f"Você selecionou "
            f"**{st.session_state.voto_pendente_b}**. "
            "Confirme o voto abaixo."
        )


        if st.button(
            "✅ Confirmar voto no Sistema B",
            use_container_width=True
        ):

            if confirmar_voto("B"):

                st.success(
                    "Voto confirmado."
                )

                st.rerun()


    st.divider()


    # --------------------------------------------------------
    # RESULTADO SISTEMA B
    # --------------------------------------------------------

    votos_b = resultado_integro(
        st.session_state.votos_b
    )


    st.markdown(
        "**Resultado registrado e apresentado:**"
    )


    st.dataframe(
        tabela_resultado(
            votos_b
        ),
        use_container_width=True,
        hide_index=True
    )


    total_b = sum(
        votos_b.values()
    )


    st.caption(
        f"Total de votos registrados no Sistema B: "
        f"{total_b}"
    )


# ============================================================
# COMPARAÇÃO
# ============================================================

st.divider()

st.header(
    "📊 Comparação dos dois sistemas"
)


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
        ]
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


    st.subheader(
        "🔎 Auditoria da demonstração"
    )


    alteracoes = [
        {
            "Candidato": candidato,
            "Registrado": votos_a_originais[candidato],
            "Apresentado": votos_a_apresentados[candidato],
            "Diferença": diferencas[candidato]
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

    elif total_registrado_a < 10:

        st.success(
            "Nenhuma alteração foi aplicada. "
            "O Sistema A ainda não atingiu 10 votos."
        )

    else:

        st.info(
            "Nenhuma diferença foi detectada "
            "com a configuração atual."
        )


    st.warning(
        "A diferença acima é proposital e serve para demonstrar "
        "uma falha de integridade. Em um sistema real, o resultado "
        "deveria ser auditável e reproduzir exatamente os registros originais."
    )


# ============================================================
# HISTÓRICO
# ============================================================

if st.session_state.historico:

    with st.expander(
        "📜 Histórico de votos confirmados"
    ):

        st.dataframe(
            pd.DataFrame(
                st.session_state.historico
            ),
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
