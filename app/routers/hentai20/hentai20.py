from typing import Any, Dict, List, Union, Optional
from bs4 import BeautifulSoup
from requests import auth
from app.handlers.api_handler import ApiHandler
from app.resources.errors import CRASH
import requests

api = ApiHandler("https://hentai20.io")


async def get_panels(chapter_id: str) -> Union[Dict[str, Any], int]:
    response: Any = await api.get(endpoint=f"/{chapter_id}", html=True)

    if type(response) is int:
        return CRASH

    soup: BeautifulSoup = get_soup(response)
    chapter_title: str = soup.select(".entry-title")[0].text

    noscript_tag = soup.select_one("#readerarea noscript")
    panels = []

    if noscript_tag:
        raw_html = noscript_tag.decode_contents()
        img_soup = get_soup(raw_html)
        panel_eles = img_soup.find_all("img")

        for panel in panel_eles:
            image_url = panel.get("src")
            if image_url:
                panels.append({"image_url": image_url})

    return {
        "chapter_id": chapter_id,
        "chapter_title": chapter_title,
        "panels": panels,
    }


async def get_manga(manga_id) -> Union[Dict[str, Any], int]:
    response: Any = await api.get(endpoint=f"/manga/{manga_id}", html=True)

    if type(response) is int:
        return CRASH

    soup: BeautifulSoup = get_soup(response)
    image_ele = soup.select(".attachment-.size-.wp-post-image")[0]
    title = image_ele.get("alt")
    image_url = image_ele.get("src")
    description = soup.select(".entry-content.entry-content-single > p")[0].text.strip()
    score = soup.select(".num")[0].text.strip()
    chapter_eles = soup.select(".eph-num > a")

    ticks = {"score": score}
    tick_eles = soup.select(".imptdt")

    for tick in tick_eles:
        tick_type = (
            tick.text.replace("Posted On", "created_at")
            .replace("Updated On", "updated_at")
            .split(" ")[0]
            .lower()
            .strip()
        )

        if tick_type == "type":
            ticks["type"] = tick.select("a")[0].text

        if tick_type in ["updated_at", "created_at", "author"]:
            ticks[tick_type] = tick.select("i")[0].text

    chapters: List[Dict[str, str]] = []

    for i in range(1, len(chapter_eles)):  #! skipping the first element
        chapter_ele = chapter_eles[i]
        href: Any = chapter_ele.get("href")
        name: Any = chapter_ele.select(".chapternum")[0].text
        _date: Any = chapter_ele.select(".chapterdate")[0].text
        chapter_id = href.replace("https://hentai20.io/", "")

        chapters.append(
            {
                "name": name,
                "chapter_id": chapter_id,
                "date": _date,
            }
        )

    return {
        "manga": {
            "manga_id": manga_id,
            "image_url": image_url,
            "title": title,
            **ticks,
            "description": description,
            "chapters": chapters,
        }
    }

async def search_manga(
    query: str,
    params: Dict[str, str], **kwargs
) -> Union[Dict[str, Any], int]:
    page = params.get("page", "1")
    params["s"] = query

    endpoint = f"/page/{page}/"

    response: Any = await api.get(**kwargs, endpoint=endpoint, params=params, html=True)

    if type(response) is int:
        return CRASH

    soup: BeautifulSoup = get_soup(response)
    mangas: List[Dict[str, Any]] = []

    if "Home" in soup.title or soup.select_one(".listupd") is None:
        return {"mangas": [], "message": "Manga page not found"}

    search_container = soup.select_one(".listupd")
    if not search_container:
        return {"mangas": [], "message": "Manga page not found"}

    manga_items = search_container.select(".bs .bsx")

    if not manga_items:
        return {"mangas": [], "message": "Manga page not found"}

    for manga_item in manga_items:
        try:
            link_element = manga_item.select_one("a")
            if not link_element:
                continue

            title = link_element.get("title", "").strip()
            href = link_element.get("href", "")
            manga_id = href.split("/manga/")[1].rstrip("/") if "/manga/" in href else ""

            img_element = manga_item.select_one("img.ts-post-image")
            image_url = img_element.get("src") if img_element else ""

            chapter_element = manga_item.select_one(".epxs")
            latest_chapter = chapter_element.text.strip() if chapter_element else ""

            score_element = manga_item.select_one(".numscore")
            score = score_element.text.strip() if score_element else "0"

            if title and manga_id:
                mangas.append({
                    "title": title,
                    "manga_id": manga_id,
                    "image_url": image_url,
                    "latest_chapter": latest_chapter,
                    "score": score
                })

        except Exception as e:
            print(f"Error parsing manga item: {str(e)}")
            continue

    pagination_info = soup.select_one(".pagination")
    total_pages = 1

    if pagination_info:
        total_pages = len(pagination_info.find_all("a"))

    return {
        "mangas": mangas,
        "pagination": {
            "page": int(page),
            "total_pages": total_pages
        },
    }


async def get_filter_mangas(
    params: Dict[str, str], **kwargs
) -> Union[Dict[str, Any], int]:
    response: Any = await api.get(**kwargs, params=params, html=True)
    page = params["page"]

    if type(response) is int:
        return CRASH

    soup: BeautifulSoup = get_soup(response)
    mangas: List[Dict[str, Any]] = []
    items: List = soup.select(".listupd .bsx > a")

    for manga in items:
        image_url = manga.select("img")[0].get("src")
        title = manga.get("title")
        href_chunks = manga.get("href").split("/")
        chunks_length = len(href_chunks)
        slug = href_chunks[chunks_length - 2]
        colored_ele = manga.select(".colored")
        colored = True if colored_ele else False
        latest_chapter = manga.select(".epxs")[0].text

        mangas.append(
            {
                "title": title,
                "image_url": image_url,
                "colored": colored,
                "slug": slug,
                "latest_chapter": latest_chapter,
            }
        )

    return {
        "mangas": mangas,
        "pagination": {
            "page": page,
        },
    }


def get_soup(html) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def download_image_from_url(image_url: Optional[str]) -> Union[None, bytes]:
    if not image_url:
        return None

    headers = {
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "Referer": "https://chapmanganato.to/",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": '"Linux"',
    }

    try:
        response = requests.get(image_url, headers=headers)
        pass
    except Exception as e:
        print(e)
        return None
    else:
        return response.content
