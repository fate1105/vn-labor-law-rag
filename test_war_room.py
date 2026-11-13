"""
Script kiểm thử nhanh Hệ thống AI Đa tác nhân (War Room Multi-Agent System)
Chạy: python test_war_room.py
"""

import sys
import io
import time
import pathlib

# Cấu hình UTF-8 console Windows
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.war_room import WarRoomOrchestrator

SAMPLE_CASE = """Bà Lê Thị Hương là công nhân may tại Công ty TNHH May mặc Hưng Thịnh, đang mang thai tháng thứ 5. 
Do ốm sốt thai kỳ, bà Hương nghỉ việc 03 ngày (có giấy xác nhận của Trạm Y tế xã). 
Tuy nhiên, Giám đốc công ty cho rằng bà tự ý bỏ việc, ban hành quyết định sa thải ngay lập tức và giữ 15 ngày tiền lương tháng gần nhất của bà Hương. 
Bà Hương đã gửi đơn khiếu nại đến UBND xã yêu cầu can thiệp bảo vệ quyền lợi hợp pháp."""

def main():
    print("=" * 80)
    print("🏛️ KIỂM THỬ HỆ THỐNG AI ĐA TÁC NHÂN (WAR ROOM MULTI-AGENT ARCHITECTURE)")
    print("=" * 80)
    print(f"\n📋 TÌNH HUỐNG ĐẦU VÀO:\n{SAMPLE_CASE}\n")
    print("-" * 80)

    orchestrator = WarRoomOrchestrator()
    print("\n🚀 Bắt đầu vận hành quy trình War Room (5 Agents)...")

    stream = orchestrator.execute_stream(SAMPLE_CASE, delay_between_agents=1.5)
    
    for event in stream:
        status = event.get("status")
        if status == "running":
            print(f"\n⏳ [{event['agent']}] — {event['msg']}")
        elif status == "completed":
            out = event["output"]
            print(f"✅ [{out.agent_name}] hoàn tất ({out.latency:.2f}s)!")
            print(f"   📌 Tiêu đề: {out.title}")
            print("   " + "-" * 70)
            # In trích đoạn 3 dòng đầu
            lines = [l for l in out.content.split("\n") if l.strip()]
            preview = "\n   ".join(lines[:4])
            print(f"   {preview}\n   ...")
        elif status == "finished":
            res = event["result"]
            print("\n" + "=" * 80)
            print(f"🎉 TOÀN BỘ TIẾN TRÌNH WAR ROOM ĐÃ HOÀN TẤT THÀNH CÔNG!")
            print(f"⏱️ Tổng thời gian thực thi: {res.total_latency:.2f}s")
            print("=" * 80)

if __name__ == "__main__":
    main()

