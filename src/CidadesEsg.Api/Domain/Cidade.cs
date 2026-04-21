namespace CidadesEsg.Api.Domain;

public class Cidade
{
    public int Id { get; set; }
    public string Nome { get; set; } = string.Empty;
    public string Estado { get; set; } = string.Empty;
    public DateTime CriadoEm { get; set; } = DateTime.UtcNow;
    public List<IndicadorEsg> Indicadores { get; set; } = new();
}
