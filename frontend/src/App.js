import React, { useEffect, useState } from 'react';
import InvoiceForm from './InvoiceForm';

function App() {
  const [invoices, setInvoices] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editInvoice, setEditInvoice] = useState(null);

  const fetchInvoices = () => {
    fetch('http://localhost:8000/invoices')
      .then(res => res.json())
      .then(data => setInvoices(data));
  };

  useEffect(() => {
    if (!showForm) fetchInvoices();
  }, [showForm]);

  const handleDownloadPDF = (id) => {
    window.open(`http://localhost:8000/invoices/${id}/pdf`, '_blank');
  };

  const handleDownloadWaybill = (id) => {
    window.open(`http://localhost:8000/waybills/by-invoice/${id}/pdf`, '_blank');
  };

  const handleDownloadTxt = (id) => {
    window.open(`http://localhost:8000/invoices/${id}/txt`, '_blank');
  };

  const handleEdit = (invoice) => {
    setEditInvoice(invoice);
    setShowForm(true);
  };

  const handleDelete = (id) => {
    if (window.confirm('Ви дійсно хочете видалити рахунок?')) {
      fetch(`http://localhost:8000/invoices/${id}`, { method: 'DELETE' })
        .then(() => fetchInvoices());
    }
  };

  if (showForm) {
    return <InvoiceForm onBack={() => { setShowForm(false); setEditInvoice(null); }} invoice={editInvoice} />;
  }

  return (
    <div style={{ maxWidth: 900, margin: '40px auto', fontFamily: 'Arial, sans-serif' }}>
      <h1>Історія рахунків</h1>
      <button style={{ marginBottom: 20, padding: '10px 20px', fontSize: 18 }} onClick={() => setShowForm(true)}>+ Створити новий рахунок</button>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ background: '#f0f0f0' }}>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>№ Рахунку</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Дата</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Одержувач</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Сума</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Статус</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Дії</th>
          </tr>
        </thead>
        <tbody>
          {invoices.length === 0 ? (
            <tr><td colSpan={6} style={{ textAlign: 'center', padding: 20 }}>Немає рахунків</td></tr>
          ) : (
            invoices.map(inv => (
              <tr key={inv.id}>
                <td style={{ border: '1px solid #ccc', padding: 8 }}>{inv.number}</td>
                <td style={{ border: '1px solid #ccc', padding: 8 }}>{inv.date}</td>
                <td style={{ border: '1px solid #ccc', padding: 8 }}>{inv.client?.name || ''}</td>
                <td style={{ border: '1px solid #ccc', padding: 8 }}>{inv.total}</td>
                <td style={{ border: '1px solid #ccc', padding: 8 }}>{inv.status}</td>
                <td style={{ border: '1px solid #ccc', padding: 8 }}>
                  <button onClick={() => handleDownloadPDF(inv.id)}>Завантажити PDF</button>
                  <button style={{ marginLeft: 8 }} onClick={() => handleDownloadWaybill(inv.id)}>Видаткова накладна</button>
                  <button style={{ marginLeft: 8 }} onClick={() => handleDownloadTxt(inv.id)}>Текстовий файл</button>
                  <button style={{ marginLeft: 8 }} onClick={() => handleEdit(inv)}>Редагувати</button>
                  <button style={{ marginLeft: 8 }} onClick={() => handleDelete(inv.id)}>Видалити</button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export default App;
