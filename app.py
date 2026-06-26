import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import zipfile
from datetime import datetime

# ========== 1. إعدادات الهوية البصرية ==========
st.set_page_config(
    page_title="ProductImage Pro | مُحسن صور المنتجات",
    page_icon="📷",
    layout="centered"
)

st.markdown("""
    <style>
    .main-title { color: #0A192F; text-align: center; font-size: 2.6rem; font-weight: bold; margin-bottom: 5px; }
    .main-title span { color: #C5A880; }
    .sub-title { color: #64748B; text-align: center; font-size: 1.1rem; margin-bottom: 30px; }
    .stButton>button { background-color: #C5A880 !important; color: #0A192F !important; font-weight: bold !important; width: 100%; border-radius: 8px !important; height: 3em; font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

# ========== 2. تهيئة عداد الجلسة ==========
if 'processed_count' not in st.session_state:
    st.session_state.processed_count = 0
if 'processed_images' not in st.session_state:
    st.session_state.processed_images = []

LIMIT_LITE = 30

# ========== 3. واجهة المستخدم ==========
st.markdown('<div class="main-title">ProductImage <span>Pro</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">النسخة الأساسية - تحسين واقتصاص صور المنتجات محلياً</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric("الصور المعالجة حتى الآن", st.session_state.processed_count)
with col2:
    remaining = max(0, LIMIT_LITE - st.session_state.processed_count)
    st.metric("المتبقي في النسخة الأساسية", remaining)

if st.session_state.processed_count >= LIMIT_LITE:
    st.error("⚠️ لقد وصلت للحد الأقصى المسموح به في النسخة الأساسية (30 صورة). يرجى ترقية البرنامج للنسخة الاحترافية.")
    st.markdown("[👉 اضغط هنا لشراء النسخة غير المحدودة من جمرود](https://your-product.gumroad.com/l/your-product)")
    st.stop()

uploaded_files = st.file_uploader(
    "ارفع صور المنتجات (JPG, PNG)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# ========== 4. دوال معالجة الصور الاحترافية (OpenCV) ==========

def enhance_image_opencv(image_bytes):
    # تحويل من bytes إلى مصفوفة نّمباي ثم إلى OpenCV BGR
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # أ- تحسين الإضاءة والتباين تلقائياً باستخدام CLAHE في فضاء ألوان LAB
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    img_enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    # ب- اقتصاص تلقائي ذكي (Auto-Crop) بناءً على حواف المنتج
    gray = cv2.cvtColor(img_enhanced, cv2.COLOR_BGR2GRAY)
    # تنعيم الصورة لتقليل الضجيج
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # كشف الحواف
    edged = cv2.Canny(blurred, 30, 150)
    # البحث عن المحيطات
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # تحديد أكبر محيط (المنتج الأساسي)
        large_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(large_contour)
        # اقتصاص المنتج مع ترك هامش أمان صغير (20 بكسل)
        padding = 20
        h_img, w_img = img_enhanced.shape[:2]
        y1 = max(0, y - padding)
        y2 = min(h_img, y + h + padding)
        x1 = max(0, x - padding)
        x2 = min(w_img, x + w + padding)
        img_cropped = img_enhanced[y1:y2, x1:x2]
    else:
        img_cropped = img_enhanced

    # ج- جعل الصورة مربعة تماماً بحجم قياسي 1024x1024 مع خلفية بيضاء
    target_size = 1024
    h_crop, w_crop = img_cropped.shape[:2]
    
    # حساب نسبة التكبير/التصغير للحفاظ على أبعاد المنتج
    scale = target_size / max(h_crop, w_crop)
    new_w = int(w_crop * scale)
    new_h = int(h_crop * scale)
    img_resized = cv2.resize(img_cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # إنشاء خلفية بيضاء مربعة 1024x1024
    final_square = np.ones((target_size, target_size, 3), dtype=np.uint8) * 255
    
    # حساب إحداثيات التوسيط لبث المنتج في منتصف الخلفية البيضاء
    x_offset = (target_size - new_w) // 2
    y_offset = (target_size - new_h) // 2
    final_square[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
    
    return final_square

# ========== 5. معالجة وتفريغ المخرجات ==========
if uploaded_files:
    # التأكد من عدم تجاوز الحد المتبقي
    if st.session_state.processed_count + len(uploaded_files) > LIMIT_LITE:
        allowed = LIMIT_LITE - st.session_state.processed_count
        st.error(f"⚠️ عذراً! لا يمكنك معالجة {len(uploaded_files)} صور. المتبقي لك في النسخة المجانية هو {allowed} صور فقط.")
    else:
        if st.button("🚀 ابدأ معالجة الصور الآن"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            st.session_state.processed_images = [] # تصفية القائمة السابقة
            
            for idx, file in enumerate(uploaded_files):
                status_text.text(f"جاري تحسين صورة: {file.name}...")
                
                # قراءة الملف ومعالجته
                file_bytes = file.read()
                result_cv = enhance_image_opencv(file_bytes)
                
                # تحويل النتيجة من BGR (OpenCV) إلى RGB (PIL) ليتمكن Streamlit من عرضها وحفظها
                result_rgb = cv2.cvtColor(result_cv, cv2.COLOR_BGR2RGB)
                result_pil = Image.fromarray(result_rgb)
                
                # حفظ في ذاكرة الجلسة
                st.session_state.processed_images.append((file.name, result_pil))
                st.session_state.processed_count += 1
                
                # تحديث شريط التقدم
                progress_bar.progress((idx + 1) / len(uploaded_files))
                
            status_text.text("✅ اكتملت معالجة جميع الصور بنجاح!")

# ========== 6. عرض الصور المعالجة وزر التحميل ==========
if st.session_state.processed_images:
    st.markdown("### 🖼️ معاينة النتائج")
    
    # عرض الصور على شكل شبكة أو تتابع
    for name, img in st.session_state.processed_images:
        st.image(img, caption=f"النسخة المحسنة المربعة: {name}", use_container_width=True)
        
    # إنشاء ملف Zip مضغوط لتحميل كل الصور دفعة واحدة دون استهلاك بيانات
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for name, img in st.session_state.processed_images:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=90)
            # تغيير الاسم ليدل على أنه تم تعديله
            new_name = f"processed_{name.rsplit('.', 1)[0]}.jpg"
            zip_file.writestr(new_name, img_bytes.getvalue())
            
    zip_buffer.seek(0)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="📥 تحميل جميع الصور المحسنة (ملف ZIP مضغوط)",
        data=zip_buffer,
        file_name=f"product_images_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
        mime="application/zip"
    )