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
