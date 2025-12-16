#!/bin/bash

### === INDSTILLINGER === ###
START_TIME="9:00"               # Tidsstyring start
STOP_TIME="17:00"                # Tidsstyring stop
APP_DIR="/home/server/backend"
VENV_DIR="$APP_DIR/venv"
APP_MODULE="app:app"             # Flask-app objekt i app.py
WS_FILE="$APP_DIR/ws_server.py"
RETRY_DELAY=5                     # sekunder mellem genstarts-forsøg

### === HJÆLPE-FUNKTIONER === ###

# --- Tjek og ryd PID hvis processen ikke lever ---
fix_pid() {
    local pidfile="$1"
    local pname="$2"

    if [ -f "$pidfile" ]; then
        PID=$(cat "$pidfile")
        if ! kill -0 "$PID" 2>/dev/null; then
            echo "$(date +'%F %T') - $pname PID-fil fandtes men processen kørte ikke. Rydder op." >> "$APP_DIR/startup.log"
            rm "$pidfile"
        else
            return 1   # processen kører → ingen opstart
        fi
    fi

    # Process kører uden PID-fil
    RUNNING_PID=$(pgrep -f "$pname" | head -n 1)
    if [ -n "$RUNNING_PID" ]; then
        echo "$RUNNING_PID" > "$pidfile"
        echo "$(date +'%F %T') - $pname kører uden PID-fil — genskabt PID: $RUNNING_PID" >> "$APP_DIR/startup.log"
        return 1
    fi

    return 0
}

# --- Start Gunicorn ---
start_app() {
    fix_pid "$APP_DIR/gunicorn.pid" "gunicorn"
    if [ $? -eq 1 ]; then return; fi

    echo "$(date +'%F %T') - Starter Gunicorn..." >> "$APP_DIR/startup.log"
    cd "$APP_DIR" || return

    # Start Gunicorn i baggrunden med virtualenv
    nohup bash -c "source $VENV_DIR/bin/activate && gunicorn --workers 3 --bind 127.0.0.1:8000 $APP_MODULE" \
        > "$APP_DIR/gunicorn.log" 2>&1 &

    sleep 2
    GUNI_PID=$!

    if ! kill -0 "$GUNI_PID" 2>/dev/null; then
        echo "$(date +'%F %T') - FEJL: Gunicorn startede ikke korrekt. Tjek gunicorn.log" >> "$APP_DIR/startup.log"
        return
    fi

    echo "$GUNI_PID" > "$APP_DIR/gunicorn.pid"
    echo "$(date +'%F %T') - Gunicorn startet med PID: $GUNI_PID" >> "$APP_DIR/startup.log"
}

# --- Start ws_server.py ---
start_ws() {
    fix_pid "$APP_DIR/ws_server.pid" "ws_server.py"
    if [ $? -eq 1 ]; then return; fi

    echo "$(date +'%F %T') - Starter ws_server.py..." >> "$APP_DIR/startup.log"

    nohup $VENV_DIR/bin/python "$WS_FILE" > "$APP_DIR/ws_server.log" 2>&1 &
    sleep 1
    WS_PID=$!

    if ! kill -0 "$WS_PID" 2>/dev/null; then
        echo "$(date +'%F %T') - FEJL: ws_server.py startede ikke korrekt. Tjek ws_server.log" >> "$APP_DIR/startup.log"
        return
    fi

    echo "$WS_PID" > "$APP_DIR/ws_server.pid"
    echo "$(date +'%F %T') - WS-server startet med PID: $WS_PID" >> "$APP_DIR/startup.log"
}

# --- Stop Gunicorn ---
stop_app() {
    if [ -f "$APP_DIR/gunicorn.pid" ]; then
        PID=$(cat "$APP_DIR/gunicorn.pid")
        echo "$(date +'%F %T') - Stopper Gunicorn (PID: $PID)..." >> "$APP_DIR/startup.log"
        kill $PID 2>/dev/null
        rm "$APP_DIR/gunicorn.pid"
        echo "$(date +'%F %T') - Gunicorn stoppet." >> "$APP_DIR/startup.log"
    else
        echo "$(date +'%F %T') - Gunicorn kører ikke." >> "$APP_DIR/startup.log"
    fi
}

# --- Stop ws_server.py ---
stop_ws() {
    if [ -f "$APP_DIR/ws_server.pid" ]; then
        PID=$(cat "$APP_DIR/ws_server.pid")
        echo "$(date +'%F %T') - Stopper ws_server.py (PID: $PID)..." >> "$APP_DIR/startup.log"
        kill $PID 2>/dev/null
        rm "$APP_DIR/ws_server.pid"
        echo "$(date +'%F %T') - WS-server stoppet." >> "$APP_DIR/startup.log"
    else
        echo "$(date +'%F %T') - ws_server.py kører ikke." >> "$APP_DIR/startup.log"
    fi
}

### === MAIN LOOP (TIDSSTYRET) === ###
echo "$(date +'%F %T') - Starter tidsstyret app-kontrol..." >> "$APP_DIR/startup.log"

while true; do
    CURRENT=$(date +%H:%M)
    echo "DEBUG: CURRENT=$CURRENT, START_TIME=$START_TIME, STOP_TIME=$STOP_TIME" >> "$APP_DIR/startup.log"

    if [[ "$CURRENT" > "$START_TIME" && "$CURRENT" < "$STOP_TIME" ]]; then
        start_app
        start_ws
    fi

    if [[ "$CURRENT" == "$STOP_TIME" ]]; then
        stop_app
        stop_ws
    fi

    sleep 30
done
