# Design — Cidades ESG Inteligentes (DevOps FIAP)

**Data:** 2026-04-21
**Aluno:** Arthur Cavalcanti Granja (RM 560650)
**Disciplina:** Navegando pelo mundo DevOps — FIAP
**Repositório:** `DevOps-FIAP`

## Objetivo

Entregar a atividade avaliativa de DevOps da FIAP: construir uma API ESG simples em .NET 8, containerizar, orquestrar via docker-compose em dois ambientes (staging e produção), e automatizar o ciclo build → test → deploy com GitHub Actions.

O foco da atividade é **DevOps**, não o app em si. O domínio ESG serve apenas para atender o requisito temático ("Cidades ESG Inteligentes").

## Não-objetivos

- Aplicação com domínio complexo, autenticação, ou UI
- Deploy em nuvem (Azure, Render, AWS) — optou-se por docker-compose local
- Kubernetes (pode ser adicionado depois como extensão)
- GitFlow completo — usa apenas `main` (prod) e `develop` (staging)
- Cobertura de testes alta — mínimo que satisfaça o requisito "execução de testes existentes"

## Stack

| Camada | Escolha |
|---|---|
| Runtime | .NET 8 |
| Framework API | ASP.NET Core Minimal API |
| ORM | Entity Framework Core 8 |
| Banco | PostgreSQL 16 |
| Testes | xUnit + `WebApplicationFactory` |
| Container | Docker (multi-stage) |
| Orquestração | Docker Compose (2 arquivos: staging, prod) |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry (GHCR) |

## Arquitetura

```
┌───────────────────────────────────────────────┐
│  GitHub Actions (CI/CD)                        │
│  build → test → docker build → push GHCR       │
└───────────────┬───────────────────────────────┘
                │
                ▼
         ┌──────────────┐
         │    GHCR      │  tags: :staging, :prod, :<sha>
         └──────┬───────┘
                │ docker compose pull
     ┌──────────┴──────────┐
     ▼                     ▼
┌─────────┐          ┌─────────┐
│STAGING  │          │  PROD   │
│api:8081 │          │api:8080 │
│db:5433  │          │db:5432  │
│pg_data_ │          │pg_data_ │
│ staging │          │  prod   │
│stg_net  │          │prod_net │
└─────────┘          └─────────┘
```

**Isolamento entre ambientes:**
- Portas distintas (8080/8081 para API, 5432/5433 para DB)
- Volumes separados (`pg_data_staging`, `pg_data_prod`)
- Redes bridge separadas (`stg_net`, `prod_net`)
- Tags de imagem separadas no GHCR

## Domínio

**Entidades:**

```csharp
Cidade {
  int Id
  string Nome
  string Estado
  DateTime CriadoEm
}

IndicadorEsg {
  int Id
  int CidadeId
  TipoIndicador Tipo
  decimal Valor
  string Unidade
  DateTime DataMedicao
}

enum TipoIndicador {
  ConsumoEnergiaKwh,
  EmissaoCo2Ton,
  AreaVerdePerc,
  ColetaSeletivaPerc
}
```

**Endpoints (Minimal API):**

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Healthcheck — retorna 200 + status do DB |
| GET | `/cidades` | Lista cidades |
| POST | `/cidades` | Cria cidade (body: `Nome`, `Estado`) |
| GET | `/cidades/{id}` | Detalhe da cidade |
| GET | `/cidades/{id}/indicadores` | Lista indicadores da cidade |
| POST | `/cidades/{id}/indicadores` | Adiciona indicador |

**Migrations:** gerenciadas via `dotnet ef migrations`. A API aplica migrations pendentes no startup (`context.Database.Migrate()`).

## Testes

Projeto `CidadesEsg.Api.Tests` (xUnit) com:

- `HealthcheckTests` — `GET /health` retorna 200
- `CidadesEndpointsTests` — POST cria, GET lista, GET 404 quando id não existe
- `IndicadoresEndpointsTests` — POST adiciona vinculado à cidade, GET filtra por cidade

Usa `WebApplicationFactory<Program>` com SQLite in-memory para isolar os testes do Postgres real (mais rápido no CI, sem dependência de container em test).

## Containerização

**Dockerfile (multi-stage):**

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY *.sln ./
COPY src/CidadesEsg.Api/*.csproj src/CidadesEsg.Api/
COPY tests/CidadesEsg.Api.Tests/*.csproj tests/CidadesEsg.Api.Tests/
RUN dotnet restore
COPY . .
RUN dotnet publish src/CidadesEsg.Api -c Release -o /app /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app .
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8080/health || exit 1
ENTRYPOINT ["dotnet", "CidadesEsg.Api.dll"]
```

**Arquivos de Compose:**

- `docker-compose.yml` — desenvolvimento local. Usa `build:` (não imagem do registry). Porta API 8080, DB 5432.
- `docker-compose.staging.yml` — usa `image: ghcr.io/<owner>/cidades-esg-api:staging`. Porta API 8081, DB 5433. Volume `pg_data_staging`. Rede `stg_net`.
- `docker-compose.prod.yml` — usa `image: ghcr.io/<owner>/cidades-esg-api:prod`. Porta API 8080, DB 5432. Volume `pg_data_prod`. Rede `prod_net`.

**Variáveis de ambiente (`.env.example`):**

```
POSTGRES_USER=esg
POSTGRES_PASSWORD=changeme
POSTGRES_DB=cidades_esg
ASPNETCORE_ENVIRONMENT=Production
ConnectionStrings__Default=Host=db;Port=5432;Database=cidades_esg;Username=esg;Password=changeme
```

Cada ambiente tem seu próprio arquivo `.env` (não commitado): `.env.staging`, `.env.prod`.

## Pipeline CI/CD

**Arquivo único:** `.github/workflows/ci-cd.yml`

**Triggers:**
- Push em `main` → pipeline completo + publica imagem `:prod` + emite instruções de deploy prod
- Push em `develop` → pipeline completo + publica imagem `:staging` + emite instruções de deploy staging
- PR em `main` → apenas build + test (sem push, sem deploy)

**Jobs:**

```
1. build-test
   ├─ setup-dotnet@v4 (.NET 8)
   ├─ dotnet restore
   ├─ dotnet build --no-restore -c Release
   └─ dotnet test --no-build --logger trx
      └─ upload test results (artefato)

2. docker-build-push  (only main/develop)
   ├─ needs: build-test
   ├─ docker/login-action → GHCR (GITHUB_TOKEN)
   ├─ docker/metadata-action (gera tags)
   └─ docker/build-push-action
      └─ tags: :staging OR :prod, + :sha-<short>

3. deploy  (only main/develop)
   ├─ needs: docker-build-push
   └─ gera artefato "deploy-instructions-<env>.txt"
      contendo comandos:
        docker compose -f docker-compose.<env>.yml pull
        docker compose -f docker-compose.<env>.yml up -d
```

**Nota sobre "deploy":** como o deploy é local (Mac do aluno), o job `deploy` não executa em máquina remota — ele apenas gera as instruções como artefato. O aluno roda os comandos manualmente para coletar evidências. Isso satisfaz o requisito "deploy automatizado em dois ambientes" no espírito da atividade acadêmica.

## Estrutura do repositório

```
DevOps-FIAP/
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-04-21-cidades-esg-devops-design.md
├── src/
│   └── CidadesEsg.Api/
│       ├── Program.cs
│       ├── CidadesEsg.Api.csproj
│       ├── Endpoints/
│       ├── Domain/
│       ├── Data/
│       └── Migrations/
├── tests/
│   └── CidadesEsg.Api.Tests/
│       ├── CidadesEsg.Api.Tests.csproj
│       ├── HealthcheckTests.cs
│       ├── CidadesEndpointsTests.cs
│       └── IndicadoresEndpointsTests.cs
├── Dockerfile
├── docker-compose.yml
├── docker-compose.staging.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
├── .dockerignore
├── CidadesEsg.sln
└── README.md
```

## Evidências para entrega

**Para o README.md e PDF:**

1. Print do pipeline GitHub Actions verde (3 jobs: build-test, docker-build-push, deploy)
2. Print da imagem publicada no GHCR (`ghcr.io/<owner>/cidades-esg-api`)
3. Prints de `docker compose -f docker-compose.staging.yml up` rodando — containers healthy
4. Prints de `docker compose -f docker-compose.prod.yml up` rodando — containers healthy
5. `curl` responses de cada ambiente:
   - `GET http://localhost:8081/health` (staging)
   - `GET http://localhost:8080/health` (prod)
   - `POST http://localhost:8081/cidades` + `GET http://localhost:8081/cidades` (fluxo end-to-end em staging)
6. Print do `docker ps` mostrando os 4 containers (2 API + 2 DB) rodando simultaneamente em redes distintas

**Estrutura do PDF de documentação:**

1. Título + nome do aluno + RM
2. Descrição do pipeline (ferramenta, etapas, lógica)
3. Docker: arquitetura, comandos usados, imagem criada
4. Prints do pipeline rodando (build, testes, deploy)
5. Prints dos ambientes staging e produção funcionando
6. Desafios encontrados e como foram resolvidos
7. Checklist de entrega (do enunciado) preenchido

## Checklist da atividade (enunciado FIAP)

| Item | Como será atendido |
|---|---|
| Projeto compactado em .ZIP com estrutura organizada | `git archive` ou zip manual no final |
| Dockerfile funcional | `Dockerfile` multi-stage na raiz |
| docker-compose.yml ou arquivos Kubernetes | 3 arquivos compose (dev, staging, prod) |
| Pipeline com etapas de build, teste e deploy | `ci-cd.yml` com 3 jobs |
| README.md com instruções e prints | Seção dedicada com passos e prints |
| Documentação técnica com evidências (PDF ou PPT) | PDF gerado ao final |
| Deploy realizado nos ambientes staging e produção | 2 composes distintos + evidências |

## Decisões-chave

| # | Decisão | Por quê |
|---|---|---|
| 1 | .NET 8 em vez de Java Spring | Scaffold mais rápido, imagem menor, melhor DX no Mac M5 |
| 2 | Minimal API em vez de Controllers | Menos boilerplate, suficiente pro escopo |
| 3 | PostgreSQL em vez de SQL Server | Imagem oficial menor, sem fricção de licença |
| 4 | Docker Compose local em vez de cloud (Render/Azure) | Zero custo, zero setup de conta, atende enunciado |
| 5 | SQLite in-memory nos testes em vez de Testcontainers | CI mais rápido, sem dependência de Docker em test |
| 6 | GHCR em vez de Docker Hub | Integração nativa com GitHub Actions, sem login extra |
| 7 | Pular Kubernetes no escopo inicial | Enunciado diz "ou" — compose satisfaz. Pode adicionar depois. |

## Riscos e mitigações

| Risco | Mitigação |
|---|---|
| Conflito de portas no Mac (8080/8081/5432/5433 em uso) | Checar portas antes; se ocupado, ajustar no compose |
| Imagem .NET grande inflando build no CI | Multi-stage + `.dockerignore` agressivo (bin/obj, tests, docs) |
| Migration falhando no primeiro `up` | `context.Database.Migrate()` no startup + healthcheck com retry implícito do compose |
| Token GHCR sem permissão de push | Usar `GITHUB_TOKEN` default com `permissions: packages: write` no workflow |
| PR em main disparando push pra GHCR indevidamente | Guard `if: github.event_name == 'push'` nos jobs de build-push e deploy |

## Próximos passos

Após aprovação deste design, próxima etapa é invocar `superpowers:writing-plans` para gerar plano de implementação passo a passo (estrutura do projeto .NET, Dockerfile, composes, workflow, testes, README, coleta de evidências).
