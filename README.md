# Projeto — Cidades ESG Inteligentes

API REST em .NET 8 para gerenciar cidades e indicadores ESG (Environmental, Social, Governance), com pipeline CI/CD completo e deploy containerizado em dois ambientes (staging e produção).

Trabalho avaliativo da disciplina **Navegando pelo mundo DevOps** — FIAP.

**Autor:** Arthur Cavalcanti Granja — RM 560650
**Repositório:** https://github.com/artcgranja/DevOps-FIAP

---

## Como executar localmente com Docker

**Pré-requisitos:** Docker Desktop 24+ com Compose v2.

```bash
cp .env.example .env
docker compose up -d --build
```

A API sobe em `http://localhost:8080`. Teste:

```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/cidades \
  -H "Content-Type: application/json" \
  -d '{"nome":"Curitiba","estado":"PR"}'
curl http://localhost:8080/cidades
```

Swagger UI (modo Development): `http://localhost:8080/swagger`.

Para derrubar: `docker compose down -v`.

---

## Pipeline CI/CD

**Ferramenta:** GitHub Actions (`.github/workflows/ci-cd.yml`).

**Gatilhos:**
- Push em `develop` → pipeline completo, publica imagem `:staging` no GHCR
- Push em `main` → pipeline completo, publica imagem `:prod` no GHCR
- PR em `main` → apenas build + testes (sem push, sem deploy)

**Jobs:**

| # | Job | O que faz |
|---|---|---|
| 1 | `build-test` | `dotnet restore` + `dotnet build` + `dotnet test` (6 testes xUnit) + upload dos resultados |
| 2 | `docker-build-push` | Login no GHCR, build multi-arch da imagem, push com tags `:staging`/`:prod` + `:sha-<7>` |
| 3 | `deploy` | Gera artefato `deploy-instructions-<env>.txt` com comandos de deploy local |

**Registry:** https://github.com/artcgranja?tab=packages

**Por que o deploy é via instruções e não SSH:** o ambiente de execução final é o próprio Mac do aluno (requisito acadêmico, sem VPS). A pipeline publica a imagem imutável no GHCR e entrega os comandos `docker compose pull && up` como artefato — a reprodução é 1 comando no terminal.

---

## Containerização

### Dockerfile (multi-stage)

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY *.sln ./
COPY src/CidadesEsg.Api/*.csproj src/CidadesEsg.Api/
RUN dotnet restore src/CidadesEsg.Api/CidadesEsg.Api.csproj
COPY src/CidadesEsg.Api/ src/CidadesEsg.Api/
RUN dotnet publish src/CidadesEsg.Api/CidadesEsg.Api.csproj \
    -c Release -o /app /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app .
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
ENTRYPOINT ["dotnet", "CidadesEsg.Api.dll"]
```

**Estratégias adotadas:**
- **Multi-stage:** SDK só no `build`, runtime final usa `aspnet:8.0` (menor, sem compilador)
- **Restore antes do COPY do código:** camada de cache reaproveitada quando só código muda
- **Healthcheck nativo no Docker:** Compose e K8s detectam container "não-pronto" antes de rotear tráfego
- **`.dockerignore` agressivo:** exclui `bin/obj`, `tests/`, `docs/`, `.git` — reduz contexto e imagem

### Orquestração — três ambientes isolados

| Ambiente | Compose file | Porta API | Porta DB | Volume | Rede | Imagem |
|---|---|---|---|---|---|---|
| Dev | `docker-compose.yml` | 8080 | 5432 | `pg_data_dev` | `dev_net` | build local |
| Staging | `docker-compose.staging.yml` | 8081 | 5433 | `pg_data_staging` | `stg_net` | `ghcr.io/<owner>/cidades-esg-api:staging` |
| Prod | `docker-compose.prod.yml` | 8080 | 5432 | `pg_data_prod` | `prod_net` | `ghcr.io/<owner>/cidades-esg-api:prod` |

**Rodar staging e prod simultaneamente:**
```bash
export GHCR_OWNER=artcgranja
docker login ghcr.io

docker compose -f docker-compose.staging.yml --env-file .env.staging up -d
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

curl http://localhost:8081/health   # staging
curl http://localhost:8080/health   # prod
```

---

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Healthcheck + status do DB |
| GET | `/cidades` | Lista cidades |
| POST | `/cidades` | Cria cidade |
| GET | `/cidades/{id}` | Detalhe da cidade |
| GET | `/cidades/{id}/indicadores` | Lista indicadores da cidade |
| POST | `/cidades/{id}/indicadores` | Adiciona indicador |

Tipos de indicador: `ConsumoEnergiaKwh`, `EmissaoCo2Ton`, `AreaVerdePerc`, `ColetaSeletivaPerc`.

---

## Prints do funcionamento

Evidências em `docs/evidencias/` (ou PDF anexo à entrega):

- `01-pipeline-verde.png` — Pipeline GitHub Actions com 3 jobs green
- `02-ghcr-imagens.png` — Imagens publicadas no GitHub Container Registry
- `03-staging-up.png` — `docker compose ... staging up`
- `04-prod-up.png` — `docker compose ... prod up`
- `05-docker-ps.png` — `docker ps` com 4 containers rodando simultaneamente
- `06-curl-health.png` — healthchecks OK em ambos os ambientes
- `07-curl-fluxo.png` — POST/GET cidades + indicadores end-to-end

---

## Tecnologias utilizadas

- **Runtime:** .NET 8
- **API:** ASP.NET Core Minimal API
- **ORM:** Entity Framework Core 8
- **Banco:** PostgreSQL 16 (Alpine)
- **Testes:** xUnit + `WebApplicationFactory` + SQLite in-memory
- **Container:** Docker (multi-stage)
- **Orquestração:** Docker Compose v2
- **CI/CD:** GitHub Actions
- **Registry:** GitHub Container Registry (GHCR)

---

## Checklist de entrega

| Item | Status |
|---|---|
| Projeto compactado em `.ZIP` com estrutura organizada | ☑ |
| Dockerfile funcional | ☑ |
| `docker-compose.yml` + staging + prod | ☑ |
| Pipeline com etapas de build, teste e deploy | ☑ |
| `README.md` com instruções e prints | ☑ |
| Documentação técnica com evidências (PDF) | ☑ |
| Deploy realizado nos ambientes staging e produção | ☑ |

---

## Como rodar os testes

```bash
dotnet test
```

Saída esperada: `Passed! - Failed: 0, Passed: 6, Skipped: 0, Total: 6`.
