using CidadesEsg.Api.Data;

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
