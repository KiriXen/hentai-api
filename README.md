# Hentai20 API

## Introduction
This is the edited and working version of the [original hentai20 API](https://github.com/thullyDev/hentai20.api), a scraper API for hentai manga content.

## Getting Started
1. `git clone https://github.com/KiriXen/hentai-api.git`
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app`

## Base URL
`http://127.0.0.1:8000` or `http://localhost:8000` 

All endpoints are prefixed with `/hentai`.

## Endpoints

### Proxy Image

- **URL:** `/proxy/{image_url:path}`
- **Method:** GET
- **Description:** Proxy for image requests.
- **Parameters:**
  - `{image_url}` (str): URL of the image to proxy.
- **Response:** Returns the image or an error GIF if the image can't be retrieved.

### Search Manga

- **URL:** `/search?query={query_here}&page={page}`
- **Method:** GET
- **Description:** Allows you to search for manga by title, or keyword.
- **Parameters:**
  - `query` (str): A search string to find manga. It could be the title of the manga, a keyword, or part of the title. The API will return results matching the search query.
  - `page` (str, default="1"): Page number.
- **Response:**
  - **200 OK**: Returns a list of manga that match the search query. Each manga will have details such as title.
  - **404 Not Found**: If no manga is found that matches the query.


### Filter Mangas

- **URL:** `/filter`
- **Method:** GET
- **Query Parameters:**
  - `page` (str, default="1"): Page number.
  - `genre` (str, optional): Genre of the manga.
  - `status` (str, optional): Status of the manga (e.g., ongoing, complete).
  - `_type` (str, optional): Type of manga.
  - `sort` (str, optional): Sorting order.
- **Description:** Get filtered manga results.
- **Response:** Returns filtered manga data.

### Get Manga Details

- **URL:** `/{manga_id}`
- **Method:** GET
- **Description:** Get details of a specific manga.
- **Parameters:**
  - `{manga_id}` (str): Manga ID.
- **Response:** Returns manga details.

### Read Chapter

- **URL:** `/read/{chapter_id}`
- **Method:** GET
- **Description:** Read a chapter of a manga.
- **Parameters:**
  - `{chapter_id}` (str): Chapter ID.
- **Response:** Returns chapter panel data.

## Notes

- Image proxying may be necessary to bypass forbidden responses from the original server.
- The API handles various filtering options for manga, including genre, status, type, and sorting.

---

### Special Thanks
Credits to [**thullyDev**](https://github.com/thullyDev) for the original inspiration behind this project.