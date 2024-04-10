PROJECT_NAME=sample-project

.PHONY: start
start:
	docker compose down
	docker compose -f docker-compose.yml -p $(PROJECT_NAME) up --build

.PHONY: dev
dev:
	docker compose down
	docker compose -f docker-compose.yml -f docker-compose.dev.yml -p $(PROJECT_NAME) up -d --build

.PHONY: clean
clean:
	docker ps -a | awk '/$(PROJECT_NAME)/ { print $$1 }' | xargs docker rm -f
	docker images -a | awk '/$(PROJECT_NAME)/ { print $$3 }' | xargs docker rmi -f