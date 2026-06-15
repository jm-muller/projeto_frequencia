from html import escape
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
ARQUIVO_ENTRADA = BASE_DIR / "dados" / "frequencia_alunos.xlsx"
ARQUIVO_SAIDA = BASE_DIR / "output" / "frequencia_tratada.xlsx"
ARQUIVO_DASHBOARD = BASE_DIR / "output" / "dashboard_frequencia.html"

# Colunas minimas para o calculo da frequencia escolar.
COLUNAS_OBRIGATORIAS = [
    "ID_Aluno",
    "Nome_Aluno",
    "Turma",
    "Serie",
    "Total_Aulas",
    "Presencas",
]


def validar_campos_vazios(base: pd.DataFrame) -> None:
    """Interrompe o processamento caso existam dados vazios na planilha."""
    if base.isnull().any().any():
        colunas_com_vazios = base.columns[base.isnull().any()].tolist()
        raise ValueError(
            "Foram encontrados campos vazios nas colunas: "
            + ", ".join(colunas_com_vazios)
        )


def validar_colunas_obrigatorias(base: pd.DataFrame) -> None:
    """Verifica se a planilha tem a estrutura esperada pelo projeto."""
    colunas_faltantes = [
        coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in base.columns
    ]
    if colunas_faltantes:
        raise ValueError(
            "A planilha nao possui as colunas obrigatorias: "
            + ", ".join(colunas_faltantes)
        )


def tratar_base(base: pd.DataFrame) -> pd.DataFrame:
    """Recalcula faltas, percentual de frequencia e situacao do aluno."""
    base_tratada = base.copy()

    base_tratada["Faltas"] = (
        base_tratada["Total_Aulas"] - base_tratada["Presencas"]
    )
    base_tratada["Frequencia_Percentual"] = (
        base_tratada["Presencas"] / base_tratada["Total_Aulas"] * 100
    ).round(2)
    base_tratada["Status_Frequencia"] = base_tratada[
        "Frequencia_Percentual"
    ].apply(lambda frequencia: "Regular" if frequencia >= 75 else "Em risco")

    return base_tratada


def criar_resumo_por_turma(base_tratada: pd.DataFrame) -> pd.DataFrame:
    """Agrupa os dados para facilitar a leitura do relatorio por turma."""
    resumo = (
        base_tratada.groupby("Turma")
        .agg(
            Total_Alunos=("ID_Aluno", "count"),
            Frequencia_Media_Turma=("Frequencia_Percentual", "mean"),
            Alunos_Regulares=(
                "Status_Frequencia",
                lambda status: (status == "Regular").sum(),
            ),
            Alunos_Em_Risco=(
                "Status_Frequencia",
                lambda status: (status == "Em risco").sum(),
            ),
        )
        .reset_index()
    )

    resumo["Frequencia_Media_Turma"] = resumo[
        "Frequencia_Media_Turma"
    ].round(2)
    return resumo


def formatar_percentual(valor: float) -> str:
    """Deixa os percentuais no formato usado nos textos do relatorio."""
    return f"{valor:.2f}%".replace(".", ",")


def criar_linhas_tabela(base_tratada: pd.DataFrame) -> str:
    """Monta as linhas da tabela principal do dashboard."""
    linhas = []
    colunas = [
        "Nome_Aluno",
        "Turma",
        "Serie",
        "Faltas",
        "Frequencia_Percentual",
        "Status_Frequencia",
    ]

    for aluno in base_tratada.sort_values("Frequencia_Percentual").to_dict("records"):
        status = str(aluno["Status_Frequencia"])
        classe_status = "status-risco" if status == "Em risco" else "status-regular"
        celulas = []

        for coluna in colunas:
            valor = aluno[coluna]
            if coluna == "Frequencia_Percentual":
                valor = formatar_percentual(float(valor))
            celulas.append(f"<td>{escape(str(valor))}</td>")

        celulas[-1] = (
            f'<td><span class="badge {classe_status}">{escape(status)}</span></td>'
        )
        linhas.append("<tr>" + "".join(celulas) + "</tr>")

    return "\n".join(linhas)


def criar_barras_turma(resumo_turma: pd.DataFrame) -> str:
    """Cria barras simples em HTML para comparar as turmas."""
    maior_total = max(int(resumo_turma["Total_Alunos"].max()), 1)
    barras = []

    for turma in resumo_turma.sort_values("Turma").to_dict("records"):
        total = int(turma["Total_Alunos"])
        em_risco = int(turma["Alunos_Em_Risco"])
        largura_total = total / maior_total * 100
        largura_risco = em_risco / max(total, 1) * 100
        nome_turma = escape(str(turma["Turma"]))
        barras.append(
            f"""
            <div class="bar-row">
                <div class="bar-label">{nome_turma}</div>
                <div class="bar-track" aria-label="{total} alunos">
                    <div class="bar-total" style="width: {largura_total:.2f}%"></div>
                    <div class="bar-risk" style="width: {largura_risco:.2f}%"></div>
                </div>
                <div class="bar-value">{total} alunos | {em_risco} em risco</div>
            </div>
            """
        )

    return "\n".join(barras)


def criar_dashboard_html(base_tratada: pd.DataFrame, resumo_turma: pd.DataFrame) -> str:
    """Gera o arquivo HTML final com indicadores, graficos e tabela."""
    total_alunos = len(base_tratada)
    frequencia_media = float(base_tratada["Frequencia_Percentual"].mean())
    alunos_risco = int((base_tratada["Status_Frequencia"] == "Em risco").sum())
    alunos_regulares = int((base_tratada["Status_Frequencia"] == "Regular").sum())
    percentual_regular = alunos_regulares / max(total_alunos, 1) * 100
    percentual_risco = alunos_risco / max(total_alunos, 1) * 100
    alunos_mais_risco = base_tratada.sort_values("Frequencia_Percentual").head(5)
    lista_risco = "\n".join(
        f"<li>{escape(str(aluno.Nome_Aluno))} - {escape(str(aluno.Turma))}: "
        f"{formatar_percentual(float(aluno.Frequencia_Percentual))}</li>"
        for aluno in alunos_mais_risco.itertuples(index=False)
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Frequencia Escolar</title>
    <style>
        :root {{
            --bg: #f6f7f9;
            --panel: #ffffff;
            --text: #18202a;
            --muted: #637083;
            --line: #d9e0e8;
            --regular: #227a50;
            --regular-soft: #dff3e8;
            --risk: #b23a3a;
            --risk-soft: #f8e2e2;
            --accent-soft: #dfeaf7;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            background: var(--bg);
            color: var(--text);
            font-family: Arial, Helvetica, sans-serif;
            line-height: 1.5;
        }}

        header {{
            background: #18324d;
            color: #ffffff;
            padding: 28px 32px;
        }}

        header h1 {{
            margin: 0 0 8px;
            font-size: clamp(26px, 4vw, 42px);
            font-weight: 700;
        }}

        header p {{
            margin: 0;
            max-width: 860px;
            color: #dce7f3;
        }}

        main {{
            width: min(1180px, calc(100% - 32px));
            margin: 24px auto 40px;
        }}

        .cards {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 16px;
            margin-bottom: 22px;
        }}

        .card, .panel {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: 0 8px 18px rgba(24, 32, 42, 0.06);
        }}

        .card {{
            padding: 18px;
        }}

        .card span {{
            color: var(--muted);
            display: block;
            font-size: 14px;
            margin-bottom: 8px;
        }}

        .card strong {{
            display: block;
            font-size: 30px;
        }}

        .grid {{
            display: grid;
            grid-template-columns: 1.35fr 0.65fr;
            gap: 16px;
            margin-bottom: 16px;
        }}

        .panel {{
            padding: 20px;
        }}

        h2 {{
            font-size: 20px;
            margin: 0 0 18px;
        }}

        .bar-row {{
            display: grid;
            grid-template-columns: 82px 1fr 170px;
            gap: 12px;
            align-items: center;
            margin: 14px 0;
        }}

        .bar-label, .bar-value {{
            color: var(--muted);
            font-size: 14px;
        }}

        .bar-track {{
            position: relative;
            height: 22px;
            overflow: hidden;
            border-radius: 6px;
            background: #eef2f6;
        }}

        .bar-total, .bar-risk {{
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
        }}

        .bar-total {{
            background: var(--accent-soft);
        }}

        .bar-risk {{
            background: var(--risk);
            opacity: 0.82;
        }}

        .donut {{
            width: 190px;
            aspect-ratio: 1;
            margin: 8px auto 18px;
            border-radius: 50%;
            background: conic-gradient(
                var(--regular) 0 {percentual_regular:.2f}%,
                var(--risk) {percentual_regular:.2f}% 100%
            );
            position: relative;
        }}

        .donut::after {{
            content: "";
            position: absolute;
            inset: 42px;
            border-radius: 50%;
            background: var(--panel);
        }}

        .legend {{
            display: grid;
            gap: 8px;
            color: var(--muted);
            font-size: 14px;
        }}

        .legend span::before {{
            content: "";
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }}

        .legend .regular::before {{
            background: var(--regular);
        }}

        .legend .risk::before {{
            background: var(--risk);
        }}

        .risk-list {{
            margin: 0;
            padding-left: 20px;
            color: var(--muted);
        }}

        .table-wrap {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 760px;
        }}

        th, td {{
            border-bottom: 1px solid var(--line);
            padding: 11px 10px;
            text-align: left;
            font-size: 14px;
        }}

        th {{
            color: var(--muted);
            font-weight: 700;
            background: #f9fafc;
        }}

        .badge {{
            display: inline-block;
            border-radius: 999px;
            padding: 4px 10px;
            font-weight: 700;
            font-size: 12px;
        }}

        .status-regular {{
            color: var(--regular);
            background: var(--regular-soft);
        }}

        .status-risco {{
            color: var(--risk);
            background: var(--risk-soft);
        }}

        footer {{
            color: var(--muted);
            font-size: 13px;
            margin-top: 16px;
            text-align: center;
        }}

        @media (max-width: 900px) {{
            .cards {{
                grid-template-columns: 1fr 1fr;
            }}

            .grid {{
                display: block;
            }}

            .grid .panel {{
                margin-bottom: 16px;
            }}
        }}

        @media (max-width: 620px) {{
            header {{
                padding: 24px 18px;
            }}

            main {{
                width: min(100% - 20px, 1180px);
            }}

            .cards {{
                grid-template-columns: 1fr;
            }}

            .bar-row {{
                grid-template-columns: 1fr;
                gap: 6px;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Dashboard de Frequencia Escolar</h1>
        <p>Monitoramento da frequencia dos alunos por turma, com destaque para estudantes abaixo de 75%.</p>
    </header>

    <main>
        <section class="cards" aria-label="Indicadores principais">
            <div class="card"><span>Total de alunos</span><strong>{total_alunos}</strong></div>
            <div class="card"><span>Frequencia media</span><strong>{formatar_percentual(frequencia_media)}</strong></div>
            <div class="card"><span>Alunos regulares</span><strong>{alunos_regulares}</strong></div>
            <div class="card"><span>Alunos em risco</span><strong>{alunos_risco}</strong></div>
        </section>

        <section class="grid">
            <div class="panel">
                <h2>Alunos por turma</h2>
                {criar_barras_turma(resumo_turma)}
            </div>

            <div class="panel">
                <h2>Status geral</h2>
                <div class="donut" aria-label="Grafico de status geral"></div>
                <div class="legend">
                    <span class="regular">Regulares: {alunos_regulares} ({formatar_percentual(percentual_regular)})</span>
                    <span class="risk">Em risco: {alunos_risco} ({formatar_percentual(percentual_risco)})</span>
                </div>
            </div>
        </section>

        <section class="panel">
            <h2>Menores frequencias</h2>
            <ol class="risk-list">
                {lista_risco}
            </ol>
        </section>

        <section class="panel" style="margin-top: 16px;">
            <h2>Tabela de acompanhamento</h2>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Aluno</th>
                            <th>Turma</th>
                            <th>Serie</th>
                            <th>Faltas</th>
                            <th>Frequencia</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {criar_linhas_tabela(base_tratada)}
                    </tbody>
                </table>
            </div>
        </section>

        <footer>Arquivo gerado automaticamente a partir da planilha tratada.</footer>
    </main>
</body>
</html>
"""


def processar_planilha(
    arquivo_entrada: Path = ARQUIVO_ENTRADA,
    arquivo_saida: Path = ARQUIVO_SAIDA,
    arquivo_dashboard: Path = ARQUIVO_DASHBOARD,
) -> tuple[Path, Path]:
    """Processa a planilha e devolve os caminhos dos arquivos gerados."""
    if not arquivo_entrada.exists():
        raise FileNotFoundError(f"Arquivo de entrada nao encontrado: {arquivo_entrada}")

    base = pd.read_excel(arquivo_entrada)
    validar_colunas_obrigatorias(base)
    validar_campos_vazios(base)

    base_tratada = tratar_base(base)
    resumo_turma = criar_resumo_por_turma(base_tratada)

    arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
    arquivo_dashboard.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
        base_tratada.to_excel(writer, sheet_name="Base_Tratada", index=False)
        resumo_turma.to_excel(writer, sheet_name="Resumo_Turma", index=False)

    arquivo_dashboard.write_text(
        criar_dashboard_html(base_tratada, resumo_turma),
        encoding="utf-8",
    )

    return arquivo_saida, arquivo_dashboard


def main() -> None:
    arquivo_saida, arquivo_dashboard = processar_planilha()

    print(f"Arquivo tratado gerado com sucesso: {arquivo_saida}")
    print(f"Dashboard HTML gerado com sucesso: {arquivo_dashboard}")


if __name__ == "__main__":
    main()
