# AI Production Studio — MVP Workflow

เป้าหมาย: ให้ผู้ใช้สร้างวิดีโอ AI ได้โดยไม่ต้องรู้ Prompt Engineering และไม่ต้องกดสร้างวิดีโอจนกว่าจะอนุมัติ Storyboard

## User flow

`ไอเดีย → บท → Storyboard → ตรวจ/อนุมัติ → สร้างวิดีโอ`

### 1. โปรเจกต์
ผู้ใช้ใส่เพียงไอเดีย เช่น

> ชายจีนโบราณที่ตายไป 1,000 ปี กลับมาพบหญิงสาวลึกลับในป่าหมอก

เลือกความยาวและอัตราส่วนภาพ แล้วให้ AI Director สร้างเรื่อง

### 2. บท
ระบบแสดง:
- ชื่อ Episode และเรื่องย่อ
- Scene / สถานที่ / เวลา / อารมณ์
- บทสนทนา
- Character Bible

ผู้ใช้แก้เนื้อหาได้ก่อนเข้าสู่ Storyboard

### 3. Storyboard
ระบบแตกเรื่องเป็น Shot พร้อม:
- ภาพตัวอย่าง
- คำอธิบาย Shot
- มุมกล้อง / การเคลื่อนกล้อง
- ระยะเวลา
- บทพูดที่สัมพันธ์กับ Shot

นี่เป็นจุดตรวจสำคัญเพื่อป้องกันการเสียค่า Video Generation จากบทหรือภาพที่ยังไม่ถูกต้อง

### 4. Final Check
ก่อนสร้าง Video ระบบต้องตรวจ:
- Story
- Dialogue
- Character Bible
- Storyboard
- Images
- Continuity

ผู้ใช้ต้องกด **อนุมัติ** ก่อน Video Director จึงเริ่มงาน

### 5. AI Workforce
เบื้องหลัง workflow รองรับ AI Employee ต่อไปนี้:

`Director → Writer → Storyboard → Character → Image → Video → Voice → Editor`

MVP UI ทำให้ผู้ใช้เห็นผลลัพธ์และอนุมัติเป็นขั้น ๆ ส่วนการเชื่อม AI จริงจะต่อผ่าน backend services ภายหลัง

## หลักการ UX

1. ผู้ใช้ไม่ต้องเห็น Prompt ที่ซับซ้อน
2. AI เสนอผลลัพธ์ ผู้ใช้เป็นผู้ตัดสินใจ
3. ทุกขั้นย้อนกลับมาแก้ได้
4. ห้ามสร้าง Video ก่อน Storyboard ผ่านการอนุมัติ
5. Character Bible ต้องถูกใช้เป็น source of truth เพื่อรักษาความต่อเนื่องของตัวละคร
