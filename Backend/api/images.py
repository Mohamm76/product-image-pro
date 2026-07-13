from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from sqlalchemy.orm import Session
import cv2
# 🎯 تحديث الاستيراد ليكون مطلقاً:
from Backend.app.database import get_db
from Backend.app import models
from Backend.services.image_service import process_single_image

router = APIRouter()

@router.post("/process-single")
async def api_process_image(
    key_code: str = Form(...),
    aspect_ratio_type: str = Form("مربع (1024x1024)"),
    brightness_offset: int = Form(0),
    auto_crop: bool = Form(True),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    رفع صورة منتج، التحقق من رصيد العميل، معالجتها، وإعادة الصورة البيضاء النقية فوراً.
    """
    # التحقق من صلاحية الكود والعداد بقاعدة البيانات
    db_key = db.query(models.ActivationKey).filter(models.ActivationKey.key_code == key_code).first()
    if not db_key or not db_key.is_active:
        raise HTTPException(status_code=403, detail="رخصة التفعيل غير صالحة أو تم تجميدها")
        
    if db_key.used_count >= db_key.max_limit:
        raise HTTPException(status_code=403, detail="لقد استهلكت جميع الصور المتاحة في باقتك الحالية")

    # قراءة الملف القادم
    contents = await file.read()
    
    # استدعاء خدمة المعالجة الصافية من مجلد الـ services
    processed_canvas = process_single_image(contents, brightness_offset, auto_crop, aspect_ratio_type)
    
    if processed_canvas is None:
        raise HTTPException(status_code=400, detail="فشلت معالجة ملف الصورة، يرجى التأكد من الصيغة")

    # تحديث العداد وتدوين حركة المرور والمقاس المختار
    db_key.used_count += 1
    log = models.TrafficLog(
        key_code=key_code, 
        action_type="IMAGE_PROCESS", 
        images_count=1,
        platform_target=aspect_ratio_type.split(" ")[0] # أخذ اسم المنصة مثل "مربع" أو "عمودي"
    )
    db.add(log)
    db.commit()

    # تحويل لوحة OpenCV الناتجة إلى بايتات JPEG لإعادتها للواجهة مباشرة
    _, encoded_img = cv2.imencode(".jpg", processed_canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    
    return Response(content=encoded_img.tobytes(), media_type="image/jpeg")