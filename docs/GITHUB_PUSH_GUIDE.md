# วิธี Push โค้ดที่ปรับปรุงแล้วขึ้น GitHub

## วิธีที่ 1: ใช้ Script อัตโนมัติ (แนะนำ)

### Linux/macOS
```bash
# 1. ไปที่โฟลเดอร์โปรเจกต์ที่ปรับปรุงแล้ว
cd ai-workforce-os-improved

# 2. สร้าง GitHub Personal Access Token
#    ไปที่: https://github.com/settings/tokens
#    คลิก "Generate new token (classic)"
#    ติ๊ก "repo" (full control)
#    คัดลอก token ที่ได้ (ขึ้นต้นด้วย ghp_)

# 3. ตั้งค่า environment variables
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
export GITHUB_USER=alexsa2517

# 4. รัน script
chmod +x scripts/push-to-github.sh
./scripts/push-to-github.sh
```

### Windows
```cmd
# 1. ไปที่โฟลเดอร์โปรเจกต์
cd ai-workforce-os-improved

# 2. สร้าง GitHub Token (ดูขั้นตอนด้านบน)

# 3. ตั้งค่า
set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
set GITHUB_USER=alexsa2517

# 4. รัน
scripts\push-to-github.bat
```

## วิธีที่ 2: ทำด้วยมือ

```bash
# 1. Clone repo ต้นฉบับ
git clone https://github.com/alexsa2517/ai-workforce-os.git
cd ai-workforce-os

# 2. สร้าง branch ใหม่
git checkout -b improved-2026

# 3. ลบไฟล์เก่าทั้งหมด (ยกเว้น .git)
rm -rf *

# 4. คัดลอกไฟล์ใหม่จากโฟลเดอร์ที่ปรับปรุงแล้ว
cp -r /path/to/ai-workforce-os-improved/* .

# 5. Commit
git add -A
git commit -m "🔧 Major improvements"

# 6. Push
git push origin improved-2026
```

## วิธีที่ 3: ใช้ GitHub Web UI (Upload ZIP)

1. ดาวน์โหลดไฟล์: `ai-workforce-os-improved.zip`
2. แตกไฟล์
3. ไปที่ GitHub repository → Code → เปลี่ยน branch เป็น `improved`
4. คลิก "Add file" → "Upload files"
5. ลากไฟล์ทั้งหมดใส่
6. Commit

## หลังจาก Push เสร็จ

1. ไปที่: `https://github.com/alexsa2517/ai-workforce-os/pulls`
2. คลิก "New Pull Request"
3. เลือก base: `main` ← compare: `improved-2026`
4. ตรวจสอบ changes แล้วคลิก "Create Pull Request"
5. Merge เข้า main
