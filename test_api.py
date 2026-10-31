"""
Test nhanh Gemini API Key
Chạy: python test_api.py
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from google import genai

load_dotenv()

try:
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Xin chào! Trả lời ngắn gọn 1 câu: bạn là ai?"
    )
    print("✅ API Key hoạt động tốt!")
    print("📝 Phản hồi từ Gemini:", response.text)
except Exception as e:
    print("❌ Lỗi:", e)
    print("👉 Kiểm tra lại GEMINI_API_KEY trong file .env")
