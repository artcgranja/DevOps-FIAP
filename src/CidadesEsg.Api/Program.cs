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
    if (db.Database.IsRelational() && !app.Environment.IsEnvironment("Testing"))
        db.Database.Migrate();
}

app.Run();

public partial class Program { }
