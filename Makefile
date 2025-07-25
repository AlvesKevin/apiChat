.PHONY: build up down logs clean help

# Variables
DOCKER_COMPOSE = docker-compose -f docker-compose.https.yml

help: ## Afficher l'aide
	@echo "🚀 API Chatbot HTTPS - Commandes disponibles:"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Construire les images Docker
	@echo "🔨 Construction des images..."
	$(DOCKER_COMPOSE) build

up: ## Démarrer les services HTTPS
	@echo "🚀 Démarrage des services HTTPS..."
	$(DOCKER_COMPOSE) up -d
	@echo "✅ Services démarrés sur https://localhost:8443"

down: ## Arrêter les services
	@echo "🛑 Arrêt des services..."
	$(DOCKER_COMPOSE) down

logs: ## Afficher les logs
	@echo "📋 Logs des services..."
	$(DOCKER_COMPOSE) logs -f

logs-web: ## Afficher les logs de l'API web
	@echo "📋 Logs de l'API web..."
	$(DOCKER_COMPOSE) logs -f web

logs-db: ## Afficher les logs de la base de données
	@echo "📋 Logs de la base de données..."
	$(DOCKER_COMPOSE) logs -f db

logs-nginx: ## Afficher les logs nginx
	@echo "📋 Logs nginx..."
	$(DOCKER_COMPOSE) logs -f nginx

clean: ## Nettoyer tous les conteneurs et volumes
	@echo "🧹 Nettoyage complet..."
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f

status: ## Vérifier le statut des services
	@echo "📊 Statut des services:"
	$(DOCKER_COMPOSE) ps

restart: down up ## Redémarrer les services

migrate: ## Exécuter les migrations Django
	@echo "📝 Exécution des migrations..."
	$(DOCKER_COMPOSE) exec web python manage.py migrate

shell: ## Ouvrir un shell Django
	@echo "🐚 Ouverture du shell Django..."
	$(DOCKER_COMPOSE) exec web python manage.py shell

admin: ## Créer un superutilisateur
	@echo "👤 Création d'un superutilisateur..."
	$(DOCKER_COMPOSE) exec web python manage.py createsuperuser

deploy-https: ## Déployer l'API avec HTTPS
	@echo "🔐 Déploiement HTTPS..."
	./deploy_https.sh

generate-ssl: ## Générer les certificats SSL
	@echo "🔑 Génération des certificats SSL..."
	./generate_ssl.sh

health-check: ## Vérifier la santé de l'API
	@echo "🔍 Diagnostic de santé de l'API..."
	./check_api_health.sh