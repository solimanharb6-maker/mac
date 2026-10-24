[app]
title = Supermarket Simulator 2D
package.name = supermarket2d
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,wav,json
version = 9.0

# المكتبات اللي طلبتها
requirements = python3==3.10.12,hostpython3==3.10.12,pygame-ce,arabic-reshaper,pybidi,six

orientation = landscape
fullscreen = 1

# إعدادات أندرويد المهمة
android.accept_sdk_license = True
android.permissions = 
android.api = 31
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
