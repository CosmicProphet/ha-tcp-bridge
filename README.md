# Home Assistant TCP Bridge for Crestron

[![Open your Home Assistant instance and show the add add-on repository dialog with this repository pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FCosmicProphet%2Fha-tcp-bridge)

TCP socket server bridging Crestron (or other TCP clients) to Home Assistant. Control HA entities via simple telnet-style commands.

## Installation

1. Click the button above, or manually add this repository URL in Home Assistant:
   - Go to **Settings → Add-ons → Add-on Store**
   - Click **⋮** (top right) → **Repositories**
   - Add: `https://github.com/CosmicProphet/ha-tcp-bridge`

2. Find "TCP Bridge for Crestron" in the add-on store and click **Install**

3. Start the add-on and check the logs

## Usage

Connect via TCP on port 8124:

```bash
nc <homeassistant-ip> 8124
```

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `PING` | Test HA connection | `PING` |
| `PRESS <entity>` | Press a button | `PRESS button.kitchen_keypad` |
| `ON <entity>` | Turn on light/switch | `ON light.living_room` |
| `OFF <entity>` | Turn off light/switch | `OFF light.living_room` |
| `LEVEL <entity> <0-100>` | Set brightness | `LEVEL light.living_room 75` |
| `LIST` | List all entities | `LIST` |
| `LISTBUTTONS` | List button entities | `LISTBUTTONS` |
| `HELP` | Show commands | `HELP` |

### Response Format

- Success: `OK: <message>`
- Error: `ERR: <message>`

## Crestron Integration

1. Create TCP/IP client on Crestron processor
2. Set IP to your Home Assistant IP
3. Set port to 8124
4. Use raw TCP mode (not SSH/Telnet negotiation)
5. Send commands with CRLF line ending (`\r\n`)

## License

MIT
