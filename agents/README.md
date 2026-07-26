# AI Agents

โฟลเดอร์นี้เก็บ AI agents ทั้งหมดในระบบ

## Agent ที่ใช้งาน

### DirectorAI
- **Location:** `backend/app/agents/director_ai/`
- **Role:** Director AI สำหรับจัดการ scene creation และ character direction
- **Components:**
  - `director.py` - Main DirectorAI class
  - `memory_loader.py` - Knowledge base loader
  - `prompt_engine.py` - Prompt generation engine
  - `character_memory.py` - Character state management

## เพิ่ม Agent ใหม่

1. สร้างโฟลเดอร์ใหม่ใน `backend/app/agents/`
2. สร้าง `__init__.py`
3. Implement agent class ตาม pattern ของ DirectorAI
4. เพิ่ม router endpoint ใน `routers/agents.py`
