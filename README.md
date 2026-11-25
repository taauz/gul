# Gulzor — Django versiyasi (2-bosqich: ro'yxatdan o'tish + yangilangan panel)

## Yangi nima qo'shildi
- **Ro'yxatdan o'tish**: har bir mijoz buyurtma berish, baholash yoki fikr qoldirishdan oldin ro'yxatdan o'tadi —
  Google orqali (bitta bosishda) yoki ism + telefon raqam va SMS orqali yuboriladigan 6 xonali kod bilan.
- **Gullar rasmi butunlay qayta yozildi**: endi haqiqiy qog'ozga o'ralgan, lentali, barglari bilan buket ko'rinishida
  chiziladi (oldingi versiyadagi tekis "gulbarglar to'plami" emas).
- **Boshqaruv paneli** to'liq yangi dizaynda: bosh sahifa (statistika, so'nggi 7 kunlik grafik), buyurtmalar (holat
  bo'yicha filtr: yangi / tayyorlanmoqda / bajarildi / bekor), **Buketlar** (tayyor sotuvdagilar) va **Dona gullar**
  (konstruktor uchun bittalab gullar) alohida bo'limlarda, mijozlar ro'yxati.
- **Surat yuklash standartlashtirildi**: admin panelda buketga surat yuklasangiz, u avtomatik ravishda kvadrat
  shaklga qirqiladi va fon tozalanadi — barcha rasmlar bir xil o'lchamda, tekis ko'rinadi.
- Buket detali oynasi (bosib ochiladigan) — kattaroq rasm, baholash, fikrlar shu yerda.

## O'rnatish

```bash
cd gulzor_django
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations shop
python manage.py migrate
python manage.py seed_shop          # 16 ta buket, 14 ta dona gul, 5 ta qadoq turini yuklaydi
python manage.py createsuperuser    # panelga kirish uchun

python manage.py runserver
```

- **http://127.0.0.1:8000/** — asosiy sayt
- **http://127.0.0.1:8000/panel/** — boshqaruv paneli (Buketlar / Dona gullar / Qadoqlar / Buyurtmalar / Mijozlar)
- **http://127.0.0.1:8000/admin/** — Django'ning to'liq admin paneli

## Ro'yxatdan o'tishni sozlash

Loyiha ildizida `.env.example` faylini `.env` deb nusxalang va to'ldiring:

```bash
cp .env.example .env      # Windows: copy .env.example .env
```

**Telefon orqali SMS kod** — [Eskiz.uz](https://eskiz.uz) da akkaunt oching, `.env` ga yozing:
```
ESKIZ_EMAIL=sizning@email.com
ESKIZ_PASSWORD=...
```
Agar bu ikkalasi bo'sh qoldirilsa, tizim **sinov rejimida** ishlaydi: SMS yuborish o'rniga kod terminalda
(`runserver` ishlab turgan oynada) chiqadi va ekranda ham ko'rsatiladi — shunday sinab ko'rishingiz mumkin.

**Google orqali kirish** — [Google Cloud Console](https://console.cloud.google.com/apis/credentials) da
"OAuth client ID" (Web application) yarating, ruxsat etilgan manzilga `http://127.0.0.1:8000` qo'shing, olingan
Client ID'ni `.env` ga yozing:
```
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
```
Bo'sh qoldirilsa, tugma ko'rinadi lekin bosilganda "hali sozlanmagan" degan xabar chiqadi — sayt buzilmaydi.

## Loyiha tuzilishi

```
gulzor_django/
  manage.py, gulzor/            — Django sozlamalari
  shop/
    models.py                   — Flower, FlowerType, WrapOption, Order, OrderItem, Profile, PhoneCode, Comment, Rating
    admin.py                    — Django admin
    views.py                    — sahifa + JSON API (reyting, komment, buyurtma)
    auth_api.py, sms.py         — ro'yxatdan o'tish (Google, telefon+SMS kod)
    panel_views.py               — /panel/ boshqaruv paneli (faqat is_staff)
    utils.py                     — yuklangan suratni kvadratga standartlashtirish
    templates/shop/              — index.html (sayt), panel/ (boshqaruv paneli)
    static/shop/
      css/style.css              — yagona umumiy dizayn
      js/art.js                  — gul/buket SVG chizish (sayt va panelda umumiy)
      js/site.js                 — sayt logikasi (savat, ro'yxatdan o'tish, baholash)
      js/panel.js                 — paneldagi jonli ko'rinish
    management/commands/seed_shop.py
```

## Eslatmalar

- `DEBUG=True` va SQLite — faqat local/sinov uchun. Productionga chiqarishdan oldin `.env` da `DEBUG=0` qiling,
  `SECRET_KEY`ni almashtiring va `ALLOWED_HOSTS`ni to'ldiring.
- Reyting va komment qoldirish, shuningdek buyurtma berish — faqat ro'yxatdan o'tgan foydalanuvchilar uchun.
  Ro'yxatdan o'tmagan mijoz shu amallardan birini bosganda avtomatik ro'yxatdan o'tish oynasi ochiladi.
