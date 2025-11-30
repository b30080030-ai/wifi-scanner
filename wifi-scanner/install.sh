#!/bin/bash

# ألوان للطباعة
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${CYAN}"
echo "╔════════════════════════════════════════╗"
echo "║     WiFi Scanner - Installation        ║"
echo "║           مثبت أداة كشف الشبكات         ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}[*] جاري تحديث الحزم...${NC}"
pkg update -y && pkg upgrade -y

echo -e "${YELLOW}[*] جاري تثبيت المتطلبات...${NC}"
pkg install -y python termux-api root-repo

echo -e "${YELLOW}[*] جاري تثبيت مكتبات Python...${NC}"
pip install rich

echo -e "${GREEN}[✓] تم التثبيت بنجاح!${NC}"
echo -e "${CYAN}[*] شغّل الأداة بالأمر: python wifi_scanner.py${NC}"
