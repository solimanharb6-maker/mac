[app]

(str) Title of your application

title = Supermarket Mobile

(str) Package name

package.name = supermarketmobile

(str) Package domain (needed for android/ios packaging)

package.domain = org.supermarket

(str) Source code where the main.py lives

source.dir = .

(list) Source files to include (python files, assets, fonts, etc.)

source.include_exts = py,png,jpg,jpeg,ttf,otf,json,wav,ogg,mp3

(list) List of directory to include (e.g. assets)

source.include_dirs = assets

(str) Application versioning (method 1)

version = 1.0.0

(list) Application requirements

Matching requirements.txt (pygame-ce, arabic-reshaper, python-bidi)

requirements = python3, pygame-ce, arabic-reshaper, python-bidi

(str) Supported orientations (landscape, sensorLandscape, portrait)

orientation = landscape

(bool) Indicate if the application should be fullscreen or not

fullscreen = 1

(list) Permissions

android.permissions = INTERNET

(int) Target Android API, should be as high as possible.

android.api = 33

(int) Minimum API your APK will support.

android.minapi = 21

(str) Android NDK version to use

android.ndk = 25b

(bool) If True, then skip trying to update the Android sdk host apps

android.skip_update = False

(bool) If True, then accept all SDK licences

android.accept_sdk_license = True

(str) Android logcat filters to use

android.logcat_filters = *:S python:D

(str) Android additional libraries to copy into libs/armeabi-v7a or libs/arm64-v8a

android.add_libs_armeabi_v7a =

(list) Android architectures to build for

android.archs = arm64-v8a, armeabi-v7a

(bool) Enable AndroidX support

android.enable_androidx = True

[buildozer]

(int) Log level (0 = error only, 1 = info, 2 = debug (with command output))

log_level = 2

(int) Display warning if buildozer is run as root (0 = false, 1 = true)

warn_on_root = 1
