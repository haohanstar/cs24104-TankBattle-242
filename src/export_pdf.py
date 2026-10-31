# -*- coding: utf-8 -*-
"""用 Word 更新目录/页码并导出 PDF。"""
import os
import traceback
import win32com.client

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX = os.path.join(BASE, "report", "坦克大战实验一报告.docx")
PDF = os.path.join(BASE, "report", "cs24104-2024210622-姚帅-坦克大战联机复刻-实验一软件项目计划.pdf")
LOG = os.path.join(BASE, "report", "export_pdf.log")
logf = open(LOG, "w", encoding="utf-8")


def log(*a):
    print(*a, file=logf, flush=True)


def main():
    word = None
    doc = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        doc = word.Documents.Open(DOCX, ConfirmConversions=False, ReadOnly=False, AddToRecentFiles=False)
        log("opened", DOCX)
        try:
            doc.Fields.Update()
            log("fields updated")
        except Exception as e:
            log("fields warning", e)
        try:
            for i in range(1, doc.TablesOfContents.Count + 1):
                doc.TablesOfContents(i).Update()
            log("toc updated", doc.TablesOfContents.Count)
        except Exception as e:
            log("toc warning", e)
        try:
            doc.Repaginate()
        except Exception as e:
            log("repaginate warning", e)
        try:
            doc.Save()
        except Exception as e:
            log("save warning", e)
        if os.path.exists(PDF):
            os.remove(PDF)
        doc.SaveAs2(PDF, FileFormat=17)
        try:
            pages = doc.ComputeStatistics(2)
        except Exception:
            pages = -1
        log("saved", PDF, os.path.getsize(PDF), "pages", pages)
        doc.Close(False)
        doc = None
        word.Quit()
        word = None
        log("done")
    except Exception:
        log("ERROR")
        log(traceback.format_exc())
        raise
    finally:
        try:
            if doc is not None:
                doc.Close(False)
        except Exception:
            pass
        try:
            if word is not None:
                word.Quit()
        except Exception:
            pass
        logf.close()


if __name__ == "__main__":
    main()
