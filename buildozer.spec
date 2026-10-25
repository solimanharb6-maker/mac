[app]
title = Supermarket Simulator 2D
package.name = supermarketsim2d
package.domain = com.supermarketsim
source.dir = .
source.include_exts = py,png,ttf,json
source.exclude_dirs = .github,.git,.buildozer,bin,web_src,__pycache__
version = 9.0

# pygame عبر p4a (sdl2). مكتبات العربي pure-python.
requirements = python3,hostpython3,pygame,arabic-reshaper==3.0.0,python-bidi==0.4.2,six,setuptools

orientation = landscape
fullscreen = 1
icon.filename = %(source.dir)s/assets/logo.png
presplash.filename = %(source.dir)s/assets/logo.png
android.presplash_color = #101420

# ============================================================
# نطاق أندرويد (للاستخدام الشخصي / sideload)
# minapi 21 = Android 5.0  ← أقدم إصدار عملي مع pygame
# api    34 = Android 14   ← مستقر جداً مع p4a (مش محتاج Play Store)
# ============================================================
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.logcat_filters = *:S python:D
android.enable_androidx = True

# لو عايز أعلى إصدار ممكن غيّر لـ:
# android.api = 36
# أو android.api = 37

[buildozer]
log_level = 2
warn_on_root = 1
