#!/bin/bash

# Script de diagnostic de santé de l'API

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

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

echo -e "${CYAN}🔍 DIAGNOSTIC DE SANTÉ API CHATBOT${NC}"
echo -e "${CYAN}===================================${NC}"

# 1. Vérifier les conteneurs
echo -e "\n${YELLOW}📦 État des conteneurs:${NC}"
docker-compose -f docker-compose.https.yml ps

# 2. Vérifier les logs récents
echo -e "\n${YELLOW}📋 Logs récents nginx:${NC}"
docker-compose -f docker-compose.https.yml logs --tail=5 nginx

echo -e "\n${YELLOW}📋 Logs récents API:${NC}"
docker-compose -f docker-compose.https.yml logs --tail=5 web

# 3. Test de connectivité locale
echo -e "\n${YELLOW}🔗 Test connectivité locale:${NC}"
if curl -k -s https://localhost:8443/health > /dev/null; then
    echo -e "${GREEN}✅ API HTTPS localhost accessible${NC}"
else
    echo -e "${RED}❌ API HTTPS localhost non accessible${NC}"
fi

# 4. Test de connectivité externe
echo -e "\n${YELLOW}🌐 Test connectivité externe:${NC}"
if curl -k -s --connect-timeout 5 https://$LOCAL_IP:8443/health > /dev/null; then
    echo -e "${GREEN}✅ API HTTPS externe accessible${NC}"
else
    echo -e "${RED}❌ API HTTPS externe non accessible${NC}"
fi

# 5. Test CORS
echo -e "\n${YELLOW}🔄 Test CORS:${NC}"
CORS_RESPONSE=$(curl -k -s -I -X OPTIONS https://localhost:8443/register -H "Origin: https://demo-chat-0b57ce.gitlab.io")
if echo "$CORS_RESPONSE" | grep -q "access-control-allow-origin"; then
    echo -e "${GREEN}✅ Headers CORS présents${NC}"
else
    echo -e "${RED}❌ Headers CORS manquants${NC}"
fi

# 6. Test API endpoints
echo -e "\n${YELLOW}🎯 Test endpoints API:${NC}"
for endpoint in "/users" "/health"; do
    response=$(curl -k -s -o /dev/null -w "%{http_code}" https://localhost:8443$endpoint)
    if [[ $response -eq 200 || $response -eq 401 ]]; then
        echo -e "${GREEN}✅ $endpoint ($response)${NC}"
    else
        echo -e "${RED}❌ $endpoint ($response)${NC}"
    fi
done

# 7. Informations de connexion
echo -e "\n${CYAN}📱 Informations de connexion:${NC}"
echo -e "URL locale:  ${GREEN}https://localhost:8443${NC}"
echo -e "URL réseau:  ${GREEN}https://$LOCAL_IP:8443${NC}"
echo -e "Frontend:    Utilisez ${GREEN}https://$LOCAL_IP:8443${NC} comme base URL"

# 8. Instructions pour accepter le certificat
echo -e "\n${YELLOW}🔐 Acceptation du certificat:${NC}"
echo -e "Si votre frontend ne fonctionne pas:"
echo -e "1. Allez sur ${GREEN}https://$LOCAL_IP:8443${NC} dans votre navigateur"
echo -e "2. Acceptez le certificat auto-signé"
echo -e "3. Vous devriez voir: ${GREEN}{\"error\": \"Token required\"}${NC}"

echo -e "\n${CYAN}✅ Diagnostic terminé${NC}"