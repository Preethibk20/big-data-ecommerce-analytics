$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$Image = "mongo:7.0.16@sha256:c630c59342c1493d50345136df2af14a76b9e827dd5316bfabee07a0880a5f3a"
$Container = "ecommerce-mongo-dev"

$existing = docker container inspect $Container 2>$null
if ($LASTEXITCODE -eq 0) {
    $label = docker inspect --format '{{index .Config.Labels "project"}}' $Container
    if ($label -ne "ecommerce-sales-analytics") {
        throw "Existing container '$Container' is not owned by ecommerce-sales-analytics"
    }
    docker start $Container | Out-Null
} else {
    docker run -d --name $Container --label project=ecommerce-sales-analytics `
        -p 127.0.0.1:27017:27017 `
        --mount "type=volume,source=ecommerce_mongo_data,target=/data/db" $Image | Out-Null
}

for ($attempt = 0; $attempt -lt 30; $attempt++) {
    docker exec $Container mongosh --quiet --eval "quit(db.adminCommand({ping:1}).ok === 1 ? 0 : 1)" 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "MongoDB responds to ping on 127.0.0.1:27017"
        exit 0
    }
    Start-Sleep -Seconds 1
}

docker logs --tail 40 $Container
exit 1

