import React, { useMemo, useState } from 'react';

type Stage = 'project' | 'script' | 'storyboard' | 'generate';

const stages: { id: Stage; label: string; icon: string }[] = [
  { id: 'project', label: 'โปรเจกต์', icon: '💡' },
  { id: 'script', label: 'บท', icon: '📝' },
  { id: 'storyboard', label: 'Storyboard', icon: '🎞️' },
  { id: 'generate', label: 'สร้างวิดีโอ', icon: '🎥' },
];

const shots = [
  ['01', '🌲', 'ป่าโบราณเต็มไปด้วยหมอก', 'Wide · Slow Pan · 5 วินาที'],
  ['02', '🧍🏻', 'หลินเฟิงเดินออกจากหมอก', 'Medium · Tracking · 5 วินาที'],
  ['03', '👩🏻', 'หญิงสาวปรากฏตัว ยิ้มทั้งน้ำตา', 'Close Up · Push In · 5 วินาที'],
  ['04', '👨🏻', 'หลินเฟิงสับสน “เจ้าเป็นใคร?”', 'Close Up · 85mm · 5 วินาที'],
];

export default function ProductionStudio() {
  const [stage, setStage] = useState<Stage>('project');
  const [idea, setIdea] = useState('ชายจีนโบราณที่ตายไป 1,000 ปี กลับมาพบหญิงสาวลึกลับในป่าหมอก');
  const [generated, setGenerated] = useState(false);
  const [approved, setApproved] = useState(false);
  const [videoStarted, setVideoStarted] = useState(false);

  const stageIndex = useMemo(() => stages.findIndex((s) => s.id === stage), [stage]);

  const next = () => {
    const nextStage = stages[Math.min(stageIndex + 1, stages.length - 1)].id;
    setStage(nextStage);
  };

  const createStory = () => {
    setGenerated(true);
    setStage('script');
  };

  const approveStoryboard = () => {
    setApproved(true);
    setStage('generate');
  };

  return (
    <div className="studio">
      <aside className="studio-sidebar">
        <div className="studio-brand">🎬 <strong>AI Workforce OS</strong><small>AI Production Studio</small></div>
        <div className="studio-nav">
          {stages.map((item, index) => (
            <button key={item.id} className={stage === item.id ? 'studio-nav-item active' : 'studio-nav-item'} onClick={() => setStage(item.id)}>
              <span>{item.icon}</span><span>{index + 1}. {item.label}</span>{index < stageIndex ? <b>✓</b> : null}
            </button>
          ))}
        </div>
        <div className="director-card"><div>🎬</div><strong>AI Director</strong><p>AI ทำงานให้คุณ แต่คุณเป็นผู้อนุมัติทุกขั้น</p></div>
      </aside>

      <div className="studio-content">
        <header className="studio-header">
          <div><small>AI PRODUCTION STUDIO</small><h1>{stages[stageIndex].label}</h1></div>
          {stage !== 'generate' && <button className="studio-button primary" onClick={next}>ถัดไป →</button>}
        </header>

        {stage === 'project' && (
          <div className="studio-stack">
            <section className="studio-hero">
              <div><span className="studio-pill">ไม่ต้องเขียน Prompt</span><h2>เปลี่ยนไอเดียให้เป็นหนัง AI</h2><p>คุณให้แค่ไอเดีย ระบบจะแตกเป็นบท ฉาก บทสนทนา Storyboard และเตรียมสร้างวิดีโอให้ตรวจสอบก่อน</p></div>
            </section>
            <section className="studio-card">
              <label>ไอเดียของคุณ</label>
              <textarea value={idea} onChange={(e) => setIdea(e.target.value)} rows={5} />
              <div className="studio-options"><label>ความยาว<select><option>Shorts 30 วินาที</option><option selected>Episode 1–2 นาที</option><option>ภาพยนตร์ 10 นาที</option></select></label><label>รูปแบบ<select><option selected>แนวตั้ง 9:16</option><option>แนวนอน 16:9</option></select></label></div>
              <button className="studio-button primary large" onClick={createStory}>✨ ให้ AI Director สร้างเรื่อง</button>
            </section>
            <section className="studio-card"><h3>โปรเจกต์ของฉัน</h3><div className="project-item"><div className="project-thumb">🌫️</div><div><strong>หลินเฟิง คนตง 1,000 ปี</strong><p>EP01 · Storyboard พร้อมตรวจสอบ</p></div><span className="studio-status">กำลังทำ</span></div></section>
          </div>
        )}

        {stage === 'script' && (
          <div className="studio-stack">
            <section className="studio-card"><div className="card-heading"><div><span className="studio-pill">EP01</span><h2>หญิงสาวในป่าหมอก</h2></div><span className="studio-status">{generated ? 'สร้างจากไอเดียแล้ว' : 'ตัวอย่าง'}</span></div><p>หลินเฟิง ชายหนุ่มที่เสียชีวิตไปเมื่อ 1,000 ปีก่อน ตื่นขึ้นในป่าลึกลับและพบหญิงสาวที่เรียกชื่อของเขา</p></section>
            <div className="studio-two-col"><section className="studio-card"><h3>🎬 Scene 01 · ป่าโบราณ</h3><p><b>เวลา:</b> กลางคืน · <b>บรรยากาศ:</b> หมอกหนา / พระจันทร์เต็มดวง</p><p>หลินเฟิงเดินผ่านป่าหมอก เขาได้ยินเสียงผู้หญิงเรียกชื่อของเขา</p></section><section className="studio-card dialogue"><h3>🗣 บทสนทนา</h3><p><b>หญิงสาว:</b> “ในที่สุด... เจ้าก็กลับมา”</p><p><b>หลินเฟิง:</b> “เจ้า...รู้จักข้าหรือ?”</p><p><b>หญิงสาว:</b> “เจ้าจำข้าไม่ได้จริงหรือ... หลินเฟิง?”</p></section></div>
            <section className="studio-card"><h3>👤 Character Bible</h3><div className="character-row"><span className="character-avatar">👨🏻</span><div><strong>หลินเฟิง</strong><p>อายุ 25 · ผมดำยาว · ชุดจีนโบราณสีดำ · สุขุม · ดวงตาดำ</p></div></div><div className="character-row"><span className="character-avatar">👩🏻</span><div><strong>หญิงปริศนา</strong><p>หญิงสาวโบราณ · ผมดำยาว · ชุดจีนสีขาว · ยิ้มทั้งน้ำตา · ลึกลับ</p></div></div></section>
            <button className="studio-button primary" onClick={() => setStage('storyboard')}>ไป Storyboard →</button>
          </div>
        )}

        {stage === 'storyboard' && (
          <div className="studio-stack">
            <section className="studio-card"><div className="card-heading"><div><span className="studio-pill">SCENE 01</span><h2>Storyboard</h2></div><span className="studio-status">ตรวจสอบก่อนสร้าง Video</span></div><p>ภาพแต่ละ Shot คือสิ่งที่ AI จะนำไปสร้างเป็นวิดีโอจริง คุณแก้ได้ก่อนเสียค่า Generate</p></section>
            <div className="shot-grid">{shots.map(([id, art, description, meta]) => <article className="shot-card" key={id}><div className="shot-art">{art}<span>🌫️</span></div><div className="shot-body"><small>SHOT {id}</small><strong>{description}</strong><p>{meta}</p><button className="studio-button secondary">แก้ Shot</button></div></article>)}</div>
            <section className="approval-card"><span className="approval-icon">✓</span><div><strong>พร้อมอนุมัติ Storyboard</strong><p>Character · Dialogue · Continuity ผ่านการตรวจ</p></div><button className="studio-button primary" onClick={approveStoryboard}>อนุมัติและไปต่อ →</button></section>
          </div>
        )}

        {stage === 'generate' && (
          <div className="studio-stack">
            <section className="generate-panel"><span className="studio-pill">FINAL CHECK</span><h2>พร้อมสร้างวิดีโอ 🎬</h2><p>ระบบจะสร้างวิดีโอจาก Storyboard ที่คุณอนุมัติเท่านั้น</p><div className="check-grid">{['Story','Dialogue','Character Bible','Storyboard','Images','Continuity'].map((x) => <div key={x}>✓ {x}</div>)}</div><div className="generate-summary"><strong>EP01</strong><span>5 Scenes · 24 Shots · ประมาณ 1:52 นาที · 9:16</span></div><button className="studio-button primary huge" disabled={!approved || videoStarted} onClick={() => setVideoStarted(true)}>{videoStarted ? '⏳ กำลังสร้าง...' : '🎥 สร้างวิดีโอ'}</button>{videoStarted && <p className="generate-message">ส่งงานให้ Video Director แล้ว — ขั้นต่อไปคือ Voice และ Editor AI</p>}</section>
            <section className="studio-card"><h3>AI Workforce ที่ทำงานเบื้องหลัง</h3><div className="worker-list">{['🎬 Director','📝 Writer','🎞️ Storyboard','👤 Character','🖼️ Image','🎥 Video','🔊 Voice','✂️ Editor'].map((x) => <span key={x}>{x}</span>)}</div></section>
          </div>
        )}
      </div>
    </div>
  );
}
