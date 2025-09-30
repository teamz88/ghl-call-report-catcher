# 📞 Call Report Catcher

TidyYourSales platformasidan avtomatik hisobot olish va n8n webhook'ga yuborish tizimi.

## 🚀 Xususiyatlar

- 🔐 OTP bilan avtomatik login
- 📧 Email orqali OTP kodni olish
- 📊 CSV hisobot yuklab olish
- 🔗 N8N webhook integratsiyasi
- 🌐 Playwright bilan brauzer avtomatizatsiyasi

## ⚙️ O'rnatish

### 1. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
playwright install
```

### 2. Ishga tushirish
```bash
python login_automation.py
```

## 📁 Fayl tuzilishi

```
callreportcatcher/
├── 🔧 app.py                 # Email OTP olish
├── 🤖 login_automation.py    # Asosiy avtomatizatsiya
├── 📤 report_sender.py       # CSV qayta ishlash va webhook
├── ⚙️ .env                   # Muhit o'zgaruvchilari
└── 📊 reports/               # Yuklab olingan CSV fayllar
```

## 🔄 Ish jarayoni

1. **🔐 Kirish** - TidyYourSales platformasiga kirish
2. **📧 OTP** - Email'dan OTP kodni olish va tasdiqlash
3. **📊 Hisobot** - Oxirgi kunlik hisobotni yuklab olish
4. **📤 Yuborish** - Ma'lumotlarni n8n webhook'ga yuborish

## 🛠️ Sozlamalar

Barcha sozlamalar <mcfile name=".env" path="/Users/bro/PROJECTS/callreportcatcher/.env"></mcfile> faylida:

- `TIDYYOURSALES_EMAIL` - Login email
- `TIDYYOURSALES_PASSWORD` - Parol
- `N8N_WEBHOOK_URL` - Webhook manzili
- `BROWSER_HEADLESS` - Brauzer rejimi (true/false)

## 🔍 Muammolarni hal qilish

### ❌ Login xatosi
- Email va parolni tekshiring
- Target URL to'g'riligini tasdiqlang

### ❌ OTP topilmadi
- Email sozlamalarini tekshiring
- Spam papkasini ko'ring

### ❌ Webhook xatosi
- N8N webhook URL'ni tekshiring
- Internet aloqasini tekshiring

## 🔒 Xavfsizlik

- `.env` faylini hech qachon git'ga commit qilmang
- Parollarni muntazam o'zgartiring
- Minimal ruxsatlardan foydalaning

---
*Ichki foydalanish uchun mo'ljallangan*