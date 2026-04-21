# Cidades ESG DevOps FIAP — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build .NET 8 ESG API, containerize with Docker, orchestrate via docker-compose in 2 environments (staging/prod), and automate build/test/deploy via GitHub Actions — satisfying FIAP DevOps assignment.

**Architecture:** ASP.NET Core Minimal API + PostgreSQL, image published to GHCR, two compose files for staging/prod with isolated networks/volumes/ports, CI/CD pipeline triggered by push to `develop` (staging) and `main` (prod).

**Tech Stack:** .NET 8, ASP.NET Core Minimal API, Entity Framework Core, PostgreSQL 16, xUnit, Docker, Docker Compose, GitHub Actions, GHCR.

**Spec reference:** [docs/superpowers/specs/2026-04-21-cidades-esg-devops-design.md](../specs/2026-04-21-cidades-esg-devops-design.md)

---

## File Structure

```
DevOps-FIAP/
├── .github/workflows/ci-cd.yml
├── src/CidadesEsg.Api/
│   ├── CidadesEsg.Api.csproj
│   ├── Program.cs
│   ├── Domain/{Cidade,IndicadorEsg,TipoIndicador}.cs
│   ├── Data/AppDbContext.cs
│   ├── Endpoints/{Health,Cidades,Indicadores}Endpoints.cs
│   ├── Migrations/ (generated)
│   ├── appsettings.json
│   └── appsettings.Development.json
├── tests/CidadesEsg.Api.Tests/
│   ├── CidadesEsg.Api.Tests.csproj
│   ├── ApiFactory.cs
│   ├── HealthcheckTests.cs
│   ├── CidadesEndpointsTests.cs
│   └── IndicadoresEndpointsTests.cs
├── CidadesEsg.sln
├── Dockerfile
├── .dockerignore
├── docker-compose.yml           (dev: build:, ports 8080/5432)
├── docker-compose.staging.yml   (image :staging, ports 8081/5433)
├── docker-compose.prod.yml      (image :prod, ports 8080/5432)
├── .env.example
├── .gitignore
└── README.md
```

---

## Task 1: Bootstrap solution, API project, and test project

**Files:**
- Create: `CidadesEsg.sln`
- Create: `src/CidadesEsg.Api/CidadesEsg.Api.csproj`
- Create: `tests/CidadesEsg.Api.Tests/CidadesEsg.Api.Tests.csproj`
- Create: `.gitignore`

- [ ] **Step 1: Verify .NET 8 SDK installed**

Run: `dotnet --version`
Expected: `8.0.xxx` (any 8.0 patch). If not installed, `brew install --cask dotnet-sdk`.

- [ ] **Step 2: Create solution and projects**

Run from repo root:
```bash
cd /Users/arthurgranja/github/DevOps-FIAP
dotnet new sln -n CidadesEsg
dotnet new webapi -n CidadesEsg.Api -o src/CidadesEsg.Api --no-https --use-minimal-apis
dotnet new xunit -n CidadesEsg.Api.Tests -o tests/CidadesEsg.Api.Tests
dotnet sln add src/CidadesEsg.Api/CidadesEsg.Api.csproj
dotnet sln add tests/CidadesEsg.Api.Tests/CidadesEsg.Api.Tests.csproj
dotnet add tests/CidadesEsg.Api.Tests reference src/CidadesEsg.Api
```

Expected: solution file and two project folders created.

- [ ] **Step 3: Add NuGet packages to API project**

Run:
```bash
cd src/CidadesEsg.Api
dotnet add package Microsoft.EntityFrameworkCore --version 8.0.10
dotnet add package Microsoft.EntityFrameworkCore.Design --version 8.0.10
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL --version 8.0.10
dotnet add package Microsoft.EntityFrameworkCore.Sqlite --version 8.0.10
cd ../..
```

Expected: packages added to `CidadesEsg.Api.csproj`.

- [ ] **Step 4: Add NuGet packages to test project**

Run:
```bash
cd tests/CidadesEsg.Api.Tests
dotnet add package Microsoft.AspNetCore.Mvc.Testing --version 8.0.10
dotnet add package Microsoft.EntityFrameworkCore.Sqlite --version 8.0.10
cd ../..
```

- [ ] **Step 5: Create `.gitignore`**

Create `/Users/arthurgranja/github/DevOps-FIAP/.gitignore`:
```
# .NET
bin/
obj/
out/
*.user
*.suo
*.DotSettings.user

# IDE
.vs/
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Env
.env
.env.staging
.env.prod
!.env.example

# Test
TestResults/
coverage/
*.trx
```

- [ ] **Step 6: Build entire solution to verify scaffold**

Run: `dotnet build`
Expected: `Build succeeded. 0 Warning(s) 0 Error(s)`.

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "chore: bootstrap .NET 8 solution with API and test projects"
```

---

## Task 2: Domain entities

**Files:**
- Create: `src/CidadesEsg.Api/Domain/TipoIndicador.cs`
- Create: `src/CidadesEsg.Api/Domain/Cidade.cs`
- Create: `src/CidadesEsg.Api/Domain/IndicadorEsg.cs`

- [ ] **Step 1: Create `TipoIndicador.cs`**

```csharp
namespace CidadesEsg.Api.Domain;

public enum TipoIndicador
{
    ConsumoEnergiaKwh,
    EmissaoCo2Ton,
    AreaVerdePerc,
    ColetaSeletivaPerc
}
```

- [ ] **Step 2: Create `Cidade.cs`**

```csharp
namespace CidadesEsg.Api.Domain;

public class Cidade
{
    public int Id { get; set; }
    public string Nome { get; set; } = string.Empty;
    public string Estado { get; set; } = string.Empty;
    public DateTime CriadoEm { get; set; } = DateTime.UtcNow;
    public List<IndicadorEsg> Indicadores { get; set; } = new();
}
```

- [ ] **Step 3: Create `IndicadorEsg.cs`**

```csharp
namespace CidadesEsg.Api.Domain;

public class IndicadorEsg
{
    public int Id { get; set; }
    public int CidadeId { get; set; }
    public Cidade? Cidade { get; set; }
    public TipoIndicador Tipo { get; set; }
    public decimal Valor { get; set; }
    public string Unidade { get; set; } = string.Empty;
    public DateTime DataMedicao { get; set; }
}
```

- [ ] **Step 4: Build to verify**

Run: `dotnet build`
Expected: build succeeds.

- [ ] **Step 5: Commit**

```bash
git add src/CidadesEsg.Api/Domain
git commit -m "feat: add ESG domain entities (Cidade, IndicadorEsg)"
```

---

## Task 3: DbContext + DI wiring

**Files:**
- Create: `src/CidadesEsg.Api/Data/AppDbContext.cs`
- Modify: `src/CidadesEsg.Api/Program.cs`
- Modify: `src/CidadesEsg.Api/appsettings.json`

- [ ] **Step 1: Create `AppDbContext.cs`**

```csharp
using CidadesEsg.Api.Domain;
using Microsoft.EntityFrameworkCore;

namespace CidadesEsg.Api.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<Cidade> Cidades => Set<Cidade>();
    public DbSet<IndicadorEsg> Indicadores => Set<IndicadorEsg>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.Entity<Cidade>(e =>
        {
            e.Property(x => x.Nome).HasMaxLength(120).IsRequired();
            e.Property(x => x.Estado).HasMaxLength(2).IsRequired();
        });

        b.Entity<IndicadorEsg>(e =>
        {
            e.Property(x => x.Unidade).HasMaxLength(20).IsRequired();
            e.Property(x => x.Valor).HasPrecision(18, 4);
            e.HasOne(x => x.Cidade)
             .WithMany(c => c.Indicadores)
             .HasForeignKey(x => x.CidadeId)
             .OnDelete(DeleteBehavior.Cascade);
        });
    }
}
```

- [ ] **Step 2: Replace `Program.cs`**

Overwrite `src/CidadesEsg.Api/Program.cs`:
```csharp
using CidadesEsg.Api.Data;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

var conn = builder.Configuration.GetConnectionString("Default")
    ?? "Host=localhost;Port=5432;Database=cidades_esg;Username=esg;Password=changeme";

builder.Services.AddDbContext<AppDbContext>(opt => opt.UseNpgsql(conn));
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    if (db.Database.IsRelational())
        db.Database.Migrate();
}

app.Run();

public partial class Program { }
```

- [ ] **Step 3: Update `appsettings.json`**

Overwrite `src/CidadesEsg.Api/appsettings.json`:
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*",
  "ConnectionStrings": {
    "Default": "Host=db;Port=5432;Database=cidades_esg;Username=esg;Password=changeme"
  }
}
```

- [ ] **Step 4: Delete the default `WeatherForecast` artifacts**

Run:
```bash
rm -f src/CidadesEsg.Api/WeatherForecast.cs
```
(If `dotnet new webapi --use-minimal-apis` didn't create one, skip.)

- [ ] **Step 5: Build**

Run: `dotnet build`
Expected: build succeeds.

- [ ] **Step 6: Commit**

```bash
git add src/CidadesEsg.Api
git commit -m "feat: add AppDbContext with Postgres provider and migration on startup"
```

---

## Task 4: Test fixture using SQLite in-memory

**Files:**
- Create: `tests/CidadesEsg.Api.Tests/ApiFactory.cs`

- [ ] **Step 1: Create `ApiFactory.cs`**

```csharp
using CidadesEsg.Api.Data;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Data.Sqlite;

namespace CidadesEsg.Api.Tests;

public class ApiFactory : WebApplicationFactory<Program>
{
    private SqliteConnection? _connection;

    protected override void ConfigureWebHost(Microsoft.AspNetCore.Hosting.IWebHostBuilder builder)
    {
        builder.UseEnvironment("Testing");

        builder.ConfigureServices(services =>
        {
            var descriptor = services.Single(d => d.ServiceType == typeof(DbContextOptions<AppDbContext>));
            services.Remove(descriptor);

            _connection = new SqliteConnection("DataSource=:memory:");
            _connection.Open();

            services.AddDbContext<AppDbContext>(opt => opt.UseSqlite(_connection));

            using var sp = services.BuildServiceProvider();
            using var scope = sp.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            db.Database.EnsureCreated();
        });
    }

    protected override void Dispose(bool disposing)
    {
        _connection?.Dispose();
        base.Dispose(disposing);
    }
}
```

- [ ] **Step 2: Add Sqlite package to tests (already done in Task 1, verify)**

Run: `grep -q "Microsoft.EntityFrameworkCore.Sqlite" tests/CidadesEsg.Api.Tests/CidadesEsg.Api.Tests.csproj && echo OK`
Expected: `OK`. If not, `cd tests/CidadesEsg.Api.Tests && dotnet add package Microsoft.EntityFrameworkCore.Sqlite --version 8.0.10`.

- [ ] **Step 3: Build**

Run: `dotnet build`
Expected: build succeeds.

- [ ] **Step 4: Commit**

```bash
git add tests/CidadesEsg.Api.Tests
git commit -m "test: add WebApplicationFactory fixture with SQLite in-memory"
```

---

## Task 5: Healthcheck endpoint (TDD)

**Files:**
- Create: `tests/CidadesEsg.Api.Tests/HealthcheckTests.cs`
- Create: `src/CidadesEsg.Api/Endpoints/HealthEndpoints.cs`
- Modify: `src/CidadesEsg.Api/Program.cs`

- [ ] **Step 1: Write failing test**

Create `tests/CidadesEsg.Api.Tests/HealthcheckTests.cs`:
```csharp
using System.Net;

namespace CidadesEsg.Api.Tests;

public class HealthcheckTests : IClassFixture<ApiFactory>
{
    private readonly ApiFactory _factory;
    public HealthcheckTests(ApiFactory factory) => _factory = factory;

    [Fact]
    public async Task Get_Health_Returns200()
    {
        var client = _factory.CreateClient();
        var resp = await client.GetAsync("/health");
        Assert.Equal(HttpStatusCode.OK, resp.StatusCode);
    }
}
```

- [ ] **Step 2: Run and verify it fails**

Run: `dotnet test --filter HealthcheckTests`
Expected: FAIL (404 Not Found, since `/health` not mapped yet).

- [ ] **Step 3: Implement `HealthEndpoints.cs`**

Create `src/CidadesEsg.Api/Endpoints/HealthEndpoints.cs`:
```csharp
using CidadesEsg.Api.Data;
using Microsoft.EntityFrameworkCore;

namespace CidadesEsg.Api.Endpoints;

public static class HealthEndpoints
{
    public static IEndpointRouteBuilder MapHealth(this IEndpointRouteBuilder app)
    {
        app.MapGet("/health", async (AppDbContext db) =>
        {
            var dbOk = await db.Database.CanConnectAsync();
            return Results.Ok(new { status = "ok", db = dbOk ? "up" : "down" });
        });
        return app;
    }
}
```

- [ ] **Step 4: Wire into `Program.cs`**

In `src/CidadesEsg.Api/Program.cs`, add `using CidadesEsg.Api.Endpoints;` at top and `app.MapHealth();` right before `app.Run();`. Final relevant section:
```csharp
using CidadesEsg.Api.Endpoints;
// ... existing code ...
app.MapHealth();
app.Run();
```

- [ ] **Step 5: Run test and verify pass**

Run: `dotnet test --filter HealthcheckTests`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/CidadesEsg.Api/Endpoints/HealthEndpoints.cs src/CidadesEsg.Api/Program.cs tests/CidadesEsg.Api.Tests/HealthcheckTests.cs
git commit -m "feat: add /health endpoint with DB connectivity check"
```

---

## Task 6: Cidades CRUD endpoints (TDD)

**Files:**
- Create: `tests/CidadesEsg.Api.Tests/CidadesEndpointsTests.cs`
- Create: `src/CidadesEsg.Api/Endpoints/CidadesEndpoints.cs`
- Modify: `src/CidadesEsg.Api/Program.cs`

- [ ] **Step 1: Write failing tests**

Create `tests/CidadesEsg.Api.Tests/CidadesEndpointsTests.cs`:
```csharp
using System.Net;
using System.Net.Http.Json;

namespace CidadesEsg.Api.Tests;

public class CidadesEndpointsTests : IClassFixture<ApiFactory>
{
    private readonly ApiFactory _factory;
    public CidadesEndpointsTests(ApiFactory factory) => _factory = factory;

    record NovaCidadeDto(string Nome, string Estado);
    record CidadeDto(int Id, string Nome, string Estado);

    [Fact]
    public async Task Post_Cidade_CreatesAndReturns201()
    {
        var client = _factory.CreateClient();
        var resp = await client.PostAsJsonAsync("/cidades", new NovaCidadeDto("Curitiba", "PR"));
        Assert.Equal(HttpStatusCode.Created, resp.StatusCode);
        var body = await resp.Content.ReadFromJsonAsync<CidadeDto>();
        Assert.NotNull(body);
        Assert.Equal("Curitiba", body!.Nome);
        Assert.True(body.Id > 0);
    }

    [Fact]
    public async Task Get_Cidades_ReturnsList()
    {
        var client = _factory.CreateClient();
        await client.PostAsJsonAsync("/cidades", new NovaCidadeDto("Recife", "PE"));
        var resp = await client.GetAsync("/cidades");
        resp.EnsureSuccessStatusCode();
        var list = await resp.Content.ReadFromJsonAsync<List<CidadeDto>>();
        Assert.NotNull(list);
        Assert.Contains(list!, c => c.Nome == "Recife");
    }

    [Fact]
    public async Task Get_Cidade_ById_NotFound_Returns404()
    {
        var client = _factory.CreateClient();
        var resp = await client.GetAsync("/cidades/99999");
        Assert.Equal(HttpStatusCode.NotFound, resp.StatusCode);
    }
}
```

- [ ] **Step 2: Run and verify they fail**

Run: `dotnet test --filter CidadesEndpointsTests`
Expected: FAIL (404 on POST/GET, endpoints not mapped).

- [ ] **Step 3: Implement `CidadesEndpoints.cs`**

Create `src/CidadesEsg.Api/Endpoints/CidadesEndpoints.cs`:
```csharp
using CidadesEsg.Api.Data;
using CidadesEsg.Api.Domain;
using Microsoft.EntityFrameworkCore;

namespace CidadesEsg.Api.Endpoints;

public static class CidadesEndpoints
{
    public record NovaCidadeDto(string Nome, string Estado);

    public static IEndpointRouteBuilder MapCidades(this IEndpointRouteBuilder app)
    {
        var g = app.MapGroup("/cidades");

        g.MapGet("", async (AppDbContext db) =>
            Results.Ok(await db.Cidades.OrderBy(c => c.Nome).ToListAsync()));

        g.MapGet("/{id:int}", async (int id, AppDbContext db) =>
        {
            var c = await db.Cidades.FindAsync(id);
            return c is null ? Results.NotFound() : Results.Ok(c);
        });

        g.MapPost("", async (NovaCidadeDto dto, AppDbContext db) =>
        {
            var c = new Cidade { Nome = dto.Nome, Estado = dto.Estado };
            db.Cidades.Add(c);
            await db.SaveChangesAsync();
            return Results.Created($"/cidades/{c.Id}", c);
        });

        return app;
    }
}
```

- [ ] **Step 4: Wire into `Program.cs`**

Add `app.MapCidades();` right after `app.MapHealth();`.

- [ ] **Step 5: Run and verify pass**

Run: `dotnet test --filter CidadesEndpointsTests`
Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/CidadesEsg.Api/Endpoints/CidadesEndpoints.cs src/CidadesEsg.Api/Program.cs tests/CidadesEsg.Api.Tests/CidadesEndpointsTests.cs
git commit -m "feat: add /cidades CRUD endpoints"
```

---

## Task 7: Indicadores endpoints (TDD)

**Files:**
- Create: `tests/CidadesEsg.Api.Tests/IndicadoresEndpointsTests.cs`
- Create: `src/CidadesEsg.Api/Endpoints/IndicadoresEndpoints.cs`
- Modify: `src/CidadesEsg.Api/Program.cs`

- [ ] **Step 1: Write failing tests**

Create `tests/CidadesEsg.Api.Tests/IndicadoresEndpointsTests.cs`:
```csharp
using System.Net;
using System.Net.Http.Json;

namespace CidadesEsg.Api.Tests;

public class IndicadoresEndpointsTests : IClassFixture<ApiFactory>
{
    private readonly ApiFactory _factory;
    public IndicadoresEndpointsTests(ApiFactory factory) => _factory = factory;

    record NovaCidadeDto(string Nome, string Estado);
    record CidadeDto(int Id, string Nome, string Estado);
    record NovoIndicadorDto(string Tipo, decimal Valor, string Unidade, DateTime DataMedicao);
    record IndicadorDto(int Id, int CidadeId, string Tipo, decimal Valor, string Unidade, DateTime DataMedicao);

    [Fact]
    public async Task Post_Indicador_AddsToCidade()
    {
        var client = _factory.CreateClient();
        var cidadeResp = await client.PostAsJsonAsync("/cidades", new NovaCidadeDto("Salvador", "BA"));
        var cidade = await cidadeResp.Content.ReadFromJsonAsync<CidadeDto>();

        var resp = await client.PostAsJsonAsync(
            $"/cidades/{cidade!.Id}/indicadores",
            new NovoIndicadorDto("AreaVerdePerc", 22.5m, "%", DateTime.UtcNow));

        Assert.Equal(HttpStatusCode.Created, resp.StatusCode);
    }

    [Fact]
    public async Task Get_Indicadores_ByCidade_ReturnsOnlyThatCidade()
    {
        var client = _factory.CreateClient();
        var c1 = await (await client.PostAsJsonAsync("/cidades", new NovaCidadeDto("Manaus", "AM")))
            .Content.ReadFromJsonAsync<CidadeDto>();
        var c2 = await (await client.PostAsJsonAsync("/cidades", new NovaCidadeDto("Belem", "PA")))
            .Content.ReadFromJsonAsync<CidadeDto>();

        await client.PostAsJsonAsync($"/cidades/{c1!.Id}/indicadores",
            new NovoIndicadorDto("EmissaoCo2Ton", 1200m, "ton", DateTime.UtcNow));
        await client.PostAsJsonAsync($"/cidades/{c2!.Id}/indicadores",
            new NovoIndicadorDto("EmissaoCo2Ton", 800m, "ton", DateTime.UtcNow));

        var resp = await client.GetAsync($"/cidades/{c1.Id}/indicadores");
        resp.EnsureSuccessStatusCode();
        var list = await resp.Content.ReadFromJsonAsync<List<IndicadorDto>>();
        Assert.Single(list!);
        Assert.Equal(c1.Id, list![0].CidadeId);
    }
}
```

- [ ] **Step 2: Run and verify fail**

Run: `dotnet test --filter IndicadoresEndpointsTests`
Expected: FAIL (endpoints not mapped).

- [ ] **Step 3: Implement `IndicadoresEndpoints.cs`**

Create `src/CidadesEsg.Api/Endpoints/IndicadoresEndpoints.cs`:
```csharp
using CidadesEsg.Api.Data;
using CidadesEsg.Api.Domain;
using Microsoft.EntityFrameworkCore;

namespace CidadesEsg.Api.Endpoints;

public static class IndicadoresEndpoints
{
    public record NovoIndicadorDto(string Tipo, decimal Valor, string Unidade, DateTime DataMedicao);

    public static IEndpointRouteBuilder MapIndicadores(this IEndpointRouteBuilder app)
    {
        app.MapGet("/cidades/{id:int}/indicadores", async (int id, AppDbContext db) =>
        {
            var cidade = await db.Cidades.FindAsync(id);
            if (cidade is null) return Results.NotFound();
            var items = await db.Indicadores.Where(i => i.CidadeId == id).ToListAsync();
            return Results.Ok(items);
        });

        app.MapPost("/cidades/{id:int}/indicadores", async (int id, NovoIndicadorDto dto, AppDbContext db) =>
        {
            var cidade = await db.Cidades.FindAsync(id);
            if (cidade is null) return Results.NotFound();

            if (!Enum.TryParse<TipoIndicador>(dto.Tipo, out var tipo))
                return Results.BadRequest(new { erro = $"Tipo inválido: {dto.Tipo}" });

            var indicador = new IndicadorEsg
            {
                CidadeId = id,
                Tipo = tipo,
                Valor = dto.Valor,
                Unidade = dto.Unidade,
                DataMedicao = dto.DataMedicao
            };
            db.Indicadores.Add(indicador);
            await db.SaveChangesAsync();
            return Results.Created($"/cidades/{id}/indicadores/{indicador.Id}", indicador);
        });

        return app;
    }
}
```

- [ ] **Step 4: Wire into `Program.cs`**

Add `app.MapIndicadores();` right after `app.MapCidades();`.

- [ ] **Step 5: Run full test suite**

Run: `dotnet test`
Expected: all 6 tests PASS (1 health + 3 cidades + 2 indicadores).

- [ ] **Step 6: Commit**

```bash
git add src/CidadesEsg.Api/Endpoints/IndicadoresEndpoints.cs src/CidadesEsg.Api/Program.cs tests/CidadesEsg.Api.Tests/IndicadoresEndpointsTests.cs
git commit -m "feat: add /cidades/{id}/indicadores endpoints"
```

---

## Task 8: Initial EF migration

**Files:**
- Create: `src/CidadesEsg.Api/Migrations/` (generated)

- [ ] **Step 1: Install `dotnet-ef` tool (user-wide)**

Run: `dotnet tool install --global dotnet-ef --version 8.0.10`
If already installed, run: `dotnet tool update --global dotnet-ef --version 8.0.10`.
Verify: `dotnet ef --version` → `8.0.10`.

- [ ] **Step 2: Generate initial migration**

Run from repo root:
```bash
dotnet ef migrations add InitialCreate \
  --project src/CidadesEsg.Api \
  --startup-project src/CidadesEsg.Api
```

Expected: folder `src/CidadesEsg.Api/Migrations/` created with `*_InitialCreate.cs` + `AppDbContextModelSnapshot.cs`.

- [ ] **Step 3: Build**

Run: `dotnet build`
Expected: build succeeds.

- [ ] **Step 4: Run tests to confirm nothing broke**

Run: `dotnet test`
Expected: 6 tests PASS (SQLite uses `EnsureCreated()`, not migrations — still works).

- [ ] **Step 5: Commit**

```bash
git add src/CidadesEsg.Api/Migrations
git commit -m "feat: add initial EF Core migration"
```

---

## Task 9: Dockerfile and .dockerignore

**Files:**
- Create: `Dockerfile`
- Create: `.dockerignore`

- [ ] **Step 1: Create `.dockerignore`**

At repo root:
```
**/bin
**/obj
**/out
**/.vs
**/.vscode
**/.idea
**/TestResults
**/*.user
.git
.gitignore
.env
.env.*
!.env.example
docs/
README.md
*.md
tests/
```

- [ ] **Step 2: Create `Dockerfile`**

At repo root:
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

- [ ] **Step 3: Build image locally**

Run: `docker build -t cidades-esg-api:local .`
Expected: image built successfully, final tag `cidades-esg-api:local`.

- [ ] **Step 4: Commit**

```bash
git add Dockerfile .dockerignore
git commit -m "feat: add multi-stage Dockerfile for .NET 8 API"
```

---

## Task 10: Docker Compose files

**Files:**
- Create: `docker-compose.yml`
- Create: `docker-compose.staging.yml`
- Create: `docker-compose.prod.yml`
- Create: `.env.example`

- [ ] **Step 1: Create `.env.example`**

At repo root:
```
POSTGRES_USER=esg
POSTGRES_PASSWORD=changeme
POSTGRES_DB=cidades_esg

ASPNETCORE_ENVIRONMENT=Production
ConnectionStrings__Default=Host=db;Port=5432;Database=cidades_esg;Username=esg;Password=changeme

IMAGE_TAG=local
```

- [ ] **Step 2: Create `docker-compose.yml` (dev)**

At repo root:
```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - pg_data_dev:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      retries: 10
    networks: [dev_net]

  api:
    build: .
    environment:
      ASPNETCORE_ENVIRONMENT: Development
      ConnectionStrings__Default: "Host=db;Port=5432;Database=${POSTGRES_DB};Username=${POSTGRES_USER};Password=${POSTGRES_PASSWORD}"
    ports:
      - "8080:8080"
    depends_on:
      db:
        condition: service_healthy
    networks: [dev_net]

volumes:
  pg_data_dev:

networks:
  dev_net:
```

- [ ] **Step 3: Create `docker-compose.staging.yml`**

At repo root:
```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5433:5432"
    volumes:
      - pg_data_staging:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      retries: 10
    networks: [stg_net]

  api:
    image: ghcr.io/${GHCR_OWNER}/cidades-esg-api:staging
    environment:
      ASPNETCORE_ENVIRONMENT: Staging
      ConnectionStrings__Default: "Host=db;Port=5432;Database=${POSTGRES_DB};Username=${POSTGRES_USER};Password=${POSTGRES_PASSWORD}"
    ports:
      - "8081:8080"
    depends_on:
      db:
        condition: service_healthy
    networks: [stg_net]

volumes:
  pg_data_staging:

networks:
  stg_net:
```

- [ ] **Step 4: Create `docker-compose.prod.yml`**

At repo root:
```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - pg_data_prod:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      retries: 10
    networks: [prod_net]

  api:
    image: ghcr.io/${GHCR_OWNER}/cidades-esg-api:prod
    environment:
      ASPNETCORE_ENVIRONMENT: Production
      ConnectionStrings__Default: "Host=db;Port=5432;Database=${POSTGRES_DB};Username=${POSTGRES_USER};Password=${POSTGRES_PASSWORD}"
    ports:
      - "8080:8080"
    depends_on:
      db:
        condition: service_healthy
    networks: [prod_net]

volumes:
  pg_data_prod:

networks:
  prod_net:
```

- [ ] **Step 5: Smoke-test dev compose locally**

Run:
```bash
cp .env.example .env
docker compose up -d --build
sleep 10
curl -s http://localhost:8080/health
```

Expected: JSON response `{"status":"ok","db":"up"}`.

- [ ] **Step 6: Tear down**

Run: `docker compose down -v`

- [ ] **Step 7: Commit**

```bash
git add docker-compose.yml docker-compose.staging.yml docker-compose.prod.yml .env.example
git commit -m "feat: add docker-compose files for dev, staging, and prod"
```

---

## Task 11: GitHub Actions CI/CD pipeline

**Files:**
- Create: `.github/workflows/ci-cd.yml`

- [ ] **Step 1: Create workflow file**

Create `.github/workflows/ci-cd.yml`:
```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository_owner }}/cidades-esg-api
  DOTNET_VERSION: "8.0.x"

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: ${{ env.DOTNET_VERSION }}

      - name: Restore
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore -c Release

      - name: Test
        run: dotnet test --no-build -c Release --logger "trx;LogFileName=test-results.trx" --results-directory TestResults

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: TestResults/

  docker-build-push:
    needs: build-test
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Compute tag
        id: meta
        run: |
          if [ "${GITHUB_REF}" = "refs/heads/main" ]; then
            echo "env_tag=prod" >> "$GITHUB_OUTPUT"
          else
            echo "env_tag=staging" >> "$GITHUB_OUTPUT"
          fi
          echo "sha_tag=sha-${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.env_tag }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.sha_tag }}

  deploy:
    needs: docker-build-push
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
    runs-on: ubuntu-latest
    steps:
      - name: Determine environment
        id: env
        run: |
          if [ "${GITHUB_REF}" = "refs/heads/main" ]; then
            echo "name=prod" >> "$GITHUB_OUTPUT"
            echo "compose=docker-compose.prod.yml" >> "$GITHUB_OUTPUT"
          else
            echo "name=staging" >> "$GITHUB_OUTPUT"
            echo "compose=docker-compose.staging.yml" >> "$GITHUB_OUTPUT"
          fi

      - name: Emit deploy instructions
        run: |
          cat > deploy-instructions-${{ steps.env.outputs.name }}.txt <<EOF
          Deploy to ${{ steps.env.outputs.name }}:

          export GHCR_OWNER=${{ github.repository_owner }}
          docker login ghcr.io -u ${{ github.actor }} -p <PAT-with-read:packages>
          docker compose -f ${{ steps.env.outputs.compose }} --env-file .env.${{ steps.env.outputs.name }} pull
          docker compose -f ${{ steps.env.outputs.compose }} --env-file .env.${{ steps.env.outputs.name }} up -d

          Verify:
            curl http://localhost:$([ "${{ steps.env.outputs.name }}" = "prod" ] && echo 8080 || echo 8081)/health
          EOF

      - name: Upload deploy instructions
        uses: actions/upload-artifact@v4
        with:
          name: deploy-instructions-${{ steps.env.outputs.name }}
          path: deploy-instructions-${{ steps.env.outputs.name }}.txt
```

- [ ] **Step 2: Create `develop` branch**

Run:
```bash
git checkout -b develop
```

- [ ] **Step 3: Commit workflow on develop**

```bash
git add .github/workflows/ci-cd.yml
git commit -m "ci: add GitHub Actions pipeline (build, test, push to GHCR, deploy instructions)"
```

- [ ] **Step 4: Create GitHub remote (if not already)**

Run:
```bash
gh repo create DevOps-FIAP --public --source=. --remote=origin --push
```

If remote already exists, just: `git push -u origin develop`.

- [ ] **Step 5: Verify pipeline runs green on `develop`**

Run: `gh run list --limit 1` after push completes.
Expected: one run in-progress then `completed success`. If failing, inspect with `gh run view --log-failed`.

- [ ] **Step 6: Merge develop → main, verify prod pipeline**

```bash
git checkout -b main
git push -u origin main
```

(Or if main already exists: `git checkout main && git merge develop --ff-only && git push`.)

Expected: second pipeline run completes green, publishes `:prod` image to GHCR.

---

## Task 12: README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md`**

At repo root:
````markdown
# Projeto — Cidades ESG Inteligentes

API REST em .NET 8 para gerenciar cidades e indicadores ESG (Environmental, Social, Governance), com pipeline CI/CD completo e deploy containerizado em dois ambientes (staging e produção).

Trabalho avaliativo da disciplina **Navegando pelo mundo DevOps** — FIAP.

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

Para derrubar: `docker compose down -v`.

## Pipeline CI/CD

**Ferramenta:** GitHub Actions (`.github/workflows/ci-cd.yml`).

**Gatilhos:**
- Push em `develop` → pipeline completo, publica imagem `:staging` no GHCR
- Push em `main` → pipeline completo, publica imagem `:prod` no GHCR
- PR em `main` → apenas build + testes

**Jobs:**
1. **build-test** — `dotnet restore`, `dotnet build`, `dotnet test` (xUnit)
2. **docker-build-push** — login no GHCR, build da imagem, push com tags `:staging`/`:prod` + `:sha-<7>`
3. **deploy** — gera artefato `deploy-instructions-<env>.txt` com comandos de deploy local

## Containerização

**Dockerfile** — multi-stage:
- Estágio `build` usa `mcr.microsoft.com/dotnet/sdk:8.0`, restaura dependências, publica release
- Estágio `runtime` usa `mcr.microsoft.com/dotnet/aspnet:8.0` (imagem menor), copia binários, expõe 8080, define healthcheck

**Estratégia de orquestração — dois ambientes isolados:**

| Ambiente | Compose file | Porta API | Porta DB | Volume | Rede | Tag imagem |
|---|---|---|---|---|---|---|
| Dev | `docker-compose.yml` | 8080 | 5432 | `pg_data_dev` | `dev_net` | build local |
| Staging | `docker-compose.staging.yml` | 8081 | 5433 | `pg_data_staging` | `stg_net` | `:staging` |
| Prod | `docker-compose.prod.yml` | 8080 | 5432 | `pg_data_prod` | `prod_net` | `:prod` |

**Rodar staging e prod simultaneamente:**
```bash
export GHCR_OWNER=<seu-usuario>
docker login ghcr.io

docker compose -f docker-compose.staging.yml --env-file .env.staging up -d
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

curl http://localhost:8081/health   # staging
curl http://localhost:8080/health   # prod
```

## Prints do funcionamento

Ver pasta `docs/evidencias/` (ou PDF anexo à entrega):

- `01-pipeline-verde.png` — Pipeline GitHub Actions com 3 jobs green
- `02-ghcr-imagens.png` — Imagens publicadas no GitHub Container Registry
- `03-staging-up.png` — `docker compose ... staging up`
- `04-prod-up.png` — `docker compose ... prod up`
- `05-docker-ps.png` — `docker ps` com 4 containers rodando
- `06-curl-health.png` — healthchecks OK em ambos os ambientes
- `07-curl-fluxo.png` — POST/GET cidades end-to-end

## Tecnologias utilizadas

- **Runtime:** .NET 8
- **API:** ASP.NET Core Minimal API
- **ORM:** Entity Framework Core 8
- **Banco:** PostgreSQL 16
- **Testes:** xUnit + `WebApplicationFactory` + SQLite in-memory
- **Container:** Docker (multi-stage)
- **Orquestração:** Docker Compose v2
- **CI/CD:** GitHub Actions
- **Registry:** GitHub Container Registry (GHCR)

## Checklist de entrega

| Item | Status |
|---|---|
| Projeto compactado em `.ZIP` com estrutura organizada | ☑ |
| Dockerfile funcional | ☑ |
| `docker-compose.yml` (+ staging/prod) | ☑ |
| Pipeline com etapas de build, teste e deploy | ☑ |
| `README.md` com instruções e prints | ☑ |
| Documentação técnica com evidências (PDF) | ☑ |
| Deploy realizado nos ambientes staging e produção | ☑ |

## Autor

Arthur Cavalcanti Granja — RM 560650
````

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with execution, pipeline, and container instructions"
```

---

## Task 13: Local smoke test + evidence collection

**Files:**
- Create: `.env.staging`, `.env.prod` (local, not committed)
- Create: `docs/evidencias/` (prints)

- [ ] **Step 1: Create local env files**

```bash
cp .env.example .env.staging
cp .env.example .env.prod
```

Edit both: set `ASPNETCORE_ENVIRONMENT` to `Staging` / `Production` respectively.

- [ ] **Step 2: Set GHCR owner and authenticate**

```bash
export GHCR_OWNER=<seu-usuario-github>
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GHCR_OWNER" --password-stdin
```

(Create a Personal Access Token classic with `read:packages` scope if needed.)

- [ ] **Step 3: Pull and run staging**

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging pull
docker compose -f docker-compose.staging.yml --env-file .env.staging up -d
sleep 10
curl -s http://localhost:8081/health | jq
```
Expected: `{"status":"ok","db":"up"}`.

- [ ] **Step 4: Pull and run prod (concurrently with staging)**

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod pull
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
sleep 10
curl -s http://localhost:8080/health | jq
```
Expected: `{"status":"ok","db":"up"}`.

- [ ] **Step 5: Collect evidence — end-to-end CRUD in staging**

```bash
curl -X POST http://localhost:8081/cidades \
  -H "Content-Type: application/json" \
  -d '{"nome":"Curitiba","estado":"PR"}'

curl -X POST http://localhost:8081/cidades/1/indicadores \
  -H "Content-Type: application/json" \
  -d '{"tipo":"AreaVerdePerc","valor":35.2,"unidade":"%","dataMedicao":"2026-04-21T00:00:00Z"}'

curl http://localhost:8081/cidades
curl http://localhost:8081/cidades/1/indicadores
```

- [ ] **Step 6: Take screenshots**

Capture and save to `docs/evidencias/`:
- `01-pipeline-verde.png` — `gh run view <run-id> --web` ou UI do Actions
- `02-ghcr-imagens.png` — página do package no GitHub
- `03-staging-up.png` — terminal mostrando `docker compose up` staging
- `04-prod-up.png` — terminal mostrando `docker compose up` prod
- `05-docker-ps.png` — saída de `docker ps`
- `06-curl-health.png` — responses dos 2 healthchecks
- `07-curl-fluxo.png` — POST/GET cidades + indicadores

- [ ] **Step 7: Tear down**

```bash
docker compose -f docker-compose.staging.yml --env-file .env.staging down
docker compose -f docker-compose.prod.yml --env-file .env.prod down
```

(Sem `-v` pra preservar volumes se quiser reusar.)

- [ ] **Step 8: Commit evidence**

```bash
git add docs/evidencias/
git commit -m "docs: add execution evidence (pipeline, deploy, healthcheck prints)"
git push
```

---

## Task 14: Generate deliverable ZIP

**Files:**
- Create: `CidadesEsg-FIAP-entrega.zip`

- [ ] **Step 1: Ensure working tree is clean**

Run: `git status`
Expected: `nothing to commit, working tree clean`.

- [ ] **Step 2: Create archive from git**

```bash
git archive --format=zip --prefix=DevOps-FIAP/ -o CidadesEsg-FIAP-entrega.zip HEAD
```

- [ ] **Step 3: Verify contents**

Run: `unzip -l CidadesEsg-FIAP-entrega.zip | head -40`
Expected: `Dockerfile`, `docker-compose*.yml`, `src/`, `tests/`, `README.md`, `.github/workflows/ci-cd.yml` present.

- [ ] **Step 4: Keep the ZIP out of git**

Run: `echo "*.zip" >> .gitignore && git add .gitignore && git commit -m "chore: ignore zip archives"`

---

## Done criteria

- All 6 tests pass (`dotnet test`)
- `docker compose up` works for dev, staging, and prod files
- GitHub Actions pipeline green on both `develop` and `main`
- GHCR has both `:staging` and `:prod` images
- Staging (8081) and prod (8080) run concurrently with isolated volumes/networks
- README + evidence prints collected
- ZIP archive ready for upload

## Self-review notes (post-write check)

- **Spec coverage:** each spec section mapped → Task 1-3 (stack/domain/DbContext), Task 4-7 (endpoints + tests), Task 8 (migration), Task 9 (Dockerfile), Task 10 (compose), Task 11 (CI/CD), Task 12 (README), Task 13 (evidence), Task 14 (ZIP). All 7 items of FIAP checklist covered.
- **Placeholders:** `<seu-usuario-github>` and `<PAT-with-read:packages>` are user-specific secrets — not plan placeholders; clearly labeled. `<run-id>` is contextual. No TBDs.
- **Type consistency:** `MapHealth`, `MapCidades`, `MapIndicadores` used consistently. `NovaCidadeDto`, `NovoIndicadorDto` same shape in tests and impl.
- **Scope:** single plan, executable end-to-end in one session.
