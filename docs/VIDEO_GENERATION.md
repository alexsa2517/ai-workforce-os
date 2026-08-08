# AI Workforce OS - Video Generation System

## Overview

ระบบสร้างวิดีโอด้วย AI แบบ End-to-End รองรับ workflow 5 phases ตามมาตรฐาน Professional AI Video Production

## 5 Phases Workflow

### Phase 1: Initial (Requirements)
เก็บข้อมูลความต้องการพื้นฐาน:
- ชื่อ/คำอธิบายโปรเจกต์
- เป้าหมายและกลุ่มเป้าหมาย
- ความยาวที่ต้องการ (วินาที)
- สัดส่วนภาพ (16:9 หรือ 9:16)
- สไตล์ภาพรวม
- ภาษา

**API:** `POST /api/v1/video/projects`

### Phase 2: Global Definitions
กำหนดค่าทั่วทั้งโปรเจกต์:
- **Style Spec**: sub-genre, rendering, color/lighting, detail density
- **Voice Profiles**: ลักษณะเสียงพากย์/พูด
- **BGM Source**: embedded (ในวิดีโอ) / separate (แยกไฟล์) / none
- **BGM Properties**: genre, BPM, key, instrumentation

**API:** `POST /api/v1/video/projects/{id}/global-def`

### Phase 3: Clip & BGM Planning
ใช้ LLM วางแผน clip-by-clip:
- แบ่งวิดีโอเป็นช่วง 3-10 วินาทีต่อ clip
- กำหนด narrative purpose (establish/develop/climax/resolve/transition)
- เขียน transition_description แบบละเอียด (2-4 ประโยค)
- วางแผน camera movement
- คำนวณ narration budget (ตามความเร็วภาษา)
- สร้าง BGM Emotional Arc Blueprint

**API:** `POST /api/v1/video/projects/{id}/plan-clips`

### Phase 4: Reference Images
สร้าง reference images สำหรับ:
- ตัวละคร (full body, face closeup)
- วัตถุสำคัญ
- สถานที่

**API:** `POST /api/v1/video/projects/{id}/reference-images`

### Phase 5: Execution
สร้างวิดีโอจริง:
1. Generate first keyframe สำหรับแต่ละ clip
2. Generate video จาก keyframe + prompt
3. รองรับ first_keyframe_reuse สำหรับ continuous clips
4. Generate TTS narration (per span)
5. Generate BGM (ถ้า separate)
6. Assembly: ต่อ clip + ผสมเสียง + transitions

**API:** `POST /api/v1/video/projects/{id}/generate`

## Database Schema

```
video_projects
├── project_id (PK)
├── title, description, goal, target_audience
├── duration_target, aspect_ratio, visual_style, language
├── style_spec (JSON)
├── voice_profiles (JSON)
├── bgm_source, bgm_properties (JSON)
├── status, current_phase, progress_percent
├── output_url, output_path
└── clips[], assets[]

video_clips
├── clip_id (PK)
├── project_id (FK)
├── sequence_number
├── narrative_purpose, pacing, scene, content_action
├── transition_description (TEXT - detailed)
├── target_duration, camera_movement
├── first_keyframe_framing, first_keyframe_visible_content
├── inter_clip_boundary, first_keyframe_reuse
├── on_screen_dialogue, sound_effects, bgm_cue
├── narration_cue, narration_budget
├── status, video_url, video_path, actual_duration

video_assets
├── asset_id (PK)
├── project_id (FK), clip_id (FK)
├── asset_type (reference_image/keyframe/video/audio_tts/audio_bgm/audio_sfx/final_video)
├── asset_role, url, local_path, prompt_used, generation_params
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/video/projects` | Create project (Phase 1) |
| GET | `/api/v1/video/projects` | List projects |
| GET | `/api/v1/video/projects/{id}` | Get project details |
| PUT | `/api/v1/video/projects/{id}` | Update project |
| DELETE | `/api/v1/video/projects/{id}` | Delete project |
| POST | `/api/v1/video/projects/{id}/global-def` | Set global definitions (Phase 2) |
| POST | `/api/v1/video/projects/{id}/plan-clips` | Plan clips (Phase 3) |
| POST | `/api/v1/video/projects/{id}/bgm-blueprint` | Generate BGM blueprint |
| POST | `/api/v1/video/projects/{id}/reference-images` | Generate reference images (Phase 4) |
| POST | `/api/v1/video/projects/{id}/generate` | Execute generation (Phase 5) |
| POST | `/api/v1/video/projects/{id}/assemble` | Assemble final video |
| POST | `/api/v1/video/projects/{id}/run-pipeline` | Run full pipeline (Phases 2-5) |
| GET | `/api/v1/video/projects/{id}/clips` | List clips |
| GET | `/api/v1/video/projects/{id}/assets` | List assets |

## Key Rules

### Transition Description
ต้องมีรายละเอียด 2-4 ประโยค ประกอบด้วย:
- **Subject appearance**: ลักษณะที่มองเห็น
- **Movement trajectory**: ทิศทางการเคลื่อนไหว
- **State changes**: การเปลี่ยนแปลง
- **Existence statements**: สิ่งที่มีอยู่ตลอด

### Narration Budget
- CJK (ไทย, จีน, ญี่ปุ่น, เกาหลี): ~4 ตัวอักษร/วินาที
- ภาษาอักษรละติน: ~2.5 คำ/วินาที

### First Keyframe Reuse
- `inter_clip_boundary = continuous` → `first_keyframe_reuse = yes`
- ต้องรอ clip ก่อนหน้าเสร็จก่อน ถึงจะสร้าง clip ถัดไปได้
- ใช้ ffmpeg ดึงเฟรมสุดท้ายจากวิดีโอ clip ก่อนหน้า

### Audio Mixing
- รวมเสียงทุก track: video audio + narration + BGM + SFX
- ไม่ทับซ้อนกัน (overlay, never replace)
- Narration ต้องได้ยินชัดเจน
- ระดับเสียง narration สม่ำเสมอทุก clip

## Integration with External Services

ระบบนี้เป็น **orchestrator** ที่จัดการ workflow แต่ต้องเชื่อมต่อกับ external services สำหรับการสร้างสื่อจริง:

| สื่อ | บริการที่แนะนำ | สถานะในระบบ |
|------|---------------|------------|
| Image Generation | DALL-E 3, Midjourney, Stable Diffusion | Placeholder (รอ integration) |
| Video Generation | Runway Gen-3, Pika Labs, Kling | Placeholder (รอ integration) |
| TTS/Narration | OpenAI TTS, ElevenLabs, Google Cloud TTS | Placeholder (รอ integration) |
| BGM Generation | Suno, Udio, AIVA | Placeholder (รอ integration) |
| Video Assembly | ffmpeg (มีในระบบแล้ว) | ✅ พร้อมใช้ |

## ตัวอย่างการใช้งาน

```bash
# 1. สร้างโปรเจกต์
curl -X POST http://localhost:8000/api/v1/video/projects \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cyberpunk City",
    "duration_target": 60,
    "aspect_ratio": "16:9",
    "language": "th"
  }'

# 2. กำหนดสไตล์
curl -X POST http://localhost:8000/api/v1/video/projects/vid_xxx/global-def \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "style_spec": {
      "sub_genre": "Cyberpunk anime",
      "rendering_line": "2D digital painting",
      "color_lighting": "Neon, dark backgrounds",
      "detail_density": "Highly detailed"
    },
    "bgm_source": "separate",
    "bgm_properties": {
      "genre_style": "Electronic",
      "bpm": 120,
      "core_instrumentation": ["synth", "bass"]
    }
  }'

# 3. วางแผน clips (ใช้ LLM)
curl -X POST http://localhost:8000/api/v1/video/projects/vid_xxx/plan-clips \
  -H "X-API-Key: your-key"

# 4. รัน pipeline ทั้งหมด
curl -X POST http://localhost:8000/api/v1/video/projects/vid_xxx/run-pipeline \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"style_spec": {...}, "bgm_source": "separate", ...}'
```

## การติดตั้ง ffmpeg

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y ffmpeg

# macOS
brew install ffmpeg

# Docker (มีใน Dockerfile แล้ว)
# ใช้ base image ที่มี ffmpeg หรือติดตั้งใน Dockerfile
```
