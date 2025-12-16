#!/bin/bash

LOGFILE="/home/server/scripts/ssh_logins.log"

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
USER=$USER
FROM=$(echo $SSH_CLIENT | awk '{print $1}')

INFO="$TIMESTAMP - USER: $USER FROM: $FROM"
echo "$INFO" >> "$LOGFILE"

# Send mail
MAIL_TO="alerts@ligegyldigmail.dk"
MAIL_FROM="noor@liggeyldigmail.dk"
SUBJECT="SSH login registreret på serveren"
BODY="Der er registreret et SSH-login:\n$INFO"

printf "Subject: %s\nFrom: %s\nTo: %s\n\n%s\n" \
    "$SUBJECT" "$MAIL_FROM" "$MAIL_TO" "$BODY" \
    | msmtp -a brevo "$MAIL_TO"
