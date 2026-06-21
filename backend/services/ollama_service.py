import json
import logging
import re
from typing import Optional

import httpx


logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_HEADERS = {"Accept-Charset": "utf-8"}

GENRE_MAP = {
    "Action": "Aksiyon",
    "Adventure": "Macera",
    "Animation": "Animasyon",
    "Comedy": "Komedi",
    "Crime": "Suç",
    "Documentary": "Belgesel",
    "Drama": "Dram",
    "Fantasy": "Fantastik",
    "Horror": "Korku",
    "Music": "Müzik",
    "Mystery": "Gizem",
    "Romance": "Romantik",
    "Science Fiction": "Bilim Kurgu",
    "Thriller": "Gerilim",
    "War": "Savaş",
    "Western": "Western",
    "History": "Tarih",
    "Family": "Aile",
    "Biography": "Biyografi",
}


def translate_genres(genres_str: str) -> str:
    if not genres_str:
        return ""
    genres = [g.strip() for g in genres_str.split(",")]
    return ", ".join(GENRE_MAP.get(g, g) for g in genres)


TR_FIXES = {
    "humor": "mizah",
    "humour": "mizah",
    "theme": "tema",
    "themes": "temalar",
    "genre": "tür",
    "genres": "türler",
    "plot": "olay örgüsü",
    "scene": "sahne",
    "scenes": "sahneler",
    "story": "hikaye",
    "character": "karakter",
    "characters": "karakterler",
    "narrative": "anlatı",
    "sequel": "devam filmi",
    "trilogy": "üçleme",
    "screenplay": "senaryo",
    "director": "yönetmen",
    "actor": "oyuncu",
    "actress": "oyuncu",
    "cast": "oyuncu kadrosu",
    "cinematography": "sinematografi",
    "soundtrack": "film müziği",
    "atmosphere": "atmosfer",
    "action": "aksiyon",
    "comedy": "komedi",
    "thriller": "gerilim",
    "drama": "dram",
    "romance": "romantizm",
    "romantic": "romantik",
    "adventure": "macera",
    "fantasy": "fantastik",
    "horror": "korku",
    "mystery": "gizem",
    "animation": "animasyon",
    "documentary": "belgesel",
    "science fiction": "bilim kurgu",
    "sci-fi": "bilim kurgu",
    "humanity": "insanlık",
    "society": "toplum",
    "social": "sosyal",
    "class": "sınıf",
    "family": "aile",
    "emotion": "duygu",
    "emotional": "duygusal",
    "impact": "etki",
    "message": "mesaj",
    "reality": "gerçeklik",
    "complex": "karmaşık",
    "unique": "özgün",
    "powerful": "güçlü",
    "dark": "karanlık",
    "deep": "derin",
    "tension": "gerilim",
    "conflict": "çatışma",
    "journey": "yolculuk",
    "struggle": "mücadele",
    "identity": "kimlik",
    "relationship": "ilişki",
    "friendship": "dostluk",
    "love": "aşk",
    "violence": "şiddet",
    "glamour": "çekicilik",
    "glamorous": "gösterişli",
    "both": "her ikisi de",
    "also": "ayrıca",
    "while": "iken",
    "however": "ancak",
    "therefore": "bu nedenle",
    "furthermore": "bunun yanı sıra",
    "although": "her ne kadar",
    "despite": "rağmen",
    "similar": "benzer",
    "similarly": "benzer şekilde",
    "overall": "genel olarak",
    "especially": "özellikle",
    "particularly": "özellikle",
    "definitely": "kesinlikle",
    "certainly": "elbette",
    "ultimately": "sonuç olarak",
}


def apply_tr_fixes(text: str) -> str:
    result = text
    for en, tr in TR_FIXES.items():
        result = re.sub(rf"\b{re.escape(en)}\b", tr, result, flags=re.IGNORECASE)
    return result


def _finalize_recommendation_reason(
    result: str,
    son_cumle: str,
    source_title: str,
    recommended_title: str,
) -> str:
    """Keep at most two body sentences and always append the exact closing line."""
    result = result.strip()
    if son_cumle in result:
        result = result.replace(son_cumle, "").strip()

    closing_markers = (
        "beğen",
        "deneyebilir",
        "beğenmeye değer",
        "beğeniminizi",
        "takip etmek",
    )
    body_parts: list[str] = []
    for part in re.split(r"(?<=[.!?])\s+", result):
        part = part.strip()
        if not part:
            continue
        lower = part.lower()
        if part.rstrip(".!?") == son_cumle.rstrip(".!?"):
            continue
        if recommended_title.lower() in lower and any(
            marker in lower for marker in closing_markers
        ):
            continue
        if (
            source_title.lower() in lower
            and recommended_title.lower() in lower
            and any(marker in lower for marker in closing_markers)
        ):
            continue
        body_parts.append(part)

    body = " ".join(body_parts[:2]).strip()
    if body and body[-1] not in ".!?":
        body += "."
    return f"{body} {son_cumle}".strip() if body else son_cumle


def _parse_ollama_response(resp: httpx.Response) -> dict:
    resp.raise_for_status()
    return json.loads(resp.content.decode("utf-8"))


async def _is_ollama_available() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(OLLAMA_TAGS_URL)
            return resp.status_code == 200
    except Exception:
        return False


async def generate_recommendation_reason(
    source_movie_title: str,
    source_movie_genres: str,
    source_movie_overview: str,
    recommended_movie_title: str,
    recommended_movie_genres: str,
    recommended_movie_overview: str,
    source_movie_overview_tr: str = "",
    recommended_movie_overview_tr: str = "",
    source_movie_director: str = "",
    source_movie_actors: str = "",
    source_movie_themes: str = "",
    source_movie_score: float | None = None,
    recommended_movie_director: str = "",
    recommended_movie_actors: str = "",
    recommended_movie_themes: str = "",
    recommended_movie_score: float | None = None,
    source_content_type: str = "Movie",
    recommended_content_type: str = "Movie",
    short_mode: bool = False,
) -> Optional[str]:
    """İki film arasındaki benzerlik açıklaması üretir."""

    if not await _is_ollama_available():
        logger.warning("Ollama kullanılamıyor, fallback metne düşülüyor.")
        return None

    source_overview = source_movie_overview_tr or source_movie_overview
    recommended_overview = recommended_movie_overview_tr or recommended_movie_overview

    source_genres_tr = translate_genres(source_movie_genres)
    recommended_genres_tr = translate_genres(recommended_movie_genres)

    same_director = (
        source_movie_director
        and recommended_movie_director
        and source_movie_director.strip().lower() == recommended_movie_director.strip().lower()
    )

    common_actors: list[str] = []
    if source_movie_actors and recommended_movie_actors:
        source_list = [a.strip() for a in source_movie_actors.split(",")]
        recommended_list = [a.strip() for a in recommended_movie_actors.split(",")]
        common_actors = [a for a in source_list if a in recommended_list]

    extra_info = ""
    if same_director:
        extra_info += f"Her iki film de {source_movie_director} tarafından yönetilmiştir. "
    if common_actors:
        extra_info += f"Her iki filmde de {', '.join(common_actors[:2])} oynamaktadır. "
    if source_movie_score and recommended_movie_score:
        extra_info += "Her iki film de izleyiciler tarafından yüksek puan almıştır. "

    source_label = (
        "filmini" if (source_content_type or "").strip().lower() == "movie" else "dizisini"
    )
    recommended_label = (
        "filmini"
        if (recommended_content_type or "").strip().lower() == "movie"
        else "dizisini"
    )
    son_cumle = (
        f"{source_movie_title} {source_label} beğendiysen, "
        f"{recommended_movie_title} {recommended_label} de beğenebilirsin."
    )

    if short_mode:
        temperature = 0.1
        num_predict = 30
        prompt = f"""Türkçe yaz. İngilizce kelime kullanma.
{source_movie_title} ve {recommended_movie_title} neden benzer?
Maksimum 10 kelime yaz."""
        stop_sequences: list[str] = []
    else:
        temperature = 0.1
        num_predict = 120
        prompt = f"""Türkçe yaz. Kısa cümleler kur. İngilizce kelime kullanma.

{source_movie_title} türü: {source_genres_tr}
{recommended_movie_title} türü: {recommended_genres_tr}

Bu iki içeriği seven birine diğerini neden önereceksin?
Tam 2 cümle yaz:
Birinci cümlede ortak tür veya atmosferi anlat.
İkinci cümlede izleyicinin neden sevebileceğini anlat.
Kapanış cümlesi yazma, öneri cümlesi yazma, soru sorma.
Sadece bu 2 cümleyi yaz."""
        stop_sequences = []

    try:
        async with httpx.AsyncClient(timeout=60.0, headers=OLLAMA_HEADERS) as client:
            resp = await client.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": num_predict,
                        "stop": stop_sequences,
                    },
                },
            )
            data = _parse_ollama_response(resp)
            result = data.get("response", "").strip()

            if short_mode:
                return apply_tr_fixes(result)

            meta_patterns = [
                r"Kelimesi kelimesine\s*:?\s*",
                r"İki içeriğin ortak türünü veya atmosferini anlat\s*:?\s*",
                r"İzleyicinin neden bu içeriği sevebileceğini anlat\s*:?\s*",
                r"İzleyicinin neden sevebileceğini anlat\s*:?\s*",
                r"anlat\s*:\s*",
                r"dizisindeki\s*",
                r"Cümle\s*\d+\s*:?\s*",
                r"^\d+[\.\)]\s*",
                r"^-\s*",
            ]
            for pattern in meta_patterns:
                result = re.sub(
                    pattern, "", result, flags=re.IGNORECASE | re.MULTILINE
                )

            result = apply_tr_fixes(result)
            result = " ".join(result.split())
            return _finalize_recommendation_reason(
                result,
                son_cumle,
                source_movie_title,
                recommended_movie_title,
            )
    except Exception as e:
        logger.error("Ollama hatası: %s", e)
        return None


async def generate_review_summary(
    movie_title: str,
    reviews: list[str],
    positive_pct: float = None,
) -> Optional[str]:
    """Film yorumlarından Türkçe genel değerlendirme üretir."""

    if not reviews:
        return None

    sample_reviews = [r[:200] for r in reviews[:8] if r and len(r) > 20]
    if not sample_reviews:
        return None

    reviews_text = "\n".join([f"- {r}" for r in sample_reviews])
    pct_text = (
        f"Eleştirmenlerin %{positive_pct:.0f}'i filmi olumlu değerlendirdi."
        if positive_pct
        else ""
    )

    prompt = f"""Sen bir film eleştirmenisin. Sadece Türkçe yaz. İngilizce kelime kullanma.

Film: {movie_title}
{pct_text}

Eleştirmen yorumları (İngilizce):
{reviews_text}

Bu yorumları analiz et ve Türkçe olarak 3 kısa cümle yaz:
1. cümle: Eleştirmenlerin genel kanaati nedir?
2. cümle: Filmin en çok övülen veya eleştirilen yönü nedir?
3. cümle: Bu filmi kim izlemeli?

Sadece 3 cümle yaz. Meta veri ekleme."""

    try:
        async with httpx.AsyncClient(timeout=60.0, headers=OLLAMA_HEADERS) as client:
            resp = await client.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 150,
                    },
                },
            )
            data = _parse_ollama_response(resp)
            result = data.get("response", "").strip()

            result = re.sub(r"^\d+[\.\)]\s*", "", result, flags=re.MULTILINE)
            result = " ".join(result.split())
            result = apply_tr_fixes(result)

            return result if result else None
    except Exception as e:
        logger.error("Ollama yorum özeti hatası: %s", e)
        return None
