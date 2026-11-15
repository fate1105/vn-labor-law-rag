"""
War Room Multi-Agent UI components, 2D SVG scene and dynamic dialogue helpers.
"""

import copy
import html
import json
import re
import streamlit as st
import streamlit.components.v1 as components

# ── Metadata của 5 Agent trong War Room ──────────────────────────────────────
AGENTS_META = [
    {
        "id": 1,
        "name": "Agent 1",
        "title": "Rà soát Pháp lý",
        "role": "Luật sư Căn cứ Pháp luật",
        "icon": "⚖️",
        "desk_item": "Tủ Luật & FAISS",
    },
    {
        "id": 2,
        "name": "Agent 2",
        "title": "Đề xuất Giải pháp",
        "role": "Chuyên viên Phân tích Vụ việc",
        "icon": "💡",
        "desk_item": "Hồ sơ Phương án",
    },
    {
        "id": 3,
        "name": "Agent 3",
        "title": "Phản biện Rủi ro",
        "role": "Luật sư Phản biện Rủi ro",
        "icon": "🛡️",
        "desk_item": "Trục Phản biện",
    },
    {
        "id": 4,
        "name": "Agent 4",
        "title": "Soạn thảo Văn bản",
        "role": "Thư ký Hành chính NĐ 30",
        "icon": "🖋️",
        "desk_item": "Mẫu NĐ 30/2020",
    },
    {
        "id": 5,
        "name": "Agent 5",
        "title": "Tổng hợp Đánh giá",
        "role": "Trưởng ban Ra Quyết định",
        "icon": "🎖️",
        "desk_item": "Búa Chủ tọa",
    },
]


# ── VIRTUAL 2D SVG+JS INTERACTIVE OFFICE SCENE (COMPONENTS.HTML) ──────────────
OFFICE_SCENE_TEMPLATE = r"""
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  html,body{margin:0;padding:0;background:transparent;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;}
  .wrap{border:1px solid #cbd5e1;border-radius:18px;overflow:hidden;background:#fff;box-shadow:0 10px 25px -5px rgba(15,23,42,.08);}
  svg{display:block;width:100%;height:auto;}
  .bar{display:flex;align-items:center;gap:10px;padding:10px 16px;background:#f8fafc;border-top:1px solid #e2e8f0;font-size:13px;color:#334155;}
  .dot{width:10px;height:10px;border-radius:50%;background:#16a34a;box-shadow:0 0 8px rgba(22,163,74,.6);animation:pd 1.2s infinite;}
  @keyframes pd{0%,100%{transform:scale(.9);opacity:.7}50%{transform:scale(1.3);opacity:1}}

  /* gõ phím */
  .armL,.armR{transform-box:fill-box;}
  .typing .armL{animation:tp .28s infinite alternate ease-in-out;}
  .typing .armR{animation:tp .28s .14s infinite alternate ease-in-out;}
  @keyframes tp{from{transform:translateY(0)}to{transform:translateY(-7px)}}
  /* nhún người khi làm việc */
  .typing .body{animation:bob .6s infinite alternate ease-in-out;transform-box:fill-box;transform-origin:center bottom;}
  @keyframes bob{from{transform:translateY(0)}to{transform:translateY(-3px)}}
  /* ngủ gật */
  .sleep .head{transform-box:fill-box;transform-origin:center bottom;transform:rotate(14deg) translateY(10px);animation:nod 2.4s infinite ease-in-out;}
  @keyframes nod{0%,100%{transform:rotate(14deg) translateY(10px)}50%{transform:rotate(8deg) translateY(6px)}}
  .zzz text{animation:zf 2.2s infinite;opacity:0;font-weight:800;fill:#64748b;}
  .zzz text:nth-child(2){animation-delay:.7s}.zzz text:nth-child(3){animation-delay:1.4s}
  @keyframes zf{0%{opacity:0;transform:translate(0,0)}30%{opacity:1}100%{opacity:0;transform:translate(14px,-26px)}}
  /* hơi nóng cà phê */
  .steam path{fill:none;stroke:#cbd5e1;stroke-width:2;stroke-linecap:round;animation:st 2s infinite;opacity:0;}
  .steam path:nth-child(2){animation-delay:.8s}
  @keyframes st{0%{opacity:0;transform:translateY(4px)}50%{opacity:.9}100%{opacity:0;transform:translateY(-8px)}}
  /* màn hình chạy chữ */
  .scr line{stroke:#e0f2fe;stroke-width:3;stroke-linecap:round;animation:ln 1s infinite alternate;}
  .scr line:nth-child(2){animation-delay:.2s}.scr line:nth-child(3){animation-delay:.4s}.scr line:nth-child(4){animation-delay:.6s}
  @keyframes ln{from{opacity:.25}to{opacity:1}}
  /* vòng sáng nhân vật đang nói */
  .ring{animation:rg 1.2s infinite alternate;}
  @keyframes rg{from{opacity:.25}to{opacity:.8}}
  /* giơ tay vẫy chào khi xong */
  .done .waveArm{animation:waveArm .7s infinite alternate ease-in-out;}
  @keyframes waveArm{
    from{transform:rotate(-8deg);}
    to{transform:rotate(16deg);}
  }
  .bubble{box-sizing:border-box;width:100%;height:100%;padding:4px 8px;border-radius:10px;background:#fff;border:1.5px solid #cbd5e1;
          font-size:10.5px;line-height:1.26;font-weight:600;color:#1e293b;display:flex;align-items:center;justify-content:center;text-align:center;word-break:normal;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.06);}
  .bubble.active{border-color:#2563eb;background:#eff6ff;box-shadow:0 0 0 2px rgba(37,99,235,0.22);}
  .bubble.done{border-color:#86efac;background:#f0fdf4;color:#166534;}
  .pop{animation:pop .35s ease-out;}
  @keyframes pop{from{transform:scale(.6);opacity:0}to{transform:scale(1);opacity:1}}

  /* người đi bộ */
  .person{transition:opacity .25s;}
  .away .person{opacity:0;}
  .legL,.legR,.wArmL,.wArmR{transform-box:fill-box;transform-origin:50% 0;}
  .walking .legL{animation:lg .32s infinite alternate ease-in-out;}
  .walking .legR{animation:lg .32s .16s infinite alternate-reverse ease-in-out;}
  .walking .wArmL{animation:lg .32s .16s infinite alternate-reverse ease-in-out;}
  .walking .wArmR{animation:lg .32s infinite alternate ease-in-out;}
  .walking .wbody{animation:wb .32s infinite alternate ease-in-out;}
  @keyframes lg{from{transform:rotate(-28deg)}to{transform:rotate(28deg)}}
  @keyframes wb{from{transform:translateY(0)}to{transform:translateY(-3px)}}
  .alert text{animation:al .5s infinite alternate;}
  @keyframes al{from{transform:translateY(0)}to{transform:translateY(-6px)}}

  /* bong bóng đang trò chuyện */
  .bubble.chat{border-color:#f59e0b;background:#fffbeb;color:#78350f;}
  /* sửa lỗi bong bóng "trượt" từ góc trái khi hiện */
  .pop{transform-box:fill-box;transform-origin:50% 100%;}

  /* ── THANH TIẾN TRÌNH PIPELINE STEPPER ── */
  .stepper-wrap{
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:8px 16px;
    background:#ffffff;
    border-top:1px solid #e2e8f0;
    gap:4px;
    overflow-x:auto;
  }
  .step-item{
    display:flex;
    align-items:center;
    gap:6px;
    padding:4px 10px;
    border-radius:20px;
    font-size:11.5px;
    font-weight:700;
    color:#64748b;
    background:#f8fafc;
    border:1px solid #e2e8f0;
    transition:all .3s ease;
    white-space:nowrap;
  }
  .step-badge{
    width:18px;
    height:18px;
    border-radius:50%;
    background:#94a3b8;
    color:#ffffff;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:10px;
    font-weight:800;
  }
  .step-sep{color:#cbd5e1;font-size:11px;font-weight:700;}
  .step-item.active{
    background:#eff6ff;
    border-color:#3b82f6;
    color:#1d4ed8;
    box-shadow:0 0 0 2px rgba(59,130,246,0.18);
  }
  .step-item.active .step-badge{
    background:#2563eb;
    box-shadow:0 0 8px rgba(37,99,235,0.6);
  }
  .step-item.done{
    background:#f0fdf4;
    border-color:#86efac;
    color:#15803d;
  }
  .step-item.done .step-badge{
    background:#16a34a;
  }
</style></head>
<body>
<div class="wrap">
  <svg id="scene" viewBox="0 0 1000 430" xmlns="http://www.w3.org/2000/svg"></svg>
  <div class="stepper-wrap">
    <div id="step-pill-1" class="step-item"><span class="step-badge">1</span><span class="step-label">Rà soát Luật</span></div>
    <div class="step-sep">➔</div>
    <div id="step-pill-2" class="step-item"><span class="step-badge">2</span><span class="step-label">Lập Phương án</span></div>
    <div class="step-sep">➔</div>
    <div id="step-pill-3" class="step-item"><span class="step-badge">3</span><span class="step-label">Phản biện Rủi ro</span></div>
    <div class="step-sep">➔</div>
    <div id="step-pill-4" class="step-item"><span class="step-badge">4</span><span class="step-label">Soạn thảo NĐ 30</span></div>
    <div class="step-sep">➔</div>
    <div id="step-pill-5" class="step-item"><span class="step-badge">5</span><span class="step-label">Trưởng ban Duyệt</span></div>
  </div>
  <div class="bar"><span class="dot"></span><b>Tiến trình phối hợp:</b><span id="msg"></span></div>
</div>
<script>
const D = __DATA__;
const X = [105, 300, 495, 690, 890];          // tâm bàn của 5 agent
const SKIN = ["#fcd5b0","#f5c29a","#e8b48a","#fcd5b0","#d9a47a"];
const SHIRT = ["#2563eb","#f59e0b","#dc2626","#7c3aed","#0f172a"];
const HAIR = ["#1f2937","#78350f","#111827","#92400e","#374151"];
const esc = s => String(s).replace(/[&<"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

function background(){
  let s = `
  <defs>
    <linearGradient id="goldPlate" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="50%" stop-color="#eab308"/>
      <stop offset="100%" stop-color="#ca8a04"/>
    </linearGradient>
  </defs>
  <rect width="1000" height="250" fill="#e0e7ff"/>
  <!-- Đèn trần âm trần LED hiện đại -->
  <rect x="180" y="0" width="200" height="6" rx="2" fill="#fff" opacity=".7"/>
  <rect x="520" y="0" width="200" height="6" rx="2" fill="#fff" opacity=".7"/>
  <rect y="250" width="1000" height="180" fill="#cbd5e1"/>
  <rect y="246" width="1000" height="8" fill="#94a3b8"/>`;
  for(let i=0;i<20;i++) s += `<line x1="${i*55-20}" y1="430" x2="${i*55+40}" y2="254" stroke="#b6c2d1" stroke-width="1"/>`;
  // cửa sổ (đặt gọn ở dải tường trên)
  for(const wx of [40,430]) s += `<rect x="${wx}" y="8" width="140" height="50" rx="6" fill="#bae6fd" stroke="#fff" stroke-width="4"/>
    <line x1="${wx+70}" y1="8" x2="${wx+70}" y2="58" stroke="#fff" stroke-width="3"/>
    <line x1="${wx}" y1="33" x2="${wx+140}" y2="33" stroke="#fff" stroke-width="3"/>`;

  // đồng hồ (đặt cao y=10..52)
  s += `<circle cx="640" cy="32" r="22" fill="#fff" stroke="#475569" stroke-width="3"/>
    <line id="hh" x1="640" y1="32" x2="640" y2="20" stroke="#0f172a" stroke-width="2.5" stroke-linecap="round"/>
    <line id="mm" x1="640" y1="32" x2="651" y2="32" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>`;
  
  // phòng kính của Trưởng ban & Biển kim loại vàng (đặt cao y=10..34)
  s += `<rect x="792" y="10" width="200" height="344" rx="12" fill="#bae6fd" fill-opacity=".2" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="8 5"/>
    <!-- Vệt sáng phản chiếu mặt kính -->
    <path d="M830 10 L800 240 M920 10 L890 240" stroke="#ffffff" stroke-width="2" stroke-linecap="round" opacity=".4"/>
    <!-- Biển chức danh mạ vàng -->
    <rect x="815" y="12" width="154" height="24" rx="5" fill="url(#goldPlate)" stroke="#b45309" stroke-width="1.2"/>
    <text x="892" y="28" text-anchor="middle" font-size="10.5" font-weight="900" fill="#78350f" letter-spacing="0.5">🏛️ PHÒNG TRƯỞNG BAN</text>`;
  
  // cây cảnh
  s += `<g transform="translate(15,360)"><rect x="-12" y="0" width="24" height="26" rx="4" fill="#92400e"/>
    <path d="M0 0 C-30 -30 -20 -50 0 -60 C20 -50 30 -30 0 0Z" fill="#16a34a"/></g>`;
  return s;
}

function agentSVG(i, a, st){
  const x = X[i], status = st.status || "waiting";
  const cls = status==="active" ? "typing" : status==="done" ? "done" : "sleep";
  const screenFill = status==="active" ? "#0284c7" : status==="done" ? "#16a34a" : "#1e293b";
  const speech = esc(st.speech || "");
  const tagTxt = {waiting:"⏳ Chờ lượt", active:"⚡ Đang làm việc", done:"✅ Đã xong"}[status];
  const tagCol = {waiting:"#64748b", active:"#2563eb", done:"#16a34a"}[status];
  const bubbleCls = status;
  let g = `<g id="seat${i}" transform="translate(${x},0)" class="${cls}">`;
  if(status==="active") g += `<ellipse class="ring" cx="0" cy="230" rx="62" ry="100" fill="#60a5fa" opacity=".25"/>`;
  // ghế + thân + đầu
  g += `<rect x="-36" y="196" width="72" height="84" rx="16" fill="#475569"/>
    <g class="person">
    <g class="body"><rect x="-28" y="188" width="56" height="84" rx="20" fill="${SHIRT[i]}"/>
      <rect x="-10" y="188" width="20" height="14" rx="4" fill="#fff" opacity=".85"/></g>
    <g class="head">
      <circle cx="0" cy="162" r="25" fill="${SKIN[i]}"/>
      <path d="M-25 160 Q-24 134 0 134 Q24 134 25 160 Q12 146 0 148 Q-12 146 -25 160Z" fill="${HAIR[i]}"/>
      ${status==="sleep" || status==="waiting"
        ? `<path d="M-12 164 q4 3 8 0 M4 164 q4 3 8 0" stroke="#1f2937" stroke-width="2" fill="none"/>`
        : `<circle cx="-8" cy="164" r="2.6" fill="#1f2937"/><circle cx="8" cy="164" r="2.6" fill="#1f2937"/>
           <path d="M-7 173 q7 ${status==="done"?8:4} 14 0" stroke="#1f2937" stroke-width="2" fill="none"/>`}
    </g>
    <line class="armL" x1="-24" y1="206" x2="-16" y2="262" stroke="${SHIRT[i]}" stroke-width="13" stroke-linecap="round"/>
    <circle class="armL" cx="-16" cy="264" r="6" fill="${SKIN[i]}"/>
    ${status==="done" ? `
    <g class="waveArm" style="transform-origin: 22px 206px;">
      <line x1="22" y1="206" x2="38" y2="160" stroke="${SHIRT[i]}" stroke-width="13" stroke-linecap="round"/>
      <circle cx="40" cy="156" r="7" fill="${SKIN[i]}"/>
    </g>` : `
    <line class="armR" x1="24" y1="206" x2="16" y2="262" stroke="${SHIRT[i]}" stroke-width="13" stroke-linecap="round"/>
    <circle class="armR" cx="16" cy="264" r="6" fill="${SKIN[i]}"/>`}
    </g>`;
  // bóng đổ dưới chân bàn & chân ghế (3D drop shadows)
  g += `<ellipse cx="0" cy="350" rx="74" ry="7" fill="#64748b" opacity=".22"/>
        <ellipse cx="0" cy="282" rx="36" ry="5" fill="#475569" opacity=".25"/>`;
  // bàn
  g += `<rect x="-84" y="270" width="168" height="14" rx="3" fill="#b45309"/>
        <rect x="-78" y="284" width="156" height="64" fill="#d97706"/>
        <rect x="-74" y="299" width="148" height="24" rx="5" fill="#fff" opacity=".95" stroke="#fed7aa" stroke-width="1"/>
        <text x="0" y="315" text-anchor="middle" font-size="10.5" font-weight="700" fill="#0f172a">${esc(a.name)} · ${esc(a.title)}</text>`;
  // màn hình
  g += `<g transform="translate(36,226)"><rect width="46" height="34" rx="4" fill="#0f172a"/>
        <rect x="3" y="3" width="40" height="28" rx="2" fill="${screenFill}"/>
        ${status==="active" ? `<g class="scr"><line x1="8" y1="10" x2="34" y2="10"/><line x1="8" y1="17" x2="28" y2="17"/><line x1="8" y1="24" x2="38" y2="24"/><line x1="8" y1="14" x2="14" y2="14" opacity="0"/></g>` : ""}
        ${status==="done" ? `<text x="23" y="25" text-anchor="middle" font-size="18" fill="#fff">✓</text>` : ""}
        <rect x="18" y="34" width="10" height="6" fill="#475569"/></g>`;
  // Búa chủ tọa thẩm phán nếu là bàn Agent 5 (Trưởng ban)
  if(i === 4){
    g += `<g transform="translate(-50,258)">
      <rect x="0" y="8" width="22" height="4" rx="1" fill="#78350f"/>
      <rect x="14" y="2" width="8" height="16" rx="2" fill="#92400e" stroke="#451a03" stroke-width="1"/>
      <ellipse cx="11" cy="14" rx="13" ry="3" fill="#451a03" opacity=".35"/>
    </g>`;
  }
  // cà phê + zzz khi chờ
  if(status==="waiting"){
    g += `<g transform="translate(-62,256)"><rect width="14" height="14" rx="3" fill="#fff" stroke="#94a3b8"/>
          <g class="steam"><path d="M4 -2 q-3 -5 0 -9"/><path d="M10 -2 q-3 -5 0 -9"/></g></g>
          <g class="zzz" transform="translate(22,128)"><text font-size="16">Z</text><text font-size="13" x="10" y="-10">z</text><text font-size="11" x="18" y="-20">z</text></g>`;
  }
  // bong bóng thoại (chỉ hiển thị khi active hoặc done, ẩn hoàn toàn khi waiting để không che trang trí)
  const isWaiting = status === "waiting" || !speech;
  const tailFill = status==="active" ? "#2563eb" : status==="done" ? "#86efac" : "#cbd5e1";
  g += `<g class="pop" style="${isWaiting ? "display:none;" : ""}"><foreignObject x="-84" y="66" width="168" height="54">
        <div xmlns="http://www.w3.org/1999/xhtml" id="bub${i}" class="bubble ${bubbleCls}">${speech}</div></foreignObject>
        <path id="tail${i}" d="M-6 120 L0 130 L6 120Z" fill="${tailFill}"/></g>`;
  // nhãn trạng thái
  g += `<rect x="-52" y="352" width="104" height="22" rx="11" fill="${tagCol}"/>
        <text x="0" y="367" text-anchor="middle" font-size="11" font-weight="800" fill="#fff">${tagTxt}</text>`;
  g += `</g>`;
  return g;
}

const svg = document.getElementById("scene");
let html = background();
D.agents.forEach((a,i) => { html += agentSVG(i, a, D.states[a.id] || {}); });
html += `<g id="walkers"></g><g id="fx"></g>`;
svg.innerHTML = html;
document.getElementById("msg").innerHTML = " " + D.msg;

// đồng bộ thanh tiến trình 5 bước (Stepper)
function updateStepper(){
  for(let k=1; k<=5; k++){
    const el = document.getElementById("step-pill-" + k);
    if(!el) continue;
    const st = (D.states[k] || {}).status || "waiting";
    el.className = "step-item " + st;
    const bg = el.querySelector(".step-badge");
    if(st === "done"){
      bg.textContent = "✓";
    } else {
      bg.textContent = k;
    }
  }
}
updateStepper();

// đồng hồ chạy thật
(function tick(){const n=new Date(),m=n.getMinutes()*6-90,h=(n.getHours()%12)*30+n.getMinutes()*.5-90;
  const hh=document.getElementById("hh"),mm=document.getElementById("mm");
  hh.setAttribute("x2",640+13*Math.cos(h*Math.PI/180));hh.setAttribute("y2",32+13*Math.sin(h*Math.PI/180));
  mm.setAttribute("x2",640+18*Math.cos(m*Math.PI/180));mm.setAttribute("y2",32+18*Math.sin(m*Math.PI/180));})();

const NS = "http://www.w3.org/2000/svg";
const FLOOR = 428, SPEED = 180;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const WALK = document.getElementById("walkers"), FX = document.getElementById("fx");
const seatOf = i => document.getElementById("seat" + i);
const svgEl = document.getElementById("scene");
let idleTimer = null;

/* ───────── tiện ích chung ───────── */
function walkerSVG(i, paper){
  return `<g class="dir"><g class="wbody">
    <rect class="legL" x="-9" y="-32" width="9" height="32" rx="4" fill="#1e293b"/>
    <rect class="legR" x="1"  y="-32" width="9" height="32" rx="4" fill="#334155"/>
    <rect x="-14" y="-78" width="28" height="50" rx="10" fill="${SHIRT[i]}"/>
    <rect class="wArmL" x="-19" y="-74" width="8" height="34" rx="4" fill="${SHIRT[i]}"/>
    <rect class="wArmR" x="11"  y="-74" width="8" height="34" rx="4" fill="${SHIRT[i]}"/>
    <circle cx="0" cy="-92" r="15" fill="${SKIN[i]}"/>
    <path d="M-15 -94 Q-14 -109 0 -109 Q14 -109 15 -94 Q7 -102 0 -101 Q-7 -102 -15 -94Z" fill="${HAIR[i]}"/>
    <circle cx="6" cy="-91" r="2" fill="#1f2937"/>
    ${paper ? `<text class="paper" x="10" y="-44" font-size="20">📄</text>` : ""}
  </g></g>`;
}
function glide(el, x0, x1){
  return el.animate(
    [{transform:`translate(${x0}px,${FLOOR}px)`},{transform:`translate(${x1}px,${FLOOR}px)`}],
    {duration: Math.abs(x1-x0)/SPEED*1000, easing:"linear", fill:"forwards"}
  ).finished;
}
/* i = chỉ số 0..4. Agent đứng dậy, trả về "actor" */
function spawn(i, paper=false){
  const w = document.createElementNS(NS,"g");
  w.innerHTML = walkerSVG(i, paper);
  w.style.transform = `translate(${X[i]}px,${FLOOR}px)`;
  WALK.appendChild(w);
  seatOf(i).classList.add("away");
  return {i, w, x: X[i], dir: w.querySelector(".dir")};
}
async function go(a, x1){
  if(Math.abs(x1 - a.x) < 2) return;
  a.dir.setAttribute("transform", x1 < a.x ? "scale(-1,1)" : "");   // quay mặt theo hướng đi
  a.w.classList.add("walking");
  await glide(a.w, a.x, x1);
  a.w.classList.remove("walking");
  a.x = x1;
}
function sit(a){ a.w.remove(); seatOf(a.i).classList.remove("away"); }

/* đổi nội dung bong bóng thoại của agent i */
function talk(i, text, mood="chat"){
  const b = document.getElementById("bub" + i); if(!b) return;
  b.textContent = text; b.className = "bubble " + mood;
  const p = b.closest(".pop");
  if(p){ 
    p.style.display = ""; 
    p.style.animation = "none"; void p.getBoundingClientRect(); p.style.animation = ""; 
  }
  const tail = document.getElementById("tail" + i);
  if(tail){
    const col = mood === "active" ? "#2563eb" : mood === "done" ? "#86efac" : "#f59e0b";
    tail.setAttribute("fill", col);
  }
}
function restore(i){
  const st = D.states[D.agents[i].id] || {};
  const b = document.getElementById("bub" + i); if(!b) return;
  const status = st.status || "waiting";
  const speech = st.speech || "";
  b.textContent = speech; 
  b.className = "bubble " + status;
  const p = b.closest(".pop");
  if(p){
    if(status === "waiting" || !speech){
      p.style.display = "none";
    } else {
      p.style.display = "";
    }
  }
  const tail = document.getElementById("tail" + i);
  if(tail){
    const col = status === "active" ? "#2563eb" : status === "done" ? "#86efac" : "#cbd5e1";
    tail.setAttribute("fill", col);
  }
}
/* chữ/emoji bay lên rồi mờ dần */
function fxText(txt, x, y, o={}){
  const {size=26, dx=0, dy=-40, dur=1400} = o;
  const t = document.createElementNS(NS,"text");
  t.textContent = txt; t.setAttribute("font-size", size); t.setAttribute("text-anchor","middle");
  t.setAttribute("x", x); t.setAttribute("y", y);
  t.style.transformBox = "fill-box"; t.style.transformOrigin = "center";
  FX.appendChild(t);
  t.animate([
    {transform:"translate(0,0) scale(.6)", opacity:0},
    {transform:`translate(${dx/2}px,${dy/2}px) scale(1.2)`, opacity:1, offset:.3},
    {transform:`translate(${dx}px,${dy}px) scale(1)`, opacity:0}
  ], {duration:dur, fill:"forwards"}).onfinish = () => t.remove();
}
function confetti(cx){
  const cols = ["#f59e0b","#2563eb","#16a34a","#dc2626","#7c3aed"];
  for(let k=0;k<22;k++){
    const r = document.createElementNS(NS,"rect");
    r.setAttribute("width","7"); r.setAttribute("height","11"); r.setAttribute("fill", cols[k%5]);
    r.setAttribute("x", cx-20+Math.random()*40); r.setAttribute("y","30");
    FX.appendChild(r);
    r.animate([{transform:"translate(0,0) rotate(0deg)",opacity:1},
               {transform:`translate(${(Math.random()-.5)*200}px,360px) rotate(${Math.random()*720}deg)`,opacity:0}],
              {duration:1800+Math.random()*900, delay:Math.random()*400, fill:"forwards"}).onfinish = () => r.remove();
  }
}

/* ───────── 1) CHUYỂN GIAO CÓ HỘI THOẠI ───────── */
const HANDOFF = (D.lines && D.lines.handoff) || [
  ["Em gửi căn cứ pháp lý nhé!",      "Đã nhận, em lập phương án ngay 👀"],
  ["Đây là các phương án xử lý.",      "Nhận rồi, để em soi kẽ hở 🔎"],
  ["Phản biện xong, nhờ soạn văn bản.","OK, em soạn theo mẫu NĐ 30 ✍️"],
  ["Dự thảo xong, trình Trưởng ban.",  "Đã nhận. Tôi sẽ chấm ma trận ⚖️"],
];
async function handoff(i){
  const j = i + 1, a = spawn(i, true), stop = X[j] - 70;
  await go(a, stop);
  const pEl = a.w.querySelector(".paper"); if(pEl) pEl.remove();

  const paper = document.createElementNS(NS,"text");
  paper.textContent = "📄"; paper.setAttribute("font-size","24");
  paper.setAttribute("x", X[j]-40); paper.setAttribute("y","268");
  paper.animate([{transform:"translateY(-20px)",opacity:0},{transform:"translateY(0)",opacity:1}],{duration:300,fill:"forwards"});
  WALK.appendChild(paper);
  fxText("❗", X[j], 150, {size:28, dy:-20, dur:1500});

  talk(i, HANDOFF[i][0]);  await sleep(1100);
  talk(j, HANDOFF[i][1]);  await sleep(1300);

  restore(i);
  await go(a, X[i]);
  sit(a);
}

/* ───────── 2) AGENT ĐI SANG BÀN NHAU TRAO ĐỔI / TRANH LUẬN ───────── */
async function visit(sc){
  const a = spawn(sc.a), stop = X[sc.b] + 75;
  await go(a, stop);
  const mid = (stop + X[sc.b]) / 2;
  for(const [who, txt] of sc.lines){
    talk(who, txt, "chat");
    fxText(sc.clash ? (Math.random() < .5 ? "⚔️" : "💥") : "💬", mid, 236, {size:30, dy:-34, dur:1500});
    await sleep(2300);
  }
  [...new Set(sc.lines.map(l => l[0]))].forEach(restore);
  await go(a, X[sc.a]);
  sit(a); restore(sc.a);
}
function mail(i, j){
  const t = document.createElementNS(NS,"text");
  t.textContent = "✉️"; t.setAttribute("font-size","28"); t.setAttribute("x","-14"); t.setAttribute("y","0");
  FX.appendChild(t);
  const x0 = X[i], x1 = X[j] - 30;
  t.animate([
    {transform:`translate(${x0}px,250px) rotate(0deg)`, opacity:1},
    {transform:`translate(${(x0+x1)/2}px,150px) rotate(-12deg)`, opacity:1, offset:.5},
    {transform:`translate(${x1}px,235px) rotate(10deg)`, opacity:1}
  ], {duration:1500, easing:"ease-in-out", fill:"forwards"}).onfinish = () => {
    t.remove();
    talk(j, `Đã nhận báo cáo Agent ${i+1} ✔`, "chat");
    fxText("✔️", x1, 215, {size:22, dy:-30});
  };
}

/* ───────── 3) KỊCH BẢN THEO TỪNG AGENT (chạy khi agent đó "running") ───────── */
const SCENES = {
  search: async () => {
    const L = [["Đang quét FAISS Top-K...","🔍"],["Kiểm tra đồ thị hiệu lực...","🕸️"],
               ["🔴 Phát hiện điều luật hết hiệu lực — loại!","❌"],["✅ Giữ lại căn cứ còn hiệu lực","📚"]];
    for(const [t, e] of L){ talk(0, t, "active"); fxText(e, X[0]+40, 215, {size:28, dy:-50}); await sleep(2300); }
    restore(0);
  },
  consult2: () => visit({a:1, b:0, lines: (D.lines && D.lines.consult2) || [
    [1,"Căn cứ này áp dụng được cho vụ việc chứ?"],
    [0,"Được, còn hiệu lực. Điều khoản cũ đã bị loại."],
    [1,"Tuyệt! Em lập 2 phương án theo căn cứ đó."]]}),
  debate3: () => visit({a:2, b:1, clash:true, lines: (D.lines && D.lines.debate3) || [
    [2,"Phương án 1 chưa tính tới thời hiệu khiếu nại!"],
    [1,"Em đã nêu thời hạn xử lý ở bước 2 rồi mà."],
    [2,"Vẫn hở: thiếu chứng cứ xác nhận y tế!"],
    [1,"Ok, em bổ sung vào phương án."],
    [2,"Tốt. Ký nháy nhé ✍️"]]}),
  consult4: () => visit({a:3, b:2, lines: (D.lines && D.lines.consult4) || [
    [3,"Rủi ro nào bắt buộc nêu trong công văn?"],
    [2,"Thời hiệu và chứng cứ. Ghi rõ nhé."],
    [3,"Rõ. Em soạn theo mẫu NĐ 30."]]}),
  report: async () => {
    [0,1,2,3].forEach((i,k) => setTimeout(() => mail(i, 4), k * 1100));
    await sleep(4 * 1100 + 1800);
    for(const l of ["Đang tổng hợp 4 báo cáo...","Chấm ma trận đa tiêu chí (MCDA)..."]){
      talk(4, l, "active"); await sleep(2500);
    }
  },

  /* ───── CẢNH KẾT THÚC: họp chốt + đóng dấu ───── */
  finale: async () => {
    const spots = [470, 545, 620, 695, 770];
    const A = [0,1,2,3,4].map(i => spawn(i));
    document.getElementById("msg").innerHTML = " 🏛️ Toàn bộ 5 chuyên gia tập trung họp chốt hồ sơ...";
    await Promise.all(A.map((a,k) => go(a, spots[k])));
    A.forEach((a,k) => a.dir.setAttribute("transform", k < 2 ? "" : "scale(-1,1)"));  // quay vào giữa

    const L = (D.lines && D.lines.finale) || [
               "Căn cứ pháp lý: đã loại điều luật hết hiệu lực ✔",
               "2 phương án xử lý đã sẵn sàng ✔",
               "Rủi ro tố tụng đã được bịt kẽ hở ✔",
               "Dự thảo công văn chuẩn NĐ 30 đã xong ✔",
               "Tôi phê duyệt! Chốt phương án tối ưu 🎖️"];
    let cur = null;
    for(let k = 0; k < 5; k++){
      if(cur) cur.remove();
      const x = spots[k];
      cur = document.createElementNS(NS,"g");
      cur.innerHTML = `<foreignObject x="${x-105}" y="190" width="210" height="88">
          <div xmlns="http://www.w3.org/1999/xhtml" class="bubble chat pop">${esc(L[k])}</div></foreignObject>
          <path d="M${x-8} 278 L${x} 294 L${x+8} 278Z" fill="#f59e0b"/>`;
      FX.appendChild(cur);
      A[k].w.animate([{transform:`translate(${A[k].x}px,${FLOOR}px)`},{transform:`translate(${A[k].x}px,${FLOOR-14}px)`},
                      {transform:`translate(${A[k].x}px,${FLOOR}px)`}], {duration:400});
      await sleep(1700);
    }
    if(cur) cur.remove();

    // đóng dấu ĐÃ DUYỆT
    const st = document.createElementNS(NS,"g");
    st.innerHTML = `<g transform="translate(500,140) rotate(-10)">
      <rect x="-175" y="-50" width="350" height="100" rx="12" fill="#fff" fill-opacity=".93" stroke="#dc2626" stroke-width="8"/>
      <rect x="-162" y="-37" width="324" height="74" rx="8" fill="none" stroke="#dc2626" stroke-width="2"/>
      <text y="19" text-anchor="middle" font-size="54" font-weight="900" fill="#dc2626" letter-spacing="4">ĐÃ DUYỆT</text></g>`;
    st.style.transformOrigin = "500px 140px";
    FX.appendChild(st);
    st.animate([{transform:"scale(3.2)",opacity:0},{transform:"scale(.92)",opacity:1,offset:.6},{transform:"scale(1)",opacity:1}],
               {duration:450, easing:"cubic-bezier(.2,.9,.3,1.2)", fill:"forwards"});
    await sleep(400);
    svgEl.animate([{transform:"translate(0,0)"},{transform:"translate(-6px,4px)"},{transform:"translate(5px,-4px)"},
                   {transform:"translate(-3px,2px)"},{transform:"translate(0,0)"}], {duration:320});

    // cả nhóm nhảy ăn mừng + pháo giấy
    A.forEach((a,k) => a.w.animate(
      [{transform:`translate(${a.x}px,${FLOOR}px)`},{transform:`translate(${a.x}px,${FLOOR-34}px)`},{transform:`translate(${a.x}px,${FLOOR}px)`}],
      {duration:480, iterations:6, delay:k*80}));
    spots.forEach(confetti);
    fxText("🎉", 300, 200, {size:44, dy:-60, dur:2200});
    fxText("🎊", 700, 200, {size:44, dy:-60, dur:2200});
    document.getElementById("msg").innerHTML = " 📁 <b>HỒ SƠ ĐÃ ĐƯỢC TRƯỞNG BAN PHÊ DUYỆT — SẴN SÀNG TRÌNH KÝ</b>";
  }
};

/* ───────── 4) HOẠT ĐỘNG NGẪU NHIÊN CỦA NGƯỜI ĐANG CHỜ ───────── */
function idle(){
  const w = D.agents.map((a,i) => i).filter(i => (D.states[D.agents[i].id]||{}).status === "waiting");
  if(!w.length) return;
  const i = w[Math.floor(Math.random()*w.length)];
  const e = ["💤","☕","👀","🤔","📱"][Math.floor(Math.random()*5)];
  fxText(e, X[i]+30, 150, {size:22, dx:10, dy:-34, dur:1800});
}

/* ───────── 5) ĐIỀU PHỐI ───────── */
(async () => {
  if(D.scene && SCENES[D.scene]){
    if(D.scene !== "finale") idleTimer = setInterval(idle, 2200);
    await SCENES[D.scene]();
    return;
  }
  idleTimer = setInterval(idle, 2200);
  D.agents.forEach((a,i) => {
    const now = (D.states[a.id]||{}).status, was = ((D.prev||{})[a.id]||{}).status;
    if(now === "done" && was !== "done" && i < D.agents.length-1) handoff(i);
  });
})();
</script></body></html>
"""


# ── Helpers trích xuất & làm sạch đối thoại từ kết quả LLM ──────────────────
def _clean_solution_name(text: str, default_val: str) -> str:
    if not text:
        return default_val
    lower = text.lower()
    if "hòa giải" in lower or "thương lượng" in lower:
        if "cơ sở" in lower:
            return "Hòa giải cơ sở & Thương lượng"
        return "Hòa giải & Thương lượng"
    elif "chế tài" in lower or "xử phạt" in lower or "thanh tra" in lower:
        return "Chế tài & Xử lý vi phạm"
    elif "khởi kiện" in lower or "tòa án" in lower:
        return "Khởi kiện ra Tòa án"
    elif "khiếu nại" in lower:
        return "Khiếu nại hành chính"

    # Làm sạch chuỗi thông thường, không bao giờ ngắt vụn từ
    t = re.sub(r"[\*\#\:\(\)]", " ", text).strip()
    t = re.sub(r"^(Phương án \d+|PA \d+)\s*", "", t, flags=re.IGNORECASE).strip()
    parts = re.split(r"[,;/\n–—]", t)
    first_part = parts[0].strip()
    if 4 <= len(first_part) <= 28:
        return first_part
    words = first_part.split()
    res = []
    for w in words:
        if sum(len(x) + 1 for x in res) + len(w) > 26:
            break
        res.append(w)
    return " ".join(res) if res else default_val


def _clean_risk_phrase(text: str) -> str:
    lower = text.lower()
    if "thời hiệu" in lower:
        if "180" in lower or "khiếu nại" in lower:
            return "Thời hiệu khiếu nại 180 ngày"
        return "Thời hiệu & Trình tự thủ tục"
    elif "chứng cứ" in lower or "y tế" in lower or "thai" in lower:
        return "Chứng cứ thai kỳ & Hồ sơ y tế"
    elif "khiếu kiện" in lower:
        return "Nguy cơ bị khiếu kiện ngược"
    elif "kỷ luật" in lower or "sa thải" in lower:
        return "Trình tự họp xử lý kỷ luật"
    m = re.search(r"(?:thời hiệu[^\n,;]{3,24}|chứng cứ[^\n,;]{3,24}|khiếu kiện[^\n,;]{3,24})", text, re.IGNORECASE)
    if m:
        return m.group(0).strip(" -*#:")
    return "Thời hiệu & Chứng cứ pháp lý"


def _clean_doc_title(text: str) -> str:
    upper = text.upper()
    if "GIẤY MỜI" in upper:
        return "Giấy mời làm việc (chuẩn NĐ 30)"
    elif "BIÊN BẢN" in upper:
        return "Biên bản hòa giải (chuẩn NĐ 30)"
    elif "KIẾN NGHỊ" in upper or "XỬ PHẠT" in upper:
        return "Công văn kiến nghị xử lý (NĐ 30)"
    elif "CÔNG VĂN" in upper or "PHÚC ĐÁP" in upper:
        return "Công văn phúc đáp (chuẩn NĐ 30)"
    return "Dự thảo văn bản công vụ chuẩn NĐ 30"


def _clean_recommendation(text: str) -> str:
    lower = text.lower()
    if "phương án 1" in lower or "hòa giải" in lower or "thương lượng" in lower:
        return "Phương án 1 (Hòa giải thương lượng)"
    elif "phương án 2" in lower or "chế tài" in lower or "thanh tra" in lower:
        return "Phương án 2 (Chế tài xử phạt)"
    return "Phương án tối ưu theo MCDA"


def extract_case_dialogue_updates(step: int, output, case_dialogue: dict) -> dict:
    content = getattr(output, "content", "") or ""
    metadata = getattr(output, "metadata", {}) or {}

    if step == 1:
        chunks = metadata.get("chunks", [])
        found_articles = []
        if isinstance(chunks, list):
            for c in chunks[:5]:
                dieu = c.get("dieu_so")
                doc_t = c.get("doc_title", "")
                if dieu:
                    if "Bộ luật Lao động" in doc_t or "BLLĐ" in doc_t:
                        label = f"Điều {dieu} BLLĐ"
                    elif "12/2022" in doc_t:
                        label = f"NĐ 12/2022"
                    elif "145/2020" in doc_t:
                        label = f"NĐ 145/2020"
                    elif "Bảo hiểm xã hội" in doc_t:
                        label = f"Điều {dieu} Luật BHXH"
                    else:
                        label = f"Điều {dieu}"
                    if label not in found_articles:
                        found_articles.append(label)
        if not found_articles:
            raw_matches = re.findall(r"(?:Điều\s+\d+|Nghị định\s+\d+/\d+|Bộ luật Lao động)", content)
            found_articles = list(dict.fromkeys(raw_matches))[:2]

        art_str = " & ".join(found_articles[:2]) if found_articles else "BLLĐ 2019"

        case_dialogue["handoff"][0] = [
            f"Gửi căn cứ {art_str} đã rà soát nhé!",
            f"Đã nhận căn cứ {art_str}, lập phương án ngay!",
        ]
        case_dialogue["consult2"] = [
            [1, f"Căn cứ {art_str} có đủ cơ sở xử lý vụ này chứ?"],
            [0, f"Rất vững, {art_str} đang còn hiệu lực và cấm sa thải!"],
            [1, "Tuyệt vời, bắt tay thiết kế 2 phương án xử lý ngay."],
        ]
        case_dialogue["finale"][0] = f"Căn cứ: {art_str} (100% còn hiệu lực) ✔"

    elif step == 2:
        m1 = re.search(r"Phương án 1\s*[\(\:]*\s*([^\n\:\*]{5,60})", content, re.IGNORECASE)
        m2 = re.search(r"Phương án 2\s*[\(\:]*\s*([^\n\:\*]{5,60})", content, re.IGNORECASE)
        pa1 = _clean_solution_name(m1.group(1) if m1 else "", "Hòa giải thương lượng")
        pa2 = _clean_solution_name(m2.group(1) if m2 else "", "Chế tài & Khởi kiện")

        case_dialogue["handoff"][1] = [
            f"Đã lập xong: {pa1} & {pa2}.",
            "Nhận rồi, để soi kẽ hở & rủi ro 🔎",
        ]
        case_dialogue["debate3"] = [
            [2, f"Phương án '{pa1}' có rủi ro về thời hiệu hoặc chứng cứ!"],
            [1, f"Bên tôi đã dự trù cả '{pa2}' nếu doanh nghiệp bất hợp tác."],
            [2, "Cần bổ sung chứng cứ y tế & cam kết bồi thường rõ ràng!"],
            [1, "Nhất trí, tôi siết chặt quy trình trong phương án."],
            [2, "Tốt, hồ sơ đã chặt chẽ. Ký nháy chuyển sang soạn thảo ✍️"],
        ]
        case_dialogue["finale"][1] = f"2 Phương án: {pa1} | {pa2} ✔"

    elif step == 3:
        risk = _clean_risk_phrase(content)

        case_dialogue["handoff"][2] = [
            f"Đã phản biện xong rủi ro: {risk}.",
            "OK, đưa vào dự thảo chuẩn NĐ 30 ✍️",
        ]
        case_dialogue["consult4"] = [
            [3, f"Rủi ro '{risk}' cần đưa vào công văn thế nào?"],
            [2, "Ghi rõ thời hạn giải quyết và yêu cầu cung cấp chứng cứ nhé."],
            [3, "Rõ, lập dự thảo văn bản chuẩn mẫu NĐ 30 ngay."],
        ]
        case_dialogue["finale"][2] = f"Đã bịt kín rủi ro: {risk} ✔"

    elif step == 4:
        doc_title = _clean_doc_title(content)

        case_dialogue["handoff"][3] = [
            f"Đã soạn xong {doc_title}, kính trình Trưởng ban.",
            "Đã nhận dự thảo! Tôi sẽ chấm ma trận MCDA ⚖️",
        ]
        case_dialogue["finale"][3] = f"Hoàn tất: {doc_title} ✔"

    elif step == 5:
        rec = _clean_recommendation(content)
        case_dialogue["finale"][4] = f"Quyết định: Phê duyệt {rec}! Trình ký 🎖️"

    return case_dialogue


def generate_war_room_scene_html(
    agent_states: dict,
    action_msg: str,
    prev_states: dict = None,
    scene: str = None,
    case_lines: dict = None,
) -> str:
    data = {
        "agents": [{"id": a["id"], "name": a["name"], "title": a["title"]} for a in AGENTS_META],
        "states": {str(k): v for k, v in agent_states.items()},
        "prev": {str(k): v for k, v in (prev_states or {}).items()},
        "msg": action_msg,
        "scene": scene,
        "lines": case_lines or {},
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return OFFICE_SCENE_TEMPLATE.replace("__DATA__", payload)


def render_office(placeholder, agent_states, action_msg, prev_states=None, scene=None, case_lines=None):
    html_content = generate_war_room_scene_html(agent_states, action_msg, prev_states, scene, case_lines)
    with placeholder:
        if hasattr(st, "iframe"):
            st.iframe(html_content, height=600)
        else:
            components.html(html_content, height=600)


def format_a4_html(text: str) -> str:
    """Định dạng nội dung văn bản hành chính theo khuôn mẫu A4 chuẩn Nghị định 30/2020/NĐ-CP."""
    if not text:
        return ""
    lines = text.split("\n")
    out = []
    for line in lines:
        raw_strip = line.strip()
        if not raw_strip:
            out.append("<div style='height:12px;'></div>")
            continue
        if raw_strip == "---":
            out.append("<hr style='border:none; border-top:1px solid #cbd5e1; margin:16px 0;'/>")
            continue

        if raw_strip.startswith("### "):
            h = html.escape(raw_strip[4:])
            out.append(f"<div style='font-size:1.15rem; font-weight:700; margin:14px 0 6px 0; text-align:center;'>{h}</div>")
            continue
        elif raw_strip.startswith("## "):
            h = html.escape(raw_strip[3:])
            out.append(f"<div style='font-size:1.25rem; font-weight:700; margin:16px 0 8px 0; text-align:center;'>{h}</div>")
            continue
        elif raw_strip.startswith("# "):
            h = html.escape(raw_strip[2:])
            out.append(f"<div style='font-size:1.35rem; font-weight:800; margin:18px 0 10px 0; text-align:center;'>{h}</div>")
            continue

        l = html.escape(line)
        l = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", l)
        l = re.sub(r"\*(.+?)\*", r"<i>\1</i>", l)

        upper_l = raw_strip.upper()
        if "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in upper_l or "ĐỘC LẬP - TỰ DO - HẠNH PHÚC" in upper_l:
            out.append(f"<div style='text-align:center; font-weight:700; line-height:1.4;'>{l}</div>")
        elif raw_strip.startswith("GIẤY MỜI") or raw_strip.startswith("CÔNG VĂN") or raw_strip.startswith("BIÊN BẢN") or raw_strip.startswith("QUYẾT ĐỊNH"):
            out.append(f"<div style='text-align:center; font-size:1.2rem; font-weight:800; margin:14px 0 6px 0;'>{l}</div>")
        else:
            out.append(f"<div style='margin-bottom:6px; line-height:1.65;'>{l}</div>")
    return "\n".join(out)


def render_war_room_dossier(final_res):
    """Hiển thị toàn bộ kết quả hội chẩn 5 Agent trong War Room kèm 5 Tabs và nút tải file Markdown."""
    st.markdown(
        f"""
        <div style="background:#f0fdf4; border:1px solid #86efac; border-left:4px solid #16a34a; padding:12px 18px; border-radius:8px; margin-bottom:18px;">
            <b>🏛️ KẾT QUẢ HỘI CHẨN ĐA TÁC NHÂN (WAR ROOM):</b> Tiến trình xử lý khép kín hoàn tất trong <b>{final_res.total_latency:.2f} giây</b> qua 5 chuyên gia AI.
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Agent 1: Căn cứ Pháp lý",
        "Agent 2: Đề xuất Phương án",
        "Agent 3: Phản biện Rủi ro",
        "Agent 4: Dự thảo NĐ 30",
        "Agent 5: Ma trận Quyết định",
    ])

    with tab1:
        st.markdown(f"#### {final_res.agent1_retrieval.title}")
        st.caption(f"Thời gian: `{final_res.agent1_retrieval.latency:.2f}s` | Lọc bỏ căn cứ [DANGER]")
        st.markdown(final_res.agent1_retrieval.content)

    with tab2:
        st.markdown(f"#### {final_res.agent2_solutions.title}")
        st.caption(f"Thời gian: `{final_res.agent2_solutions.latency:.2f}s` | Đề xuất Phương án Hòa giải & Chế tài")
        st.markdown(final_res.agent2_solutions.content)

    with tab3:
        st.markdown(f"#### {final_res.agent3_critique.title}")
        st.caption(f"Thời gian: `{final_res.agent3_critique.latency:.2f}s` | Đánh giá rủi ro tố tụng & thời hiệu")
        st.markdown(final_res.agent3_critique.content)

    with tab4:
        st.markdown(f"#### {final_res.agent4_draft.title}")
        st.caption(f"Thời gian: `{final_res.agent4_draft.latency:.2f}s` | Soạn thảo theo chuẩn Nghị định 30/2020/NĐ-CP")
        st.markdown(
            f"""
            <div class="a4-document-container">
                <div style="text-align:center; margin-bottom:14px;">
                    <span class="a4-doc-badge">📜 DỰ THẢO VĂN BẢN CÔNG VỤ • CHUẨN THỂ THỨC NGHỊ ĐỊNH 30/2020/NĐ-CP</span>
                </div>
                <div class="a4-paper-sheet">
                    {format_a4_html(final_res.agent4_draft.content)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab5:
        st.markdown(f"#### {final_res.agent5_evaluation.title}")
        st.caption(f"Thời gian: `{final_res.agent5_evaluation.latency:.2f}s` | Khuyến nghị tối ưu cho Cán bộ")
        st.markdown(final_res.agent5_evaluation.content)

    st.markdown("---")
    # Nút tải toàn bộ hồ sơ
    full_doc = f"# HỒ SƠ TƯ VẤN & THAM MƯU XỬ LÝ VỤ VIỆC PHÁP LÝ\n" \
               f"**Hệ thống AI Đa tác nhân (War Room Multi-Agent System)**\n\n" \
               f"## I. TÌNH HUỐNG / VỤ VIỆC ĐẦU VÀO\n{final_res.case_description}\n\n" \
               f"## II. CĂN CỨ PHÁP LÝ HIỆN HÀNH (AGENT 1)\n{final_res.agent1_retrieval.content}\n\n" \
               f"## III. PHÂN TÍCH & CÁC PHƯƠNG ÁN XỬ LÝ (AGENT 2)\n{final_res.agent2_solutions.content}\n\n" \
               f"## IV. BÁO CÁO PHẢN BIỆN RỦI RO & KHẮC PHỤC (AGENT 3)\n{final_res.agent3_critique.content}\n\n" \
               f"## V. DỰ THẢO VĂN BẢN CÔNG VỤ (AGENT 4)\n{final_res.agent4_draft.content}\n\n" \
               f"## VI. MA TRẬN ĐÁNH GIÁ & KHUYẾN NGHỊ RA QUYẾT ĐỊNH (AGENT 5)\n{final_res.agent5_evaluation.content}\n"

    st.download_button(
        label="📥 Tải toàn bộ Hồ sơ Tham mưu Tư vấn (.md)",
        data=full_doc,
        file_name="ho_so_tham_muu_war_room.md",
        mime="text/markdown",
        use_container_width=True,
    )



