// Rebuild the final evaluation deck using the bundled Artifact Tool runtime.
// Run with the bundled Node executable; set ARTIFACT_TOOL_ROOT if using another install.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const RUNTIME = process.env.ARTIFACT_RUNTIME_ROOT || '/Users/astar/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const SKILL = process.env.PRESENTATION_SKILL_DIR || '/Users/astar/.codex/plugins/cache/openai-primary-runtime/presentations/26.1123.11515/skills/presentations';
const TOOL = process.env.ARTIFACT_TOOL_ROOT || path.join(RUNTIME, 'node/node_modules/@oai/artifact-tool');
process.env.RUNTIME_NODE_MODULES ||= path.join(RUNTIME,'node/node_modules');
process.env.RUNTIME_NODE ||= path.join(RUNTIME,'node/bin/node');
const { Presentation, PresentationFile, registerPdfFontFace } = await import(pathToFileURL(path.join(TOOL, 'dist/artifact_tool.mjs')).href);
for(const [weight,file] of [[400,'Arial.ttf'],[700,'Arial Bold.ttf']]) {
 const source=await fs.readFile(path.join(process.env.PRESENTATION_FONT_DIR || '/System/Library/Fonts/Supplemental',file));
 registerPdfFontFace({family:'Arial',weight,style:'normal',source});
}
const { finalizePresentation } = await import(pathToFileURL(path.join(SKILL, 'container_tools/artifact_tool_utils.mjs')).href);
const OUT = path.join(ROOT, 'docs/submission/09-final-presentation');
const TMP = path.join(ROOT, 'tmp/final-deck');
await fs.mkdir(path.join(OUT, 'slides'), { recursive: true });
await fs.mkdir(TMP, { recursive: true });
const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const C = { navy:'#172C46', amber:'#B87317', ink:'#20334B', muted:'#5A6878', light:'#F7F8FA', white:'#FFFFFF' };
const FONT = 'Arial';
const specs=[];

function text(slide, value, x, y, w, h, size=24, color=C.ink, bold=false) {
  const shape=slide.shapes.add({ geometry:'textbox', position:{left:x,top:y,width:w,height:h}, fill:'none', line:{fill:'none',width:0} });
  shape.text=value;
  shape.text.style={fontFamily:FONT,fontSize:size,color,bold};
  return shape;
}
function slide(section,title,notes='') {
  const s=presentation.slides.add();
  s.background.fill=C.white;
  text(s,section.toUpperCase(),72,34,1050,26,17,C.amber,true);
  text(s,title,72,81,1136,82,44,C.navy,true);
  text(s,`DeadlineDesk    UCS503P    ${presentation.slides.items.length}`,72,675,1136,24,15,C.muted);
  s.speakerNotes.text=notes;
  specs.push({section,title});
  return s;
}
function row(s,label,body,y,{labelWidth=280,size=26}={}) {
  text(s,label,72,y,labelWidth,64,size,C.navy,true);
  text(s,body,72+labelWidth+28,y,1136-labelWidth-28,88,size,C.ink);
}
async function image(s,rel,x,y,w,h,alt) {
  const bytes=await fs.readFile(path.join(ROOT,rel));
  s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});
}

// 1. Introduction
{
 const s=slide('Introduction','DeadlineDesk','Sources: README.md, project-report-final/main.tex. Introduce the campus deadline problem and both implemented workflows. Evaluation is 1 December 2026, 8:00 AM, Lab 105.');
 s.background.fill=C.navy;
 for(const shape of s.shapes.items) shape.text.style={...shape.text.style,color:C.white};
 text(s,'Placement readiness and academic submissions',72,225,1100,110,48,C.white,true);
 text(s,'Final Software Engineering Project Presentation',72,370,1100,48,28,'#E8C78F');
 text(s,'Aryan Gupta  1024030764\nAksh Goyal  1024030766\nNaveen Bansal  1024030767',72,465,1100,120,25,C.white);
}
{
 const s=slide('Introduction','Two workflows, one account','Sources: code/core/views.py, models.py; README.md. Reminder means a persisted log row. It does not mean an email was delivered.');
 row(s,'Placement Track','Publish a company round and required checklist. Students see whether they are ready to apply.',200);
 row(s,'Academic Dropbox','Publish an assignment, accept work under its late policy, then review and grade the submission.',345);
 text(s,'Shared session authentication, role checks, persistence and an audit trail support both paths.',72,525,1110,85,29,C.navy,true);
}
// 2. Background
{
 const s=slide('Background','Campus deadline work','Source: project-proposal/main.tex. These are the project motivation and intended user responsibilities, not measured campus-wide survey results.');
 row(s,'Students','Track due times, prepare placement documents and check submission feedback.',190);
 row(s,'Teaching assistants','Set late rules and maintain a consistent submission-to-grade record.',325);
 row(s,'Placement staff','Publish application windows and make required documents explicit.',460);
}
{
 const s=slide('Background','Implementation stack','Sources: requirements.txt, code/deadlinedesk/settings.py, core/templates, core/static, Dockerfile. Python is the language; Django is the web framework.');
 row(s,'Frontend','Django HTML templates and CSS render forms, dashboards and status messages.',185,{labelWidth:235,size:25});
 row(s,'Backend','Python with Django handles sessions, validation, policies and authorization.',295,{labelWidth:235,size:25});
 row(s,'Storage','SQLite holds domain records. Authenticated views serve private uploaded files.',405,{labelWidth:235,size:25});
 row(s,'Runtime','Gunicorn serves the app. WhiteNoise serves static assets. MkDocs builds the project site.',515,{labelWidth:235,size:25});
}
// 3. Problem Statement
{
 const s=slide('Problem Statement','Deadline decisions need enforceable rules','Sources: docs/srs.md; final requirements in project-report-final/main.tex. Explain that a list of deadlines alone cannot answer acceptance or readiness questions.');
 text(s,'A student needs to know what is due, what is missing and what happened after submitting.',72,185,1105,105,34,C.navy,true);
 row(s,'Readiness','Require every mandatory placement item before showing a ready result.',330,{labelWidth:235,size:25});
 row(s,'Acceptance','Use server time and the assignment’s published late policy.',435,{labelWidth:235,size:25});
 row(s,'Privacy','Keep academic files and review actions scoped to the correct users.',540,{labelWidth:235,size:25});
}
// 4. Your Solution
{
 const s=slide('Your Solution','Roles and access boundaries','Sources: core/decorators.py; core/views.py, including _check_submission_access. Final changes restrict TA ownership and current-user audit feeds.');
 const cols=[['Student','Open-round checklists\nOne accepted upload\nOwn grade and feedback'],['TA / Faculty','Own assignments\nOwn submission roster\nReview and grading'],['Placement Admin','Companies and rounds\nRequired checklist items\nPublication and reminder logs']];
 cols.forEach(([h,b],i)=>{const x=72+i*386;text(s,h,x,210,350,58,30,C.navy,true);text(s,b,x,305,350,250,25,C.ink);});
 text(s,'A Placement Admin cannot download academic files. Another TA cannot review or grade an assignment they do not own.',72,590,1120,64,22,C.muted);
}
{
 const s=slide('Your Solution','Application architecture','Source: docs/uml/06-component/diagram.drawio. The native draw.io file is the editable architecture source. No external email or plagiarism service is implemented.');
 await image(s,'docs/uml/06-component/diagram.png',72,160,1136,480,'Django application component diagram');
}
{
 const s=slide('Your Solution','Placement readiness','Sources: core/views.py round_publish, round_detail, checklist_toggle; models.py effective_status. A checklist toggle is reversible and is not retry idempotency.');
 row(s,'1  Prepare','Create a company and draft a placement round with opening and closing times.',185,{labelWidth:220,size:25});
 row(s,'2  Publish','Add at least one required item, then publish the round and record its T-24h reminder.',295,{labelWidth:220,size:25});
 row(s,'3  Complete','The student ticks required items while the round is open.',405,{labelWidth:220,size:25});
 row(s,'4  Decide','The page shows ready only when every required item is complete.',515,{labelWidth:220,size:25});
}
{
 const s=slide('Your Solution','Academic submission and grading','Sources: core/views.py assignment_submit, submission_review, submission_grade; forms.py. Rejected uploads create no Submission row; accepted files receive an explicit late status and similarity stub.');
 row(s,'Publish','The TA sets the assignment due time and one late policy.',185,{labelWidth:220,size:25});
 row(s,'Submit','The server checks duplicates, lateness, file extension and a 5 MiB ceiling.',295,{labelWidth:220,size:25});
 row(s,'Review','The assignment owner opens the accepted submission and records feedback.',405,{labelWidth:220,size:25});
 row(s,'Grade','The student sees the stored score, maximum, feedback and separate late penalty.',515,{labelWidth:220,size:25});
}
{
 const s=slide('Your Solution','Late-policy decisions','Source: core/services.py evaluate_lateness; core/tests/test_late_policy.py. Exact due time is accepted. Grace boundary is inclusive. Unknown late policy raises ValueError for a late timestamp.');
 row(s,'At the deadline','Accept as on time with no penalty.',185,{labelWidth:300,size:26});
 row(s,'Reject policy','Reject any submission after the deadline.',295,{labelWidth:300,size:26});
 row(s,'Penalty policy','Accept late work and store the configured penalty percentage.',405,{labelWidth:300,size:26});
 row(s,'Grace policy','Accept through the end of the grace window. Reject later work.',515,{labelWidth:300,size:26});
}
{
 const s=slide('Your Solution','Data relationships and state','Sources: core/models.py and docs/uml/05-state-machine/diagram.drawio. Grade is one-to-one with Submission. A graded record remains graded when start-review is pressed again; the owner can revise a grade.');
 row(s,'Placement','A company has rounds. Each round has ordered checklist items and reminder records.',185,{labelWidth:240,size:25});
 row(s,'Completion','A student/item pair has at most one checklist-completion record.',295,{labelWidth:240,size:25});
 row(s,'Academic','A student/assignment pair has one accepted submission and at most one current grade.',405,{labelWidth:240,size:25});
 row(s,'Lifecycle','Accepted work moves from submitted to under review to graded. A TA can also grade directly.',515,{labelWidth:240,size:25});
}
{
 const s=slide('Your Solution','Eight UML views','Source: docs/uml/README.md. Eight distinct UML types appear in separate docs folders. DFDs, ER diagrams and the Gantt chart are supporting material outside this count.');
 const items=[['Use case','Actors and goals'],['Class','Models and relationships'],['Sequence','Request and call order'],['Activity','Workflow decisions'],['State machine','Submission lifecycle'],['Component','Runtime responsibilities'],['Deployment','Host and artifact topology'],['Package','Source dependencies']];
 items.forEach(([name,meaning],i)=>{const col=i<4?0:1;const y=195+(i%4)*102;const x=72+col*590;text(s,name,x,y,255,50,27,C.navy,true);text(s,meaning,x,y+42,520,46,23,C.muted);});
}
{
 const s=slide('Your Solution','Demonstration deployment','Source: docs/uml/07-deployment/diagram.drawio, scripts/run_demo.py, Dockerfile. Temporary public HTTPS tunnel forwards to an isolated synthetic-data Django demo. The host and tunnel must stay active. GitHub Pages serves documentation separately.');
 await image(s,'docs/uml/07-deployment/diagram.png',72,160,1136,465,'Demo deployment topology');
}
{
 const s=slide('Your Solution','Project schedule','Source: docs/gantt-chart/gantt-chart.drawio. The original W3-4 proposal phase is reconstructed. W4-7 journals and dated October/November revisions supply the evidence. December 1 is a scheduled evaluation milestone.');
 await image(s,'docs/gantt-chart/gantt-chart.png',72,160,1136,480,'Project milestones through the final evaluation');
}
// 5. Results
{
 const s=slide('Results','36 automated cases pass','Sources: docs/test-cases/results.json, core/tests/test_late_policy.py, core/tests/test_workflows.py. The suite includes repeatable demo seeding without duplicate reminders. Passing cases verify the stated assertions. They do not establish complete security, load or concurrency coverage.');
 text(s,'36',72,190,270,160,112,C.navy,true);
 text(s,'passing cases\n25 November 2026',72,360,300,105,27,C.amber,true);
 text(s,'Late-policy boundary decisions\nPlacement publication and readiness\nPrivate submission access and TA ownership\nLogin, logout and CSRF checks\nInvalid files, duplicate uploads and grade validation',430,195,765,310,27,C.ink);
 text(s,'Remaining limits: reminder delivery, malware scanning, production concurrency and institutional sign-on.',72,570,1120,72,24,C.muted);
}
{
 const s=slide('Results','Live workflows verified','Sources: docs/final-verification.md, scripts/run_demo.py, seed_demo.py and docs/live-demo.md. Public HTTPS browser checks on 25 November verified invalid-login feedback; Student checklist readiness and real .py file upload; owner TA review, invalid 101/100 grade rejection and published 92/100 plus feedback; Student sees the persisted grade after relogin. Placement Admin created company and draft round, saw required-item publication rejection, then published after adding the item and saw Open plus T-24h reminder. Placement Admin submission access returned 403. Console warnings/errors were zero during these flows. Accounts are synthetic fixtures. Temporary tunnel availability depends on the running Mac and cloudflared process.');
 text(s,'Placement publication and student readiness verified\nFile upload, TA review and student-visible grade verified',72,185,1120,120,30,C.navy,true);
 row(s,'Demo accounts','student / Student@W7\nta / Faculty@W7\nplacement / Placement@W7',350,{labelWidth:300,size:25});
 text(s,'Open the current application link from the project site’s Live demo page.',72,520,1136,50,26,C.ink);
 text(s,'aryanorastar.github.io/ucs503p-202627-deadlinedesk/',72,578,1136,42,24,C.amber,true);
}

for (const [index,s] of presentation.slides.items.entries()) {
  const stem=`slide-${String(index+1).padStart(2,'0')}`;
  const png=await presentation.export({slide:s,format:'png',scale:1.5});
  await fs.writeFile(path.join(OUT,'slides',`${stem}.png`),new Uint8Array(await png.arrayBuffer()));
  const layout=await s.export({format:'layout'});
  await fs.writeFile(path.join(TMP,`${stem}.layout.json`),await layout.text());
}
const candidate=path.join(TMP,'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidate);
execFileSync(path.join(RUNTIME,'python/bin/python3'),['-c',`
import os,sys,zipfile,xml.etree.ElementTree as ET
p=sys.argv[1]
ns={'dc':'http://purl.org/dc/elements/1.1/','cp':'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'}
with zipfile.ZipFile(p) as z, zipfile.ZipFile(p+'.metadata','w',zipfile.ZIP_DEFLATED) as out:
 for info in z.infolist():
  data=z.read(info.filename)
  if info.filename=='docProps/core.xml':
   root=ET.fromstring(data)
   for prefix,key,value in [('dc','title','DeadlineDesk Final Project Presentation'),('dc','creator','Aryan Gupta, Aksh Goyal, Naveen Bansal'),('cp','lastModifiedBy','DeadlineDesk Team')]:
    q='{'+ns[prefix]+'}'+key
    element=root.find(q)
    if element is None: element=ET.SubElement(root,q)
    element.text=value
   data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
  out.writestr(info,data)
os.replace(p+'.metadata',p)
`,candidate],{stdio:'inherit'});
await fs.mkdir(path.join(TMP,'validated'),{recursive:true});
const buildId=Date.now();
const finalPath=path.join(TMP,'validated',`validated-${buildId}.pptx`);
await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath,
 pythonExecutable:path.join(RUNTIME,'python/bin/python3'),
 integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
 explicitTotalSlideCount:16,fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,
 receiptPath:path.join(TMP,`validation-${buildId}.json`)});
await fs.copyFile(finalPath,path.join(OUT,'DeadlineDesk_Final_Presentation.pptx'));
try {
 const pdf=await presentation.export({format:'pdf'});
 await fs.writeFile(path.join(OUT,'DeadlineDesk_Final_Presentation.pdf'),new Uint8Array(await pdf.arrayBuffer()));
} catch(error) {
 console.warn(`Native PDF exporter unavailable (${error.message}). Converting the validated PPTX with bundled LibreOffice.`);
 execFileSync(path.join(RUNTIME,'bin/override/soffice'),['--headless','--convert-to','pdf','--outdir',OUT,path.join(OUT,'DeadlineDesk_Final_Presentation.pptx')],{stdio:'inherit',timeout:60000});
}
execFileSync(path.join(RUNTIME,'python/bin/python3'),['-c',`
import os,sys
from pypdf import PdfReader,PdfWriter
p=sys.argv[1]
w=PdfWriter(clone_from=PdfReader(p))
w.add_metadata({'/Title':'DeadlineDesk Final Project Presentation','/Author':'Aryan Gupta, Aksh Goyal, Naveen Bansal','/Subject':'UCS503P final evaluation, 1 December 2026'})
with open(p+'.metadata','wb') as f: w.write(f)
os.replace(p+'.metadata',p)
`,path.join(OUT,'DeadlineDesk_Final_Presentation.pdf')],{stdio:'inherit'});
// Previews show the delivered PDF, including the conversion renderer's typography.
execFileSync('pdftoppm',['-r','144','-png',path.join(OUT,'DeadlineDesk_Final_Presentation.pdf'),path.join(OUT,'slides/slide')],{stdio:'inherit',timeout:60000});
await fs.writeFile(path.join(TMP,'slides.json'),JSON.stringify(specs,null,2)+'\n');
await fs.writeFile(path.join(OUT,'README.md'),`# Final project presentation\n\n[View the PDF](DeadlineDesk_Final_Presentation.pdf) · [Editable PowerPoint](DeadlineDesk_Final_Presentation.pptx) · [Deck source](https://github.com/aryanorastar/ucs503p-202627-deadlinedesk/blob/master/scripts/build_final_presentation.mjs)\n\nEvaluation: **1 December 2026, 8:00 AM, Lab 105**. The presentation follows the required order: Introduction, Background, Problem Statement, Your Solution, Results.\n\nThe 16 slides cover the implemented application, eight UML types, schedule, 36 passing automated cases and the demonstration setup. The public application uses a temporary tunnel; see the [current live demo instructions](../../live-demo.md) for availability and restart details.\n\n## Slide previews\n\n${specs.map((s,i)=>`### ${i+1}. ${s.title}\n\n${s.section}\n\n![Slide ${i+1}: ${s.title}](slides/slide-${String(i+1).padStart(2,'0')}.png)`).join('\n\n')}\n`);
console.log(`Saved ${presentation.slides.items.length} slides, PDF, validated PPTX and PNG previews in ${OUT}`);
