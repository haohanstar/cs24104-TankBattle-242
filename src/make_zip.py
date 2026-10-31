# -*- coding: utf-8 -*-
"""在用户审完 PDF 后，打包实验一源码 zip。

默认不执行；用户确认后运行：python src/make_zip.py
"""
import os
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "cs24104-2024210622-姚帅-坦克大战联机复刻-实验一软件项目计划-源码.zip")

INCLUDE_DIRS = ["docs", "report", "src", "maps"]
SKIP_DIRS = {"__pycache__", ".git", "raw"}
SKIP_SUFFIX = {".log", ".pyc"}
SKIP_FILES = {"test-clean.png", "fig-02-tiled-ui.png"}
EXCLUDE_REL = {
    os.path.join("docs", "个人任务清单.md"),
    os.path.join("docs", "操作步骤.md"),
}


def iter_files():
    for name in ["README.md", ".gitignore"]:
        p = os.path.join(BASE, name)
        if os.path.isfile(p):
            yield p
    for d in INCLUDE_DIRS:
        root = os.path.join(BASE, d)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS]
            for fn in filenames:
                if fn in SKIP_FILES:
                    continue
                if any(fn.endswith(s) for s in SKIP_SUFFIX):
                    continue
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, BASE)
                if rel in EXCLUDE_REL:
                    continue
                # PDF 单独提交，源码 zip 里不再放副本
                if rel.startswith("report" + os.sep) and fn.lower().endswith(".pdf"):
                    continue
                if os.path.isfile(p):
                    yield p
    p = os.path.join(BASE, "model", "TankBattle.qea")
    if os.path.isfile(p):
        yield p


def main():
    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in iter_files():
            rel = os.path.relpath(p, BASE)
            z.write(p, rel)
    print("saved", OUT, os.path.getsize(OUT))
    with zipfile.ZipFile(OUT) as z:
        print("files:", len(z.namelist()))
        for n in z.namelist():
            print(" ", n)


if __name__ == "__main__":
    main()
