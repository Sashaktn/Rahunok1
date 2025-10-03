import React, { useEffect, useState } from 'react';
import InvoiceForm from './InvoiceForm';

function App() {
  const [invoices, setInvoices] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editInvoice, setEditInvoice] = useState(null);

  const fetchInvoices = () => {
    fetch('http://localhost:8000/invoices')
      .then(res => res.json())
      .then(data => {
        // Сортуємо: спочатку за датою (спадання), потім за номером рахунку (спадання)
        data.sort((a, b) => {
          const dateA = new Date(a.date);
          const dateB = new Date(b.date);
          if (dateA > dateB) return -1;
          if (dateA < dateB) return 1;
          // Якщо дати однакові — сортуємо за номером рахунку (як число, спадання)
          const numA = parseInt(a.number, 10);
          const numB = parseInt(b.number, 10);
          if (!isNaN(numA) && !isNaN(numB)) {
            if (numA > numB) return -1;
            if (numA < numB) return 1;
          } else {
            // Якщо номер не число — сортуємо як рядок
            if (a.number > b.number) return -1;
            if (a.number < b.number) return 1;
          }
          return 0;
        });
        setInvoices(data);
      });
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

  // Завантаження всіх txt-файлів
  const handleDownloadAllTxt = async () => {
    const response = await fetch('http://localhost:8000/invoices/download/all');
    if (!response.ok) {
      alert('Не вдалося завантажити файли');
      return;
    }
    const blob = await response.blob();
    // Створюємо посилання для завантаження
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'all_invoices.txt';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  // Завантажити всі документи для рахунку (zip)
  const handleDownloadAllDocs = async (inv) => {
    const url = `http://localhost:8000/invoices/${inv.id}/archive`;
    const response = await fetch(url);
    if (!response.ok) {
      alert('Не вдалося завантажити архів');
      return;
    }
    const blob = await response.blob();
    const a = document.createElement('a');
    a.href = window.URL.createObjectURL(blob);
    a.download = `invoice_${inv.number}_docs.zip`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(a.href);
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
                  <div style={{ display: 'flex', gap: 4 }}>
                    <button title="Завантажити всі документи" style={{ width: 36, height: 36, borderRadius: 6, background: '#1976d2', color: 'white', border: 'none', fontSize: 18, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={() => handleDownloadAllDocs(inv)}>
                      <span role="img" aria-label="download">⬇️</span>
                    </button>
                    <button title="Редагувати" style={{ width: 36, height: 36, borderRadius: 6, background: '#ffc107', color: '#333', border: 'none', fontSize: 18, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={() => handleEdit(inv)}>
                      <span role="img" aria-label="edit">✏️</span>
                    </button>
                    <button title="Видалити" style={{ width: 36, height: 36, borderRadius: 6, background: '#f44336', color: 'white', border: 'none', fontSize: 18, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={() => handleDelete(inv.id)}>
                      <span role="img" aria-label="delete">🗑️</span>
                    </button>
                  </div>
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
