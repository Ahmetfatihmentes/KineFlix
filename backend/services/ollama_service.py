import json
import logging
import re
from typing import Optional

import httpx

from backend.core.config import get_settings as _get_settings

logger = logging.getLogger(__name__)

OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_HEADERS = {"Accept-Charset": "utf-8"}

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

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


def _build_fallback_reason(
    source_title: str,
    source_genres: str,
    source_content_type: str,
    recommended_title: str,
    recommended_genres: str,
    recommended_content_type: str,
    source_director: str = "",
    recommended_director: str = "",
    source_actors: str = "",
    recommended_actors: str = "",
) -> str:
    src_genres = {g.strip() for g in translate_genres(source_genres).split(",")} if source_genres else set()
    rec_genres = {g.strip() for g in translate_genres(recommended_genres).split(",")} if recommended_genres else set()
    common_genres = src_genres & rec_genres

    parts: list[str] = []
    if common_genres:
        parts.append(f"Her iki yapım da {', '.join(sorted(common_genres))} türünde.")
    elif rec_genres:
        parts.append(f"Benzer yapım tarzına sahip bir {next(iter(rec_genres))} filmi.")

    if (source_director and recommended_director
            and source_director.strip().lower() == recommended_director.strip().lower()):
        parts.append(f"Her iki yapım da {source_director} tarafından yönetilmiştir.")

    if source_actors and recommended_actors:
        src_list = [a.strip() for a in source_actors.split(",")]
        rec_list = [a.strip() for a in recommended_actors.split(",")]
        common_actors = [a for a in src_list if a in rec_list]
        if common_actors:
            parts.append(f"{', '.join(common_actors[:2])} her iki yapımda da yer almaktadır.")

    src_label = "filmini" if (source_content_type or "").lower() == "movie" else "dizisini"
    rec_label = "filmini" if (recommended_content_type or "").lower() == "movie" else "dizisini"
    closing = f"{source_title} {src_label} beğendiysen, {recommended_title} {rec_label} de beğenebilirsin."
    body = " ".join(parts)
    return f"{body} {closing}".strip() if body else closing


def _build_fallback_review(movie_title: str, positive_pct: float | None) -> str | None:
    if positive_pct is None:
        return None
    pct = int(positive_pct)
    if positive_pct >= 80:
        return (
            f"Eleştirmenler {movie_title} filmini büyük çoğunlukla olumlu karşıladı; "
            f"beğeni oranı %{pct} seviyesinde. "
            f"Güçlü anlatımı ve etkileyici performanslarıyla öne çıkıyor. "
            f"Türün hayranlarının kaçırmaması gereken bir yapım."
        )
    if positive_pct >= 55:
        return (
            f"Eleştirmenler {movie_title} için karışık görüşler bildirdi; "
            f"beğeni oranı %{pct}. "
            f"Filmin bazı yönleri takdir görürken bazı eleştirmenler eksiklikler de tespit etti. "
            f"Türü sevenler için ilginç bir seçenek olabilir."
        )
    return (
        f"Eleştirmenler {movie_title} konusunda bölünmüş görüşlere sahip; "
        f"beğeni oranı %{pct} seviyesinde. "
        f"Film bazı izleyicilere hitap edecek özgün unsurlar barındırıyor. "
        f"İzlemeden önce konu özetini incelemeniz önerilir."
    )


async def _call_groq(prompt: str, max_tokens: int = 200) -> str:
    api_key = _get_settings().GROQ_API_KEY
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.3,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def _is_ollama_available() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{_get_settings().OLLAMA_BASE_URL.rstrip('/')}/api/tags")
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
        num_predict = 50
        prompt = f"""Sadece Türkçe yaz. İngilizce kelime kullanma.
{source_movie_title} ({source_genres_tr}) ve {recommended_movie_title} ({recommended_genres_tr}) neden benzer?
1 cümle yaz. Maksimum 15 kelime. Türkçe tür ve tema kelimelerini kullan."""
    else:
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

    # LLM çağrısı: production'da Groq, lokalde Ollama
    settings = _get_settings()
    use_groq = settings.ENVIRONMENT == "production" and bool(settings.GROQ_API_KEY)
    if use_groq:
        try:
            result = await _call_groq(prompt, max_tokens=num_predict * 2)
        except Exception as e:
            logger.error("Groq hatası [%s]: %s", type(e).__name__, e)
            return None
    else:
        if not await _is_ollama_available():
            logger.warning("Ollama kullanılamıyor, kural tabanlı fallback kullanılıyor.")
            return None
        try:
            async with httpx.AsyncClient(
                timeout=float(_get_settings().OLLAMA_TIMEOUT),
                headers=OLLAMA_HEADERS,
            ) as client:
                resp = await client.post(
                    f"{_get_settings().OLLAMA_BASE_URL.rstrip('/')}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_predict": num_predict,
                            "stop": [],
                        },
                    },
                )
                data = _parse_ollama_response(resp)
                result = data.get("response", "").strip()
        except Exception as e:
            logger.error("Ollama hatası [%s]: %s", type(e).__name__, e)
            return None

    # Ortak post-processing
    if short_mode:
        result = apply_tr_fixes(result)
        meta_patterns = [
            r"Cümle\s*\d+\s*[:;]?\s*",
            r"^\d+[\.\)]\s*",
            r"Because\b.*",
        ]
        for pattern in meta_patterns:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE | re.MULTILINE)
        result = " ".join(result.split()).strip()
        return result

    meta_patterns = [
        r"Birinci\s+Cümle[n]?\s*[:;]?\s*",
        r"İkinci\s+Cümle[n]?\s*[:;]?\s*",
        r"Üçüncü\s+Cümle[n]?\s*[:;]?\s*",
        r"Cümle\s*\d+\s*[:;]?\s*",
        r"^\d+[\.\)]\s*",
        r"de ortak tür ve atmosferi anlatırız\s*:?\s*",
        r"de izleyicinin neden sevebileceğini anlatırız\s*:?\s*",
        r"ortak tür ve atmosferi anlatırız\s*:?\s*",
    ]
    for pattern in meta_patterns:
        result = re.sub(pattern, "", result, flags=re.IGNORECASE | re.MULTILINE)

    result = apply_tr_fixes(result)
    result = " ".join(result.split()).strip()
    return _finalize_recommendation_reason(
        result,
        son_cumle,
        source_movie_title,
        recommended_movie_title,
    )


async def generate_review_summary(
    movie_title: str,
    reviews: list[str],
    positive_pct: float = None,
) -> Optional[str]:
    """Film yorumlarından Türkçe genel değerlendirme üretir."""

    if not reviews:
        return _build_fallback_review(movie_title, positive_pct)

    sample_reviews = [r[:200] for r in reviews[:8] if r and len(r) > 20]
    if not sample_reviews:
        return _build_fallback_review(movie_title, positive_pct)

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

    # LLM çağrısı: production'da Groq, lokalde Ollama
    settings = _get_settings()
    use_groq = settings.ENVIRONMENT == "production" and bool(settings.GROQ_API_KEY)
    if use_groq:
        try:
            result = await _call_groq(prompt, max_tokens=200)
        except Exception as e:
            logger.error("Groq yorum özeti hatası [%s]: %s", type(e).__name__, e)
            return _build_fallback_review(movie_title, positive_pct)
    else:
        if not await _is_ollama_available():
            logger.warning("Ollama kullanılamıyor, istatistik tabanlı yorum üretiliyor.")
            return _build_fallback_review(movie_title, positive_pct)
        try:
            async with httpx.AsyncClient(
                timeout=float(_get_settings().OLLAMA_TIMEOUT),
                headers=OLLAMA_HEADERS,
            ) as client:
                resp = await client.post(
                    f"{_get_settings().OLLAMA_BASE_URL.rstrip('/')}/api/generate",
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
        except Exception as e:
            logger.error("Ollama yorum özeti hatası [%s]: %s", type(e).__name__, e)
            return _build_fallback_review(movie_title, positive_pct)

    # Ortak post-processing
    meta_patterns = [
        r"Birinci\s+Cümle[n]?\s*[:;]?\s*",
        r"İkinci\s+Cümle[n]?\s*[:;]?\s*",
        r"Üçüncü\s+Cümle[n]?\s*[:;]?\s*",
        r"Cümle\s*\d+\s*[:;]?\s*",
        r"^\d+[\.\)]\s*",
    ]
    for pattern in meta_patterns:
        result = re.sub(pattern, "", result, flags=re.IGNORECASE | re.MULTILINE)

    result = apply_tr_fixes(result)
    result = " ".join(result.split()).strip()
    return result if result else None


async def analyze_sentiment(text: str) -> str:
    """Kullanıcı yorumunu POSITIVE veya NEGATIVE olarak sınıflandırır."""
    prompt = f"""Bu yorumu analiz et ve sadece "POSITIVE" veya "NEGATIVE" yaz.
Başka hiçbir şey yazma.

Yorum: {text[:500]}"""

    settings = _get_settings()
    use_groq = settings.ENVIRONMENT != "local" and bool(settings.GROQ_API_KEY)
    try:
        result = await _call_groq(prompt, max_tokens=10) if use_groq else await _call_ollama_sentiment(prompt)
    except Exception as e:
        logger.warning("Sentiment analizi başarısız: %s", e)
        return "POSITIVE"

    result = result.strip().upper()
    return "POSITIVE" if "POSITIVE" in result else "NEGATIVE"


async def _call_ollama_sentiment(prompt: str) -> str:
    if not await _is_ollama_available():
        return "POSITIVE"
    async with httpx.AsyncClient(
        timeout=float(_get_settings().OLLAMA_TIMEOUT),
        headers=OLLAMA_HEADERS,
    ) as client:
        resp = await client.post(
            f"{_get_settings().OLLAMA_BASE_URL.rstrip('/')}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 10},
            },
        )
        data = _parse_ollama_response(resp)
        return data.get("response", "POSITIVE").strip()
