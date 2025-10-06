# Prototipo NHN Automatizado

Demo local para mostrar **automatización de procesos** con **FastAPI** + **n8n** + **Mailhog** y (opcional) **Google Sheets**.  
Caso de uso: cuando se crea un *lead*, se orquesta el envío de email y el alta en una planilla.

---

## 🧰 Stack / Hecho con

- **Python + FastAPI** — API de ejemplo (`POST /leads`).
- **n8n (self-hosted)** — orquestación (Webhook → Email → Google Sheets).
- **Mailhog** — SMTP de desarrollo (UI para ver correos).
- **Google Sheets** (opcional) — “CRM” mínimo para registrar leads.
- **Docker & Docker Compose** — todo corre en contenedores.

---

## 🔎 Arquitectura

```mermaid
flowchart LR
  A[Cliente / Swagger] -->|JSON| B(FastAPI)

  subgraph API
    B --> C[(SQLite)]
    B --> D[Excel / openpyxl]
    B --> E[SMTP - Mailhog]
    B --> F[/n8n Webhook/]
  end

  subgraph n8n
    F --> G["Send Email (SMTP)"]
    F --> H["Google Sheets (Append)"]
    F -.-> I["Slack / Discord (opcional)"]
  end

  E --> J[Mailhog UI]
📦 Estructura
bash
Copiar código
.
├─ app/                     # FastAPI (endpoint /leads)
├─ data/                    # (opcional) archivos locales
├─ rules/                   # (opcional) reglas
├─ lead_pipeline.json       # Workflow n8n (Webhook → Email → Sheets)
├─ docker-compose.yml
├─ Dockerfile
├─ requirements.txt
├─ .env.example
└─ README.md
⚙️ Requisitos
Docker y Docker Compose

(Opcional) Cuenta de Google si vas a usar Google Sheets

🚀 Puesta en marcha
Variables de entorno (opcional):

bash
Copiar código
cp .env.example .env
Levantar servicios:

bash
Copiar código
docker compose up -d --build
docker compose ps
URLs:

API (FastAPI) → http://localhost:8000 (Swagger en /docs)

n8n → http://localhost:5678

Mailhog (UI) → http://localhost:8025

Primer uso de n8n: registrate con usuario/contraseña locales.

🔄 Importar el workflow en n8n
n8n → Workflows → Import from file.

Elegí lead_pipeline.json (incluido en este repo).

Activate el workflow.

Credencial SMTP (Mailhog)
n8n → Credentials → New → SMTP

Host: mailhog

Port: 1025

User/Pass: vacío

SSL/TLS: apagado

📊 Google Sheets (opcional)
1) Hoja de ejemplo
Creá una planilla con la fila 1 (encabezados exactos):

bash
Copiar código
id, created_at, name, email, source, priority, status, owner, notes
2) Credencial en n8n
A) Service Account (recomendada)

Google Cloud: habilitá Google Sheets API y creá una Service Account (descargá la key JSON).

n8n → Credentials → New → Google Service Account → pegá client_email y private_key (o el JSON entero).

Compartí la hoja con el client_email de esa Service Account como Editor.

Test en n8n (OK).

B) OAuth2 (tu usuario)

Redirect URL: http://localhost:5678/rest/oauth2-credential/callback

Scope: https://www.googleapis.com/auth/spreadsheets

3) Nodo “Google Sheets → Append row in sheet”
Resource: Sheet Within Document

Operation: Append Row

Document: By ID (el ID entre /d/ y /edit en la URL)

Sheet: Hoja 1

Mapping Column Mode: Map Each Column Manually

Options → Cell Format: RAW ← (evita #ERROR! en Sheets)

Values to Send (usá Expression, sin =):

Columna	Valor (Expression)
id	{{ $json.body.id }}
created_at	{{ $now.toFormat('yyyy-LL-dd HH:mm:ss') }}
name	{{ $json.body.name }}
email	{{ $json.body.email }}
source	{{ $json.body.source }}
priority	{{ $json.body.priority }}
status	{{ $json.body.status }}
owner	{{ $json.body.owner }}
notes	{{ $json.body.notes }}

Si el nodo Sheets está después de “Send email”, referí explícitamente al Webhook:
{{ $node["Webhook"].json.body.name }} (…igual para cada campo).
Alternativa más limpia: ramificar desde el Webhook hacia Send email y Google Sheets.

✅ Probar el flujo
Con el workflow activo:

bash
Copiar código
curl -X POST http://localhost:8000/leads \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Ana Test\",\"email\":\"ana@test.com\",\"source\":\"landing\",\"priority\":\"Alta\",\"status\":\"En evaluación\",\"owner\":\"Equipo A\",\"notes\":\"Quiero una demo urgente\"}"
Esperado:

n8n → Executions en verde

Mailhog con el correo

Google Sheets con la nueva fila

🧯 Troubleshooting
#ERROR! en Sheets → en el nodo: Options → Cell Format = RAW y expresiones sin =.

Valores undefined → el nodo lee la salida de Send email.

Conectá Append row directo al Webhook, o

Usá {{ $node["Webhook"].json.body.campo }}.

403 / permiso en Sheets → compartí la hoja con el client_email (Service Account) como Editor.

Encabezados → la fila 1 debe coincidir exacto.

OAuth redirect_uri_mismatch → la Redirect URL debe ser exactamente la de n8n.

🗺️ Roadmap / Extensiones
Conectores WhatsApp / Telegram / Instagram (entrada de leads).

Slack/Discord para alertas internas.

Persistencia en DB/CRM (Postgres, MySQL, HubSpot, etc.).

Enriquecimiento con IA (clasificación de prioridad / routing).