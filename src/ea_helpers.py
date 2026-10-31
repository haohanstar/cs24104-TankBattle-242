# -*- coding: utf-8 -*-
"""Enterprise Architect COM 自动化封装。
只使用 EA 17.2 已验证的接口；所有坐标采用 EA 的反向 Y 轴（top/bottom 为负）。
"""
import os
import shutil
import time
import pythoncom
import win32com.client


class ModelBuilder:
    def __init__(self, qea_path, template_path=r"D:\NEWJOB\Environment\EABase.qea", log=None, reset=True):
        self.qea_path = qea_path
        self.log = log or (lambda *a: None)
        os.makedirs(os.path.dirname(qea_path), exist_ok=True)
        if reset:
            if os.path.exists(qea_path):
                os.remove(qea_path)
            shutil.copyfile(template_path, qea_path)
        elif not os.path.exists(qea_path):
            raise RuntimeError("Project not found: %s" % qea_path)
        pythoncom.CoInitialize()
        self.ea = win32com.client.Dispatch("EA.App")
        self.rep = self.ea.Repository
        self.rep.SuppressEADialogs = True
        if not self.rep.OpenFile(qea_path):
            raise RuntimeError("EA OpenFile failed: %s" % qea_path)
        self.pi = self.rep.GetProjectInterface()
        # 激活 DFD MDG
        try:
            self.rep.ActivateTechnology("DFD")
        except Exception as e:
            self.log("ActivateTechnology(DFD) warning:", e)
        self.model = self.rep.Models.GetAt(0)
        self.packages = {}
        self.elements = {}
        self.diagrams = {}
        self._note_seq = 0
        if not reset:
            self._load_existing()
        self.log("EA opened:", qea_path, "version", self.rep.LibraryVersion)

    def _load_existing(self):
        def walk(p):
            try:
                for i in range(p.Packages.Count):
                    sp = p.Packages.GetAt(i)
                    self.packages[sp.Name] = sp
                    walk(sp)
                for i in range(p.Elements.Count):
                    e = p.Elements.GetAt(i)
                    self.elements[e.Name] = e
                for i in range(p.Diagrams.Count):
                    d = p.Diagrams.GetAt(i)
                    self.diagrams[d.Name] = d
            except Exception as e:
                self.log("load warning", e)
        for i in range(self.rep.Models.Count):
            walk(self.rep.Models.GetAt(i))

    def find_pkg(self, name):
        return self.packages.get(name)

    # ---------- packages / elements ----------
    def add_pkg(self, parent, name, key=None, notes=""):
        p = parent.Packages.AddNew(name, "Package")
        p.Update()
        if notes:
            p.Notes = notes
            p.Update()
        if key:
            self.packages[key] = p
        self.log("pkg:", name, p.PackageID)
        return p

    def add_elem(self, pkg, name, typ, stereotype="", notes="", abstract=False, subtype=None,
                 key=None, display_name=None):
        reg_key = key or name
        if reg_key in self.elements and self.elements[reg_key] is not None:
            return self.elements[reg_key]
        e = pkg.Elements.AddNew(display_name or name, typ)
        if stereotype:
            e.Stereotype = stereotype
        if notes:
            e.Notes = notes
        if abstract:
            e.Abstract = True
        if subtype is not None:
            try:
                e.Subtype = subtype
            except Exception as ex:
                self.log("set subtype warning", name, ex)
        e.Update()
        self.elements[reg_key] = e
        return e

    def add_attr(self, elem, display_name, type_name, is_id=False, notes=""):
        # display_name 形如 "customerId {PK}" 或 "customerId: String {PK}"
        name = display_name
        if ": " in name:
            left, right = name.split(": ", 1)
            name = left
            # 取 PK/FK 标记
            marker = ""
            if "{" in right:
                marker = " " + right[right.index("{"):]
            name = name + marker
            type_name = type_name or right.split(" {")[0]
        a = elem.Attributes.AddNew(name, type_name)
        if is_id:
            try:
                a.IsID = True
            except Exception:
                pass
        if notes:
            a.Notes = notes
        a.Update()
        return a

    def add_method(self, elem, name, ret="void", params=None, visibility="public", notes=""):
        mname = name.split("(")[0].strip()
        m = elem.Methods.AddNew(mname, ret or "void")
        m.ReturnType = ret or "void"
        try:
            m.Visibility = visibility
        except Exception:
            pass
        if notes:
            m.Notes = notes
        for pname, ptype in (params or []):
            p = m.Parameters.AddNew(pname, ptype)
            p.Update()
        m.Update()
        return m

    # ---------- diagrams ----------
    def add_diagram(self, pkg, name, typ, stereotype="", notes="", key=None):
        d = pkg.Diagrams.AddNew(name, typ)
        if stereotype:
            d.Stereotype = stereotype
        if notes:
            d.Notes = notes
        d.Update()
        if key:
            self.diagrams[key] = d
        self.diagrams[name] = d
        self.log("diagram:", name, d.DiagramID, typ, stereotype)
        return d

    def place(self, diag, elem, x, y, w, h):
        if isinstance(elem, str):
            elem = self.elements[elem]
        layout = "l=%s;r=%s;t=%s;b=%s;" % (x, x + w, -y, -(y + h))
        o = diag.DiagramObjects.AddNew(layout, "")
        o.ElementID = elem.ElementID
        o.left = x
        o.right = x + w
        o.top = -y
        o.bottom = -(y + h)
        o.Update()
        return o

    def add_note(self, pkg, diag, text, x, y, w, h, name=None):
        self._note_seq += 1
        n = pkg.Elements.AddNew(name or ("Note_%03d" % self._note_seq), "Note")
        n.Notes = text
        n.Update()
        self.place(diag, n, x, y, w, h)
        return n

    # ---------- connectors ----------
    def connect(self, client, supplier, name="", typ="Association", stereotype="", direction="",
                notes="", client_card="", supplier_card="", client_role="", supplier_role="",
                seq_no=None, transition_event="", guard="", action="", subtype="",
                route_style=None, line_color=None):
        if isinstance(client, str):
            client = self.elements[client]
        if isinstance(supplier, str):
            supplier = self.elements[supplier]
        c = client.Connectors.AddNew(name, typ)
        c.ClientID = client.ElementID
        c.SupplierID = supplier.ElementID
        if stereotype:
            c.Stereotype = stereotype
        if direction:
            c.Direction = direction
        if notes:
            c.Notes = notes
        if subtype:
            try:
                c.Subtype = subtype
            except Exception:
                pass
        if client_role:
            c.ClientEnd.Role = client_role
        if supplier_role:
            c.SupplierEnd.Role = supplier_role
        if client_card:
            c.ClientEnd.Cardinality = str(client_card)
        if supplier_card:
            c.SupplierEnd.Cardinality = str(supplier_card)
        if seq_no is not None:
            c.SequenceNo = int(seq_no)
        if transition_event:
            c.TransitionEvent = transition_event
        if guard:
            c.TransitionGuard = guard
        if action:
            c.TransitionAction = action
        if route_style is not None:
            try:
                c.RouteStyle = route_style
            except Exception:
                pass
        if line_color is not None:
            try:
                c.Color = line_color
            except Exception:
                pass
        c.Update()
        return c

    # ---------- export ----------
    def style(self, diag, size=10, font="Microsoft YaHei"):
        """统一放大图内元素字体，提升 PDF 中可读性。"""
        try:
            for i in range(diag.DiagramObjects.Count):
                o = diag.DiagramObjects.GetAt(i)
                try:
                    o.fontName = font
                    o.fontSize = size
                    o.FontBold = 0
                    o.FontItalic = 0
                    o.FontUnderline = 0
                    o.Update()
                except Exception:
                    pass
            diag.Update()
        except Exception as e:
            self.log("style warning", e)

    def set_scale(self, diag, scale=200):
        try:
            diag.Scale = scale
            diag.Update()
        except Exception as e:
            self.log("scale warning", e)

    def export(self, key_or_diag, path):
        d = self.diagrams[key_or_diag] if isinstance(key_or_diag, str) else key_or_diag
        self.pi.PutDiagramImageToFile(d.DiagramGUID, path, 1)
        self.log("export:", d.Name, path, os.path.getsize(path) if os.path.exists(path) else 0)
        return path

    def save(self):
        try:
            self.rep.SaveAllDiagrams()
        except Exception as e:
            self.log("SaveAllDiagrams warning", e)

    def close(self):
        try:
            self.rep.SaveAllDiagrams()
        except Exception:
            pass
        try:
            self.rep.CloseFile()
        except Exception as e:
            self.log("CloseFile warning", e)
        time.sleep(1)
        try:
            self.rep.Exit()
        except Exception as e:
            self.log("Exit warning", e)
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass
