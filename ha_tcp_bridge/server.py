#!/usr/bin/env python3
"""
TCP Bridge for Home Assistant - Crestron Integration (Add-on Version)
Listens for simple text commands and translates to HA API calls

Commands:
  PRESS <entity_id>           - Press a button
  ON <entity_id>              - Turn on a light
  OFF <entity_id>             - Turn off a light
  LEVEL <entity_id> <0-100>   - Set light level
  LIST                        - List all entities
  LISTBUTTONS                 - List button entities
  HELP                        - Show commands

Connect via: telnet <ip> 8124
Line ending: CRLF (\r\n)
"""

VERSION = "1.0.0"

import socket
import threading
import requests
import json
import os
import sys

# Configuration - Auto-detected for HAOS Add-on
def get_config():
    """Load configuration from add-on options or environment"""
    config = {
        "ha_url": "http://supervisor/core",
        "ha_token": os.environ.get("SUPERVISOR_TOKEN", ""),
        "tcp_port": 8124
    }
    
    # Try to load add-on options
    options_path = "/data/options.json"
    if os.path.exists(options_path):
        try:
            with open(options_path) as f:
                options = json.load(f)
                config["tcp_port"] = options.get("port", 8124)
        except Exception as e:
            log(f"Warning: Could not load options.json: {e}")
    
    # Fall back to environment variables (for standalone/Docker use)
    if not config["ha_token"]:
        config["ha_token"] = os.environ.get("HA_TOKEN", "")
        config["ha_url"] = os.environ.get("HA_URL", "http://localhost:8123")
    
    config["tcp_port"] = int(os.environ.get("TCP_PORT", config["tcp_port"]))
    
    return config

CONFIG = None  # Loaded at startup

def log(msg):
    print(f"[HA-TCP] {msg}", flush=True)

def ha_request(method, endpoint, data=None):
    """Make a request to Home Assistant API"""
    headers = {
        "Authorization": f"Bearer {CONFIG['ha_token']}",
        "Content-Type": "application/json"
    }
    url = f"{CONFIG['ha_url']}/api/{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=10)
        else:
            resp = requests.post(url, headers=headers, json=data, timeout=10)
        return resp.status_code, resp.json() if resp.text else {}
    except Exception as e:
        return 500, {"error": str(e)}

def get_entity_list():
    """Get list of controllable entities"""
    status, states = ha_request("GET", "states")
    result = []
    if status == 200:
        for entity in states:
            eid = entity.get("entity_id", "")
            if eid.startswith(("button.", "light.", "switch.", "cover.", "fan.")):
                state = entity.get("state", "")
                name = entity.get("attributes", {}).get("friendly_name", eid)
                result.append(f"{eid} [{state}] - {name}")
    return result

def handle_command(cmd):
    """Process a command and return response"""
    cmd = ''.join(c for c in cmd if c.isprintable() or c.isspace()).strip()
    cmd = cmd.strip("'\"` \t")
    parts = cmd.upper().split()
    if not parts:
        return "ERR: Empty command"

    action = parts[0]

    if action == "HELP":
        return f"""HA-TCP Bridge v{VERSION}
Line ending: CRLF (\\r\\n)

Commands:
PRESS <entity_id>         - Press a button
ON <entity_id>            - Turn on light/switch
OFF <entity_id>           - Turn off light/switch
LEVEL <entity_id> <0-100> - Set brightness
LIST                      - List entities
LISTBUTTONS               - List button entities only
PING                      - Test connection

Example: PRESS button.kitchen_keypad_bright
Example: ON light.living_room
Example: LEVEL light.living_room 50"""

    elif action == "PING":
        status, _ = ha_request("GET", "")
        return "OK: Connected to Home Assistant" if status == 200 else "ERR: Cannot reach Home Assistant"

    elif action == "LIST":
        entities = get_entity_list()
        return f"OK: {len(entities)} entities\n" + "\n".join(entities[:50])

    elif action == "LISTBUTTONS":
        status, states = ha_request("GET", "states")
        buttons = []
        if status == 200:
            for entity in states:
                eid = entity.get("entity_id", "")
                if eid.startswith("button."):
                    name = entity.get("attributes", {}).get("friendly_name", eid)
                    buttons.append(f"{eid} - {name}")
        return f"OK: {len(buttons)} buttons\n" + "\n".join(buttons)

    elif action == "PRESS":
        if len(parts) < 2:
            return "ERR: Usage: PRESS <entity_id>"
        entity_id = parts[1].lower()
        if not entity_id.startswith("button."):
            entity_id = f"button.{entity_id}"

        status, resp = ha_request("POST", "services/button/press", {"entity_id": entity_id})
        if status == 200:
            return f"OK: Pressed {entity_id}"
        else:
            return f"ERR: {resp.get('message', 'Failed to press button')}"

    elif action == "ON":
        if len(parts) < 2:
            return "ERR: Usage: ON <entity_id>"
        entity_id = parts[1].lower()

        if entity_id.startswith("light.") or "." not in entity_id:
            if not entity_id.startswith("light."):
                entity_id = f"light.{entity_id}"
            service = "light/turn_on"
        elif entity_id.startswith("switch."):
            service = "switch/turn_on"
        else:
            service = "homeassistant/turn_on"

        status, resp = ha_request("POST", f"services/{service}", {"entity_id": entity_id})
        return f"OK: {entity_id} on" if status == 200 else f"ERR: {resp}"

    elif action == "OFF":
        if len(parts) < 2:
            return "ERR: Usage: OFF <entity_id>"
        entity_id = parts[1].lower()

        if entity_id.startswith("light.") or "." not in entity_id:
            if not entity_id.startswith("light."):
                entity_id = f"light.{entity_id}"
            service = "light/turn_off"
        elif entity_id.startswith("switch."):
            service = "switch/turn_off"
        else:
            service = "homeassistant/turn_off"

        status, resp = ha_request("POST", f"services/{service}", {"entity_id": entity_id})
        return f"OK: {entity_id} off" if status == 200 else f"ERR: {resp}"

    elif action == "LEVEL":
        if len(parts) < 3:
            return "ERR: Usage: LEVEL <entity_id> <0-100>"
        entity_id = parts[1].lower()
        try:
            level = int(parts[2])
            if not 0 <= level <= 100:
                raise ValueError()
        except:
            return "ERR: Level must be 0-100"

        if not entity_id.startswith("light."):
            entity_id = f"light.{entity_id}"

        brightness = int(level * 255 / 100)
        status, resp = ha_request("POST", "services/light/turn_on", {
            "entity_id": entity_id,
            "brightness": brightness
        })
        return f"OK: {entity_id} set to {level}%" if status == 200 else f"ERR: {resp}"

    else:
        return f"ERR: Unknown command '{action}'. Type HELP for commands."

def handle_client(conn, addr):
    """Handle a TCP client connection"""
    log(f"Client connected: {addr}")
    conn.settimeout(None)

    try:
        conn.send(f"HA-TCP Bridge v{VERSION} Ready. Type HELP for commands.\r\n> ".encode())
        buffer = ""

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                buffer += data.decode("utf-8", errors="ignore")

                while "\n" in buffer or "\r" in buffer:
                    for sep in ["\r\n", "\n", "\r"]:
                        if sep in buffer:
                            line, buffer = buffer.split(sep, 1)
                            break

                    line = line.strip()
                    if line:
                        log(f"Command from {addr}: {line}")
                        response = handle_command(line)
                        conn.send(f"{response}\r\n> ".encode())

            except socket.timeout:
                break

    except Exception as e:
        log(f"Error with client {addr}: {e}")
    finally:
        conn.close()
        log(f"Client disconnected: {addr}")

def main():
    global CONFIG
    CONFIG = get_config()
    
    if not CONFIG["ha_token"]:
        print("ERROR: No authentication token available!")
        print("If running as add-on: Check that homeassistant_api is enabled in config.yaml")
        print("If running standalone: Set HA_TOKEN environment variable")
        sys.exit(1)

    log(f"Configuration loaded:")
    log(f"  HA URL: {CONFIG['ha_url']}")
    log(f"  TCP Port: {CONFIG['tcp_port']}")
    log(f"  Token: {'[SUPERVISOR]' if 'supervisor' in CONFIG['ha_url'].lower() else '[MANUAL]'}")

    # Test HA connection
    status, _ = ha_request("GET", "")
    if status != 200:
        print(f"WARNING: Cannot connect to Home Assistant at {CONFIG['ha_url']}")
    else:
        log(f"Connected to Home Assistant")

    # Start TCP server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", CONFIG["tcp_port"]))
    server.listen(5)

    log(f"TCP server listening on port {CONFIG['tcp_port']}")
    log("Waiting for Crestron connections...")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        log("Shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    main()
