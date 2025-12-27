# Kostal Inverter Microservice

A FastAPI microservice for collecting and serving data from Kostal solar inverters via Home Assistant.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)

## Overview

This microservice bridges Kostal solar inverters and the VoltCast application, providing a REST API for real-time and historical energy data.

**Key Features:**
- Real-time generation, consumption, and battery status
- Historical data storage and retrieval
- Mock mode for testing without hardware
- Automatic data collection every 15 seconds
- Docker support with CI/CD pipeline
- working on port 8082

## API Endpoints

### Data Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/kostal/realtimedata` | GET | Current generation, consumption, battery |
| `/kostal/lfdata` | GET | Lifetime/interval totals |
| `/kostal/historicaldata` | GET | Historical consumption data |

### Configuration Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/kostal/{username}` | GET | Get inverter config |
| `/kostal` | POST | Create inverter config |
| `/kostal` | PUT | Update inverter config |
| `/kostal/user/{user}` | DELETE | Delete inverter config |


## Database

**SQLite database** (`app/database.db`) stores:

- **historic_data**: Consumption data with timestamps
- **inverter**: Inverter configurations (URL, tokens)

Data is collected every 15 seconds (configurable via `DATA_COLLECTION_INTERVAL`)


## CI/CD

GitHub Actions workflows:
- **Build & Test**: Runs tests and SonarQube analysis
- **Docker Build**: Builds and pushes image to GHCR on main branch

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite
- **HTTP Client**: httpx (async)
- **Scheduler**: APScheduler
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Container**: Docker, Docker Compose

## License

Part of the VoltCast Advanced Software Engineering project at Alpen-Adria-Universität Klagenfurt.

## Links

- **Organisation**: https://github.com/VoltCast-a-ASE-project
- **Repository**: https://github.com/VoltCast-a-ASE-project/Kostal-Microservice
---

**Version**: 1.0.0 | **Python**: 3.10+ | **FastAPI**: 0.100+
