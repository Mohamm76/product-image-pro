import streamlit as st
import cv2
import io
import zipfile
from PIL import Image
from core.image_engine import process_single_image
from core.auth_manager import validate_activation_key

# إعدادات الصفحة والواجهة وتجاوب الجوال
st.set_page_config(page_title="Automix | ProductImage Pro", page_icon="📸", layout="wide")

# تصميم الهيدر بشكل تسويقي جذاب
st.markdown("""
    <div style='text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 10px; margin-bottom: 25px;'>
        <h2 style='color: #1E1E1E; margin-bottom: 0;'>📸 Automix ProductImage Pro</h2>
        <p style='color: #666; font-size: 16px;'>معالج ومحسّن صور المنتجات الذكي والمربع لمتاجر (سلة وزد)</p>
    </div>
""", unsafe_allow_html=True)

# إدارة حالة الجلسة (Session State)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "processed_images" not in st.session_state:
    st.session_state.processed_images = []

# --- 1. واجهة تسجيل الدخول والتفعيل ---
if not st.session_state.authenticated:
    st.markdown("### 🔑 تفعيل النظام")
    input_key = st.text_input("أدخل كstyle التفعيل الخاص بك والمستلم من جمرود:", type="password")
    
    if st.button("تفعيل الحساب والإنطلاق 🚀", use_container_width=True):
        is_valid, key_info = validate_activation_key(input_key.strip())
        if is_valid:
            st.session_state.authenticated = True
            st.session_state.key_code = input_key.strip()
            st.session_state.max_limit = key_info["max_limit"]
            st.session_state.used_count = key_info["used"]
            st.success("🎯 تم التفعيل بنجاح! أهلاً بك في باقة الـ 100 صورة.")
            st.rerun()
        else:
            st.error("❌ كود التفعيل غير صحيح أو انتهت صلاحيته، تأكد من البيانات.")

# --- 2. واجهة النظام الأساسية بعد التفعيل ---
else:
    # شريط جانبي معلوماتي أنيق
    with st.sidebar:
        st.markdown(f"### 👤 باقة الحساب")
        st.info(f"**الكود النشط:** `{st.session_state.key_code}`")
        st.metric(label="الصور المتبقية في باقتك", value=st.session_state.max_limit - st.session_state.used_count)
        st.markdown("---")
        st.markdown("### 🛠️ خيارات التحكم الذكي")
        auto_crop = st.checkbox("تفعيل الاقتصاص التلقائي الذكي", value=True, help="يقوم بتركيز القص على المنتج فقط وعزل الخلفية الزائدة")
        extra_brightness = st.slider("إضاءة إضافية يدوية", min_value=-50, max_value=50, value=0, step=5)
        
        if st.button("تسجيل الخروج 🚪"):
            st.session_state.authenticated = False
            st.rerun()

    # ساحة رفع الصور الرئيسية
    st.markdown("### 📥 ارفع صور منتجاتك هنا")
    uploaded_files = st.file_uploader(
        "يمكنك رفع صورة واحدة أو عدة صور معاً من استوديو الجوال مباشرة:", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("🚀 ابدأ معالجة وتحسين الصور الآن", use_container_width=True):
            progress_bar = st.progress(0)
            st.session_state.processed_images = []
            
            for idx, file_file in enumerate(uploaded_files):
                # المعالجة عبر المحرك الأساسي المستقل
                result_cv = process_single_image(file_file.read(), extra_brightness, auto_crop)
                
                if result_cv is not None:
                    result_rgb = cv2.cvtColor(result_cv, cv2.COLOR_BGR2RGB)
                    result_pil = Image.fromarray(result_rgb)
                    st.session_state.processed_images.append((file_file.name, result_pil))
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
                
            st.success("✅ اكتملت معالجة جميع الصور وتحويلها لمربع قياسي 1024x1024!")

    # عرض النتائج وتنزيلها بشكل متجاوب
    if st.session_state.processed_images:
        st.markdown("### 🖼️ معاينة الصور الجاهزة للمتجر:")
        
        # إنشاء شبكة عرض مرنة تناسب شاشة الجوال (صورتين في كل سطر)
        cols = st.columns(2)
        for idx, (name, img) in enumerate(st.session_state.processed_images):
            with cols[idx % 2]:
                st.image(img, caption=f"جاهزة: {name}", use_container_width=True)
                
        # تجميع الملفات في ZIP بنقرة واحدة
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for name, img in st.session_state.processed_images:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG', quality=95)
                clean_name = name.rsplit('.', 1)[0]
                zip_file.writestr(f"automix_{clean_name}.jpg", img_bytes.getvalue())
                
        zip_buffer.seek(0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📥 حفظ جميع الصور المعدلة إلى الجوال (ملف ZIP واحد)",
            data=zip_buffer,
            file_name="automix_products_1024x1024.zip",
            mime="application/zip",
            use_container_width=True
        )