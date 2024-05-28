// Gelen JSON verisini tanımlayan interface
// interface ApiResponse {
//     recommendations: string[];
//   }
  
  // Gelen JSON verisini tanımlayan interface
// src/types/Song.ts içinde tanımlanan Song tipi
interface Song {
    id: string;
    title: string;
    author: string;
    user_id: string;
    song_path: string;
    image_path: string;
    category: string;
}

// Gelen JSON verisini tanımlayan ApiResponse interface'i
interface ApiResponse {
    recommendations: Song[];  // API'den tam Song objeleri döndüğünü varsayıyoruz
}

// Önerilen şarkıları çeken fonksiyon
const getRecommendations = async (): Promise<Song[]> => {
    const response = await fetch('http://127.0.0.1:8000/recommendations/');
    const data: ApiResponse = await response.json();
    return data.recommendations;  // Artık doğrudan Song[] döndürebiliriz
}

export default getRecommendations;
  