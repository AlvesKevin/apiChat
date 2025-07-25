#!/bin/bash

# Script de déploiement HTTPS pour l'API Chatbot

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${MAGENTA}🔐 DÉPLOIEMENT API CHATBOT - HTTPS${NC}"
echo -e "${MAGENTA}====================================${NC}"

# Fonction pour obtenir l'IP locale
get_local_ip() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        LOCAL_IP=$(hostname -I | awk '{print $1}')
    else
        LOCAL_IP="localhost"
    fi
    echo $LOCAL_IP
}

LOCAL_IP=$(get_local_ip)

echo -e "${CYAN}📍 Configuration HTTPS:${NC}"
echo -e "   IP locale: ${GREEN}$LOCAL_IP${NC}"
echo -e "   Port HTTPS: ${GREEN}443 (8443)${NC}"
echo -e "   Port HTTP: ${GREEN}80 (redirect vers HTTPS)${NC}"

# Vérifier si Docker est en cours
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker n'est pas en cours d'exécution${NC}"
    exit 1
fi

# Vérifier si OpenSSL est installé
if ! command -v openssl &> /dev/null; then
    echo -e "${RED}❌ OpenSSL n'est pas installé${NC}"
    echo -e "${YELLOW}   Installation requise:${NC}"
    echo -e "${YELLOW}   - macOS: brew install openssl${NC}"
    echo -e "${YELLOW}   - Linux: sudo apt-get install openssl${NC}"
    exit 1
fi

# Générer les certificats SSL s'ils n'existent pas
if [ ! -f "ssl/server.crt" ] || [ ! -f "ssl/server.key" ]; then
    echo -e "${BLUE}🔑 Génération des certificats SSL...${NC}"
    ./generate_ssl.sh
else
    echo -e "${GREEN}✅ Certificats SSL trouvés${NC}"
fi

# Arrêter les conteneurs existants
echo -e "${YELLOW}🛑 Arrêt des conteneurs existants...${NC}"
docker-compose -f docker-compose.https.yml down -v 2>/dev/null || true
docker-compose down -v 2>/dev/null || true

# Construire et lancer avec HTTPS
echo -e "${BLUE}🔨 Construction et lancement avec HTTPS...${NC}"
if ! docker-compose -f docker-compose.https.yml up -d --build; then
    echo -e "${RED}❌ Échec du lancement des conteneurs${NC}"
    exit 1
fi

# Attendre que les services soient prêts
echo -e "${YELLOW}⏳ Attente du démarrage des services...${NC}"
sleep 20

# Vérifier que l'API répond en HTTPS
echo -e "${CYAN}🏥 Vérification de l'API HTTPS...${NC}"
if curl -k -s https://localhost:8443/users > /dev/null; then
    echo -e "${GREEN}✅ API HTTPS accessible localement${NC}"
else
    echo -e "${RED}❌ API HTTPS non accessible${NC}"
fi

# Vérifier l'accès externe
if [ "$LOCAL_IP" != "localhost" ] && [ "$LOCAL_IP" != "127.0.0.1" ]; then
    echo -e "${CYAN}🌐 Test d'accès HTTPS externe...${NC}"
    if curl -k -s --connect-timeout 5 https://$LOCAL_IP:8443/users > /dev/null; then
        echo -e "${GREEN}✅ API HTTPS accessible depuis l'externe${NC}"
    else
        echo -e "${YELLOW}⚠️  API HTTPS peut ne pas être accessible depuis l'externe${NC}"
        echo -e "${YELLOW}    Vérifiez votre firewall (ports 80, 443, 8443)${NC}"
    fi
fi

# Test des headers CORS
echo -e "${CYAN}🔍 Vérification de la configuration CORS...${NC}"
CORS_TEST=$(curl -k -s -I -X OPTIONS https://$LOCAL_IP:8443/register \
    -H "Origin: https://demo-chat-0b57ce.gitlab.io" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type,x-api-key")

CORS_PASSED=0
CORS_TOTAL=3

# Test 1: Access-Control-Allow-Origin
if echo "$CORS_TEST" | grep -q "Access-Control-Allow-Origin: \*"; then
    echo -e "${GREEN}✅ CORS Origin configuré${NC}"
    ((CORS_PASSED++))
else
    echo -e "${RED}❌ CORS Origin manquant${NC}"
fi

# Test 2: Access-Control-Allow-Methods
if echo "$CORS_TEST" | grep -q "Access-Control-Allow-Methods.*POST"; then
    echo -e "${GREEN}✅ CORS Methods configuré${NC}"
    ((CORS_PASSED++))
else
    echo -e "${RED}❌ CORS Methods manquant${NC}"
fi

# Test 3: Access-Control-Allow-Headers
if echo "$CORS_TEST" | grep -q "Access-Control-Allow-Headers.*x-api-key"; then
    echo -e "${GREEN}✅ CORS Headers configuré${NC}"
    ((CORS_PASSED++))
else
    echo -e "${RED}❌ CORS Headers manquant${NC}"
fi

if [ $CORS_PASSED -eq $CORS_TOTAL ]; then
    echo -e "${GREEN}🎉 Configuration CORS complète!${NC}"
else
    echo -e "${YELLOW}⚠️  Configuration CORS incomplète ($CORS_PASSED/$CORS_TOTAL)${NC}"
fi

# Fonction pour ouvrir le navigateur
open_browser() {
    local url="$1"
    echo -e "${BLUE}🌐 Ouverture automatique du navigateur pour accepter le certificat...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "$url" 2>/dev/null
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open > /dev/null; then
            xdg-open "$url" 2>/dev/null
        elif command -v gnome-open > /dev/null; then
            gnome-open "$url" 2>/dev/null
        fi
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Windows
        start "$url" 2>/dev/null
    fi
}

# Acceptation automatique du certificat
echo -e "${CYAN}🔐 Configuration de l'acceptation du certificat...${NC}"
echo -e "${YELLOW}Pour que votre frontend fonctionne, vous devez accepter le certificat SSL.${NC}"

# Demander si on veut ouvrir le navigateur automatiquement
read -p "$(echo -e ${CYAN}Voulez-vous ouvrir automatiquement le navigateur pour accepter le certificat? [Y/n]: ${NC})" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    open_browser "https://$LOCAL_IP:8443"
    echo -e "${GREEN}📋 Instructions d'acceptation du certificat:${NC}"
    echo -e "   1. Dans la page qui s'ouvre, vous verrez un avertissement de sécurité"
    echo -e "   2. Cliquez sur '${CYAN}Paramètres avancés${NC}' ou '${CYAN}Advanced${NC}'"
    echo -e "   3. Cliquez sur '${CYAN}Continuer vers le site${NC}' ou '${CYAN}Proceed to $LOCAL_IP${NC}'"
    echo -e "   4. Vous devriez voir: ${GREEN}{\"error\": \"Token required\"}${NC}"
    echo -e "   5. C'est normal ! Le certificat est maintenant accepté."
    
    echo -e "\n${YELLOW}⏳ Appuyez sur Entrée une fois le certificat accepté...${NC}"
    read
else
    echo -e "${YELLOW}📋 Acceptation manuelle requise:${NC}"
    echo -e "   Allez sur: ${GREEN}https://$LOCAL_IP:8443${NC}"
    echo -e "   Acceptez le certificat auto-signé"
fi

# Test final après acceptation
echo -e "${CYAN}🧪 Test final de l'API...${NC}"
if curl -k -s https://$LOCAL_IP:8443/users | grep -q "Token required"; then
    echo -e "${GREEN}✅ API HTTPS entièrement fonctionnelle${NC}"
else
    echo -e "${YELLOW}⚠️  Vérifiez que le certificat a bien été accepté${NC}"
fi

# Afficher les informations de connexion
echo -e "\n${GREEN}🎉 DÉPLOIEMENT HTTPS TERMINÉ!${NC}"
echo -e "${GREEN}==============================${NC}"

echo -e "\n${CYAN}🔐 URLs HTTPS d'accès:${NC}"
echo -e "   Local:    ${GREEN}https://localhost:8443${NC}"
echo -e "   Réseau:   ${GREEN}https://$LOCAL_IP:8443${NC}"

echo -e "\n${CYAN}🔗 Endpoints HTTPS:${NC}"
echo -e "   Register: ${BLUE}POST${NC} https://$LOCAL_IP:8443/register"
echo -e "   Login:    ${BLUE}POST${NC} https://$LOCAL_IP:8443/login"
echo -e "   Users:    ${BLUE}GET${NC}  https://$LOCAL_IP:8443/users"
echo -e "   Messages: ${BLUE}GET/POST${NC} https://$LOCAL_IP:8443/messages"

echo -e "\n${CYAN}📋 Conteneurs:${NC}"
echo -e "   API Django: ${GREEN}chatbot_api${NC}"
echo -e "   Base données: ${GREEN}chatbot_db${NC}"
echo -e "   Proxy HTTPS: ${GREEN}chatbot_nginx${NC}"

echo -e "\n${YELLOW}⚠️  Certificats auto-signés:${NC}"
echo -e "   • Les navigateurs afficheront un avertissement de sécurité"
echo -e "   • Cliquez sur 'Paramètres avancés' puis 'Continuer vers le site'"
echo -e "   • Ou ajoutez une exception de sécurité"

echo -e "\n${CYAN}🔍 Commandes utiles:${NC}"
echo -e "   Logs API:     ${GREEN}docker-compose -f docker-compose.https.yml logs -f web${NC}"
echo -e "   Logs Nginx:   ${GREEN}docker-compose -f docker-compose.https.yml logs -f nginx${NC}"
echo -e "   Arrêter:      ${GREEN}docker-compose -f docker-compose.https.yml down${NC}"
echo -e "   Redémarrer:   ${GREEN}docker-compose -f docker-compose.https.yml restart${NC}"

echo -e "\n${CYAN}📱 Test depuis un autre appareil:${NC}"
echo -e "   curl -k https://$LOCAL_IP:8443/users"

echo -e "\n${GREEN}✨ L'API est maintenant accessible en HTTPS!${NC}"
echo -e "${GREEN}   Compatible avec les frontends HTTPS comme GitLab Pages${NC}"