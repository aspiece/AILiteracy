// Practice-only progress. No account, server, grade, or external-service state.
const lessonId = document.body.dataset.lesson;
const localProgress = (() => {
  let available = true;
  try {
    const probe = 'ai-literacy-storage-probe';
    localStorage.setItem(probe, '1');
    localStorage.removeItem(probe);
  } catch (_) { available = false; }
  return {
    get available() { return available; },
    get(key) { try { return localStorage.getItem(key); } catch (_) { available = false; return null; } },
    set(key, value) { try { localStorage.setItem(key, value); return true; } catch (_) { available = false; return false; } },
    remove(key) { try { localStorage.removeItem(key); return true; } catch (_) { available = false; return false; } }
  };
})();
const progressKey = 'ai-literacy-practice-v1-' + lessonId;
const emptyPractice = () => ({ version: 1, lesson: lessonId, step: 0, choices: {}, scenarios: {} });
function readPractice() {
  try {
    const value = JSON.parse(localProgress.get(progressKey) || 'null');
    return value && value.version === 1 && value.lesson === lessonId ? value : emptyPractice();
  } catch (_) { return emptyPractice(); }
}
const practiceControls = new Map();
function registerPracticeControls() {
  document.querySelectorAll('.question, .scenario-card').forEach(group => {
    const card = group.closest('.scenario-card');
    const groupId = group.dataset.questionId || (card && 'scenario:' + (card.dataset.program || card.dataset.bank));
    if (!groupId) return;
    const controls = [...group.querySelectorAll('input[type="radio"], input[type="checkbox"], select')];
    controls.forEach((control, i) => {
      const key = groupId + ':' + (control.dataset.responseId || control.name || 'select-' + i);
      if (!practiceControls.has(key)) practiceControls.set(key, []);
      practiceControls.get(key).push(control);
    });
  });
}
registerPracticeControls();
const scenarioOptions = new Map();
document.querySelectorAll('.scenario-simulation').forEach(sim => {
  const mode = sim.dataset.feedbackMode;
  if (!['media-audit', 'program-scenario'].includes(mode)) return;
  scenarioOptions.set(mode, new Set([...sim.querySelectorAll('.scenario-card')].map(card => card.dataset.program).filter(Boolean)));
});
function sanitizePractice(value) {
  if (!value || value.version !== 1 || value.lesson !== lessonId ||
      !Number.isInteger(value.step) || value.step < 0 ||
      value.step >= document.querySelectorAll('.lesson-step').length) return null;
  const result = emptyPractice();
  result.step = value.step;
  if (!value.choices || typeof value.choices !== 'object' || Array.isArray(value.choices) ||
      !value.scenarios || typeof value.scenarios !== 'object' || Array.isArray(value.scenarios)) return null;
  for (const [key, controls] of practiceControls) {
    const values = Object.prototype.hasOwnProperty.call(value.choices, key) ? value.choices[key] : undefined;
    if (values === undefined) continue;
    if (!Array.isArray(values) || values.some(v => typeof v !== 'string')) return null;
    const allowed = new Set(controls.flatMap(c => c.tagName === 'SELECT' ? [...c.options].map(o => o.value) : [c.value]));
    if (values.some(v => !allowed.has(v)) || new Set(values).size !== values.length) return null;
    if (controls[0].type !== 'checkbox' && values.length > 1) return null;
    result.choices[key] = values;
  }
  for (const [mode, names] of scenarioOptions) {
    if (!Object.prototype.hasOwnProperty.call(value.scenarios, mode)) continue;
    const name = value.scenarios[mode];
    if (typeof name !== 'string' || !names.has(name)) return null;
    result.scenarios[mode] = name;
  }
  return result;
}
const savedPractice = readPractice();
const practice = sanitizePractice(savedPractice) || emptyPractice();
let announceSave = () => {};
function savePractice() {
  if (!lessonId) return false;
  const ok = localProgress.set(progressKey, JSON.stringify(practice));
  announceSave(ok);
  return ok;
}
function restoreChoices(root = document) {
  for (const [key, controls] of practiceControls) {
    const values = practice.choices[key] || [];
    controls.filter(c => root.contains(c)).forEach(c => {
      if (c.tagName === 'SELECT') c.value = values[0] || '';
      else c.checked = values.includes(c.value);
    });
  }
}
document.addEventListener('change', event => {
  for (const [key, controls] of practiceControls) {
    if (!controls.includes(event.target)) continue;
    practice.choices[key] = controls[0].tagName === 'SELECT' ? [event.target.value] :
      controls.filter(c => c.checked).map(c => c.value);
    savePractice();
    break;
  }
});
function rememberScenario(mode, card) {
  if (card && card.dataset.program) practice.scenarios[mode] = card.dataset.program;
  else delete practice.scenarios[mode];
  savePractice();
}

document.querySelector('.menu-button')?.addEventListener('click', event => {
  const nav = document.querySelector('#course-nav');
  const open = nav.classList.toggle('open');
  event.currentTarget.setAttribute('aria-expanded', String(open));
});

// Formative feedback only; never used to grade the external certification assessment.
function evaluatePracticeOrder(selected, canonical, alternatives = []) {
  const valid = [canonical, ...alternatives].filter(order =>
    Array.isArray(order) && order.length === canonical.length &&
    new Set(order).size === canonical.length && order.every(value => canonical.includes(value)));
  const counts = valid.map(order => order.reduce((sum, value, index) => sum + Number(selected[index] === value), 0));
  const best = Math.max(0, ...counts);
  const nearest = valid.filter((_, index) => counts[index] === best);
  return {
    correct: selected.length === canonical.length && best === canonical.length,
    best,
    review: selected.map((value, index) => nearest.every(order => order[index] !== value) ? index + 1 : null).filter(Boolean)
  };
}
function practiceSelectionFeedback(selected, correct) {
  return { hits: selected.filter(value => correct.includes(value)).length,
    extra: selected.filter(value => !correct.includes(value)),
    missing: correct.filter(value => !selected.includes(value)).length };
}

document.querySelectorAll('.question').forEach(question => {
  const shuffleOptions = select => {
    const placeholder = select.querySelector('option[value=""]');
    const choices = [...select.querySelectorAll('option:not([value=""])')];
    for (let index = choices.length - 1; index > 0; index -= 1) {
      const swapIndex = Math.floor(Math.random() * (index + 1));
      [choices[index], choices[swapIndex]] = [choices[swapIndex], choices[index]];
    }
    select.replaceChildren(...(placeholder ? [placeholder] : []), ...choices);
  };
  question.querySelectorAll('.matching-row select, .ordering-row select').forEach(shuffleOptions);
  const button = question.querySelector('.check-answer');
  if (!button) return;
  const feedback = question.querySelector('.feedback');
  const originalCorrectFeedback = feedback?.textContent.trim() || 'Correct.';
  if (!feedback) return;
  let attempts = 0;
  question.addEventListener('change', () => { feedback.hidden = true; });
  button.addEventListener('click', () => {
    const correct = JSON.parse(question.dataset.correct || '[]');
    let isCorrect = false;
    let diagnostic = '';
    let nextHint = '';
    if (['matching_question', 'categorization_question'].includes(question.dataset.questionType)) {
      const selects = [...question.querySelectorAll('.matching-row select')];
      if (selects.some(select => !select.value)) {
        feedback.textContent = 'Choose a match for every row first.';
        feedback.classList.add('incorrect');
        feedback.hidden = false;
        return;
      }
      if (question.dataset.questionType === 'matching_question') {
        const selectedValues = selects.map(select => select.value);
        if (new Set(selectedValues).size !== selectedValues.length) {
          feedback.textContent = 'Use each match only once.';
          feedback.classList.add('incorrect');
          feedback.hidden = false;
          return;
        }
      }
      const mismatches = selects.map((select, index) => correct[select.dataset.responseId] !== select.value ? index + 1 : null).filter(Boolean);
      isCorrect = mismatches.length === 0;
      diagnostic = (selects.length - mismatches.length) + ' of ' + selects.length + ' matches are correct. Review row' + (mismatches.length === 1 ? ' ' : 's ') + mismatches.join(', ') + '.';
      nextHint = 'Read the label for each row again; compare what the situation describes with the responsibility or concept.';

    } else if (question.dataset.questionType === 'ordering_question') {
      const selects = [...question.querySelectorAll('.ordering-row select')];
      if (selects.some(select => !select.value)) {
        feedback.textContent = 'Choose a step for every position first.';
        feedback.classList.add('incorrect');
        feedback.hidden = false;
        return;
      }
      const selectedValues = selects.map(select => select.value);
      if (new Set(selectedValues).size !== selectedValues.length) {
        feedback.textContent = 'Use each step only once.';
        feedback.classList.add('incorrect');
        feedback.hidden = false;
        return;
      }
      let alternatives = [];
      try { alternatives = JSON.parse(question.dataset.acceptedOrders || '[]'); } catch (_) { /* use canonical */ }
      if (!Array.isArray(alternatives)) alternatives = [];
      const result = evaluatePracticeOrder(selectedValues, correct, alternatives);
      isCorrect = result.correct;
      diagnostic = result.best + ' of ' + correct.length + ' positions match a valid order.' +
        (result.review.length ? ' Review position' + (result.review.length === 1 ? ' ' : 's ') + result.review.join(', ') + '.' : '');
      nextHint = 'Think about which actions must happen before another action can safely begin.';

    } else {
      const selected = [...question.querySelectorAll('input:checked')].map(input => input.value);
      if (!selected.length) {
        feedback.textContent = 'Choose an answer first.';
        feedback.classList.add('incorrect');
        feedback.hidden = false;
        return;
      }
      const result = practiceSelectionFeedback(selected, correct);
      isCorrect = result.extra.length === 0 && result.missing === 0;
      if (question.dataset.questionType === 'multiple_answers_question') {
        diagnostic = result.hits + ' correct choice' + (result.hits === 1 ? '' : 's') + ' selected; ' +
          result.extra.length + ' selected choice' + (result.extra.length === 1 ? ' needs' : 's need') + ' review. ' +
          (result.missing ? 'Some correct choices are still missing.' : 'Review your extra selections.');
        let hints = {};
        try { hints = JSON.parse(question.dataset.choiceHints || '{}'); } catch (_) { /* use general hint */ }
        nextHint = result.extra.map(value => typeof hints?.[value] === 'string' ? hints[value] : '').filter(Boolean).join(' ') ||
          'Read each option separately. Decide whether it meets the question’s goal before moving to the next.';
      } else {
        nextHint = 'Read the question again and explain why your chosen option fits the idea above.';
      }

    }
    feedback.classList.toggle('incorrect', !isCorrect);
    feedback.replaceChildren();
    if (isCorrect) {
      feedback.textContent = question.dataset.feedbackCorrect || originalCorrectFeedback;
    } else {
      const lead = document.createElement('strong');
      lead.textContent = 'Not yet. ';
      attempts += 1;
      feedback.append(lead, question.dataset.feedbackIncorrect || 'Review the idea above and try another answer.');
      if (diagnostic) {
        const detail = document.createElement('p');
        detail.textContent = diagnostic;
        feedback.append(detail);
      }
      if (attempts >= 2 && nextHint) {
        const hint = document.createElement('p');
        hint.textContent = 'Try this: ' + nextHint;
        feedback.append(hint);
      }
    }
    feedback.hidden = false;
  });
});

const reflectionKeys = [];
document.querySelectorAll('textarea').forEach((field, index) => {
  const legacyKey = 'ai-literacy-' + (lessonId || 'home') + '-' + index;
  const key = field.id ? 'ai-literacy-reflection-' + lessonId + '-' + field.id : legacyKey;
  reflectionKeys.push(key, legacyKey);
  field.value = localProgress.get(key) ?? localProgress.get(legacyKey) ?? '';
  field.addEventListener('input', () => announceSave(localProgress.set(key, field.value)));
});

const stepper = document.querySelector('.stepper');
if (stepper) {
  const steps = [...stepper.querySelectorAll('.lesson-step')];
  const previous = document.querySelector('#previous-step');
  const next = document.querySelector('#next-step');
  const progress = document.querySelector('[role="progressbar"]');
  const progressFill = progress.querySelector('span');
  const status = document.querySelector('#step-status');
  const count = document.querySelector('#step-count');
  const announcement = document.querySelector('#step-announcement');
  const storageKey = `ai-literacy-lesson-${document.body.dataset.lesson}-step`;
  const requestedParam = new URLSearchParams(location.search).get('step');
  const requested = requestedParam === null ? -1 : Number(requestedParam) - 1;
  const legacyStep = Number(localProgress.get(storageKey) || 0);
  const savedStep = sanitizePractice(savedPractice) && localProgress.get(progressKey) !== null ? practice.step :
    Number.isInteger(legacyStep) && legacyStep >= 0 && legacyStep < steps.length ? legacyStep : 0;
  let current = Number.isInteger(requested) && requested >= 0 && requested < steps.length ? requested : savedStep;
  const priorStep = savedStep;
  const hadSavedStep = localProgress.get(progressKey) !== null || localProgress.get(storageKey) !== null;

  function showStep(index, moveFocus = false) {
    current = Math.min(Math.max(index, 0), steps.length - 1);
    steps.forEach((step, stepIndex) => { step.hidden = stepIndex !== current; });
    const label = steps[current].dataset.stepLabel || String(current + 1);
    const percent = ((current + 1) / steps.length) * 100;
    status.textContent = `Step ${label}`;
    count.textContent = `${current + 1} of ${steps.length}`;
    progress.setAttribute('aria-valuenow', String(current + 1));
    progress.setAttribute('aria-valuetext', `Step ${current + 1} of ${steps.length}`);
    progressFill.style.width = `${percent}%`;
    previous.disabled = current === 0;
    next.disabled = false;
    next.textContent = current === steps.length - 1 ? 'Finish lesson ✓' : 'Next step →';
    practice.step = current;
    savePractice();
    const url = new URL(location.href);
    url.searchParams.set('step', String(current + 1));
    history.replaceState(null, '', url.href);
    announcement.textContent = `Now showing step ${label}, ${current + 1} of ${steps.length}.`;
    if (moveFocus) {
      const heading = steps[current].querySelector('h2, h1');
      if (heading) { heading.setAttribute('tabindex', '-1'); heading.focus(); }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  previous.addEventListener('click', () => showStep(current - 1, true));
  next.addEventListener('click', () => {
    if (current === steps.length - 1) {
      announcement.textContent = 'Lesson complete. Submit any required work using your instructor’s directions.';
      next.textContent = 'Lesson complete ✓';
      next.disabled = true;
      return;
    }
    showStep(current + 1, true);
  });
  // Keep explicit step links meaningful while offering a return to the previous saved step.
  showStep(current);
  const panel = document.createElement('details');
  panel.className = 'practice-resume';
  panel.style.cssText = 'margin-top:1rem;border:1px solid #767676;border-radius:8px;padding:.75rem;background:#fff;color:#222';
  panel.innerHTML = '<summary style="cursor:pointer;font-weight:700">Save and resume practice (this device only)</summary><p>Practice choices and written reflections are saved in this browser on this device when storage is available. These are not grades or submitted assignments.</p><p>Switching devices? Keep required writing in your school worksheet or LMS. Download a resume file for your step and practice selections, save it in your school-managed storage if allowed, then open this same lesson on the other device and load it. The file does not include written reflections, names, grades or work in other tools. Do not share it with classmates.</p><p>On a shared device, save required work first, then clear this lesson’s local practice before leaving.</p><div style="display:flex;flex-wrap:wrap;gap:.5rem"><button class="step-button secondary" type="button" data-resume="download">Download resume file</button><button class="step-button secondary" type="button" data-resume="load">Load resume file</button><button class="step-button secondary" type="button" data-resume="clear">Clear this lesson’s local practice</button></div><input type="file" accept=".json,application/json" hidden><p role="status" aria-live="polite" data-resume-status></p>';
  (document.querySelector('.step-progress') || stepper).append(panel);
  const message = panel.querySelector('[data-resume-status]');
  const say = text => { if (message.textContent !== text) message.textContent = text; };
  announceSave = ok => { say(ok ? 'Practice saved on this device.' : 'Browser storage unavailable. Download a resume file before leaving; keep writing in your school worksheet.'); };
  announceSave(localProgress.available);
  if (!localProgress.available) panel.open = true;
  if (hadSavedStep && priorStep !== current) {
    const resume = document.createElement('button');
    resume.type = 'button';
    resume.className = 'step-button secondary';
    resume.textContent = 'Return to previously saved step ' + (priorStep + 1);
    panel.querySelector('div').prepend(resume);
    panel.open = true;
    resume.addEventListener('click', () => { showStep(priorStep, true); resume.remove(); });
  }
  const fileInput = panel.querySelector('input[type="file"]');
  panel.querySelector('[data-resume="download"]').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(practice, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'ai-practice-lesson-' + lessonId + '.json';
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    say('Resume file requested. Save it in school-managed storage if allowed. Written reflections are not included.');
  });
  panel.querySelector('[data-resume="load"]').addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', async () => {
    const file = fileInput.files[0];
    fileInput.value = '';
    if (!file) return;
    try {
      if (file.size > 65536) throw new Error('File too large.');
      const restored = sanitizePractice(JSON.parse(await file.text()));
      if (!restored) throw new Error('Invalid or different lesson.');
      if (!confirm('Replace this lesson’s saved practice selections and step with the resume file? Written reflections on this device will stay.')) return;
      if (!localProgress.set(progressKey, JSON.stringify(restored))) {
        say('Cannot load the file while browser storage is unavailable. Keep the file and use a browser with storage enabled.');
        return;
      }
      const url = new URL(location.href);
      url.searchParams.set('step', String(restored.step + 1));
      if (url.href === location.href) location.reload();
      else location.assign(url.href);
    } catch (_) { say('This resume file could not be loaded. Choose a valid file from this same lesson. Your current work was not changed.'); }
  });
  panel.querySelector('[data-resume="clear"]').addEventListener('click', () => {
    if (!confirm('Clear practice choices and written reflections for this lesson on this device? Save any required work first. This does not change submitted work.')) return;
    const removed = [...new Set([progressKey, storageKey, ...reflectionKeys])].map(key => localProgress.remove(key)).every(Boolean);
    if (!removed) { say('Some local data could not be cleared. Check your browser storage settings before leaving a shared device.'); return; }
    const url = new URL(location.href);
    url.searchParams.set('step', '1');
    if (url.href === location.href) location.reload();
    else location.assign(url.href);
  });
}

document.querySelectorAll('a[href^="http"]').forEach(link => {
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  if (!link.querySelector('.external-link-label')) {
    const note = document.createElement('span');
    note.className = 'sr-only external-link-label';
    note.textContent = ' (opens in a new tab)';
    link.append(note);
  }
});

const zoomButtons = [...document.querySelectorAll('.image-zoom')];
if (zoomButtons.length) {
  const dialog = document.createElement('dialog');
  dialog.className = 'image-dialog';
  dialog.setAttribute('aria-label', 'Enlarged lesson image');
  dialog.innerHTML = '<button class="image-dialog-close" type="button">Close</button><img alt="">';
  document.body.append(dialog);
  const dialogImage = dialog.querySelector('img');
  const closeButton = dialog.querySelector('.image-dialog-close');
  let returnFocus;

  zoomButtons.forEach(button => {
    button.addEventListener('click', () => {
      const sourceImage = button.querySelector('img');
      dialogImage.src = sourceImage.currentSrc || sourceImage.src;
      dialogImage.alt = sourceImage.alt;
      returnFocus = button;
      dialog.showModal();
      closeButton.focus();
    });
  });
  closeButton.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener('close', () => returnFocus?.focus());
}

const vocabularyLinks = [...document.querySelectorAll('.vocab-link')];
if (vocabularyLinks.length) {
  const dialog = document.createElement('dialog');
  dialog.className = 'vocabulary-dialog';
  dialog.setAttribute('aria-labelledby', 'vocabulary-dialog-term');
  dialog.innerHTML = '<button class="vocabulary-dialog-close" type="button" aria-label="Close definition">Close</button><h2 id="vocabulary-dialog-term"></h2><p></p>';
  document.body.append(dialog);
  const term = dialog.querySelector('h2');
  const definition = dialog.querySelector('p');
  const closeButton = dialog.querySelector('.vocabulary-dialog-close');
  let returnFocus;

  vocabularyLinks.forEach(link => {
    link.addEventListener('click', () => {
      term.textContent = link.dataset.term;
      definition.textContent = link.dataset.definition;
      returnFocus = link;
      dialog.showModal();
      closeButton.focus();
    });
  });
  closeButton.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener('close', () => returnFocus?.focus());
}

document.querySelectorAll('.scenario-simulation').forEach(simulation => {
  const allCards = [...simulation.querySelectorAll('.scenario-card')];
  const previousCase = simulation.querySelector('.scenario-previous');
  const nextCase = simulation.querySelector('.scenario-next');
  const feedbackMode = simulation.dataset.feedbackMode || 'human-decisions';
  const cardLimit = Number(simulation.dataset.cardLimit || 0);

  if (feedbackMode === 'media-audit' && simulation.querySelector('.media-program-select')) {
    const select = simulation.querySelector('.media-program-select');
    const start = simulation.querySelector('.media-audit-start');
    const picker = simulation.querySelector('.media-program-picker');
    const deck = simulation.querySelector('.scenario-deck');
    const another = simulation.querySelector('.media-audit-actions');
    const anotherButton = simulation.querySelector('.media-audit-another');
    const count = simulation.querySelector('.simulation-count');

    function shuffleChoices(card) {
      card.querySelectorAll('.audit-question .choices').forEach(group => {
        const choices = [...group.children];
        for (let index = choices.length - 1; index > 0; index -= 1) {
          const swapIndex = Math.floor(Math.random() * (index + 1));
          [choices[index], choices[swapIndex]] = [choices[swapIndex], choices[index]];
        }
        choices.forEach(choice => group.appendChild(choice));
      });
    }

    function resetComparison() {
      allCards.forEach(card => {
        card.hidden = true;
        card.querySelectorAll('input').forEach(input => { input.checked = false; });
        card.querySelectorAll('.audit-question').forEach(question => question.classList.remove('incorrect'));
        const feedback = card.querySelector('.feedback');
        feedback.hidden = true;
        feedback.classList.remove('incorrect');
        feedback.innerHTML = feedback.dataset.completeFeedback || feedback.innerHTML;
      });
      deck.hidden = true;
      another.hidden = true;
      count.textContent = 'Choose your program';
    }

    allCards.forEach(card => {
      const feedback = card.querySelector('.feedback');
      feedback.dataset.completeFeedback = feedback.innerHTML;
      card.addEventListener('change', () => { feedback.hidden = true; another.hidden = true; });
      card.querySelector('.scenario-check').addEventListener('click', () => {
        const questions = [...card.querySelectorAll('.audit-question')];
        let allCorrect = true;
        questions.forEach(question => {
          const answer = question.querySelector('input:checked');
          const correct = Boolean(answer) && answer.value === question.dataset.correct;
          question.classList.toggle('incorrect', !correct);
          allCorrect = allCorrect && correct;
        });
        feedback.classList.toggle('incorrect', !allCorrect);
        if (allCorrect) {
          feedback.innerHTML = '<strong>Comparison complete.</strong> ' + feedback.dataset.completeFeedback;
          another.hidden = false;
          anotherButton.focus();
        } else {
          feedback.textContent = 'Review the highlighted questions. Use details in both images and choose the response that calls for appropriate human review.';
          another.hidden = true;
        }
        feedback.hidden = false;
      });
    });

    select.addEventListener('change', () => {
      resetComparison();
      rememberScenario(feedbackMode, null);
      picker.hidden = false;
      start.disabled = !select.value;
    });
    function openComparison(moveFocus = true) {
      resetComparison();
      const activeCard = allCards.find(card => card.dataset.bank === select.value);
      if (!activeCard) return;
      shuffleChoices(activeCard);
      picker.hidden = true;
      deck.hidden = false;
      activeCard.hidden = false;
      count.textContent = activeCard.dataset.program;
      const heading = activeCard.querySelector('h3');
      heading?.setAttribute('tabindex', '-1');
      restoreChoices(activeCard);
      rememberScenario(feedbackMode, activeCard);
      if (moveFocus) heading?.focus();
    }
    start.addEventListener('click', () => openComparison());
    const savedCard = allCards.find(card => card.dataset.program === practice.scenarios[feedbackMode]);
    if (savedCard) {
      select.value = savedCard.dataset.bank;
      start.disabled = false;
      openComparison(false);
    }
    anotherButton.addEventListener('click', () => {
      resetComparison();
      rememberScenario(feedbackMode, null);
      select.value = '';
      start.disabled = true;
      picker.hidden = false;
      select.focus();
    });
    return;
  }

  if (feedbackMode === 'program-scenario' && simulation.querySelector('.program-scenario-select')) {
    const select = simulation.querySelector('.program-scenario-select');
    const start = simulation.querySelector('.program-scenario-start');
    const picker = simulation.querySelector('.program-scenario-picker');
    const deck = simulation.querySelector('.scenario-deck');
    const actions = simulation.querySelector('.program-scenario-actions');
    const anotherButton = simulation.querySelector('.program-scenario-another');
    const count = simulation.querySelector('.simulation-count');

    function shuffleChoices(card) {
      card.querySelectorAll('.choices').forEach(choiceGroup => {
        const choices = [...choiceGroup.children];
        for (let index = choices.length - 1; index > 0; index -= 1) {
          const swapIndex = Math.floor(Math.random() * (index + 1));
          [choices[index], choices[swapIndex]] = [choices[swapIndex], choices[index]];
        }
        choices.forEach(choice => choiceGroup.appendChild(choice));
      });
    }

    function resetScenario() {
      allCards.forEach(card => {
        card.hidden = true;
        card.querySelectorAll('input').forEach(input => { input.checked = false; });
        // Written reflections remain saved for their own career scenario.
        card.querySelectorAll('.decision-pathway-step').forEach((step, index) => { step.hidden = index !== 0; });
        card.querySelectorAll('.feedback').forEach(feedback => {
          feedback.hidden = true;
          feedback.classList.remove('incorrect');
        });
      });
      deck.hidden = true;
      actions.hidden = true;
      count.textContent = 'Choose a program';
    }

    allCards.forEach(card => {
      const steps = [...card.querySelectorAll('.decision-pathway-step')];
      steps.forEach((step, stepIndex) => {
        const check = step.querySelector('.scenario-check');
        if (!check) return;
        const feedback = step.querySelector('.feedback');
        step.addEventListener('change', () => {
          feedback.hidden = true;
          steps.slice(stepIndex + 1).forEach(later => { later.hidden = true; });
          actions.hidden = true;
        });
        check.addEventListener('click', () => {
          const answer = step.querySelector('input:checked');
        if (!answer) {
          feedback.textContent = 'Choose a response before checking your decision.';
          feedback.classList.add('incorrect');
          feedback.hidden = false;
          return;
        }
        const correct = JSON.parse(step.dataset.correct || '[]').includes(answer.value);
        feedback.classList.toggle('incorrect', !correct);
        if (correct) {
          feedback.innerHTML = '<strong>Good thinking.</strong> You identified an important part of using AI responsibly.';
          const nextStep = steps[stepIndex + 1];
          if (nextStep) {
            nextStep.hidden = false;
            const nextControl = nextStep.querySelector('input, textarea');
            nextControl?.focus();
          }
        } else {
          feedback.innerHTML = '<strong>Try again.</strong> Look for the choice that protects people and keeps a trained person responsible for the final decision.';
        }
        feedback.hidden = false;
      });
      });
      const exemplarButton = card.querySelector('.scenario-exemplar');
      const exemplarFeedback = card.querySelector('.exemplar-feedback');
      const reflection = card.querySelector('textarea');
      reflection.addEventListener('input', () => { exemplarFeedback.hidden = true; actions.hidden = true; });
      const originalExemplar = exemplarFeedback.innerHTML;
      exemplarButton.addEventListener('click', () => {
        const response = reflection.value.trim();
        if (!response) {
          exemplarFeedback.innerHTML = '<strong>Write your explanation first.</strong> Then compare it with the exemplar to see which ideas you included.';
          exemplarFeedback.classList.add('incorrect');
          exemplarFeedback.hidden = false;
          return;
        }
        exemplarFeedback.innerHTML = originalExemplar;
        exemplarFeedback.classList.remove('incorrect');
        exemplarFeedback.hidden = false;
        actions.hidden = false;
        anotherButton.focus();
      });
    });

    select.addEventListener('change', () => {
      resetScenario();
      rememberScenario(feedbackMode, null);
      picker.hidden = false;
      start.disabled = !select.value;
    });
    function openScenario(moveFocus = true) {
      resetScenario();
      const activeCard = allCards[Number(select.value) - 1];
      if (!activeCard) return;
      shuffleChoices(activeCard);
      picker.hidden = true;
      deck.hidden = false;
      activeCard.hidden = false;
      count.textContent = activeCard.dataset.program;
      const heading = activeCard.querySelector('.scenario-category');
      heading?.setAttribute('tabindex', '-1');
      restoreChoices(activeCard);
      rememberScenario(feedbackMode, activeCard);
      // Recheck saved selections to reveal each successive step; no completion is assumed.
      if (moveFocus) heading?.focus();
    }
    start.addEventListener('click', () => openScenario());
    const savedCardIndex = allCards.findIndex(card => card.dataset.program === practice.scenarios[feedbackMode]);
    if (savedCardIndex >= 0) {
      select.value = String(savedCardIndex + 1);
      start.disabled = false;
      openScenario(false);
    }
    anotherButton.addEventListener('click', () => {
      resetScenario();
      rememberScenario(feedbackMode, null);
      select.value = '';
      start.disabled = true;
      picker.hidden = false;
      select.focus();
    });
    return;
  }

  function beginSimulation(selectedCards) {
    allCards.forEach(card => {
      if (!selectedCards.includes(card)) card.remove();
    });
    simulation.querySelector('.scenario-deck').hidden = false;
    simulation.querySelector('.scenario-controls').hidden = false;
    const count = simulation.querySelector('.simulation-count');
    count.innerHTML = `${feedbackMode === 'media-audit' ? 'Comparison' : 'Case'} <span>1</span> of ${selectedCards.length}`;
    const caseNumber = count.querySelector('span');
    let currentCase = 0;
    const completed = new Set();

    function showCase(index, moveFocus = false) {
      currentCase = Math.min(Math.max(index, 0), selectedCards.length - 1);
      selectedCards.forEach((card, cardIndex) => { card.hidden = cardIndex !== currentCase; });
      caseNumber.textContent = String(currentCase + 1);
      previousCase.disabled = currentCase === 0;
      nextCase.disabled = !completed.has(currentCase);
      nextCase.textContent = currentCase === selectedCards.length - 1 ? 'Complete simulation ✓' : `Next ${feedbackMode === 'media-audit' ? 'comparison' : 'case'} →`;
      if (moveFocus) {
        const heading = selectedCards[currentCase].querySelector('h3, .scenario-category');
        heading?.setAttribute('tabindex', '-1');
        heading?.focus();
      }
    }

    selectedCards.forEach((card, cardIndex) => {
      const check = card.querySelector('.scenario-check');
      const feedback = card.querySelector('.feedback');
      const correctFeedback = feedback.innerHTML;
      check.addEventListener('click', () => {
        const answer = card.querySelector('input:checked');
        if (!answer) {
          feedback.textContent = 'Choose a decision before checking your answer.';
          feedback.classList.add('incorrect');
          feedback.hidden = false;
          return;
        }
        const correct = JSON.parse(card.dataset.correct || '[]').includes(answer.value);
        feedback.classList.toggle('incorrect', !correct);
        if (correct) {
          completed.add(cardIndex);
          feedback.innerHTML = '<strong>Good decision.</strong> ' + correctFeedback;
          if (cardIndex === currentCase) nextCase.disabled = false;
        } else {
          feedback.innerHTML = feedbackMode === 'media-audit'
            ? '<strong>Not yet.</strong> Identify the obvious concern, then remember that a polished appearance never replaces normal source, claim, permission, and context checks.'
            : '<strong>Not yet.</strong> Use the Human Decisions Map to identify where a trained person must check or decide.';
        }
        feedback.hidden = false;
      });
    });

    previousCase.addEventListener('click', () => showCase(currentCase - 1, true));
    nextCase.addEventListener('click', () => {
      if (currentCase === selectedCards.length - 1) {
        nextCase.textContent = 'Simulation complete ✓';
        nextCase.disabled = true;
        simulation.querySelector('.simulation-count').textContent = `${selectedCards.length} of ${selectedCards.length} complete`;
        return;
      }
      showCase(currentCase + 1, true);
    });
    showCase(0);
  }

  const selectedCards = [];
  const bankNumbers = [...new Set(allCards.map(card => card.dataset.bank))];
  bankNumbers.forEach(bank => {
    const bankCards = allCards.filter(card => card.dataset.bank === bank);
    selectedCards.push(bankCards[Math.floor(Math.random() * bankCards.length)]);
  });
  beginSimulation(selectedCards.slice(0, cardLimit || selectedCards.length));
});

// Restore choices after matching/ordering options and scenario choices have been shuffled.
restoreChoices();
