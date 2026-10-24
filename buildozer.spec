[app]
title = Supermarket Simulator 2D
package.name = supermarket2d
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,wav,json
version = 9.0

# ✅ الاعتماديات الأساسية: pygame-ce هي المحرك، مع دعم العربية
requirements = python3,pygame-ce,arabic-reshaper,python-bidi,six

# ملاحظة: python-bidi قد يسبب مشاكل في البناء أحياناً.
# البديل هو pybidi ولكن يتطلب تعديلاً في الكود (from pybidi.algorithm import get_display)
# ابدأ بـ python-bidi، وإذا فشل البناء، جرّب pybidi.

orientation = landscape
fullscreen = 1

# إعدادات أندرويد
android.permissions = 
android.api = 31
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
