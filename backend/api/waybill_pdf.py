from fastapi import APIRouter, HTTPException, Response, Depends
from sqlalchemy.orm import Session
from utils.database import SessionLocal
from models.waybill import Waybill
from models.invoice import Invoice, InvoiceItem
from models.client import Client
from weasyprint import HTML
from jinja2 import Template
from num2words import num2words
from datetime import datetime
import locale

router = APIRouter(prefix="/waybills", tags=["waybills-pdf"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функція для форматування дати українською
MONTHS_UA = [
    '', 'січня', 'лютого', 'березня', 'квітня', 'травня', 'червня',
    'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня'
]
def format_date_ua(dt):
    return f"{dt.day:02d} {MONTHS_UA[dt.month]} {dt.year}"

WAYBILL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<style>
body { font-family: DejaVu Sans, Arial, sans-serif; font-size: 13px; }
table { border-collapse: collapse; width: 100%; margin-top: 10px; }
th, td { border: 1px solid #000; padding: 4px 8px; text-align: left; }
th { background: #f0f0f0; }
.right { text-align: right; }
.center { text-align: center; }
.bold { font-weight: bold; }
</style>
</head>
<body>
<div style="text-align:center; font-weight:bold; font-size:16px; margin-bottom:10px;">Видаткова накладна №{{ waybill.number }} від {{ date_ua }}</div>
<div><span class="bold">Постачальник</span><br>
Фізична особа-підприємець<br>
Чернієнко Олександр Іванович<br>
ІПН 3194110954<br>
Р/р UA563220010000026006340026851<br>
Акціонерне Товариство УНІВЕРСАЛ БАНК<br>
МФО 322001<br>
Адреса: 20500 Черкаська область, Звенигородський район, смт. Катеринопіль, вул. Ватутіна, буд. 25<br>
Не є платником податку на прибуток на загальних підставах.
</div>
<br>
<div><span class="bold">Покупець</span><br>{{ client.name }}{% if client.code %}<br>{{ client.code }}{% endif %}</div>
<br>
<div>Підстава <span style="margin-left:20px;">Рахунок на оплату №{{ waybill.number }}</span></div>
<br>
<table>
<thead>
<tr><th>№</th><th>Товар</th><th>Кількість</th><th>Од.</th><th>Ціна без ПДВ</th><th>Сума всього без ПДВ</th></tr>
</thead>
<tbody>
{% for item in items %}
<tr>
<td class="center">{{ loop.index }}</td>
<td>{{ item.name }}</td>
<td class="center">{{ item.quantity }}</td>
<td class="center">{{ item.unit }}</td>
<td class="right">{{ '%.2f' % item.price }}</td>
<td class="right">{{ '%.2f' % item.total }}</td>
</tr>
{% endfor %}
</tbody>
</table>
<br>
<div class="right">
<span class="bold">Разом без ПДВ:</span> {{ '%.2f' % waybill.total }}<br>
<span class="bold">ПДВ:</span> 0.00<br>
<span class="bold">Разом з ПДВ:</span> {{ '%.2f' % waybill.total }}
</div>
<br>
<div>Всього найменувань: {{ items|length }},<br>
на суму <span class="bold">{{ total_words }}</span></div>
<br>
<div>Від постачальника* ____________________________ Отримав(ла) ____________________________</div>
<br>
<div style="font-size:12px;">Чернієнко Олександр Іванович<br>*Виконавець і відповідальна особа за господарські операції і правильність оформлення  тел: +38 096 827 9701<br>За дорученням №____ від ____</div>
</body>
</html>
'''

def number_to_words(amount):
    hryvnia = int(amount)
    kopiyky = int(round((amount - hryvnia) * 100))
    hryvnia_words = num2words(hryvnia, lang='uk')
    return f"{hryvnia_words} гривень, {kopiyky:02d} копійок. Без ПДВ."

@router.get("/{waybill_id}/pdf")
def get_waybill_pdf(waybill_id: int, db: Session = Depends(get_db)):
    waybill = db.query(Waybill).filter(Waybill.id == waybill_id).first()
    if not waybill:
        raise HTTPException(status_code=404, detail="Waybill not found")
    client = db.query(Client).filter(Client.id == waybill.client_id).first()
    invoice = db.query(Invoice).filter(Invoice.id == waybill.invoice_id).first()
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
    html = Template(WAYBILL_TEMPLATE).render(waybill=waybill, client=client, items=items, total_words=number_to_words(waybill.total))
    pdf = HTML(string=html).write_pdf()
    return Response(content=pdf, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=waybill_{waybill.number}.pdf"})

@router.get("/by-invoice/{invoice_id}/pdf")
def get_waybill_by_invoice_pdf(invoice_id: int, db: Session = Depends(get_db)):
    waybill = db.query(Waybill).filter(Waybill.invoice_id == invoice_id).first()
    if not waybill:
        raise HTTPException(status_code=404, detail="Waybill not found")
    client = db.query(Client).filter(Client.id == waybill.client_id).first()
    invoice = db.query(Invoice).filter(Invoice.id == waybill.invoice_id).first()
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
    date_ua = format_date_ua(waybill.date)
    html = Template(WAYBILL_TEMPLATE).render(waybill=waybill, client=client, items=items, total_words=number_to_words(waybill.total), date_ua=date_ua)
    pdf = HTML(string=html).write_pdf()
    return Response(content=pdf, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=waybill_{waybill.number}.pdf"})
