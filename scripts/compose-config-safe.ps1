param(
    [string]$ComposeFile = "docker-compose.yml"
)

# Prints compose config without resolving .env placeholders.
# Use this instead of `docker compose config` when sharing output.
docker compose -f $ComposeFile config --no-interpolate
