up:
	docker-compose up -d --build

dev:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart bot

logs:
	docker-compose logs -f bot

rebuild:
	docker-compose build bot

ps:
	docker-compose ps

prune:
	docker volume prune -f

rm_db:
	docker-compose down --volumes

deps:
	docker-compose exec bot pip install -r requirements.txt

run-migration:
	docker exec -i tg-video-count-bot_db_1 psql -U postgres -d marathon_db < migrations/1_payments.sql

