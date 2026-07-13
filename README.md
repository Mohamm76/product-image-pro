```markdow
# 🚀 Automix Product Photo Enhancer & Marketing Automation (Backend)

نظام خلفي ذكي ومستقر (Backend API) مصمم لخدمة منصة **Automix Smart Systems** لتسريع وتطوير سير عمل المتاجر الإلكترونية من خلال معالجة وتحسين صور المنتجات برمجياً، وأتمتة صناعة المحتوى الإعلاني والتسويقي باستخدام الذكاء الاصطناعي.

---

## 🛠️ التقنيات المستخدمة (Tech Stack)
* **Framework:** FastAPI (Python)
* **Database & ORM:** PostgreSQL & SQLAlchemy
* **Validation:** Pydantic v2
* **Security:** JWT (JSON Web Tokens) & Passlib (Bcrypt)
* **Image Processing:** OpenCV & NumPy

---

## 📂 هيكلية المجلدات الشجرية (Project Structure)
```text
product_photo_enhancer/
├── Backend/
│   ├── api/          # مسارات واجهات البرمجة (Auth, Images, Marketing)
│   └── app/          # الإعدادات المركزية (Database, Models, Schemas, Main)
│   └── services/     # منطق الأعمال (خدمات المعالجة والذكاء الاصطناعي)
├── .env.example      # نموذج لمتغيرات البيئة المطلوبة
├── .gitignore        # الملفات المستبعدة من الرفع
└── requirements.txt  # الحزم والمكتبات المطلوبة

```

---

## 🚀 طريقة التشغيل المحلي (Installation & Setup)

### 1. تجهيز البيئة الوهمية وتثبيت المتطلبات:

```bash
# إنشاء وتفعيل البيئة الوهمية
python -m venv env
source env/Scripts/activate  # لنظام Windows (PowerShell)

# تثبيت المكتبات
pip install -r requirements.txt

```

### 2. إعداد متغيرات البيئة:

قم بإنشاء ملف `.env` في المجلد الرئيسي بناءً على الملف التوضيحي وضَع بيانات الاتصال بقاعدة بيانات PostgreSQL الخاصة بك:

```env
DATABASE_URL=postgresql://postgres:كلمة_المرور@localhost:5432/automix_db

```

### 3. إقلاع الخادم:

```bash
uvicorn Backend.app.main:app --reload

```

عند تشغيل السيرفر، توجه إلى الرابط التفاعلي للاستعراض والتجربة: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

```

---

## 3️⃣ خطوات الرفع النهائي على GitHub 📦

الآن بعد تجهيز الملفات والتأكد من وجود ملف `.gitignore` لحماية ملف الـ `.env` الخاص بكلمة مرور قاعدة البيانات، افتح الـ Terminal ونفذ سلسلة أوامر Git التالية لرفع المشروع:

```powershell
# 1. تهيئة مستودع Git محلي
git init

# 2. إضافة جميع الملفات المصرح بها (سيتم استبعاد الحزم والبيئة تلقائياً بسبب .gitignore)
git add .

# 3. تسجيل التعديلات برقم إصدار أولي
git commit -m "Initial commit: Setup FastAPI backend with PostgreSQL integration"

# 4. تسمية الفرع الرئيسي
git branch -M main

# 5. ربط المستودع المحلي بمستودعك على جيتهب (استبدل الرابط برابط مستودعك الفعلي)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git

# 6. الرفع النهائي
git push -u origin main

```

جهّز هذه الأوراق والملفات الآن ليكون مشروعك جاهزاً ومحمياً بالكامل للرفع، وأخبرني إذا تم الرفع بنجاح لتظهر أيقونة مشروعك خضراء ومضيئة على جيتهب!