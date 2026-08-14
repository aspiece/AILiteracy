from __future__ import annotations

import html
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlencode


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_canvas_source"
LESSONS = ROOT / "lessons"
ASSETS = ROOT / "assets"
FORM_LINKS_PATH = ROOT / "form-links.json"
LESSON_QUESTION_BANK_PATH = ROOT / "lesson-page-questions.json"

VIDEO_TITLES = {
    "DC8Bpa1UWek": "AI Literacy: What is AI?",
    "VL3WIlrWd5o": "AI Literacy: How Does Generative AI Work?",
    "dpRK9y7fuJA": "AI Literacy: What is Generative AI?",
    "BQosMFvT0aU": "AI Literacy: What is an AI Chatbot?",
    "IFoEcetEdVQ": "AI Literacy: How to Write Good Prompts",
    "lKsuxtGJSKA": "AI Literacy: Refining Chatbot Results",
    "42pF4FP152Y": "AI Literacy: Creating AI-Generated Images",
    "UYplvFrfR9I": "AI Literacy: How Do AI Image Generators Work?",
    "G3YHo2vsXZk": "AI Literacy: Recognizing AI-Generated Images",
    "VwAlOUE4K7M": "AI Literacy: What is Algorithmic Bias?",
    "_WpTWizRGys": "AI Literacy: Recognizing Algorithmic Bias",
    "vyTqZQ7VArE": "AI Literacy: How to Minimize Algorithmic Bias",
    "MIHz5bji-aI": "AI Literacy: What Should I Share with AI?",
    "wbtX_iATxwQ": "AI Literacy: Privacy and AI",
    "v4KgddiHSIM": "AI Literacy: Controlling My Data",
    "fv2e58rgI9k": "AI Literacy: AI and Ethics",
    "Oyw3xt_IeXg": "AI Literacy: Copyright and AI",
    "Q9CHETXIagI": "AI Literacy: Ethical Content Creation with AI",
    "g_FeQh9oYuY": "AI Literacy: AI and the Future of Education",
    "kgeLvlCCFRo": "AI Literacy: AI and the Future of Work",
    "olf-MrpLZCY": "AI Literacy: AI and the Future of Society",
}

VIDEO_FOCUSES = {
    "DC8Bpa1UWek": "Watch for one example of a task that people designed AI to do.",
    "VL3WIlrWd5o": "Watch for one way people help train a generative AI model.",
    "dpRK9y7fuJA": "Watch for how generative AI uses patterns to create new content.",
    "BQosMFvT0aU": "Watch for how a chatbot uses a prompt to produce a response.",
    "IFoEcetEdVQ": "Watch for one prompt detail that makes an AI response more useful.",
    "lKsuxtGJSKA": "Watch for one way to improve a chatbot response after its first answer.",
    "42pF4FP152Y": "Watch for how details in a prompt change an AI-generated image.",
    "UYplvFrfR9I": "Watch for how training examples help an image generator learn patterns.",
    "G3YHo2vsXZk": "Watch for one way to verify an image when visual clues are not enough.",
    "VwAlOUE4K7M": "Watch for one way training data can create an unfair AI result.",
    "_WpTWizRGys": "Watch for one question that can reveal bias in an AI result.",
    "vyTqZQ7VArE": "Watch for one step people can take to reduce unfair AI results.",
    "MIHz5bji-aI": "Watch for one type of information that should not be entered into an AI tool.",
    "wbtX_iATxwQ": "Watch for what may happen to information after it enters an AI tool.",
    "v4KgddiHSIM": "Watch for one action that can reduce a privacy risk.",
    "fv2e58rgI9k": "Watch for one ethical question to ask before using AI-created work.",
    "Oyw3xt_IeXg": "Watch for one reason to check permission before using AI-assisted content.",
    "Q9CHETXIagI": "Watch for one way a creator should explain how AI helped with a project.",
    "g_FeQh9oYuY": "Watch for one reason your own knowledge still matters when you use AI.",
    "kgeLvlCCFRo": "Watch for one human skill that may become more valuable as AI changes work.",
    "olf-MrpLZCY": "Watch for one AI challenge that may affect groups of people differently.",
}

# Source of truth: "AI Literacy Videos" alignment spreadsheet supplied by the
# course author. Each instructional step receives one unique Michigan Virtual
# video and its matching language alternatives.
STEP_VIDEOS = {
    "1.2": ("dpRK9y7fuJA", "E1S7b1TFUDA", "V03T4s4p9Eg"),
    "1.3": ("VL3WIlrWd5o", "nbZkVY0vMmg", "Fk67dmrhHRk"),
    "1.4": ("DC8Bpa1UWek", "SxvVF5W0zMI", "0Vs6avs5eL8"),
    "2.2": ("BQosMFvT0aU", "lnde8dANViY", "FXYe6CHTRLk"),
    "2.3": ("IFoEcetEdVQ", "kPZzaguQWUo", "SnNfHBjdfn0"),
    "2.4": ("lKsuxtGJSKA", "kir2InOp_mA", "VOvIY_9S1LY"),
    "3.2": ("42pF4FP152Y", "v6GR-MxtH6w", "-kJqEG-Pwpw"),
    "3.3": ("UYplvFrfR9I", "xt6g2eW-kuA", "IFGONKoeUR8"),
    "3.4": ("G3YHo2vsXZk", "z78Qm5HZTa8", "Sy0uubytJmY"),
    "4.2": ("VwAlOUE4K7M", "gXl0ud9talY", "detnBXmY0E0"),
    "4.3": ("_WpTWizRGys", "oLeV1eQWNNU", "q9Lkx0h87Aw"),
    "4.4": ("vyTqZQ7VArE", "vz6Mrya_XlQ", "WilqtfYlI_8"),
    "5.2": ("MIHz5bji-aI", "ZmF-ECcEtrA", "qK0MGPVnwgk"),
    "5.3": ("wbtX_iATxwQ", "wNLJuaserYo", "KvUtJNfB75I"),
    "5.4": ("v4KgddiHSIM", "2y4096oxQB0", "wQsSr1mjTTQ"),
    "6.2": ("fv2e58rgI9k", "yxqRty_6aaw", "Yxn3bhYwBII"),
    "6.3": ("Oyw3xt_IeXg", "0cqQ6eCOsc4", "Lv80Hkkq0EA"),
    "6.4": ("Q9CHETXIagI", "AZ81cSrFPFw", "-DBXdvct6l8"),
    "7.2": ("g_FeQh9oYuY", "eq90NsLxP0A", "EcZ6rFFw3pw"),
    "7.3": ("kgeLvlCCFRo", "QAUB-lN47hg", "TnRsNw4Gkcw"),
    "7.4": ("olf-MrpLZCY", "5uxmBz0Lcy8", "G61viZr5a3U"),
}

STEP_TITLES = {
    "1.2": "Connect & Learn: What Generative AI Can and Cannot Do",
    "1.3": "Learn: How Generative AI Learns from Data",
    "1.4": "Learn: AI Types and Human Responsibility",
    "2.2": "Connect & Learn: How AI Chatbots Create Responses",
    "2.3": "Learn: Write Stronger AI Prompts",
    "2.4": "Learn: Check and Improve AI Responses",
    "3.2": "Connect & Learn: Creating and Questioning AI-Generated Images",
    "3.3": "Learn: How AI Image Generators Create Images",
    "3.4": "Learn: Verify AI-Generated Media",
    "4.2": "Connect & Learn: Is This AI Result Fair? How Bias Begins",
    "4.3": "Learn: Recognize Algorithmic Bias",
    "4.4": "Learn: Reduce Bias and Respond Responsibly",
    "5.2": "Connect & Learn: What Information Is Safe to Share with AI?",
    "5.3": "Learn: What Happens to Data Entered into AI",
    "5.4": "Learn: Control Your Data and Reduce Privacy Risks",
    "6.2": "Connect & Learn: Ethics and Human Responsibility",
    "6.3": "Learn: Copyright and Permission in AI-Created Work",
    "6.4": "Learn: Create Responsibly with AI",
    "7.2": "Connect & Learn: Knowledge, Learning, and Future Possibilities",
    "7.3": "Learn: Task Change, Augmentation, and Human-Led Work",
    "7.4": "Learn: Societal, Access, and Environmental Impacts",
}

VIDEO_TRANSCRIPTS = {
    "DC8Bpa1UWek": "https://docs.google.com/document/d/1bJu24L53SVnFYWGdJ9EyUS69uW_dMMAxeQr3iZf8rgI/edit",
    "dpRK9y7fuJA": "https://docs.google.com/document/d/1veh2GBHT8hUwhf26V3sDMQMalKur3cAkbS3hdLtOj5Q/edit",
    "VL3WIlrWd5o": "https://docs.google.com/document/d/14uXuzVANLbcFazOOoyXBesAP3Bvm23fQ8I1se1jMRqw/edit",
    "IFoEcetEdVQ": "https://docs.google.com/document/d/10OeD9GDiUXZtuEfeYVUFC_5-XFvJ_MUmaDmbyfwbVg8/edit",
    "UYplvFrfR9I": "https://docs.google.com/document/d/1c39kGzCvVcNHqoX0YG3l7jwByRBCKLhXTe6zCi4-ze8/edit",
    "G3YHo2vsXZk": "https://docs.google.com/document/d/1SpztDGHw9h7CdNZ0j4qyv0FEh39uFcFTcBrmlIaMz8k/edit",
    "_WpTWizRGys": "https://docs.google.com/document/d/1svKP5hv_xVMULKPtoQN8vv_QsjFOH8gIkoOgGpnD7vA/edit",
    "vyTqZQ7VArE": "https://docs.google.com/document/d/1EATbkhtmBiu3GhvA41N7WarFK2LdGn8-yRbBDM2EEZ4/edit",
    "MIHz5bji-aI": "https://docs.google.com/document/d/1hJM9vL8FkDUeVSaOZcDe8eGMYhqbQXei90Fr3IRI8AQ/edit",
    "wbtX_iATxwQ": "https://docs.google.com/document/d/1WCa-c649fnm9kIa1lAXPSvPEm7p3Y74js5Y06FGRjX8/edit",
    "v4KgddiHSIM": "https://docs.google.com/document/d/1mT47vgksqkFXahYYWBMgQyJooY0pKpsXEFqOgcV_nNM/edit",
    "fv2e58rgI9k": "https://docs.google.com/document/d/1-tsrZQlpzLNjY3QJXAZ71lOM9ovbZFJc2tHS6ejdng4/edit",
    "Oyw3xt_IeXg": "https://docs.google.com/document/d/1sHKDQcMXVrM0_T6bsCdKTNwhlReqctvNoEuxurNO6v0/edit",
    "Q9CHETXIagI": "https://docs.google.com/document/d/14HdtekAsmHVqL2_m0QAQKdCgHMDuHjB1e5CyArodz90/edit",
    "g_FeQh9oYuY": "https://docs.google.com/document/d/1hq8UFnfWuMZtSVEkWkJai1CZb02qJUwIo9FT0N4BNUQ/edit",
    "kgeLvlCCFRo": "https://docs.google.com/document/d/1H31vA93t08toKWsn9VXpbLSu8dJcx3CIwjAb3Myotzg/edit",
    "olf-MrpLZCY": "https://docs.google.com/document/d/1q1sMcRo71j9CrwfDMbXR4ggznccjlEL_Q311GYgjfpo/edit",
}


def align_video_to_step(value: str, step_label: str) -> str:
    """Enforce the spreadsheet's primary and translated video alignment."""
    if step_label not in STEP_VIDEOS:
        return value
    video_id, spanish_id, arabic_id = STEP_VIDEOS[step_label]
    iframe = re.search(r'<iframe\b[^>]*youtube-nocookie\.com/embed/[^>]+></iframe>', value, flags=re.I)
    if not iframe:
        return value
    replacement = re.sub(r'src="[^"]+"', f'src="https://www.youtube-nocookie.com/embed/{video_id}?cc_load_policy=1"', iframe.group(0), count=1, flags=re.I)
    if re.search(r'title="[^"]*"', replacement, flags=re.I):
        replacement = re.sub(r'title="[^"]*"', f'title="{html.escape(VIDEO_TITLES[video_id])}"', replacement, count=1, flags=re.I)
    else:
        replacement = replacement.replace("<iframe", f'<iframe title="{html.escape(VIDEO_TITLES[video_id])}"', 1)
    value = value[:iframe.start()] + replacement + value[iframe.end():]

    # Keep an existing English transcript when it belongs to the aligned video;
    # otherwise provide the video's captioned English view.
    after_iframe = iframe.start() + len(replacement)
    access = re.match(r'(</div>\s*)(<(?:div|p|nav)\b[^>]*>.*?</(?:div|p|nav)>)', value[after_iframe:], flags=re.I | re.S)
    english = VIDEO_TRANSCRIPTS.get(video_id, f'https://www.youtube.com/watch?v={video_id}&cc_load_policy=1')
    english_label = "English transcript" if video_id in VIDEO_TRANSCRIPTS else "Watch with English captions"
    if access:
        old_access = access.group(2)
        new_access = (
            '<div class="video-access">'
            f'<a href="{html.escape(english)}" target="_blank" rel="noopener">{english_label}</a> | '
            f'<a href="https://www.youtube.com/watch?v={spanish_id}" target="_blank" rel="noopener">Watch in Spanish</a> | '
            f'<a href="https://www.youtube.com/watch?v={arabic_id}" target="_blank" rel="noopener">Watch in Arabic</a></div>'
        )
        start = after_iframe + len(access.group(1))
        value = value[:start] + new_access + value[start + len(old_access):]
    return set_video_focus(value)


def set_video_focus(value: str) -> str:
    """Give every primary lesson video one clear focus in its preceding callout."""
    # Remove older multi-item focus panels. Their most important idea is folded
    # into the single, immediately actionable prompt below.
    value = re.sub(
        r'<div[^>]*>\s*<h3[^>]*>.*?Viewing Focus</h3>.*?</ol>\s*</div>',
        "",
        value,
        flags=re.I | re.S,
    )
    value = re.sub(
        r'<div[^>]*>\s*<p[^>]*>Viewing Focus:</p>\s*<p[^>]*>.*?</p>\s*</div>',
        "",
        value,
        flags=re.I | re.S,
    )
    for video_id, focus in VIDEO_FOCUSES.items():
        iframe_pattern = re.compile(
            rf'<iframe\b[^>]*src="[^"]*{re.escape(video_id)}[^"]*"[^>]*>',
            flags=re.I,
        )
        search_from = 0
        while match := iframe_pattern.search(value, search_from):
            window_start = max(0, match.start() - 1800)
            window = value[window_start:match.start()]
            prompt_markers = list(re.finditer(
                r"(?:Your next move:</strong>|<h3[^>]*>.*?Your Next Move</h3>)",
                window,
                flags=re.I | re.S,
            ))
            if not prompt_markers:
                search_from = match.end()
                continue
            marker = prompt_markers[-1]
            prompt_end = window_start + marker.end()
            if marker.group(0).lower().startswith("<h3"):
                paragraph_open = re.search(r"<p[^>]*>", value[prompt_end:match.start()], flags=re.I)
                if not paragraph_open:
                    search_from = match.end()
                    continue
                prompt_end += paragraph_open.end()
            paragraph_end = value.find("</p>", prompt_end, match.start())
            if paragraph_end < 0:
                search_from = match.end()
                continue
            value = value[:prompt_end] + " " + focus + value[paragraph_end:]
            search_from = match.end() + len(focus)
    return value

LESSON_TITLES = {
    1: "Humans Behind AI: How People Shape What AI Does",
    2: "Prompt Like a Pro: The AI Test Lab",
    3: "Verify Before You Trust: Auditing AI Media",
    4: "The Bias Trap: Is AI Really Fair?",
    5: "Privacy Shield: What NOT to Share with AI",
    6: "Create with Integrity: Ethics, Copyright, and Original Work",
    7: "Level Up: AI Skills for Your Future Career",
    8: "Build, Test, Improve: Model Rescue and Certification",
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def children(node, name):
    return [child for child in node.iter() if local_name(child.tag) == name]


def first_text(node, name, default=""):
    found = next((x for x in node.iter() if local_name(x.tag) == name), None)
    return (found.text or default).strip() if found is not None else default


def positive_varequals(node, negated=False):
    values = []
    for child in node:
        child_name = local_name(child.tag)
        if child_name == "not":
            values.extend(positive_varequals(child, True))
        elif child_name == "varequal" and not negated and (child.text or "").strip():
            values.append((child.text or "").strip())
        else:
            values.extend(positive_varequals(child, negated))
    return values


def clean_fragment(value: str) -> str:
    value = html.unescape(value or "")
    reading_level_replacements = (
        (
            "Before moving on, consider: If you use AI to generate an outline and then write the entire essay yourself, what specific AI disclosure (if any) is required by your class rules?",
            "Before moving on, think about this question: If AI makes an outline but you write the essay, do your class rules require you to explain how you used AI?",
        ),
        (
            "Model Refinement (Improved Model): Fix mislabeled data or add better examples, then train the improved model to make it more accurate.",
            "Model Refinement (Improved Model): Fix labels that are wrong or add better examples. Then train the model again and check whether it improved.",
        ),
        (
            "Explain why an approved tool or privacy setting does not remove the need for minimum-necessary data and accountable human approval.",
            "Explain why an approved tool or privacy setting is not enough by itself. People must still use only the data they need and get approval from a responsible person.",
        ),
        (
            "Viewing focus: Identify one possible benefit, one possible harm or cost, one group that may experience the impact differently, and one way people can guide the outcome.",
            "While you watch, find one benefit and one possible harm or cost. Name one group that may be affected in a different way. Then describe one way people can guide the result.",
        ),
        (
            "A designer submits a promotional flyer containing stock artwork, but forgot to record the image license source or verify if commercial use is permitted.",
            "A designer submits an ad with stock artwork. The designer did not record the image license or check whether the image may be used for business.",
        ),
        (
            "Viewing focus: Identify one workplace task AI might automate, one task AI might assist, one responsibility people must continue to lead, and one skill workers may need to strengthen.",
            "While you watch, find one task AI might do and one task it might help with. Name one duty people must still lead and one skill workers may need to build.",
        ),
        (
            "Imagine this: You ask an AI image tool to create a picture of a \"successful team.\" Every single person it draws is young, wearing a formal suit, and standing in a tall office building.",
            "Imagine that you ask AI to make a picture of a \"successful team.\" It shows only young people in suits inside a tall office building.",
        ),
        (
            "Work through all analysis sections in the document, evaluating privacy risks and drafting a safer alternative.",
            "Complete every part of the document. Find the privacy risks and write a safer choice.",
        ),
        (
            "Main Rule: Respect creative rights and be transparent. Always verify permissions, provide accurate attribution, disclose AI assistance when required, and ensure human originality guides the final work.",
            "Main Rule: Respect the rights of creators and be honest. Check permission, give correct credit, and explain AI use when required. Make sure a person's own work guides the final result.",
        ),
        (
            "Once you have completed all sections of your worksheet (Source & Rights Record, Credit Statement, AI Disclosure, and Final Decision), submit your completed assignment to your course.",
            "Complete every part of the worksheet. This includes the source record, credit statement, AI-use statement, and final decision. Then submit the assignment to your course.",
        ),
        (
            "Expand the Program Scenarios Table above, copy the scenario for your specific program, and paste it into Step 1 of your worksheet.",
            "Open the Program Scenarios table above. Copy the example for your program and paste it into Step 1 of the worksheet.",
        ),
        (
            "Main Rule: Do not call every AI mistake bias. Investigate whether the concern is isolated or repeated, examine the data and rules, compare outcomes across relevant groups or conditions, and keep qualified people responsible for decisions and appeals.",
            "Main Rule: Do not call every AI mistake bias. Check whether the problem happened once or many times. Review the data and rules, compare results, and keep trained people in charge of decisions and appeals.",
        ),
        (
            "Big Question: How can data, rules, and testing choices create unequal AI outcomes, and what evidence and safeguards are needed before the system affects people?",
            "Big Question: How can data, rules, and testing lead to unfair AI results? What proof and safety steps are needed before the system affects people?",
        ),
        (
            "Apply the five-part Privacy Scanner to classify proposed uses as Clear, Warning, or Stop and recommend safeguards or non-AI alternatives.",
            "Use the five-part Privacy Scanner to rate an idea as Clear, Warning, or Stop. Suggest a safety step or a way to do the task without AI.",
        ),
        (
            "In this lesson, students use the 5-Tip Prompting Formula to shape a chatbot response and the 3-Step Audit Process to evaluate the complete AI-supported solution. They consider why AI is being used, who may benefit or be affected, what evidence and safeguards are needed, and whether the result should be used, revised, or rejected.",
            "In this lesson, you will use the 5-Tip Prompting Formula to guide a chatbot. Then you will use the 3-Step Audit Process to check the full result. You will decide why AI is being used, who may be affected, what proof and safety steps are needed, and whether to use, revise, or reject the result.",
        ),
        (
            "Study the Responsible AI Routine pathway below. Notice how evaluating career impact requires balancing efficiency gains against environmental costs and human skill development.",
            "Study the Responsible AI Routine below. Think about how AI may save time but also use resources or change the skills people need.",
        ),
        (
            "Key takeaway: More detail can improve an AI response, but access is not the same as authorization and private detail is not the same as useful context. A professional preserves the task, uses only the minimum necessary information, and follows the approved process.",
            "Key takeaway: More detail may improve an AI answer, but having access does not mean you have permission to share. Private details are not always useful. Keep the goal, use only the information you need, and follow the approved steps.",
        ),
        (
            "Main Rule: Better data creates better models, but human oversight completes the system. Never deploy or trust an AI model without rigorous testing, continuous error analysis, and responsible human control.",
            "Main Rule: Better data can improve a model, but people must remain in control. Do not use or trust a model until people test it, study its errors, and take responsibility for its use.",
        ),
        (
            "Ask for Sources & Reasoning: Ask the chatbot why it gave a certain response or request its sources to evaluate its logic and verify information.",
            "Ask for sources and reasons: Ask why the chatbot gave its answer and where the information came from. Then check its logic and facts.",
        ),
        (
            "Entering information is only the first privacy decision. Think about the full data lifecycle: collect or enter → process → store → keep → review or share → possibly use for training or product improvement → delete or request deletion.",
            "Entering information is only the first privacy choice. Follow the data through each step: enter, use, save, keep, review or share, and delete. A company might also use the data to train or improve a product.",
        ),
        (
            "S — Search, Check, and Strengthen: Check accuracy, originality, safety, close matches, sources, and professional rules. Revise, replace, or reject material that cannot be verified.",
            "S — Search, Check, and Strengthen: Check the facts, safety, sources, rules, and possible copied material. Change, replace, or reject anything you cannot confirm.",
        ),
        (
            "Warning — The task may become appropriate after direct and indirect identifiers are removed. No protected record, password, confidential work, or restricted material may remain.",
            "Warning — The task may be safe after all identifying details are removed. Do not include protected records, passwords, private work, or restricted material.",
        ),
        (
            "AI can create convincing images, audio, video, graphics, logos, and designs. Convincing media, however, is not automatically accurate, safe, authentic, or appropriate to use.",
            "AI can create realistic images, audio, video, graphics, logos, and designs. But realistic media may still be wrong, unsafe, fake, or not suitable to use.",
        ),
        (
            "Grading Standard (Complete / Incomplete): To earn a Complete mark, you must thoroughly address all 5 parts of the worksheet with thoughtful, full-sentence explanations where required. If any section is incomplete or missing, your submission will be marked Incomplete and returned for revision.",
            "Grading: Complete all five parts of the worksheet. Use full sentences when the directions ask for them. Missing parts will be marked Incomplete and returned for revision.",
        ),
        (
            "In this lesson, students investigate workplace-style images without being asked to guess which are AI-generated. They examine how prompt choices and training patterns shape AI images and why detailed prompts do not guarantee accuracy or safety. Using Pause, Trace, Check, Decide, Disclose, students audit fictional workplace media and make an evidence-based Approve, Revise, or Reject decision.",
            "In this lesson, you will study workplace-style images. You will see how prompts and training patterns shape AI images and why detailed prompts do not promise safe or correct results. You will use Pause, Trace, Check, Decide, Disclose to review made-up workplace media. Then you will choose Approve, Revise, or Reject and support your choice with evidence.",
        ),
        (
            "Building and improving an AI model is a repeating cycle. Take a look at the five steps below to see how a model learns, gets tested, and improves over time:",
            "Building an AI model is a cycle that repeats. Review the five steps below to see how a model learns, is tested, and improves:",
        ),
        (
            "Main Rule: Use only the minimum information needed, only when you are authorized, and only through an approved process. An approved tool is not blanket permission to enter every available detail.",
            "Main Rule: Use only the information you need. Make sure you have permission and follow the approved steps. An approved tool does not mean you may enter every detail.",
        ),
        (
            "Yellow Light: AI may help, but important questions, limits, checking steps, training needs, access concerns, or environmental costs must be addressed first.",
            "Yellow Light: AI may help, but some concerns must be fixed first. Check the limits, review steps, training needs, access, and effects on resources.",
        ),
        (
            "In this assignment, you will evaluate a realistic workplace task tied to your program or future career using the Responsible AI Routine.",
            "In this assignment, you will use the Responsible AI Routine to review a workplace task linked to your program or future career.",
        ),
        (
            "Before moving on, consider: Why is a search check alone not enough to prove that an AI-assisted creation is fully original and ready to share?",
            "Before moving on, think about this question: Why can a search not prove by itself that AI-assisted work is original and ready to share?",
        ),
        (
            "AI can also spread false information, expose private data, create unfair results, or make people depend too much on technology. AI systems also use electricity, water for cooling, computers, and other materials.",
            "AI can spread false information, expose private data, create unfair results, or make people depend too much on it. AI systems also use electricity, cooling water, computers, and other materials.",
        ),
        (
            "Important Current Guidance: Using AI does not automatically prevent copyright protection. Human-created writing, design choices, arrangement, or meaningful changes in AI-assisted work may be protected. Material created only by AI generally is not protected, and a prompt alone is usually not enough to show human authorship. Mixed works can be complex, so current guidance and school or workplace rules still matter.",
            "Current guidance: Using AI does not always remove copyright protection. A person's writing, design choices, or major changes may still be protected. Work made only by AI is usually not protected, and a prompt alone may not show enough human work. Follow current school, workplace, and copyright rules.",
        ),
        (
            "Assess tool fit to determine whether an AI solution or a traditional approach is best for a given workplace scenario.",
            "Decide whether AI or a non-AI method is the better choice for a workplace task.",
        ),
        (
            "Training Data: If the data is missing key information or mostly represents one group, the AI may repeat those uneven patterns.",
            "Training Data: If key information is missing or one group appears most often, the AI may repeat unfair patterns.",
        ),
        (
            "Big Question: How can I verify AI-generated or altered media and decide whether it is responsible to use or share?",
            "Big Question: How can I check media made or changed by AI? How can I decide whether it is safe and fair to use or share?",
        ),
        (
            "Audit for Accuracy: Check whether the AI covered all your instructions and verify factual details independently. AI can generate convincing mistakes or false facts.",
            "Check for accuracy: Make sure the AI followed every direction. Check the facts with another trusted source because AI can make believable mistakes.",
        ),
    )
    for old_text, new_text in reading_level_replacements:
        flexible_pattern = re.escape(old_text).replace(r"\ ", r"\s+")
        value = re.sub(flexible_pattern, new_text, value)
    remaining_reading_replacements = (
        ("Fix mislabeled data or add better examples, then train the improved model to make it more accurate.", "Fix labels that are wrong or add better examples. Then train the model again and check whether it improved."),
        ("You ask an AI image tool to create a picture of a \"successful team.\" Every single person it draws is young, wearing a formal suit, and standing in a tall office building.", "You ask AI to make a picture of a \"successful team.\" It shows only young people in suits inside a tall office building."),
        ("Respect creative rights and be transparent. Always verify permissions, provide accurate attribution, disclose AI assistance when required, and ensure human originality guides the final work.", "Respect the rights of creators and be honest. Check permission, give correct credit, and explain AI use when required. Make sure a person's own work guides the final result."),
        ("Once you have completed all sections of your worksheet (Source & Rights Record, Credit Statement, AI Disclosure, and Final Decision), submit your completed assignment to your course.", "Complete every part of the worksheet. This includes the source record, credit statement, AI-use statement, and final decision. Then submit the assignment to your course."),
        ("Expand the Program Scenarios Table above, copy the scenario for your specific program, and paste it into Step 1 of your worksheet.", "Open the Program Scenarios table above. Copy the example for your program and paste it into Step 1 of the worksheet."),
        ("Do not call every AI mistake bias. Investigate whether the concern is isolated or repeated, examine the data and rules, compare outcomes across relevant groups or conditions, and keep qualified people responsible for decisions and appeals.", "Do not call every AI mistake bias. Check whether the problem happened once or many times. Review the data and rules, compare results, and keep trained people in charge of decisions and appeals."),
        ("How can data, rules, and testing choices create unequal AI outcomes, and what evidence and safeguards are needed before the system affects people?", "How can data, rules, and testing lead to unfair AI results? What proof and safety steps are needed before the system affects people?"),
        ("More detail can improve an AI response, but access is not the same as authorization and private detail is not the same as useful context. A professional preserves the task, uses only the minimum necessary information, and follows the approved process.", "More detail may improve an AI answer, but having access does not mean you have permission to share. Private details are not always useful. Keep the goal, use only the information you need, and follow the approved steps."),
        ("Better data creates better models, but human oversight completes the system. Never deploy or trust an AI model without rigorous testing, continuous error analysis, and responsible human control.", "Better data can improve a model, but people must remain in control. Do not use or trust a model until people test it, study its errors, and take responsibility for its use."),
        ("While you watch, look for three things: why your own knowledge and careful thinking still matter, one way AI may help learning, and one rule that would make that use safer and more responsible.", "While you watch, find three things. Why does your own knowledge matter? How might AI help you learn? What rule would make that use safer?"),
        ("Ask the chatbot why it gave a certain response or request its sources to evaluate its logic and verify information.", "Ask why the chatbot gave its answer and where the information came from. Then check its logic and facts."),
        ("Check accuracy, originality, safety, close matches, sources, and professional rules. Revise, replace, or reject material that cannot be verified.", "Check the facts, safety, sources, rules, and possible copied material. Change, replace, or reject anything you cannot confirm."),
        ("The task may become appropriate after direct and indirect identifiers are removed. No protected record, password, confidential work, or restricted material may remain.", "The task may be safe after all identifying details are removed. Do not include protected records, passwords, private work, or restricted material."),
        ("To earn a Complete mark, you must thoroughly address all 5 parts of the worksheet with thoughtful, full-sentence explanations where required. If any section is incomplete or missing, your submission will be marked Incomplete and returned for revision.", "Complete all five parts of the worksheet. Use full sentences when the directions ask for them. Missing parts will be marked Incomplete and returned for revision."),
        ("Use only the minimum information needed, only when you are authorized, and only through an approved process. An approved tool is not blanket permission to enter every available detail.", "Use only the information you need. Make sure you have permission and follow the approved steps. An approved tool does not mean you may enter every detail."),
        ("AI may help, but important questions, limits, checking steps, training needs, access concerns, or environmental costs must be addressed first.", "AI may help, but some concerns must be fixed first. Check the limits, review steps, training needs, access, and effects on resources."),
        ("Using AI does not automatically prevent copyright protection. Human-created writing, design choices, arrangement, or meaningful changes in AI-assisted work may be protected. Material created only by AI generally is not protected, and a prompt alone is usually not enough to show human authorship. Mixed works can be complex, so current guidance and school or workplace rules still matter.", "Using AI does not always remove copyright protection. A person's writing, design choices, or major changes may still be protected. Work made only by AI is usually not protected, and a prompt alone may not show enough human work. Follow current school, workplace, and copyright rules."),
        ("If the data is missing key information or mostly represents one group, the AI may repeat those uneven patterns.", "If key information is missing or one group appears most often, the AI may repeat unfair patterns."),
        ("How can I verify AI-generated or altered media and decide whether it is responsible to use or share?", "How can I check media made or changed by AI? How can I decide whether it is safe and fair to use or share?"),
        ("Check whether the AI covered all your instructions and verify factual details independently. AI can generate convincing mistakes or false facts.", "Make sure the AI followed every direction. Check the facts with another trusted source because AI can make believable mistakes."),
        ("In construction, electrical work, welding, aviation, and mechatronics, AI may help estimate costs, watch systems, or suggest ideas. Trained workers must still follow codes, inspect real conditions, use hands-on skills, and make safety decisions.", "AI may help in construction, electrical work, welding, aviation, and mechatronics. It can estimate costs, watch systems, or suggest ideas. Trained workers must still follow codes, inspect conditions, use hands-on skills, and make safety choices."),
        ("Provides learning modules, interactive tools, and educator guides on machine learning foundations and model evaluation.", "Includes lessons, activities, and guides about machine learning and testing AI models."),
        ("Provides the student videos and educator materials used as the starting point for this lesson.", "Includes student videos and teacher materials for this lesson."),
        ("Provides the three student videos and educator materials used as the starting point for this lesson.", "Includes three student videos and teacher materials for this lesson."),
        ("Provides official guidance on copyright principles, original human authorship, fair use, licensing, and AI-generated materials.", "Gives official guidance about copyright, human-created work, fair use, licenses, and AI-made materials."),
        ("A U.S. government framework for identifying and managing privacy risk while using personal data and technology services.", "A U.S. government guide for managing privacy risks when people use data and technology."),
    )
    for old_text, new_text in remaining_reading_replacements:
        flexible_pattern = re.escape(old_text).replace(r"\ ", r"\s+")
        value = re.sub(flexible_pattern, new_text, value)
    value = value.replace(
        "If the data missing key information or mostly shows one group, the AI repeats those uneven patterns.",
        "If the data is missing key information or mostly represents one group, the AI may repeat those uneven patterns.",
    )
    value = value.replace(
        "In this lesson, you will examine the data, labels, rules, proxy information, testing choices, and human decisions behind fictional workplace AI systems. You will distinguish an isolated error from a possible bias warning sign and a repeated unfair pattern, analyze unequal outcomes such as false positives or false negatives, and recommend safeguards, appeals, monitoring, and meaningful human authority.",
        "In this lesson, you will look at how data, rules, and human choices shape workplace AI systems. You will learn the difference between a single mistake, a warning sign of bias, and a pattern of unfair results. You will also study errors that affect groups in different ways. Finally, you will suggest ways to make AI systems safer and fairer through testing, review, appeals, and human decision making.",
    )
    value = value.replace(
        "In this lesson, students distinguish privacy, confidentiality, security, ownership, authorization, and de-identification. They trace information through a data lifecycle and use the Privacy Scanner to ethically evaluate AI uses, preserve the task's purpose, and choose an approved safeguard or non-AI alternative.",
        "This lesson is about keeping information safe. You will learn about privacy, confidentiality, security, ownership, permission, and removing personal details. You will track what happens to data from the time it is collected until it is deleted. Then you will use the Privacy Scanner to check an AI task. You will choose a safe way to use AI or complete the task without it.",
    )
    value = value.replace(
        "In this lesson, students explore how AI impacts future careers, compare automation with augmentation, analyze environmental and technical trade-offs, and evaluate how human skills complement AI tools in professional settings.",
        "This lesson looks at how AI may change careers. You will compare automation, where AI does a task, with augmentation, where AI helps a person do a task. You will study the benefits and costs of using AI, including its effects on energy and the environment. You will also identify the human skills that still matter at work.",
    )
    value = value.replace(
        "AI can quickly draft content, create code, generate graphics, and summarize work, but using AI-supported material involves critical legal, professional, and ethical decisions. Work generated by AI is not automatically free to use, completely original, or compliant with copyright, trademark, and organizational guidelines.",
        "AI can help people draft text, write code, make images, and summarize information. But people must still make important legal, workplace, and ethical choices. AI-made content is not always free to use or fully original. It may also break copyright, trademark, or workplace rules. You must check the source, permission, and rules before using or sharing it.",
    )
    value = value.replace(
        "Big Question: How can individuals and organizations balance AI automation and augmentation while preserving essential human skills and managing environmental and operational trade-offs?",
        "Big Question: How can people and workplaces use AI and still keep important human skills? How can they lower its effects on energy, resources, and daily work?",
    )
    value = value.replace(
        "How can individuals and organizations balance AI automation and augmentation while preserving essential human skills and managing environmental and operational trade-offs?",
        "How can people and workplaces use AI and still keep important human skills? How can they lower its effects on energy, resources, and daily work?",
    )
    value = value.replace(
        "Focus on What to Do (Not What to Avoid):",
        "Focus on what to do:",
    )
    value = value.replace(
        "Give positive, explicit follow-up directions telling the AI what to add, fix, or expand rather than negative commands (e.g., say <em>\"Include step-by-step examples\"</em> instead of <em>\"Don't make it generic\"</em>).",
        "Tell the AI what it should add, fix, or explain. Use clear and positive directions. For example, say <em>\"Include examples with clear steps\"</em> instead of <em>\"Don't make it generic\"</em>.",
    )
    value = value.replace(
        "Watch for the data lifecycle: collection or entry, processing, storage, retention, review or sharing, possible training or product improvement, and deletion or deletion requests.",
        "Watch what happens to data at each step. Data may be entered, used, saved, kept, reviewed, or shared. A company may also use it to train or improve a product. At the end, the data may be deleted, or a person may ask for it to be deleted.",
    )
    value = value.replace(
        "Classify the likely source as rule-based, data-driven, both, undetermined, or another system failure; then recommend changes to the data, rules, testing, workflow, appeal process, monitoring, or human review and defend a Green, Yellow, or Red Light verdict.",
        "Decide what may have caused the problem. It may come from rules, data, both, or another system error. Then suggest ways to improve the data, rules, testing, work steps, appeals, tracking, or human review. Use your evidence to choose a Green, Yellow, or Red Light rating.",
    )
    value = value.replace(
        "Compare outcomes across relevant people, groups, equipment, environments, or conditions and identify a possible false positive, false negative, exclusion, lower ranking, or other disparity.",
        "Compare results for different people, groups, equipment, places, or conditions. Look for unfair patterns. These may include false alerts, missed problems, lower scores, or people being left out.",
    )
    value = value.replace(
        "Evaluate the source, quality, representation, missing information, privacy considerations, and limitations of data used in a fictional AI-supported process.",
        "Review the data used in a made-up AI task. Check where the data came from, how good it is, who it represents, and what may be missing. Also check for privacy risks and limits in the data.",
    )
    value = value.replace(
        "Identify the judgment, relationship, hands-on skill, safety choice, ethical responsibility, creativity, communication, or accountability that people must continue to lead.",
        "Name the parts of a job that people should continue to lead. These may include judgment, relationships, hands-on skills, safety, ethics, creativity, communication, and taking responsibility.",
    )
    value = re.sub(
        r"Identify the judgment, relationship, hands-on skill, safety choice,\s*ethical responsibility, creativity, communication, or accountability\s*that people must continue to lead\.",
        "Name the parts of a job that people should continue to lead. These may include judgment, relationships, hands-on skills, safety, ethics, creativity, communication, and taking responsibility.",
        value,
    )
    value = re.sub(
        r"Culinary, Hospitality, and Cosmetology:\s*AI may help with scheduling, inventory, comparisons, or early ideas;\s*professionals still use sensory judgment, protect clients, follow safety\s*rules, and manage relationships\.",
        "In cooking, hotels, and cosmetology, AI may help plan schedules, track supplies, compare choices, or develop early ideas. People must still use their senses and judgment, protect clients, follow safety rules, and build relationships.",
        value,
    )
    value = re.sub(
        r"Culinary, Hospitality, and Cosmetology:.*?manage\s+relationships\.",
        "In cooking, hotels, and cosmetology, AI may help plan schedules, track supplies, compare choices, or develop early ideas. People must still use their senses and judgment, protect clients, follow safety rules, and build relationships.",
        value,
        flags=re.DOTALL,
    )
    value = re.sub(
        r"Construction, Electrical, Welding, Aviation, and Mechatronics:.*?make\s+safety decisions\.",
        "In construction, electrical work, welding, aviation, and mechatronics, AI may help estimate costs, watch systems, or suggest ideas. Trained workers must still follow codes, inspect real conditions, use hands-on skills, and make safety decisions.",
        value,
        flags=re.DOTALL,
    )
    value = re.sub(
        r"Health Science and Veterinary Medicine:.*?make\s+care decisions\.",
        "In health science and veterinary medicine, AI may help organize made-up information or point out patterns. Trained professionals must still protect records, study the full situation, talk with people, and make care decisions.",
        value,
        flags=re.DOTALL,
    )
    value = re.sub(
        r"Public Safety and Forensics:.*?make\s+high-stakes decisions\.",
        "In public safety and forensics, AI may help organize information or find patterns. Trained workers must still protect evidence, follow laws and rules, study the full situation, and make serious decisions.",
        value,
        flags=re.DOTALL,
    )
    value = value.replace(
        "Viewing focus: Identify why personal knowledge and critical thinking remain important, one possible benefit of AI-supported learning, and one condition needed for that benefit to occur responsibly.",
        "While you watch, look for three things: why your own knowledge and careful thinking still matter, one way AI may help learning, and one rule that would make that use safer and more responsible.",
    )
    value = value.replace(
        "A student uses AI to brainstorm logo concepts, redraws and edits the selected concept in design software, credits the inspiration source, and includes an AI disclosure note detailing their modifications.",
        "A student asks AI for logo ideas. The student redraws and edits one idea in design software. They credit the source of the idea and explain how they used AI and changed the design.",
    )
    value = value.replace(
        "A student uses AI to generate initial layout concepts, refines the design manually, runs a reverse image check to ensure originality, and cites the AI assistance in their project notes.",
        "A student asks AI for layout ideas, then changes the design by hand. They use a reverse image search to look for close matches. They also explain how AI helped with the project.",
    )
    value = value.replace(
        "Check: What evidence, model limitations, affected people, gaps, unfair assumptions, accessibility concerns, safety risks, privacy risks, and other harms must be reviewed?",
        "Check: What facts need to be checked? What are the model's limits? Think about who may be affected, what information may be missing, and whether the AI makes unfair guesses. Also check for access, safety, privacy, or other risks.",
    )
    value = value.replace(
        "What evidence, model limitations, affected people, gaps, unfair assumptions, accessibility concerns, safety risks, privacy risks, and other harms must be reviewed?",
        "What facts need to be checked? What are the model's limits? Think about who may be affected, what information may be missing, and whether the AI makes unfair guesses. Also check for access, safety, privacy, or other risks.",
    )
    value = value.replace(
        "A colleague creates an original staff training handout using their own text, a Creative Commons vector icon (credited), and an AI-generated outline that was extensively revised and disclosed.",
        "A coworker makes a staff training handout. They write their own text and give credit for a Creative Commons icon. They also use AI to create an outline, make major changes to it, and explain how they used AI.",
    )
    value = value.replace(
        "AI technology is reshaping careers, industries, and daily tasks by automating routine processes and augmenting human capabilities. However, integrating AI introduces trade-offs between speed, accuracy, human oversight, environmental costs, and task fit.",
        "AI is changing careers, industries, and daily tasks. It can do some routine tasks and help people with others. But using AI also involves choices. People must weigh speed and accuracy against human review, energy use, and whether the tool fits the task.",
    )
    value = value.replace(
        "AI systems may use historical records, examples, labels, measurements, thresholds, and scoring rules to make predictions or recommendations. When those inputs are incomplete, inaccurate, unrepresentative, or built on unsupported assumptions, the system may create repeated unfair patterns or provide lower-quality service for particular people, groups, equipment, environments, or conditions. A concerning result is a reason to investigate, but not every error is proof of algorithmic bias.",
        "AI systems may use past records, examples, labels, measurements, and rules to make predictions or suggestions. If this information is missing, wrong, or unfair, the system may repeat unfair patterns or give some groups worse results. A troubling result should be checked, but one mistake does not always prove the system is biased.",
    )
    value = re.sub(
        r"Identify a repeatable step involving data, scheduling, sorting,\s*drafting, or monitoring that may be automated when the use is approved\s*and appropriate\.",
        "Find one step that is done the same way each time. It may involve data, schedules, sorting, drafting, or tracking. AI may do this step if its use is allowed and fits the task.",
        value,
    )
    value = value.replace(
        "How can people create and share AI-supported work fairly, legally, and transparently while honoring copyright, licensing, and human originality?",
        "How can people use AI to create and share work in a fair and legal way? How can they respect copyright, follow license rules, and show their own original work?",
    )
    value = value.replace(
        "In the first seven lessons, students learned to guide AI, verify outputs, examine bias, protect private information, create responsibly, and evaluate where AI belongs in school and workplace tasks. Lesson 8 completes the sequence by allowing students to build, test, and improve a simple classification model before completing the cumulative certification assessment.",
        "In the first seven lessons, you learned how to guide AI, check its answers, look for bias, protect private information, and use AI responsibly. In Lesson 8, you will build, test, and improve a simple AI model. Then you will complete the final assessment.",
    )
    value = value.replace(
        "A student asks AI to write code in the distinct style of an online developer's private repo, submits it verbatim, and claims full personal authorship without disclosure.",
        "A student asks AI to copy the style of code from a developer's private online project. The student submits the code without changes, says it is all their own work, and does not mention using AI.",
    )
    value = value.replace(
        "To decide, reflect on what result you need, how accurate it must be, what happens if the tool makes a mistake, data privacy, resource costs, and whether a simpler method already solves the problem safely.",
        "To decide, ask: What result do I need? How accurate must it be? What could happen if the tool is wrong? Also check privacy, energy use, and whether a simpler method can do the job safely.",
    )
    value = value.replace(
        "Use only fictional or approved information. Never enter real patient, student, customer, employee, applicant, victim, suspect, account, security, employer, or confidential information into an unapproved AI tool.",
        "Use only made-up or approved information. Do not put real private information into an AI tool that has not been approved. This includes names or records about patients, students, customers, workers, applicants, victims, suspects, accounts, security, or employers.",
    )
    value = re.sub(
        r"Automotive:\s*AI may organize sensor patterns or suggest possible causes;\s*technicians still inspect, test, communicate with customers, and authorize\s*safe repairs\.",
        "In automotive work, AI may sort sensor data or suggest possible causes of a problem. Technicians must still inspect and test the vehicle, talk with customers, and approve safe repairs.",
        value,
    )
    value = value.replace(
        "AI can help with studying, writing, planning, troubleshooting, and workplace communication, but each use creates a data-handling decision. Information may be collected, processed, stored, retained, reviewed, shared, or used for model training depending on the tool, account, settings, contract, and organizational policy.",
        "AI can help with school and workplace tasks, but each use involves a choice about data. A tool may collect, use, save, keep, review, share, or train on information. What happens depends on the tool, account, settings, contract, and workplace rules.",
    )
    value = value.replace(
        "A student wants AI to help write a workplace message. The student pastes a real person's name, contact information, account details, and problem into a chatbot because “more details will produce a better answer.”",
        "A student wants AI to help write a workplace message. They paste in a real person's name, contact details, account information, and problem. The student thinks that more details will create a better answer.",
    )
    value = re.sub(
        r"Automotive:.*?authorize\s+safe repairs\.",
        "In automotive work, AI may sort sensor data or suggest possible causes of a problem. Technicians must still inspect and test the vehicle, talk with customers, and approve safe repairs.",
        value,
        flags=re.DOTALL,
    )
    value = re.sub(
        r"A student wants AI to help write a workplace message\. The student pastes a real person.s name, contact information, account details, and problem into a chatbot because .more details will produce a better answer..",
        "A student wants AI to help write a workplace message. They paste in a real person's name, contact details, account information, and problem. The student thinks that more details will create a better answer.",
        value,
    )
    value = value.replace(
        "Study the Responsible AI Routine pathway below. Notice how protecting privacy requires verifying authorization, minimizing data, and enforcing safeguards before entering information into an AI system.",
        "Study the Responsible AI Routine below. Notice the steps that protect privacy. Check that you have permission, use only the data you need, and add safety steps before entering information into AI.",
    )
    value = value.replace(
        "In this lesson, students explore copyright, fair use, public domain, permissive licensing, ownership, attribution, and transparency. They evaluate workplace and academic scenarios to determine authorization, give appropriate credit, disclose AI usage, and choose an ethical path forward.",
        "In this lesson, you will learn about copyright, fair use, public domain work, licenses, ownership, credit, and honesty about AI use. You will review school and workplace examples. You will decide whether someone has permission, how to give credit, when to explain AI use, and what action is fair.",
    )
    value = re.sub(
        r"Identify a step where AI could provide information, ideas, feedback,\s*organization, a prediction, or a first draft while a qualified person\s*stays responsible\.",
        "Find one step where AI could help a trained person. AI might provide information, ideas, feedback, organization, a prediction, or a first draft. The person must still check the work and remain responsible.",
        value,
    )
    value = value.replace(
        "Information entered into AI models may be stored, used to train future systems, or accidentally exposed depending on the settings and agreements in place.",
        "Information entered into an AI tool may be saved, used to train the system, or exposed by mistake. What happens depends on the tool's settings and agreements.",
    )
    value = value.replace(
        "How can people train, test, improve, and oversee AI classification models so they support real workplace decisions accurately, fairly, and responsibly?",
        "How can people train, test, improve, and oversee an AI classification model? How can they help it make accurate and fair choices at work?",
    )
    value = value.replace(
        "A better prompt may improve the response, but only careful evaluation and human responsibility determine whether it should be used.",
        "A better prompt may improve an AI answer. But a person must still check the answer and take responsibility before using it.",
    )
    value = value.replace(
        "Data controls may let you limit location, camera, microphone, history, file access, or use of your data for product improvement. Account safety includes using strong passwords, turning on two-step verification, signing out of shared devices, tracking your accounts, and deleting accounts you no longer need.",
        "Data controls may let you turn off access to your location, camera, microphone, history, or files. They may also limit how a company uses your data. Protect your account with a strong password and two-step verification. Sign out of shared devices, keep track of your accounts, and delete accounts you no longer use.",
    )
    value = value.replace(
        "Study the Responsible AI Routine pathway below. Notice how evaluating fairness requires checking training data, comparing group outcomes, and establishing human appeal authority before implementing a system.",
        "Study the Responsible AI Routine below. To check fairness, review the training data and compare results for different groups. Make sure people can question a result and ask a trained person to review it before the system is used.",
    )
    value = value.replace(
        "An intern submits a blog post entirely generated by AI, claiming it as 100% original human-written copy without disclosing AI tools or verifying facts.",
        "An intern uses AI to write an entire blog post. The intern says a person wrote all of it. They do not mention AI or check the facts.",
    )
    value = value.replace(
        "A student uses AI to generate an entire graphic, submits it as original work without changes, and does not disclose AI involvement.",
        "A student uses AI to make an entire graphic. The student makes no changes, submits it as original work, and does not explain that AI was used.",
    )
    value = re.sub(
        r"Computer Science and Cybersecurity:.*?approve\s+systems\.",
        "In computer science and cybersecurity, AI may help draft code or sort alerts. Trained workers must still test the system, keep it secure, record their work, follow license rules, and approve the final result.",
        value,
        flags=re.DOTALL,
    )
    value = value.replace(
        "Study the Responsible AI Routine pathway below. Notice how building and deploying AI models requires validating training data, testing for misclassifications, and retaining human accountability.",
        "Study the Responsible AI Routine below. When building an AI model, check the training data and test where the model makes mistakes. A person must remain responsible for how the model is used.",
    )
    value = value.replace(
        "Study the Responsible AI Routine pathway below. Notice how ethical intellectual property practices require checking copyright, providing credit, and disclosing AI contributions before publishing work.",
        "Study the Responsible AI Routine below. Before sharing AI-assisted work, check copyright, give credit, and explain how AI helped.",
    )
    value = value.replace(
        "“Create a five-step visual tire-inspection checklist for a first-year automotive student. Use a numbered list, include one safety reminder, and ask for the vehicle type before finalizing.”",
        "“Make a five-step tire inspection checklist for a new automotive student. Use a numbered list and add one safety reminder. Before you finish, ask what type of vehicle the student will inspect.”",
    )
    value = value.replace(
        "In this lesson, students select their exact GCI program and enter one of six equivalent fictional workplace scenarios. They build, test, and improve a simple classification model using machine learning, diagnose model errors, recommend safeguards, and complete the final certification exam.",
        "In this lesson, you will choose a program area that interests you and work with one of six made-up workplace examples. You will build, test, and improve a simple AI model. You will find errors, suggest safety steps, and complete the final assessment.",
    )
    value = value.replace(
        "Answer these 5 questions in the text box below:",
        "Answer these 5 questions and submit your answers in the course:",
    )
    value = re.sub(
        r'<p([^>]*)><strong([^>]*)>Step 4: Save (?:&amp;|&) Submit</strong><br\s*/?>Submit your completed worksheet using <em>one</em> of the following methods:</p>\s*<ul[^>]*>.*?</ul>',
        r'<p\1><strong\2>Step 4: Save &amp; Submit</strong><br>Submit your completed worksheet to your course.</p>',
        value,
        flags=re.DOTALL,
    )
    value = value.replace(
        "Once you have completed all sections of your worksheet (Source & Rights Record, Credit Statement, AI Disclosure, and Final Decision), save and submit your document here.",
        "Once you have completed all sections of your worksheet (Source & Rights Record, Credit Statement, AI Disclosure, and Final Decision), submit your completed assignment to your course.",
    )
    value = value.replace(
        "Upload your completed file or share your document link to this assignment page.",
        "Submit your completed assignment to your course.",
    )
    value = value.replace(
        "After completing the simulation, you will reflect on what you learned and connect it to your GCI program area by submitting a short text entry.",
        "After completing the simulation, you will reflect on what you learned and connect it to a program area that interests you in a short document.",
    )
    value = value.replace(
        "Click <strong>Submit Assignment</strong> at the top of this page and type your answers to the following 4 reflection questions in the Text Entry box:",
        "Create a document and answer the following 4 reflection questions. Submit your completed document to your course:",
    )
    for group_number in range(1, 7):
        value = value.replace(
            f'scope="row">Version {group_number}</th>',
            f'scope="row">Program Group {group_number}</th>',
        )
    value = value.replace("Version 1", "Initial Model")
    value = value.replace("Version 2", "Improved Model")
    value = value.replace("version 2", "the improved model")
    value = value.replace("(v1)", "(Initial Model)")
    value = value.replace("(v2)", "(Improved Model)")
    value = value.replace("testing Initial Model", "testing the Initial Model")
    value = value.replace("Run Initial Model", "Run the Initial Model")
    value = value.replace("Retrain Improved Model", "Retrain the Improved Model")
    value = value.replace("in Initial Model?", "in the Initial Model?")
    value = value.replace("in Improved Model change", "in the Improved Model change")
    value = value.replace("https://www.youtube.com/embed/dpRK9y7fuJA", "https://www.youtube-nocookie.com/embed/dpRK9y7fuJA?cc_load_policy=1")
    value = value.replace("https://gisd.instructure.com/courses/2083/files/274996/download?download_frd=1", "https://www.youtube.com/watch?v=BQosMFvT0aU&cc_load_policy=1")
    value = value.replace('href="url?id=43"', 'href="https://www.youtube.com/watch?v=fv2e58rgI9k&cc_load_policy=1"')
    value = value.replace('href="url?id=41"', 'href="https://www.youtube.com/watch?v=fv2e58rgI9k"')
    value = value.replace(
        "https://questions.learnosity.com/v2023.2.LTS/xdomain",
        "https://www.youtube-nocookie.com/embed/VwAlOUE4K7M?cc_load_policy=1",
    )
    value = value.replace(
        '<p style="margin: 0; font-size: 0.9em; color: #005a70; text-align: center;">English transcript | Watch in Spanish | Watch in Arabic</p>',
        '<p style="margin: 0; font-size: 0.9em; color: #005a70; text-align: center;">'
        '<a href="https://www.youtube.com/watch?v=VwAlOUE4K7M&cc_load_policy=1" target="_blank" rel="noopener">Watch with English captions</a> | '
        '<a href="https://www.youtube-nocookie.com/embed/gXl0ud9talY?rel=0" target="_blank" rel="noopener">Watch in Spanish</a> | '
        '<a href="https://www.youtube-nocookie.com/embed/detnBXmY0E0?rel=0" target="_blank" rel="noopener">Watch in Arabic</a></p>',
    )
    value = re.sub(r'(href="https://www\.youtube\.com/watch\?v=(?:BQosMFvT0aU|fv2e58rgI9k)&(?:amp;)?cc_load_policy=1"[^>]*>)English transcript(</a>)', r'\1Watch with English captions\2', value)
    value = value.replace("$IMS-CC-FILEBASE$/Uploaded%20Media/", "../assets/media/")
    value = value.replace("$IMS-CC-FILEBASE$/Uploaded Media/", "../assets/media/")
    value = value.replace('src="url?id=17/159962/preview"', 'src="../assets/media/Responsible_AI_Routine_Web_Mobile_1200px.png"')
    value = value.replace(
        'src="../assets/media/M01_ResponsibleAIRoutine_v1.png"',
        'src="../assets/media/Responsible_AI_Routine_Web_Mobile_1200px.png"',
    )
    value = value.replace(
        'alt="AI Decision Pathway with Goal, Protect, Use, Check, and Own."',
        f'alt="{html.escape(ROUTINE_ALT, quote=True)}"',
    )
    value = value.replace(
        'alt="AI Decision Pathway showing Goal, Protect, Use, Check, and Own."',
        f'alt="{html.escape(ROUTINE_ALT, quote=True)}"',
    )
    value = value.replace(
        'alt="Data security flowchart for assessing prompt safety and privacy compliance."',
        'alt="Human oversight flowchart for deciding when an AI output needs review, more information, safeguards, or a stop."',
    )
    value = value.replace('href="url?id=38"', 'href="https://www.iea.org/reports/key-questions-on-energy-and-ai"')
    value = re.sub(r"\sdata-api-(?:endpoint|returntype)=\"[^\"]*\"", "", value)
    value = re.sub(r'<div[^>]*>\s*<p[^>]*>[^<]*Need Help Submitting in Canvas.*?</div>', '', value, flags=re.I | re.S)
    value = re.sub(r'<a[^>]+href="\$CANVAS_OBJECT_REFERENCE\$[^\"]*"[^>]*>.*?</a>', '', value, flags=re.I | re.S)
    value = re.sub(r'<a[^>]+href="https://community\.canvaslms\.com/[^\"]*"[^>]*>.*?</a>', '', value, flags=re.I | re.S)
    value = re.sub(r'\srel="/courses/[^\"]*"', ' rel="noopener"', value)
    value = value.replace("return to Canvas", "return to this lesson")
    value = value.replace("Return to Canvas", "Return to this lesson")
    value = value.replace("submit it in Canvas", "submit it to your course")
    value = value.replace("Submit it in Canvas", "Submit it to your course")
    value = value.replace("Submitting in Canvas", "Submitting to your course")
    value = value.replace("in Canvas", "in your course")
    value = value.replace("Canvas will", "The assessment will")
    value = value.replace("Canvas keeps", "The assessment keeps")
    value = value.replace("Canvas", "your course")
    value = value.replace('Click the blue <strong>Submit Assignment</strong> button at the top of the page to upload your file.', 'Submit the assignment to your course.')
    value = value.replace("Pedictor", "Predictor")
    value = re.sub(r"\bstandalone\s+lesson\b", "lesson", value, flags=re.I)
    value = re.sub(r"https://www\.youtube\.com/embed/([A-Za-z0-9_-]+)", r"https://www.youtube-nocookie.com/embed/\1?cc_load_policy=1", value)
    for video_id, title in VIDEO_TITLES.items():
        pattern = rf'(<iframe[^>]*src="[^"]*{re.escape(video_id)}[^"]*"[^>]*)(title="[^"]*")([^>]*>)'
        if re.search(pattern, value, flags=re.I):
            value = re.sub(pattern, rf'\1title="{html.escape(title)}"\3', value, flags=re.I)
        else:
            pattern = rf'(<iframe[^>]*)(title="[^"]*")([^>]*src="[^"]*{re.escape(video_id)}[^"]*"[^>]*>)'
            value = re.sub(pattern, rf'\1title="{html.escape(title)}"\3', value, flags=re.I)
    late_reading_replacements = (
        ("Distinguish privacy, confidentiality, security, ownership, authorization, de-identification, and data minimization in an AI-supported task.", "Explain the differences among privacy, confidentiality, security, ownership, permission, removing identifying details, and using less data."),
        ("Never share personal identifying details, confidential records, or proprietary organizational data without clear authorization and secure environments.", "Do not share identifying details, private records, or an organization's protected data unless you have permission and use a secure tool."),
        ("Demonstrate comprehensive mastery of responsible AI principles by completing the cumulative certification assessment.", "Show what you learned about responsible AI by completing the final assessment."),
        ("Identify direct and indirect identifiers, determine data ownership, and verify authorization for proposed uses.", "Find details that could identify someone, decide who owns the data, and check whether the planned use has permission."),
        ("Evaluate representation, affected people, community impacts, safeguards, and disclosure requirements to justify an Approve, Revise, or Reject decision.", "Check who is shown, who may be affected, and what safety or disclosure steps are needed. Use evidence to choose Approve, Revise, or Reject."),
        ("Test model performance, calculate accuracy, and analyze misclassification patterns (false positives and false negatives).", "Test the model, calculate how often it is correct, and study its mistakes, including false positives and false negatives."),
        ("Differentiate between AI automation (replacing routine tasks) and AI augmentation (enhancing human capabilities).", "Explain the difference between automation, when AI does a routine task, and augmentation, when AI helps a person."),
        ("Protecting information and maintaining security is an essential responsibility whenever using AI tools.", "You are responsible for protecting information and keeping it secure when you use AI."),
        ("Always follow your organization's specific data classification guidelines, privacy regulations, and approved AI tool lists.", "Follow your organization's rules for data, privacy, and approved AI tools."),
        ("A qualified reviewer examines evidence and context, can override or stop the system, documents the decision, and accepts responsibility.", "A trained reviewer checks the evidence and full situation. The reviewer can stop the system, records the decision, and takes responsibility."),
        ("Define copyright, permission, originality, attribution, trademark, and transparency in the context of AI tools.", "Explain copyright, permission, original work, credit, trademarks, and honesty about AI use."),
        ("Formulate a personalized strategy for continuous career adaptability in an AI-driven workforce.", "Make a personal plan to keep learning and adjust as AI changes work."),
        ("Identify a correction, safeguard, source attribution, AI-use disclosure, or human-approval requirement.", "Name a needed fix, safety step, source credit, AI-use statement, or human approval."),
        ("Evaluate the technical, operational, and environmental trade-offs associated with AI deployment.", "Compare the technical, workplace, and environmental costs and benefits of using AI."),
        ("Verify an important claim and identify possible bias, missing perspectives, unequal access, privacy risks, safety concerns, or other harms.", "Check an important claim. Look for bias, missing views, access problems, privacy or safety risks, and other harm."),
        ("Explain how information moves through collection, processing, storage, retention, review, sharing, possible model training, and deletion.", "Explain what happens when information is collected, used, saved, kept, reviewed, shared, used for training, or deleted."),
        ("Check: Has information been properly de-identified, minimized, or safeguard-checked across its entire lifecycle?", "Check: Were identifying details removed? Was only needed data used? Were safety steps followed from start to finish?"),
        ("Improve model performance by retraining with targeted, high-quality examples to address identified weaknesses.", "Improve the model by training it again with better examples that target its weak areas."),
        ("Remove names, specific dates, identifying numbers, or proprietary identifiers from text before pasting into an AI interface.", "Before using AI, remove names, exact dates, ID numbers, and details that belong to an organization."),
        ("Distinguish provenance and authenticity from accuracy and context, and use Pause, Trace, Check, Decide, Disclose to identify required evidence.", "Explain how a media file's source differs from whether it is real, correct, or shown in context. Use Pause, Trace, Check, Decide, Disclose to find the proof you need."),
        ("Draft clear attributions and AI disclosure statements following academic or workplace guidelines.", "Write clear source credits and AI-use statements that follow school or workplace rules."),
        ("Own: Who retains final accountability for authorizing, sharing, approving, or removing data?", "Own: Who is responsible for allowing, sharing, approving, or removing the data?"),
        ("Human Responsibility: According to the Responsible AI Routine ( Goal → Protect → Use → Check → Own ), who holds ultimate responsibility for a decision made with the help of an AI tool, and why?", "Human Responsibility: When AI helps with a decision, who is still responsible for the final choice, and why? Use the Responsible AI Routine in your answer."),
        ("Own: Who retains final responsibility for approving model deployment, monitoring errors, and making end-point decisions?", "Own: Who is responsible for approving the model, watching for errors, and making the final decisions?"),
        ("Check: Are there unequal outcomes, false positives/negatives, or missing representative data across groups?", "Check: Do groups get different results? Are there false alerts, missed problems, or missing examples?"),
        ("Grading Criteria: Complete / Incomplete (All 5 PAUSE categories filled out thoroughly with clear justification).", "Grading: Complete all five PAUSE sections and clearly explain each choice."),
        ("Data curation includes selecting, preparing, labeling, and reviewing the examples used to train a system.", "Data curation means choosing, preparing, labeling, and checking the examples used to train a system."),
        ("Select a program-aligned workplace scenario and build a simple machine learning classification model using training data.", "Choose a workplace example linked to your program. Then use training data to build a simple AI classification model."),
        ("Fix mislabeled data or add better examples, then train the improved model to make it more accurate.", "Fix labels that are wrong or add better examples. Then train the model again and check whether it improved."),
        ("Once you have completed all sections of your worksheet (Source & Rights Record, Credit Statement, AI Disclosure, and Final Decision), submit your completed assignment to your course.", "Complete every part of the worksheet. This includes the source record, credit statement, AI-use statement, and final decision. Then submit the assignment to your course."),
        ("Expand the Program Scenarios Table above, copy the scenario for your specific program, and paste it into Step 1 of your worksheet.", "Open the Program Scenarios table above. Copy the example for your program and paste it into Step 1 of the worksheet."),
        ("While you watch, look for three things: why your own knowledge and careful thinking still matter, one way AI may help learning, and one rule that would make that use safer and more responsible.", "While you watch, find three things. Why does your own knowledge matter? How might AI help you learn? What rule would make that use safer?"),
        ("To earn a Complete mark, you must thoroughly address all 5 parts of the worksheet with thoughtful, full-sentence explanations where required. If any section is incomplete or missing, your submission will be marked Incomplete and returned for revision.", "Complete all five parts of the worksheet. Use full sentences when the directions ask for them. Missing parts will be marked Incomplete and returned for revision."),
        ("If the data is missing key information or mostly represents one group, the AI may repeat those uneven patterns.", "If key information is missing or one group appears most often, the AI may repeat unfair patterns."),
        ("In construction, electrical work, welding, aviation, and mechatronics, AI may help estimate costs, watch systems, or suggest ideas. Trained workers must still follow codes, inspect real conditions, use hands-on skills, and make safety decisions.", "AI may help in construction, electrical work, welding, aviation, and mechatronics. It can estimate costs, watch systems, or suggest ideas. Trained workers must still follow codes, inspect conditions, use hands-on skills, and make safety choices."),
    )
    for old_text, new_text in late_reading_replacements:
        flexible_pattern = re.escape(old_text).replace(r"\ ", r"\s+")
        value = re.sub(flexible_pattern, new_text, value)
    value = re.sub(
        r"Expand the <em>Program Scenarios Table</em> above, copy the scenario for your specific program, and paste it into Step 1 of your worksheet\.",
        "Open the Program Scenarios table above. Copy the example for your program and paste it into Step 1 of the worksheet.",
        value,
    )
    value = re.sub(
        r"To earn a <strong>Complete</strong> mark, you must thoroughly address all 5 parts of the worksheet with thoughtful, full-sentence explanations where required\. If any section is incomplete or missing, your submission will be marked <strong>Incomplete</strong> and returned for revision\.",
        "Complete all five parts of the worksheet. Use full sentences when the directions ask for them. Missing parts will be marked <strong>Incomplete</strong> and returned for revision.",
        value,
    )
    value = re.sub(
        r'href="https://www\.youtube-nocookie\.com/embed/([A-Za-z0-9_-]+)[^"]*"',
        r'href="https://www.youtube.com/watch?v=\1"',
        value,
        flags=re.I,
    )
    value = re.sub(
        r'href="https://youtu\.be/([A-Za-z0-9_-]+)[^"]*"',
        r'href="https://www.youtube.com/watch?v=\1"',
        value,
        flags=re.I,
    )
    # Reflection prompts are working content and must remain visible. Source
    # material stays collapsible so it does not interrupt the learning flow.
    def unwrap_reflection(match: re.Match) -> str:
        block = match.group(0)
        summary = re.search(r"<summary[^>]*>(.*?)</summary>", block, flags=re.I | re.S)
        heading = re.sub(r"<[^>]+>", "", summary.group(1)).strip() if summary else "Reflection Questions"
        body = re.sub(r"<summary[^>]*>.*?</summary>", "", block, count=1, flags=re.I | re.S)
        body = re.sub(r"^<details[^>]*>|</details>$", "", body.strip(), flags=re.I | re.S)
        return f'<section class="reflection-questions"><h3>{heading}</h3>{body}</section>'

    value = re.sub(
        r"<details\b[^>]*>\s*<summary[^>]*>.*?(?:Reflection Questions|Reflect Before You Continue).*?</summary>.*?</details>",
        unwrap_reflection,
        value,
        flags=re.I | re.S,
    )
    value = re.sub(
        r'<(?:p|h[2-4]|blockquote)\b[^>]*>\s*(?:<[^>]+>\s*)*Complete the questions that appear below(?: to demonstrate your understanding)?\.?\s*(?:</[^>]+>\s*)*</(?:p|h[2-4]|blockquote)>',
        "",
        value,
        flags=re.I,
    )
    value = re.sub(
        r"<h([1-4])([^>]*)>(.*?)</h\1>",
        lambda match: f'<h{match.group(1)}{match.group(2)}>{match.group(3).replace(" — ", ": ")}</h{match.group(1)}>',
        value,
        flags=re.I | re.S,
    )
    value = re.sub(
        r'<h2([^>]*)>([^<]*Pacing at a Glance[^<]*)</h2>',
        lambda match: f'<h2 class="pacing-heading"{match.group(1)}>{match.group(2)}</h2>',
        value,
        flags=re.I,
    )
    value = re.sub(
        r'<h2([^>]*)>([^<]*Learning Goals[^<]*)</h2>',
        lambda match: f'<h2 class="objectives-heading"{match.group(1)}>{match.group(2)}</h2>',
        value,
        flags=re.I,
    )
    value = re.sub(
        r'(<h2 class="objectives-heading"[^>]*>.*?</h2>\s*<p[^>]*>.*?</p>\s*)<ul([^>]*)>(.*?)</ul>',
        r'\1<ul class="objective-cards"\2>\3</ul>',
        value,
        count=1,
        flags=re.I | re.S,
    )
    value = set_video_focus(value)
    value = accessibility_fragment(value)
    value = make_images_zoomable(value)
    value = re.sub(
        r'<div[^>]*>\s*(<button class="image-zoom"[^>]*>\s*<img[^>]+Responsible_AI_Routine_Web_Mobile_1200px\.png.*?</button>)\s*</div>',
        r'<div class="routine-intro-visual">\1</div>',
        value,
        flags=re.I | re.S,
    )
    return value


def extract_lesson_vocabulary(overview: str) -> list[tuple[str, str]]:
    """Read the authoritative term-definition pairs from the lesson overview."""
    start = re.search(r"Key Words to Know", overview, flags=re.I)
    if not start:
        return []
    section = overview[start.end():]
    source_start = re.search(r"<(?:details|summary)\b[^>]*>.*?(?:Source|Acknowledgment)", section, flags=re.I | re.S)
    if source_start:
        section = section[:source_start.start()]
    vocabulary = []
    for match in re.finditer(r"<strong[^>]*>([^<:]+):</strong>\s*(.*?)</div>", section, flags=re.I | re.S):
        term = re.sub(r"\s+", " ", html.unescape(match.group(1))).strip()
        definition = re.sub(r"<[^>]+>", " ", match.group(2))
        definition = re.sub(r"\s+", " ", html.unescape(definition)).strip()
        if term and definition:
            vocabulary.append((term, definition))
    return vocabulary


def structure_routine_overview(overview: str) -> str:
    """Place the overview Routine image and application guidance in a bounded grid."""
    visual = re.search(
        r'(<figure class="routine-figure">.*?</figure>|<div class="routine-intro-visual">.*?</div>)',
        overview,
        flags=re.I | re.S,
    )
    if not visual:
        return overview
    repeated_steps = re.search(
        r'(<p[^>]*>\s*(?:<strong[^>]*>)?\s*Goal\s*(?:→|â†’).*?</p>\s*<ul[^>]*>.*?</ul>)',
        overview[:visual.start()],
        flags=re.I | re.S,
    )
    if repeated_steps:
        overview = overview[:repeated_steps.start()] + overview[repeated_steps.end():]
        visual = re.search(
            r'(<figure class="routine-figure">.*?</figure>|<div class="routine-intro-visual">.*?</div>)',
            overview,
            flags=re.I | re.S,
        )

    routine_heading = list(re.finditer(r"<h2\b[^>]*>.*?Responsible AI Routine.*?</h2>", overview[:visual.start()], flags=re.I | re.S))
    if routine_heading:
        section_start = routine_heading[-1].end()
        before_visual = overview[section_start:visual.start()]
        before_visual = re.sub(
            r'<div\b[^>]*>\s*<p\b[^>]*>\s*<strong[^>]*>.*?Your next move:.*?</p>\s*</div>',
            "",
            before_visual,
            count=1,
            flags=re.I | re.S,
        )
        overview = overview[:section_start] + before_visual + overview[visual.start():]
        visual = re.search(
            r'(<figure class="routine-figure">.*?</figure>|<div class="routine-intro-visual">.*?</div>)',
            overview,
            flags=re.I | re.S,
        )

    visual_html = visual.group(1)
    if visual_html.lower().startswith("<figure"):
        button = re.search(r'<button class="image-zoom".*?</button>', visual_html, flags=re.I | re.S)
        visual_html = f'<div class="routine-intro-visual">{button.group(0)}</div>' if button else visual_html
    guidance_html = (
        '<div class="routine-overview-guidance">'
        '<h3>When to use this routine</h3>'
        '<p>Use it before AI supports a school, workplace, or personal task, especially when information, safety, fairness, or other people may be affected.</p>'
        '<h3>Your next move</h3>'
        '<p>Study the five steps in the image. Choose one step you think is easiest to forget and explain why it matters.</p>'
        '<div class="routine-resource-buttons">'
        '<a href="https://drive.google.com/file/d/1ZU5oKUOuZtzy2pleGarrKHy60p8J_RS2/view?usp=drivesdk" target="_blank" rel="noopener">View accessible web version</a>'
        '<a href="https://drive.google.com/file/d/1P82VigGCzn5qVHIDCmn2E0EmWflxOZiR/view?usp=drivesdk" target="_blank" rel="noopener">Download print version</a>'
        '</div></div>'
    )
    replacement = (
        f'<div class="routine-overview-grid">{guidance_html}{visual_html}</div>'
    )
    return overview[:visual.start()] + replacement + overview[visual.end():]


def normalize_source_foundations(value: str) -> str:
    """Keep source material concise, consistently named, and collapsible."""
    def normalize(match: re.Match) -> str:
        block = match.group(0)
        if not re.search(r"<summary[^>]*>.*?(?:Source|Attribution|Acknowledgment).*?</summary>", block, flags=re.I | re.S):
            return block
        block = re.sub(r"<details\b(?![^>]*\bclass=)([^>]*)>", r'<details class="source-foundation"\1>', block, count=1, flags=re.I)
        block = re.sub(r'<details\b([^>]*?)class="([^"]*)"([^>]*)>', lambda m: f'<details{m.group(1)}class="{m.group(2)} source-foundation"{m.group(3)}>' if "source-foundation" not in m.group(2).split() else m.group(0), block, count=1, flags=re.I)
        block = re.sub(r"<summary[^>]*>.*?</summary>", "<summary>Source Foundation</summary>", block, count=1, flags=re.I | re.S)
        block = re.sub(r"<p\b[^>]*>.*?<strong[^>]*>\s*Acknowledgment:.*?</p>", "", block, flags=re.I | re.S)
        block = re.sub(r"<p\b[^>]*>\s*<strong[^>]*>\s*Source Foundation:.*?</p>", "", block, flags=re.I | re.S)
        block = re.sub(r"(</a>)\s*(?:&mdash;|—|â€”|-).*?(</li>)", r"\1\2", block, flags=re.I | re.S)

        def concise_paragraph(match: re.Match) -> str:
            paragraph = match.group(1)
            link = re.search(r'<a\b[^>]*href="([^"]+)"[^>]*>.*?</a>', paragraph, flags=re.I | re.S)
            if not link:
                return match.group(0)
            prefix = paragraph[:link.start()]
            label = re.sub(r"<[^>]+>", " ", prefix)
            label = re.sub(r"\s+", " ", html.unescape(label)).strip()
            label = re.split(r"\s+(?:—|â€”|-)\s+", label, maxsplit=1)[0].strip(" .,:;")
            if not label:
                label = re.sub(r"<[^>]+>", " ", link.group(0))
                label = re.sub(r"\s+", " ", html.unescape(label)).strip()
            return f'<li class="source-item"><a href="{html.escape(link.group(1), quote=True)}" target="_blank" rel="noopener">{html.escape(label)}</a></li>'

        block = re.sub(r"<p\b[^>]*>(.*?)</p>", concise_paragraph, block, flags=re.I | re.S)
        block = re.sub(
            r'((?:\s*<li class="source-item">.*?</li>)+)',
            lambda m: f'<ul class="source-list">{m.group(1)}</ul>',
            block,
            flags=re.I | re.S,
        )
        return block

    return re.sub(r"<details\b[^>]*>.*?</details>", normalize, value, flags=re.I | re.S)


def link_lesson_vocabulary(value: str, vocabulary: list[tuple[str, str]]) -> str:
    """Turn every visible occurrence of this lesson's vocabulary into a dialog trigger."""
    if not vocabulary:
        return value
    terms = sorted(vocabulary, key=lambda item: len(item[0]), reverse=True)
    definitions = {term.casefold(): definition for term, definition in terms}
    pattern = re.compile(r"(?<![\w])(" + "|".join(re.escape(term) for term, _ in terms) + r")(?![\w])", re.I)
    tokens = re.split(r"(<[^>]+>)", value)
    blocked = 0
    blocked_tags = {"a", "button", "details", "script", "style", "title"}
    for index, token in enumerate(tokens):
        if token.startswith("<"):
            tag = re.match(r"</?\s*([a-z0-9]+)", token, flags=re.I)
            if tag and tag.group(1).lower() in blocked_tags:
                blocked += -1 if token.lstrip().startswith("</") else (0 if token.rstrip().endswith("/>") else 1)
            continue
        if blocked or not token.strip():
            continue
        tokens[index] = pattern.sub(
            lambda m: (
                f'<button class="vocab-link" type="button" data-term="{html.escape(m.group(0), quote=True)}" '
                f'data-definition="{html.escape(definitions[m.group(0).casefold()], quote=True)}">{m.group(0)}</button>'
            ),
            token,
        )
    linked = "".join(tokens)

    def unlink_question(match: re.Match) -> str:
        return re.sub(
            r'<button class="vocab-link"[^>]*>(.*?)</button>',
            r"\1",
            match.group(0),
            flags=re.I | re.S,
        )

    return re.sub(
        r'<article class="question"[^>]*>.*?</article>',
        unlink_question,
        linked,
        flags=re.I | re.S,
    )


def accessibility_fragment(value: str) -> str:
    """Apply shared WCAG-oriented semantics to imported course HTML."""
    # Header cells inside a table head describe columns, not rows.
    value = re.sub(
        r"<thead\b[^>]*>.*?</thead>",
        lambda match: re.sub(r'scope=["\']row["\']', 'scope="col"', match.group(0), flags=re.I),
        value,
        flags=re.I | re.S,
    )

    # Wide imported tables need a keyboard-scrollable region at high zoom and
    # on small screens. Use the caption as the region name when one exists.
    def wrap_table(match: re.Match) -> str:
        table = match.group(0)
        caption = re.search(r"<caption\b[^>]*>(.*?)</caption>", table, flags=re.I | re.S)
        label = re.sub(r"<[^>]+>", " ", caption.group(1)) if caption else "Lesson information table"
        label = re.sub(r"\s+", " ", html.unescape(label)).strip()
        return (
            f'<div class="table-scroll" role="region" aria-label="{html.escape(label, quote=True)}" tabindex="0">'
            f"{table}</div>"
        )

    value = re.sub(r"<table\b[^>]*>.*?</table>", wrap_table, value, flags=re.I | re.S)
    return value


def make_images_zoomable(value: str) -> str:
    """Make imported lesson images operable at full size with mouse or keyboard."""
    matches = list(re.finditer(r"<img\b[^>]*>", value, flags=re.I))
    for match in reversed(matches):
        prefix = value[:match.start()]
        if prefix.rfind('<button class="image-zoom"') > prefix.rfind("</button>"):
            continue
        image = match.group(0)
        alt_match = re.search(r'alt="([^"]*)"', image, flags=re.I)
        label = "Enlarge instructional image"
        if alt_match and alt_match.group(1).strip():
            short_alt = re.sub(r"\s+", " ", html.unescape(alt_match.group(1))).strip()
            label = f"Enlarge image: {short_alt[:120]}"
        replacement = (
            f'<button class="image-zoom" type="button" aria-label="{html.escape(label, quote=True)}">'
            f"{image}</button>"
        )
        value = value[:match.start()] + replacement + value[match.end():]
    return value


def body_from_html(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"<body[^>]*>(.*)</body>", text, re.S | re.I)
    return clean_fragment(match.group(1) if match else text)


def metadata(node) -> dict[str, str]:
    result = {}
    for field in children(node, "qtimetadatafield"):
        label = first_text(field, "fieldlabel")
        result[label] = first_text(field, "fieldentry")
    return result


def extract_questions(path: Path) -> list[dict]:
    root = ET.parse(path).getroot()
    questions = []
    for item in children(root, "item"):
        meta = metadata(item)
        presentation = next((x for x in item if local_name(x.tag) == "presentation"), None)
        if presentation is None:
            continue
        prompt_node = next((x for x in presentation.iter() if local_name(x.tag) == "mattext"), None)
        prompt = clean_fragment(prompt_node.text if prompt_node is not None else item.get("title", ""))
        labels = children(presentation, "response_label")
        choices = []
        for label in labels:
            text_node = next((x for x in label.iter() if local_name(x.tag) == "mattext"), None)
            choices.append({"id": label.get("ident", ""), "html": clean_fragment(text_node.text if text_node is not None else "")})
        correct = []
        for varequal in children(item, "varequal"):
            if (varequal.text or "").strip():
                correct.append((varequal.text or "").strip())
        if meta.get("question_type") in {"multiple_choice_question", "multiple_answers_question"}:
            full_credit = next((
                condition for condition in children(item, "respcondition")
                if any(local_name(x.tag) == "setvar" and (x.text or "").strip() == "100" for x in condition.iter())
            ), None)
            if full_credit is not None:
                correct = positive_varequals(full_credit)
        matching_rows = []
        if meta.get("question_type") in {"matching_question", "categorization_question"}:
            correct_map = {
                varequal.get("respident", ""): (varequal.text or "").strip()
                for varequal in children(item, "varequal")
                if varequal.get("respident") and (varequal.text or "").strip()
            }
            for response in children(presentation, "response_lid"):
                row_material = next((x for x in response if local_name(x.tag) == "material"), None)
                row_text_node = next((x for x in row_material.iter() if local_name(x.tag) == "mattext"), None) if row_material is not None else None
                row_choices = []
                for response_label in children(response, "response_label"):
                    choice_text = next((x for x in response_label.iter() if local_name(x.tag) == "mattext"), None)
                    row_choices.append({"id": response_label.get("ident", ""), "html": clean_fragment(choice_text.text if choice_text is not None else "")})
                response_id = response.get("ident", "")
                matching_rows.append({
                    "id": response_id,
                    "label": clean_fragment(row_text_node.text if row_text_node is not None else ""),
                    "choices": row_choices,
                    "correct": correct_map.get(response_id, ""),
                })
        feedback = ""
        feedback_nodes = children(item, "itemfeedback")
        if feedback_nodes:
            feedback_text = next((x for x in feedback_nodes[0].iter() if local_name(x.tag) == "mattext"), None)
            feedback = clean_fragment(feedback_text.text if feedback_text is not None else "")
        questions.append({
            "id": item.get("ident", ""),
            "title": item.get("title", ""),
            "type": meta.get("question_type", "multiple_choice_question"),
            "prompt": prompt,
            "choices": choices,
            "correct": correct,
            "feedback": feedback,
            "matching_rows": matching_rows,
        })
    return questions


def approved_questions_for_step(step_label: str) -> list[dict]:
    """Return the reviewed question-bank records in the renderer's QTI-like shape."""
    if not LESSON_QUESTION_BANK_PATH.exists():
        return []
    payload = json.loads(LESSON_QUESTION_BANK_PATH.read_text(encoding="utf-8"))
    records = [
        record for record in payload.get("questions", [])
        if record.get("question_id", "").startswith(f"{step_label}.")
    ]
    records.sort(key=lambda record: int(record["question_id"].rsplit(".", 1)[1]))

    rendered = []
    for record in records:
        question_id = record["question_id"]
        question_type = record["question_type"]
        type_map = {
            "multiple_choice": "multiple_choice_question",
            "multiple_answer": "multiple_answers_question",
            "matching": "matching_question",
            "categorization": "categorization_question",
            "ordering": "ordering_question",
        }
        answers = [
            (chr(65 + index), str(record.get(f"answer_{index + 1}", "")).strip())
            for index in range(6)
        ]
        choices = [{"id": letter, "html": text} for letter, text in answers if text]
        correct = [part.strip() for part in str(record.get("correct_answer", "")).split(",") if part.strip()]
        matching_rows = []

        raw_pairs = str(record.get("match_pairs", "")).strip()
        pairs = []
        if raw_pairs:
            for part in re.split(r"[;\r\n]+", raw_pairs):
                if "=>" not in part:
                    continue
                left, right = (value.strip() for value in part.split("=>", 1))
                if left and right:
                    pairs.append((left, right))

        if question_type == "matching" and pairs:
            option_values = [(f"option-{index}", right) for index, (_, right) in enumerate(pairs, 1)]
            matching_rows = [
                {
                    "id": f"{question_id}-row-{index}",
                    "label": html.escape(left),
                    "choices": [{"id": option_id, "html": text} for option_id, text in option_values],
                    "correct": option_values[index - 1][0],
                }
                for index, (left, _) in enumerate(pairs, 1)
            ]
            choices = []
            correct = []
        elif question_type == "categorization" and pairs:
            categories = list(dict.fromkeys(left for left, _ in pairs))
            option_values = [(f"category-{index}", category) for index, category in enumerate(categories, 1)]
            category_ids = {category: option_id for option_id, category in option_values}
            matching_rows = [
                {
                    "id": f"{question_id}-row-{index}",
                    "label": html.escape(item),
                    "choices": [{"id": option_id, "html": text} for option_id, text in option_values],
                    "correct": category_ids[category],
                }
                for index, (category, item) in enumerate(pairs, 1)
            ]
            choices = []
            correct = []

        correct_feedback = str(record.get("feedback_correct", "")).strip()
        incorrect_feedback = str(record.get("feedback_incorrect", "")).strip()
        rendered.append({
            "id": question_id,
            "title": record.get("question_title", ""),
            "type": type_map[question_type],
            "prompt": f'<p>{html.escape(str(record["question_text"]).strip())}</p>',
            "choices": choices,
            "correct": correct,
            "feedback": f"<p>{html.escape(correct_feedback)}</p>" if correct_feedback else "",
            "feedback_correct_text": correct_feedback,
            "feedback_incorrect_text": incorrect_feedback,
            "matching_rows": matching_rows,
            "plain_text": True,
        })
    return rendered


def quiz_description(identifier: str) -> str:
    path = SOURCE / identifier / "assessment_meta.xml"
    if not path.exists():
        return ""
    root = ET.parse(path).getroot()
    desc = next((x for x in root.iter() if local_name(x.tag) == "description"), None)
    return clean_fragment(desc.text if desc is not None else "")


def module_lessons():
    root = ET.parse(SOURCE / "course_settings" / "module_meta.xml").getroot()
    output = {n: [] for n in range(1, 9)}
    current = None
    for item in children(root, "item"):
        title = first_text(item, "title")
        content_type = first_text(item, "content_type")
        if content_type == "ContextModuleSubHeader":
            match = re.search(r"Lesson\s+(\d+)", title)
            current = int(match.group(1)) if match else current
            continue
        if current not in output:
            continue
        ref = first_text(item, "identifierref")
        output[current].append({"title": title, "type": content_type, "ref": ref})
    return output


def step_number(step: dict, number: int, fallback: int) -> str:
    match = re.match(rf"\s*({number}\.\d+)", step["title"])
    return match.group(1) if match else f"{number}.{fallback}"


def legacy_human_decisions_simulation() -> str:
    banks = [
        ("Care and evidence", "g40021a10c569f3348b9974cc70df02fa"),
        ("Transportation and equipment", "gf52a7636e46a937855d4da46bb020557"),
        ("Skilled trades", "gebc041f85f656024f67a9dffc6a226a0"),
        ("Digital and design", "g1238be10fbcef09527dda86954b7317d"),
        ("Education and public service", "g221dd1c90c5750946e62adf240d5d5f1"),
        ("Hospitality and personal services", "g9cd543f18d7eab0d405d58cb47807b27"),
    ]
    cards = []
    for bank_index, (bank_title, bank_id) in enumerate(banks, 1):
        questions = extract_questions(SOURCE / "non_cc_assessments" / f"{bank_id}.xml.qti")
        for question_index, question in enumerate(questions, 1):
            choices = "".join(
                f'<label><input type="radio" name="scenario-{bank_index}-{question_index}" value="{html.escape(choice["id"])}"> <span>{choice["html"]}</span></label>'
                for choice in question["choices"]
            )
            cards.append(
                f'<article class="scenario-card" data-bank="{bank_index}" data-scenario-id="{html.escape(question["id"])}" '
                f'data-correct="{html.escape(json.dumps(question["correct"]))}" hidden>'
                f'<p class="scenario-category">Career category {bank_index} of 6 · {html.escape(bank_title)}</p>'
                f'{question["prompt"]}<div class="choices">{choices}</div>'
                f'<button class="scenario-check" type="button">Check decision</button>'
                f'<div class="feedback" role="status" hidden>{question["feedback"] or "Review the Human Decisions Map and try again."}</div></article>'
            )
    return (
        '<section class="scenario-simulation" aria-labelledby="simulation-title">'
        '<div class="simulation-header"><div><p class="eyebrow">Interactive simulation</p><h3 id="simulation-title">Human Decisions Workplace Cases</h3></div>'
        '<p class="simulation-count" aria-live="polite">Case <span>1</span> of 6</p></div>'
        '<p>One workplace case is selected from each career category. Use the Human Decisions Map to choose the response that keeps trained people responsible.</p>'
        f'<div class="scenario-deck">{"".join(cards)}</div>'
        '<div class="scenario-controls"><button class="step-button secondary scenario-previous" type="button">← Previous case</button>'
        '<button class="step-button scenario-next" type="button" disabled>Next case →</button></div>'
        '</section>'
    )


def human_decisions_simulation() -> str:
    """Return one required, career-program-specific responsible-AI decision pathway."""
    scenarios = [
        ("Agriscience - Vet Med", "An AI tool flags a dog's symptoms as a possible infection after a student enters notes from a visit.", "The tool could be wrong about the animal's condition.", "The animal owner's name and visit details.", "A qualified veterinary professional who can examine the animal.", "Use the AI result as one clue, then have a qualified veterinary professional examine the animal and review the evidence.", "The tool can identify patterns, but a qualified person must check the animal's condition and make the care decision."),
        ("Automotive - Medium Heavy Diesel", "A diagnostic tool suggests replacing a truck's fuel injector based on an error code.", "Replacing a part without testing could waste money or fail to fix the problem.", "The customer's identifying information and vehicle records that are not needed.", "A trained technician who can inspect and test the truck.", "Inspect the truck, compare the error code with test results, and have a trained technician decide on the repair.", "An error code can guide an inspection, but it does not replace testing or a trained technician's decision."),
        ("Aviation", "A planning tool recommends a route change because it predicts better weather conditions.", "A prediction could miss a weather or safety condition that affects the flight.", "Passenger information and any route details that should stay secure.", "A qualified person using approved weather, route, and safety information.", "Check approved weather, route, and safety information before a qualified person decides whether to change the plan.", "A recommendation is not a final flight decision. Approved sources and qualified human review are required."),
        ("Computer Science", "An AI coding assistant suggests a change that would give users more personalized results.", "The change could expose user information or create an unfair result.", "User data, account details, and private code that are not needed.", "A development team that can test the code and check privacy impacts.", "Review the code, test it with appropriate examples, and check whether it protects user information before using it.", "The team must test the suggestion and protect people's information before adding it to a product."),
        ("Construction Trades", "A tool predicts that a framing crew can finish a job faster by changing the work sequence.", "Changing the sequence could create a safety problem or conflict with the plans.", "Job-site security details and any private worker information.", "A trained supervisor who can check plans, conditions, and safety rules.", "Compare the suggestion with the plans, job-site conditions, and safety rules before a trained supervisor approves a change.", "Speed predictions cannot replace safety requirements, site conditions, or qualified supervision."),
        ("Cosmetology", "A scheduling tool recommends adding an extra client appointment to a stylist's day.", "The extra appointment could reduce service quality or ignore a client's needs.", "Client names, contact details, and service notes.", "The stylist who understands the schedule, client needs, and available time.", "Have the stylist review the schedule, client needs, and available time before deciding whether to add the appointment.", "The tool can organize options, but the person responsible for the service must decide what is realistic and appropriate."),
        ("Culinary", "A menu-planning tool suggests a new dish for an event based on popular online recipes.", "The dish could include an allergen or fail to fit the event's needs.", "Guest names, allergy details, and private event information.", "The chef who can check ingredients, equipment, cost, and event needs.", "Check ingredients, allergies, kitchen equipment, cost, and event needs before the chef decides whether to use the dish.", "A popular recipe may not fit the event. A trained person must check safety, resources, and the full situation."),
        ("Education", "A writing tool suggests that a student should receive extra reading support after reviewing a short assignment.", "One short sample could give an incomplete or unfair picture of the learner.", "The student's name, work, grades, and other personal information.", "An educator who can consider the student's work, progress, and needs.", "Use the suggestion as one piece of information, then have an educator review the student's work, progress, and needs before deciding on support.", "A short sample cannot show the whole learner. An educator must consider more evidence and make the support decision."),
        ("Health Science - Medical Careers", "An AI tool highlights a patient note as needing quick follow-up.", "The alert could be incomplete or could miss important details about the patient.", "The patient's name, health details, and other protected information.", "A qualified health professional using the patient record and approved procedures.", "Have a qualified health professional review the patient record, current condition, and approved procedures before deciding what happens next.", "The alert may help prioritize review, but it cannot make a care decision or replace professional judgment."),
        ("Marketing - Graphic Design", "An image tool creates a campaign graphic that includes a familiar-looking logo and a claim about a product.", "The graphic could use protected material or make an inaccurate claim.", "Client files, campaign plans, and private brand information.", "A person who can verify permissions and check claims with approved sources.", "Check permission to use the visual elements and verify the claim with approved sources before a person approves the graphic.", "A polished graphic still needs permission checks and accurate claims before it is shared."),
        ("Mechatronics", "A maintenance system predicts that a machine part may fail soon and suggests stopping the line immediately.", "Stopping the line or ignoring a real problem could affect safety and production.", "Private production details and any information not needed for maintenance.", "A trained person who can inspect the machine, sensor data, and safety procedures.", "Inspect the machine, compare the alert with sensor data and safety procedures, and have a trained person decide on the response.", "The prediction can guide maintenance, but qualified people must check the evidence and balance safety with the full work situation."),
        ("Public Safety", "A dispatch support tool ranks calls by predicted urgency.", "The ranking could miss details that change how quickly people need help.", "Names, addresses, and other sensitive call details.", "Trained staff who can review the details and decide how to respond.", "Use the ranking as one input, then have trained staff review the details and decide how to respond.", "Predictions can miss important context. Trained people must make the response decision and remain accountable."),
        ("US Army JROTC", "A planning tool suggests who should lead parts of a team exercise based on past performance notes.", "Past notes could be incomplete and lead to an unfair assignment.", "Personal performance notes and private student information.", "The instructor and team members who can consider current skills, goals, and fairness.", "Have the instructor and team review current skills, goals, and fairness before assigning leadership roles.", "Past notes do not tell the full story. People must make fair decisions and take responsibility for team roles."),
        ("Welding", "A tool recommends welding settings based on the material listed in a work order.", "The listed material or settings may not match the real job conditions.", "Work-order details and any private customer information.", "A trained welder who can check the material, equipment, and safety procedures.", "Check the actual material, equipment condition, job requirements, and safety procedures before a trained welder sets up the work.", "The tool may offer a starting point, but a trained welder must verify the real conditions and follow safety procedures."),
        ("Forensic Science", "A software tool marks part of a comparison image as a possible match.", "A possible match could be mistaken for proof.", "Case details, identifying information, and evidence not approved for sharing.", "A qualified expert using approved methods and documented review.", "Treat the result as a lead, then use approved methods and qualified expert review before drawing any conclusion.", "A possible match is not proof. Evidence needs careful human review and documented methods."),
    ]

    def choice_set(name: str, correct_text: str, distractors: list[str]) -> str:
        choices = [(correct_text, True), *((text, False) for text in distractors)]
        return ''.join(
            f'<label><input type="radio" name="{name}" value="{choice_index}"> <span>{html.escape(choice)}</span></label>'
            for choice_index, (choice, _correct) in enumerate(choices, 1)
        )

    cards = []
    for index, (program, situation, risk, protect, reviewer, responsible_action, feedback) in enumerate(scenarios, 1):
        risk_choices = choice_set(f'program-risk-{index}', risk, [
            'There is no risk because the tool used data.',
            'The only concern is whether the screen looks professional.',
            'The tool should make the final decision as quickly as possible.',
        ])
        protect_choices = choice_set(f'program-protect-{index}', protect, [
            'Nothing; every detail should be entered to get a better answer.',
            'Only the color of the tool interface.',
            'Information is private only after a final decision is made.',
        ])
        review_choices = choice_set(f'program-review-{index}', reviewer, [
            'The AI tool, because it created the suggestion.',
            'Anyone who is available, even if they do not understand the situation.',
            'No one; the first recommendation should be accepted.',
        ])
        cards.append(
            f'<article class="scenario-card program-scenario-card" data-program="{html.escape(program)}" hidden>'
            f'<p class="scenario-category">Your selected program: {html.escape(program)}</p>'
            f'<p><strong>Situation:</strong> {html.escape(situation)}</p>'
            '<div class="decision-pathway">'
            f'<section class="decision-pathway-step" data-correct="[&quot;1&quot;]"><p class="pathway-label">1. Spot the risk</p><p>What is the most important concern to check first?</p><div class="choices">{risk_choices}</div><button class="scenario-check" type="button">Check my thinking</button><div class="feedback" role="status" hidden></div></section>'
            f'<section class="decision-pathway-step" data-correct="[&quot;1&quot;]" hidden><p class="pathway-label">2. Protect information</p><p>What information should stay private or be left out of an AI prompt?</p><div class="choices">{protect_choices}</div><button class="scenario-check" type="button">Check my thinking</button><div class="feedback" role="status" hidden></div></section>'
            f'<section class="decision-pathway-step" data-correct="[&quot;1&quot;]" hidden><p class="pathway-label">3. Choose the human check</p><p>Who should review the AI suggestion before a decision is made?</p><div class="choices">{review_choices}</div><button class="scenario-check" type="button">Check my thinking</button><div class="feedback" role="status" hidden></div></section>'
            f'<section class="decision-pathway-step decision-pathway-reflection" hidden><p class="pathway-label">4. Make and explain the decision</p><label for="program-explain-{index}">In one or two sentences, explain how AI could help and what a person must do before the final decision.</label><textarea id="program-explain-{index}" rows="4"></textarea><button class="scenario-exemplar" type="button">Compare with an exemplar</button><div class="feedback exemplar-feedback" role="status" hidden><strong>Compare your response with this exemplar:</strong> {html.escape(responsible_action)} <span>{html.escape(feedback)}</span></div></section>'
            '</div></article>'
        )
    options = "".join(f'<option value="{index}">{html.escape(program)}</option>' for index, (program, *_rest) in enumerate(scenarios, 1))
    return (
        '<section class="scenario-simulation program-scenario-simulation" data-feedback-mode="program-scenario" aria-labelledby="program-scenario-title">'
        '<div class="simulation-header"><div><p class="eyebrow">Interactive practice</p><h3 id="program-scenario-title">Make a Responsible AI Decision</h3></div>'
        '<p class="simulation-count" aria-live="polite">Choose a program</p></div>'
        '<p>Select the program that fits you best. Work through a four-part decision pathway, then compare your explanation with an exemplar.</p>'
        '<div class="media-program-picker program-scenario-picker"><label for="program-scenario-select">Your program</label>'
        f'<select id="program-scenario-select" class="media-program-select program-scenario-select"><option value="">Choose a program</option>{options}</select>'
        '<button class="step-button program-scenario-start" type="button" disabled>Start my scenario</button>'
        '<p class="media-program-help">After you complete your scenario, you may choose another program for optional practice.</p></div>'
        f'<div class="scenario-deck" hidden>{"".join(cards)}</div>'
        '<div class="media-audit-actions program-scenario-actions" hidden><p><strong>Your required scenario is complete.</strong> You may stop here or choose another program for optional practice.</p>'
        '<button class="step-button secondary program-scenario-another" type="button">Choose another program</button></div>'
        '</section>'
    )


def media_audit_simulation(questions: list[dict]) -> str:
    cards = []
    program_options = []
    decisions = {
        'Welding': 'Revise',
        'Agriscience and Veterinary Medicine': 'Hold for verification',
        'Public Safety': 'Revise',
        'Mechatronics': 'Hold for verification',
        'Marketing and Graphic Design': 'Hold for verification',
        'U.S. Army JROTC': 'Reject',
        'Health Science and Medical Careers': 'Hold for verification',
        'Forensic Science': 'Revise',
        'Education': 'Revise',
        'Culinary Arts': 'Hold for verification',
        'Construction Trades': 'Hold for verification',
        'Computer Science': 'Hold for verification',
        'Cosmetology': 'Reject',
        'Automotive and Medium/Heavy Diesel': 'Reject',
        'Aviation': 'Reject',
    }
    for index, question in enumerate(questions, 1):
        program_match = re.search(r'<h3>(.*?) Media Audit</h3>', question["prompt"], re.I | re.S)
        program = html.unescape(re.sub(r'<[^>]+>', '', program_match.group(1))).strip() if program_match else f'Program {index}'
        feedback_text = html.unescape(re.sub(r'<[^>]+>', '', question["feedback"])).strip()
        problem_match = re.match(r'\s*Image\s+([AB])\s+needs review', feedback_text, re.I)
        problem_image = problem_match.group(1).upper() if problem_match else 'A'
        other_image = 'B' if problem_image == 'A' else 'A'
        decision = decisions.get(program, 'Hold for verification')
        concern_match = re.search(r'Main concern:\s*(.*?)\s*Responsible next step:', feedback_text, re.I | re.S)
        next_step_match = re.search(r'Responsible next step:\s*(.*)$', feedback_text, re.I | re.S)
        concern = concern_match.group(1).strip() if concern_match else 'The image includes a claim or detail that needs review.'
        responsible_next_step = next_step_match.group(1).strip() if next_step_match else 'Check the image with a trusted source or qualified expert.'
        prompt = re.sub(
            r'<p><strong>Which assessment and next step are most appropriate\?</strong></p>\s*$',
            '',
            question["prompt"],
            flags=re.I,
        )
        question_name = f'media-audit-{index}'

        def audit_question(number: int, legend: str, correct: str, distractors: list[str]) -> str:
            answers = [correct, *distractors]
            choices = ''.join(
                f'<label><input type="radio" name="{question_name}-{number}" value="{choice_index}"> '
                f'<span>{html.escape(answer)}</span></label>'
                for choice_index, answer in enumerate(answers)
            )
            return (
                f'<fieldset class="audit-question" data-correct="0"><legend>{number}. {html.escape(legend)}</legend>'
                f'<div class="choices">{choices}</div></fieldset>'
            )

        guided_questions = (
            audit_question(1, 'Which image has the most obvious concern?', f'Image {problem_image}',
                           [f'Image {other_image}', 'Both images are ready to approve', 'Neither image can be reviewed'])
            + audit_question(2, 'What is the main concern?', concern, [
                'The image uses colors that may not match the program brand.',
                'The image does not prove whether it was made with AI.',
                'The two images use different layouts.',
            ])
            + audit_question(3, f'What review decision fits Image {problem_image} best?', decision,
                           [option for option in ['Approve', 'Revise', 'Reject', 'Hold for verification'] if option != decision][:3])
            + audit_question(4, 'What should the reviewer do next?', responsible_next_step, [
                'Approve it because it looks polished.',
                'Use an AI detector score as final proof.',
                'Share it first and check the evidence later.',
            ])
        )
        program_options.append(f'<option value="{index}">{html.escape(program)}</option>')
        cards.append(
            f'<article class="scenario-card media-audit-card" data-bank="{index}" data-program="{html.escape(program)}" hidden>'
            f'{prompt}<div class="audit-question-list">{guided_questions}</div>'
            '<button class="scenario-check" type="button">Check my comparison</button>'
            f'<div class="feedback" role="status" hidden>{question["feedback"]} '
            f'Image {other_image} has no obvious visual concern, but appearance alone does not prove that it is ready. '
            'A reviewer must still check its source, claims, permissions, context, and intended use.</div></article>'
        )
    return (
        '<section class="scenario-simulation media-audit-simulation" data-feedback-mode="media-audit" '
        'aria-labelledby="media-audit-title">'
        '<div class="simulation-header"><div><p class="eyebrow">Interactive image comparison</p>'
        '<h3 id="media-audit-title">Career Program Media Audit</h3></div>'
        '<p class="simulation-count" aria-live="polite">Choose your program</p></div>'
        '<p>Study one image pair from your career program. Four questions will guide you through the clues, concern, review decision, and responsible next step.</p>'
        '<div class="media-program-picker"><label for="media-program-select"><strong>Select your career program</strong></label>'
        f'<select id="media-program-select" class="media-program-select"><option value="">Choose a program</option>{"".join(program_options)}</select>'
        '<button class="step-button media-audit-start" type="button" disabled>Start my comparison</button>'
        '<p class="media-program-help">Finish this comparison before choosing another program for optional practice.</p></div>'
        f'<div class="scenario-deck" hidden>{"".join(cards)}</div>'
        '<div class="scenario-controls" hidden><button class="step-button secondary scenario-previous" type="button">← Previous comparison</button>'
        '<button class="step-button scenario-next" type="button" disabled>Next comparison →</button></div>'
        '<div class="media-audit-actions" hidden><p>You completed your program comparison. You may stop here or practice with another program.</p>'
        '<button class="step-button secondary media-audit-another" type="button">Choose another program</button></div>'
        '</section>'
    )


def add_check_next_move(value: str) -> str:
    """Place one heading-free next-step box immediately before a question set."""
    value = re.sub(
        r'<div[^>]*>(?:(?!<div\b|</div>)[\s\S])*?Your next move:'
        r'(?:(?!<div\b|</div>)[\s\S])*?Complete (?:the )?(?:checks|questions)'
        r'(?:(?!<div\b|</div>)[\s\S])*?</div>',
        "",
        value,
        flags=re.I,
    )
    def remove_check_heading(match: re.Match) -> str:
        heading_text = re.sub(r"<[^>]+>", " ", match.group(0))
        return "" if "check for understanding" in " ".join(heading_text.split()).lower() else match.group(0)

    value = re.sub(r'<h([2-4])\b[^>]*>.*?</h\1>', remove_check_heading, value, flags=re.I | re.S)
    value = re.sub(
        r'<p[^>]*>\s*(?:<strong[^>]*>)?\s*(?:✏️\s*)?Check for Understanding:?\s*(?:</strong>)?\s*</p>',
        "",
        value,
        flags=re.I,
    )
    box = (
        '<div class="check-next-move" style="border: 2px solid #2980B9; background-color: #F2F9FD; '
        'padding: 14px 16px; border-radius: 8px; margin: 18px 0 12px 0;">'
        '<p style="margin: 0; color: #222222;"><strong style="color: #005A70;">✅ Your next move:</strong> '
        'Complete the checks for understanding below. Use the feedback to review your answer before continuing.</p></div>'
    )
    return value.rstrip() + box


ROUTINE_ALT = (
    "Responsible AI Routine: 1 Goal—What am I trying to do? "
    "2 Protect—What should stay private? 3 Use—How can AI help? "
    "4 Check—Is it accurate and safe? 5 Own—Who is responsible in the end?"
)
ASSET_VERSION = "20260814-link-contrast"
ROUTINE_WEB_URL = "https://drive.google.com/file/d/1ZU5oKUOuZtzy2pleGarrKHy60p8J_RS2/view?usp=drivesdk"
ROUTINE_PRINT_URL = "https://drive.google.com/file/d/1P82VigGCzn5qVHIDCmn2E0EmWflxOZiR/view?usp=drivesdk"
FEEDBACK_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdSzdOE6ONsmktbDhx8tdDnaN6dhNoUTnA3qFYDOVGzdjkrqA/viewform"
FEEDBACK_LOCATION_PARAM = "entry.1955824508"


def feedback_link(number: int, step_label: str, title: str) -> str:
    """Return a short, prefilled feedback invitation for a lesson step."""
    location = f"Lesson {number}, Step {step_label}: {title}"
    query = urlencode({
        "usp": "pp_url",
        FEEDBACK_LOCATION_PARAM: location,
    })
    url = html.escape(f"{FEEDBACK_FORM_URL}?{query}", quote=True)
    return (
        '<aside class="lesson-feedback" aria-label="Feedback for this lesson step">'
        '<p><strong>Help improve this step.</strong> Did something work well, feel unclear, or need to be fixed?</p>'
        f'<a class="lesson-feedback-link" href="{url}" target="_blank" rel="noopener">'
        'Share feedback on this step <span class="sr-only">(opens feedback form in a new tab)</span></a>'
        '</aside>'
    )


def append_feedback_link(section: str, number: int) -> str:
    """Add one feedback link immediately before a generated step closes."""
    label_match = re.search(r'data-step-label="([^"]+)"', section)
    title_match = re.search(r'<h2[^>]*>(.*?)</h2>', section, flags=re.I | re.S)
    if not label_match or not section.rstrip().endswith("</section>"):
        return section
    step_label = html.unescape(label_match.group(1))
    title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip() if title_match else "Lesson overview"
    while True:
        decoded_title = html.unescape(title)
        if decoded_title == title:
            break
        title = decoded_title
    return section.rstrip()[:-10] + feedback_link(number, step_label, title) + "</section>"


def routine_figure(caption: str) -> str:
    """Return the shared routine visual with an accessible enlargement control."""
    return (
        '<figure class="routine-figure">'
        '<button class="image-zoom" type="button" aria-label="Enlarge the Responsible AI Routine image">'
        f'<img src="../assets/media/Responsible_AI_Routine_Web_Mobile_1200px.png" alt="{html.escape(ROUTINE_ALT, quote=True)}" loading="eager" decoding="async">'
        '</button>'
        f'<figcaption>{html.escape(caption)} Select the image to enlarge it. '
        '<span class="routine-links">'
        f'<a href="{ROUTINE_WEB_URL}" target="_blank" rel="noopener">Open web/mobile version</a>'
        '<span aria-hidden="true"> · </span>'
        f'<a href="{ROUTINE_PRINT_URL}" target="_blank" rel="noopener">Open print-quality version</a>'
        '</span></figcaption>'
        '</figure>'
    )


def instructional_figure(src: str, alt: str, caption: str) -> str:
    """Return a step-specific instructional image with context and enlargement."""
    return (
        '<figure class="instructional-figure">'
        f'<button class="image-zoom" type="button" aria-label="Enlarge image: {html.escape(alt[:120], quote=True)}">'
        f'<img src="../assets/media/{html.escape(src, quote=True)}" alt="{html.escape(alt, quote=True)}" loading="eager" decoding="async">'
        '</button>'
        f'<figcaption>{html.escape(caption)} Select the image to enlarge it.</figcaption>'
        '</figure>'
    )


def graphic_resource_links(*links: tuple[str, str]) -> str:
    """Return links to alternate graphic formats stored with the course."""
    items = " · ".join(
        f'<a href="../assets/media/exports/{html.escape(filename, quote=True)}" target="_blank" rel="noopener">{html.escape(label)}</a>'
        for label, filename in links
    )
    return f'<p class="graphic-resource-links"><strong>Graphic formats:</strong> {items}</p>'


def lesson_7_4_content() -> str:
    """Return a concise, learner-centered sequence for Step 7.4."""
    return '''<div class="impact-lesson">
<div class="step-intro"><p><strong>Estimated time:</strong> 11 minutes</p><p>AI can create benefits and costs at the same time. Your job is to examine the full impact before deciding whether a use is responsible.</p></div>
<div class="check-next-move"><p><strong>▶️ Your next move:</strong> While viewing, identify one AI benefit and one challenge that could affect groups of people differently.</p></div>
<div class="video-wrap"><iframe allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen src="https://www.youtube-nocookie.com/embed/olf-MrpLZCY?cc_load_policy=1" title="AI Literacy: AI and the Future of Society"></iframe></div>
<p class="video-access"><a href="https://www.youtube.com/watch?v=olf-MrpLZCY" target="_blank" rel="noopener">Watch directly on YouTube</a></p>
<h3>Use four impact questions</h3>
<div class="impact-grid">
<section><h4>1. Work and skills</h4><p>What time could be saved? What skills could grow, weaken, or change?</p></section>
<section><h4>2. People and fairness</h4><p>Who benefits? Who could be harmed or excluded? Who can question a result?</p></section>
<section><h4>3. Access</h4><p>Can people use the tool across devices, languages, disabilities, costs, and training levels?</p></section>
<section><h4>4. Resources and environment</h4><p>What energy, cooling water, equipment, and replacement waste may be required?</p></section>
</div>
<p class="impact-context"><strong>Important:</strong> Impact estimates change with the model, task, hardware, data center, power source, and amount of use. Use estimates for comparison, not as exact measurements.</p>
<div class="calculator-task"><h3>Try the Everyday AI Impact calculator</h3><ol><li><a href="https://geneseelearninglab.com/AIImpact.html" target="_blank" rel="noopener">Open the calculator</a>.</li><li>Choose one AI activity and record the estimate for one use.</li><li>Change the amount to 2,000 uses and compare the energy, phone-battery, and water estimates.</li><li>Name one safeguard that could reduce unnecessary use or improve access.</li></ol></div>
<div class="decision-check"><h3>Make a responsible recommendation</h3><p>State the <strong>benefit</strong>, the most important <strong>cost or risk</strong>, one <strong>safeguard</strong>, and the <strong>trained person</strong> who should review the result.</p></div>
<details class="source-foundation"><summary>Sources and Source Foundation</summary><div><ul><li><a href="https://www.youtube.com/watch?v=olf-MrpLZCY" target="_blank" rel="noopener">Michigan Virtual: AI and the Future of Society</a></li><li><a href="https://www.iea.org/reports/key-questions-on-energy-and-ai" target="_blank" rel="noopener">International Energy Agency: Key Questions on Energy and AI</a></li><li><a href="https://www.itu.int/en/ITU-D/Environment/Pages/Publications/The-Global-E-waste-Monitor-2024.aspx" target="_blank" rel="noopener">ITU: Global E-waste Monitor 2024</a></li><li><a href="https://doi.org/10.6028/NIST.AI.100-1" target="_blank" rel="noopener">NIST AI Risk Management Framework</a></li><li><a href="https://doi.org/10.54394/QFBQ1907" target="_blank" rel="noopener">International Labour Organization: Generative AI and Jobs</a></li></ul></div></details>
</div>'''


def step_html(step: dict, number: int, index: int) -> str:
    title = re.sub(r"^\d+\.\d+\s*[^A-Za-z0-9]*\s*", "", step["title"]).strip()
    step_label = step_number(step, number, index)
    title = STEP_TITLES.get(step_label, title).replace(" — ", ": ")
    if step["type"] == "WikiPage":
        return ""
    if step["type"] == "Assignment":
        folder = SOURCE / step["ref"]
        candidates = list(folder.glob("*.html"))
        content = body_from_html(candidates[0]) if candidates else "<p>Complete the applied learning task described by your instructor.</p>"
        # Assignment pages begin with the generated step h2, so imported
        # subsection headings belong at h3 rather than skipping to h4.
        content = re.sub(r"<(/?)h4\b", r"<\1h3", content, flags=re.I)
        assignment_routine_captions = {
            "8.5": "Use the routine to guide your final model decisions and reflection.",
        }
        if step_label in assignment_routine_captions:
            content = routine_figure(assignment_routine_captions[step_label]) + content
        if step_label == "6.5":
            content = re.sub(
                r'<div[^>]*>\s*<strong[^>]*>Responsible AI Routine:</strong>\s*<span>.*?</span>\s*</div>',
                "",
                content,
                count=1,
                flags=re.I | re.S,
            )
        if step_label == "5.5":
            content = instructional_figure(
                "Minimum_Necessary_Data_1600x1000.png",
                "Minimum necessary data example. A prompt with a fictional full name, phone number, account number, employer file detail, and exact incident date is changed into a safer prompt using only a general role, fictional situation, and task goal. The safer version confirms permission, removes identifying details, and uses an approved tool.",
                "Compare the two fictional prompts. Remove details that the task does not require before entering information into an approved tool.",
            ) + content
        if step_label == "4.5":
            content = instructional_figure(
                "M01_AIReviewBoard_v1.png",
                "Five-step AI Review Board investigation: identify the AI role, find possible harm, require a human check, create a safer rule, and give a verdict.",
                "Use these five steps to investigate the workplace AI case before giving your verdict.",
            ) + graphic_resource_links(
                ("Open mobile version", "AI_Review_Board_Mobile_1200x900.png"),
                ("Open print version", "AI_Review_Board_Print_8.5x11.png"),
            ) + content
        if step_label == "8.5":
            content = content.replace("1. Select Your Program", "1. Choose Your Program Group")
            content = content.replace(
                "Find your career program below to see which simulation path you will follow.",
                "Choose the program group that best matches your current program or career interest. You make this choice. In the simulation, select the same group number shown in the table.",
            )
            content = content.replace("Program Track:", "Program Choice:")
            content = content.replace(
                "Which career program did you choose, and what was the main flaw or missing data in the Initial Model?",
                "Which program group did you choose? Name the career area and explain the main flaw or missing data you found in the Initial Model.",
            )
            content = content.replace(
                "Launch the simulation, select your program, and review your initial training data.",
                "Launch the simulation, select the program group you chose from the table, and review its initial training data.",
            )
            content = content.replace(
                "Work through the steps for your program, then return to this lesson to answer the reflection questions below.",
                "Complete the simulation using your chosen program group. Then return to this lesson and answer the four visible reflection questions.",
            )
        if step_label == "4.5":
            content = re.sub(
                r"<strong>Step 2: Submit Your Answers\.</strong>\s*Answer these 5 questions(?: in the text box below| and submit your answers in the course)?:",
                "<strong>Step 2: Prepare Your Reflection.</strong> Use the five questions below to plan a complete response:",
                content,
                flags=re.I,
            )
            content += (
                '<div class="check-next-move" style="border: 2px solid #2980B9; background-color: #F2F9FD; '
                'padding: 14px 16px; border-radius: 8px; margin: 18px 0 12px 0;">'
                '<p style="margin: 0; color: #222222;"><strong style="color: #005A70;">✅ Your next move:</strong> '
                'Return to your course and complete the Step 4.5 reflection question assignment. Include answers to all five reflection questions.</p></div>'
            )
        if '<div class="question-set">' in content:
            before, after = content.split('<div class="question-set">', 1)
            content = add_check_next_move(before) + '<div class="question-set">' + after
        handoff = "" if step_label in {"2.5", "4.5", "5.5", "6.5", "7.5", "8.5"} else classroom_handoff()
        return f'<section class="lesson-step classroom-activity" id="step-{step_label.replace(".", "-")}" data-step-label="{step_label}" hidden><p class="eyebrow">Step {step_label} · Practical application</p><h2>{html.escape(title)}</h2>{content}{handoff}</section>'
    qti = SOURCE / "non_cc_assessments" / f'{step["ref"]}.xml.qti'
    questions = approved_questions_for_step(step_label)
    if not questions:
        questions = extract_questions(qti) if qti.exists() else []
    desc = quiz_description(step["ref"])
    if step_label == "7.4":
        desc = lesson_7_4_content()
    lesson_two_graphics = {
        "2.3": (
            "M01_5TipPromptFormula_v1.png",
            "Five-tip prompting formula: Specificity, Role, Format, Interactive Questions, and Tone.",
            "Use this formula to choose the prompt details that fit your goal; every prompt does not need all five tips.",
        ),
        "2.4": (
            "M01_3StepAuditProcess_v1.png",
            "Three-step AI response audit: Check Facts, Find Gaps, and Ask Again.",
            "Use this three-step process to check an AI response and improve what is missing or incorrect.",
        ),
    }
    if step_label in lesson_two_graphics:
        desc += instructional_figure(*lesson_two_graphics[step_label])
        lesson_two_exports = {
            "2.3": (
                ("Open mobile version", "Five_Tip_Prompting_Formula_Mobile_1200x675.png"),
                ("Open print version", "Five_Tip_Prompting_Formula_Print_8.5x11.png"),
            ),
            "2.4": (
                ("Open mobile version", "Three_Step_Audit_Process_Mobile_1200x675.png"),
                ("Open print version", "Three_Step_Audit_Process_Print_8.5x11.png"),
            ),
        }
        desc += graphic_resource_links(*lesson_two_exports[step_label])
    phase_two_graphics = {
        "6.3": (
            "Copyright_Permission_Decision_Path_1100x1726.png",
            "Copyright and permission decision path: identify whether every part is your own; if not, confirm permission or a license; include required credit; disclose AI help; and stop to get permission, replace material, or ask for help when permission is missing.",
            "Follow each decision before you use or share work. Finding something online does not give you permission to use it.",
        ),
        "7.3": (
            "AI_Task_Change_Continuum_1600x900.png",
            "AI task change continuum from an automated step, where AI handles a narrow repeated action, to augmented work, where AI supports a person, to a human-led decision, where a trained person reviews evidence, context, and consequences.",
            "Use the continuum to decide how much human judgment and review a task needs.",
        ),
        "7.4": (
            "Career_Impact_Balance_Map_1600x1200.png",
            "Full-impact map connecting a proposed AI use to Work and Skills, People and Fairness, Access, and Resources and Environment, followed by the question: What safeguards would improve the outcome?",
            "Consider all four areas before judging the effect of an AI use on a career or workplace.",
        ),
    }
    if step_label in phase_two_graphics:
        desc += instructional_figure(*phase_two_graphics[step_label])
    if step_label == "3.3":
        desc += instructional_figure(
            "Verify_Before_You_Trust_1600x700.png",
            "Verify Before You Trust process: 1 Pause and identify what makes you uncertain; 2 Trace where the media came from; 3 Check what reliable evidence shows; 4 Decide whether it is accurate, safe, and appropriate to use; 5 Disclose what others should know about its source or AI use. No single clue or detector score is final proof.",
            "Use the five steps whenever you investigate media. Follow the process instead of treating one clue or detector score as final proof.",
        )
    if step_label == "7.3":
        desc += instructional_figure(
            "Career_Task_AI_Role_1600x1000.png",
            "Fictional maintenance-request comparison. Before AI support, people sort requests, draft summaries, review evidence, and decide. With responsible AI support, AI groups requests and drafts a summary, while a trained supervisor checks evidence and decides. People remain responsible for correcting errors, considering safety and context, and approving the final action.",
            "Compare the same task before and after AI support. Identify what became faster and what responsibility remained with trained people.",
        )
    phase_three_graphics = {
        "6.4": (
            "AI_Use_Disclosure_Anatomy_1600x900.png",
            "Annotated AI-use disclosure: I used an approved AI tool to brainstorm three headings. I chose one heading, wrote the full draft, checked the facts, and revised the final work. Callouts identify the tool or type of help, the specific task AI performed, the student's work, and the checking and revision.",
            "Use the four callouts to identify what a clear AI-use disclosure should explain. Follow your course or workplace rules.",
        ),
        "8.2": (
            "Uneven_Outcomes_Comparison_1600x900.png",
            "Fictional practice data showing 90 percent overall model accuracy while Test Group A scores 96 percent, Test Group B scores 91 percent, and Test Group C scores 68 percent. Review questions ask whether each group is represented, which errors matter most, and what must improve before use.",
            "Compare the group results with the overall score. Notice what the 90 percent summary hides and decide what must be reviewed before use.",
        ),
    }
    if step_label in phase_three_graphics:
        desc += instructional_figure(*phase_three_graphics[step_label])
    lesson_four_graphics = {
        "4.3": (
            "M01_BiasRedFlags_v1.png",
            "Quick bias red flags: stereotypes, missing groups or situations, unsupported assumptions, unequal treatment, hidden uncertainty, and possible effects on health, safety, rights, money, education, reputation, employment, or the future.",
            "Use these red flags to decide when an AI result needs a closer investigation. A red flag is a reason to check evidence, not proof of bias by itself.",
        ),
        "4.4": (
            "M01_HumanOversightFlowchart_v1.png",
            "Human oversight flowchart for deciding when an AI output needs review, more information, safeguards, correction, or a stop before use.",
            "Follow the flowchart before a result affects a person. Use it to identify who must review the evidence and who has authority to correct, stop, or approve the decision.",
        ),
    }
    if step_label in lesson_four_graphics:
        filename = lesson_four_graphics[step_label][0]
        desc = re.sub(
            rf'<div[^>]*>\s*<button class="image-zoom"[^>]*>\s*<img[^>]+{re.escape(filename)}[^>]*>\s*</button>\s*</div>',
            "",
            desc,
            count=1,
            flags=re.I | re.S,
        )
        desc += instructional_figure(*lesson_four_graphics[step_label])
    if step_label == "8.3":
        desc = re.sub(
            r'<p[^>]*>Building an AI model is a cycle that repeats\. Review the five steps below.*?</div>\s*<p[^>]*>As you answer the reflection questions below, think about how each step in this cycle helps make an AI system more accurate and reliable\.</p>',
            (
                '<p>Building an AI model is a cycle that repeats. People define the goal, prepare data, train and test the model, improve it, and monitor how it is used.</p>'
                + instructional_figure(
                    "Six_Step_Model_Building_Cycle_1600x1200.png",
                    "Six-step model-building cycle: 1 Define the goal and success criteria; 2 Collect and prepare appropriate data; 3 Train the model; 4 Test results and compare groups; 5 Improve data, rules, or training; 6 Monitor use and keep human responsibility. The cycle returns to step 1, and people make choices at every step.",
                    "Trace the cycle from Define through Monitor. Notice that human choices and responsibility continue at every step.",
                )
                + graphic_resource_links(
                    ("Open mobile version", "Six_Step_Model_Building_Cycle_Mobile_1200x1800.png"),
                    ("Open print version", "Six_Step_Model_Building_Cycle_Print_8.5x11.png"),
                )
                + '<ol class="graphic-text-equivalent"><li><strong>Define:</strong> Set the goal and success criteria.</li><li><strong>Collect:</strong> Gather and prepare appropriate data.</li><li><strong>Train:</strong> Build the model from the prepared examples.</li><li><strong>Test:</strong> Check results and compare performance across groups or conditions.</li><li><strong>Improve:</strong> Change the data, rules, or training when evidence shows a problem.</li><li><strong>Monitor:</strong> Review real use and keep people responsible for decisions.</li></ol>'
                + '<p>As you answer the questions below, think about how each step helps people find problems and improve the system.</p>'
            ),
            desc,
            count=1,
            flags=re.I | re.S,
        )
    if step_label == "5.2":
        desc += (
            '<div class="routine-text-cue"><p><strong>Responsible AI Routine reminder:</strong> '
            'Goal → Protect → Use → Check → Own</p><p>For this step, focus on <strong>Protect</strong>: '
            'confirm permission and use only the information the task requires.</p></div>'
        )
    if step_label == "1.5":
        desc = (
            '<p>In this activity, you will decide how AI can support a workplace task without replacing human judgment.</p>'
            '<div class="next-move"><p>👀 <strong>Your next move:</strong> Study the map, then use it to guide each part of your decision pathway.</p></div>'
        )
        desc += instructional_figure(
            "Human_Decisions_Map_1600x1000.png",
            "Human Decisions Map: AI may help sort information, find patterns, draft options, or make a recommendation. A trained person must check evidence, consider the full situation, make high-impact decisions, and take responsibility. More human review is needed as effects on health, safety, rights, money, education, reputation, or the future increase.",
            "Use this map to decide what AI may help with and what a trained person must review or decide in each case.",
        )
        return f'<section class="lesson-step classroom-activity" id="step-1-5" data-step-label="1.5" hidden><p class="eyebrow">Step 1.5 · Practical application</p><h2>{html.escape(title)}</h2>{desc}{human_decisions_simulation()}</section>'
    if step_label == "3.5" and qti.exists():
        desc = desc.replace('For each image:', 'For each comparison:')
        desc = desc.replace('Decide whether it is ready to use.', 'Identify which image has an obvious concern.')
        desc = desc.replace('Choose the most responsible next step.', 'Choose the strongest review decision and the evidence or expert to check next.')
        desc = desc.replace(
            'You are evaluating the image for accuracy, safety, permission, and privacy — not trying to determine whether it was created by AI.',
            'You are evaluating accuracy, safety, permission, privacy, and context — not trying to determine whether AI created an image. A polished image still needs normal verification before approval.',
        )
        qti_text = qti.read_text(encoding="utf-8")
        bank_match = re.search(r"<sourcebank_ref>([^<]+)</sourcebank_ref>", qti_text)
        bank_questions = []
        if bank_match:
            bank_path = SOURCE / "non_cc_assessments" / f"{bank_match.group(1)}.xml.qti"
            if bank_path.exists():
                bank_questions = [q for q in extract_questions(bank_path) if re.search(r"<img\b", q["prompt"], flags=re.I)]
        next_move = (
            '<div class="check-next-move" style="border: 2px solid #2980B9; background-color: #F2F9FD; '
            'padding: 14px 16px; border-radius: 8px; margin: 18px 0 12px 0;">'
            '<p style="margin: 0; color: #222222;"><strong style="color: #005A70;">✅ Your next move:</strong> '
            'Select your career program. Use the four guided questions to identify the concern, choose a review decision, and decide what evidence or expert should be checked next.</p></div>'
        )
        fictional_notice = (
            '<div class="fictional-material-notice"><p><strong>Fictional practice materials:</strong> '
            'All comparison examples in this activity are fictional. Some intentionally include unsafe, inaccurate, '
            'misleading, private, or incomplete content so you can practice identifying problems. Do not treat them as real records or approved guidance.</p></div>'
        )
        practice_note = '<p class="save-note">This is a practice activity and does not need to be submitted.</p>'
        return (
            f'<section class="lesson-step classroom-activity" id="step-3-5" data-step-label="3.5" hidden>'
            f'<p class="eyebrow">Step 3.5 · Practical application</p><h2>{html.escape(title)}</h2>'
            f'{desc}{fictional_notice}{next_move}{media_audit_simulation(bank_questions)}{practice_note}</section>'
        )
    if step_label == "2.4":
        desc = desc.replace("IFoEcetEdVQ", "lKsuxtGJSKA")
        desc = desc.replace("AI Literacy: How to Write Good Prompts", "AI Literacy: Refining Chatbot Results")
        desc = re.sub(
            r'<div[^>]*>\s*<a[^>]+10OeD9GDiUXZtuEfeYVUFC_5-XFvJ_MUmaDmbyfwbVg8[^>]*>.*?</div>',
            '<div class="video-access"><a href="https://www.youtube.com/watch?v=lKsuxtGJSKA&cc_load_policy=1" target="_blank" rel="noopener">Watch with English captions</a></div>',
            desc,
            count=1,
            flags=re.I,
        )
    question_html = []
    for q_index, question in enumerate(questions, 1):
        if question["type"] in {"matching_question", "categorization_question"} and question["matching_rows"]:
            rows = []
            correct_map = {}
            for row_index, row in enumerate(question["matching_rows"], 1):
                correct_map[row["id"]] = row["correct"]
                options = '<option value="">Choose a match</option>' + "".join(
                    f'<option value="{html.escape(choice["id"])}">{html.escape(re.sub(r"<[^>]+>", "", choice["html"]).strip())}</option>'
                    for choice in row["choices"]
                )
                rows.append(
                    f'<div class="matching-row"><label for="match-{question["id"]}-{row_index}">{row["label"]}</label>'
                    f'<select id="match-{question["id"]}-{row_index}" data-response-id="{html.escape(row["id"])}">{options}</select></div>'
                )
            interaction = f'<div class="matching-grid">{"".join(rows)}</div><button class="check-answer" type="button">Check matches</button>'
            correct = html.escape(json.dumps(correct_map))
        elif question["type"] == "ordering_question" and question["choices"]:
            ordered_rows = []
            for position in range(1, len(question["correct"]) + 1):
                options = '<option value="">Choose a step</option>' + "".join(
                    f'<option value="{html.escape(choice["id"])}">{html.escape(re.sub(r"<[^>]+>", "", choice["html"]).strip())}</option>'
                    for choice in question["choices"]
                )
                ordered_rows.append(
                    f'<div class="ordering-row"><span class="ordering-position" aria-hidden="true">{position}</span>'
                    f'<label class="sr-only" for="order-{question["id"]}-{position}">Step {position}</label>'
                    f'<select id="order-{question["id"]}-{position}" data-position="{position}">{options}</select></div>'
                )
            interaction = f'<p class="interaction-hint">Choose the steps in order, from first to last.</p><div class="ordering-list">{"".join(ordered_rows)}</div><button class="check-answer" type="button">Check order</button>'
            correct = html.escape(json.dumps(question["correct"]))
        else:
            input_type = "checkbox" if question["type"] == "multiple_answers_question" else "radio"
            choices = "".join(
                f'<label><input type="{input_type}" name="{question["id"]}" value="{html.escape(choice["id"])}"> '
                f'<span>{html.escape(choice["html"]) if question.get("plain_text") else choice["html"]}</span></label>'
                for choice in question["choices"]
            )
            correct = html.escape(json.dumps(question["correct"]))
        if question["type"] not in {"matching_question", "categorization_question", "ordering_question"} and choices:
            interaction = f'<div class="choices">{choices}</div><button class="check-answer" type="button">Check answer</button>'
        elif question["type"] not in {"matching_question", "categorization_question", "ordering_question"}:
            interaction = '<textarea rows="5" aria-label="Your response" placeholder="Write your response here..."></textarea><p class="save-note">Your response stays in this browser.</p>'
        correct_feedback = question.get("feedback_correct_text") or re.sub(r"<[^>]+>", "", question.get("feedback", "")).strip()
        incorrect_feedback = question.get("feedback_incorrect_text") or "Review the idea above and try another answer."
        question_html.append(
            f'<article class="question" data-question-id="{html.escape(question["id"], quote=True)}" '
            f'data-question-type="{html.escape(question["type"])}" data-correct="{correct}" '
            f'data-feedback-correct="{html.escape(correct_feedback, quote=True)}" '
            f'data-feedback-incorrect="{html.escape(incorrect_feedback, quote=True)}"><h3>Check {q_index}</h3>{question["prompt"]}{interaction}'
            f'<div class="feedback" role="status" hidden>{question["feedback"] or "Review the lesson content and try again."}</div></article>'
        )
    label = "Show what you know" if "Show What You Know" in step["title"] else "Learn and check"
    handoff = classroom_handoff() if re.search(r"\b\d+\.5\b", step["title"]) else ""
    classes = "lesson-step classroom-activity" if handoff else "lesson-step"
    if questions:
        desc = add_check_next_move(desc)
    question_set = f'<div class="question-set">{"".join(question_html)}</div>' if questions else ""
    return f'<section class="{classes}" id="step-{step_label.replace(".", "-")}" data-step-label="{step_label}" hidden><p class="eyebrow">Step {step_label} · {label}</p><h2>{html.escape(title)}</h2>{desc}{question_set}{handoff}</section>'


def classroom_handoff() -> str:
    return ('<div class="classroom-handoff"><h3>Submit your work</h3>'
            '<p>Complete the activity using the directions above. Save your response as a document with a clear file name, then submit the document to your course.</p></div>')


def lesson_page(number: int, steps: list[dict]) -> str:
    overview = body_from_html(SOURCE / "wiki_content" / f"{number}-dot-1-lesson-overview.html")
    vocabulary = extract_lesson_vocabulary(overview)
    if number == 1:
        overview = overview.replace(
            "../assets/media/M01_ResponsibleAIRoutine_v1.png",
            "../assets/media/Responsible_AI_Routine_Web_Mobile_1200px.png",
        )
        overview = overview.replace(
            'alt="AI Decision Pathway with Goal, Protect, Use, Check, and Own."',
            f'alt="{html.escape(ROUTINE_ALT, quote=True)}"',
        )
        overview = re.sub(
            r'<div[^>]*>\s*(?:<button class="image-zoom"[^>]*>)?<img[^>]+src="\.\./assets/media/Responsible_AI_Routine_Web_Mobile_1200px\.png"[^>]*>(?:</button>)?\s*</div>',
            routine_figure("Learn these five questions now. You will use them throughout the course."),
            overview,
            count=1,
            flags=re.I,
        )
    overview = structure_routine_overview(overview)
    content_steps = [f'<section class="lesson-step overview" id="step-{number}-1" data-step-label="{number}.1"><p class="eyebrow">Step {number}.1 · Start here</p>{overview}</section>']
    assessment_next_move = (
        "Return to your course and begin with the Reflection on Your Program Scenario section. "
        "Use your Lesson 1.5 decision pathway to explain your thinking, then complete the Lesson 1 assessment. "
        "Follow your instructor's directions for attempts and the required score."
        if number == 1
        else f"Return to your course and complete the Lesson {number} assessment. Follow your instructor's directions for attempts and the required score."
    )
    for index, step in enumerate(steps, 1):
        if re.search(rf"\b{number}\.6\b", step["title"]):
            label = step_number(step, number, len(content_steps) + 1)
            content_steps.append(
                f'<section class="lesson-step assessment-callout" id="step-{label.replace(".", "-")}" data-step-label="{label}" hidden><p class="eyebrow">Step {label} · Lesson assessment</p>'
                f'<h2>{html.escape(re.sub(r"^\d+\.\d+\s*[^A-Za-z0-9]*\s*", "", step["title"]).strip().replace(" — ", ": "))}</h2>'
                f'<div class="check-next-move"><p><strong>✅ Your next move:</strong> {assessment_next_move}</p></div></section>'
            )
        else:
            rendered = step_html(step, number, index)
            if rendered:
                rendered = align_video_to_step(rendered, step_number(step, number, index))
                content_steps.append(rendered)
    content_steps = [append_feedback_link(step, number) for step in content_steps]
    step_count = len(content_steps)
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lesson {number}: {html.escape(LESSON_TITLES[number])} | AI Literacy</title><link rel="stylesheet" href="../assets/styles.css?v={ASSET_VERSION}"></head>
<body data-lesson="{number}"><a class="skip-link" href="#main">Skip to lesson content</a>
<header class="site-header classroom-header"><span class="brand">AI Literacy</span><span class="classroom-label">Course lesson</span></header>
<main id="main"><div class="lesson-hero"><h1 class="lesson-identity">Lesson {number}: {html.escape(LESSON_TITLES[number])}</h1>
<div class="step-progress" aria-label="Lesson progress"><div class="progress-text"><span id="step-status">Step {number}.1</span><span id="step-count">1 of {step_count}</span></div><div class="progress" role="progressbar" aria-labelledby="step-status" aria-valuemin="1" aria-valuemax="{step_count}" aria-valuenow="1" aria-valuetext="Step 1 of {step_count}"><span style="width:{100 / step_count:.2f}%"></span></div></div></div>
<div class="stepper" data-total-steps="{step_count}">{''.join(content_steps)}
<p class="sr-only" id="step-announcement" aria-live="polite"></p>
<nav class="step-controls" aria-label="Lesson step navigation"><button class="step-button secondary" id="previous-step" type="button">← Previous step</button><button class="step-button" id="next-step" type="button">Next step →</button></nav>
<p class="step-help">Your place in this lesson is saved automatically on this device.</p></div></main>
<footer><p>Artificial Intelligence Literacy</p></footer><script src="../assets/app.js?v={ASSET_VERSION}"></script></body></html>'''
    page = page.replace('loading="lazy"', 'loading="eager" decoding="async"')
    image_sources = list(dict.fromkeys(re.findall(r'<img[^>]+src="([^"]+)"', page, flags=re.I)))
    preloads = "".join(
        f'<link rel="preload" as="image" href="{html.escape(source, quote=True)}" fetchpriority="low">'
        for source in image_sources
    )
    page = page.replace("</head>", preloads + "</head>")
    page = normalize_source_foundations(page)
    page = link_lesson_vocabulary(page, vocabulary)
    return re.sub(r"[ \t]+\n", "\n", page)


def nav_links(active: int | None = None, prefix="lessons/") -> str:
    return "".join(
        f'<a href="{prefix}lesson-{n}.html"' + (' aria-current="page"' if n == active else '') + f'>Lesson {n}</a>'
        for n in range(1, 9)
    )


def index_page() -> str:
    cards = "".join(
        f'<a class="lesson-card" href="lessons/lesson-{n}.html"><span class="lesson-number">{n}</span><div><h2>{html.escape(LESSON_TITLES[n])}</h2><p>Open lesson {n}</p></div></a>'
        for n in range(1, 9)
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Eight student-facing lessons for responsible, practical AI literacy."><title>AI Literacy | Student Course</title><link rel="stylesheet" href="assets/styles.css?v={ASSET_VERSION}"></head>
<body><a class="skip-link" href="#main">Skip to course</a><header class="site-header"><a class="brand" href="index.html">AI Literacy</a><button class="menu-button" aria-expanded="false" aria-controls="course-nav">Lessons</button><nav id="course-nav">{nav_links()}</nav></header>
<main id="main"><section class="home-hero"><div><p class="eyebrow">Career-ready learning</p><h1>Use AI with skill, judgment, and responsibility.</h1><p class="lede">Eight practical lessons help you understand how AI works, improve its output, protect people and information, and keep humans accountable.</p><a class="button" href="lessons/lesson-1.html">Start lesson 1</a></div><div class="routine" aria-label="Responsible AI Routine"><span>Goal</span><span>Protect</span><span>Use</span><span>Check</span><span>Own</span></div></section>
<section class="course-map"><p class="eyebrow">Course map</p><h2>Eight lessons. One responsible routine.</h2><div class="lesson-grid">{cards}</div></section></main><footer><p>Artificial Intelligence Literacy</p></footer><script src="assets/app.js?v={ASSET_VERSION}"></script></body></html>'''


def assessment_export():
    source = SOURCE / "non_cc_assessments" / "g3082f0bad454e4f7cafd09297e14acbf.xml.qti"
    questions = extract_questions(source)
    (ROOT / "assessment-questions.json").write_text(json.dumps(questions, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# AI Skills Certification Assessment", "", "Mastery goal: 16/20. Recommended settings: quiz mode, collect email optional, shuffle choices, three attempts.", ""]
    for i, q in enumerate(questions, 1):
        prompt = re.sub("<[^>]+>", "", q["prompt"]).strip()
        lines += [f"## {i}. {prompt}", ""]
        for choice in q["choices"]:
            mark = "[correct]" if choice["id"] in q["correct"] else ""
            lines.append(f"- {re.sub('<[^>]+>', '', choice['html']).strip()} {mark}".rstrip())
        lines.append("")
    (ROOT / "ASSESSMENT.md").write_text("\n".join(lines), encoding="utf-8")


def lesson_assessments_export(modules):
    output = {}
    for number, steps in modules.items():
        step = next((s for s in steps if re.search(rf"\b{number}\.6\b", s["title"])), None)
        if not step:
            continue
        qti = SOURCE / "non_cc_assessments" / f'{step["ref"]}.xml.qti'
        questions = extract_questions(qti) if qti.exists() else []
        if number == 8:
            questions = extract_questions(SOURCE / "non_cc_assessments" / "g3082f0bad454e4f7cafd09297e14acbf.xml.qti")[:20]
        output[str(number)] = {"title": step["title"], "questions": questions}
    (ROOT / "lesson-assessments.json").write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    LESSONS.mkdir(exist_ok=True)
    (ASSETS / "media").mkdir(parents=True, exist_ok=True)
    for image in (SOURCE / "web_resources" / "Uploaded Media").iterdir():
        if image.is_file():
            shutil.copy2(image, ASSETS / "media" / image.name)
    modules = module_lessons()
    (ROOT / "index.html").write_text(index_page(), encoding="utf-8")
    for number, steps in modules.items():
        (LESSONS / f"lesson-{number}.html").write_text(lesson_page(number, steps), encoding="utf-8")
    assessment_export()
    lesson_assessments_export(modules)


if __name__ == "__main__":
    main()
