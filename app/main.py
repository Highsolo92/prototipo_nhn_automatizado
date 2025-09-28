from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.models import SessionLocal, init_db, Lead
from app.schemas import LeadIn, LeadOut
from app.services import excel as excel_svc
from app.services.emailer import send_email
from app.services.notifier import notify
from app.rules import RuleEngine, exec_actions
import csv, io, httpx, os

app = FastAPI(title="NHN Ops Hub", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

init_db()
excel_svc.ensure_master()
engine = RuleEngine()
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

# --- DB dependency ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

# --- Core logic shared ---

def _process_lead(db: Session, payload: LeadIn) -> Lead:
    lead = Lead(
        name=payload.name,
        email=payload.email,
        source=payload.source,
        notes=payload.notes,
    )
    actions = engine.apply({
        "name": lead.name,
        "email": lead.email,
        "source": lead.source,
        "notes": lead.notes,
    })
    exec_actions(actions, lead)

    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Excel
    excel_svc.append_lead({
        "id": lead.id,
        "created_at": lead.created_at,
        "name": lead.name,
        "email": lead.email,
        "source": lead.source,
        "priority": lead.priority,
        "status": lead.status,
        "owner": lead.owner,
        "notes": lead.notes,
    })

    # Email (Mailhog en dev)
    try:
        send_email(lead.email, "Registro recibido", "email_confirm.html.j2", {
            "name": lead.name, "priority": lead.priority, "owner": lead.owner
        })
    except Exception:
        pass

    # Notificaciones opcionales
    try:
        notify(f"Nuevo lead: {lead.name} ({lead.email}) prioridad {lead.priority}")
    except Exception:
        pass

    # Webhook a n8n (si está configurado)
    try:
        if N8N_WEBHOOK_URL:
            httpx.post(N8N_WEBHOOK_URL, json={
                "id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "priority": lead.priority,
                "status": lead.status,
                "owner": lead.owner,
                "source": lead.source,
                "notes": lead.notes,
            }, timeout=10)
    except Exception:
        pass

    return lead

# --- Endpoints ---

@app.post("/leads", response_model=LeadOut)
def create_lead(payload: LeadIn, db: Session = Depends(get_db)):
    return _process_lead(db, payload)

@app.get("/leads", response_model=list[LeadOut])
def list_leads(db: Session = Depends(get_db)):
    items = db.query(Lead).order_by(Lead.id.desc()).all()
    return items

@app.post("/leads/import")
def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    count = 0
    for row in reader:
        payload = LeadIn(
            name=row.get("name", ""),
            email=row.get("email", ""),
            source=row.get("source", "csv"),
            notes=row.get("notes", ""),
        )
        _process_lead(db, payload)
        count += 1
    return {"imported": count}

@app.post("/export/daily")
def export_daily(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    path = excel_svc.export_daily(leads)
    return {"report": path}
