# คู่มือ Push ขึ้น GitHub แบบ Step-by-Step

## ขั้นตอนที่ 1: สร้าง GitHub Token (ทำครั้งเดียว)

1. เปิด https://github.com/settings/tokens
2. คลิก **"Generate new token (classic)"**
3. ใส่ชื่อ token: `AI Workforce OS Push`
4. เลือก expiration: **No expiration** (หรือ 90 วัน)
5. ติ๊ก ☑️ **repo** (full control of private repositories)
6. เลื่อนลงมาล่างสุด กด **Generate token**
7. **คัดลอก token ทันที** (จะขึ้นต้นด้วย `ghp_...`) — ดูได้ครั้งเดียว!

---

## ขั้นตอนที่ 2: รัน Script (ทำตามนี้)

เปิด Terminal แล้วพิมพ์ทีละบรรทัด:

```bash
# 1. ไปที่โฟลเดอร์โปรเจกต์
cd ai-workforce-os-improved

# 2. ตั้งค่า token (วาง token ที่คัดลอกมา)
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
export GITHUB_USER=alexsa2517

# 3. รัน script
./scripts/push-to-github.sh
```

---

## ขั้นตอนที่ 3: Merge บน GitHub

1. เปิดลิงก์ที่ script แสดง (หรือไปที่ https://github.com/alexsa2517/ai-workforce-os/pulls)
2. คลิก **"New Pull Request"**
3. base: `main` ← compare: `improved-2026...`
4. ตรวจสอบไฟล์ที่เปลี่ยน
5. คลิก **"Create Pull Request"**
6. คลิก **"Merge Pull Request"** → **"Confirm Merge"**

---

## ✅ เสร็จแล้ว!

โค้ดใหม่จะอยู่บน GitHub แล้ว สามารถ clone ได้ด้วย:
```bash
git clone https://github.com/alexsa2517/ai-workforce-os.git
```
