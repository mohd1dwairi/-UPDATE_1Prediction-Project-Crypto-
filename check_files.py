import os

# فحص وجود الملفات الأساسية
paths_to_check = [
    "app/db/__init__.py",
    "app/db/session.py",
    "app/db/models.py"
]

print("🔍 Checking project structure...")
for path in paths_to_check:
    if os.path.exists(path):
        print(f"✅ Found: {path}")
    else:
        print(f"❌ MISSING: {path} <-- (هذا هو سبب المشكلة)")

# عرض الملفات الموجودة فعلياً في مجلد db
if os.path.exists("app/db"):
    print("\n📁 Files currently in app/db:")
    print(os.listdir("app/db"))