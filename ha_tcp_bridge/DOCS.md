# TCP Bridge for Crestron

A simple TCP socket server that bridges Crestron (or other TCP clients) to Home Assistant. 
Control Home Assistant entities via telnet-style commands.

## Connection Details

| Setting | Value |
|---------|-------|
| IP | Your Home Assistant IP |
| Port | 8124 (configurable) |
| Protocol | TCP (raw socket) |
| Line Ending | CRLF (`\r\n`) |

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `HELP` | Show commands and version | `HELP` |
| `PING` | Test HA connection | `PING` |
| `PRESS <entity>` | Press a button | `PRESS button.kitchen_keypad_bright` |
| `ON <entity>` | Turn on light/switch | `ON light.living_room` |
| `OFF <entity>` | Turn off light/switch | `OFF light.living_room` |
| `LEVEL <entity> <0-100>` | Set brightness | `LEVEL light.living_room 75` |
| `LIST` | List all entities | `LIST` |
| `LISTBUTTONS` | List button entities | `LISTBUTTONS` |

## Response Format

- Success: `OK: <message>`
- Error: `ERR: <message>`

## Crestron Integration

### TCP Client Setup

1. Create TCP/IP client on Crestron processor
2. Set IP to your Home Assistant IP
3. Set port to 8124
4. Use raw TCP mode (not SSH/Telnet negotiation)

### Sending Commands

Send command string followed by CRLF (`\r\n` / `0x0D 0x0A`):

```
PRESS button.kitchen_keypad_bright\r\n
```

### Parsing Responses

Check first 3 characters of response:
- `OK:` = Success
- `ERR` = Error

## Testing

You can test the connection from any machine on your network:

```bash
nc <home-assistant-ip> 8124
# or
telnet <home-assistant-ip> 8124
```

Then type `PING` and press Enter.

## Troubleshooting

### Cannot connect to bridge
- Check the add-on is running (green indicator)
- Check the add-on logs for errors
- Verify port 8124 is not blocked by firewall

### Commands return ERR
- Check entity ID exists: use `LISTBUTTONS` or `LIST`
- Verify entity ID spelling (case-insensitive)

### Connection drops
- The bridge maintains persistent connections
- Check network stability between Crestron and Home Assistant
