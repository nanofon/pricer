docker-compose up -d --build

docker logs --tail=50 pricer-db-1
docker logs --tail=50 pricer-crawler-1
docker logs --tail=50 pricer-embedder-1
docker logs --tail=50 pricer-ml-1
docker logs --tail=50 pricer-api-1
docker logs --tail=50 pricer-frontend-1

docker exec -it pricer-db-1 psql -U postgres -d pricer

docker-compose down
