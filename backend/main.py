from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import client, invoice, products, invoice_pdf, waybill_pdf
from utils.database import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(client.router)
app.include_router(invoice.router)
app.include_router(products.router)
app.include_router(invoice_pdf.router)
app.include_router(waybill_pdf.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}