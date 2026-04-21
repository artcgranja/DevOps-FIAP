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
