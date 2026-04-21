# Evidências de execução

Todas as evidências em texto foram capturadas em `2026-04-21` no ambiente do aluno.
Para a entrega da FIAP, capture **screenshots** dos comandos correspondentes e salve como `.png` nesta pasta.

## Índice

| Arquivo | O que comprova |
|---|---|
| `01-ambientes-up.txt` | `docker ps` + `network ls` + `volume ls` com os 4 containers (staging + prod) rodando simultaneamente em redes/volumes isolados |
| `02-healthcheck.txt` | `GET /health` retornando 200 em `localhost:8081` (staging) e `localhost:8080` (prod) |
| `03-fluxo-staging.txt` | Fluxo E2E: POST cidade → POST indicador → GET cidades → GET indicadores |
| `04-isolamento.txt` | Prova que prod está vazio enquanto staging tem 2 cidades — DBs isolados |
| `05-pipeline.txt` | Listagem dos runs do GitHub Actions (3 runs green) + link público |
| `06-testes.txt` | `dotnet test` — 6/6 passando |
| `07-ghcr.txt` | `docker inspect` das imagens `:staging` e `:prod` pulladas do GHCR |

## Para o PDF de entrega

Sugestão de screenshots (abrir cada arquivo .txt no terminal e printar):

1. **01-pipeline-verde.png** — página do Actions no GitHub, 3 jobs green
   URL: https://github.com/artcgranja/DevOps-FIAP/actions
2. **02-ghcr-imagens.png** — página do package
   URL: https://github.com/users/artcgranja/packages/container/package/cidades-esg-api
3. **03-docker-ps.png** — `docker ps` mostrando 4 containers
4. **04-curl-health.png** — 2 `curl` de healthcheck side-by-side
5. **05-curl-fluxo.png** — POST + GET cidades no staging
6. **06-isolamento.png** — evidência de que prod ≠ staging
7. **07-testes-locais.png** — `dotnet test` green

## Links públicos

- Repo: https://github.com/artcgranja/DevOps-FIAP
- Actions: https://github.com/artcgranja/DevOps-FIAP/actions
- GHCR: https://github.com/users/artcgranja/packages/container/package/cidades-esg-api
