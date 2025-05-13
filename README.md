# 📊 YouTube Data Collection using YouTube Data API (v3)

## Overview

This project collects metadata about YouTube videos for various **languages** and **categories** using the **YouTube Data API v3**. It aims to collect up to **1000 hours of video data** per language or category and store the metadata (title, URL, duration, language, etc.) in **Excel files**.

## 🎯 Use Cases

* Gathering linguistic datasets for research
* Creating corpora for low-resource languages (e.g., Arabic, Marathi, Urdu)
* Analyzing video distribution by category and language
* Training ML/NLP models on language-labeled content

---

## 🔧 Setup Instructions

1. **Install Required Libraries**

Make sure you have Python 3.7+ and install the following dependencies:

```bash
pip install pandas google-api-python-client isodate openpyxl
```

2. **Get a YouTube API Key**

* Go to [Google Cloud Console](https://console.cloud.google.com/)
* Create a project and enable the **YouTube Data API v3**
* Generate an **API Key**
* Replace the `API_KEY` variable in each script with your actual key

---

## 📁 Project Files

### 1. `fetch_data.ipynb`

**Purpose**:
Reads existing Excel sheets with YouTube video URLs and appends `defaultLanguage` and `defaultAudioLanguage` to each entry by querying the YouTube API.

**Main Functions**:

* `get_video_languages(video_id)`: Fetches language metadata for a video.
* Loops over multiple Excel files.
* For each video URL:

  * Extracts the video ID from the URL.
  * Calls YouTube API to fetch language information.
* Appends two new columns to each file:

  * `Default Language`
  * `Default Audio Language`

**Input**: List of Excel files (`final_language_videos_*.xlsx`)
**Output**: Updates each Excel file with additional language metadata columns.

---

### 2. `links_category.py`

**Purpose**:
Collects YouTube videos based on **language + content category queries** (e.g., "Arabic movies", "Arabic news") until a total duration of 1000 hours is reached.

**Key Components**:

* `get_youtube_service()`: Authenticates the YouTube Data API.
* `convert_duration_to_hours(duration)`: Converts ISO 8601 durations (e.g., "PT1H23M") to hours.
* `is_similar(title1, title2)`: Prevents duplication using fuzzy title matching.
* `search_videos_by_queries(language_query, queries, max_hours)`: Main logic to fetch video metadata.

  * Combines the language with each category term (e.g., Arabic + songs).
  * Fetches search results page-by-page.
  * Checks language metadata and duration.
  * Avoids duplicate videos using fuzzy matching.
* `save_to_excel_append(...)`: Appends new results to a cumulative Excel sheet (`final_language_videos_unique_1000_hours_v2.xlsx`).

**Output Excel Columns**:

* Title
* URL
* Duration (ISO format)
* Hours
* defaultAudioLanguage
* Category
* Cumulative Hours

---

### 3. `links_channel.py`

**Purpose**:
Fetches videos based on a **language-specific query only** (e.g., just "Arabic") without category distinction, filtering strictly by `defaultAudioLanguage`.

**Differences from `links_category.py`**:

* Does not use category keywords.
* Uses stricter filtering — only includes videos that explicitly list the audio language as the target language (e.g., `"ar"` for Arabic).
* Saves the result into a file named `final_language_videos_unique_1000_hours.xlsx`.

**When to Use**:
When you want to ensure high precision language matching without category noise.

---

### 4. `links_query.py`

**Purpose**:
Very similar to `links_category.py`, this script also fetches videos using language + category queries.

**Difference**:

* This version does **not filter** by `defaultAudioLanguage`, allowing broader coverage.
* Still performs fuzzy deduplication and stops at \~1000 hours of video.

**Ideal Use Case**:
When you want high coverage for a language across content types, regardless of metadata reliability.

---

## 🧠 Design Principles

* **Language-Centric**: Each script is designed to target a specific language (`language_query`) like `"Arabic"` or `"Marathi"`.
* **Deduplication**: Uses `difflib.SequenceMatcher` to avoid collecting similar video titles.
* **Duration Budgeting**: Stops once the total collected video hours cross `max_hours=1000`.
* **Metadata Augmentation**: Adds extra info (e.g., language, category) for deeper analysis.
* **Excel Output**: Stores data in `.xlsx` files using `pandas` and `openpyxl`.

---

## 📝 Output Example (Excel Columns)

| Title           | URL                                                                     | Duration | Hours | defaultAudioLanguage | Category | Cumulative Hours |
| --------------- | ----------------------------------------------------------------------- | -------- | ----- | -------------------- | -------- | ---------------- |
| Arabic Song XYZ | [https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=)... | PT1H2M   | 1.03  | ar                   | songs    | 1.03             |
| Arabic News ABC | [https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=)... | PT30M    | 0.50  | ar                   | news     | 1.53             |
| ...             | ...                                                                     | ...      | ...   | ...                  | ...      | ...              |
| **Total**       |                                                                         |          | 1000  |                      |          | 1000             |

---

## ⚙️ Requirements

* Python 3.7+
* `google-api-python-client`
* `pandas`
* `isodate`
* `openpyxl`

You can install dependencies using:

```bash
pip install google-api-python-client pandas isodate openpyxl
```

---

## 🚀 How to Run

1. **Collect videos for a language and category**:

```bash
python links_category.py
```

2. **Collect videos for a language only**:

```bash
python links_channel.py
```

3. **Collect videos and allow broader language coverage**:

```bash
python links_query.py
```

4. **Update existing Excel files with language metadata**:

Run the Jupyter Notebook `fetch_data.ipynb` and execute all cells.

---

## 🛡️ Notes

* API key quotas may be exceeded if you perform many searches in a day. Consider batching requests and handling quota errors.
* The YouTube API does not guarantee language metadata for every video.
* Fuzzy title matching is heuristic and might miss or overmatch in some cases.

---

Let me know if you want this in PDF, LaTeX, or formatted for a GitHub `README.md` file.
