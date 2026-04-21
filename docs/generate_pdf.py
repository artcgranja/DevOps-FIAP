"""Gera o PDF de entrega da atividade DevOps FIAP."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = "/Users/arthurgranja/github/DevOps-FIAP/docs/CidadesEsg-FIAP-entrega.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="TitleBig", parent=styles["Title"], fontSize=26, spaceAfter=18,
    alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="Subtitle", parent=styles["Normal"], fontSize=13, spaceAfter=8,
    alignment=TA_CENTER, textColor=colors.grey,
))
styles.add(ParagraphStyle(
    name="H1", parent=styles["Heading1"], fontSize=18, spaceBefore=16,
    spaceAfter=10, textColor=colors.HexColor("#1a4a7c"),
))
styles.add(ParagraphStyle(
    name="H2", parent=styles["Heading2"], fontSize=14, spaceBefore=12,
    spaceAfter=6, textColor=colors.HexColor("#2e6ba8"),
))
styles.add(ParagraphStyle(
    name="Body", parent=styles["BodyText"], fontSize=11, leading=16,
    spaceAfter=8, alignment=TA_LEFT,
))
styles.add(ParagraphStyle(
    name="CodeBlock", parent=styles["Code"], fontSize=9, leading=12,
    leftIndent=10, textColor=colors.HexColor("#202020"),
    backColor=colors.HexColor("#f3f3f3"),
))
styles.add(ParagraphStyle(
    name="Caption", parent=styles["Italic"], fontSize=9,
    alignment=TA_CENTER, textColor=colors.grey, spaceAfter=10,
))

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Cidades ESG Inteligentes - FIAP DevOps",
    author="Arthur Cavalcanti Granja",
)

story = []
P = lambda text, style="Body": Paragraph(text, styles[style])


def code_block(text: str):
    """Render a preformatted code block with monospace font."""
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe = safe.replace("\n", "<br/>").replace(" ", "&nbsp;")
    return Paragraph(f'<font face="Courier" size="8.5">{safe}</font>', styles["CodeBlock"])


# --- COVER ---
story.append(Spacer(1, 3 * cm))
story.append(P("Cidades ESG Inteligentes", "TitleBig"))
story.append(P("Atividade Avaliativa — Navegando pelo mundo DevOps", "Subtitle"))
story.append(Spacer(1, 1.5 * cm))
story.append(P("<b>Aluno:</b> Arthur Cavalcanti Granja", "Body"))
story.append(P("<b>RM:</b> 560650", "Body"))
story.append(P("<b>Data:</b> 21 de Abril de 2026", "Body"))
story.append(P("<b>Repositório:</b> https://github.com/artcgranja/DevOps-FIAP", "Body"))
story.append(P("<b>Registry:</b> ghcr.io/artcgranja/cidades-esg-api", "Body"))

story.append(Spacer(1, 1.5 * cm))
story.append(P("<b>Resumo</b>", "H2"))
story.append(P(
    "API REST em .NET 8 para gerenciar cidades e indicadores ESG (Environmental, "
    "Social, Governance). O projeto aplica práticas completas de DevOps: "
    "containerização multi-stage com Docker, orquestração via Docker Compose em "
    "dois ambientes isolados (staging e produção), e pipeline CI/CD automatizada "
    "no GitHub Actions que executa build, testes (xUnit), publica imagens no "
    "GitHub Container Registry e gera artefatos de deploy.",
    "Body",
))
story.append(PageBreak())


# --- 1. DESCRIÇÃO DO PIPELINE ---
story.append(P("1. Descrição do Pipeline CI/CD", "H1"))
story.append(P(
    "<b>Ferramenta:</b> GitHub Actions. O workflow está definido em "
    "<font face='Courier'>.github/workflows/ci-cd.yml</font>.",
    "Body",
))

story.append(P("Gatilhos", "H2"))
story.append(P(
    "• <b>Push em <font face='Courier'>develop</font></b> → pipeline completo, "
    "publica imagem com tag <font face='Courier'>:staging</font><br/>"
    "• <b>Push em <font face='Courier'>main</font></b> → pipeline completo, "
    "publica imagem com tag <font face='Courier'>:prod</font><br/>"
    "• <b>Pull Request em <font face='Courier'>main</font></b> → apenas build + "
    "testes (não publica imagem)",
    "Body",
))

story.append(P("Jobs (executados sequencialmente)", "H2"))
cell_style = ParagraphStyle(
    name="Cell", parent=styles["BodyText"], fontSize=9, leading=12, spaceAfter=0,
)
data = [
    ["#", "Job", "O que faz"],
    ["1",
     Paragraph("build-test", cell_style),
     Paragraph(
         "dotnet restore + dotnet build (Release) + dotnet test (xUnit, 6 testes) "
         "+ upload dos resultados como artefato.", cell_style)],
    ["2",
     Paragraph("docker-build-push", cell_style),
     Paragraph(
         "Login no GHCR via GITHUB_TOKEN, build multi-stage da imagem Docker, "
         "push com tags :staging/:prod e :sha-&lt;7&gt; para rastreabilidade.",
         cell_style)],
    ["3",
     Paragraph("deploy", cell_style),
     Paragraph(
         "Determina o ambiente (main→prod, develop→staging), gera artefato "
         "'deploy-instructions-&lt;env&gt;.txt' com comandos "
         "docker compose pull &amp;&amp; up.", cell_style)],
]
tbl = Table(data, colWidths=[0.8 * cm, 3.8 * cm, 11.4 * cm])
tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a4a7c")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f7f7f7")),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story.append(tbl)
story.append(Spacer(1, 0.4 * cm))

story.append(P("Lógica de rastreabilidade", "H2"))
story.append(P(
    "Cada imagem publicada recebe <b>duas tags</b>: uma de ambiente "
    "(<font face='Courier'>:staging</font> ou <font face='Courier'>:prod</font>) "
    "e uma do commit SHA curto (<font face='Courier'>:sha-abc1234</font>). Isso "
    "permite promover, fazer rollback, e auditar exatamente qual commit gerou "
    "qual imagem em produção.",
    "Body",
))

story.append(P("Observação sobre o deploy", "H2"))
story.append(P(
    "Como o ambiente de execução final é a máquina local do aluno (requisito "
    "acadêmico, sem VPS), o job <font face='Courier'>deploy</font> não faz SSH "
    "para uma máquina remota — ele publica a imagem imutável no GHCR e entrega "
    "as instruções como artefato. A reprodução do deploy é 1 comando: "
    "<font face='Courier'>docker compose pull && up -d</font>.",
    "Body",
))
story.append(PageBreak())


# --- 2. DOCKER ---
story.append(P("2. Containerização com Docker", "H1"))

story.append(P("Arquitetura", "H2"))
story.append(P(
    "Três ambientes totalmente isolados via arquivos de Docker Compose "
    "distintos. Cada ambiente possui sua própria rede bridge, volume "
    "persistente para o Postgres, portas mapeadas separadas e tag de imagem:",
    "Body",
))

arch_data = [
    ["Ambiente", "Compose", "Porta API", "Porta DB", "Volume", "Rede", "Tag"],
    ["Dev", "docker-compose.yml", "8080", "5432", "pg_data_dev", "dev_net", "build local"],
    ["Staging", "docker-compose.staging.yml", "8081", "5433", "pg_data_staging", "stg_net", ":staging"],
    ["Prod", "docker-compose.prod.yml", "8080", "5432", "pg_data_prod", "prod_net", ":prod"],
]
arch_tbl = Table(arch_data, colWidths=[1.8 * cm, 3.8 * cm, 1.8 * cm, 1.7 * cm, 2.7 * cm, 1.6 * cm, 2.2 * cm])
arch_tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a4a7c")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
     [colors.white, colors.HexColor("#f3f3f3"), colors.white]),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
]))
story.append(arch_tbl)
story.append(Spacer(1, 0.5 * cm))

story.append(P("Dockerfile (multi-stage)", "H2"))
dockerfile = """FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY *.sln ./
COPY src/CidadesEsg.Api/*.csproj src/CidadesEsg.Api/
RUN dotnet restore src/CidadesEsg.Api/CidadesEsg.Api.csproj
COPY src/CidadesEsg.Api/ src/CidadesEsg.Api/
RUN dotnet publish src/CidadesEsg.Api/CidadesEsg.Api.csproj \\
    -c Release -o /app /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app .
RUN apt-get update && apt-get install -y --no-install-recommends curl
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \\
  CMD curl -f http://localhost:8080/health || exit 1
ENTRYPOINT ["dotnet", "CidadesEsg.Api.dll"]"""
story.append(code_block(dockerfile))
story.append(Spacer(1, 0.3 * cm))

story.append(P("Estratégias adotadas", "H2"))
story.append(P(
    "• <b>Multi-stage:</b> o estágio <font face='Courier'>build</font> usa o "
    "SDK completo (~800MB); o estágio final <font face='Courier'>runtime</font> "
    "usa apenas o runtime ASP.NET (~110MB). Imagem final ~85% menor.<br/>"
    "• <b>Ordem de COPY:</b> <font face='Courier'>.csproj</font> copiado antes "
    "do código-fonte — o cache do <font face='Courier'>dotnet restore</font> é "
    "reaproveitado quando só o código muda.<br/>"
    "• <b>Healthcheck nativo:</b> Docker, Compose e Kubernetes detectam "
    "automaticamente container não-pronto e evitam rotear tráfego.<br/>"
    "• <b>.dockerignore agressivo:</b> exclui <font face='Courier'>bin/obj</font>, "
    "<font face='Courier'>tests/</font>, <font face='Courier'>docs/</font>, "
    "<font face='Courier'>.git</font> — reduz o contexto enviado ao daemon.",
    "Body",
))

story.append(P("Comandos principais", "H2"))
cmds = """# Dev local
docker compose up -d --build

# Staging (pull da imagem do GHCR)
export GHCR_OWNER=artcgranja
docker login ghcr.io
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d

# Prod (mesma lógica, compose diferente)
docker compose -f docker-compose.prod.yml --env-file .env.prod -p prod up -d

# Verificação
curl http://localhost:8081/health   # staging
curl http://localhost:8080/health   # prod"""
story.append(code_block(cmds))
story.append(PageBreak())


# --- 3. PRINTS ---
story.append(P("3. Evidências de Execução", "H1"))

story.append(P("3.1 Pipeline CI/CD rodando (GitHub Actions)", "H2"))
story.append(P(
    "Página do GitHub Actions mostrando 5 execuções do workflow "
    "<font face='Courier'>CI/CD</font>, todas com status green "
    "(build + testes + push para GHCR + deploy instructions). As duas primeiras "
    "execuções correspondem à inauguração do pipeline em ambas as branches "
    "(<font face='Courier'>develop</font> → staging e "
    "<font face='Courier'>main</font> → prod).",
    "Body",
))
img1 = Image("/Users/arthurgranja/github/DevOps-FIAP/docs/evidencias/08-pipeline-actions.png",
             width=16.5 * cm, height=9.2 * cm)
story.append(img1)
story.append(P(
    "Figura 1 — GitHub Actions com 5 runs green. "
    "URL: github.com/artcgranja/DevOps-FIAP/actions",
    "Caption",
))
story.append(Spacer(1, 0.2 * cm))

story.append(P("3.2 Ambientes staging e produção funcionando", "H2"))
story.append(P(
    "Terminal mostrando (1) <font face='Courier'>docker ps</font> com os "
    "<b>4 containers rodando simultaneamente</b> — 2 APIs .NET (portas 8080 e "
    "8081) + 2 PostgreSQL (portas 5432 e 5433), todos com status "
    "<font face='Courier'>healthy</font>; (2) <font face='Courier'>curl</font> "
    "nos endpoints <font face='Courier'>/health</font> de ambos os ambientes, "
    "retornando <font face='Courier'>{\"status\":\"ok\",\"db\":\"up\"}</font>; "
    "(3) fluxo end-to-end: POST cria cidade em staging, GET retorna a lista "
    "atualizada.",
    "Body",
))
img2 = Image("/Users/arthurgranja/github/DevOps-FIAP/docs/evidencias/09-terminal-evidencias.png",
             width=16.5 * cm, height=6.2 * cm)
story.append(img2)
story.append(P(
    "Figura 2 — docker ps + healthcheck staging/prod + fluxo CRUD.",
    "Caption",
))
story.append(PageBreak())


# --- 4. DESAFIOS ---
story.append(P("4. Desafios Encontrados e Soluções", "H1"))

desafios = [
    ("Instalação do .NET SDK sem sudo",
     "O <font face='Courier'>brew install --cask dotnet-sdk</font> exige "
     "<font face='Courier'>sudo</font> via instalador .pkg. Sem acesso a "
     "terminal interativo, a instalação travava pedindo senha.",
     "Usei o script oficial da Microsoft "
     "(<font face='Courier'>dotnet-install.sh</font>) que instala em "
     "<font face='Courier'>~/.dotnet</font> sem privilégios elevados. "
     "Adicionei ao <font face='Courier'>.zshrc</font> para persistir o PATH."),
    ("Ciclo de referência na serialização JSON",
     "Ao retornar um <font face='Courier'>IndicadorEsg</font> após um POST, o "
     "EF Core já havia linkado a navegação bidirecional Cidade↔Indicadores. O "
     "<font face='Courier'>System.Text.Json</font> entrou em loop infinito e "
     "falhou com JsonException (cycle detected).",
     "Configurei <font face='Courier'>ReferenceHandler.IgnoreCycles</font> "
     "globalmente via <font face='Courier'>ConfigureHttpJsonOptions</font>. "
     "Aproveitei e adicionei <font face='Courier'>JsonStringEnumConverter</font> "
     "para serializar o enum TipoIndicador como string legível."),
    ("Hook de segurança bloqueando o workflow do GitHub Actions",
     "O hook de segurança avisou sobre interpolação direta de "
     "<font face='Courier'>${{ github.* }}</font> dentro de blocos "
     "<font face='Courier'>run:</font>, um vetor clássico de injeção em "
     "Actions quando o input vem de fonte não confiável.",
     "Refatorei todas as expressões template para serem declaradas em "
     "<font face='Courier'>env:</font> do step e consumidas como variáveis de "
     "shell entre aspas duplas. Além de passar o hook, é a boa prática oficial "
     "recomendada pela própria documentação do GitHub."),
    ("Conflito de portas e nomes entre staging e prod",
     "Rodando os dois <font face='Courier'>docker compose up</font> no mesmo "
     "host, o segundo falhava com conflito de nome de container (ambos usavam "
     "<font face='Courier'>devops-fiap-api-1</font>).",
     "Usei a flag <font face='Courier'>-p prod</font> no compose de produção "
     "para forçar um project name distinto. Assim, staging fica sob o prefixo "
     "<font face='Courier'>devops-fiap-*</font> e prod sob "
     "<font face='Courier'>prod-*</font>, com redes e volumes totalmente "
     "isolados."),
    ("Platform mismatch arm64 × amd64",
     "Imagens publicadas pelo GitHub Actions são amd64 (runner Ubuntu). "
     "Ao puxar no Mac M5 (arm64), o Docker alertava "
     "'platform does not match'.",
     "Deixei rodando via emulação (Rosetta/qemu do Docker Desktop) — "
     "é o comportamento correto para o escopo acadêmico. Em produção real, "
     "adicionaria <font face='Courier'>platforms: linux/amd64,linux/arm64</font> "
     "na action <font face='Courier'>docker/build-push-action</font> para "
     "publicar uma imagem multi-arch."),
]

for titulo, problema, solucao in desafios:
    story.append(P(f"<b>{titulo}</b>", "H2"))
    story.append(P(f"<b>Problema:</b> {problema}", "Body"))
    story.append(P(f"<b>Solução:</b> {solucao}", "Body"))
story.append(PageBreak())


# --- 5. CHECKLIST ---
story.append(P("5. Checklist de Entrega", "H1"))

check_data = [
    ["Item", "Status", "Onde conferir"],
    ["Projeto compactado em .ZIP com estrutura organizada",
     "✓",
     "CidadesEsg-FIAP-entrega.zip (raiz do repo)"],
    ["Dockerfile funcional",
     "✓",
     "Dockerfile (multi-stage, healthcheck, 110 MB)"],
    ["docker-compose.yml ou arquivos Kubernetes",
     "✓",
     "docker-compose.yml + .staging.yml + .prod.yml"],
    ["Pipeline com etapas de build, teste e deploy",
     "✓",
     ".github/workflows/ci-cd.yml (3 jobs)"],
    ["README.md com instruções e prints",
     "✓",
     "README.md na raiz"],
    ["Documentação técnica com evidências (PDF)",
     "✓",
     "Este documento"],
    ["Deploy realizado nos ambientes staging e produção",
     "✓",
     "Figuras 1 e 2 + docs/evidencias/"],
]
ck = Table(check_data, colWidths=[8 * cm, 1.5 * cm, 7 * cm])
ck.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a4a7c")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (1, 0), (1, -1), "CENTER"),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
     [colors.white, colors.HexColor("#f3f3f3")]),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(ck)
story.append(Spacer(1, 1 * cm))

story.append(P("6. Stack Técnica", "H1"))
stack = [
    ("Runtime", ".NET 8 (SDK 8.0.420 / aspnet:8.0 na runtime image)"),
    ("Framework API", "ASP.NET Core Minimal API"),
    ("ORM", "Entity Framework Core 8"),
    ("Banco de dados", "PostgreSQL 16 (Alpine)"),
    ("Testes", "xUnit + WebApplicationFactory + SQLite in-memory (6 testes)"),
    ("Containerização", "Docker (multi-stage, healthcheck nativo)"),
    ("Orquestração", "Docker Compose v2 (3 arquivos: dev / staging / prod)"),
    ("CI/CD", "GitHub Actions (.github/workflows/ci-cd.yml)"),
    ("Registry", "GitHub Container Registry — ghcr.io"),
    ("Controle de versão", "Git + duas branches (develop → staging, main → prod)"),
]
for k, v in stack:
    story.append(P(f"<b>{k}:</b> {v}", "Body"))

doc.build(story)
print(f"PDF gerado: {OUT}")
