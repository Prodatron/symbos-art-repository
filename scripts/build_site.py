import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ART_DIR = REPO_ROOT / "art"
SITE_DIR = REPO_ROOT / "site"
SITE_ART_DIR = SITE_DIR / "art"
GALLERY_JSON = SITE_DIR / "gallery.json"
INDEX_SRC = REPO_ROOT / "index.html"
INDEX_DST = SITE_DIR / "index.html"
IMG_EXTS = {".png", ".jpg", ".jpeg"}
SGX_EXT = ".sgx"

def parse_name(base: str):
    """Convenção: titulo__autor  (dois underscores)"""
    parts = base.split("__", 1)
    title = parts[0].replace("_", " ").replace("-", " ").strip()
    author = parts[1].strip() if len(parts) > 1 else "Unknown"
    return title, author

def main():
    if not ART_DIR.exists():
        raise SystemExit("Missing 'art/' directory.")

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_ART_DIR.mkdir(parents=True, exist_ok=True)

    entries = {}
    for f in ART_DIR.iterdir():
        if f.is_dir():
            continue
        ext = f.suffix.lower()
        if ext in IMG_EXTS or ext == SGX_EXT:
            entries.setdefault(f.stem, {})
            if ext in IMG_EXTS:
                entries[f.stem]["image"] = f
            elif ext == SGX_EXT:
                entries[f.stem]["sgx"] = f

    items = []
    for base, data in entries.items():
        if "image" not in data or "sgx" not in data:
            continue
        img_src = data["image"]
        sgx_src = data["sgx"]
        shutil.copy2(img_src, SITE_ART_DIR / img_src.name)
        shutil.copy2(sgx_src, SITE_ART_DIR / sgx_src.name)
        title, author = parse_name(base)
        items.append({
            "id": base,
            "title": title,
            "author": author,
            "image": f"art/{img_src.name}",
            "sgx": f"art/{sgx_src.name}"
        })

    items.sort(key=lambda x: x["title"].lower())

    with open(GALLERY_JSON, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    shutil.copy2(INDEX_SRC, INDEX_DST)
    print(f"✅ Built gallery with {len(items)} artworks.")

if __name__ == "__main__":
    main()
