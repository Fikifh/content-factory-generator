import os
import asyncio
import requests
import json
import re
from dotenv import load_dotenv
from google import genai
import edge_tts

# Try importing for MoviePy v1.x, fallback to v2.x logic if needed
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
except ImportError:
    from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips

# Load Environment Variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
VOICE = os.getenv("TIKTOK_VOICE", "id-ID-ArdiNeural")
SPEED = os.getenv("TIKTOK_SPEED", "+10%")

# Initialize Gemini
client_ai = None
if GEMINI_API_KEY:
    try:
        client_ai = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"⚠️ Failed to init Gemini: {e}")

async def generate_script_json(topic):
    """
    Generate script in JSON format: [{text, visual_keyword}, ...]
    """
    print(f"🧠 Generating SCENE-BASED script for: {topic}...")
    
    if not client_ai: return None

    prompt = f"""
    Bertindaklah sebagai Video Editor TikTok profesional.
    Buatkan naskah video pendek (total 30-40 detik) tentang: "{topic}".

    Berikut adalah kerangka konten standar (sekitar 40 detik) yang dirancang dengan format "winning formula" edukasi anatomi:

    ⚙️ Spesifikasi Teknis & Format Dasar
    Rasio Video: Vertikal (9:16).

    Visual Utama: Visualisasi kaya yang menampilkan gambar/animasi anatomi atau organ dalam tubuh.

    Presenter: Avatar 3D realistis perempuan, mengambang (floating) di sisi kiri layar secara konsisten pada setiap adegan, sementara latar belakang tetap menampilkan visualisasi video utama.

    Audio: Voice-over (VO) perempuan dengan bahasa dan logat Indonesia yang natural.

    Teks: Tanpa teks di layar (no text overlay) dan bersih dari kata-kata yang dilarang oleh aturan affiliate TikTok.

    Gaya Bahasa: Informatif dan edukatif (bukan cerita atau pengalaman personal).

    Syarat Produk: Dipastikan sudah terdaftar PIRT.

    📋 Kerangka Naskah (Formula "Apa yang Terjadi Pada Tubuhmu?")
    1. Hook Visual & Anatomi (0 - 5 Detik)

    Fokus: Langsung menarik perhatian dengan pertanyaan "Apa yang akan terjadi pada tubuhmu jika kamu mengonsumsi [Nama Produk]?"

    Visual: Latar belakang langsung menampilkan animasi atau gambar anatomi organ target (misalnya usus, lambung, atau peredaran darah) yang membutuhkan perawatan. Avatar di kiri mulai berbicara.

    2. Edukasi Bahan Utama 1 (5 - 17 Detik)

    Fokus: Membedah komposisi bahan pertama dan menjelaskan secara ilmiah namun mudah dipahami tentang manfaatnya bagi tubuh.

    Visual: Transisi ke visualisasi bahan herbal pertama (misal: ekstrak rimpang/daun) yang masuk ke dalam tubuh, lalu menunjukkan efek visual bagaimana bahan tersebut bereaksi pada organ (misal: meluruhkan kotoran atau meredakan inflamasi).

    3. Edukasi Bahan Utama 2 (17 - 28 Detik)

    Fokus: Melanjutkan ke bahan komposisi kedua dan bagaimana bahan ini bekerja sama dengan bahan pertama untuk menyelesaikan masalah pada organ tersebut.

    Visual: Menampilkan bahan herbal kedua bekerja di dalam anatomi tubuh, memperlihatkan proses perbaikan atau pemulihan fungsi organ secara visual.

    4. Hasil Akhir pada Tubuh (28 - 35 Detik)

    Fokus: Kesimpulan dari efek sinergis seluruh bahan-bahan herbal tersebut. Memberikan pemahaman edukatif tentang kondisi tubuh yang kembali optimal.

    Visual: Menampilkan keseluruhan sistem organ tubuh yang kini terlihat sehat, bersih, dan berfungsi dengan baik.

    5. Call to Action / Penutup (35 - 40 Detik)

    Fokus: Mengarahkan penonton secara halus untuk mendapatkan solusi herbal tersebut.

    Visual: Menampilkan kemasan produk herbal yang jelas (dengan logo PIRT terlihat atau tersirat), sementara avatar memberikan isyarat ke arah keranjang kuning.

    Kerangka ini sangat efektif karena penonton TikTok cenderung menyukai konten yang memberi tahu mereka sesuatu yang baru secara visual (edukasi anatomi), alih-alih sekadar disuruh membeli barang.
    
    PENTING: Keluarkan output HANYA dalam format JSON Array murni. Jangan ada markdown (```json), jangan ada teks pembuka/penutup.
    
    Struktur JSON harus seperti ini:
    [
        {{"text": "Kalimat narasi hook yang memikat.", "keyword": "english keyword for visual representation"}},
        {{"text": "Kalimat menjelaskan masalah.", "keyword": "english keyword specific to problem"}},
        {{"text": "Kalimat menjelaskan solusi.", "keyword": "english keyword specific to solution"}},
        {{"text": "Kalimat Call to Action.", "keyword": "english keyword for clicking/buying"}}
    ]

    Pastikan "keyword" dalam Bahasa Inggris agar mudah dicari di stock footage, dan "text" dalam Bahasa Indonesia Gaul.
    """

    try:
        response = client_ai.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        raw_text = response.text.strip()
        
        # Bersihkan markdown json jika ada
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "")
        
        script_data = json.loads(raw_text)
        print(f"✅ Script Generated: {len(script_data)} scenes.")
        return script_data
    except Exception as e:
        print(f"❌ Error generating JSON script: {e}")
        print(f"Raw Output: {raw_text if 'raw_text' in locals() else 'None'}")
        return None

async def generate_audio_segment(text, filename):
    try:
        communicate = edge_tts.Communicate(text, VOICE, rate=SPEED)
        await communicate.save(filename)
        return filename
    except Exception as e:
        print(f"❌ Audio Gen Error: {e}")
        return None

def download_video_segment(query, filename):
    if not PEXELS_API_KEY: return None
    
    headers = {"Authorization": PEXELS_API_KEY}
    # Cari video portrait, ambil yang durasinya pendek
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation=portrait&size=medium"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['videos']:
                # Pilih video yang durasinya minimal 5 detik agar aman dipotong
                # Prioritaskan video yang tidak terlalu besar
                valid_videos = [v for v in data['videos'] if v['duration'] >= 5]
                target_video = valid_videos[0] if valid_videos else data['videos'][0]
                
                # Ambil link file video (preferensi HD tapi ringan)
                video_files = target_video['video_files']
                # Sort by width descending, pick one close to 720p or 1080p
                video_files.sort(key=lambda x: x['width'], reverse=True)
                download_link = video_files[0]['link']
                
                for v in video_files:
                    if v['width'] <= 1080 and v['width'] >= 720:
                        download_link = v['link']
                        break

                print(f"⬇️ Downloading for '{query}'...")
                vid_data = requests.get(download_link).content
                with open(filename, 'wb') as f:
                    f.write(vid_data)
                return filename
    except Exception as e:
        print(f"❌ Video DL Error ({query}): {e}")
        return None
    return None

def create_scene_clip(audio_path, video_path):
    try:
        audio_clip = AudioFileClip(audio_path)
        video_clip = VideoFileClip(video_path)
        
        # Audio duration controls scene length
        scene_duration = audio_clip.duration + 0.2 # Tambah buffer dikit biar gak kepotong
        
        # Loop or Cut Video
        if video_clip.duration < scene_duration:
            video_clip = video_clip.loop(duration=scene_duration)
        else:
            video_clip = video_clip.subclip(0, scene_duration)
            
        # Resize/Crop to Vertical 9:16 (1080x1920) logic simple
        # Asumsi Pexels sudah portrait, kita force resize fit height
        if video_clip.size[1] != 1920:
             # Resize height to 1920, maintain aspect ratio
             video_clip = video_clip.resize(height=1920)
             # Center Crop width to 1080
             if video_clip.size[0] > 1080:
                 video_clip = video_clip.crop(x1=video_clip.size[0]/2 - 540, width=1080)
        
        final_scene = video_clip.set_audio(audio_clip)
        return final_scene
    except Exception as e:
        print(f"❌ Scene Assembly Error: {e}")
        return None

async def main():
    TOPIC = "Apa yang terjadi pada tubuhmu jika rajin konsumsi jahe, kunyit, sereh dalam seminggu?"
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMP_DIR = os.path.join(BASE_DIR, "temp")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    
    # Create dirs
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Generate JSON Script
    scenes_data = await generate_script_json(TOPIC)
    if not scenes_data: return

    final_clips = []

    # 2. Process Each Scene
    for i, scene in enumerate(scenes_data):
        print(f"\n🎬 Processing Scene {i+1}: {scene['keyword']}")
        
        audio_path = os.path.join(TEMP_DIR, f"audio_{i}.mp3")
        video_path = os.path.join(TEMP_DIR, f"video_{i}.mp4")
        
        # A. Audio
        await generate_audio_segment(scene['text'], audio_path)
        
        # B. Video
        download_video_segment(scene['keyword'], video_path)
        
        # C. Assemble Scene
        if os.path.exists(audio_path) and os.path.exists(video_path):
            clip = create_scene_clip(audio_path, video_path)
            if clip:
                final_clips.append(clip)
        else:
            print("⚠️ Skipping scene due to missing asset.")

    # 3. Final Assembly
    if final_clips:
        print("\n🔨 Stitching all scenes together...")
        final_video = concatenate_videoclips(final_clips, method="compose")
        output_file = os.path.join(OUTPUT_DIR, "tiktok_smart_scene.mp4")
        
        final_video.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24, threads=4)
        print(f"\n🚀 DONE! Video saved at: {output_file}")
    else:
        print("❌ No clips to assemble.")

if __name__ == "__main__":
    asyncio.run(main())
