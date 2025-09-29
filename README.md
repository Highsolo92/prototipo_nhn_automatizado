# NHN Ops Hub — MVP de Automatización (FastAPI + n8n + Mailhog + Excel)

> Prototipo demostrable para un rol de **IA & Automatización**: alta de leads vía API, reglas editables, actualización de Excel, envío de emails y orquestación con **n8n**. Pensado para mostrar punta a punta en una demo de 5–7 minutos.

![stack](https://img.shields.io/badge/FastAPI-0.110+-green) ![n8n](https://img.shields.io/badge/n8n-self--hosted-orange) ![Docker](https://img.shields.io/badge/Docker-Compose-blue) ![Status](https://img.shields.io/badge/status-MVP-success)

---

## TL;DR
- **POST /leads** → aplica **reglas YAML**, guarda en **SQLite**, añade fila a **Excel**, envía email (Mailhog) y dispara **n8n** por webhook.  
- **Import CSV** y **export diario** a Excel.  
- Todo corre con **Docker Compose**.

---

## Arquitectura

```mermaid
flowchart LR
  A[Cliente / Swagger] -->|JSON| B(FastAPI)
  subgraph API
    B --> C[(SQLite)]
    B --> D[Excel\nopenpyxl]
    B --> E[SMTP\nMailhog]
    B -->|POST JSON| F[/n8n Webhook/]
  end
  subgraph n8n
    F --> G[Send Email (SMTP)]
    F --> H[Google Sheets (opcional)]
    F --> I[Slack/Discord (opcional)]
  end
  E --> J[Mailhog UI]
