from __future__ import annotations

import html
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_canvas_source"
LESSONS = ROOT / "lessons"
ASSETS = ROOT / "assets"
FORM_LINKS_PATH = ROOT / "form-links.json"

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

LESSON_TITLES = {
    1: "Humans Behind AI — How People Shape What AI Does",
    2: "Prompt Like a Pro — The AI Test Lab",
    3: "Verify Before You Trust — Auditing AI Media",
    4: "The Bias Trap — Is AI Really Fair?",
    5: "Privacy Shield — What NOT to Share with AI",
    6: "Create with Integrity — Ethics, Copyright, and Original Work",
    7: "Level Up — AI Skills for Your Future Career",
    8: "Build, Test, Improve — Model Rescue and Certification",
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
        "In this lesson, you will choose your GCI program and work with one of six made-up workplace examples. You will build, test, and improve a simple AI model. You will find errors, suggest safety steps, and complete the final assessment.",
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
        "After completing the simulation, you will reflect on what you learned and connect it to your GCI program area in a short document.",
    )
    value = value.replace(
        "Click <strong>Submit Assignment</strong> at the top of this page and type your answers to the following 4 reflection questions in the Text Entry box:",
        "Create a document and answer the following 4 reflection questions. Submit your completed document to your course:",
    )
    for group_number in (1, 2, 3):
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
    value = value.replace("https://www.youtube.com/embed/dpRK9y7fuJA", "https://www.youtube-nocookie.com/embed/BQosMFvT0aU?cc_load_policy=1")
    value = value.replace("https://gisd.instructure.com/courses/2083/files/274996/download?download_frd=1", "https://www.youtube.com/watch?v=BQosMFvT0aU&cc_load_policy=1")
    value = value.replace('href="url?id=43"', 'href="https://www.youtube.com/watch?v=fv2e58rgI9k&cc_load_policy=1"')
    value = value.replace('href="url?id=41"', 'href="https://www.youtube.com/watch?v=fv2e58rgI9k"')
    value = value.replace(
        "https://questions.learnosity.com/v2023.2.LTS/xdomain",
        "https://www.youtube-nocookie.com/embed/_WpTWizRGys?cc_load_policy=1",
    )
    value = value.replace(
        '<p style="margin: 0; font-size: 0.9em; color: #005a70; text-align: center;">English transcript | Watch in Spanish | Watch in Arabic</p>',
        '<p style="margin: 0; font-size: 0.9em; color: #005a70; text-align: center;">'
        '<a href="https://docs.google.com/document/d/1svKP5hv_xVMULKPtoQN8vv_QsjFOH8gIkoOgGpnD7vA/edit" target="_blank" rel="noopener">English transcript</a> | '
        '<a href="https://www.youtube-nocookie.com/embed/oLeV1eQWNNU?rel=0" target="_blank" rel="noopener">Watch in Spanish</a> | '
        '<a href="https://www.youtube-nocookie.com/embed/q9Lkx0h87Aw?rel=0" target="_blank" rel="noopener">Watch in Arabic</a></p>',
    )
    value = re.sub(r'(href="https://www\.youtube\.com/watch\?v=(?:BQosMFvT0aU|fv2e58rgI9k)&(?:amp;)?cc_load_policy=1"[^>]*>)English transcript(</a>)', r'\1Watch with English captions\2', value)
    value = value.replace("$IMS-CC-FILEBASE$/Uploaded%20Media/", "../assets/media/")
    value = value.replace("$IMS-CC-FILEBASE$/Uploaded Media/", "../assets/media/")
    value = value.replace('src="url?id=17/159962/preview"', 'src="../assets/media/M01_ResponsibleAIRoutine_v1.png"')
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


def human_decisions_simulation() -> str:
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


def step_html(step: dict, number: int, index: int) -> str:
    title = re.sub(r"^\d+\.\d+\s*[^A-Za-z0-9]*\s*", "", step["title"]).strip()
    step_label = step_number(step, number, index)
    if step["type"] == "WikiPage":
        return ""
    if step["type"] == "Assignment":
        folder = SOURCE / step["ref"]
        candidates = list(folder.glob("*.html"))
        content = body_from_html(candidates[0]) if candidates else "<p>Complete the applied learning task described by your instructor.</p>"
        handoff = "" if step_label in {"2.5", "4.5", "5.5", "6.5", "7.5", "8.5"} else classroom_handoff()
        return f'<section class="lesson-step classroom-activity" id="step-{step_label.replace(".", "-")}" data-step-label="{step_label}" hidden><p class="eyebrow">Step {step_label} · Practical application</p><h2>{html.escape(title)}</h2>{content}{handoff}</section>'
    qti = SOURCE / "non_cc_assessments" / f'{step["ref"]}.xml.qti'
    questions = extract_questions(qti) if qti.exists() else []
    desc = quiz_description(step["ref"])
    if step_label == "1.5":
        desc = re.sub(
            r'(<strong[^>]*>How this works:</strong>).*?(</p>)',
            r'\1 You will complete six workplace cases, one from each career category. Choose the response that keeps trained people involved in checking evidence and making final decisions. You may retry a case after reading the feedback. This is a practice activity and does not need to be submitted.\2',
            desc,
            count=1,
            flags=re.I | re.S,
        )
        return f'<section class="lesson-step classroom-activity" id="step-1-5" data-step-label="1.5" hidden><p class="eyebrow">Step 1.5 · Practical application</p><h2>{html.escape(title)}</h2>{desc}{human_decisions_simulation()}</section>'
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
                f'<label><input type="{input_type}" name="{question["id"]}" value="{html.escape(choice["id"])}"> <span>{choice["html"]}</span></label>'
                for choice in question["choices"]
            )
            correct = html.escape(json.dumps(question["correct"]))
        if question["type"] not in {"matching_question", "categorization_question", "ordering_question"} and choices:
            interaction = f'<div class="choices">{choices}</div><button class="check-answer" type="button">Check answer</button>'
        elif question["type"] not in {"matching_question", "categorization_question", "ordering_question"}:
            interaction = '<textarea rows="5" aria-label="Your response" placeholder="Write your response here..."></textarea><p class="save-note">Your response stays in this browser.</p>'
        question_html.append(
            f'<article class="question" data-question-type="{html.escape(question["type"])}" data-correct="{correct}"><h3>Check {q_index}</h3>{question["prompt"]}{interaction}'
            f'<div class="feedback" role="status" hidden>{question["feedback"] or "Review the lesson content and try again."}</div></article>'
        )
    label = "Show what you know" if "Show What You Know" in step["title"] else "Learn and check"
    handoff = classroom_handoff() if re.search(r"\b\d+\.5\b", step["title"]) else ""
    classes = "lesson-step classroom-activity" if handoff else "lesson-step"
    return f'<section class="{classes}" id="step-{step_label.replace(".", "-")}" data-step-label="{step_label}" hidden><p class="eyebrow">Step {step_label} · {label}</p><h2>{html.escape(title)}</h2>{desc}<div class="question-set">{"".join(question_html)}</div>{handoff}</section>'


def classroom_handoff() -> str:
    return ('<div class="classroom-handoff"><h3>Submit your work</h3>'
            '<p>Complete the activity using the directions above. Save your response as a document with a clear file name, then submit the document to your course.</p></div>')


def lesson_page(number: int, steps: list[dict]) -> str:
    overview = body_from_html(SOURCE / "wiki_content" / f"{number}-dot-1-lesson-overview.html")
    content_steps = [f'<section class="lesson-step overview" id="step-{number}-1" data-step-label="{number}.1"><p class="eyebrow">Step {number}.1 · Start here</p>{overview}</section>']
    form_links = json.loads(FORM_LINKS_PATH.read_text(encoding="utf-8")) if FORM_LINKS_PATH.exists() else {}
    for index, step in enumerate(steps, 1):
        if re.search(rf"\b{number}\.6\b", step["title"]):
            form_url = form_links.get(str(number), "assessment.html")
            label = step_number(step, number, len(content_steps) + 1)
            content_steps.append(
                f'<section class="lesson-step assessment-callout" id="step-{label.replace(".", "-")}" data-step-label="{label}" hidden><p class="eyebrow">Step {label} · Lesson assessment · Google Form</p>'
                f'<h2>{html.escape(re.sub(r"^\d+\.\d+\s*[^A-Za-z0-9]*\s*", "", step["title"]).strip())}</h2>'
                f'<p>Complete the assessment to show what you know from Lesson {number}. Follow your instructor’s directions for the mastery score and attempts.</p>'
                f'<a class="button" href="{html.escape(form_url)}" target="_blank" rel="noopener">Open Lesson {number} assessment <span aria-hidden="true">↗</span></a></section>'
            )
        else:
            rendered = step_html(step, number, index)
            if rendered:
                content_steps.append(rendered)
    step_count = len(content_steps)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lesson {number}: {html.escape(LESSON_TITLES[number])} | AI Literacy</title><link rel="stylesheet" href="../assets/styles.css"></head>
<body data-lesson="{number}"><a class="skip-link" href="#main">Skip to lesson content</a>
<header class="site-header classroom-header"><span class="brand">AI Literacy</span><span class="classroom-label">Course lesson</span></header>
<main id="main"><div class="lesson-hero"><p class="eyebrow">Lesson {number}</p><h1>{html.escape(LESSON_TITLES[number])}</h1>
<div class="step-progress" aria-label="Lesson progress"><div class="progress-text"><span id="step-status">Step {number}.1</span><span id="step-count">1 of {step_count}</span></div><div class="progress" role="progressbar" aria-labelledby="step-status" aria-valuemin="1" aria-valuemax="{step_count}" aria-valuenow="1"><span style="width:{100 / step_count:.2f}%"></span></div></div></div>
<div class="stepper" data-total-steps="{step_count}">{''.join(content_steps)}
<p class="sr-only" id="step-announcement" aria-live="polite"></p>
<nav class="step-controls" aria-label="Lesson step navigation"><button class="step-button secondary" id="previous-step" type="button">← Previous step</button><button class="step-button" id="next-step" type="button">Next step →</button></nav>
<p class="step-help">Your place in this lesson is saved automatically on this device.</p></div></main>
<footer><p>Artificial Intelligence Literacy · Genesee Career Institute</p></footer><script src="../assets/app.js"></script></body></html>'''


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
<meta name="description" content="Eight student-facing lessons for responsible, practical AI literacy."><title>AI Literacy | Student Course</title><link rel="stylesheet" href="assets/styles.css"></head>
<body><a class="skip-link" href="#main">Skip to course</a><header class="site-header"><a class="brand" href="index.html">AI Literacy</a><button class="menu-button" aria-expanded="false" aria-controls="course-nav">Lessons</button><nav id="course-nav">{nav_links()}</nav></header>
<main id="main"><section class="home-hero"><div><p class="eyebrow">Career-ready learning</p><h1>Use AI with skill, judgment, and responsibility.</h1><p class="lede">Eight practical lessons help you understand how AI works, improve its output, protect people and information, and keep humans accountable.</p><a class="button" href="lessons/lesson-1.html">Start lesson 1</a></div><div class="routine" aria-label="Responsible AI Routine"><span>Goal</span><span>Protect</span><span>Use</span><span>Check</span><span>Own</span></div></section>
<section class="course-map"><p class="eyebrow">Course map</p><h2>Eight lessons. One responsible routine.</h2><div class="lesson-grid">{cards}</div></section></main><footer><p>Artificial Intelligence Literacy · Genesee Career Institute</p></footer><script src="assets/app.js"></script></body></html>'''


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
