document.addEventListener('DOMContentLoaded', function () {
    const svg = document.getElementById('locatorSvg');
    if (!svg) return;

    const dataEl = document.getElementById('locator-data');
    const currentIdEl = document.getElementById('current-table-id');
    const urlTplEl = document.getElementById('table-detail-url-template');
    const urlTemplate = urlTplEl ? urlTplEl.dataset.template : null;
    const currentId = currentIdEl ? parseInt(currentIdEl.dataset.id, 10) : null;

    let tables = [];
    try {
        tables = JSON.parse(dataEl.textContent) || [];
    } catch (e) {
        console.error('Не вдалося прочитати дані для міні-схеми', e);
        return;
    }
    if (!tables.length) return;

    // Same grid fallback as the main floor plan, kept compact since this
    // widget only needs to communicate relative position, not exact seating.
    const CELL_W = 26, CELL_H = 24, START_X = 18, START_Y = 18;
    const needsLayout = tables.filter(t => t.x == null || t.y == null).length;
    const cols = Math.max(1, Math.min(6, Math.ceil(Math.sqrt(needsLayout * 1.3))));
    let gridIndex = 0;
    tables.forEach(t => {
        if (t.x == null || t.y == null) {
            t.x = START_X + (gridIndex % cols) * CELL_W;
            t.y = START_Y + Math.floor(gridIndex / cols) * CELL_H;
            gridIndex++;
        }
    });

    const svgNS = 'http://www.w3.org/2000/svg';
    const g = document.getElementById('locatorTables');

    tables.forEach(t => {
        const isCurrent = t.id === currentId;
        const r = isCurrent ? 7.5 : 5;

        const node = document.createElementNS(svgNS, 'g');
        node.setAttribute('class', 'locator-table' + (isCurrent ? ' current' : ''));

        if (isCurrent) {
            const ring = document.createElementNS(svgNS, 'circle');
            ring.setAttribute('cx', t.x); ring.setAttribute('cy', t.y);
            ring.setAttribute('r', r + 4);
            ring.setAttribute('class', 'locator-pulse');
            node.appendChild(ring);
        }

        const dot = document.createElementNS(svgNS, 'circle');
        dot.setAttribute('cx', t.x); dot.setAttribute('cy', t.y); dot.setAttribute('r', r);
        dot.setAttribute('class', 'locator-dot');
        node.appendChild(dot);

        if (isCurrent) {
            const label = document.createElementNS(svgNS, 'text');
            label.setAttribute('x', t.x); label.setAttribute('y', t.y - r - 6);
            label.setAttribute('class', 'locator-here');
            label.setAttribute('text-anchor', 'middle');
            label.textContent = 'Ви тут';
            node.appendChild(label);
        } else if (urlTemplate) {
            node.style.cursor = 'pointer';
            node.addEventListener('click', () => {
                window.location.href = urlTemplate.replace('999999', t.id);
            });
            const title = document.createElementNS(svgNS, 'title');
            title.textContent = t.title;
            node.appendChild(title);
        }

        g.appendChild(node);
    });

    // Fit viewBox tightly around all tables.
    const PAD = 14;
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    tables.forEach(t => {
        const reach = (t.id === currentId ? 12 : 6);
        minX = Math.min(minX, t.x - reach);
        maxX = Math.max(maxX, t.x + reach);
        minY = Math.min(minY, t.y - reach);
        maxY = Math.max(maxY, t.y + reach);
    });
    minX -= PAD; minY -= PAD; maxX += PAD; maxY += PAD;
    let w = maxX - minX, h = maxY - minY;
    const minAspectH = w * 0.65;
    if (h < minAspectH) { minY -= (minAspectH - h) / 2; h = minAspectH; }
    svg.setAttribute('viewBox', `${minX} ${minY} ${w} ${h}`);
});