# Site Gerador de Relatorio de Frequencia Escolar

Projeto simples de Ciencia de Dados para uma Atividade Extensionista com o tema:

**Desenvolver um Dashboard Online para Monitoramento da Frequencia Escolar em Escola Publica de Porto Alegre/RS**.

O produto final deste projeto e um site simples em Python no qual o usuario envia uma planilha Excel e gera automaticamente um relatorio visual em HTML.

## Objetivo do projeto

O objetivo deste projeto e facilitar o acompanhamento da frequencia escolar dos alunos de uma escola publica, ajudando professores e equipe pedagogica a identificarem alunos em risco por baixa frequencia.

Com o site, a escola pode enviar a planilha e visualizar:

- total de alunos acompanhados;
- frequencia media;
- quantidade de alunos com frequencia regular;
- quantidade de alunos em risco;
- turmas com maior necessidade de acompanhamento;
- tabela de alunos ordenada pela menor frequencia.

## Tecnologias utilizadas

- Python
- Pandas
- Flask
- Excel
- HTML
- CSS
- GitHub

## Estrutura do projeto

```text
dashboard-frequencia-escolar/
|
|-- dados/
|   `-- frequencia_alunos.xlsx
|
|-- output/
|   |-- frequencia_tratada.xlsx
|   `-- dashboard_frequencia.html
|
|-- static/
|   `-- css/
|       `-- site.css
|
|-- templates/
|   `-- index.html
|
|-- scripts/
|   `-- tratamento_dados.py
|
|-- app.py
|-- README.md
`-- requirements.txt
```

## Base de dados

A planilha `dados/frequencia_alunos.xlsx` possui dados ficticios de pelo menos 50 alunos, com as seguintes colunas:

- ID_Aluno
- Nome_Aluno
- Turma
- Serie
- Total_Aulas
- Presencas
- Faltas
- Frequencia_Percentual
- Status_Frequencia

Regras utilizadas:

- `Total_Aulas` e igual a 100 para todos os alunos.
- `Presencas` varia entre 50 e 100.
- `Faltas` e calculado por `Total_Aulas - Presencas`.
- `Frequencia_Percentual` e calculado por `Presencas / Total_Aulas * 100`.
- `Status_Frequencia` recebe `Regular` quando a frequencia e maior ou igual a 75%.
- `Status_Frequencia` recebe `Em risco` quando a frequencia e menor que 75%.

## Como instalar as dependencias

No terminal, acesse a pasta do projeto:

```bash
cd dashboard-frequencia-escolar
```

Instale as bibliotecas necessarias:

```bash
pip install -r requirements.txt
```

## Como executar o site

Execute o site local:

```bash
python app.py
```

Depois, acesse no navegador:

```text
http://127.0.0.1:5000
```

Na tela inicial:

1. Clique em `Selecionar planilha`.
2. Escolha um arquivo `.xlsx`.
3. Clique em `Subir planilha e gerar relatorio`.
4. Clique em `Abrir relatorio` para visualizar o dashboard.
5. Se desejar, clique em `Baixar Excel tratado`.

## Como executar apenas o tratamento em Python

Execute o script:

```bash
python scripts/tratamento_dados.py
```

O script realiza as seguintes etapas:

1. Le o arquivo `dados/frequencia_alunos.xlsx`.
2. Verifica se existem campos vazios.
3. Recalcula as colunas `Faltas`, `Frequencia_Percentual` e `Status_Frequencia`.
4. Cria um resumo por turma.
5. Exporta o arquivo tratado para `output/frequencia_tratada.xlsx`.
6. Gera o dashboard visual em `output/dashboard_frequencia.html`.

## Como visualizar o dashboard gerado

Depois de executar o script, abra o arquivo abaixo no navegador:

```text
output/dashboard_frequencia.html
```

O arquivo HTML contem:

- cartoes com os indicadores principais;
- grafico de alunos por turma;
- grafico de status geral;
- lista dos alunos com menor frequencia;
- tabela completa para acompanhamento.

Como o dashboard e um arquivo HTML simples, ele pode ser enviado, aberto no navegador ou publicado em um repositorio GitHub.

## Como publicar para apresentar sem localhost

Este projeto esta preparado para dois tipos de publicacao:

### Opcao 1: GitHub Pages

Use esta opcao para apresentar o dashboard pronto, sem a tela de upload.

O arquivo `index.html` na raiz do projeto e uma copia do dashboard gerado em `output/dashboard_frequencia.html`. Ele pode ser publicado diretamente no GitHub Pages.

Passo a passo:

1. Suba o projeto para um repositorio no GitHub.
2. No GitHub, acesse `Settings`.
3. Acesse `Pages`.
4. Em `Build and deployment`, selecione `Deploy from a branch`.
5. Escolha a branch `main` e a pasta `/root`.
6. Salve e aguarde o GitHub gerar o link.

O link ficara parecido com:

```text
https://SEU-USUARIO.github.io/dashboard-frequencia-escolar/
```

### Opcao 2: Render

Use esta opcao para publicar o site Flask completo, com upload de planilha e geracao do relatorio online.

Arquivos ja preparados para o Render:

- `requirements.txt`, com as dependencias do projeto;
- `gunicorn`, servidor usado em producao;
- `Procfile`, com o comando de inicializacao;
- `render.yaml`, com a configuracao do servico web.

Passo a passo:

1. Suba o projeto para um repositorio no GitHub.
2. Crie uma conta ou acesse o Render.
3. Clique em `New +`.
4. Escolha `Web Service`.
5. Conecte o repositorio do GitHub.
6. Use as configuracoes:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

7. Clique em `Deploy Web Service`.
8. Ao finalizar, o Render fornecera um link publico terminado em `.onrender.com`.

Observacao: o Render pode apagar arquivos enviados depois de reiniciar o servico, pois este projeto nao usa banco de dados nem armazenamento persistente. Para apresentacao, isso nao atrapalha: basta enviar a planilha novamente quando quiser gerar o relatorio.

## Como enviar o projeto para o GitHub

1. Crie um repositorio no GitHub com o nome `dashboard-frequencia-escolar`.
2. No terminal, dentro da pasta do projeto, execute:

```bash
git init
git add .
git commit -m "Cria dashboard HTML de frequencia escolar"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/dashboard-frequencia-escolar.git
git push -u origin main
```

3. Substitua `SEU-USUARIO` pelo seu usuario do GitHub.
4. Copie o link do repositorio para entregar junto com a atividade.

## Entregaveis finais

- Codigo Python funcionando.
- Arquivo Excel original em `dados/frequencia_alunos.xlsx`.
- Site para upload da planilha em `app.py`.
- Arquivo Excel tratado em `output/frequencia_tratada.xlsx`.
- Dashboard HTML em `output/dashboard_frequencia.html`.
- README com passo a passo.
- Link do GitHub.
- Link do dashboard publicado ou video de ate 5 minutos mostrando sua utilizacao.

## Criterios de simplicidade

Este projeto nao utiliza login, banco de dados, API externa, Machine Learning ou automacoes complexas.

O foco e manter uma solucao basica, didatica e facil de entender:

- planilha simples;
- tratamento em Python;
- upload pelo site;
- visualizacao em HTML;
- uso por professores sem conhecimento tecnico em tecnologia.
