from fastapi import APIRouter, Depends, HTTPException, File, Response as FastAPIResponse
from sqlalchemy.orm import Session
from schemas.invoice import InvoiceCreate, InvoiceRead
from models.invoice import Invoice, InvoiceItem
from models.client import Client
from models.waybill import Waybill
from utils.database import SessionLocal
from typing import List
from datetime import date
import os

router = APIRouter(prefix="/invoices", tags=["invoices"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=InvoiceRead)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    db_invoice = Invoice(
        number=invoice.number,
        date=invoice.date,
        client_id=invoice.client_id,
        total=invoice.total,
        status=invoice.status
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    # Додаємо позиції рахунку
    for item in invoice.items:
        db_item = InvoiceItem(
            invoice_id=db_invoice.id,
            name=item.name,
            quantity=item.quantity,
            unit=item.unit,
            price=item.price,
            total=item.total
        )
        db.add(db_item)
    db.commit()
    db.refresh(db_invoice)
    # Створення текстового файлу з реквізитами у підпапці
    client = db.query(Client).filter(Client.id == db_invoice.client_id).first()
    txt_dir = os.path.join(os.getcwd(), "invoices_txt")
    os.makedirs(txt_dir, exist_ok=True)
    filename = f"invoice_{db_invoice.number}.txt"
    filepath = os.path.join(txt_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Рахунок №{db_invoice.number} від {db_invoice.date}\n")
        f.write(f"Постачальник: ФОП Чернієнко Олександр Іванович, ІПН 3194110954\n")
        f.write(f"Р/р UA563220010000026006340026851, АТ УНІВЕРСАЛ БАНК, МФО 322001\n")
        f.write(f"Адреса: 20500 Черкаська обл., смт. Катеринопіль, вул. Ватутіна, 25\n")
        f.write(f"Покупець: {client.name if client else ''}{(' (' + client.code + ')') if client and client.code else ''}\n")
        f.write(f"\nТовари:\n")
        for item in invoice.items:
            f.write(f"- {item.name}, {item.quantity} {item.unit}, {item.price} грн, на суму {item.total} грн\n")
        f.write(f"\nВсього до сплати: {db_invoice.total} грн\n")
    return db_invoice

@router.get("/", response_model=List[InvoiceRead])
def read_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Invoice).offset(skip).limit(limit).all()

@router.get("/{invoice_id}", response_model=InvoiceRead)
def read_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.put("/{invoice_id}", response_model=InvoiceRead)
def update_invoice(invoice_id: int, invoice: InvoiceCreate, db: Session = Depends(get_db)):
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db_invoice.number = invoice.number
    db_invoice.date = invoice.date
    db_invoice.client_id = invoice.client_id
    db_invoice.total = invoice.total
    db_invoice.status = invoice.status
    # Оновлюємо позиції рахунку
    db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()
    for item in invoice.items:
        db_item = InvoiceItem(
            invoice_id=invoice_id,
            name=item.name,
            quantity=item.quantity,
            unit=item.unit,
            price=item.price,
            total=item.total
        )
        db.add(db_item)
    # Оновлюємо або створюємо відповідну видаткову накладну
    db_waybill = db.query(Waybill).filter(Waybill.invoice_id == invoice_id).first()
    if db_waybill:
        db_waybill.number = invoice.number
        db_waybill.date = invoice.date
        db_waybill.client_id = invoice.client_id
        db_waybill.total = invoice.total
        db_waybill.status = 'created'
    else:
        db_waybill = Waybill(
            invoice_id=invoice_id,
            number=invoice.number,
            date=invoice.date,
            client_id=invoice.client_id,
            total=invoice.total,
            status='created'
        )
        db.add(db_waybill)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()
    db.delete(db_invoice)
    db.commit()
    return {"ok": True}

@router.get("/{invoice_id}/txt")
def download_invoice_txt(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    filename = f"invoice_{invoice.number}.txt"
    txt_dir = os.path.join(os.getcwd(), "invoices_txt")
    filepath = os.path.join(txt_dir, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Text file not found")
    with open(filepath, "rb") as f:
        content = f.read()
    return FastAPIResponse(content, media_type="text/plain", headers={"Content-Disposition": f"attachment; filename={filename}"})