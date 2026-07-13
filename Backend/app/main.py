from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
  # 🎯 الاستيراد المطلق الصحيح المتوافق مع هيكل مجلداتك الحالي
from Backend.api import auth, images, marketing

# 🛠️ إنشاء جداول قاعدة البيانات (PostgreSQL) تلقائياً عند إقلاع السيرفر إن لم تكن موجودة
Base.metadata.create_all(bind=engine)

# تهيئة تطبيق FastAPI مع تحديد الإصدار والوصف
app = FastAPI(
    title="Automix Pro Enterprise Core API",
    description="النظام المركزي السحابي لإدارة الرخص، معالجة الصور، وأدوات التسويق بالذكاء الاصطناعي للمتاجر السعودية",
    version="2.0.0"
)

# 🔒 تفعيل إعدادات الحماية ومشاركة الموارد (CORS Middleware)
# تتيح هذه الإعدادات لواجهة Streamlit أو أي تطبيق جوال مستقبلي الاتصال بالسيرفر بأمان وبدون حجب
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في بيئة الإنتاج الفعلي، يفضل استبدال "*" برابط موقعك الحقيقي لزيادة الأمان
    allow_credentials=True,
    allow_methods=["*"],  # السماح بجميع أنواع الطلبات (GET, POST, PUT, DELETE)
    allow_headers=["*"],
)

# 🎯 تجميع وربط المسارات الفرعية (Router Registration) مع تنظيمها بالـ Tags
app.include_router(auth.router, prefix="/api/v1/auth", tags=["إدارة الصلاحيات والأتمتة (Auth & Webhooks)"])
app.include_router(images.router, prefix="/api/v1/images", tags=["محرك معالجة الصور الفني (Image Engine)"])
app.include_router(marketing.router, prefix="/api/v1/marketing", tags=["أدوات الذكاء الاصطناعي والتسويق (AI Marketing)"])

@app.get("/", tags=["الفحص العام (Health Check)"])
def root_status():
    """
    نقطة فحص سلامة السيرفر والتأكد من جاهزيته للعمل.
    """
    return {
        "status": "Operational",
        "system": "Automix Core Backend",
        "version": "2.0.0",
        "target_market": "Saudi Arabia (Salla, Zid, Noon)"
    }