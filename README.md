# API Chatbot Django

API REST pour un chatbot développée avec Django et Django REST Framework, avec authentification JWT et support des images.

## Fonctionnalités

- Inscription et connexion d'utilisateurs
- Authentification par token JWT
- Messages publics et privés
- Support des images (upload en base64)
- API dockerisée avec PostgreSQL

## Endpoints

### POST /register
Créer un compte utilisateur
```json
{
  "username": "string",
  "password": "string"
}
```

### POST /login
Authentification utilisateur
```json
{
  "username": "string",
  "password": "string"
}
```

### GET /users
Lister tous les utilisateurs (authentification requise)
Header: `x-api-key: <JWT_TOKEN>`

### POST /messages
Envoyer un message (authentification requise)
Header: `x-api-key: <JWT_TOKEN>`
```json
{
  "content": "string",
  "to": "int (optionnel)",
  "image": {
    "name": "string",
    "content": "string (base64)"
  }
}
```

### GET /messages
Récupérer les messages (authentification requise)
Header: `x-api-key: <JWT_TOKEN>`

## Installation

### Installation locale

1. Cloner le projet
2. Créer un fichier `.env` basé sur `.env.example`
3. Lancer avec Docker:

```bash
docker-compose up --build
```

L'API sera disponible sur http://localhost:8000

### Installation pour accès externe

Pour rendre l'API accessible depuis d'autres appareils sur le réseau :

```bash
# Déploiement HTTP (accès réseau local)
./deploy_external.sh

# Ou avec Make
make deploy-external
```

L'API sera accessible depuis votre réseau local via votre IP (ex: http://192.168.1.100:8000)

### Installation HTTPS (recommandé)

Pour une compatibilité avec les frontends HTTPS (comme GitLab Pages) :

```bash
# Déploiement HTTPS avec certificats auto-signés
./deploy_https.sh

# Ou avec Make
make deploy-https
```

L'API sera accessible en HTTPS via votre IP (ex: https://192.168.1.100:8443)

## Tests

### Lancer tous les tests automatiquement
```bash
# Avec le script de test complet (recommandé)
./test_runner.sh

# Ou avec Make
make test
```

### Tests rapides (API déjà en cours)
```bash
make test-quick
# ou
python3 tests/test_api.py
```

### Tests manuels interactifs
```bash
python3 tests/test_manual.py
```

### Autres commandes utiles
```bash
make help              # Voir toutes les commandes
make up                # Démarrer les services
make down              # Arrêter les services
make logs              # Voir les logs
make clean             # Nettoyer complètement
make deploy-external   # Déployer pour accès externe
make deploy-https      # Déployer avec HTTPS
make network-info      # Voir les infos réseau
make generate-ssl      # Générer certificats SSL
```

## Tests inclus

La batterie de tests vérifie :

✅ **Register** : Inscription utilisateur, validation des données, utilisateurs existants  
✅ **Login** : Authentification, tokens JWT, credentials invalides  
✅ **Users** : Liste des utilisateurs, authentification requise  
✅ **Messages** : Envoi/réception, messages publics/privés, images en base64  
✅ **Sécurité** : Authentification JWT, validation des tokens

## Accès réseau

### Informations de connexion

```bash
# Obtenir votre IP et les URLs d'accès
make network-info
# ou
./get_network_info.sh
```

### Configuration firewall

- **macOS** : Préférences Système > Sécurité > Pare-feu > Autoriser le port 8000
- **Linux** : `sudo ufw allow 8000`
- **Windows** : Panneau de configuration > Pare-feu > Autoriser une app

### Accès depuis un autre appareil

Une fois l'API déployée avec accès externe, les autres personnes peuvent accéder à :
- **Base URL** : `http://VOTRE_IP:8000`
- **Exemple** : `http://192.168.1.100:8000/register`

### Test de connectivité

```bash
# Test HTTP depuis un autre appareil
curl http://VOTRE_IP:8000/users

# Test HTTPS depuis un autre appareil
curl -k https://VOTRE_IP:8443/users
```

## Problèmes CORS et Mixed Content

Si votre frontend utilise HTTPS (comme GitLab Pages), vous devez utiliser la version HTTPS de l'API :

1. **Déployez avec HTTPS** : `make deploy-https`
2. **Acceptez le certificat** : Dans votre navigateur, allez sur `https://VOTRE_IP:8443` et acceptez le certificat auto-signé
3. **Configurez votre frontend** : Utilisez `https://VOTRE_IP:8443` comme base URL

### Certificats auto-signés

Les navigateurs afficheront un avertissement pour les certificats auto-signés :
- Cliquez sur "Paramètres avancés"
- Puis "Continuer vers le site (non sécurisé)"
- L'API sera alors accessible en HTTPS