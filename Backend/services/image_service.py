import cv2
import numpy as np

def process_single_image(image_bytes: bytes, brightness_offset: int = 0, auto_crop: bool = True, aspect_ratio_type: str = "مربع (1024x1024)") -> np.ndarray:
    """
    المحرك الذكي لتحسين صور المنتجات وتوسيطها على خلفية بيضاء نقية 100% وفقاً لأبعاد المنصات السعودية.
    """
    # قراءة مصفوفة بايتات الصورة وتحويلها إلى OpenCV Matrix
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None

    h_orig, w_orig = img.shape[:2]

    # 1. تحسين الإضاءة والألوان عبر خوارزمية CLAHE لإزالة الضباب والغمامة
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    img_enhanced = cv2.merge((cl, a, b))
    img_enhanced = cv2.cvtColor(img_enhanced, cv2.COLOR_LAB2BGR)
    
    # تطبيق التعديل اليدوي على السطوع إذا تم تزويده
    if brightness_offset != 0:
        img_enhanced = cv2.convertScaleAbs(img_enhanced, alpha=1.0, beta=brightness_offset)
    
    # 2. الاقتصاص التلقائي الذكي (Auto-Crop) لمعالجة الحواف وهوامش الأمان
    img_cropped = img_enhanced.copy()
    if auto_crop:
        gray = cv2.cvtColor(img_enhanced, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        edged = cv2.Canny(blurred, 30, 130)
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            large_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(large_contour) > (h_orig * w_orig * 0.05):
                x, y, w, h = cv2.boundingRect(large_contour)
                padding = int(max(w, h) * 0.08)  # هامش أمان 8%
                
                y1, y2 = max(0, y - padding), min(h_orig, y + h + padding)
                x1, x2 = max(0, x - padding), min(w_orig, x + w + padding)
                
                if (y2 - y1) > 50 and (x2 - x1) > 50:
                    img_cropped = img_enhanced[y1:y2, x1:x2]

    # 3. تحديد أبعاد اللوحة المستهدفة بناءً على الخيار المحدد للمنصة
    if "عمودي" in aspect_ratio_type:
        target_w, target_h = 1080, 1350
    elif "أفقي" in aspect_ratio_type:
        target_w, target_h = 1200, 628
    else:  # المربع القياسي لسلة وزد ونون
        target_w, target_h = 1024, 1024

    # تغيير حجم المنتج مع الحفاظ على التناسب البصري (Aspect Ratio) لمنع التمطيط
    h_c, w_c = img_cropped.shape[:2]
    scale = min(target_w / w_c, target_h / h_c)
    new_w, new_h = int(w_c * scale), int(h_c * scale)
    
    img_resized = cv2.resize(img_cropped, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    
    # إنشاء اللوحة البيضاء الثلجية النقية (RGB 255) بالكامل
    final_canvas = np.ones((target_h, target_w, 3), dtype=np.uint8) * 255
    
    # حساب نقطة المنتصف لتوسيط السلعة رياضياً بالسنتر تماماً
    x_offset = (target_w - new_w) // 2
    y_offset = (target_h - new_h) // 2
    final_canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
    
    return final_canvas