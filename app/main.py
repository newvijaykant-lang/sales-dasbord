from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
from pathlib import Path

app = FastAPI()

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_sales.csv"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    # Simple aggregation from sample CSV: total sales per product
    try:
        df = pd.read_csv(DATA_PATH)
        df['total'] = df['quantity'] * df['price']
        agg = df.groupby('product', as_index=False)['total'].sum()
        result = agg.to_dict(orient='records')
        return JSONResponse(content={"totals": result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


CLOCK_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Digital World Clock</title>
    <style>
      body { font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; padding: 2rem; background: #f7fafc; }
      h1 { margin-bottom: 0.5rem }
      .clocks { display: flex; flex-wrap: wrap; gap: 1rem; }
      .clock { background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); width: 200px; }
      .zone { font-weight: 600; }
      .time { font-size: 1.4rem; margin-top: 0.5rem }
      .controls { margin-bottom: 1rem }
      select, button { padding: 0.4rem 0.6rem; margin-right: 0.5rem }
    </style>
  </head>
  <body>
    <h1>Digital World Clock</h1>
    <p>Displays the current time in multiple time zones. Use the menu to add more zones.</p>

    <div class="controls">
      <select id="tz-select"></select>
      <button id="add-btn">Add Zone</button>
      <button id="clear-btn">Clear All</button>
    </div>

    <div class="clocks" id="clocks"></div>

    <script>
      const commonTimeZones = [
        'UTC',
        'Europe/London',
        'Europe/Berlin',
        'America/New_York',
        'America/Los_Angeles',
        'Asia/Kolkata',
        'Asia/Tokyo',
        'Australia/Sydney'
      ];

      const tzSelect = document.getElementById('tz-select');
      const clocks = document.getElementById('clocks');
      const addBtn = document.getElementById('add-btn');
      const clearBtn = document.getElementById('clear-btn');

      function populateSelect() {
        tzSelect.innerHTML = '';
        commonTimeZones.forEach(tz => {
          const opt = document.createElement('option');
          opt.value = tz;
          opt.textContent = tz;
          tzSelect.appendChild(opt);
        });
      }

      function createClockElement(zone) {
        const el = document.createElement('div');
        el.className = 'clock';
        el.dataset.zone = zone;
        el.innerHTML = `
          <div class="zone">${zone}</div>
          <div class="time" id="time-${zone.replace(/[/]/g,'-')}">--:--:--</div>
        `;
        return el;
      }

      function updateClocks() {
        document.querySelectorAll('.clock').forEach(card => {
          const zone = card.dataset.zone;
          const timeEl = card.querySelector('.time');
          try {
            const now = new Date();
            const s = now.toLocaleString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false, timeZone: zone });
            timeEl.textContent = s;
          } catch (err) {
            timeEl.textContent = 'Invalid TZ';
          }
        });
      }

      function addZone(zone) {
        // prevent duplicates
        if (document.querySelector(`.clock[data-zone="${zone}"]`)) return;
        const el = createClockElement(zone);
        clocks.appendChild(el);
        updateClocks();
      }

      addBtn.addEventListener('click', () => {
        const zone = tzSelect.value;
        if (zone) addZone(zone);
      });

      clearBtn.addEventListener('click', () => {
        clocks.innerHTML = '';
      });

      // initialize
      populateSelect();
      // add a few defaults
      ['UTC','Europe/London','America/New_York'].forEach(z => addZone(z));
      updateClocks();
      setInterval(updateClocks, 500);
    </script>
  </body>
</html>
"""


@app.get("/clock", response_class=HTMLResponse)
async def clock():
    return HTMLResponse(content=CLOCK_HTML)
