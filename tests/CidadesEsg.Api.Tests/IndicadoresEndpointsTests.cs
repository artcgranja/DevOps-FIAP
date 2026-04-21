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
