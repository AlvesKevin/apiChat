#!/bin/bash

# Script pour générer des certificats SSL auto-signés

set -e

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔐 GÉNÉRATION DES CERTIFICATS SSL${NC}"
echo -e "${CYAN}=================================${NC}"

# Créer le dossier ssl s'il n'existe pas
mkdir -p ssl

# Obtenir l'IP locale
if [[ "$OSTYPE" == "darwin"* ]]; then
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    LOCAL_IP=$(hostname -I | awk '{print $1}')
else
    LOCAL_IP="localhost"
fi

echo -e "${YELLOW}📍 IP locale détectée: $LOCAL_IP${NC}"

# Générer la clé privée
echo -e "${CYAN}🔑 Génération de la clé privée...${NC}"
openssl genrsa -out ssl/server.key 2048

# Créer le fichier de configuration pour le certificat
cat > ssl/server.conf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = FR
ST = France
L = Paris
O = Chatbot API
OU = Development
CN = chatbot-api.local

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = chatbot-api.local
DNS.3 = *.chatbot-api.local
IP.1 = 127.0.0.1
IP.2 = $LOCAL_IP
EOF

# Générer le certificat
echo -e "${CYAN}📜 Génération du certificat SSL...${NC}"
openssl req -new -x509 -key ssl/server.key -out ssl/server.crt -days 365 -config ssl/server.conf -extensions v3_req

# Créer un certificat combiné pour nginx
cat ssl/server.crt ssl/server.key > ssl/server.pem

# Permissions
chmod 600 ssl/server.key
chmod 644 ssl/server.crt
chmod 644 ssl/server.pem

echo -e "${GREEN}✅ Certificats SSL générés avec succès!${NC}"
echo -e "${GREEN}=================================${NC}"
echo -e "📁 Fichiers créés:"
echo -e "   ssl/server.key - Clé privée"
echo -e "   ssl/server.crt - Certificat"
echo -e "   ssl/server.pem - Certificat combiné"
echo -e ""
echo -e "${YELLOW}⚠️  Certificats auto-signés:${NC}"
echo -e "   • Les navigateurs afficheront un avertissement de sécurité"
echo -e "   • Cliquez sur 'Avancé' puis 'Continuer vers le site'"
echo -e "   • Valides pour: localhost, $LOCAL_IP, chatbot-api.local"
echo -e ""
echo -e "${CYAN}🌐 URLs HTTPS disponibles:${NC}"
echo -e "   https://localhost:8443"
echo -e "   https://$LOCAL_IP:8443"