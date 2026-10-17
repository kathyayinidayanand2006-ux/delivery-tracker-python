"""Interactive Modern Web UI for Food Delivery Order Tracker."""

UI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Food Delivery Order Tracker — Operational Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-primary: #090d16;
      --bg-secondary: #0f172a;
      --bg-card: rgba(17, 24, 39, 0.75);
      --border: rgba(255, 255, 255, 0.08);
      --border-focus: #38bdf8;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.25);
      --success: #10b981;
      --success-glow: rgba(16, 185, 129, 0.2);
      --warning: #f59e0b;
      --danger: #ef4444;
      --purple: #a855f7;
      --radius: 12px;
      --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background: radial-gradient(circle at 10% 20%, #1e1b4b 0%, #0a0f1d 50%, #030712 100%);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.5;
      padding-bottom: 60px;
    }

    header {
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 50;
    }

    .header-inner {
      max-width: 1280px;
      margin: 0 auto;
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .logo-icon {
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, #38bdf8, #818cf8);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      box-shadow: 0 4px 14px var(--accent-glow);
    }

    .brand h1 {
      font-size: 1.25rem;
      font-weight: 700;
      background: linear-gradient(to right, #f8fafc, #93c5fd);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .brand p {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .status-badges {
      display: flex;
      gap: 12px;
      align-items: center;
    }

    .badge {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 500;
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--border);
    }

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--text-muted);
    }

    .dot.online {
      background: var(--success);
      box-shadow: 0 0 10px var(--success);
      animation: pulse 2s infinite;
    }

    .dot.offline {
      background: var(--danger);
      box-shadow: 0 0 10px var(--danger);
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(1.1); }
    }

    main {
      max-width: 1280px;
      margin: 32px auto;
      padding: 0 24px;
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 28px;
    }

    @media (max-width: 980px) {
      main { grid-template-columns: 1fr; }
    }

    .card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 24px;
      backdrop-filter: blur(12px);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .card-title {
      font-size: 1.1rem;
      font-weight: 600;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: #e2e8f0;
    }

    .form-group {
      margin-bottom: 16px;
    }

    label {
      display: block;
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--text-muted);
      margin-bottom: 6px;
    }

    input, select, textarea {
      width: 100%;
      padding: 10px 14px;
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text);
      font-family: inherit;
      font-size: 0.9rem;
      transition: var(--transition);
    }

    input:focus, select:focus, textarea:focus {
      outline: none;
      border-color: var(--border-focus);
      box-shadow: 0 0 0 3px var(--accent-glow);
    }

    button {
      cursor: pointer;
      font-family: inherit;
      font-size: 0.875rem;
      font-weight: 600;
      padding: 10px 18px;
      border-radius: 8px;
      border: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: var(--transition);
    }

    .btn-primary {
      background: linear-gradient(135deg, #0284c7, #38bdf8);
      color: #fff;
      box-shadow: 0 4px 14px var(--accent-glow);
      width: 100%;
    }

    .btn-primary:hover {
      background: linear-gradient(135deg, #0369a1, #0284c7);
      transform: translateY(-1px);
    }

    .btn-sm {
      padding: 6px 12px;
      font-size: 0.8rem;
    }

    .btn-action {
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.3);
    }

    .btn-action:hover {
      background: rgba(56, 189, 248, 0.25);
    }

    .btn-danger {
      background: rgba(239, 68, 68, 0.15);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .btn-danger:hover {
      background: rgba(239, 68, 68, 0.25);
    }

    .btn-delete {
      background: rgba(148, 163, 184, 0.1);
      color: #cbd5e1;
      border: 1px solid rgba(148, 163, 184, 0.2);
    }

    .btn-delete:hover {
      background: rgba(239, 68, 68, 0.2);
      color: #ef4444;
      border-color: rgba(239, 68, 68, 0.4);
    }

    /* Orders feed */
    .order-card {
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
      margin-bottom: 16px;
      transition: var(--transition);
    }

    .order-card:hover {
      border-color: rgba(56, 189, 248, 0.4);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
    }

    .order-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }

    .order-id {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.95rem;
      font-weight: 600;
      color: #38bdf8;
    }

    .status-tag {
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      padding: 4px 10px;
      border-radius: 9999px;
      letter-spacing: 0.05em;
    }

    .status-placed { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .status-accepted { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    .status-cooking { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .status-out_for_delivery { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .status-delivered { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .status-cancelled { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

    .order-meta {
      font-size: 0.85rem;
      color: var(--text-muted);
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 12px;
    }

    .order-meta strong {
      color: #f1f5f9;
    }

    .progress-bar-container {
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.06);
      border-radius: 9999px;
      margin-bottom: 14px;
      overflow: hidden;
    }

    .progress-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #38bdf8, #10b981);
      transition: width 0.4s ease;
    }

    .order-items {
      font-size: 0.825rem;
      background: rgba(0, 0, 0, 0.2);
      border-radius: 6px;
      padding: 8px 12px;
      margin-bottom: 14px;
      color: #cbd5e1;
    }

    .order-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      justify-content: flex-end;
    }

    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #1e293b;
      border: 1px solid var(--border);
      padding: 12px 20px;
      border-radius: 8px;
      color: #fff;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      z-index: 100;
      opacity: 0;
      transform: translateY(20px);
      transition: var(--transition);
      pointer-events: none;
      font-size: 0.875rem;
    }

    .toast.show {
      opacity: 1;
      transform: translateY(0);
    }

    .restaurant-queue-box {
      margin-top: 24px;
      padding-top: 18px;
      border-top: 1px solid var(--border);
    }
  </style>
</head>
<body>

  <header>
    <div class="header-inner">
      <div class="brand">
        <div class="logo-icon">🍔</div>
        <div>
          <h1>Food Delivery Order Tracker</h1>
          <p>Real-time State Machine & Delivery Pipeline Dashboard</p>
        </div>
      </div>
      <div class="status-badges">
        <div class="badge">
          <div id="pgDot" class="dot"></div>
          <span>PostgreSQL: <strong id="pgStatus">Checking...</strong></span>
        </div>
        <div class="badge">
          <div id="redisDot" class="dot"></div>
          <span>Redis: <strong id="redisStatus">Checking...</strong></span>
        </div>
      </div>
    </div>
  </header>

  <main>
    <!-- Left column: Order Placement and Queue View -->
    <section>
      <div class="card">
        <div class="card-title">
          <span>Place New Order</span>
          <span style="font-size: 0.8rem; color: #38bdf8;">POST /orders</span>
        </div>

        <form id="orderForm" onsubmit="createOrder(event)">
          <div class="form-group">
            <label for="customerName">Customer Name</label>
            <input type="text" id="customerName" required placeholder="e.g. Kathyayini / Aditya" value="Kathyayini">
          </div>

          <div class="form-group">
            <label for="restaurantSelect">Restaurant</label>
            <select id="restaurantSelect">
              <option value="Spice Garden">Spice Garden</option>
              <option value="Biryani Junction">Biryani Junction</option>
              <option value="Dosa Corner">Dosa Corner</option>
              <option value="Cafe Milano">Cafe Milano</option>
            </select>
          </div>

          <div class="form-group">
            <label for="dishSelect">Preset Menu Item</label>
            <select id="dishSelect" onchange="updatePriceFromDish()">
              <option value="Butter Chicken,32000">Butter Chicken (₹320.00)</option>
              <option value="Paneer Tikka,24000">Paneer Tikka (₹240.00)</option>
              <option value="Hyderabadi Dum Biryani,28000">Hyderabadi Dum Biryani (₹280.00)</option>
              <option value="Masala Dosa,12000">Masala Dosa (₹120.00)</option>
              <option value="Filter Coffee,4000">Filter Coffee (₹40.00)</option>
            </select>
          </div>

          <div class="form-group">
            <label for="itemPaise">Total (Paise)</label>
            <input type="number" id="itemPaise" value="32000" min="100" required>
            <small style="color: var(--text-muted); font-size: 0.75rem;">100 paise = ₹1.00</small>
          </div>

          <button type="submit" class="btn-primary">
            <span>🚀</span> Place Delivery Order
          </button>
        </form>

        <div class="restaurant-queue-box">
          <div class="card-title" style="margin-bottom: 8px;">
            <span>Restaurant Queue</span>
            <span style="font-size: 0.8rem; color: #a855f7;">GET /restaurants/.../queue</span>
          </div>
          <div style="display: flex; gap: 8px; margin-bottom: 12px;">
            <select id="queueRestaurantSelect" style="flex: 1;">
              <option value="Spice Garden">Spice Garden</option>
              <option value="Biryani Junction">Biryani Junction</option>
              <option value="Dosa Corner">Dosa Corner</option>
              <option value="Cafe Milano">Cafe Milano</option>
            </select>
            <button class="btn-sm btn-action" onclick="fetchQueue()">Check</button>
          </div>
          <div id="queueOutput" style="font-size: 0.8rem; color: var(--text-muted);">Click Check to inspect active kitchen orders.</div>
        </div>
      </div>
    </section>

    <!-- Right column: Active Orders Feed -->
    <section>
      <div class="card">
        <div class="card-title">
          <span>Active Orders & Concurrency Controls</span>
          <div style="display: flex; gap: 8px;">
            <button class="btn-sm btn-action" onclick="refreshOrders()">↻ Refresh</button>
          </div>
        </div>

        <div id="ordersList">
          <div style="text-align: center; color: var(--text-muted); padding: 40px 0;">
            Loading active orders...
          </div>
        </div>
      </div>
    </section>
  </main>

  <div id="toast" class="toast"></div>

  <script>
    const knownOrderIds = new Set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);

    function showToast(msg, isError = false) {
      const toast = document.getElementById('toast');
      toast.innerText = msg;
      toast.style.borderColor = isError ? '#ef4444' : '#10b981';
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 3500);
    }

    async function checkHealth() {
      try {
        const res = await fetch('/health');
        const data = await res.json();
        const pgDot = document.getElementById('pgDot');
        const redisDot = document.getElementById('redisDot');
        const pgStatus = document.getElementById('pgStatus');
        const redisStatus = document.getElementById('redisStatus');

        if (data.postgres) {
          pgDot.className = 'dot online';
          pgStatus.innerText = 'Connected';
        } else {
          pgDot.className = 'dot offline';
          pgStatus.innerText = 'Error';
        }

        if (data.redis) {
          redisDot.className = 'dot online';
          redisStatus.innerText = 'Connected';
        } else {
          redisDot.className = 'dot offline';
          redisStatus.innerText = 'Error';
        }
      } catch (err) {
        document.getElementById('pgDot').className = 'dot offline';
        document.getElementById('redisDot').className = 'dot offline';
        document.getElementById('pgStatus').innerText = 'Offline';
        document.getElementById('redisStatus').innerText = 'Offline';
      }
    }

    function updatePriceFromDish() {
      const val = document.getElementById('dishSelect').value;
      const [_, paise] = val.split(',');
      document.getElementById('itemPaise').value = paise;
    }

    async function createOrder(e) {
      e.preventDefault();
      const customer = document.getElementById('customerName').value.trim();
      const restaurant = document.getElementById('restaurantSelect').value;
      const dishVal = document.getElementById('dishSelect').value;
      const [dishName] = dishVal.split(',');
      const paise = parseInt(document.getElementById('itemPaise').value, 10);

      const payload = {
        customer: customer,
        restaurant: restaurant,
        items: [{ name: dishName, paise: paise }]
      };

      try {
        const res = await fetch('/orders', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Failed to place order');
        }
        const created = await res.json();
        knownOrderIds.add(created.id);
        showToast(`Order #${created.id} placed successfully!`);
        refreshOrders();
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function advanceStatus(oid, targetStatus, expectedStatus) {
      try {
        const res = await fetch(`/orders/${oid}/status`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            to: targetStatus,
            expected: expectedStatus,
            actor: 'Kitchen Staff'
          })
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Status transition rejected');
        }
        showToast(`Order #${oid} moved to ${targetStatus}`);
        refreshOrders();
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function cancelOrder(oid, expectedStatus) {
      if (!confirm(`Cancel order #${oid}? (Allowed only before cooking)`)) return;
      try {
        const res = await fetch(`/orders/${oid}/cancel`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            expected: expectedStatus,
            actor: 'Customer'
          })
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Cancellation rejected');
        }
        showToast(`Order #${oid} cancelled`);
        refreshOrders();
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function deleteOrder(oid) {
      if (!confirm(`Permanently delete order #${oid}? (Only terminal orders)`)) return;
      try {
        const res = await fetch(`/orders/${oid}`, { method: 'DELETE' });
        if (res.status === 204) {
          knownOrderIds.delete(oid);
          showToast(`Order #${oid} deleted from Postgres database`);
          refreshOrders();
          return;
        }
        const err = await res.json();
        throw new Error(err.detail || 'Delete rejected');
      } catch (err) {
        showToast(err.message, true);
      }
    }

    async function fetchQueue() {
      const rest = document.getElementById('queueRestaurantSelect').value;
      const output = document.getElementById('queueOutput');
      output.innerText = 'Fetching queue...';
      try {
        const res = await fetch(`/restaurants/${encodeURIComponent(rest)}/queue`);
        if (res.status === 404) {
          output.innerHTML = `<em>No outstanding orders for ${rest}</em>`;
          return;
        }
        const data = await res.json();
        output.innerHTML = `<strong>${data.outstanding} outstanding</strong> order(s) for ${data.restaurant}.`;
      } catch (err) {
        output.innerText = 'Error loading queue: ' + err.message;
      }
    }

    async function refreshOrders() {
      const container = document.getElementById('ordersList');
      const orderList = [];

      for (const id of Array.from(knownOrderIds).sort((a,b) => b - a)) {
        try {
          const res = await fetch(`/orders/${id}`);
          if (res.ok) {
            const data = await res.json();
            orderList.push(data);
          }
        } catch (_) {}
      }

      if (orderList.length === 0) {
        container.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 40px 0;">No active orders found. Place an order on the left!</div>';
        return;
      }

      container.innerHTML = orderList.map(order => {
        const progressPct = Math.round((order.progress || 0) * 100);
        const isTerminal = order.terminal;
        const canCancel = order.can_cancel;

        let nextActionBtn = '';
        if (order.status === 'placed') {
          nextActionBtn = `<button class="btn-sm btn-action" onclick="advanceStatus(${order.id}, 'accepted', 'placed')">✓ Accept Order</button>`;
        } else if (order.status === 'accepted') {
          nextActionBtn = `<button class="btn-sm btn-action" onclick="advanceStatus(${order.id}, 'cooking', 'accepted')">🍳 Start Cooking</button>`;
        } else if (order.status === 'cooking') {
          nextActionBtn = `<button class="btn-sm btn-action" onclick="advanceStatus(${order.id}, 'out_for_delivery', 'cooking')">🛵 Out for Delivery</button>`;
        } else if (order.status === 'out_for_delivery') {
          nextActionBtn = `<button class="btn-sm btn-action" onclick="advanceStatus(${order.id}, 'delivered', 'out_for_delivery')">🎉 Mark Delivered</button>`;
        }

        const cancelBtn = canCancel ?
          `<button class="btn-sm btn-danger" onclick="cancelOrder(${order.id}, '${order.status}')">✕ Cancel</button>` : '';

        const deleteBtn = isTerminal ?
          `<button class="btn-sm btn-delete" onclick="deleteOrder(${order.id})">🗑 Delete (CRUD)</button>` : '';

        const itemsDesc = (order.items || []).map(i => `${i.name} (₹${(i.paise/100).toFixed(2)})`).join(', ') || 'No items';

        return `
          <div class="order-card">
            <div class="order-header">
              <span class="order-id">Order #${order.id} (v${order.version})</span>
              <span class="status-tag status-${order.status}">${order.status.replace(/_/g, ' ')}</span>
            </div>

            <div class="progress-bar-container">
              <div class="progress-bar-fill" style="width: ${progressPct}%;"></div>
            </div>

            <div class="order-meta">
              <div>Customer: <strong>${order.customer}</strong></div>
              <div>Restaurant: <strong>${order.restaurant}</strong></div>
              <div>Total: <strong>₹${order.total_rupees.toFixed(2)}</strong></div>
              <div>Cache: <strong>${order.cached ? 'Hit (Redis)' : 'Miss (Postgres)'}</strong></div>
            </div>

            <div class="order-items">
              <strong>Items:</strong> ${itemsDesc}
            </div>

            <div class="order-actions">
              ${nextActionBtn}
              ${cancelBtn}
              ${deleteBtn}
            </div>
          </div>
        `;
      }).join('');
    }

    // Initialize
    checkHealth();
    refreshOrders();
    setInterval(checkHealth, 5000);
    setInterval(refreshOrders, 10000);
  </script>
</body>
</html>
"""
