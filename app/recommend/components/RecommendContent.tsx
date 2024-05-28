"use client";
// İlk olarak gerekli modülleri ve hookları import ediyoruz
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Song } from "@/types"; // Song tipini varsayılan olarak export ettiğiniz dosya
import MediaItem from "@/components/MediaItem";
import LikeButton from "@/components/LikeButton";
import useOnPlay from "@/hooks/useOnPlay";
import { useUser } from "@/hooks/useUser";
import getRecommendations from "@/actions/getRecommendations";

interface LikedContentProps {
    songs: Song[];
}

const LikedContent: React.FC<LikedContentProps> = ({ songs }) => {
    const router = useRouter();
    const { isLoading, user } = useUser();
    const [recommendations, setRecommendations] = useState<Song[]>([]);

    const onPlay = useOnPlay([...songs, ...recommendations]);

    useEffect(() => {
        const fetchRecommendations = async () => {
            const fetchedRecommendations = await getRecommendations();
            const filteredRecommendations = fetchedRecommendations.filter(rec =>
                !songs.some(song => song.id === rec.id)
            );
            setRecommendations(filteredRecommendations);
        };

        fetchRecommendations();
    }, [songs]);

    useEffect(() => {
        if (!isLoading && !user) {
            router.replace('/');
        }
    }, [isLoading, user, router]);

    if (songs.length === 0 && recommendations.length === 0) {
        return <div className="flex flex-col gap-y-2 w-full px-6 text-neutral-400">No liked songs or recommendations.</div>;
    }

    return (
        <div className="flex flex-col gap-y-2 w-full p-6">
            {songs.concat(recommendations).map((song) => (
                <div key={song.id} className="flex items-center gap-x-4 w-full">
                    <div className="flex-1">
                        <MediaItem onClick={() => onPlay(song.id)} data={song} />
                    </div>
                    {/* <LikeButton songId={song.id} /> */}
                </div>
            ))}
        </div>
    );
}

export default LikedContent;
