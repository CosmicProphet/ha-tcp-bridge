# Changelog

## [1.0.7] - 2025-12-27

### Changed
- LIST command results are now sorted alphabetically

## [1.0.6] - 2025-12-27

### Changed
- Unified LIST command with optional filters
- `LIST` - all entities
- `LIST BUTTON` - filter by domain
- `LIST KITCHEN` - filter by text match
- `LIST BUTTON KITCHEN` - multiple filters (AND logic)
- Removed LISTBUTTONS and LISTLIGHTS (use `LIST BUTTON` and `LIST LIGHT` instead)

## [1.0.5] - 2025-12-27

### Added
- Entity validation before executing commands (PRESS, ON, OFF, LEVEL)
- Returns `ERR: Entity '<entity_id>' not found` for non-existent entities

## [1.0.4] - 2025-12-27

### Added
- LISTLIGHTS command to list only light entities

## [1.0.3] - 2025-12-27

### Fixed
- LIST command now shows all entities (removed 50 entity limit)

## [1.0.2] - 2025-12-27

### Fixed
- Added execute permission to run script in Dockerfile

## [1.0.1] - 2025-12-27

### Fixed
- Fixed s6-overlay v3 compatibility (moved run script to rootfs/etc/services.d/)
- Added `init: false` for proper s6-overlay handling

## [1.0.0] - 2025-12-27

### Initial Release
- TCP socket server bridging Crestron/telnet commands to Home Assistant
- Commands: PING, PRESS, ON, OFF, LEVEL, LIST, LISTBUTTONS, HELP
- Automatic authentication via Supervisor API (no manual token required)
- Configurable TCP port (default: 8124)
- Supports amd64 and aarch64 architectures
