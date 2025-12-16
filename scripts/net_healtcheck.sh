#!/bin/bash

FAILED=0
ERRORS=""

GREEN='\e[32m'
RED='\e[31m'
NC='\e[0m'

LOGFILE="$HOME/scripts/logs/net_healthcheck.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "---- Netvaerks-healthcheck ($TIMESTAMP) ----"
echo "---- Netvaerks-healthcheck ($TIMESTAMP) ----" >> "$LOGFILE"

declare -A HOSTS=(
    ["MLS"]="192.168.10.1"
    ["Router 1941 VLAN10"]="192.168.10.2"
    ["Server (localhost test)"]="192.168.10.3"
    ["Backup Laptop VLAN20"]="192.168.20.3"
)

for NAME in "${!HOSTS[@]}"; do
    IP=${HOSTS[$NAME]}
    echo "Tester $NAME ($IP)..."
    echo "Tester $NAME ($IP)..." >> "$LOGFILE"

    if ping -c 1 $IP > /dev/null 2>&1; then
        MSG="[OK] $NAME svarer på ping!"
        echo -e "${GREEN}$MSG${NC}"
    else
        MSG="[FEJL] $NAME svarer ikke! Tjek netværket."
        echo -e "${RED}$MSG${NC}"
        FAILED=1
        ERRORS+="$MSG"$'\n'
    fi

    echo "$MSG" >> "$LOGFILE"
    echo "-------------------------------------------"
    echo "-------------------------------------------" >> "$LOGFILE"
done


if [ "$FAILED" -ne 0 ]; then
    MAIL_TO="alerts@ligegyldigmail.dk"
    MAIL_FROM="noor@ligegyldigmail.dk"
    SUBJECT="Netværksfejl på serveren $(hostname)"

    BODY="Der er registreret en fejl i netvaerks-healthcheck scriptet $(date '+%Y-%m-%d %H:%M:%S')

Foelgende tests fejlede:
$ERRORS

Se ogsaa logfilen:
$LOGFILE
"


    printf "Subject: %s\nFrom: %s\nTo: %s\n\n%s\n" "$SUBJECT" "$MAIL_FROM" "$MAIL_TO" "$BODY" | msmtp -a brevo "$MAIL_TO"
fi

