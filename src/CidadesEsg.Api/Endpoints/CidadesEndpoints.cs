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
