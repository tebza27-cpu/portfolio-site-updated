from pathlib import Path
from zipfile import ZipFile

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).parent
STATIC = ROOT / "static"
OUTPUT = STATIC / "Mokhele_IT_Solutions_Professional_Proposal_Images_2026.pptx"
DESIGNER = STATIC / "Designer (1).png"
INVESTOR_SOURCE = STATIC / "business_presentation_investor_11_oct_2026_Latest_Update.pptx"
SOURCE_IMAGES = ROOT / "_presentation_images"

W = Inches(13.333)
H = Inches(7.5)

NAVY = RGBColor(9, 25, 46)
DEEP_BLUE = RGBColor(8, 42, 79)
BLUE = RGBColor(19, 150, 236)
PALE_BLUE = RGBColor(167, 205, 231)
INK = RGBColor(27, 39, 53)
SLATE = RGBColor(91, 109, 141)
MIST = RGBColor(234, 234, 237)
WHITE = RGBColor(255, 255, 255)
GREEN = RGBColor(51, 166, 126)


def set_fill(shape, color, transparency=0):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.fill.transparency = transparency


def set_line(shape, color, width=1, transparency=0):
    shape.line.color.rgb = color
    shape.line.width = Pt(width)
    shape.line.transparency = transparency


def rect(slide, x, y, w, h, color, radius=False, transparency=0, line=None):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, x, y, w, h)
    set_fill(shape, color, transparency)
    if line:
        set_line(shape, line)
    else:
        shape.line.fill.background()
    return shape


def text(slide, value, x, y, w, h, size=16, color=INK, bold=False,
         font="Aptos", align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP,
         margin=0.04, spacing=1.08):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(margin)
    tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin)
    tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = spacing
    run = p.add_run()
    run.text = value
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def rich_text(slide, lines, x, y, w, h, size=16, color=INK, bullet_color=BLUE,
              gap=5, font="Aptos"):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    for index, item in enumerate(lines):
        p = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        p.text = item
        p.font.name = font
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.space_after = Pt(gap)
        p.level = 0
        p._p.get_or_add_pPr().insert(0, p._p._new_buChar())
        p._p.pPr[0].set("char", "•")
    return box


def add_image(slide, path, x, y, w, h):
    with Image.open(path) as image:
        image_ratio = image.width / image.height
    box_ratio = w / h
    picture = slide.shapes.add_picture(str(path), x, y, w, h)
    if image_ratio > box_ratio:
        visible_width = box_ratio / image_ratio
        crop = (1 - visible_width) / 2
        picture.crop_left = crop
        picture.crop_right = crop
    elif image_ratio < box_ratio:
        visible_height = image_ratio / box_ratio
        crop = (1 - visible_height) / 2
        picture.crop_top = crop
        picture.crop_bottom = crop
    return picture


def extract_source_images():
    SOURCE_IMAGES.mkdir(exist_ok=True)
    with ZipFile(INVESTOR_SOURCE) as archive:
        for name in archive.namelist():
            if name.startswith("ppt/media/image") and name.lower().endswith((".jpg", ".jpeg", ".png")):
                target = SOURCE_IMAGES / Path(name).name
                target.write_bytes(archive.read(name))


def source_image(number):
    return SOURCE_IMAGES / f"image{number}.jpg"


def image_panel(slide, image_path, x, y, w, h, label=None):
    rect(slide, x, y, w, h, NAVY, radius=True)
    add_image(slide, image_path, x + Inches(0.06), y + Inches(0.06), w - Inches(0.12), h - Inches(0.12))
    if label:
        rect(slide, x + Inches(0.18), y + h - Inches(0.5), Inches(1.68), Inches(0.31), NAVY, radius=True, transparency=12)
        text(slide, label.upper(), x + Inches(0.18), y + h - Inches(0.445), Inches(1.68), Inches(0.17), size=7.5, color=WHITE, bold=True, align=PP_ALIGN.CENTER, spacing=1.0)


def base(slide, number, section, dark=False):
    if dark:
        rect(slide, Inches(0), Inches(0), W, H, NAVY)
        footer_color = PALE_BLUE
    else:
        rect(slide, Inches(0), Inches(0), W, H, MIST)
        footer_color = SLATE
        rect(slide, Inches(0), Inches(0), Inches(0.16), H, BLUE)
    text(slide, section.upper(), Inches(0.64), Inches(0.34), Inches(5.4), Inches(0.24),
         size=9, color=footer_color, bold=True, font="Aptos", spacing=1.0)
    text(slide, f"MOKHELE IT SOLUTIONS   /   {number:02d}", Inches(10.2), Inches(7.08), Inches(2.45), Inches(0.2),
         size=8, color=footer_color, bold=True, align=PP_ALIGN.RIGHT, spacing=1.0)


def title(slide, heading, subheading=None, dark=False):
    text(slide, heading, Inches(0.64), Inches(0.83), Inches(8.8), Inches(0.78),
         size=30, color=WHITE if dark else NAVY, bold=True, font="Aptos Display", spacing=0.95)
    if subheading:
        text(slide, subheading, Inches(0.68), Inches(1.66), Inches(8.7), Inches(0.45),
             size=12, color=PALE_BLUE if dark else SLATE, font="Aptos", spacing=1.0)


def pill(slide, label, x, y, w, color=BLUE, text_color=WHITE):
    rect(slide, x, y, w, Inches(0.34), color, radius=True)
    text(slide, label.upper(), x, y + Inches(0.02), w, Inches(0.24), size=8,
         color=text_color, bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE, spacing=1.0)


def metric(slide, value, label, x, y, w, dark=False, accent=BLUE):
    text(slide, value, x, y, w, Inches(0.54), size=25, color=accent if dark else NAVY,
         bold=True, font="Aptos Display", spacing=0.95)
    text(slide, label, x, y + Inches(0.58), w, Inches(0.42), size=10,
         color=PALE_BLUE if dark else SLATE, spacing=1.0)


def card(slide, x, y, w, h, heading, body, accent=BLUE, dark=False):
    rect(slide, x, y, w, h, DEEP_BLUE if dark else WHITE, radius=True,
         transparency=0, line=RGBColor(35, 62, 91) if dark else RGBColor(215, 220, 227))
    rect(slide, x, y, Inches(0.07), h, accent, radius=True)
    text(slide, heading, x + Inches(0.24), y + Inches(0.2), w - Inches(0.42), Inches(0.34),
         size=14, color=WHITE if dark else NAVY, bold=True, font="Aptos Display")
    text(slide, body, x + Inches(0.24), y + Inches(0.68), w - Inches(0.44), h - Inches(0.85),
         size=10.5, color=PALE_BLUE if dark else INK, spacing=1.08)


def add_cover(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, Inches(0), Inches(0), W, H, NAVY)
    add_image(slide, DESIGNER, Inches(7.75), Inches(0), Inches(5.58), H)
    rect(slide, Inches(7.75), Inches(0), Inches(5.58), H, NAVY, transparency=38)
    rect(slide, Inches(0), Inches(0), Inches(8.6), H, NAVY)
    rect(slide, Inches(0.65), Inches(0.78), Inches(0.14), Inches(1.06), BLUE)
    text(slide, "MOKHELE", Inches(1.03), Inches(0.75), Inches(5.6), Inches(0.48), size=16,
         color=PALE_BLUE, bold=True, font="Aptos Display", spacing=1.0)
    text(slide, "IT SOLUTIONS", Inches(1.03), Inches(1.22), Inches(6.8), Inches(0.54), size=26,
         color=WHITE, bold=True, font="Aptos Display", spacing=1.0)
    text(slide, "Reliable technology support for small businesses and the people behind them.",
         Inches(1.03), Inches(2.25), Inches(5.7), Inches(1.1), size=25, color=WHITE,
         bold=True, font="Aptos Display", spacing=0.98)
    text(slide, "UPDATED BUSINESS PROPOSAL  /  2026", Inches(1.05), Inches(4.15), Inches(4.8), Inches(0.3),
         size=10, color=BLUE, bold=True, spacing=1.0)
    text(slide, "Sifiso Mokhele  |  Founder", Inches(1.05), Inches(4.62), Inches(4.8), Inches(0.35),
         size=14, color=PALE_BLUE, spacing=1.0)
    text(slide, "18 years of support experience  •  Remote and on-site delivery  •  South Africa",
         Inches(1.05), Inches(6.64), Inches(7.1), Inches(0.28), size=9, color=PALE_BLUE, spacing=1.0)
    text(slide, "01", Inches(12.45), Inches(7.02), Inches(0.35), Inches(0.2), size=8, color=PALE_BLUE, bold=True, align=PP_ALIGN.RIGHT)


def add_problem(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    base(slide, 2, "The opportunity")
    title(slide, "Small businesses need a dependable IT partner.", "Technology problems cost time, revenue, and confidence.")
    image_panel(slide, source_image(2), Inches(8.18), Inches(2.25), Inches(4.35), Inches(3.85), "The customer need")
    card(slide, Inches(0.72), Inches(2.32), Inches(6.9), Inches(1.02), "The friction", "Slow troubleshooting, unreliable devices, weak backups, and unclear digital processes pull owners away from growth.", accent=BLUE)
    card(slide, Inches(0.72), Inches(3.55), Inches(6.9), Inches(1.02), "The gap", "Teams with 1 to 50 employees need support but often cannot justify a full-time IT technician or enterprise contract.", accent=PALE_BLUE)
    card(slide, Inches(0.72), Inches(4.78), Inches(6.9), Inches(1.02), "The response", "Mokhele IT Solutions packages practical support, cloud guidance, and basic security into an affordable service.", accent=GREEN)
    text(slide, "The promise", Inches(0.72), Inches(6.28), Inches(1.7), Inches(0.3), size=11, color=BLUE, bold=True)
    text(slide, "Less downtime. More confidence. A clearer way to work.", Inches(2.05), Inches(6.2), Inches(6.2), Inches(0.48), size=20, color=NAVY, bold=True, font="Aptos Display")


def add_company(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    base(slide, 3, "The business")
    title(slide, "A lean service business built on earned trust.", "The founder's existing capability is the first asset.")
    image_panel(slide, source_image(1), Inches(8.18), Inches(2.25), Inches(4.35), Inches(3.85), "Built on experience")
    metric(slide, "18 years", "Support Analyst experience", Inches(0.72), Inches(2.45), Inches(2.6))
    metric(slide, "R2k–R5k", "Lean startup budget", Inches(3.72), Inches(2.45), Inches(2.6))
    metric(slide, "1–50", "Employee target businesses", Inches(0.72), Inches(3.85), Inches(2.6))
    metric(slide, "Remote + on-site", "Flexible delivery model", Inches(3.72), Inches(3.85), Inches(2.8))
    rect(slide, Inches(0.72), Inches(5.3), Inches(6.9), Inches(0.02), PALE_BLUE)
    text(slide, "Mission", Inches(0.72), Inches(5.58), Inches(1.35), Inches(0.3), size=11, color=BLUE, bold=True)
    text(slide, "Affordable, reliable IT support that solves problems quickly, improves productivity, and helps clients maintain secure IT environments.", Inches(2.0), Inches(5.5), Inches(5.55), Inches(0.72), size=15, color=NAVY, bold=True, font="Aptos Display", spacing=1.04)
    text(slide, "Home-based and remote support from South Africa, with on-site service where the client needs it.", Inches(0.72), Inches(6.55), Inches(7.1), Inches(0.3), size=10.5, color=SLATE)


def add_services(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    base(slide, 4, "The offer")
    title(slide, "Practical support across the moments that matter.", "A clear service menu makes it easy to buy help and easy to deliver it consistently.")
    services = [
        ("Everyday support", "Computer and laptop troubleshooting\nPerformance tune-ups\nVirus and malware removal", BLUE),
        ("Connected work", "Wi-Fi and network troubleshooting\nPrinter and email setup\nRemote support", PALE_BLUE),
        ("Cloud and continuity", "Microsoft 365 setup and administration\nBackup and recovery support\nUser account management", GREEN),
        ("Safer operations", "Basic cybersecurity assessments\nPhishing and password awareness\nDevice security checks", RGBColor(91, 92, 99)),
    ]
    image_panel(slide, source_image(3), Inches(8.18), Inches(2.25), Inches(4.35), Inches(3.85), "Practical service delivery")
    for i, (heading, body, accent) in enumerate(services):
        x = Inches(0.7 + (i % 2) * 3.55)
        y = Inches(2.38 + (i // 2) * 1.67)
        card(slide, x, y, Inches(3.25), Inches(1.35), heading, body, accent=accent)
    text(slide, "Delivery model", Inches(0.72), Inches(5.88), Inches(1.3), Inches(0.25), size=10, color=BLUE, bold=True)
    text(slide, "One-off support  →  Projects  →  Monthly support plans", Inches(2.05), Inches(5.82), Inches(5.85), Inches(0.36), size=15, color=NAVY, bold=True, font="Aptos Display")


def add_market(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    base(slide, 5, "The market")
    title(slide, "Start where trust already travels.", "A focused local market creates a practical path to the first ten recurring clients.")
    market = [
        ("Small businesses", "1–50 employees\nNo in-house IT team"),
        ("Professional offices", "Accountants, lawyers\nConsultants and practices"),
        ("Community organisations", "Churches and NGOs\nLocal service groups"),
        ("Home users", "Remote workers\nFamilies and entrepreneurs"),
    ]
    image_panel(slide, source_image(5), Inches(8.18), Inches(2.25), Inches(4.35), Inches(3.85), "The people we serve")
    for i, (heading, body) in enumerate(market):
        x = Inches(0.72)
        y = Inches(2.42 + i * 0.95)
        rect(slide, x, y, Inches(6.9), Inches(0.7), WHITE, radius=True, line=RGBColor(215, 220, 227))
        text(slide, f"0{i+1}", x + Inches(0.22), y + Inches(0.15), Inches(0.58), Inches(0.34), size=17, color=BLUE, bold=True, font="Aptos Display")
        text(slide, heading, x + Inches(1.0), y + Inches(0.12), Inches(2.1), Inches(0.25), size=12.5, color=NAVY, bold=True, font="Aptos Display")
        text(slide, body.replace("\n", "  /  "), x + Inches(3.05), y + Inches(0.17), Inches(3.55), Inches(0.25), size=10, color=SLATE)
    text(slide, "Acquisition starts with the founder's network: former colleagues, church members, friends, family, neighbours, and local business owners.", Inches(0.72), Inches(6.35), Inches(7.1), Inches(0.55), size=14, color=NAVY, bold=True, font="Aptos Display", spacing=1.0)


def add_pricing(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    base(slide, 6, "The model")
    title(slide, "A price ladder that turns help into continuity.", "Accessible entry points create trust; support plans create recurring revenue.")
    plans = [
        ("BRONZE", "R500", "per month", ["Remote support", "Monthly health check", "Email assistance"], BLUE),
        ("SILVER", "R1,000", "per month", ["Everything in Bronze", "Priority support", "Backup checks", "Device management"], PALE_BLUE),
        ("GOLD", "R2,000+", "per month", ["Unlimited support", "Microsoft 365 administration", "Security reviews", "Staff assistance"], GREEN),
    ]
    for i, (name, price, period, items, accent) in enumerate(plans):
        x = Inches(0.82 + i * 4.18)
        rect(slide, x, Inches(2.35), Inches(3.62), Inches(3.45), WHITE, radius=True, line=accent)
        rect(slide, x, Inches(2.35), Inches(3.62), Inches(0.12), accent, radius=True)
        text(slide, name, x + Inches(0.25), Inches(2.68), Inches(2.6), Inches(0.3), size=11, color=SLATE, bold=True)
        text(slide, price, x + Inches(0.25), Inches(3.13), Inches(2.6), Inches(0.56), size=26, color=NAVY, bold=True, font="Aptos Display")
        text(slide, period, x + Inches(0.28), Inches(3.75), Inches(2.5), Inches(0.22), size=9, color=SLATE)
        for j, item in enumerate(items):
            text(slide, "•  " + item, x + Inches(0.28), Inches(4.25 + j * 0.34), Inches(3.0), Inches(0.24), size=10, color=INK)
    text(slide, "Additional project pricing", Inches(0.84), Inches(6.25), Inches(2.2), Inches(0.25), size=10, color=BLUE, bold=True)
    text(slide, "Remote support R250–R500/hour  •  On-site R400–R700/hour  •  Microsoft 365 setup R1,000–R3,000  •  IT audit R1,500–R5,000", Inches(3.02), Inches(6.19), Inches(9.1), Inches(0.38), size=10.5, color=NAVY, bold=True)


def add_go_to_market(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    base(slide, 7, "The route to market")
    title(slide, "Earn the first five customers, then compound trust.", "A simple weekly rhythm keeps the business visible and the pipeline moving.")
    steps = [
        ("01", "Be findable", "WhatsApp Business, LinkedIn, Facebook, a simple website, and business cards."),
        ("02", "Start warm", "Ask the existing network for introductions and share a clear, human service message."),
        ("03", "Visit locally", "Offer a free initial IT health check to professional offices and small businesses."),
        ("04", "Follow through", "Document fixes, check back, request referrals, and invite clients onto a support plan."),
    ]
    image_panel(slide, source_image(4), Inches(8.18), Inches(2.25), Inches(4.35), Inches(3.85), "Trust is the advantage")
    for i, (number, heading, body) in enumerate(steps):
        y = Inches(2.38 + i * 0.98)
        text(slide, number, Inches(0.78), y, Inches(0.65), Inches(0.42), size=20, color=BLUE, bold=True, font="Aptos Display")
        text(slide, heading, Inches(1.65), y + Inches(0.02), Inches(2.1), Inches(0.28), size=13, color=NAVY, bold=True, font="Aptos Display")
        text(slide, body, Inches(3.55), y + Inches(0.02), Inches(3.85), Inches(0.45), size=9.5, color=SLATE, spacing=1.05)
    rect(slide, Inches(0.78), Inches(6.38), Inches(7.05), Inches(0.42), DEEP_BLUE, radius=True)
    text(slide, "A free first conversation lowers the barrier; consistent follow-up turns a good first experience into a relationship.", Inches(0.98), Inches(6.49), Inches(6.65), Inches(0.18), size=9.5, color=WHITE, bold=True, align=PP_ALIGN.CENTER)


def add_operations(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    base(slide, 8, "The operating system")
    title(slide, "Small overhead. Repeatable delivery.", "The first version of the business can run on tools and habits the founder already understands.")
    card(slide, Inches(0.72), Inches(2.4), Inches(3.7), Inches(2.3), "Launch kit", "Reliable laptop\nSmartphone and stable internet\nRemote-support software\nBasic toolkit and documentation", accent=BLUE)
    card(slide, Inches(4.82), Inches(2.4), Inches(3.7), Inches(2.3), "Client workflow", "Discover\nDiagnose\nResolve\nDocument\nFollow up", accent=PALE_BLUE)
    card(slide, Inches(8.92), Inches(2.4), Inches(3.7), Inches(2.3), "Control points", "Clear quotations\nService records\nBackup verification\nInvoicing and scheduling\nCompliance research", accent=GREEN)
    text(slide, "Estimated lean setup", Inches(0.74), Inches(5.35), Inches(2.2), Inches(0.3), size=11, color=BLUE, bold=True)
    text(slide, "Registration R500–R1,000  •  Business cards R300  •  Marketing materials R500  •  Basic toolkit R500  •  Internet and communication: existing", Inches(2.48), Inches(5.28), Inches(9.7), Inches(0.52), size=12, color=NAVY, bold=True, font="Aptos Display")


def add_financials(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    base(slide, 9, "The economics")
    title(slide, "A conservative base case with visible upside.", "The business can launch lean, prove demand, and add capacity as recurring revenue grows.")
    rect(slide, Inches(0.72), Inches(2.35), Inches(5.62), Inches(3.65), DEEP_BLUE, radius=True)
    text(slide, "YEAR 1 BASE CASE", Inches(1.02), Inches(2.68), Inches(2.7), Inches(0.26), size=10, color=PALE_BLUE, bold=True)
    metric(slide, "10", "recurring business clients", Inches(1.02), Inches(3.18), Inches(2.3), dark=True, accent=BLUE)
    metric(slide, "R10k–R20k", "monthly revenue target", Inches(3.82), Inches(3.18), Inches(2.05), dark=True, accent=GREEN)
    text(slide, "Milestones", Inches(1.02), Inches(4.7), Inches(1.2), Inches(0.24), size=10, color=PALE_BLUE, bold=True)
    text(slide, "Months 1–3: register, launch presence, win first 3 customers\nMonths 4–6: reach 5–10 regular clients, introduce plans\nMonths 7–12: reach 15–20 clients, add cloud and security services", Inches(1.02), Inches(5.02), Inches(4.75), Inches(0.78), size=9.5, color=WHITE, spacing=1.05)
    rect(slide, Inches(6.75), Inches(2.35), Inches(5.82), Inches(3.65), WHITE, radius=True, line=RGBColor(215, 220, 227))
    text(slide, "GROWTH CASE", Inches(7.05), Inches(2.68), Inches(2.7), Inches(0.26), size=10, color=BLUE, bold=True)
    metric(slide, "20", "active clients", Inches(7.05), Inches(3.18), Inches(2.3), accent=BLUE)
    metric(slide, "R30k", "monthly sales at R1,500 average", Inches(9.85), Inches(3.18), Inches(2.25), accent=GREEN)
    text(slide, "Growth levers", Inches(7.05), Inches(4.7), Inches(1.2), Inches(0.24), size=10, color=BLUE, bold=True)
    text(slide, "•  More Silver and Gold plans\n•  Microsoft 365 consulting\n•  Cybersecurity awareness training\n•  Computer upgrades and referral partnerships", Inches(7.05), Inches(5.02), Inches(4.7), Inches(0.85), size=10.5, color=INK, spacing=1.04)


def add_roadmap(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    base(slide, 10, "The roadmap")
    title(slide, "Twelve months from launch to a trusted local partner.", "The plan is staged so each milestone funds the next layer of capability.")
    phases = [
        ("Q1", "Launch", "Register the business\nSet up digital presence\nWin first 3 customers", BLUE),
        ("Q2", "Stabilise", "Reach 5–10 clients\nIntroduce support plans\nStandardise workflows", PALE_BLUE),
        ("Q3", "Expand", "Add Microsoft 365\nOffer security awareness\nBuild referral partnerships", GREEN),
        ("Q4", "Scale", "Reach 15–20 clients\nImprove service reliability\nPrepare for sustainable growth", RGBColor(91, 92, 99)),
    ]
    image_panel(slide, source_image(6), Inches(8.18), Inches(2.25), Inches(4.35), Inches(3.85), "The long-term vision")
    rect(slide, Inches(1.12), Inches(3.2), Inches(0.08), Inches(2.65), PALE_BLUE)
    for i, (quarter, heading, body, accent) in enumerate(phases):
        y = Inches(2.38 + i * 0.98)
        rect(slide, Inches(0.94), y + Inches(0.1), Inches(0.45), Inches(0.45), accent, radius=True)
        text(slide, quarter, Inches(1.62), y, Inches(0.6), Inches(0.24), size=10, color=accent, bold=True)
        text(slide, heading, Inches(2.3), y, Inches(1.4), Inches(0.3), size=13, color=NAVY, bold=True, font="Aptos Display")
        text(slide, body.replace("\n", "  /  "), Inches(3.7), y + Inches(0.02), Inches(3.55), Inches(0.42), size=9.5, color=SLATE, spacing=1.0)
    text(slide, "Three-year vision", Inches(0.78), Inches(6.35), Inches(1.65), Inches(0.25), size=10, color=BLUE, bold=True)
    text(slide, "A trusted, growing IT support business with recurring clients and a strong reputation across local communities and small enterprises.", Inches(2.35), Inches(6.28), Inches(5.3), Inches(0.45), size=12.5, color=NAVY, bold=True, font="Aptos Display")


def add_next_step(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, Inches(0), Inches(0), W, H, NAVY)
    add_image(slide, source_image(7), Inches(7.15), Inches(0), Inches(6.18), H)
    rect(slide, Inches(7.15), Inches(0), Inches(6.18), H, NAVY, transparency=30)
    rect(slide, Inches(0), Inches(0), Inches(8.6), H, NAVY)
    text(slide, "THE NEXT MOVE", Inches(0.78), Inches(0.8), Inches(2.6), Inches(0.28), size=10, color=BLUE, bold=True)
    text(slide, "Package the expertise.\nProve the value.\nBuild the relationship.", Inches(0.78), Inches(1.6), Inches(6.35), Inches(2.05), size=32, color=WHITE, bold=True, font="Aptos Display", spacing=0.96)
    text(slide, "Mokhele IT Solutions is designed to begin with a low-risk launch and grow through reliable service, recurring support plans, and the trust of every client served.", Inches(0.82), Inches(4.2), Inches(5.85), Inches(1.05), size=16, color=PALE_BLUE, font="Aptos Display", spacing=1.05)
    rect(slide, Inches(0.82), Inches(5.83), Inches(2.28), Inches(0.48), BLUE, radius=True)
    text(slide, "LET'S BUILD IT", Inches(0.82), Inches(5.96), Inches(2.28), Inches(0.2), size=10, color=WHITE, bold=True, align=PP_ALIGN.CENTER, spacing=1.0)
    text(slide, "Sifiso Mokhele  |  +27 64 937 3653  |  info@mokheleitsolutions.co.za\nwww.mokheleitsolutions.co.za", Inches(0.82), Inches(6.7), Inches(6.7), Inches(0.42), size=9, color=PALE_BLUE, spacing=1.0)
    text(slide, "11", Inches(12.45), Inches(7.02), Inches(0.35), Inches(0.2), size=8, color=PALE_BLUE, bold=True, align=PP_ALIGN.RIGHT)


def build():
    extract_source_images()
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    add_cover(prs)
    add_problem(prs)
    add_company(prs)
    add_services(prs)
    add_market(prs)
    add_pricing(prs)
    add_go_to_market(prs)
    add_operations(prs)
    add_financials(prs)
    add_roadmap(prs)
    add_next_step(prs)
    prs.core_properties.title = "Mokhele IT Solutions - Updated Business Proposal"
    prs.core_properties.subject = "IT support and technology services business proposal"
    prs.core_properties.author = "Sifiso Mokhele"
    prs.core_properties.keywords = "IT support, Microsoft 365, cybersecurity, small business"
    prs.save(OUTPUT)
    print(f"Created {OUTPUT}")
    print(f"Slides: {len(prs.slides)}")


if __name__ == "__main__":
    build()