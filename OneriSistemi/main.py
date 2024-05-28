from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import os
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # .env dosyasındaki değişkenleri yükler

# Ortam değişkenlerini al
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Supabase client'ını oluştur
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Güvenlik için uygun olmayabilir, uygun olanı seçin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/liked_songs")
async def read_root():
    # liked_songs tablosundan tüm song_id'leri çek
    liked_data = supabase.table("liked_songs").select("song_id").execute()
    liked_songs_ids = [item['song_id'] for item in liked_data.data if 'song_id' in item]

    if not liked_songs_ids:
        return {"error": "No liked songs found"}

    # songs tablosundan şarkı bilgilerini al
    songs_data = supabase.table("songs").select("id, title, category").execute()
    songs = songs_data.data

    if not songs:
        return {"error": "No songs found in the database"}

    # liked_songs_id'ler ile eşleşen şarkıların title ve category bilgilerini al
    liked_songs_info = [
        {"title": song["title"], "category": song["category"]}
        for song in songs if song["id"] in liked_songs_ids
    ]

    return {"liked_songs": liked_songs_info}

@app.get("/recommendations/")
async def get_recommendations():
    # liked_songs tablosundan tüm song_id'leri ve kullanıcı bilgilerini çek
    liked_data = supabase.table("liked_songs").select("song_id, user_id").execute()
    liked_songs = liked_data.data

    if not liked_songs:
        return {"error": "No liked songs found"}

    # songs tablosundan şarkı bilgilerini al
    data = supabase.table("songs").select("id, title, category, song_path, image_path, author").execute()
    songs = data.data

    if not songs:
        return {"error": "No songs found in the database"}

    all_recommendations = set()  # Tekrarları önlemek için set kullanıyoruz
    final_recommendations = []  # Önerilen şarkıları tutacak liste

    # Her beğenilen şarkı için önerileri hesapla
    for liked_song in liked_songs:
        song_id = liked_song['song_id']
        song_info = next((song for song in songs if song["id"] == song_id), None)

        if not song_info:
            continue

        # Şarkının kategorisine göre benzer şarkıları bul
        vectorizer = CountVectorizer()
        song_matrix = vectorizer.fit_transform([song["category"] for song in songs])
        liked_vector = vectorizer.transform([song_info["category"]])

        # Beğenilen şarkı ve tüm şarkılar arasında kosinüs benzerliği hesapla
        similarity_scores = cosine_similarity(liked_vector, song_matrix).flatten()

        # Benzerlik puanlarına göre şarkıları öner
        recommended_song_indices = np.argsort(similarity_scores)[::-1]
        recommendations = []
        for idx in recommended_song_indices:
            if songs[idx]["id"] != song_id and similarity_scores[idx] > 0.1:
                recommended_song = songs[idx]
                recommended_title = recommended_song["title"]
                if recommended_title not in all_recommendations:
                    recommendations.append({
                        "id": recommended_song["id"],
                        "title": recommended_song["title"],
                        "song_path": recommended_song["song_path"],
                        "image_path": recommended_song["image_path"],
                        "author": recommended_song["author"]
                    })
                    all_recommendations.add(recommended_title)
                if len(recommendations) == 2:  # Her beğenilen şarkı için en fazla 2 öneri
                    break
        final_recommendations.extend(recommendations)  # Bu beğenilen şarkının önerilerini ekle

    return {"recommendations": final_recommendations}  # Liste olarak dönüş yapıyoruz

# Komut satırında "uvicorn main:app --reload" ile uygulamayı çalıştırabilirsiniz.
