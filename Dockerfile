FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY *.sln ./
COPY src/CidadesEsg.Api/*.csproj src/CidadesEsg.Api/
RUN dotnet restore src/CidadesEsg.Api/CidadesEsg.Api.csproj

COPY src/CidadesEsg.Api/ src/CidadesEsg.Api/
RUN dotnet publish src/CidadesEsg.Api/CidadesEsg.Api.csproj \
    -c Release -o /app /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app .

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["dotnet", "CidadesEsg.Api.dll"]
