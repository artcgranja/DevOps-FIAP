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
