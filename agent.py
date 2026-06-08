import os
import requests
import feedparser
from google import genai

# ดึงค่าความปลอดภัยจาก GitHub Secrets
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def get_latest_news():
    # ข่าวด่วนฟุตบอล
    feed_url = "https://skysports.com" 
    feed = feedparser.parse(feed_url)
    if feed.entries:
        latest = feed.entries[0]
        return f"หัวข้อข่าว: {latest.title}\nรายละเอียด: {latest.description}"
    return "ไม่พบข่าวสารล่าสุด"

def generate_content(news_text):
    client = genai.Client(api_key=GEMINI_KEY)
    
    prompt = f"""
    คุณคือ "แอดมินท่านเซอร์" แฟนบอลแมนยูสายกวน เจนเนื้อหาภาษาไทยจากข่าวนี้:
    {news_text}
    
    กฎเหล็ก:
    1. สรุปข่าวให้อ่านสนุก กระชับไม่เกิน 5-6 บรรทัด ภาษาเพจฟุตบอลตลกและกวนประสาท
    2. เน้นอวยแมนยู แซวคู่แข่งร่วมลีกแบบน่าหมั่นไส้ (ห้ามหยาบคายรุนแรง)
    3. จบด้วยประโยคสะกิดต่อมเรียกทัวร์ลงให้คนอยากเข้ามาเขียนคอมเมนต์
    4. ปิดท้ายบทความด้วยแฮชแท็ก (#) เก๋ๆ จำนวน 5-7 อัน
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text

def send_to_telegram_text(content_text):
    # ส่งเฉพาะเนื้อหาข้อความตรงเข้า Telegram (เลี่ยงปัญหาไฟล์ภาพพัง)
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": content_text
    }
    response = requests.post(url, json=payload)
    print(f"ผลลัพธ์การส่งจาก Telegram API: {response.text}")

def main():
    try:
        news = get_latest_news()
        print(f"ดึงข่าวสำเร็จ: {news}")
        
        post_content = generate_content(news)
        print(f"AI เจนเนื้อหาสำเร็จ: {post_content}")
        
        send_to_telegram_text(post_content)
        print("ระบบรันเสร็จสิ้นกระบวนการเรียบร้อย!")
    except Exception as e:
        print(f"เกิดข้อผิดพลาดฉุกเฉินในระบบ: {e}")

if __name__ == "__main__":
    main()
