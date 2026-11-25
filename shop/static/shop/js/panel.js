/* Panel: ro'yxatdagi rasmchalar va formadagi jonli ko'rinish */
(function(){
  const val = id => { const el = document.getElementById('id_' + id); return el ? el.value : ''; };
  const chk = id => { const el = document.getElementById('id_' + id); return !!(el && el.checked); };
  const sample = [
    {color: '#eb9fb5', dark: '#c96c8a', petals: 8}, {color: '#ffffff', dark: '#d8cfc0', petals: 8},
    {color: '#f4e07c', dark: '#d1a93a', petals: 10}, {color: '#d1567a', dark: '#8f2f4d', petals: 6},
    {color: '#b9a3e0', dark: '#7e63b8', petals: 7}, {color: '#eb9fb5', dark: '#c96c8a', petals: 6},
  ];

  document.querySelectorAll('.p-thumb[data-kind]').forEach(el => {
    if(el.querySelector('img')) return;
    const d = el.dataset, k = d.kind;
    let svg = '';
    if(k === 'flower') svg = bouquetFromFlower({id: d.id, color: d.color, dark: d.dark, bg: d.bg});
    else if(k === 'type') svg = flowerIcon({color: d.color, dark: d.dark, petals: parseInt(d.petals, 10) || 6});
    else if(k === 'wrap') svg = composeBouquet(sample, {seed: 4, wrap: {color: d.color, ribbon: d.ribbon === '1', ribbonColor: '#cf7590'}});
    el.insertAdjacentHTML('afterbegin', svg);
  });

  const box = document.getElementById('livePreview');
  if(!box) return;
  const kind = box.dataset.kind;
  function draw(){
    if(kind === 'flower'){
      const bg = val('bg_color') || '#f8e3ea';
      box.style.background = bg;
      box.innerHTML = bouquetFromFlower({id: 7, color: val('color'), dark: val('dark_color'), bg: bg});
    } else if(kind === 'type'){
      const p = Math.max(1, Math.min(16, parseInt(val('petal_count'), 10) || 6));
      box.style.background = 'transparent';
      box.innerHTML = flowerIcon({color: val('color'), dark: val('dark_color'), petals: p});
    } else {
      box.style.background = 'transparent';
      box.innerHTML = composeBouquet(sample, {seed: 4, wrap: {color: val('color'), ribbon: chk('has_ribbon'), ribbonColor: '#cf7590'}});
    }
  }
  document.querySelectorAll('.p-form input, .p-form select').forEach(i => {
    i.addEventListener('input', draw); i.addEventListener('change', draw);
  });
  draw();
})();
