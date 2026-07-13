from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class ActivationKey(Base):
    """
    جدول إدارة رخص التفعيل وباقات المشتركين (Automix SaaS Licenses)
    """
    __tablename__ = "activation_keys"

    key_code = Column(String, primary_key=True, index=True, unique=True)
    buyer_email = Column(String, index=True, nullable=False)
    max_limit = Column(Integer, default=100, nullable=False)
    used_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # علاقة ربط شجرية مع جدول حركات المرور (Cascading Delete)
    logs = relationship("TrafficLog", back_populates="license", cascade="all, delete-orphan")


class TrafficLog(Base):
    """
    جدول التحليلات المتقدمة ومراقبة حركة مرور وموارد النظام (Traffic & Metrics Analytics)
    """
    __tablename__ = "traffic_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    key_code = Column(String, ForeignKey("activation_keys.key_code", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String, index=True, nullable=False)  # تتبع الميزات: "IMAGE_PROCESS" أو "KEY_VALIDATE" أو "AI_DESCRIPTION"
    images_count = Column(Integer, default=0, nullable=False)
    platform_target = Column(String, nullable=True)  # توثيق المنصة مثل: "سلة", "زد", "نون"
    ip_address = Column(String, nullable=True)  # لحماية النظام من الـ Spam والطلبات المتكررة
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # ربط خلفي مع جدول الرخص
    license = relationship("ActivationKey", back_populates="logs")