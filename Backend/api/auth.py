from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
# 🎯 استبدل الاستيراد القديم بالنقاط بهذا الاستيراد المطلق الصريح:
from Backend.app.database import get_db
from Backend.app import models, schemas

router = APIRouter()

@router.post("/verify", response_model=schemas.KeyResponse)
def verify_key(request: schemas.KeyVerifyRequest, db: Session = Depends(get_db)):
    """
    التحقق من صلاحية كود التفعيل وحساب المتبقي في باقة العميل.
    """
    db_key = db.query(models.ActivationKey).filter(models.ActivationKey.key_code == request.key_code).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="كود التفعيل غير موجود بالنظام")
    
    if not db_key.is_active:
        raise HTTPException(status_code=403, detail="هذا الكود تم إيقافه من قبل الإدارة")

    remaining = db_key.max_limit - db_key.used_count
    
    # تدوين حركة التحقق في جدول الـ Traffic
    log = models.TrafficLog(key_code=db_key.key_code, action_type="KEY_VALIDATE", images_count=0)
    db.add(log)
    db.commit()

    return {
        "key_code": db_key.key_code,
        "buyer_email": db_key.buyer_email,
        "max_limit": db_key.max_limit,
        "used_count": db_key.used_count,
        "remaining": remaining,
        "is_active": db_key.is_active,
        "created_at": db_key.created_at
    }

@router.post("/payhip-webhook")
def payhip_webhook_receiver(payload: schemas.PayhipWebhook, db: Session = Depends(get_db)):
    """
    استقبال إشعارات الشراء الفورية من Payhip وتوليد كود تلقائياً للمشتري.
    """
    if "paid" in payload.event or "complete" in payload.event:
        # توليد كود مميز يبدأ بـ AMX للبراند الخاص بك
        new_generated_key = f"AMX-{uuid.uuid4().hex[:8].upper()}"
        
        db_key = models.ActivationKey(
            key_code=new_generated_key,
            buyer_email=payload.email,
            max_limit=100,
            used_count=0
        )
        db.add(db_key)
        db.commit()
        
        return {"status": "success", "issued_key": new_generated_key}
    return {"status": "ignored_event"}