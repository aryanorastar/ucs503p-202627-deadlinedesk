#!/usr/bin/env python3
"""Render the Week 7 schedule, activity flows, and data model.

Each editable .drawio file is the source for its matching PDF and PNG export.
Run from the repository root with:

    python3 project-proposal/scripts/render_additional_diagrams.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from render_diagrams import (
    ACTOR_FILLS,
    ENTITY,
    INK,
    LINE,
    MUTED,
    PROCESS,
    STORE,
    WHITE,
    Diagram,
    Edge,
    Node,
    box_style,
    edge_style,
    ellipse_style,
    rel,
    render_pdf,
    render_png,
    text_style,
    write_drawio,
)


FIGURES = Path(__file__).resolve().parents[1] / "figures"
PRESENTATION_VIEWS = Path(__file__).resolve().parents[2] / "tmp/deadlinedesk-week7-ppt/figures"


def label_style(size: int = 16, color: str = INK, bold: bool = False,
                align: str = "center") -> str:
    return text_style(size, color, bold=bold, align=align)


def rhombus_style(fill: str, stroke: str, size: int = 18) -> str:
    return (
        f"rhombus;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
        f"strokeWidth=1.6;fontColor={INK};fontSize={size};fontFamily=Helvetica;"
        "verticalAlign=middle;align=center;"
    )


def path_edge(diagram: Diagram, edge_id: str, source: Node, target: Node,
              start: tuple[float, float], finish: tuple[float, float],
              points: list[tuple[float, float]] | None = None,
              label: str = "", label_offset: tuple[float, float] = (0.0, 0.0),
              arrow: str = "block") -> None:
    exit_rel, entry_rel = rel(source, *start), rel(target, *finish)
    diagram.edges.append(Edge(
        edge_id, source.id, target.id, exit_rel, entry_rel,
        label=label,
        label_offset=label_offset,
        points=points or [],
        style=edge_style(exit_rel, entry_rel, arrow=arrow),
    ))


def build_gantt() -> Diagram:
    diagram = Diagram("Gantt Chart Through Week 7", "gantt-chart", 1420, 620)
    add = diagram.nodes.append
    add(Node("title", 240, 18, 940, 34, "DeadlineDesk Project Gantt Chart",
             label_style(30, INK, True)))
    add(Node("subtitle", 180, 52, 1060, 26,
             "Documented milestones from Week 3 through the Week 7 prototype",
             label_style(18, MUTED)))

    task_x, task_w = 48, 420
    week_x, week_w, grid_top, grid_bottom = 480, 185, 155, 480
    row_centers = [202, 255, 308, 361, 414, 467]
    week_names = ["W3", "W4", "W5", "W6", "W7"]

    # Alternating week columns and row rules form a quiet, readable time grid.
    for index, week in enumerate(week_names):
        x = week_x + index * week_w
        fill = "#F2F5F9" if index % 2 == 0 else "#FFFFFF"
        add(Node(f"week-bg-{index}", x, grid_top, week_w, grid_bottom - grid_top, "",
                 f"rounded=0;fillColor={fill};strokeColor=#D6DDE6;strokeWidth=1;"))
        add(Node(f"week-label-{index}", x, 115, week_w, 28, week,
                 label_style(19, INK, True)))

    add(Node("task-header", task_x, 115, task_w, 28, "Work item",
             label_style(19, INK, True, "left")))
    tasks = [
        ("Scope definition, proposal and repository setup", 0, 2, "#1A2B47", "Plan"),
        ("Architecture, roles, SRS and user flows", 2, 1, "#426C9E", "Design"),
        ("Authentication and academic late-policy rules", 2, 1, "#426C9E", "Foundation"),
        ("Placement Track and Academic Dropbox workflows", 3, 1, "#2F7A52", "Build"),
        ("Responsive UI, review and grading integration", 3, 1, "#2F7A52", "Integrate"),
        ("Automated tests, browser QA, CI, docs and demo seed", 4, 1, "#C07A16", "Verify"),
    ]
    for index, (label, start_week, duration, color, phase) in enumerate(tasks):
        cy = row_centers[index]
        add(Node(f"task-{index}", task_x, cy - 18, task_w, 36, label,
                 label_style(17, INK, False, "left")))
        left = week_x + start_week * week_w + 10
        width = duration * week_w - 20
        add(Node(f"bar-{index}", left, cy - 14, width, 28, phase,
                 box_style(color, color, size=14, bold=True, rounded=True)))
        if index < len(tasks) - 1:
            add(Node(f"row-rule-{index}", task_x, cy + 29, task_w + 5 * week_w, 1,
                     "", "rounded=0;fillColor=#E0E5EC;strokeColor=none;"))

    add(Node("note", 48, 510, 1320, 28,
             "Week-level view from the proposal, backlog and Week 4–7 journals; it does not imply day-level estimates.",
             label_style(16, MUTED, False, "left")))
    add(Node("legend", 48, 560, 1320, 24,
             "Navy: scope and setup      Blue: design and foundation      Green: implementation      Amber: Week 7 verification",
             label_style(15, MUTED)))
    return diagram


def build_activity_placement() -> Diagram:
    diagram = Diagram("Placement Track Activity Diagram", "activity-placement", 1500, 610)
    add = diagram.nodes.append
    add(Node("title", 150, 18, 700, 34, "Placement Track Activity Diagram",
             label_style(27, INK, True)))
    add(Node("subtitle", 100, 50, 800, 24,
             "Round publication, reminder logging and student readiness",
             label_style(16, MUTED)))

    blue_fill, blue_stroke = ACTOR_FILLS["student"]
    green_fill, green_stroke = ACTOR_FILLS["staff"]
    amber_fill, amber_stroke = PROCESS
    initial = Node("start", 40, 160, 40, 40, "",
                   ellipse_style(INK, INK, size=12))
    admin = Node("admin-publish", 120, 120, 230, 120,
                 "Placement Admin\nCreate company and round\nwith required checklist",
                 box_style(green_fill, green_stroke, size=20, bold=True))
    reminder = Node("reminder-log", 400, 120, 230, 120,
                    "DeadlineDesk\nPublish the round and log\nT-24h reminder",
                    box_style(amber_fill, amber_stroke, size=20, bold=True))
    student = Node("student-checklist", 680, 120, 230, 120,
                   "Student\nOpen published round and\ncomplete checklist",
                   box_style(blue_fill, blue_stroke, size=20, bold=True))
    decision = Node("checklist-decision", 980, 105, 180, 150,
                    "All required\nitems complete?",
                    rhombus_style("#FFF9EC", amber_stroke, 20))
    ready = Node("ready", 1220, 120, 240, 120,
                 "DeadlineDesk\nShow readiness result",
                 box_style(amber_fill, amber_stroke, size=20, bold=True))
    final_outer = Node("end-outer", 1318, 340, 44, 44, "",
                       ellipse_style(WHITE, INK, size=10))
    final_inner = Node("end-inner", 1331, 353, 18, 18, "",
                       ellipse_style(INK, INK, size=10))
    for node in (initial, admin, reminder, student, decision, ready, final_outer, final_inner):
        add(node)

    path_edge(diagram, "p-start-admin", initial, admin, (80, 180), (120, 180))
    path_edge(diagram, "p-admin-reminder", admin, reminder, (350, 180), (400, 180))
    path_edge(diagram, "p-reminder-student", reminder, student, (630, 180), (680, 180))
    path_edge(diagram, "p-student-decision", student, decision, (910, 180), (980, 180))
    path_edge(diagram, "p-yes", decision, ready, (1160, 180), (1220, 180),
              label="Yes", label_offset=(0, -22))
    path_edge(diagram, "p-no-loop", decision, student, (1070, 255), (795, 240),
              points=[(1070, 335), (795, 335)], label="Not yet",
              label_offset=(0, -22))
    path_edge(diagram, "p-ready-end", ready, final_outer, (1340, 240), (1340, 340))

    add(Node("legend", 150, 462, 1200, 26,
             "Blue: Student action      Green: Placement Admin action      Amber: system action or decision",
             label_style(14, MUTED)))
    add(Node("scope-note", 160, 500, 1180, 28,
             "The reminder is stored as a scheduled log entry; email delivery is outside the Week 7 prototype.",
             label_style(14, MUTED)))
    return diagram


def build_activity_academic() -> Diagram:
    diagram = Diagram("Academic Dropbox Activity Diagram", "activity-academic", 1840, 650)
    add = diagram.nodes.append
    add(Node("title", 150, 18, 700, 34, "Academic Dropbox Activity Diagram",
             label_style(27, INK, True)))
    add(Node("subtitle", 100, 50, 800, 24,
             "Submission acceptance, late-policy evaluation and grading",
             label_style(16, MUTED)))

    blue_fill, blue_stroke = ACTOR_FILLS["student"]
    green_fill, green_stroke = ACTOR_FILLS["staff"]
    amber_fill, amber_stroke = PROCESS
    initial = Node("start", 32, 160, 40, 40, "",
                   ellipse_style(INK, INK, size=12))
    publish = Node("publish-assignment", 100, 120, 220, 110,
                    "TA / Faculty\nPublish assignment,\ndue time and late policy",
                    box_style(green_fill, green_stroke, size=19, bold=True))
    upload = Node("upload-file", 380, 120, 205, 110,
                  "Student\nUpload assignment file",
                  box_style(blue_fill, blue_stroke, size=20, bold=True))
    evaluate = Node("evaluate-policy", 640, 120, 245, 110,
                    "DeadlineDesk\nRecord time and apply\nreject, grace or penalty",
                    box_style(amber_fill, amber_stroke, size=19, bold=True))
    decision = Node("accepted-decision", 930, 100, 180, 150,
                    "Submission\naccepted?",
                    rhombus_style("#FFF9EC", amber_stroke, 20))
    rejected = Node("rejected", 820, 355, 235, 88,
                    "Student sees\nrejection reason",
                    box_style(blue_fill, blue_stroke, size=20, bold=True))
    rejected_end = Node("rejected-end-outer", 915, 495, 44, 44, "",
                        ellipse_style(WHITE, INK, size=10))
    rejected_end_inner = Node("rejected-end-inner", 928, 508, 18, 18, "",
                              ellipse_style(INK, INK, size=10))
    accepted = Node("accepted", 1180, 120, 250, 110,
                    "DeadlineDesk\nSave late outcome and\ncalculate similarity stub",
                    box_style(amber_fill, amber_stroke, size=19, bold=True))
    grade = Node("grade", 1480, 120, 250, 110,
                 "TA / Faculty\nReview and enter grade\n+ feedback",
                 box_style(green_fill, green_stroke, size=19, bold=True))
    result = Node("result", 1480, 335, 250, 100,
                  "Student\nView late status, grade\nand feedback",
                  box_style(blue_fill, blue_stroke, size=19, bold=True))
    final_outer = Node("accepted-end-outer", 1760, 360, 44, 44, "",
                       ellipse_style(WHITE, INK, size=10))
    final_inner = Node("accepted-end-inner", 1773, 373, 18, 18, "",
                       ellipse_style(INK, INK, size=10))
    for node in (initial, publish, upload, evaluate, decision, rejected,
                 rejected_end, rejected_end_inner, accepted, grade, result,
                 final_outer, final_inner):
        add(node)

    path_edge(diagram, "a-start-publish", initial, publish, (72, 180), (100, 175))
    path_edge(diagram, "a-publish-upload", publish, upload, (320, 175), (380, 175))
    path_edge(diagram, "a-upload-evaluate", upload, evaluate, (585, 175), (640, 175))
    path_edge(diagram, "a-evaluate-decision", evaluate, decision, (885, 175), (930, 175))
    path_edge(diagram, "a-reject", decision, rejected, (1020, 250), (937, 355),
              points=[(1020, 305), (937, 305)], label="No: reject",
              label_offset=(-70, 0))
    path_edge(diagram, "a-rejected-end", rejected, rejected_end, (937, 443), (937, 495))
    path_edge(diagram, "a-accept", decision, accepted, (1110, 175), (1180, 175),
              label="Yes", label_offset=(0, -22))
    path_edge(diagram, "a-accepted-grade", accepted, grade, (1430, 175), (1480, 175))
    path_edge(diagram, "a-grade-result", grade, result, (1605, 230), (1605, 335))
    path_edge(diagram, "a-result-end", result, final_outer, (1730, 385), (1760, 382))

    add(Node("legend", 390, 570, 1060, 22,
             "Blue: Student      Green: TA / Faculty      Amber: DeadlineDesk",
             label_style(14, MUTED)))
    add(Node("scope-note", 350, 600, 1140, 22,
             "The text-overlap score is a teaching stub, not a plagiarism verdict.",
             label_style(14, MUTED)))
    return diagram


def build_er_placement_model() -> Diagram:
    diagram = Diagram("Placement Track ER Model", "er-placement-model", 1500, 650)
    add = diagram.nodes.append
    add(Node("title", 330, 18, 840, 36, "Placement Track Data Model",
             label_style(30, INK, True)))
    add(Node("subtitle", 260, 54, 980, 26,
             "Week 7 Django entities and placement relationships",
             label_style(18, MUTED)))

    identity_fill, identity_stroke = ENTITY
    placement_fill, placement_stroke = ACTOR_FILLS["student"]
    user = Node("user", 610, 100, 280, 90,
                "User\nPK id · username UQ\nrole · roll_number",
                box_style(identity_fill, identity_stroke, size=18, bold=True))
    company = Node("company", 40, 245, 230, 120,
                   "Company\nPK id · name UQ\ncreated_by FK User",
                   box_style(placement_fill, placement_stroke, size=18, bold=True))
    round_ = Node("placement-round", 350, 230, 320, 150,
                  "PlacementRound\nPK id · company_id FK\ntitle · opens_at · closes_at\nstatus · created_by FK User",
                  box_style(placement_fill, placement_stroke, size=18, bold=True))
    reminder = Node("reminder-log", 800, 245, 300, 120,
                    "ReminderLog\nPK id · placement_round_id FK\nscheduled_for · status · sent_at",
                    box_style(placement_fill, placement_stroke, size=17, bold=True))
    audit = Node("audit-log", 40, 445, 270, 120,
                 "AuditLog\nPK id · actor_id FK User (nullable)\naction · entity_type/id · detail JSON",
                 box_style(identity_fill, identity_stroke, size=16, bold=True))
    item = Node("checklist-item", 400, 445, 300, 120,
                "ChecklistItem\nPK id · placement_round_id FK\ntitle · required · position",
                box_style(placement_fill, placement_stroke, size=18, bold=True))
    completion = Node("checklist-completion", 850, 435, 360, 140,
                      "ChecklistCompletion\nPK id · item_id FK · student_id FK User\ncompleted_at · UQ(item_id, student_id)",
                      box_style(placement_fill, placement_stroke, size=17, bold=True))
    for node in (user, company, round_, reminder, audit, item, completion):
        add(node)

    path_edge(diagram, "company-round", company, round_, (270, 305), (350, 305),
              label="1 : N", label_offset=(0, -20), arrow="none")
    path_edge(diagram, "round-reminder", round_, reminder, (670, 305), (800, 305),
              label="1 : N", label_offset=(0, -20), arrow="none")
    path_edge(diagram, "round-item", round_, item, (510, 380), (550, 445),
              points=[(510, 410), (550, 410)], label="1 : N",
              label_offset=(35, 0), arrow="none")
    path_edge(diagram, "item-completion", item, completion,
              (700, 505), (850, 505), label="1 : N",
              label_offset=(0, -20), arrow="none")
    path_edge(diagram, "user-round", user, round_, (750, 190), (510, 230),
              arrow="none")
    add(Node("note", 345, 600, 840, 28,
             "User foreign keys also identify the creator, checklist student and audit actor.",
             label_style(15, MUTED)))
    return diagram


def build_er_academic_model() -> Diagram:
    diagram = Diagram("Academic Dropbox ER Model", "er-academic-model", 1500, 600)
    add = diagram.nodes.append
    add(Node("title", 330, 18, 840, 36, "Academic Dropbox Data Model",
             label_style(30, INK, True)))
    add(Node("subtitle", 260, 54, 980, 26,
             "Week 7 Django entities and submission relationships",
             label_style(18, MUTED)))

    identity_fill, identity_stroke = ENTITY
    academic_fill, academic_stroke = ACTOR_FILLS["staff"]
    user = Node("user", 610, 100, 280, 90,
                "User\nPK id · username UQ\nrole · roll_number",
                box_style(identity_fill, identity_stroke, size=18, bold=True))
    assignment = Node("assignment", 100, 280, 300, 130,
                      "Assignment\nPK id · title · due_at\nlate_policy · created_by FK User",
                      box_style(academic_fill, academic_stroke, size=19, bold=True))
    submission = Node("submission", 570, 265, 380, 160,
                      "Submission\nPK id · assignment_id FK\nstudent_id FK User · file · submitted_at\nlate_status · penalty · similarity · status\nUQ(assignment_id, student_id)",
                      box_style(academic_fill, academic_stroke, size=17, bold=True))
    grade = Node("grade", 1120, 280, 300, 130,
                 "Grade\nPK id · submission_id FK UQ\nscore · max_score · feedback\ngraded_by FK User",
                 box_style(academic_fill, academic_stroke, size=18, bold=True))
    for node in (user, assignment, submission, grade):
        add(node)

    path_edge(diagram, "assignment-submission", assignment, submission,
              (400, 345), (570, 345), label="1 : N",
              label_offset=(0, -20), arrow="none")
    path_edge(diagram, "submission-grade", submission, grade,
              (950, 345), (1120, 345), label="1 : 0..1",
              label_offset=(0, -20), arrow="none")
    path_edge(diagram, "user-assignment", user, assignment,
              (680, 190), (250, 280), arrow="none")
    add(Node("note", 250, 485, 1000, 42,
             "User foreign keys identify assignment creator, submitting student and grader. A student has one submission per assignment; each submission has at most one grade.",
             label_style(15, MUTED)))
    return diagram


def build_er() -> Diagram:
    diagram = Diagram("DeadlineDesk Entity Relationship Diagram", "er-diagram", 1800, 760)
    add = diagram.nodes.append
    add(Node("title", 300, 18, 1200, 34, "DeadlineDesk Entity-Relationship Diagram",
             label_style(28, INK, True)))
    add(Node("subtitle", 380, 52, 1040, 24,
             "Week 7 Django data model; PK = primary key, FK = foreign key, UQ = unique",
             label_style(16, MUTED)))

    identity_fill, identity_stroke = ENTITY
    placement_fill, placement_stroke = ACTOR_FILLS["student"]
    academic_fill, academic_stroke = ACTOR_FILLS["staff"]

    # Domain headings and subtle grouping fields.
    add(Node("placement-group", 30, 230, 960, 30, "PLACEMENT TRACK",
             label_style(17, placement_stroke, True, "left")))
    add(Node("academic-group", 1120, 230, 620, 30, "ACADEMIC DROPBOX",
             label_style(17, academic_stroke, True, "left")))

    user = Node("user", 760, 90, 280, 120,
                "User\nPK id\nusername UQ · role · roll_number",
                box_style(identity_fill, identity_stroke, size=16, bold=True))
    company = Node("company", 30, 280, 220, 120,
                   "Company\nPK id\nname UQ\ncreated_by FK User",
                   box_style(placement_fill, placement_stroke, size=16, bold=True))
    round_ = Node("placement-round", 320, 265, 280, 150,
                  "PlacementRound\nPK id · company_id FK\ntitle · opens_at · closes_at\nstatus · created_by FK User",
                  box_style(placement_fill, placement_stroke, size=15, bold=True))
    reminder = Node("reminder-log", 690, 280, 250, 125,
                    "ReminderLog\nPK id · placement_round_id FK\nscheduled_for · status · sent_at\ncreated_by FK User",
                    box_style(placement_fill, placement_stroke, size=14, bold=True))
    item = Node("checklist-item", 55, 530, 250, 125,
                "ChecklistItem\nPK id · placement_round_id FK\ntitle · required · position",
                box_style(placement_fill, placement_stroke, size=16, bold=True))
    completion = Node("checklist-completion", 380, 525, 300, 140,
                      "ChecklistCompletion\nPK id · item_id FK\nstudent_id FK User · completed_at\nUQ(item_id, student_id)",
                      box_style(placement_fill, placement_stroke, size=14, bold=True))
    assignment = Node("assignment", 1190, 280, 240, 125,
                      "Assignment\nPK id\ntitle · due_at · late_policy\ncreated_by FK User",
                      box_style(academic_fill, academic_stroke, size=16, bold=True))
    submission = Node("submission", 1480, 270, 280, 150,
                      "Submission\nPK id · assignment_id FK\nstudent_id FK User · file · submitted_at\nlate_status · penalty · similarity · status\nUQ(assignment_id, student_id)",
                      box_style(academic_fill, academic_stroke, size=14, bold=True))
    grade = Node("grade", 1480, 530, 280, 130,
                 "Grade\nPK id · submission_id FK UQ\nscore · max_score · feedback\ngraded_by FK User",
                 box_style(academic_fill, academic_stroke, size=15, bold=True))
    audit = Node("audit-log", 720, 530, 270, 125,
                 "AuditLog\nPK id · actor_id FK User (nullable)\naction · entity_type/id · detail JSON",
                 box_style(identity_fill, identity_stroke, size=14, bold=True))
    entities = [user, company, round_, reminder, item, completion,
                assignment, submission, grade, audit]
    for entity in entities:
        add(entity)

    # Domain relationships. User foreign keys are named on each table and
    # summarized in the explanatory note so the diagram stays uncluttered.
    path_edge(diagram, "er-company-round", company, round_,
              (250, 340), (320, 340), label="1 : N", label_offset=(0, -20), arrow="none")
    path_edge(diagram, "er-round-item", round_, item,
              (460, 415), (180, 530), points=[(460, 475), (180, 475)],
              label="1 : N", label_offset=(-12, -20), arrow="none")
    path_edge(diagram, "er-round-reminder", round_, reminder,
              (600, 340), (690, 342), label="1 : N", label_offset=(0, -20), arrow="none")
    path_edge(diagram, "er-item-completion", item, completion,
              (305, 592), (380, 595), label="1 : N", label_offset=(0, -20), arrow="none")
    path_edge(diagram, "er-assignment-submission", assignment, submission,
              (1430, 342), (1480, 345), label="1 : N", label_offset=(0, -20), arrow="none")
    path_edge(diagram, "er-submission-grade", submission, grade,
              (1620, 420), (1620, 530), label="1 : 0..1", label_offset=(42, 0), arrow="none")

    add(Node("constraints-note", 180, 690, 1450, 42,
             "User is referenced by created_by, student_id, graded_by and actor_id. One student has one checklist completion per item and one submission per assignment; each submission has at most one grade.",
             label_style(14, MUTED, False, "left")))
    return diagram


def main() -> int:
    FIGURES.mkdir(parents=True, exist_ok=True)
    builders = [
        build_gantt,
        build_activity_placement,
        build_activity_academic,
        build_er,
    ]
    for builder in builders:
        diagram = builder()
        drawio_path = FIGURES / f"{diagram.filename}.drawio"
        pdf_path = FIGURES / f"{diagram.filename}.pdf"
        png_path = FIGURES / f"{diagram.filename}.png"
        write_drawio(diagram, drawio_path)
        render_pdf(drawio_path, pdf_path)
        render_png(pdf_path, png_path)
        print(f"{diagram.filename}: {drawio_path.name}, {pdf_path.name}, {png_path.name}")
    PRESENTATION_VIEWS.mkdir(parents=True, exist_ok=True)
    for builder in (build_er_placement_model, build_er_academic_model):
        diagram = builder()
        drawio_path = PRESENTATION_VIEWS / f"{diagram.filename}.drawio"
        pdf_path = PRESENTATION_VIEWS / f"{diagram.filename}.pdf"
        png_path = PRESENTATION_VIEWS / f"{diagram.filename}.png"
        write_drawio(diagram, drawio_path)
        render_pdf(drawio_path, pdf_path)
        render_png(pdf_path, png_path)
        print(f"{diagram.filename}: generated presentation-only view in {PRESENTATION_VIEWS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
