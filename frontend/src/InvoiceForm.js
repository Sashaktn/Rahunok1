import React, { useEffect, useState } from 'react';

function InvoiceForm({ onBack, invoice }) {
  const [number, setNumber] = useState(invoice?.number || '');
  const [date, setDate] = useState(invoice?.date || new Date().toISOString().slice(0, 10));
  const [clients, setClients] = useState([]);
  const [clientQuery, setClientQuery] = useState(invoice?.client?.name || '');
  const [clientId, setClientId] = useState(invoice?.client_id || invoice?.client?.id || null);
  const [showClientModal, setShowClientModal] = useState(false);
  const [newClient, setNewClient] = useState({ name: '', code: '' });
  const [products, setProducts] = useState([]);
  const [productQuery, setProductQuery] = useState('');
  const [productResults, setProductResults] = useState([]);
  const [items, setItems] = useState(invoice?.items?.map(item => ({ ...item })) || []);
  const [status, setStatus] = useState(invoice?.status || 'draft');

  // Пошук клієнтів
  useEffect(() => {
    fetch('http://localhost:8000/clients')
      .then(res => res.json())
      .then(data => setClients(data));
  }, [showClientModal]);

  // Пошук товарів
  useEffect(() => {
    if (productQuery.length < 2) {
      setProductResults([]);
      return;
    }
    fetch(`http://localhost:8000/products?q=${encodeURIComponent(productQuery)}`)
      .then(res => res.json())
      .then(data => setProductResults(data));
  }, [productQuery]);

  // Додаємо товар у рахунок
  const addProduct = (product) => {
    setItems([...items, {
      name: product.name,
      quantity: 1,
      unit: 'шт.',
      price: parseFloat(product.price) || 0,
      total: parseFloat(product.price) || 0
    }]);
    setProductQuery('');
    setProductResults([]);
  };

  // Оновлення кількості/ціни
  const updateItem = (idx, field, value) => {
    setItems(items => items.map((item, i) =>
      i === idx ? { ...item, [field]: value, total: field === 'quantity' || field === 'price' ? (field === 'quantity' ? value * item.price : item.quantity * value) : item.total } : item
    ));
  };

  // Додавання нового клієнта
  const handleAddClient = () => {
    fetch('http://localhost:8000/clients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newClient)
    })
      .then(res => res.json())
      .then(client => {
        setClients([...clients, client]);
        setClientId(client.id);
        setShowClientModal(false);
        setNewClient({ name: '', code: '' });
      });
  };

  // Підрахунок суми
  const total = items.reduce((sum, item) => sum + (parseFloat(item.total) || 0), 0);

  // Збереження рахунку
  const handleSave = () => {
    const invoiceData = {
      number: number || 'AUTO',
      date,
      client_id: clientId,
      total,
      status,
      items: items.map(item => ({
        name: item.name,
        quantity: parseInt(item.quantity),
        unit: item.unit,
        price: parseFloat(item.price),
        total: parseFloat(item.total)
      }))
    };
    const method = invoice?.id ? 'PUT' : 'POST';
    const url = invoice?.id ? `http://localhost:8000/invoices/${invoice.id}` : 'http://localhost:8000/invoices';
    fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(invoiceData)
    })
      .then(res => res.json())
      .then(() => {
        alert('Рахунок збережено!');
        if (onBack) onBack();
      });
  };

  return (
    <div style={{ maxWidth: 900, margin: '40px auto', fontFamily: 'Arial, sans-serif' }}>
      <h2>{invoice ? 'Редагування рахунку' : 'Створення рахунку'}</h2>
      <div style={{ marginBottom: 16 }}>
        <label>Номер рахунку: <input value={number} onChange={e => setNumber(e.target.value)} placeholder="Авто" /></label>
        <label style={{ marginLeft: 24 }}>Дата: <input type="date" value={date} onChange={e => setDate(e.target.value)} /></label>
      </div>
      <div style={{ marginBottom: 16 }}>
        <label>Одержувач: </label>
        <input
          list="clients-list"
          value={clientQuery}
          onChange={e => {
            setClientQuery(e.target.value);
            const found = clients.find(c => c.name === e.target.value);
            setClientId(found ? found.id : null);
          }}
          placeholder="Почніть вводити назву..."
        />
        <datalist id="clients-list">
          {clients.map(c => <option key={c.id} value={c.name} />)}
        </datalist>
        <button onClick={() => setShowClientModal(true)} style={{ marginLeft: 8 }}>+ Новий клієнт</button>
        {clientId && <span style={{ marginLeft: 16, color: '#555' }}>Код: {clients.find(c => c.id === clientId)?.code}</span>}
      </div>
      <div style={{ marginBottom: 16 }}>
        <label>Додати товар: </label>
        <input
          value={productQuery}
          onChange={e => setProductQuery(e.target.value)}
          placeholder="Почніть вводити назву або артикул..."
        />
        {productResults.length > 0 && (
          <div style={{ border: '1px solid #ccc', background: '#fff', position: 'absolute', zIndex: 10, width: 400 }}>
            {productResults.map(p => (
              <div key={p.id} style={{ padding: 6, cursor: 'pointer' }} onClick={() => addProduct(p)}>
                {p.name} <span style={{ color: '#888' }}>({p.articul || p.id})</span>
              </div>
            ))}
          </div>
        )}
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: 16 }}>
        <thead>
          <tr style={{ background: '#f0f0f0' }}>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Товар</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Кількість</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Од.</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Ціна</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}>Сума</th>
            <th style={{ border: '1px solid #ccc', padding: 8 }}></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, idx) => (
            <tr key={idx}>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>{item.name}</td>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>
                <input type="number" min={1} value={item.quantity} onChange={e => updateItem(idx, 'quantity', parseInt(e.target.value) || 1)} style={{ width: 60 }} />
              </td>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>{item.unit}</td>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>
                <input type="number" min={0} value={item.price} onChange={e => updateItem(idx, 'price', parseFloat(e.target.value) || 0)} style={{ width: 80 }} />
              </td>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>{(item.quantity * item.price).toFixed(2)}</td>
              <td style={{ border: '1px solid #ccc', padding: 8 }}>
                <button onClick={() => setItems(items => items.filter((_, i) => i !== idx))}>Видалити</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ marginBottom: 16, textAlign: 'right', fontWeight: 'bold' }}>
        Разом: {total.toFixed(2)} грн
      </div>
      <div>
        <button onClick={handleSave} style={{ padding: '10px 20px', fontSize: 16 }}>Зберегти рахунок</button>
        <button onClick={onBack} style={{ marginLeft: 16, padding: '10px 20px', fontSize: 16 }}>Повернутися</button>
      </div>
      {showClientModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.3)', zIndex: 100 }}>
          <div style={{ background: '#fff', padding: 24, borderRadius: 8, maxWidth: 400, margin: '100px auto' }}>
            <h3>Новий клієнт</h3>
            <div style={{ marginBottom: 12 }}>
              <input placeholder="Назва" value={newClient.name} onChange={e => setNewClient({ ...newClient, name: e.target.value })} style={{ width: '100%', marginBottom: 8 }} />
              <input placeholder="Код (ІПН, ЄДРПОУ, ГО...)" value={newClient.code} onChange={e => setNewClient({ ...newClient, code: e.target.value })} style={{ width: '100%' }} />
            </div>
            <button onClick={handleAddClient} style={{ marginRight: 8 }}>Додати</button>
            <button onClick={() => setShowClientModal(false)}>Скасувати</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default InvoiceForm;