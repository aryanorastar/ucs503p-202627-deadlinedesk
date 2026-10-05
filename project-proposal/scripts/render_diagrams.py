#!/usr/bin/env python3
"""Author and export the canonical DeadlineDesk diagrams.

The ``build_*`` functions describe each diagram once.  ``write_drawio`` writes
that description out as an editable draw.io (mxGraphModel) file, and
``render_pdf`` *re-parses the file that was just written* to produce the PDF
export.  The PNG is rasterised from that PDF.  Because every export is derived
from the ``.drawio`` source, the editable file and the submitted figures can
never drift apart.

Usage:  python3 project-proposal/scripts/render_diagrams.py
"""

from __future__ import annotations

import math
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas as rl_canvas

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"

# --------------------------------------------------------------------------
# Shared visual language
# --------------------------------------------------------------------------
INK = "#1A2B47"          # primary text and heavy strokes
MUTED = "#5B6779"        # subtitles, legends, column headers
LINE = "#44536B"         # connectors
WHITE = "#FFFFFF"

ACTOR_FILLS = {
    "student": ("#E7EFFA", "#2E5C9A"),
    "staff": ("#E6F1EA", "#2F7A52"),
    "admin": ("#FBEEE0", "#B5741F"),
}
ENTITY = ("#EDF1F7", "#5B6779")
PROCESS = ("#FFF3E2", "#C07A16")
STORE = ("#E8F1EC", "#2F7A52")

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

F_TITLE = 26
F_SUBTITLE = 15
F_HEADER = 17
F_NODE = 18
F_EDGE = 16
F_LEGEND = 14

LEADING = 1.28
ARROW_LEN = 11.0
ARROW_HALF = 4.4


# --------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------
@dataclass
class Node:
    id: str
    x: float
    y: float
    w: float
    h: float
    label: str = ""
    style: str = ""

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


@dataclass
class Edge:
    id: str
    source: str
    target: str
    exit: tuple[float, float]
    entry: tuple[float, float]
    label: str = ""
    label_offset: tuple[float, float] = (0.0, 0.0)
    points: list[tuple[float, float]] = field(default_factory=list)
    style: str = ""


@dataclass
class Diagram:
    name: str
    filename: str
    width: float
    height: float
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)


# --------------------------------------------------------------------------
# Text helpers (shared by the builder and the renderer so that the draw.io
# label breaks and the PDF label breaks are identical)
# --------------------------------------------------------------------------
def text_width(text: str, font: str, size: float) -> float:
    return pdfmetrics.stringWidth(text, font, size)


def wrap(text: str, max_width: float, size: float = F_NODE, bold: bool = False) -> str:
    """Greedy word wrap; returns a string with embedded newlines."""
    font = FONT_BOLD if bold else FONT
    out_lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if not current or text_width(trial, font, size) <= max_width:
                current = trial
            else:
                out_lines.append(current)
                current = word
        out_lines.append(current)
    return "\n".join(out_lines)


def block_size(label: str, size: float, bold: bool = False) -> tuple[float, float]:
    font = FONT_BOLD if bold else FONT
    lines = label.split("\n")
    width = max((text_width(line, font, size) for line in lines), default=0.0)
    return width, len(lines) * size * LEADING


# --------------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------------
def rel(node: Node, px: float, py: float) -> tuple[float, float]:
    return ((px - node.x) / node.w, (py - node.y) / node.h)


def ellipse_point_towards(node: Node, tx: float, ty: float) -> tuple[float, float]:
    dx, dy = tx - node.cx, ty - node.cy
    a, b = node.w / 2, node.h / 2
    scale = 1.0 / math.sqrt((dx / a) ** 2 + (dy / b) ** 2)
    return (node.cx + dx * scale, node.cy + dy * scale)


def ellipse_x_at_y(node: Node, y: float, left: bool) -> float:
    a, b = node.w / 2, node.h / 2
    dy = min(abs(y - node.cy), b)
    dx = a * math.sqrt(max(0.0, 1.0 - (dy / b) ** 2))
    return node.cx - dx if left else node.cx + dx


def ellipse_y_at_x(node: Node, x: float, top: bool) -> float:
    a, b = node.w / 2, node.h / 2
    dx = min(abs(x - node.cx), a)
    dy = b * math.sqrt(max(0.0, 1.0 - (dx / a) ** 2))
    return node.cy - dy if top else node.cy + dy


# --------------------------------------------------------------------------
# Style builders
# --------------------------------------------------------------------------
def box_style(fill: str, stroke: str, size: float = F_NODE, bold: bool = False, rounded: bool = True) -> str:
    return (
        f"rounded={1 if rounded else 0};whiteSpace=wrap;html=1;arcSize=8;"
        f"fillColor={fill};strokeColor={stroke};strokeWidth=1.6;"
        f"fontColor={INK};fontSize={size};fontStyle={1 if bold else 0};"
        f"fontFamily=Helvetica;verticalAlign=middle;align=center;"
    )


def ellipse_style(fill: str, stroke: str, size: float = F_NODE, bold: bool = False) -> str:
    return (
        f"ellipse;whiteSpace=wrap;html=1;"
        f"fillColor={fill};strokeColor={stroke};strokeWidth=1.6;"
        f"fontColor={INK};fontSize={size};fontStyle={1 if bold else 0};"
        f"fontFamily=Helvetica;verticalAlign=middle;align=center;"
    )


def store_style(size: float = F_NODE) -> str:
    fill, stroke = STORE
    return (
        f"shape=partialRectangle;whiteSpace=wrap;html=1;top=1;bottom=1;left=1;right=0;"
        f"fillColor={fill};strokeColor={stroke};strokeWidth=1.6;"
        f"fontColor={INK};fontSize={size};fontStyle=0;"
        f"fontFamily=Helvetica;verticalAlign=middle;align=center;"
    )


def actor_style(size: float = F_NODE) -> str:
    return (
        f"shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
        f"outlineConnect=0;fillColor={INK};strokeColor={INK};strokeWidth=1.6;"
        f"fontColor={INK};fontSize={size};fontStyle=1;fontFamily=Helvetica;align=center;"
    )


def text_style(size: float, color: str = INK, bold: bool = False, align: str = "center") -> str:
    return (
        f"text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;"
        f"fontColor={color};fontSize={size};fontStyle={1 if bold else 0};"
        f"fontFamily=Helvetica;align={align};verticalAlign=middle;"
    )


def edge_style(exit_pt: tuple[float, float], entry_pt: tuple[float, float], arrow: str = "block") -> str:
    return (
        f"edgeStyle=none;rounded=0;html=1;"
        f"exitX={exit_pt[0]:.4f};exitY={exit_pt[1]:.4f};exitDx=0;exitDy=0;exitPerimeter=0;"
        f"entryX={entry_pt[0]:.4f};entryY={entry_pt[1]:.4f};entryDx=0;entryDy=0;entryPerimeter=0;"
        f"strokeColor={LINE};strokeWidth=1.4;endArrow={arrow};endFill=1;endSize=7;startArrow=none;"
        f"fontColor={MUTED};fontSize={F_EDGE};fontFamily=Helvetica;"
    )


# --------------------------------------------------------------------------
# draw.io serialisation
# --------------------------------------------------------------------------
def _value(label: str) -> str:
    return escape(label.replace("\n", "<br>"), quote=True)


def write_drawio(diagram: Diagram, path: Path) -> None:
    cells: list[str] = []
    for node in diagram.nodes:
        cells.append(
            f'<mxCell id="{node.id}" value="{_value(node.label)}" style="{node.style}" '
            f'vertex="1" parent="1">'
            f'<mxGeometry x="{node.x:g}" y="{node.y:g}" width="{node.w:g}" height="{node.h:g}" as="geometry"/>'
            f"</mxCell>"
        )
    for edge in diagram.edges:
        geometry = '<mxGeometry relative="1" as="geometry">'
        if edge.points:
            geometry += '<Array as="points">'
            geometry += "".join(f'<mxPoint x="{px:g}" y="{py:g}"/>' for px, py in edge.points)
            geometry += "</Array>"
        geometry += "</mxGeometry>"
        cells.append(
            f'<mxCell id="{edge.id}" style="{edge.style}" edge="1" parent="1" '
            f'source="{edge.source}" target="{edge.target}">{geometry}</mxCell>'
        )
        if edge.label:
            ox, oy = edge.label_offset
            cells.append(
                f'<mxCell id="{edge.id}-label" value="{_value(edge.label)}" '
                f'style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;'
                f'fontColor={MUTED};fontSize={F_EDGE};fontFamily=Helvetica;'
                f'labelBackgroundColor={WHITE};" vertex="1" connectable="0" parent="{edge.id}">'
                f'<mxGeometry x="0" relative="1" as="geometry">'
                f'<mxPoint x="{ox:g}" y="{oy:g}" as="offset"/></mxGeometry></mxCell>'
            )
    body = "".join(cells)
    xml = (
        '<mxfile host="app.diagrams.net" agent="DeadlineDesk render_diagrams.py" type="device">'
        f'<diagram name="{escape(diagram.name, quote=True)}" id="{diagram.filename}">'
        f'<mxGraphModel dx="{diagram.width:g}" dy="{diagram.height:g}" grid="1" gridSize="10" '
        f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        f'pageWidth="{diagram.width:g}" pageHeight="{diagram.height:g}" math="0" shadow="0" '
        f'background="{WHITE}">'
        f"<root><mxCell id=\"0\"/><mxCell id=\"1\" parent=\"0\"/>{body}</root>"
        "</mxGraphModel></diagram></mxfile>"
    )
    path.write_text(xml + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# draw.io -> PDF renderer
# --------------------------------------------------------------------------
def parse_style(style: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for token in style.split(";"):
        token = token.strip()
        if not token:
            continue
        if "=" in token:
            key, _, value = token.partition("=")
            out[key.strip()] = value.strip()
        else:
            out[token] = "1"
    return out


class Renderer:
    def __init__(self, canvas: rl_canvas.Canvas, height: float) -> None:
        self.c = canvas
        self.height = height

    def fy(self, y: float) -> float:
        """draw.io y (downwards) -> PDF y (upwards)."""
        return self.height - y

    # -- primitives ------------------------------------------------------
    def draw_text_block(self, label: str, cx: float, cy: float, size: float,
                        color: str, bold: bool, align: str = "center") -> None:
        if not label:
            return
        font = FONT_BOLD if bold else FONT
        lines = label.split("\n")
        leading = size * LEADING
        self.c.setFillColor(colors.HexColor(color))
        self.c.setFont(font, size)
        top = cy - (len(lines) - 1) * leading / 2
        for index, line in enumerate(lines):
            y = self.fy(top + index * leading) - size * 0.35
            if align == "center":
                self.c.drawCentredString(cx, y, line)
            elif align == "left":
                self.c.drawString(cx, y, line)
            else:
                self.c.drawRightString(cx, y, line)

    def draw_node(self, node: Node) -> None:
        st = parse_style(node.style)
        size = float(st.get("fontSize", F_NODE))
        bold = st.get("fontStyle", "0") in {"1", "3"}
        font_color = st.get("fontColor", INK)
        fill = st.get("fillColor", "none")
        stroke = st.get("strokeColor", "none")
        width = float(st.get("strokeWidth", 1.0))
        shape = st.get("shape", "")

        if fill not in ("none", ""):
            self.c.setFillColor(colors.HexColor(fill))
        if stroke not in ("none", ""):
            self.c.setStrokeColor(colors.HexColor(stroke))
            self.c.setLineWidth(width)
        do_fill = 1 if fill not in ("none", "") else 0
        do_stroke = 1 if stroke not in ("none", "") else 0

        x0, y0 = node.x, self.fy(node.y + node.h)

        if "ellipse" in st:
            self.c.ellipse(node.x, self.fy(node.y + node.h), node.x + node.w,
                           self.fy(node.y), fill=do_fill, stroke=do_stroke)
        elif st.get("rhombus") == "1":
            path = self.c.beginPath()
            path.moveTo(node.cx, self.fy(node.y))
            path.lineTo(node.x + node.w, self.fy(node.cy))
            path.lineTo(node.cx, self.fy(node.y + node.h))
            path.lineTo(node.x, self.fy(node.cy))
            path.close()
            self.c.drawPath(path, fill=do_fill, stroke=do_stroke)
        elif shape == "umlActor":
            self.draw_actor(node, stroke if do_stroke else INK)
        elif shape == "partialRectangle":
            if do_fill:
                self.c.rect(x0, y0, node.w, node.h, fill=1, stroke=0)
            if do_stroke:
                self.c.setLineCap(0)
                if st.get("top", "0") == "1":
                    self.c.line(node.x, self.fy(node.y), node.x + node.w, self.fy(node.y))
                if st.get("bottom", "0") == "1":
                    self.c.line(node.x, self.fy(node.y + node.h), node.x + node.w, self.fy(node.y + node.h))
                if st.get("left", "0") == "1":
                    self.c.line(node.x, self.fy(node.y), node.x, self.fy(node.y + node.h))
                if st.get("right", "0") == "1":
                    self.c.line(node.x + node.w, self.fy(node.y), node.x + node.w, self.fy(node.y + node.h))
        elif "text" in st:
            pass
        else:
            radius = float(st.get("arcSize", 0)) if st.get("rounded", "0") == "1" else 0
            if radius:
                self.c.roundRect(x0, y0, node.w, node.h, radius, fill=do_fill, stroke=do_stroke)
            else:
                self.c.rect(x0, y0, node.w, node.h, fill=do_fill, stroke=do_stroke)

        align = st.get("align", "center")
        if shape == "umlActor":
            label_w, label_h = block_size(node.label, size, bold)
            self.draw_text_block(node.label, node.cx, node.y + node.h + 8 + label_h / 2,
                                 size, font_color, bold, "center")
        elif "text" in st:
            anchor = {"center": node.cx, "left": node.x, "right": node.x + node.w}[align]
            self.draw_text_block(node.label, anchor, node.cy, size, font_color, bold, align)
        else:
            self.draw_text_block(node.label, node.cx, node.cy, size, font_color, bold, "center")

    def draw_actor(self, node: Node, color: str) -> None:
        """Stick figure inscribed in the node bounding box (draw.io umlActor)."""
        self.c.setStrokeColor(colors.HexColor(color))
        self.c.setFillColor(colors.HexColor(color))
        self.c.setLineWidth(2.0)
        self.c.setLineCap(1)
        cx = node.cx
        head_r = node.w * 0.21
        head_cy = node.y + head_r
        torso_top = node.y + 2 * head_r
        torso_bottom = node.y + node.h * 0.62
        self.c.circle(cx, self.fy(head_cy), head_r, fill=1, stroke=0)
        self.c.line(cx, self.fy(torso_top), cx, self.fy(torso_bottom))
        arm_y = node.y + node.h * 0.36
        self.c.line(cx - node.w * 0.44, self.fy(arm_y), cx + node.w * 0.44, self.fy(arm_y))
        self.c.line(cx, self.fy(torso_bottom), cx - node.w * 0.38, self.fy(node.y + node.h))
        self.c.line(cx, self.fy(torso_bottom), cx + node.w * 0.38, self.fy(node.y + node.h))
        self.c.setLineCap(0)

    def draw_edge(self, points: list[tuple[float, float]], st: dict[str, str]) -> None:
        stroke = st.get("strokeColor", LINE)
        self.c.setStrokeColor(colors.HexColor(stroke))
        self.c.setFillColor(colors.HexColor(stroke))
        self.c.setLineWidth(float(st.get("strokeWidth", 1.4)))
        self.c.setLineCap(0)
        path = self.c.beginPath()
        end = points[-1]
        if st.get("endArrow", "none") != "none":
            px, py = points[-2]
            dx, dy = end[0] - px, end[1] - py
            length = math.hypot(dx, dy) or 1.0
            ux, uy = dx / length, dy / length
            end = (end[0] - ux * ARROW_LEN * 0.92, end[1] - uy * ARROW_LEN * 0.92)
        path.moveTo(points[0][0], self.fy(points[0][1]))
        for px, py in points[1:-1]:
            path.lineTo(px, self.fy(py))
        path.lineTo(end[0], self.fy(end[1]))
        self.c.drawPath(path, stroke=1, fill=0)
        if st.get("endArrow", "none") != "none":
            self.draw_arrow_head(points[-2], points[-1], stroke)

    def draw_arrow_head(self, frm: tuple[float, float], to: tuple[float, float], color: str) -> None:
        dx, dy = to[0] - frm[0], to[1] - frm[1]
        length = math.hypot(dx, dy) or 1.0
        ux, uy = dx / length, dy / length
        nx, ny = -uy, ux
        bx, by = to[0] - ux * ARROW_LEN, to[1] - uy * ARROW_LEN
        self.c.setFillColor(colors.HexColor(color))
        path = self.c.beginPath()
        path.moveTo(to[0], self.fy(to[1]))
        path.lineTo(bx + nx * ARROW_HALF, self.fy(by + ny * ARROW_HALF))
        path.lineTo(bx - nx * ARROW_HALF, self.fy(by - ny * ARROW_HALF))
        path.close()
        self.c.drawPath(path, stroke=0, fill=1)


def polyline_midpoint(points: list[tuple[float, float]]) -> tuple[float, float]:
    segments = [
        (points[i], points[i + 1], math.dist(points[i], points[i + 1]))
        for i in range(len(points) - 1)
    ]
    total = sum(seg[2] for seg in segments)
    target = total / 2
    walked = 0.0
    for (ax, ay), (bx, by), length in segments:
        if walked + length >= target:
            t = (target - walked) / (length or 1.0)
            return (ax + (bx - ax) * t, ay + (by - ay) * t)
        walked += length
    return points[-1]


def render_pdf(drawio_path: Path, pdf_path: Path) -> None:
    """Render a .drawio file written by this script into a one-page PDF."""
    tree = ET.parse(drawio_path)
    model = tree.find(".//mxGraphModel")
    assert model is not None
    width = float(model.get("pageWidth", "900"))
    height = float(model.get("pageHeight", "600"))
    root = model.find("root")
    assert root is not None

    geometry: dict[str, Node] = {}
    vertices: list[Node] = []
    edges: list[ET.Element] = []
    labels: dict[str, ET.Element] = {}

    for cell in root.findall("mxCell"):
        cell_id = cell.get("id", "")
        style = cell.get("style", "") or ""
        geom = cell.find("mxGeometry")
        if cell.get("vertex") == "1" and "edgeLabel" not in style:
            node = Node(
                id=cell_id,
                x=float(geom.get("x", "0")),
                y=float(geom.get("y", "0")),
                w=float(geom.get("width", "0")),
                h=float(geom.get("height", "0")),
                label=(cell.get("value", "") or "").replace("<br>", "\n"),
                style=style,
            )
            geometry[cell_id] = node
            vertices.append(node)
        elif cell.get("edge") == "1":
            edges.append(cell)
        elif "edgeLabel" in style:
            labels[cell.get("parent", "")] = cell

    canvas = rl_canvas.Canvas(str(pdf_path), pagesize=(width, height))
    canvas.setTitle(drawio_path.stem)
    renderer = Renderer(canvas, height)

    canvas.setFillColor(colors.HexColor(model.get("background", WHITE)))
    canvas.rect(0, 0, width, height, fill=1, stroke=0)

    for node in vertices:
        renderer.draw_node(node)

    for cell in edges:
        st = parse_style(cell.get("style", "") or "")
        src = geometry[cell.get("source", "")]
        dst = geometry[cell.get("target", "")]
        start = (src.x + float(st["exitX"]) * src.w, src.y + float(st["exitY"]) * src.h)
        finish = (dst.x + float(st["entryX"]) * dst.w, dst.y + float(st["entryY"]) * dst.h)
        waypoints: list[tuple[float, float]] = []
        geom = cell.find("mxGeometry")
        array = geom.find("Array") if geom is not None else None
        if array is not None:
            waypoints = [(float(p.get("x")), float(p.get("y"))) for p in array.findall("mxPoint")]
        points = [start, *waypoints, finish]
        renderer.draw_edge(points, st)

        label_cell = labels.get(cell.get("id", ""))
        if label_cell is None:
            continue
        label_geom = label_cell.find("mxGeometry")
        offset = label_geom.find("mxPoint") if label_geom is not None else None
        ox = float(offset.get("x", "0")) if offset is not None else 0.0
        oy = float(offset.get("y", "0")) if offset is not None else 0.0
        mid = polyline_midpoint(points)
        label_style = parse_style(label_cell.get("style", "") or "")
        size = float(label_style.get("fontSize", F_EDGE))
        text = (label_cell.get("value", "") or "").replace("<br>", "\n")
        bg = label_style.get("labelBackgroundColor", "none")
        if bg not in ("none", ""):
            bw, bh = block_size(text, size)
            canvas.setFillColor(colors.HexColor(bg))
            canvas.rect(mid[0] + ox - bw / 2 - 3, renderer.fy(mid[1] + oy + bh / 2),
                        bw + 6, bh, fill=1, stroke=0)
        renderer.draw_text_block(text, mid[0] + ox, mid[1] + oy, size,
                                 label_style.get("fontColor", MUTED), False, "center")

    canvas.showPage()
    canvas.save()


def render_png(pdf_path: Path, png_path: Path, dpi: int = 200) -> None:
    if shutil.which("pdftoppm"):
        subprocess.run(
            ["pdftoppm", "-r", str(dpi), "-png", "-singlefile", str(pdf_path), str(png_path.with_suffix(""))],
            check=True,
        )
        return
    if shutil.which("gs"):
        subprocess.run(
            ["gs", "-dBATCH", "-dNOPAUSE", "-sDEVICE=png16m", f"-r{dpi}",
             "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4",
             f"-sOutputFile={png_path}", str(pdf_path)],
            check=True,
        )
        return
    raise SystemExit("Need pdftoppm (poppler) or gs (ghostscript) to rasterise the PNG exports.")


# --------------------------------------------------------------------------
# Diagram 1: use-case diagram
# --------------------------------------------------------------------------
USE_CASE_COLUMN = 240.0
USE_CASE_ROW_Y = [150.0, 255.0, 360.0, 465.0, 570.0, 675.0]
UC_WRAP = 0.74 * USE_CASE_COLUMN

STUDENT_CASES = [
    "View placement rounds",
    "Complete document checklist",
    "View readiness result",
    "View assignments",
    "Upload submission",
    "View late decision, grade and feedback",
]
STAFF_CASES = [
    "Publish assignment and late policy",
    "Review submission",
    "Grade submission and feedback",
]
ADMIN_CASES = [
    "Create company and placement round",
    "Add required checklist items",
    "Publish round and log T-24h reminder",
]


def ellipse_side_point(node: Node, from_left: bool, actor_y: float) -> tuple[float, float]:
    """Attachment point on the side of an oval facing the actor.

    The point is pulled slightly towards the actor so the association arrives at
    a natural angle, but it stays on the near side of the oval so the line never
    passes through a neighbouring use case.
    """
    a, b = node.w / 2, node.h / 2
    delta = actor_y - node.cy
    lean = 0.0 if abs(delta) < 1.0 else math.copysign(0.45 * b, delta)
    dxu = -a if from_left else a
    scale = 1.0 / math.sqrt((dxu / a) ** 2 + (lean / b) ** 2)
    return (node.cx + dxu * scale, node.cy + lean * scale)


def build_use_case() -> Diagram:
    diagram = Diagram("Use-Case Diagram", "use-case-diagram", 1000, 800)
    add = diagram.nodes.append

    add(Node("title", 200, 18, 600, 32, "DeadlineDesk Use-Case Diagram",
             text_style(F_TITLE, INK, bold=True)))
    add(Node("subtitle", 200, 48, 600, 22, "UCS503P project proposal - Week 7 prototype scope",
             text_style(F_SUBTITLE, MUTED)))

    add(Node("boundary", 170, 78, 610, 654, "", box_style(WHITE, INK, rounded=False)))
    add(Node("boundary-label", 275, 88, 400, 22, "DeadlineDesk",
             text_style(F_HEADER, INK, bold=True)))

    ovals: dict[str, Node] = {}

    def add_cases(prefix: str, cases: list[str], rows: list[float], x: float, key: str) -> None:
        fill, stroke = ACTOR_FILLS[key]
        for index, (label, y) in enumerate(zip(cases, rows)):
            node = Node(f"{prefix}{index}", x, y - 42, USE_CASE_COLUMN, 84,
                        wrap(label, UC_WRAP), ellipse_style(fill, stroke))
            ovals[node.id] = node
            add(node)

    add_cases("uc-s", STUDENT_CASES, USE_CASE_ROW_Y, 192, "student")
    add_cases("uc-t", STAFF_CASES, USE_CASE_ROW_Y[:3], 518, "staff")
    add_cases("uc-a", ADMIN_CASES, USE_CASE_ROW_Y[3:], 518, "admin")

    for node in (
        Node("actor-student", 50, 362, 76, 100, "Student", actor_style()),
        Node("actor-staff", 844, 205, 76, 100, "TA / Faculty", actor_style()),
        Node("actor-admin", 844, 520, 76, 100, "Placement Admin", actor_style()),
    ):
        add(node)

    add(Node("legend", 100, 752, 800, 22,
             "Blue: Student use cases      Green: TA / Faculty use cases      "
             "Amber: Placement Admin use cases      Plain lines: actor associations",
             text_style(F_LEGEND, MUTED)))

    def associate(actor_id: str, anchor: tuple[float, float], exit_rel: tuple[float, float],
                  targets: list[str], from_left: bool) -> None:
        for target_id in targets:
            oval = ovals[target_id]
            point = ellipse_side_point(oval, from_left, anchor[1])
            entry_rel = rel(oval, *point)
            diagram.edges.append(Edge(
                id=f"e-{actor_id}-{target_id}", source=actor_id, target=target_id,
                exit=exit_rel, entry=entry_rel,
                style=edge_style(exit_rel, entry_rel, arrow="none"),
            ))

    associate("actor-student", (126, 412), (1.0, 0.5), [f"uc-s{i}" for i in range(6)], True)
    associate("actor-staff", (844, 255), (0.0, 0.5), [f"uc-t{i}" for i in range(3)], False)
    associate("actor-admin", (844, 570), (0.0, 0.5), [f"uc-a{i}" for i in range(3)], False)
    return diagram


# --------------------------------------------------------------------------
# Shared data-flow helpers
# --------------------------------------------------------------------------
def side_anchor(node: Node, other: Node, y: float) -> float:
    """X coordinate where a horizontal flow at `y` leaves/meets `node`."""
    if "ellipse" in node.style:
        return ellipse_x_at_y(node, y, left=other.cx < node.cx)
    return node.x + node.w if other.cx > node.cx else node.x


def add_horizontal_flow(diagram: Diagram, edge_id: str, src: Node, dst: Node, y: float,
                        label: str, wrap_width: float, above: bool = True) -> None:
    sx = side_anchor(src, dst, y)
    tx = side_anchor(dst, src, y)
    exit_rel, entry_rel = rel(src, sx, y), rel(dst, tx, y)
    text = wrap(label, wrap_width, size=F_EDGE)
    _, bh = block_size(text, F_EDGE)
    offset_y = -(bh / 2 + 5) if above else (bh / 2 + 5)
    diagram.edges.append(Edge(
        id=edge_id, source=src.id, target=dst.id, exit=exit_rel, entry=entry_rel,
        label=text, label_offset=(0.0, offset_y), style=edge_style(exit_rel, entry_rel),
    ))


# --------------------------------------------------------------------------
# Diagram 2: DFD level 0
# --------------------------------------------------------------------------
def build_dfd0() -> Diagram:
    diagram = Diagram("DFD Level 0", "dfd-level-0", 1000, 540)
    add = diagram.nodes.append

    add(Node("title", 200, 12, 600, 32, "DeadlineDesk Data-Flow Diagram (Level 0)",
             text_style(F_TITLE, INK, bold=True)))
    add(Node("subtitle", 150, 40, 700, 22,
             "System context - external entities and the single DeadlineDesk process",
             text_style(F_SUBTITLE, MUTED)))

    entity_fill, entity_stroke = ENTITY
    process_fill, process_stroke = PROCESS

    admin = Node("e-admin", 405, 62, 170, 58, "Placement Admin",
                 box_style(entity_fill, entity_stroke))
    student = Node("e-student", 30, 205, 170, 270, "Student",
                   box_style(entity_fill, entity_stroke))
    staff = Node("e-staff", 800, 230, 170, 220, "TA / Faculty",
                 box_style(entity_fill, entity_stroke))
    process = Node("p0", 365, 215, 250, 250, "0. DeadlineDesk",
                   ellipse_style(process_fill, process_stroke, size=20, bold=True))
    for node in (admin, student, staff, process):
        add(node)

    add(Node("legend", 100, 502, 800, 22,
             "Rectangles: external entities      Circle: system process      "
             "Arrows: direction of data movement",
             text_style(F_LEGEND, MUTED)))

    flows = [
        ("f1", student, process, 240, "credentials", True),
        ("f2", student, process, 280, "checklist updates", True),
        ("f3", student, process, 320, "submission file", True),
        ("f4", process, student, 360, "readiness result", False),
        ("f5", process, student, 400, "late result", False),
        ("f6", process, student, 440, "grade and feedback", False),
        ("f7", staff, process, 265, "assignment policy", True),
        ("f8", staff, process, 315, "review and grade", True),
        ("f9", process, staff, 405, "submission and similarity data", False),
    ]
    for edge_id, src, dst, y, label, above in flows:
        add_horizontal_flow(diagram, edge_id, src, dst, y, label, 165, above=above)

    def vertical(edge_id: str, src: Node, dst: Node, x: float, label: str, left: bool) -> None:
        if "ellipse" in src.style:
            exit_rel = rel(src, x, ellipse_y_at_x(src, x, top=True))
            entry_rel = rel(dst, x, dst.y + dst.h)
        else:
            exit_rel = rel(src, x, src.y + src.h)
            entry_rel = rel(dst, x, ellipse_y_at_x(dst, x, top=True))
        text = wrap(label, 175, size=F_EDGE)
        bw, _ = block_size(text, F_EDGE)
        offset_x = -(bw / 2 + 12) if left else (bw / 2 + 12)
        diagram.edges.append(Edge(
            id=edge_id, source=src.id, target=dst.id, exit=exit_rel, entry=entry_rel,
            label=text, label_offset=(offset_x, 0.0), style=edge_style(exit_rel, entry_rel),
        ))

    vertical("f10", admin, process, 450, "companies, rounds and checklist items", True)
    vertical("f11", process, admin, 530, "publication and reminder status", False)
    return diagram


# --------------------------------------------------------------------------
# Diagram 3: DFD level 1
# --------------------------------------------------------------------------
L1_ROWS = [195.0, 385.0, 575.0, 765.0]
L1_ROW_DATA = [
    ("All authenticated roles", "1.0 Authentication and Roles", "D1\nUsers and Roles",
     "credentials", "authenticated session and role",
     "user and role records", "role and credential lookup"),
    ("Placement Admin", "2.0 Placement Track", "D2\nPlacement Data",
     "companies, rounds and checklist items", "publication and readiness status",
     "round and checklist records", "checklist completion data"),
    ("Student", "3.0 Academic Dropbox", "D3\nAcademic Data",
     "submission file", "late result, grade and feedback",
     "submission and grade records", "assignment and late policy"),
    ("TA / Faculty", "4.0 Reminder and Audit", "D4\nAudit and Reminder Logs",
     "assignment policy and deadline changes", "reminder and audit trail",
     "reminder and audit records", "scheduled reminder log"),
]
L1_PROCESS_EVENTS = [
    "authorised role context",
    "deadline and policy context",
    "publication, submission and grading events",
]


def build_dfd1() -> Diagram:
    """Left-to-right rows: external entity -> process -> data store.

    The canvas is kept close to A4 proportions so the figure stays legible at
    full text width in a portrait proposal, without a rotated page.
    """
    diagram = Diagram("DFD Level 1", "dfd-level-1", 1000, 930)
    add = diagram.nodes.append

    add(Node("title", 200, 18, 600, 32, "DeadlineDesk Data-Flow Diagram (Level 1)",
             text_style(F_TITLE, INK, bold=True)))
    add(Node("subtitle", 150, 48, 700, 22,
             "Implemented processes, persistent stores and the roles they serve",
             text_style(F_SUBTITLE, MUTED)))
    add(Node("h-entities", 24, 96, 168, 22, "External entities",
             text_style(F_HEADER, MUTED, bold=True)))
    add(Node("h-processes", 375, 96, 250, 22, "Processes",
             text_style(F_HEADER, MUTED, bold=True)))
    add(Node("h-stores", 760, 96, 215, 22, "Data stores",
             text_style(F_HEADER, MUTED, bold=True)))

    entity_fill, entity_stroke = ENTITY
    process_fill, process_stroke = PROCESS

    entities: list[Node] = []
    processes: list[Node] = []
    stores: list[Node] = []
    for index, (row_y, data) in enumerate(zip(L1_ROWS, L1_ROW_DATA)):
        entity = Node(f"n-e{index}", 24, row_y - 38, 168, 76,
                      wrap(data[0], 145), box_style(entity_fill, entity_stroke))
        process = Node(f"n-p{index}", 375, row_y - 45, 250, 90,
                       wrap(data[1], 185), ellipse_style(process_fill, process_stroke))
        store = Node(f"n-d{index}", 760, row_y - 41, 215, 82,
                     wrap(data[2], 180), store_style())
        entities.append(entity)
        processes.append(process)
        stores.append(store)
        for node in (entity, process, store):
            add(node)

    add(Node("legend", 100, 886, 800, 22,
             "Rectangles: external entities      Ovals: processes      "
             "Open rectangles: data stores      Arrows: direction of data movement",
             text_style(F_LEGEND, MUTED)))

    for index, row_y in enumerate(L1_ROWS):
        entity, process, store = entities[index], processes[index], stores[index]
        _, _, _, to_process, to_entity, to_store, from_store = L1_ROW_DATA[index]
        add_horizontal_flow(diagram, f"l1-a{index}", entity, process, row_y - 22,
                            to_process, 178, above=True)
        add_horizontal_flow(diagram, f"l1-b{index}", process, entity, row_y + 22,
                            to_entity, 178, above=False)
        add_horizontal_flow(diagram, f"l1-c{index}", process, store, row_y - 22,
                            to_store, 132, above=True)
        add_horizontal_flow(diagram, f"l1-d{index}", store, process, row_y + 22,
                            from_store, 132, above=False)

    for index, label in enumerate(L1_PROCESS_EVENTS):
        src, dst = processes[index], processes[index + 1]
        exit_rel = rel(src, src.cx, src.y + src.h)
        entry_rel = rel(dst, dst.cx, dst.y)
        # Centred on the arrow (with a white label background) so the text stays
        # clear of the entity-side and store-side flow labels on either side.
        text = wrap(label, 215, size=F_EDGE)
        diagram.edges.append(Edge(
            id=f"l1-v{index}", source=src.id, target=dst.id,
            exit=exit_rel, entry=entry_rel,
            label=text, label_offset=(0.0, 0.0),
            style=edge_style(exit_rel, entry_rel),
        ))
    return diagram


# --------------------------------------------------------------------------
def main() -> int:
    FIGURES.mkdir(parents=True, exist_ok=True)
    builders = [
        ("use-case-diagram", build_use_case),
        ("dfd-level-0", build_dfd0),
        ("dfd-level-1", build_dfd1),
    ]
    for stem, builder in builders:
        diagram = builder()
        drawio_path = FIGURES / f"{stem}.drawio"
        pdf_path = FIGURES / f"{stem}.pdf"
        png_path = FIGURES / f"{stem}.png"
        write_drawio(diagram, drawio_path)
        render_pdf(drawio_path, pdf_path)
        render_png(pdf_path, png_path)
        print(f"{stem}: {drawio_path.name}, {pdf_path.name}, {png_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
