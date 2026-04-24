.PHONY: up down seed reset help

help:
	@echo "Available commands:"
	@echo "  make up     - Start the PostgreSQL container"
	@echo "  make down   - Stop the container (data is preserved)"
	@echo "  make reset  - Stop the container AND wipe all data"
	@echo "  make seed   - Load sample mentees into the database"

up:
	docker compose up -d

down:
	docker compose down

reset:
	docker compose down -v

seed:
	docker exec -i giga_mentees_db psql -U giga -d giga_mentees < sql/seed.sql
