import streamlit as st
import cv2
import io
import zipfile
from PIL import Image
from core.image_engine import process_single_image
from core.auth_manager import validate_activation_key

# 1. إعدادات الصفحة وهوية البراند المتجاوبة مع الجوال
st.set_page_config(page_title="Automix Pro | معالج الصور السعودي", page_icon="📸", layout="wide")

# تصميم الهيدر الاحترافي بما يتناسب مع معايير المتاجر السعودية
st.markdown("""
    <div style='text-align: center; padding: 15px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>
        <h2 style='color: #1E293B; margin-bottom: 5px; font-family: sans-serif;'>📸 Automix ProductImage Pro</h2>
        <p style='color: #64748B; font-size: 15px; margin-top: 0;'>النظام الذكي المتكامل لتهيئة وتحسين صور المنتجات وفقاً لمعايير (سلة، زد، ونون)</p>
    </div>
""", unsafe_allow_html=True)

# إدارة حالة الجلسة (Session State)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "processed_images" not in st.session_state:
    st.session_state.processed_images = []

# --- 🔒 الواجهة الأولى: التحقق والتفعيل ---
if not st.session_state.authenticated:
    st.markdown("<div style='max-width: 500px; margin: 0 auto;'>", unsafe_allow_html=True)
    st.markdown("### 🔑 تفعيل النظام")
    # ❌ الكود القديم المسبب للمشكلة:
    # input_key = st.text_input("أدخل كود التفعيل المستلم من متجر Payhip / Gumroad:", type="password")
    # ✅ الكود الجديد المعدل والمستجيب فوراً على الجوال:
    input_key = st.text_input("أدخل كود التفعيل المستلم من متجر Payhip / Gumroad:")
    
    if st.button("تحقق وتفعيل الحساب 🚀", use_container_width=True):
        is_valid, key_info = validate_activation_key(input_key.strip())
        if is_valid:
            st.session_state.authenticated = True
            st.session_state.key_code = input_key.strip()
            st.session_state.max_limit = key_info["max_limit"]
            st.session_state.used_count = key_info["used"]
            st.success("🎯 تم التفعيل بنجاح! أهلاً بك في باقة الـ 100 صورة.")
            st.rerun()
        else:
            st.error("❌ كود التفعيل غير صحيح، يرجى التأكد من الكود المرفق في فاتورتك.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 🚀 الواجهة الثانية: لوحة تحكم المحرك الذكي بعد التفعيل ---
else:
    # القائمة الجانبية المليئة بخيارات التحكم والمعايير المحلية
    with st.sidebar:
        st.markdown("### 👤 حالة الاشتراك")
        st.info(f"**كود التفعيل:** `{st.session_state.key_code}`")
        st.metric(label="الصور المتبقية في باقتك", value=st.session_state.max_limit - st.session_state.used_count)
        
        st.markdown("---")
        st.markdown("### 📐 معايير المنصات السعودية")
        
        # ميزة التحجيم الذكي حسب نوع المنصة
        platform_preset = st.selectbox(
            "اختر أبعاد المنصة المستهدفة:",
            [
                "مربع (1024x1024) - القياسي لسلة وزد",
                "عمودي للملابس والقصص (1350x1080)",
                "أفقي للبنرات (1200x628)"
            ]
        )
        
        st.markdown("---")
        st.markdown("### 🛠️ خيارات المعالجة")
        auto_crop = st.checkbox("تفعيل الاقتصاص التلقائي الذكي", value=True, help="عزل الأطراف الفارغة وتركيز الكاميرا على المنتج فقط")
        extra_brightness = st.slider("مستوى الإضاءة الإضافية", min_value=-50, max_value=50, value=0, step=5)
        
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.processed_images = []
            st.rerun()

    # ساحة العمل لرفع الصور
    st.markdown("### 📥 ارفع صور منتجاتك")
    uploaded_files = st.file_uploader(
        "يمكنك رفع صورة واحدة أو عدة صور معاً (PNG, JPG, JPEG):", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("🚀 ابدأ المعالجة وتحسين الإضاءة فوراً", use_container_width=True):
            progress_bar = st.progress(0)
            st.session_state.processed_images = []
            
            # استخراج النص الصافي للأبعاد المحددة
            selected_ratio = platform_preset.split(" - ")[0].strip()
            
            for idx, file_item in enumerate(uploaded_files):
                file_bytes = file_item.read()
                
                # 1. الاحتفاظ بالصورة الأصلية للمقارنة قبل المعالجة
                orig_pil = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                
                # 2. تشغيل المحرك المطور للحصول على خلفية بيضاء نقية والتحجيم الصحيح
                result_cv = process_single_image(file_bytes, extra_brightness, auto_crop, selected_ratio)
                
                if result_cv is not None:
                    result_rgb = cv2.cvtColor(result_cv, cv2.COLOR_BGR2RGB)
                    result_pil = Image.fromarray(result_rgb)
                    
                    # حفظ (الاسم، الصورة الأصلية، الصورة المعالجة المحدثة)
                    st.session_state.processed_images.append((file_item.name, orig_pil, result_pil))
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
                
            st.success("✅ اكتملت معالجة الصور وضبطها على أعلى معايير النقاء والتحجيم البصري!")

    # --- 🖼️ قسم استعراض الصور (مقارنة قبل وبعد) وخيارات التحميل ---
    if st.session_state.processed_images:
        st.markdown("---")
        st.markdown("### 🔄 استعراض الفحص (قبل المعالجة 🆚 خلفية بيضاء نقية بعد التحسين)")
        
        for name, orig_img, proc_img in st.session_state.processed_images:
            with st.container():
                st.markdown(f"**📦 اسم المنتج:** `{name}`")
                
                # عرض مقارنة ثنائية جنباً إلى جنب تناسب شاشات الكمبيوتر والجوال
                col1, col2 = st.columns(2)
                with col1:
                    st.image(orig_img, caption="❌ الصورة الأصلية قبل التحسين", use_container_width=True)
                with col2:
                    st.image(proc_img, caption="✨ بعد معالجة Automix (خلفية نقية 100%)", use_container_width=True)
                
                # خيار التحميل الفردي (العادي) لكل صورة بشكل منفصل
                img_buffer = io.BytesIO()
                proc_img.save(img_buffer, format="JPEG", quality=95)
                
                st.download_button(
                    label=f"📥 تحميل هذه الصورة الفردية بشكل عادي",
                    data=img_buffer.getvalue(),
                    file_name=f"automix_{name.rsplit('.', 1)[0]}.jpg",
                    mime="image/jpeg",
                    key=f"dl_{name}"
                )
                st.markdown("<hr style='margin: 15px 0; border: 0.5px dashed #cbd5e1;'/>", unsafe_allow_html=True)
        
        # خيار التحميل الجماعي المضغوط (ZIP) لجميع الصور دفعة واحدة لراحة التاجر
        st.markdown("### 📦 خيارات التحميل الدفعي الجماعي")
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for name, _, proc_img in st.session_state.processed_images:
                single_buffer = io.BytesIO()
                proc_img.save(single_buffer, format='JPEG', quality=95)
                clean_name = name.rsplit('.', 1)[0]
                zip_file.writestr(f"automix_{clean_name}.jpg", single_buffer.getvalue())
                
        zip_buffer.seek(0)
        
        st.download_button(
            label="📥 تحميل جميع الصور المعالجة معاً في ملف مضغوط واحد (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="automix_saudi_stores_package.zip",
            mime="application/zip",
            use_container_width=True
        )