from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
# 🎯 تحديث الاستيراد ليكون مطلقاً:
from Backend.app.database import get_db
from Backend.app import models, schemas
from Backend.services.ai_service import AIService

router = APIRouter()
ai_handler = AIService()  # استدعاء الكلاس من الـ services

@router.post("/generate-description", response_model=schemas.DescriptionResponse)
def api_generate_description(
    request: schemas.DescriptionRequest, 
    key_code: str, 
    db: Session = Depends(get_db)
):
    """
    مسار توليد الأوصاف التسويقية للمنتجات بالاعتماد على المحرك المستقبلي.
    """
    db_key = db.query(models.ActivationKey).filter(models.ActivationKey.key_code == key_code).first()
    if not db_key or not db_key.is_active:
        raise HTTPException(status_code=403, detail="رخصة التفعيل غير صالحة")

    # تشغيل خدمة التوليد
    result_text = ai_handler.generate_product_description(request.product_name, request.features)
    
    # تدوين حركة المرور بنوع الخدمة التسويقية الجديدة
    log = models.TrafficLog(key_code=key_code, action_type="AI_DESCRIPTION", images_count=0)
    db.add(log)
    db.commit()

    return {
        "success": True,
        "product_name": request.product_name,
        "generated_description": result_text
    }