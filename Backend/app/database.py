import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from dotenv import load_dotenv

# 1️⃣ تحميل المتغيرات من ملف .env المحلي (الموجود في المجلد الرئيسي)
load_dotenv()

# 2️⃣ قراءة الرابط بأمان: إذا وجد DATABASE_URL في البيئة سيأخذه، وإذا لم يجده سيضع مساراً وهمياً لحماية الكود عند الرفع
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:DUMMY_PASSWORD@localhost:5432/DUMMY_DB_NAME"
)

# إنشاء محرك الاتصال مع تفعيل الـ Pool Management لإدارة الطلبات المتزامنة بكفاءة
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True  # التحقق من سلامة الاتصال قبل إرسال الاستعلامات
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# الـ Dependency المحرك لجميع مسارات الـ API (Yield Session)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()