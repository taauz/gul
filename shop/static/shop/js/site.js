(function(){
'use strict';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const readJSON = id => JSON.parse(document.getElementById(id).textContent);
const money = n => Number(n).toLocaleString('ru-RU') + " so'm";
const fmtPhone = p => { const d = String(p).replace(/\D/g, ''); return d.length === 12 ? `+${d.slice(0, 3)} ${d.slice(3, 5)} ${d.slice(5, 8)} ${d.slice(8, 10)} ${d.slice(10)}` : (p ? '+' + d : ''); };
const lum = hex => { const m = /^#([0-9a-f]{6})$/i.exec(hex || ''); if(!m) return 1; const n = parseInt(m[1], 16); return (0.299 * (n >> 16 & 255) + 0.587 * (n >> 8 & 255) + 0.114 * (n & 255)) / 255; };

let ME = readJSON('me-data');
const CFG = readJSON('config-data');
const FLOWERS = readJSON('flowers-data');
const TYPES = readJSON('types-data');
const WRAPS = readJSON('wraps-data');

/* ---------- API ---------- */
function csrf(){ const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/); return m ? decodeURIComponent(m[1]) : ''; }
async function api(url, body){
  try{
    const r = await fetch(url, {method: 'POST', credentials: 'same-origin',
      headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()}, body: JSON.stringify(body || {})});
    let data = {};
    try{ data = await r.json(); }catch(e){}
    data.status = r.status;
    if(data.ok === undefined) data.ok = r.ok;
    return data;
  }catch(e){
    return {ok: false, status: 0, error: "Tarmoq xatosi. Internetni tekshiring."};
  }
}

/* ---------- toast, modallar ---------- */
function toast(msg){
  const t = $('#toast'); t.textContent = msg; t.classList.add('show');
  clearTimeout(t._tm); t._tm = setTimeout(() => t.classList.remove('show'), 3000);
}
const overlay = $('#overlay');
function closeAll(keepOverlay){
  $$('.modal.show, .drawer.show').forEach(e => e.classList.remove('show'));
  if(!keepOverlay === true){ overlay.classList.remove('show'); document.body.classList.remove('noscroll'); }
}
function openEl(el){ closeAll(true); overlay.classList.add('show'); el.classList.add('show'); document.body.classList.add('noscroll'); }
overlay.addEventListener('click', () => closeAll());
$$('[data-close]').forEach(b => b.addEventListener('click', () => closeAll()));
document.addEventListener('keydown', e => { if(e.key === 'Escape') closeAll(); });

/* ---------- gul barglari (tepadan tushadi) ---------- */
(function(){
  if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const wrap = $('#petals'), n = window.innerWidth < 640 ? 10 : 18;
  for(let i = 0; i < n; i++){
    const p = document.createElement('div');
    p.className = 'petal';
    p.style.left = (Math.random() * 100) + 'vw';
    p.style.animationDuration = (9 + Math.random() * 10) + 's';
    p.style.animationDelay = (Math.random() * -20) + 's';
    p.style.setProperty('--drift', (Math.random() * 160 - 80) + 'px');
    p.style.setProperty('--s', (.6 + Math.random() * .9).toFixed(2));
    p.style.background = i % 2 ? 'linear-gradient(135deg,#f3cdd7,#e8aab9)' : 'linear-gradient(135deg,#e8aab9,#d1849a)';
    wrap.appendChild(p);
  }
})();

/* ---------- foydalanuvchi ---------- */
function renderUser(){
  const slot = $('#userSlot');
  if(!ME.auth){
    slot.innerHTML = '<button class="btn small ghost" id="loginBtn" type="button">Kirish</button>';
    $('#loginBtn').onclick = () => openAuth();
    return;
  }
  const ini = esc((ME.name || '?').trim().charAt(0).toUpperCase());
  slot.innerHTML = `<div class="umenu"><button class="avatar" id="uBtn" type="button" aria-label="Profil">${ini}</button>
    <div class="umenu-pop" id="uPop"><div class="u-name">${esc(ME.name)}</div><div class="u-sub">${esc(ME.phone ? fmtPhone(ME.phone) : ME.email)}</div>
    ${ME.is_staff ? `<a class="u-link" href="${esc(CFG.panel_url)}">Boshqaruv paneli</a>` : ''}
    <button class="u-link" id="logoutBtn" type="button">Chiqish</button></div></div>`;
  $('#uBtn').onclick = e => { e.stopPropagation(); $('#uPop').classList.toggle('open'); };
  $('#logoutBtn').onclick = async () => { await api('/api/auth/logout/'); ME = {auth: false}; renderUser(); toast('Tizimdan chiqdingiz'); };
}
document.addEventListener('click', () => { const p = $('#uPop'); if(p) p.classList.remove('open'); });

function requireAuth(action, afterLogin){
  if(ME.auth) return action();
  openAuth(() => { if(afterLogin) afterLogin(); action(); });
}

/* ---------- ro'yxatdan o'tish oynasi ---------- */
let pending = null, authName = '', authPhone = '', otpTimer = null, verifying = false, gStarted = false;
const err1 = m => { $('#authErr1').textContent = m || ''; };
const err2 = m => { $('#authErr2').textContent = m || ''; };

function showStep(n){ $('#authStep1').hidden = n !== 1; $('#authStep2').hidden = n !== 2; err1(''); err2(''); }
function openAuth(after){
  pending = after || null;
  showStep(1);
  const art = $('#authArt');
  if(!art.innerHTML.trim()){
    art.innerHTML = composeBouquet([
      {color: '#eb9fb5', dark: '#c96c8a', petals: 8}, {color: '#ffffff', dark: '#d8cfc0', petals: 8}, {color: '#f4e07c', dark: '#d1a93a', petals: 10},
      {color: '#d1567a', dark: '#8f2f4d', petals: 6}, {color: '#b9a3e0', dark: '#7e63b8', petals: 7}, {color: '#f6b79a', dark: '#d98461', petals: 6},
      {color: '#eb9fb5', dark: '#c96c8a', petals: 6}, {color: '#ffffff', dark: '#d8cfc0', petals: 10}, {color: '#f4e07c', dark: '#d1a93a', petals: 8},
    ], {seed: 11, filler: true, wrap: {color: '#f1e2d0', ribbon: true, ribbonColor: '#cf7590'}});
  }
  initGoogle();
  openEl($('#authModal'));
  setTimeout(() => $('#aName').focus(), 250);
}

const G_ICON = '<svg viewBox="0 0 48 48" width="18" height="18"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>';
function initGoogle(){
  const holder = $('#gBtn');
  if(gStarted) return;
  if(!CFG.google_client_id){
    holder.innerHTML = `<button class="g-fake" type="button">${G_ICON}<span>Google orqali davom etish</span></button>`;
    holder.firstChild.onclick = () => toast('Google orqali kirish hali sozlanmagan (.env ichida GOOGLE_CLIENT_ID kerak)');
    gStarted = true; return;
  }
  const start = () => {
    google.accounts.id.initialize({client_id: CFG.google_client_id, callback: onGoogle});
    google.accounts.id.renderButton(holder, {theme: 'outline', size: 'large', shape: 'pill', width: 280, text: 'continue_with'});
    gStarted = true;
  };
  if(window.google && google.accounts) return start();
  const sc = document.createElement('script');
  sc.src = 'https://accounts.google.com/gsi/client'; sc.async = true; sc.onload = start;
  sc.onerror = () => { holder.innerHTML = '<div class="form-err">Google yuklanmadi. Internetni tekshiring.</div>'; };
  document.head.appendChild(sc);
}
async function onGoogle(resp){
  const res = await api('/api/auth/google/', {credential: resp.credential});
  if(res.ok) loginDone(res.user); else err1(res.error || "Google orqali kirib bo'lmadi");
}

$('#aPhone').addEventListener('input', e => {
  let d = e.target.value.replace(/\D/g, '');
  if(d.length > 9 && d.startsWith('998')) d = d.slice(3);
  d = d.slice(0, 9);
  e.target.value = [d.slice(0, 2), d.slice(2, 5), d.slice(5, 7), d.slice(7, 9)].filter(Boolean).join(' ');
});

async function doSend(name, digits, btn){
  if(btn) btn.disabled = true;
  const res = await api('/api/auth/send-code/', {name, phone: '998' + digits});
  if(btn) btn.disabled = false;
  if(res.ok || res.wait){
    authName = name; authPhone = digits;
    goStep2(res.wait || 60, res.dev_code);
    if(!res.ok) err2(res.error);
  }else{
    (($('#authStep2').hidden) ? err1 : err2)(res.error || 'Xatolik');
  }
}
$('#authSend').onclick = () => {
  const name = $('#aName').value.trim(), digits = $('#aPhone').value.replace(/\D/g, '');
  if(name.length < 2) return err1('Ismingizni kiriting');
  if(digits.length !== 9) return err1("Telefon raqamini to'liq kiriting");
  err1(''); doSend(name, digits, $('#authSend'));
};
$('#authResend').onclick = () => doSend(authName, authPhone, $('#authResend'));
$('#authBack').onclick = () => { clearInterval(otpTimer); showStep(1); };

const otpCode = () => $$('#otp input').map(i => i.value).join('');
function buildOtp(){
  const box = $('#otp');
  box.innerHTML = Array.from({length: 6}, (_, i) => `<input inputmode="numeric" maxlength="1" autocomplete="off" aria-label="Kod ${i + 1}">`).join('');
  const ins = $$('input', box);
  ins.forEach((inp, i) => {
    inp.addEventListener('input', () => {
      inp.value = inp.value.replace(/\D/g, '').slice(-1);
      if(inp.value && ins[i + 1]) ins[i + 1].focus();
      if(otpCode().length === 6) verify();
    });
    inp.addEventListener('keydown', e => { if(e.key === 'Backspace' && !inp.value && ins[i - 1]) ins[i - 1].focus(); });
    inp.addEventListener('paste', e => {
      const t = ((e.clipboardData || window.clipboardData).getData('text') || '').replace(/\D/g, '').slice(0, 6);
      if(!t) return;
      e.preventDefault();
      t.split('').forEach((c, k) => { ins[k].value = c; });
      ins[Math.min(t.length, 5)].focus();
      if(t.length === 6) verify();
    });
  });
}
function startTimer(sec){
  clearInterval(otpTimer);
  const btn = $('#authResend'); let left = sec;
  const tick = () => {
    btn.textContent = left > 0 ? `Qayta yuborish (${Math.floor(left / 60)}:${String(left % 60).padStart(2, '0')})` : 'Qayta yuborish';
    btn.disabled = left > 0;
    if(left <= 0) clearInterval(otpTimer);
    left--;
  };
  tick(); otpTimer = setInterval(tick, 1000);
}
function goStep2(wait, devCode){
  buildOtp(); showStep(2);
  $('#authSent').textContent = `${fmtPhone('998' + authPhone)} raqamiga SMS kod yuborildi`;
  const hint = $('#devHint');
  if(devCode){ hint.hidden = false; hint.textContent = `Test rejimi: kod ${devCode} (haqiqiy SMS uchun .env ga ESKIZ kalitlarini kiriting)`; }
  else hint.hidden = true;
  startTimer(wait);
  setTimeout(() => { const f = $('#otp input'); if(f) f.focus(); }, 100);
}
async function verify(){
  if(verifying) return;
  if(otpCode().length !== 6) return err2("Kodni to'liq kiriting");
  verifying = true; $('#authVerify').disabled = true;
  const res = await api('/api/auth/verify/', {phone: '998' + authPhone, code: otpCode(), name: authName});
  verifying = false; $('#authVerify').disabled = false;
  if(res.ok) return loginDone(res.user);
  err2(res.error || 'Xatolik');
  $$('#otp input').forEach(i => { i.value = ''; });
  $('#otp input').focus();
  if(res.expired){ clearInterval(otpTimer); const b = $('#authResend'); b.disabled = false; b.textContent = 'Qayta yuborish'; }
}
$('#authVerify').onclick = verify;

function loginDone(user){
  ME = user; renderUser(); closeAll();
  toast(`Xush kelibsiz, ${ME.name}!`);
  const p = pending; pending = null;
  if(p) setTimeout(p, 300);
}

/* ---------- savat ---------- */
const CART_KEY = 'gulzor_cart_v2';
let cart = [];
try{ const c = JSON.parse(localStorage.getItem(CART_KEY)); if(Array.isArray(c)) cart = c; }catch(e){}
cart = cart.filter(i => i && i.qty > 0 && (i.type === 'custom' || (i.type === 'ready' && FLOWERS.some(f => f.id === i.id))));
cart.forEach(i => { if(i.type === 'ready'){ const f = FLOWERS.find(x => x.id === i.id); i.price = f.price; i.name = f.name; i.color = f.color; } });
const saveCart = () => { try{ localStorage.setItem(CART_KEY, JSON.stringify(cart)); }catch(e){} };
const cartCount = () => cart.reduce((a, i) => a + i.qty, 0);
const cartTotal = () => cart.reduce((a, i) => a + i.price * i.qty, 0);
function updateBadges(){ $('#badgeTop').textContent = cartCount(); $('#badgeFab').textContent = cartCount(); }
function bump(){ const fab = $('#openCartFab'); fab.classList.remove('bump'); void fab.offsetWidth; fab.classList.add('bump'); }
function addToCart(item){
  const ex = item.type === 'ready' && cart.find(c => c.type === 'ready' && c.id === item.id);
  if(ex) ex.qty = Math.min(50, ex.qty + 1); else cart.push(Object.assign({qty: 1}, item));
  saveCart(); updateBadges(); bump();
  toast(`${item.name} savatga qo'shildi`);
}
function renderCart(){
  const body = $('#cartBody');
  if(!cart.length){
    body.innerHTML = '<div class="empty">Savat hozircha bo\u2018sh<span>Buketlardan tanlang yoki o\u2018zingiz yasang.</span></div>';
  }else{
    body.innerHTML = cart.map((it, i) => `<div class="cart-item">
      <span class="dot" style="background:${esc(it.color || '#e8aab9')}"></span>
      <div class="ci-main"><div class="ci-name">${esc(it.name)}</div><div class="ci-sub">${it.type === 'custom' ? esc(it.details) : money(it.price)}</div></div>
      <div class="ci-side">
        <div class="stepper sm"><button type="button" data-dec="${i}">−</button><span>${it.qty}</span><button type="button" data-inc="${i}">+</button></div>
        <b>${money(it.price * it.qty)}</b>
        <button class="link-btn" type="button" data-rm="${i}">O'chirish</button>
      </div></div>`).join('');
  }
  $('#cartTotal').textContent = money(cartTotal());
}
$('#cartBody').addEventListener('click', e => {
  const t = e.target.closest('[data-inc],[data-dec],[data-rm]'); if(!t) return;
  const i = +(t.dataset.inc ?? t.dataset.dec ?? t.dataset.rm), it = cart[i]; if(!it) return;
  if(t.dataset.inc !== undefined) it.qty = Math.min(50, it.qty + 1);
  else if(t.dataset.dec !== undefined) it.qty -= 1;
  else it.qty = 0;
  cart = cart.filter(x => x.qty > 0);
  saveCart(); updateBadges(); renderCart();
});
function openCart(){ renderCart(); openEl($('#cartDrawer')); }
$('#openCartTop').onclick = openCart;
$('#openCartFab').onclick = openCart;

/* ---------- buyurtma ---------- */
let selectedPay = 'Naqd';
$$('#payOpts .seg-opt').forEach(o => o.addEventListener('click', () => {
  $$('#payOpts .seg-opt').forEach(x => x.classList.remove('active'));
  o.classList.add('active'); selectedPay = o.dataset.pay;
}));
function openCheckout(){
  $('#cName').value = ME.name || '';
  $('#cPhone').value = ME.phone ? fmtPhone(ME.phone) : '';
  openEl($('#checkoutModal'));
}
$('#goCheckout').onclick = () => {
  if(!cart.length) return toast("Avval savatga mahsulot qo'shing");
  requireAuth(openCheckout);
};
$('#submitOrder').onclick = async () => {
  const name = $('#cName').value.trim(), phone = $('#cPhone').value.trim(), addr = $('#cAddr').value.trim();
  if(name.length < 2 || phone.replace(/\D/g, '').length < 9) return toast("Ism va telefon raqamini to'g'ri kiriting");
  const btn = $('#submitOrder'); btn.disabled = true;
  const res = await api('/api/order/', {
    customer: {name, phone, addr, pay: selectedPay},
    items: cart.map(i => ({type: i.type, id: i.id, qty: i.qty, selections: i.selections || null, wrap: i.wrap || null})),
  });
  btn.disabled = false;
  if(res.status === 401){ closeAll(); ME = {auth: false}; renderUser(); return openAuth(openCheckout); }
  if(res.ok){
    cart = []; saveCart(); updateBadges(); closeAll();
    toast("Buyurtmangiz qabul qilindi! To'lov mahsulotni olishda amalga oshadi.");
  }else toast(res.error || 'Buyurtma yuborilmadi');
};

/* ---------- tayyor buketlar ---------- */
const starSVG = on => `<svg viewBox="0 0 20 20" class="st ${on ? 'on' : ''}"><path d="M10 1.5l2.6 5.6 6.1.6-4.6 4.1 1.3 6-5.4-3.1-5.4 3.1 1.3-6L1.3 7.7l6.1-.6L10 1.5z"/></svg>`;
const stars = avg => [1, 2, 3, 4, 5].map(i => starSVG(i <= Math.round(avg))).join('');
const artOf = f => f.image ? `<img src="${esc(f.image)}" alt="${esc(f.name)}" loading="lazy">` : bouquetFromFlower(f);

function sortedFlowers(){
  const a = FLOWERS.slice(), m = $('#sortSel').value;
  if(m === 'asc') a.sort((x, y) => x.price - y.price);
  else if(m === 'desc') a.sort((x, y) => y.price - x.price);
  else if(m === 'rating') a.sort((x, y) => y.avg - x.avg || y.cnt - x.cnt);
  return a;
}
function cardHTML(f, idx){
  const chips = (f.discount ? `<span class="chip sale">-${f.discount}%</span>` : '') + (f.badge ? `<span class="chip">${esc(f.badge)}</span>` : '');
  return `<article class="card" style="--i:${idx}">
    <button class="art" type="button" data-open="${f.id}" style="background:${esc(f.bg)}" aria-label="${esc(f.name)} haqida batafsil">${artOf(f)}<span class="chips">${chips}</span></button>
    <div class="card-body">
      <h3 class="c-name" data-open="${f.id}">${esc(f.name)}</h3>
      <div class="c-rate">${stars(f.avg)}<span>${f.cnt ? f.avg.toFixed(1) + ' (' + f.cnt + ')' : 'Baho yo\u2018q'}</span></div>
      <div class="c-price"><b>${money(f.price)}</b>${f.old ? `<s>${money(f.old)}</s>` : ''}</div>
      <button class="btn primary block" type="button" data-add="${f.id}">Savatga qo'shish</button>
    </div></article>`;
}
function renderGrid(){
  const grid = $('#grid');
  if(!FLOWERS.length){ grid.innerHTML = '<p class="lead">Hozircha buketlar yo\u2018q.</p>'; return; }
  grid.innerHTML = sortedFlowers().map(cardHTML).join('');
  const io = new IntersectionObserver(es => es.forEach(en => { if(en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); } }), {threshold: .12});
  $$('#grid .card').forEach(c => io.observe(c));
}
$('#sortSel').addEventListener('change', renderGrid);
$('#grid').addEventListener('click', e => {
  const add = e.target.closest('[data-add]');
  if(add){
    const f = FLOWERS.find(x => x.id === +add.dataset.add);
    addToCart({type: 'ready', id: f.id, name: f.name, price: f.price, color: f.color});
    add.classList.remove('pulse'); void add.offsetWidth; add.classList.add('pulse');
    return;
  }
  const open = e.target.closest('[data-open]');
  if(open) openProduct(+open.dataset.open);
});

/* ---------- buket oynasi: baho va fikrlar ---------- */
let curId = null;
const flowerById = id => FLOWERS.find(f => f.id === id);
function renderPmRate(f){
  let h = '<div class="stars-i" role="group" aria-label="Baholash">';
  for(let i = 5; i >= 1; i--) h += `<button type="button" class="star-b ${i <= Math.round(f.avg) ? 'on' : ''}" data-star="${i}" aria-label="${i} yulduz">${starSVG(false)}</button>`;
  h += `</div><span class="rate-txt">${f.cnt ? f.avg.toFixed(1) + ' · ' + f.cnt + ' ta baho' : 'Birinchi bo\u2018lib baholang'}</span>`;
  $('#pmRate').innerHTML = h;
}
function renderPmComments(f){
  $('#pmComments').innerHTML = f.comments.length
    ? f.comments.map(c => `<div class="cm"><b>${esc(c.name)}</b><p>${esc(c.text)}</p></div>`).join('')
    : '<div class="cm empty-cm">Hali fikr yo\u2018q. Birinchi bo\u2018ling.</div>';
}
function openProduct(id){
  const f = flowerById(id); if(!f) return;
  curId = id;
  $('#pmArt').style.background = f.bg;
  $('#pmArt').innerHTML = artOf(f);
  $('#pmName').textContent = f.name;
  $('#pmPrice').innerHTML = `<b>${money(f.price)}</b>${f.old ? `<s>${money(f.old)}</s>` : ''}`;
  $('#pmDesc').textContent = f.desc || ''; $('#pmDesc').hidden = !f.desc;
  $('#pmText').value = '';
  renderPmRate(f); renderPmComments(f);
  openEl($('#productModal'));
}
$('#pmAdd').onclick = () => { const f = flowerById(curId); addToCart({type: 'ready', id: f.id, name: f.name, price: f.price, color: f.color}); };
$('#pmRate').addEventListener('click', e => {
  const b = e.target.closest('[data-star]'); if(!b) return;
  const id = curId, v = +b.dataset.star;
  requireAuth(async () => {
    const res = await api(`/api/flower/${id}/rating/`, {value: v});
    if(res.ok){
      const f = flowerById(id); f.avg = res.avg; f.cnt = res.cnt;
      renderPmRate(f); renderGrid(); toast('Bahoyingiz uchun rahmat!');
    }else toast(res.error || 'Baho qabul qilinmadi');
  }, () => openProduct(id));
});
$('#pmSend').onclick = () => {
  const id = curId, text = $('#pmText').value.trim();
  if(!text) return;
  requireAuth(async () => {
    const res = await api(`/api/flower/${id}/comment/`, {text});
    if(res.ok){
      const f = flowerById(id); f.comments.unshift(res.comment);
      $('#pmText').value = ''; renderPmComments(f); toast('Fikringiz qo\u2018shildi');
    }else toast(res.error || 'Fikr yuborilmadi');
  }, () => { openProduct(id); $('#pmText').value = text; });
};
$('#pmText').addEventListener('keydown', e => { if(e.key === 'Enter') $('#pmSend').click(); });

/* ---------- o'zim yasayman (konstruktor) ---------- */
let selections = {};
let activeWrap = WRAPS.length ? WRAPS[0].id : null;
const wrapById = id => WRAPS.find(w => w.id === id);
const selCount = () => Object.values(selections).reduce((a, b) => a + b, 0);
function builderTotal(){
  let sum = 0;
  TYPES.forEach(t => { sum += t.price * (selections[t.id] || 0); });
  const w = wrapById(activeWrap);
  return sum + (w && selCount() ? w.price : 0);
}
function bloomsFromSelections(){
  const lists = TYPES.filter(t => (selections[t.id] || 0) > 0)
    .map(t => Array.from({length: selections[t.id]}, () => ({color: t.color, dark: t.dark, petals: t.petals})));
  const out = [];
  for(let i = 0, more = true; more; i++){
    more = false;
    lists.forEach(l => { if(l[i]){ out.push(l[i]); more = true; } });
  }
  return out.slice(0, 30);
}
function wrapStyle(w){
  const c = w ? w.color : '#c9a56b';
  return {color: c, ribbon: w ? w.ribbon : false, ribbonColor: lum(c) < .4 ? '#e6c36a' : '#cf7590'};
}
function renderPreview(){
  const n = selCount();
  $('#previewBox').innerHTML = composeBouquet(bloomsFromSelections(), {seed: 5, filler: n > 5, wrap: wrapStyle(wrapById(activeWrap))})
    + (n ? '' : '<div class="pv-hint">Gullarni tanlang — dasta shu yerda yig\u2018iladi</div>');
  $('#previewCount').textContent = n ? `${n} ta gul` : 'Gul tanlanmagan';
  $('#builderTotal').textContent = 'Jami: ' + money(builderTotal());
}
function renderTypeGrid(){
  $('#typeGrid').innerHTML = TYPES.map(t => `<div class="type-card">
    <div class="t-icon">${flowerIcon(t)}</div>
    <div class="tname">${esc(t.name)}</div>
    <div class="tprice">${money(t.price)} / dona</div>
    <div class="stepper"><button type="button" data-dec="${t.id}" aria-label="Kamaytirish">−</button><span id="qty-${t.id}">${selections[t.id] || 0}</span><button type="button" data-inc="${t.id}" aria-label="Ko'paytirish">+</button></div>
  </div>`).join('');
}
$('#typeGrid').addEventListener('click', e => {
  const b = e.target.closest('[data-inc],[data-dec]'); if(!b) return;
  const id = +(b.dataset.inc ?? b.dataset.dec), cur = selections[id] || 0;
  selections[id] = b.dataset.inc !== undefined ? Math.min(60, cur + 1) : Math.max(0, cur - 1);
  const span = $('#qty-' + id); span.textContent = selections[id];
  span.classList.remove('bump'); void span.offsetWidth; span.classList.add('bump');
  renderPreview();
});
function renderWrapOptions(){
  $('#wrapOptions').innerHTML = WRAPS.map(w => `<button type="button" class="wrap-opt ${w.id === activeWrap ? 'active' : ''}" data-w="${w.id}"><span class="dot" style="background:${esc(w.color)}"></span>${esc(w.name)} <em>+${money(w.price)}</em></button>`).join('');
}
$('#wrapOptions').addEventListener('click', e => {
  const b = e.target.closest('[data-w]'); if(!b) return;
  activeWrap = +b.dataset.w; renderWrapOptions(); renderPreview();
});
$('#addCustom').onclick = () => {
  if(!selCount()) return toast('Kamida bitta gul tanlang');
  const w = wrapById(activeWrap);
  const parts = TYPES.filter(t => selections[t.id] > 0).map(t => `${t.name} x${selections[t.id]}`);
  addToCart({
    type: 'custom', name: "O'zi yasagan dasta", price: builderTotal(), color: '#e8aab9',
    selections: Object.assign({}, selections), wrap: activeWrap,
    details: parts.join(', ') + (w ? ' · ' + w.name : ''),
  });
  selections = {}; renderTypeGrid(); renderPreview();
};

/* ---------- buyurtmalarim ---------- */
const ordersPop = $('#ordersPop');
let ordersLoaded = false;
function renderOrders(list){
  const body = $('#ordersBody');
  if(!list.length){ body.innerHTML = '<div class="op-empty">Hali buyurtmalaringiz yo\u2018q.</div>'; return; }
  body.innerHTML = list.map(o => `<div class="op-item">
    <div class="op-head"><b>#${o.id} · ${money(o.total)}</b><span class="pill st-${esc(o.status)}">${esc(o.status_label)}</span></div>
    <div class="op-items">${o.items.map(i => esc(i.name) + ' ×' + i.qty).join(', ')}</div>
    <div class="op-items">${esc(o.date)} · ${esc(o.pay)}</div>
  </div>`).join('');
}
async function loadOrders(){
  const body = $('#ordersBody');
  body.innerHTML = '<div class="op-empty">Yuklanmoqda…</div>';
  const res = await api('/api/my-orders/');
  if(res.ok){ ordersLoaded = true; renderOrders(res.orders); }
  else body.innerHTML = '<div class="op-empty">Yuklab bo\u2018lmadi</div>';
}
$('#openOrders').onclick = e => {
  e.stopPropagation();
  requireAuth(() => {
    const willOpen = !ordersPop.classList.contains('open');
    ordersPop.classList.toggle('open');
    if(willOpen) loadOrders();
  });
};
document.addEventListener('click', e => { if(!e.target.closest('.orders-slot')) ordersPop.classList.remove('open'); });

/* ---------- musiqa (fon uchun, lokal audio fayl) ---------- */
(function(){
  const btn = $('#musicBtn'), iconPlay = $('#musicIconPlay'), iconPause = $('#musicIconPause');
  const audio = $('#bgMusic');
  if(!audio) return;
  audio.volume = 0.6;

  function setPlayingUI(on){
    iconPlay.hidden = on; iconPause.hidden = !on;
    btn.classList.toggle('playing', on);
  }
  audio.addEventListener('playing', () => setPlayingUI(true));
  audio.addEventListener('pause', () => setPlayingUI(false));
  audio.addEventListener('error', () => {
    setPlayingUI(false); btn.classList.remove('loading');
    toast("Musiqa fayli topilmadi. Loyihada shop/static/shop/audio/bg-music.m4a borligini tekshiring.");
  });

  btn.addEventListener('click', () => {
    if(audio.paused){
      btn.classList.add('loading');
      audio.play().then(() => btn.classList.remove('loading'))
        .catch(() => { btn.classList.remove('loading'); toast("Brauzer ovozni avtomatik yoqishga ruxsat bermadi, tugmani qayta bosing."); });
    } else {
      audio.pause();
    }
  });
})();

/* ---------- bosh sahifa rasmi ---------- */
$('#heroArt').innerHTML = composeBouquet([
  {color: '#eb9fb5', dark: '#c96c8a', petals: 8}, {color: '#ffffff', dark: '#d8cfc0', petals: 8}, {color: '#f4e07c', dark: '#d1a93a', petals: 10},
  {color: '#d1567a', dark: '#8f2f4d', petals: 6}, {color: '#b9a3e0', dark: '#7e63b8', petals: 7}, {color: '#f6b79a', dark: '#d98461', petals: 6},
  {color: '#eb9fb5', dark: '#c96c8a', petals: 6}, {color: '#ffffff', dark: '#d8cfc0', petals: 10}, {color: '#f4e07c', dark: '#d1a93a', petals: 8},
  {color: '#d1567a', dark: '#8f2f4d', petals: 8}, {color: '#f6cfe0', dark: '#d193b0', petals: 8},
], {seed: 21, filler: true, wrap: {color: '#f1e2d0', ribbon: true, ribbonColor: '#cf7590'}});

/* ---------- header soyasi ---------- */
window.addEventListener('scroll', () => $('.site-header').classList.toggle('scrolled', window.scrollY > 30), {passive: true});

/* ---------- boshlash ---------- */
renderUser();
renderGrid();
renderTypeGrid();
renderWrapOptions();
renderPreview();
updateBadges();
})();
