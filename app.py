import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import zipfile
from datetime import datetime

# ========== 1. الهوية البصرية المتطورة للجوال والكمبيوتر ==========
st.set_page_config(
    page_title="ProductImage Pro | تيسير التجارة الرقمية",
    page_icon="✨",
    layout="centered"
)

# تصميم عصري بلمسة زمردية وذهبية (رؤية 2030) متناسق تماماً مع شاشات الجوال
st.markdown("""
    <style>
    .main-title { color: #022c22; text-align: center; font-size: 2.2rem; font-weight: 800; margin-bottom: 2px; font-family: 'Cairo', sans-serif; }
    .main-title span { color: #059669; }
    .sub-title { color: #4b5563; text-align: center; font-size: 1rem; margin-bottom: 25px; }
    .feature-box { background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 12px; margin-bottom: 20px; text-align: center; color: #166534; }
    .stButton>button { background: linear-gradient(135deg, #059669 0%, #047857 100%) !important; color: white !important; font-weight: bold !important; width: 100%; border-radius: 10px !important; height: 3.2em; font-size: 1.05rem; border: none !important; box-shadow: 0 4px 6px -1px rgba(5, 150, 105, 0.2); }
    </style>
""", unsafe_allow_html=True)

# ========== 2. إدارة الأكواد والعدادات (تأمين النسخة) ==========
# قائمة الأكواد المفعلة التي ستعطيها للـ 100 عميل (يمكنك تغييرها أو زيادة أعدادها)
VALID_KEYS = {
    "SA-PRO-9981": 100,
    "SA-PRO-4412": 100,
    "SA-PRO-7753": 100,
    "VIP-MOHAMMED": 100  # كود خاص بك للتجربة والتأكد
}

if 'user_key' not in st.session_state:
    st.session_state.user_key = ""
if 'user_limit' not in st.session_state:
    st.session_state.user_limit = 0
if 'processed_count' not in st.session_state:
    st.session_state.processed_count = 0
if 'processed_images' not in st.session_state:
    st.session_state.processed_images = []

# ========== 3. واجهة المستخدم الرسومية ==========
st.markdown('<div class="main-title">ProductImage <span>Pro V1</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">حسّن صور منتجاتك واجعلها جاهزة لـ "سلة وزد" بضغطة زر</div>', unsafe_allow_html=True)

# نظام التحقق من كود التفعيل لحماية أرباحك
if not st.session_state.user_key:
    st.markdown('<div class="feature-box">🛡️ هذا التطبيق مخصص للمشتركين. يرجى إدخال كود التفعيل المستلم من جمرود لبدء الاستخدام.</div>', unsafe_allow_html=True)
    activation_input = st.text_input("🔑 أدخل كود التفعيل الخاص بك:", placeholder="مثال: SA-PRO-XXXX").strip()
    
    if st.button("تفعيل الحساب"):
        if activation_input in VALID_KEYS:
            st.session_state.user_key = activation_input
            st.session_state.user_limit = VALID_KEYS[activation_input]
            st.success("✅ تم التفعيل بنجاح! باقتك الحالية: 100 صورة.")
            st.rerun()
        else:
            st.error("❌ كود التفعيل غير صحيح أو منتهي الصلاحية. تأكد من الكود أو قم بالشراء من جمرود.")
    
    st.markdown("---")
    st.markdown("### 🛒 الميزات المضمنة في باقة الـ 50 ريال:")
    st.write("• تحسين الإضاءة الذكي والأوتوماتيكي للمنتجات.")
    st.write("• ضبط قياسات الصورة لتصبح مربعة 1024×1024 (المعيار الذهبي للمتاجر).")
    st.write("• تحميل سريع ومباشر على الجوال بملف مضغوط واحد.")
    st.stop() # إيقاف بقية التطبيق حتى يتم إدخال الكود

# في حال تم التفعيل، تظهر الواجهة الكاملة:
st.sidebar.markdown(f"### 👤 الحساب المتصل: \n`{st.session_state.user_key}`")
remaining_images = max(0, st.session_state.user_limit - st.session_state.processed_count)
st.sidebar.metric("المتبقي في باقتك", f"{remaining_images} صورة")

if remaining_images <= 0:
    st.error("⚠️ انتهت صلاحية الباقة الحالية (تم استهلاك 100 صورة).")
    st.markdown("[👉 اضغط هنا لشراء كود تفعيل جديد بقيمة 50 ريال](https://your-gumroad-link.com)")
    st.stop()

# أدوات تحسين إضافية اختيارية وسهلة في الجوال
with st.expander("⚙️ خيارات تحسين إضافية (اختياري)"):
    extra_brightness = st.slider("زيادة السطوع اليدوي", -50, 50, 0)
    auto_crop = st.checkbox("تفعيل الاقتصاص التلقائي الذكي للحواف", value=True)

uploaded_files = st.file_uploader(
    "📸 اختر أو التقط صور المنتجات من جوالك:",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# ========== 4. خوارزمية المعالجة المتطورة بـ OpenCV ==========
def enhance_image_v1(image_bytes, b_offset, crop_flag):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # تحسين احترافي للإضاءة والتباين (ملاءمة لمعايير الإعلانات)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    img_enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    if b_offset != 0:
        img_enhanced = cv2.convertScaleAbs(img_enhanced, alpha=1.0, beta=b_offset)
    
    # الاقتصاص الذكي
    if crop_flag:
        gray = cv2.cvtColor(img_enhanced, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 40, 180)
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            large_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(large_contour)
            p = 25
            h_i, w_i = img_enhanced.shape[:2]
            img_enhanced = img_enhanced[max(0, y-p):min(h_i, y+h+p), max(0, x-p):min(w_i, x+w+p)]

    # تحويل لمربع كامل 1024x1024
    target_size = 1024
    h_c, w_c = img_enhanced.shape[:2]
    scale = target_size / max(h_c, w_c)
    new_w, new_h = int(w_c * scale), int(h_c * scale)
    img_resized = cv2.resize(img_enhanced, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    final_square = np.ones((target_size, target_size, 3), dtype=np.uint8) * 255
    x_offset = (target_size - new_w) // 2
    y_offset = (target_size - new_h) // 2
    final_square[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized
    
    return final_square

# ========== 5. التشغيل واستخراج النتائج ==========
if uploaded_files:
    if len(uploaded_files) > remaining_images:
        st.error(f"❌ عدد الصور المرفوعة ({len(uploaded_files)}) أكبر من المتبقي في باقتك ({remaining_images}). يرجى تقليل الصور.")
    else:
        if st.button("🚀 ابدأ معالجة الصور الآن"):
            progress_bar = st.progress(0)
            st.session_state.processed_images = []
            
            for idx, file in enumerate(uploaded_files):
                result_cv = enhance_image_v1(file.read(), extra_brightness, auto_crop)
                result_rgb = cv2.cvtColor(result_cv, cv2.COLOR_BGR2RGB)
                result_pil = Image.fromarray(result_rgb)
                
                st.session_state.processed_images.append((file.name, result_pil))
                st.session_state.processed_count += 1
                progress_bar.progress((idx + 1) / len(uploaded_files))
                
            st.success("✅ اكتمل التعديل!")

if st.session_state.processed_images:
    st.markdown("### 🖼️ معاينة وتحميل نتائجك:")
    
    # تجهيز ملف الـ ZIP مباشرة في ذاكرة الجوال
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for name, img in st.session_state.processed_images:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=92)
            zip_file.writestr(f"pro_{name.rsplit('.', 1)[0]}.jpg", img_bytes.getvalue())
            
    zip_buffer.seek(0)
    
    st.download_button(
        label="📥 حفظ الصور المعدلة إلى الجوال (ملف ZIP)",
        data=zip_buffer,
        file_name=f"products_1024x1024.zip",
        mime="application/zip"
    )