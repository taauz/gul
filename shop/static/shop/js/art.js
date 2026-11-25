/* Gul rasmlari (SVG) — sayt va panel uchun umumiy. Tashqi rasm kerak emas. */
let _gid = 0;

function rng(seed){
  let a = (seed >>> 0) || 1;
  return function(){
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
function hex2rgb(h){
  const m = /^#?([0-9a-f]{6})$/i.exec(h || '');
  if(!m) return null;
  const n = parseInt(m[1], 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
function mix(a, b, t){
  const A = hex2rgb(a), B = hex2rgb(b);
  if(!A || !B) return a;
  return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, '0')).join('');
}
const f1 = n => (Math.round(n * 10) / 10).toString();

/* Bitta gul boshi */
function realisticFlower(color, dark, cx, cy, r, petals, rot){
  rot = rot || 0;
  _gid++;
  const gid = 'pg' + _gid;
  const defs = `<defs>
    <radialGradient id="${gid}" cx="42%" cy="18%" r="85%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity=".65"/>
      <stop offset="40%" stop-color="${color}"/>
      <stop offset="100%" stop-color="${dark}"/>
    </radialGradient>
    <filter id="fs${gid}" x="-60%" y="-60%" width="220%" height="220%">
      <feDropShadow dx="0" dy="${f1(r * 0.07)}" stdDeviation="${f1(r * 0.06)}" flood-color="${dark}" flood-opacity="0.35"/>
    </filter>
  </defs>`;

  if(petals <= 1){ // kalla
    const p = `M ${f1(cx)} ${f1(cy + r * .9)} C ${f1(cx - r * .95)} ${f1(cy + r * .25)} ${f1(cx - r * .7)} ${f1(cy - r * .95)} ${f1(cx)} ${f1(cy - r)} C ${f1(cx + r * .7)} ${f1(cy - r * .95)} ${f1(cx + r * .95)} ${f1(cy + r * .25)} ${f1(cx)} ${f1(cy + r * .9)} Z`;
    return `${defs}<g filter="url(#fs${gid})"><path d="${p}" fill="url(#${gid})" stroke="${dark}" stroke-opacity=".3" stroke-width=".6"/>
      <ellipse cx="${f1(cx)}" cy="${f1(cy + r * .05)}" rx="${f1(r * .11)}" ry="${f1(r * .5)}" fill="#f2c94c"/></g>`;
  }

  let outer = '', inner = '', stamens = '';
  const step = 360 / petals;
  for(let i = 0; i < petals; i++){
    const a = step * i + rot, tip = r * 1.08, w = r * (petals > 9 ? 0.2 : 0.34);
    outer += `<g transform="rotate(${f1(a)} ${f1(cx)} ${f1(cy)})">
      <path d="M ${f1(cx)} ${f1(cy)} C ${f1(cx - w)} ${f1(cy - r * .55)} ${f1(cx - w * .5)} ${f1(cy - tip)} ${f1(cx)} ${f1(cy - tip)} C ${f1(cx + w * .5)} ${f1(cy - tip)} ${f1(cx + w)} ${f1(cy - r * .55)} ${f1(cx)} ${f1(cy)} Z" fill="url(#${gid})" stroke="${dark}" stroke-width=".5" stroke-opacity=".3"/>
      <path d="M ${f1(cx)} ${f1(cy - r * .12)} L ${f1(cx)} ${f1(cy - tip * .86)}" stroke="#fff" stroke-width=".6" stroke-opacity=".4" fill="none"/></g>`;
  }
  for(let i = 0; i < petals; i++){
    const a = step * i + step / 2 + rot, tip = r * .62, w = r * (petals > 9 ? 0.13 : 0.2);
    inner += `<path d="M ${f1(cx)} ${f1(cy)} C ${f1(cx - w)} ${f1(cy - r * .3)} ${f1(cx - w * .5)} ${f1(cy - tip)} ${f1(cx)} ${f1(cy - tip)} C ${f1(cx + w * .5)} ${f1(cy - tip)} ${f1(cx + w)} ${f1(cy - r * .3)} ${f1(cx)} ${f1(cy)} Z" fill="${dark}" opacity=".5" transform="rotate(${f1(a)} ${f1(cx)} ${f1(cy)})"/>`;
  }
  const sc = Math.min(petals, 7);
  for(let i = 0; i < sc; i++){
    stamens += `<circle cx="${f1(cx)}" cy="${f1(cy - r * .14)}" r="${f1(Math.max(r * .025, .8))}" fill="#8a6a1f" transform="rotate(${f1(360 / sc * i)} ${f1(cx)} ${f1(cy)})"/>`;
  }
  return `${defs}<g filter="url(#fs${gid})">${outer}${inner}
    <circle cx="${f1(cx)}" cy="${f1(cy)}" r="${f1(r * .16)}" fill="#f4d35e"/>
    <circle cx="${f1(cx)}" cy="${f1(cy)}" r="${f1(r * .16)}" fill="url(#${gid})" opacity=".3"/>${stamens}</g>`;
}

/* Yagona gul belgisi (konstruktor kartalari uchun) */
function flowerIcon(t){
  return `<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">${realisticFlower(t.color, t.dark, 50, 52, 38, t.petals || 6, 12)}</svg>`;
}

/* Qog'ozga o'ralgan buket: blooms = [{color, dark, petals}] */
function composeBouquet(blooms, o){
  o = o || {};
  const rnd = rng(o.seed || 1);
  const n = blooms.length;
  const wrap = Object.assign({color: '#d8bd94', ribbon: false, ribbonColor: '#cf7590'}, o.wrap || {});
  const back = mix(wrap.color, '#000000', .16), panelB = mix(wrap.color, '#ffffff', .05), panelA = mix(wrap.color, '#ffffff', .17);
  const C = {x: 100, y: 76};
  const R = n <= 1 ? 0 : Math.min(50, 14 + 8 * Math.sqrt(n));
  const rb = Math.max(13, Math.min(42, 52 / Math.sqrt(Math.max(n, 1)) + 6));

  let s = '<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">';
  s += '<ellipse cx="100" cy="197" rx="30" ry="3.5" fill="#000" opacity=".10"/>';
  s += `<path d="M46 116 Q100 104 154 116 L108 196 Q100 200 92 196 Z" fill="${back}"/>`;

  if(n > 0){
    const L = 8;
    for(let k = 0; k < L; k++){
      const a = (-165 + k * (150 / (L - 1))) * Math.PI / 180;
      const dist = R * .8 + rb * .7 + 6;
      const x = C.x + dist * Math.cos(a), y = C.y + dist * Math.sin(a) * .78;
      const deg = a * 180 / Math.PI - 90, len = 11 + rb * .3, wid = 5 + rb * .12;
      s += `<g transform="translate(${f1(x)} ${f1(y)}) rotate(${f1(deg)})"><ellipse rx="${f1(wid)}" ry="${f1(len)}" fill="${k % 2 ? '#5b8c67' : '#4c7a58'}"/><path d="M0 ${f1(-len * .9)} L0 ${f1(len * .9)}" stroke="#fff" stroke-opacity=".28" stroke-width=".8"/></g>`;
    }
  }

  const pos = [];
  for(let i = 0; i < n; i++){
    const d = R * Math.sqrt((i + .6) / n), a = i * 2.39996;
    pos.push({x: C.x + d * Math.cos(a), y: C.y + d * Math.sin(a) * .78});
  }
  pos.forEach(p => {
    s += `<path d="M${f1(p.x)} ${f1(p.y)} Q${f1((p.x + 100) / 2)} ${f1((p.y + 128) / 2 + 6)} 100 132" stroke="#4d7a58" stroke-width="1.8" fill="none" opacity=".9"/>`;
  });

  if(o.filler && n > 0){
    for(let k = 0; k < 34; k++){
      const a = rnd() * Math.PI * 2, d = R * .9 + rb * rnd() * 1.2 + 6;
      s += `<circle cx="${f1(C.x + d * Math.cos(a))}" cy="${f1(C.y + d * Math.sin(a) * .78)}" r="${f1(1.3 + rnd() * .9)}" fill="#fff" stroke="#e6dfe8" stroke-width=".3"/>`;
    }
  }

  for(let i = n - 1; i >= 0; i--){
    const b = blooms[i], p = pos[i];
    s += realisticFlower(b.color, b.dark, p.x, p.y, rb * (.9 + .2 * rnd()), b.petals || 6, Math.round(rnd() * 360));
  }

  // old qog'oz (ustma-ust ikki qatlam)
  s += `<path d="M154 116 Q128 124 104 124 L100 198 Q104 199 108 196 Z" fill="${panelB}"/>`;
  s += `<path d="M46 116 Q80 126 114 122 L102 198 Q97 199 92 196 Z" fill="${panelA}" stroke="#000" stroke-opacity=".10" stroke-width=".8"/>`;

  if(wrap.ribbon){
    const rc = wrap.ribbonColor, rd = mix(rc, '#000000', .2);
    s += `<path d="M64 147 Q100 158 136 147 L134 155 Q100 166 66 155 Z" fill="${rc}"/>`;
    s += `<path d="M98 162 L89 182 L95 181 L102 164 Z" fill="${rd}"/><path d="M102 162 L111 182 L105 181 L98 164 Z" fill="${rd}"/>`;
    s += `<path d="M100 159 C82 146 79 169 100 162 C121 169 118 146 100 159 Z" fill="${rc}"/><circle cx="100" cy="160.5" r="3.4" fill="${rd}"/>`;
  }
  return s + '</svg>';
}

/* Tayyor buket: bazadagi Flower ranglaridan avtomatik yig'iladi */
function bouquetFromFlower(f){
  const light = mix(f.color, '#ffffff', .45), deep = mix(f.color, f.dark, .55);
  const recipe = [[f.color, 8], [light, 6], [f.color, 7], [deep, 6], [light, 8], [f.color, 6], [deep, 7], [light, 6], [f.color, 8]];
  return composeBouquet(
    recipe.map(([c, p]) => ({color: c, dark: f.dark, petals: p})),
    {seed: Number(f.id) || 3, filler: true,
     wrap: {color: mix(f.bg, '#d9c3a3', .38), ribbon: true, ribbonColor: f.dark}}
  );
}

if(typeof module !== 'undefined'){ module.exports = {composeBouquet, bouquetFromFlower, flowerIcon, realisticFlower, mix}; }
