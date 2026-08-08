document.querySelector('.menu-button')?.addEventListener('click', event => {
  const nav = document.querySelector('#course-nav');
  const open = nav.classList.toggle('open');
  event.currentTarget.setAttribute('aria-expanded', String(open));
});

document.querySelectorAll('.question').forEach(question => {
  const button = question.querySelector('.check-answer');
  if (!button) return;
  button.addEventListener('click', () => {
    const feedback = question.querySelector('.feedback');
    const correct = JSON.parse(question.dataset.correct || '[]');
    let isCorrect = false;
    if (['matching_question', 'categorization_question'].includes(question.dataset.questionType)) {
      const selects = [...question.querySelectorAll('.matching-row select')];
      if (selects.some(select => !select.value)) {
        feedback.textContent = 'Choose a match for every row first.';
        feedback.classList.add('incorrect');
        feedback.hidden = false;
        return;
      }
      isCorrect = selects.every(select => correct[select.dataset.responseId] === select.value);
    } else if (question.dataset.questionType === 'ordering_question') {
      const selects = [...question.querySelectorAll('.ordering-row select')];
      if (selects.some(select => !select.value)) {
        feedback.textContent = 'Choose a step for every position first.';
        feedback.classList.add('incorrect');
        feedback.hidden = false;
        return;
      }
      const selectedValues = selects.map(select => select.value);
      isCorrect = selectedValues.length === correct.length && selectedValues.every((value, index) => value === correct[index]);
    } else {
      const selected = [...question.querySelectorAll('input:checked')].map(input => input.value);
      if (!selected.length) {
        feedback.textContent = 'Choose an answer first.';
        feedback.classList.add('incorrect');
        feedback.hidden = false;
        return;
      }
      isCorrect = selected.length === correct.length && selected.every(value => correct.includes(value));
    }
    feedback.classList.toggle('incorrect', !isCorrect);
    if (!isCorrect) feedback.innerHTML = '<strong>Not yet.</strong> Review the idea above and try another answer.';
    feedback.hidden = false;
  });
});

document.querySelectorAll('textarea').forEach((field, index) => {
  const key = `ai-literacy-${document.body.dataset.lesson || 'home'}-${index}`;
  field.value = localStorage.getItem(key) || '';
  field.addEventListener('input', () => localStorage.setItem(key, field.value));
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
  const requested = Number(new URLSearchParams(location.search).get('step')) - 1;
  let current = Number.isInteger(requested) && requested >= 0 ? requested : Number(localStorage.getItem(storageKey) || 0);
  current = Math.min(Math.max(current, 0), steps.length - 1);

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
    localStorage.setItem(storageKey, String(current));
    history.replaceState(null, '', `${location.pathname}?step=${current + 1}`);
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
      announcement.textContent = 'Lesson complete. Submit any required work in your course.';
      next.textContent = 'Lesson complete ✓';
      next.disabled = true;
      return;
    }
    showStep(current + 1, true);
  });
  showStep(current);
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

document.querySelectorAll('.scenario-simulation').forEach(simulation => {
  const allCards = [...simulation.querySelectorAll('.scenario-card')];
  const selectedCards = [];
  const bankNumbers = [...new Set(allCards.map(card => card.dataset.bank))];
  bankNumbers.forEach(bank => {
    const bankCards = allCards.filter(card => card.dataset.bank === bank);
    selectedCards.push(bankCards[Math.floor(Math.random() * bankCards.length)]);
  });
  allCards.forEach(card => {
    if (!selectedCards.includes(card)) card.remove();
  });

  const previousCase = simulation.querySelector('.scenario-previous');
  const nextCase = simulation.querySelector('.scenario-next');
  const caseNumber = simulation.querySelector('.simulation-count span');
  const feedbackMode = simulation.dataset.feedbackMode || 'human-decisions';
  let currentCase = 0;
  const completed = new Set();

  function showCase(index, moveFocus = false) {
    currentCase = Math.min(Math.max(index, 0), selectedCards.length - 1);
    selectedCards.forEach((card, cardIndex) => { card.hidden = cardIndex !== currentCase; });
    caseNumber.textContent = String(currentCase + 1);
    previousCase.disabled = currentCase === 0;
    nextCase.disabled = !completed.has(currentCase);
    nextCase.textContent = currentCase === selectedCards.length - 1 ? 'Complete simulation ✓' : 'Next case →';
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
          ? '<strong>Not yet.</strong> Compare the safety, accuracy, permission, and privacy details in both images, then try again.'
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
});
