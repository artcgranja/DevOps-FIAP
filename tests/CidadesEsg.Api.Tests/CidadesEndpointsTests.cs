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
