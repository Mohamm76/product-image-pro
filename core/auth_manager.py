def validate_activation_key(key):
    """
    التحقق من كود التفعيل وصلاحيته.
    """
    # كود المطور الافتراضي وكود تجريبي إضافي
    valid_keys = {
        "VIP-MOHAMMED": {"max_limit": 100, "used": 0},
        "AUTOMIX-PRO": {"max_limit": 100, "used": 0}
    }
    
    if key in valid_keys:
        return True, valid_keys[key]
    return False, None