from fastapi import APIRouter, HTTPException, Response, Depends
from sqlalchemy.orm import Session
from utils.database import SessionLocal
from models.invoice import Invoice, InvoiceItem
from models.client import Client
from weasyprint import HTML
from jinja2 import Template
from num2words import num2words
import io

router = APIRouter(prefix="/invoices", tags=["invoices-pdf"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

HTML_TEMPLATE = '''
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
<div><span class="bold">Постачальник</span><br>
<span class="bold">Фізична особа-підприємець</span><br>
<span class="bold">Чернієнко Олександр Іванович</span><br>
<span class="bold">ІПН 3194110954</span><br>
<span class="bold">Р/р UA563220010000026006340026851</span><br>
<span class="bold">Акціонерне Товариство УНІВЕРСАЛ БАНК</span><br>
<span class="bold">МФО 322001</span></div>
<br>
<div><span class="bold">Одержувач</span><br>{{ client.name }}{% if client.code %}<br>{{ client.code }}{% endif %}</div>
<br>
<div><span class="bold">Платник</span><br>той самий</div>
<br>
<div class="center"><span class="bold">РАХУНОК №{{ invoice.number }}</span><br>від {{ invoice.date.strftime('%d.%m.%Y') }}</div>
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
<span class="bold">Разом без ПДВ:</span> {{ '%.2f' % invoice.total }}<br>
<span class="bold">ПДВ:</span> 0.00<br>
<span class="bold">Разом з ПДВ:</span> {{ '%.2f' % invoice.total }}
</div>
<br>
<div><span class="bold">Всього на суму:</span> {{ total_words }} </div>
<br>
<div class="bold">Виписав: _______________ Чернієнко О.І.</div>
<br>
<div class="bold">Можливі банківські витрати (комісія банку, плата за переказ грошей тощо) повинні бути оплачені відправником грошових коштів.</div>
</body>
</html>
'''

def number_to_words(amount):
    hryvnia = int(amount)
    kopiyky = int(round((amount - hryvnia) * 100))
    hryvnia_words = num2words(hryvnia, lang='uk')
    return f"{hryvnia_words} гривень, {kopiyky:02d} копійок. Без ПДВ."

@router.get("/{invoice_id}/pdf")
def get_invoice_pdf(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    client = db.query(Client).filter(Client.id == invoice.client_id).first()
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).all()
    html = Template(HTML_TEMPLATE).render(invoice=invoice, client=client, items=items, total_words=number_to_words(invoice.total))
    pdf = HTML(string=html).write_pdf()
    return Response(content=pdf, media_type="application/pdf", headers={"Content-Disposition": f"inline; filename=invoice_{invoice.number}.pdf"})