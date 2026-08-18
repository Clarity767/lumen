document.addEventListener('DOMContentLoaded', function () {
    const svg = document.getElementById('floorSvg');
    if (!svg) return; // this page has no floor plan

    const dataEl = document.getElementById('floorplan-data');
    const urlTplEl = document.getElementById('table-detail-url-template');
    const urlTemplate = urlTplEl ? urlTplEl.dataset.template : null;

    let tables = [];
    try {
        tables = JSON.parse(dataEl.textContent) || [];
    } catch (e) {
        console.error('Не вдалося прочитати дані для схеми залу', e);
    }

    const radiusBySeats = s => s <= 2 ? 30 : s <= 4 ? 40 : s <= 6 ? 48 : 56;

    // Auto-layout fallback: any table without pos_x/pos_y gets placed on a grid,
    // sized generously enough that the bigger table shapes don't overlap.
    // Columns adapt to the table count so a handful of tables don't get
    // stretched thin across a wide, mostly-empty canvas.
    const CELL_W = 230, CELL_H = 210, START_X = 150, START_Y = 140;
    const needsLayout = tables.filter(t => t.x == null || t.y == null).length;
    const GRID_COLS = Math.max(1, Math.min(5, Math.ceil(Math.sqrt(needsLayout * 1.3))));
    let gridIndex = 0;
    tables.forEach(t => {
        if (t.x == null || t.y == null) {
            t.x = START_X + (gridIndex % GRID_COLS) * CELL_W;
            t.y = START_Y + Math.floor(gridIndex / GRID_COLS) * CELL_H;
            gridIndex++;
        }
    });

    const svgNS = 'http://www.w3.org/2000/svg';
    const tablesG = document.getElementById('tables');
    const tooltip = document.getElementById('tooltip');
    const stage = document.querySelector('.floor-stage');
    const panel = document.getElementById('floorPanel');
    let selectedId = null;

    function seatDots(cx, cy, ringR, count) {
        const g = document.createElementNS(svgNS, 'g');
        for (let i = 0; i < count; i++) {
            const angle = (i / count) * Math.PI * 2 - Math.PI / 2;
            const dot = document.createElementNS(svgNS, 'circle');
            dot.setAttribute('class', 'seat-dot');
            dot.setAttribute('cx', cx + Math.cos(angle) * ringR);
            dot.setAttribute('cy', cy + Math.sin(angle) * ringR);
            dot.setAttribute('r', 5);
            g.appendChild(dot);
        }
        return g;
    }

    function render() {
        tablesG.innerHTML = '';
        tables.forEach(t => {
            const r = radiusBySeats(t.seats);
            const g = document.createElementNS(svgNS, 'g');
            const isTaken = t.status === 'taken';
            g.setAttribute('class', 'table-group' + (isTaken ? ' reserved' : '') + (t.id === selectedId ? ' selected' : ''));
            g.setAttribute('tabindex', '0');
            g.setAttribute('role', 'button');
            g.setAttribute('aria-label', `${t.title}, ${t.seats} місць, ${isTaken ? 'заброньовано' : 'вільно'}`);

            const shape = document.createElementNS(svgNS, t.seats >= 6 ? 'rect' : 'circle');
            if (t.seats >= 6) {
                shape.setAttribute('x', t.x - r); shape.setAttribute('y', t.y - r * 0.72);
                shape.setAttribute('width', r * 2); shape.setAttribute('height', r * 1.44);
                shape.setAttribute('rx', 6);
            } else {
                shape.setAttribute('cx', t.x); shape.setAttribute('cy', t.y); shape.setAttribute('r', r);
            }
            shape.setAttribute('class', 'table-shape');
            g.appendChild(shape);
            g.appendChild(seatDots(t.x, t.y, r + 18, t.seats));

            const label = document.createElementNS(svgNS, 'text');
            label.setAttribute('class', 'table-label');
            label.setAttribute('x', t.x); label.setAttribute('y', t.y + 3);
            label.textContent = t.seats;
            g.appendChild(label);

            g.addEventListener('mouseenter', e => showTooltip(t, e));
            g.addEventListener('mousemove', positionTooltip);
            g.addEventListener('mouseleave', hideTooltip);
            g.addEventListener('click', () => select(t.id));
            g.addEventListener('keydown', e => {
                if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(t.id); }
            });

            tablesG.appendChild(g);
        });
    }


    function fitViewBox() {
        if (!tables.length) return;
        const PAD = 70;
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        tables.forEach(t => {
            const reach = radiusBySeats(t.seats) + 20; 
            minX = Math.min(minX, t.x - reach);
            maxX = Math.max(maxX, t.x + reach);
            minY = Math.min(minY, t.y - reach);
            maxY = Math.max(maxY, t.y + reach);
        });
        minX -= PAD; minY -= PAD; maxX += PAD; maxY += PAD;
        let w = maxX - minX, h = maxY - minY;


        const minAspectH = w * 0.42;
        if (h < minAspectH) {
            const extra = (minAspectH - h) / 2;
            minY -= extra; h = minAspectH;
        }

        svg.setAttribute('viewBox', `${minX} ${minY} ${w} ${h}`);
    }

    function showTooltip(t, evt) {
        const statusText = t.status === 'taken'
            ? (t.free_from ? `заброньовано · вільно з ${t.free_from}` : 'заброньовано')
            : 'вільно';
        tooltip.innerHTML = `<b>${t.title}</b><br>${t.seats} місць · ${statusText}`;
        tooltip.classList.add('show');
        positionTooltip(evt);
    }
    function positionTooltip(evt) {
        const rect = stage.getBoundingClientRect();
        tooltip.style.left = (evt.clientX - rect.left) + 'px';
        tooltip.style.top = (evt.clientY - rect.top) + 'px';
    }
    function hideTooltip() { tooltip.classList.remove('show'); }

    function select(id) {
        selectedId = id;
        render();
        const t = tables.find(x => x.id === id);
        const free = t.status !== 'taken';
        const detailUrl = urlTemplate ? urlTemplate.replace('999999', id) : '#';
        panel.innerHTML = `
            <h3>${t.title}</h3>
            ${t.zone ? `<span class="zone-tag">${t.zone}</span>` : ''}
            <div class="panel-row">
                <span class="k">Місць</span>
                <div>
                    <span class="v">${t.seats}</span>
                    <div class="seats-row">${'<span></span>'.repeat(t.seats)}</div>
                </div>
            </div>
            <div class="panel-row">
                <span class="k">Ціна</span>
                <span class="v">${t.price} грн</span>
            </div>
            <span class="status-badge ${free ? 'free' : 'taken'}">${free ? 'Вільно' : 'Заброньовано'}</span>
            ${!free && t.free_from ? `<div class="free-from-note">Вільно з ${t.free_from}</div>` : ''}
            ${free
                ? `<a class="btn btn-primary" style="display:block;text-align:center;margin-top:1.1rem;" href="${detailUrl}">Забронювати</a>`
                : `<a class="btn btn-outline-secondary disabled" style="display:block;text-align:center;margin-top:1.1rem;pointer-events:none;" href="#">Недоступно</a>`}
        `;
    }

    fitViewBox();
    render();


    const tabs = document.querySelectorAll('.lm-view-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(b => b.classList.remove('active'));
            tab.classList.add('active');
            const view = tab.dataset.view;
            document.getElementById('floorView').style.display = view === 'floor' ? '' : 'none';
            document.getElementById('listView').style.display = view === 'list' ? '' : 'none';
        });
    });
});