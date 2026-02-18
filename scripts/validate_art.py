import sys
from pathlib import Path

ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
BLOCKED_EXTS = ALLOWED_IMAGE_EXTS | {".sgx"}

def fail(msg: str) -> None:
    print(f"❌ VALIDATION FAILED: {msg}")
    sys.exit(1)

def warn(msg: str) -> None:
    print(f"⚠️  {msg}")

def is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except Exception:
        return False

def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    art_dir = repo_root / "art"

    if not art_dir.exists():
        fail("Missing required folder: /art")

    # 1) BLOCK: no .png/.jpg/.jpeg/.sgx anywhere outside /art
    for p in repo_root.rglob("*"):
        if p.is_dir():
            continue

        # Ignore git internals
        if ".git" in p.parts:
            continue

        ext = p.suffix.lower()
        if ext in BLOCKED_EXTS and not is_inside(p, art_dir):
            fail(
                f"Artwork files must be stored ONLY in /art. "
                f"Found '{p.as_posix()}' outside /art."
            )

    # 2) Validate pairs inside /art (PNG/JPG/JPEG + matching SGX)
    found = {}  # base_name -> set(exts)

    for p in art_dir.rglob("*"):
        if p.is_dir():
            continue

        # Allow .gitkeep inside /art
        if p.name == ".gitkeep":
            continue

        ext = p.suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTS and ext != ".sgx":
            fail(f"Invalid file type in /art: {p.name} (allowed: PNG/JPG/JPEG + SGX)")

        base = p.name[: -len(p.suffix)]
        found.setdefault(base, set()).add(ext)

    if not found:
        warn("No artworks found yet in /art (this is OK).")
        print("✅ Validation passed.")
        return

    for base, exts in sorted(found.items()):
        has_sgx = ".sgx" in exts
        img_exts = [e for e in exts if e in ALLOWED_IMAGE_EXTS]

        if not img_exts and has_sgx:
            fail(f"Found '{base}.sgx' but no matching image '{base}.png/.jpg/.jpeg'")

        if img_exts and not has_sgx:
            fail(f"Found image for '{base}' but missing matching '{base}.sgx'")

        if len(img_exts) > 1:
            fail(f"Multiple image files for same base '{base}': {img_exts}. Keep only ONE (PNG OR JPG/JPEG).")

    print("✅ Validation passed.")

if __name__ == "__main__":
    main()
