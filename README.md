Prototipo NHN Automatizado

Demo local para mostrar automatización de procesos con FastAPI + n8n + Mailhog + Google Sheets (opcional).
Sirve para demostrar cómo orquestar eventos de negocio (alta de lead) y documentar el flujo de punta a punta.

La API expone POST /leads y envía el evento a n8n.

n8n envía un email (vía Mailhog) y registra el lead en Google Sheets.

Mailhog captura los correos para pruebas locales (sin enviar a internet).

Arquitectura
flowchart LR
  A[Cliente / Swagger] -->|JSON| B(FastAPI)

  subgraph API
    B --> C[(SQLite)]
    B --> D[Excel<br/>openpyxl]
    B --> E[SMTP<br/>Mailhog]
    B --> F[/n8n Webhook/]
  end

  subgraph n8n
    F --> G["Send Email (SMTP)"]
    F --> H["Google Sheets (Append)"]
    F -.-> I["Slack/Discord (opcional)"]
  end

  E --> J[Mailhog UI]

Requisitos

Docker y Docker Compose

(Opcional) Cuenta de Google para usar Google Sheets

Estructura del proyecto
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

Variables de entorno

Copiá el ejemplo y ajustá si lo necesitás:

cp .env.example .env


El stack funciona out-of-the-box con los valores por defecto.

Levantar el entorno
docker compose up -d --build
docker compose ps


Servicios y URLs:

API FastAPI: http://localhost:8000
 (Swagger en /docs)

n8n: http://localhost:5678

Mailhog (UI): http://localhost:8025

Primer acceso a n8n: registrate con usuario/contraseña locales.

Importar el workflow en n8n

n8n → Workflows → Import from file.

Elegí lead_pipeline.json (incluido en este repo).

Activate el workflow.

Credencial SMTP (Mailhog)

Credentials → New → SMTP

Host: mailhog — Port: 1025 — User/Pass: vacío — SSL/TLS: apagado.

Google Sheets (opcional pero recomendado)
1) Crear la hoja

En Google Drive, crea una hoja llamada NHN Leads con estos encabezados en la fila 1 (idénticos):

id, created_at, name, email, source, priority, status, owner, notes

2) Credencial en n8n

Opción A — Service Account (recomendada)

Google Cloud Console → crea/usa un Proyecto.

APIs & Services → Enable APIs → habilitá Google Sheets API.

IAM & Admin → Service Accounts → Create → Add key (JSON).

En n8n → Credentials → New → Google Service Account.

Pegá client_email y private_key (o el JSON completo).

Compartí la hoja con el client_email de la Service Account como Editor.

Test en n8n (OK).

Opción B — OAuth2 (tu usuario de Google)

Google Cloud Console → OAuth consent screen (External) → agregate como Test user.

Credentials → Create → OAuth client (Web):

Authorized redirect URI:
http://localhost:5678/rest/oauth2-credential/callback

En n8n → Credentials → Google OAuth2 → pega Client ID/Secret.

Scopes: https://www.googleapis.com/auth/spreadsheets

Connect y Test.

3) Configurar el nodo “Google Sheets → Append row in sheet”

Resource: Sheet Within Document

Operation: Append Row

Document: By ID (el ID entre /d/ y /edit en la URL)

Sheet: Hoja 1 (o el nombre que uses)

Mapping Column Mode: Map Each Column Manually

Options → Cell Format: RAW ← (evita #ERROR! en Sheets)

Values to Send (usar Expression — sin = delante):

Column	Value (Expression)
id	{{ $json.body.id }}
created_at	{{ $now.toFormat('yyyy-LL-dd HH:mm:ss') }}
name	{{ $json.body.name }}
email	{{ $json.body.email }}
source	{{ $json.body.source }}
priority	{{ $json.body.priority }}
status	{{ $json.body.status }}
owner	{{ $json.body.owner }}
notes	{{ $json.body.notes }}

Si conectaste el nodo “Append row in sheet” después de “Send email”, referí al Webhook explícitamente, por ejemplo:
{{ $node["Webhook"].json.body.name }}.
Alternativa más simple: ramificá desde el Webhook hacia Send email y hacia Google Sheets.

Probar el flujo

Con el workflow activado:

curl -X POST http://localhost:8000/leads \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Ana Test\",\"email\":\"ana@test.com\",\"source\":\"landing\",\"priority\":\"Alta\",\"status\":\"En evaluación\",\"owner\":\"Equipo A\",\"notes\":\"Quiero una demo urgente\"}"


Verificá:

n8n → Executions en verde

Mailhog (UI): correo recibido

Google Sheets: fila nueva con los datos

Troubleshooting

403 / permission en Sheets → compartí la hoja con el client_email de la Service Account (Editor).

#ERROR! en celdas → en el nodo, Options → Cell Format = RAW y asegurate de usar expresiones sin =.

Valores undefined → el nodo lee la salida de Send email (que no trae body).

Conectá Append row directo al Webhook, o

Usá {{ $node["Webhook"].json.body.campo }} en cada columna.

No coincide con encabezados → la fila 1 de la hoja debe llamarse exactamente como en la tabla.

redirect_uri_mismatch (OAuth2) → la Redirect URL en Google debe ser exactamente la de n8n.

The caller does not have permission → faltó compartir la hoja con el client_email.

Extensiones posibles

WhatsApp / Telegram / Instagram (conector + webhook)

Slack/Discord para alertas internas

Persistencia en DB/CRM (Postgres, MySQL, HubSpot, etc.)

IA para clasificar prioridad de lead (OpenAI u otro proveedor)

Comandos útiles

Parar y limpiar:

docker compose down


Recrear solo n8n (si actualizás el workflow):

docker compose restart n8n

Changelog

v0.2 — Agregado nodo Google Sheets (Append), guía de credenciales y Cell Format = RAW.

v0.1 — Webhook → Send Email + Mailhog.