[app]
title = E.D.I.T.H
package.name = edith_ai
package.domain = com.tonystark.corp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
requirements = python3,flet,google-generativeai,requests,certifi,chardet,idna,urllib3

# (Android specific)
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 25b
android.accept_sdk_license = True

# (Icon & Splash)
# icon.filename = icon.png
# presplash.filename = splash.png

[buildozer]
log_level = 2
warn_on_root = 1
