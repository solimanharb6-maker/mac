[app]
title = Supermarket Simulator 2D
package.name = supermarketsim2d
package.domain = com.supermarketsim
source.dir = .
source.include_exts = py,png,ttf,json
source.exclude_dirs = .github,.git,.buildozer,bin,web_src,__pycache__
version = 9.0

# pygame via p4a's sdl2 bootstrap. Arabic libs are pure-python (bidi pinned to the pure-python 0.4.2).
requirements = python3,hostpython3,pygame,arabic-reshaper==3.0.0,python-bidi==0.4.2,six,setuptools

orientation = landscape
fullscreen = 1
icon.filename = %(source.dir)s/assets/logo.png
presplash.filename = %(source.dir)s/assets/logo.png
android.presplash_color = #101420

# Android 5.0 (API 21) and up. API 33 target = fine for sideloaded APK.
# Google Play now needs target API 36 -> raise android.api when you publish there.
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
