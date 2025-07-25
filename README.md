# API Chatbot avec HTTPS et Documentation Swagger

API REST Django pour système de chat avec authentification JWT, déploiement Docker, HTTPS et documentation interactive.

## 🚀 Démarrage rapide

```bash
./deploy_https.sh
```

L'API sera accessible sur : **https://localhost:8443**

## 📚 Documentation interactive

- **Swagger UI** : https://localhost:8443/api/docs/
- **ReDoc** : https://localhost:8443/api/redoc/
- **Schéma OpenAPI** : https://localhost:8443/api/schema/
- **Page d'accueil** : https://localhost:8443/

## 📋 Fonctionnalités

- **Documentation Swagger** : Interface interactive pour tester l'API
- **Authentification JWT** : Système sécurisé avec tokens
- **Gestion utilisateurs** : Inscription, connexion, liste des utilisateurs
- **Messages** : Envoi/réception avec support d'images (base64)
- **HTTPS** : Certificats SSL auto-générés
- **CORS** : Compatible avec frontends externes
- **Docker** : Déploiement containerisé complet

## 🔗 Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Page d'accueil avec liens documentation |
| POST | `/register` | Inscription utilisateur |
| POST | `/login` | Connexion (retourne JWT) |
| GET | `/users` | Liste des utilisateurs (JWT requis) |
| GET/POST | `/messages` | Messages (JWT requis) |

## 🔐 Authentification

1. **Inscription** : `POST /register` avec `username` et `password`
2. **Connexion** : `POST /login` pour obtenir le JWT token
3. **Utilisation** : Ajouter le header à toutes les requêtes protégées :
   ```
   x-api-key: <votre_jwt_token>
   ```

## 📱 Upload d'images

Format pour envoyer une image :
```json
{
  "content": "Message avec image",
  "image": {
    "name": "photo.png",
    "content": "base64_encoded_image_data"
  }
}
```

## 🧪 Test de l'API

La documentation Swagger permet de tester directement tous les endpoints :

1. Ouvrir https://localhost:8443/api/docs/
2. Créer un compte via `/register`
3. Se connecter via `/login` pour obtenir le token
4. Cliquer sur "Authorize" et saisir le token
5. Tester tous les endpoints

## 🛠️ Commandes utiles

```bash
make help          # Aide
make deploy-https   # Déploiement HTTPS
make health-check   # Diagnostic API
make logs          # Voir les logs
make down          # Arrêter les services
```

## 🏗️ Architecture

```
Frontend → Nginx (HTTPS + CORS) → Django API → PostgreSQL
                ↓
          Documentation Swagger
```

## 📖 Documentation technique

### Structure des réponses

**Succès** :
```json
{
  "success": true
}
```

**Erreur** :
```json
{
  "error": "Message d'erreur",
  "success": false
}
```

### Exemple d'utilisation complète

```bash
# 1. Inscription
curl -k -X POST https://localhost:8443/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "password123"}'

# 2. Connexion
curl -k -X POST https://localhost:8443/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "password123"}'

# 3. Utilisation avec token
curl -k -X GET https://localhost:8443/users \
  -H "x-api-key: YOUR_JWT_TOKEN"
```

## 🌐 Accès externe

L'API est configurée pour être accessible depuis d'autres appareils du réseau local. L'IP sera affichée lors du déploiement.

## 📄 OpenAPI/Swagger

L'API est entièrement documentée selon les standards OpenAPI 3.0 avec :
- Descriptions détaillées de chaque endpoint
- Exemples de requêtes et réponses
- Schémas de validation
- Support d'authentification JWT intégré