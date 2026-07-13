from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# --- 1. مخططات التحقق من رخص التفعيل (Activation Key Schemas) ---

class KeyVerifyRequest(BaseModel):
    """البيانات المطلوبة عند التحقق من كود التفعيل"""
    key_code: str = Field(..., min_length=4, max_length=50, description="كود التفعيل الفريد للمشترك")

class KeyResponse(BaseModel):
    """البيانات التي يعيدها السيرفر عند نجاح التحقق من الكود"""
    key_code: str
    buyer_email: EmailStr
    max_limit: int
    used_count: int
    remaining: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # تحويل كائنات الـ SQLAlchemy تلقائياً إلى JSON


# --- 2. مخططات ميزات المستقبل التسويقية (AI Marketing Schemas) ---

class DescriptionRequest(BaseModel):
    """المدخلات المطلوبة لتوليد وصف منتج بالذكاء الاصطناعي"""
    product_name: str = Field(..., min_length=2, max_length=150, description="اسم المنتج المراد كتابة وصف له")
    features: Optional[str] = Field(None, max_length=500, description="الخصائص أو النقاط الأساسية للمنتج")

class DescriptionResponse(BaseModel):
    """المخرجات الناتجة بعد توليد الوصف من محرك الـ AI"""
    success: bool
    product_name: str
    generated_description: str


# --- 3. مخطط أتمتة عمليات البيع (Payhip Webhook Schema) ---

class PayhipWebhook(BaseModel):
    """التحقق من البيانات القادمة تلقائياً من منصة Payhip فور حدوث عملية شراء"""
    event: str = Field(..., description="نوع العملية مثل: checkout.paid")
    email: EmailStr = Field(..., description="بريد المشتري لإرسال الكود إليه")
    product_name: str = Field(..., description="اسم الباقة المشتراة")