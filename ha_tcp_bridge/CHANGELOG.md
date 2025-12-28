# Changelog

## [1.0.0] - 2025-12-27

### Initial Release
- TCP socket server bridging Crestron/telnet commands to Home Assistant
- Commands: PING, PRESS, ON, OFF, LEVEL, LIST, LISTBUTTONS, HELP
- Automatic authentication via Supervisor API (no manual token required)
- Configurable TCP port (default: 8124)
- Supports amd64 and aarch64 architectures
