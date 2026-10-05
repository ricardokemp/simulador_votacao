# 🗳️ Simulador de Integridade de Votação

Aplicação web educacional desenvolvida em Python + Streamlit para demonstrar,
de forma controlada e explícita, a diferença entre:

- um sistema que apresenta exatamente os votos registrados;
- um sistema cujo resultado apresentado sofre uma alteração proposital.

## ⚠️ Aviso

Este projeto é **somente uma demonstração educacional**.

Os candidatos e votos são fictícios. A alteração do resultado é identificada
claramente na interface para demonstrar uma falha de integridade.

Não é um sistema eleitoral real e não deve ser utilizado para eleições,
votações reais ou interferência em processos eleitorais.

## Estrutura

```text
simulador-votacao/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Executar localmente

Instale Python 3.10 ou superior.

```bash
pip install -r requirements.txt
```

Depois:

```bash
streamlit run app.py
```

O Streamlit abrirá a aplicação no navegador.

## Publicar no GitHub + Streamlit

1. Crie um repositório no GitHub.
2. Envie `app.py`, `requirements.txt`, `README.md` e `.gitignore`.
3. No Streamlit Community Cloud, crie uma nova aplicação.
4. Selecione o repositório.
5. Selecione o arquivo `app.py`.
6. Publique.

A aplicação poderá ser acessada por uma URL pública fornecida pelo
Streamlit Community Cloud.

## Como funciona

### Sistema A

O voto é confirmado normalmente e permanece registrado no estado da aplicação.

Depois, para fins de demonstração, a aplicação gera um segundo conjunto de
dados chamado "resultado apresentado". Uma porcentagem configurável dos votos
dos outros candidatos é transferida para o candidato selecionado como
favorecido.

A interface mostra os dois conjuntos de dados para tornar a alteração
auditável.

### Sistema B

O resultado apresentado é exatamente igual aos votos registrados.

### Comparação

A parte inferior da aplicação apresenta:

- votos registrados no Sistema A;
- resultado apresentado pelo Sistema A;
- votos registrados no Sistema B;
- diferenças detectadas pela auditoria da demonstração.

## Licença

Projeto demonstrativo para fins educacionais.
