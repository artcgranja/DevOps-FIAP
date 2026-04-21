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
