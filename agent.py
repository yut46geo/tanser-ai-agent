import os
import requests
import feedparser
from google import genai

# ตั้งค่าคีย์และไอดีระบบผ่าน Environment Variables
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_latest_news():
    # ดึงข่าวฟุตบอลล่าสุด
    feed_url = "https://skysports.com" 
    feed = feedparser.parse(feed_url)
    if feed.entries:
        latest = feed.entries[0]
        title = getattr(latest, 'title', 'No Title')
        desc = getattr(latest, 'description', 'No Description')
        return f"Title: {title}\nDescription: {desc}"
    return "No news found."

def generate_content(news_text):
    client = genai.Client(api_key=GEMINI_KEY)
    
    prompt = f"""
    คุณคือ "แอดมินท่านเซอร์" เจ้าของเพจฟุตบอลแมนยูสายกวน เจนเนื้อหาจากข่าวนี้:
    {news_text}
    
    กฎการเขียน:
    1. สรุปข่าวให้กระชับ ยาวไม่เกิน 5-6 บรรทัด ภาษาวัยรุ่นไทย กวนประสาท ตลก
    2. เน้นอวยแมนยู และแซวขยี้ทีมคู่แข่งร่วมลีกด้วยฉายาฮาๆ ไม่หยาบคาย
    3. จบด้วยประโยคสะกิดต่อมเรียกคอมเมนต์ (Call to Action)
    4. ใส่แฮชแท็ก (#) ที่เกี่ยวข้องท้ายบทความ 5-7 อัน
    
    รูปแบบคำตอบ (Strict Output Format):
    [เนื้อหาโพสต์ภาษาไทย]
    ===SPLIT===
    [คำสั่งสร้างภาพภาษาอังกฤษสั้นๆ เช่น A funny 3D cartoon of a sad rival football fan, comedy style]
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text

def send_to_telegram(text, image_url):
    # เปลี่ยนมาส่งแบบธรรมดา ไม่ใช้ Markdown เพื่อป้องกันโค้ดอักขระพังแล้วบอทไม่ยอมส่ง
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": image_url,
        "caption": text
    }
    response = requests.post(url, json=payload)
    print(f"Telegram Response: {response.text}")

def main():
    try:
        news = get_latest_news()
        ai_output = generate_content(news)
        
        # เปลี่ยนตัวแยกเป็น ===SPLIT=== เพื่อความแม่นยำ ไม่ให้สับสนกับเครื่องหมายขีดในข่าว
        parts = ai_output.split("===SPLIT===")
        
        post_content = parts[0].strip() if len(parts) > 0 else ai_output
        image_prompt = parts[1].strip() if len(parts) > 1 else "Manchester United funny cartoon"
        
        # ล้างอักขระพิเศษส่วนเกินออกจาก Prompt รูปภาพ
        image_prompt = image_prompt.replace("[", "").replace("]", "").strip()
        
        encoded_prompt = requests.utils.quote(image_prompt)
        image_url = f"https://pollinations.ai{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        send_to_telegram(post_content, image_url)
        print("ส่งรายงานเข้า Telegram สำเร็จเรียบร้อย!")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()
