import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from scripts.tratamento_dados import BASE_DIR, processar_planilha


UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"

# O site trabalha sempre com a ultima planilha enviada.
ARQUIVO_UPLOAD = UPLOAD_DIR / "planilha_enviada.xlsx"
ARQUIVO_EXCEL = OUTPUT_DIR / "frequencia_tratada.xlsx"
ARQUIVO_RELATORIO = OUTPUT_DIR / "dashboard_frequencia.html"
EXTENSOES_PERMITIDAS = {".xlsx"}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dashboard-frequencia-escolar")


def extensao_permitida(nome_arquivo: str) -> bool:
    """Confere se o arquivo enviado esta no formato esperado."""
    return Path(nome_arquivo).suffix.lower() in EXTENSOES_PERMITIDAS


@app.route("/", methods=["GET", "POST"])
def index():
    relatorio_gerado = ARQUIVO_RELATORIO.exists()

    if request.method == "POST":
        arquivo = request.files.get("planilha")

        if not arquivo or arquivo.filename == "":
            flash("Selecione uma planilha Excel antes de gerar o relatorio.", "erro")
            return redirect(url_for("index"))

        nome_seguro = secure_filename(arquivo.filename)
        if not extensao_permitida(nome_seguro):
            flash("Envie um arquivo no formato .xlsx.", "erro")
            return redirect(url_for("index"))

        try:
            # Salva o arquivo recebido e chama o mesmo tratamento usado no terminal.
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            arquivo.save(ARQUIVO_UPLOAD)
            processar_planilha(
                arquivo_entrada=ARQUIVO_UPLOAD,
                arquivo_saida=ARQUIVO_EXCEL,
                arquivo_dashboard=ARQUIVO_RELATORIO,
            )
            flash("Planilha processada e relatorio gerado com sucesso.", "sucesso")
            return redirect(url_for("index"))
        except Exception as erro:
            flash(f"Nao foi possivel gerar o relatorio: {erro}", "erro")
            return redirect(url_for("index"))

    return render_template("index.html", relatorio_gerado=relatorio_gerado)


@app.route("/relatorio")
def relatorio():
    """Abre o dashboard HTML gerado pelo processamento."""
    if not ARQUIVO_RELATORIO.exists():
        flash("Gere um relatorio antes de tentar visualiza-lo.", "erro")
        return redirect(url_for("index"))

    return send_file(ARQUIVO_RELATORIO)


@app.route("/download/excel")
def download_excel():
    """Disponibiliza a planilha tratada para download."""
    if not ARQUIVO_EXCEL.exists():
        flash("Gere um relatorio antes de baixar a planilha tratada.", "erro")
        return redirect(url_for("index"))

    return send_file(ARQUIVO_EXCEL, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", port=5000)
