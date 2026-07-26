# Contributing to AI Workforce OS

ขอบคุณที่สนใจร่วมพัฒนา AI Workforce OS!

## วิธีการร่วมพัฒนา

### 1. Fork Repository
Fork โปรเจกต์นี้ไปที่บัญชี GitHub ของคุณ

### 2. Clone และสร้าง Branch
```bash
git clone https://github.com/alexsa2517/ai-workforce-os.git
cd ai-workforce-os
git checkout -b feature/your-feature-name
```

### 3. ตั้งค่า Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # แก้ไขค่าใน .env ให้ตรงกับของคุณ
```

### 4. เขียน Code และ Test
- เขียน unit tests สำหรับฟีเจอร์ใหม่
- ตรวจสอบว่า tests ทั้งหมดผ่าน: `python -m pytest tests/`

### 5. Commit และ Push
```bash
git add .
git commit -m "feat: เพิ่มฟีเจอร์ใหม่"
git push origin feature/your-feature-name
```

### 6. สร้าง Pull Request
สร้าง Pull Request พร้อมอธิบายสิ่งที่เปลี่ยนแปลง

## Coding Standards

- ใช้ Python 3.11+
- ใช้ type hints ในทุก function
- เขียน docstring สำหรับทุก class และ method
- ใช้ black formatter สำหรับ format code
- ใช้ isort สำหรับจัดเรียง imports

## Pull Request Guidelines

- 1 PR ต่อ 1 ฟีเจอร์
- อธิบายสิ่งที่เปลี่ยนแปลงอย่างชัดเจน
- เพิ่ม tests สำหรับโค้ดใหม่
- ตรวจสอบว่า CI/CD ผ่านทั้งหมด

## Reporting Bugs

รายงานบั๊กผ่าน [Issues](https://github.com/alexsa2517/ai-workforce-os/issues) พร้อมรายละเอียด:
- ขั้นตอนการ reproduce
- ผลลัพธ์ที่คาดหวัง
- ผลลัพธ์ที่เกิดขึ้นจริง
- Version ที่ใช้
