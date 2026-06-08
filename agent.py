import os
import requests
import feedparser
from google import genai

# ตั้งค่าคีย์และไอดีระบบผ่าน Environment Variables
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_latest_news():
    # ดึงข่าวล่าสุดจาก RSS Feed ของ Sky Sports Football
    feed_url = "https://skysports.com" 
    feed = feedparser.parse(feed_url)
    if feed.entries:
        latest = feed.entries[0]
        return f"Title: {latest.title}\nDescription: {latest.description}"
    return "No news found."

def generate_content(news_text):
    # สั่งงานสมอง Gemini ให้เขียนคอนเทนต์และคิด Prompt รูปภาพ
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
    ---
    [เนื้อหาโพสต์ภาษาไทย]
    ---
    [คำสั่งสร้างภาพภาษาอังกฤษสั้นๆ เช่น A funny 3D cartoon of a sad rival football fan, comedy style]
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    # ดึงค่าคำตอบออกมาให้ถูกต้องตามโครงสร้างใหม่
    return response.text

def send_to_telegram(text, image_url):
    # ส่งทั้งข้อความและรูปภาพตรงเข้า Telegram ของคุณ
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": image_url,
        "caption": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    print(f"Telegram Response: {response.text}")

def main():
    try:
        news = get_latest_news()
        ai_output = generate_content(news)
        
        # แยกเนื้อหาบทความ กับ คำสั่งเจนรูปภาพออกจากกันด้วยเครื่องหมาย ---
        parts = ai_output.split("---")
        
        if len(parts) >= 3:
            post_content = parts[1].strip()
            image_prompt = parts[2].replace("[", "").replace("]", "").strip()
        elif len(parts) == 2:
            post_content = parts[0].strip()
            image_prompt = parts[1].replace("[", "").replace("]", "").strip()
        else:
            post_content = ai_output
            image_prompt = "Manchester United funny cartoon"
        
        # ส่ง Prompt ไปที่ Pollinations AI เพื่อดึงลิงก์รูปภาพฟรี
        encoded_prompt = requests.utils.quote(image_prompt)
        image_url = f"https://pollinations.ai{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        send_to_telegram(post_content, image_url)
        print("ส่งรายงานเข้า Telegram สำเร็จเรียบร้อย!")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()
