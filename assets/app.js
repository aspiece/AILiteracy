document.querySelector('.menu-button')?.addEventListener('click', event => {
  const nav = document.querySelector('#course-nav');
  const open = nav.classList.toggle('open');
  event.currentTarget.setAttribute('aria-expanded', String(open));
});

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
  button.addEventListener('click', () => {
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
      if (question.dataset.questionType === 'matching_question') {
        const selectedValues = selects.map(select => select.value);
        if (new Set(selectedValues).size !== selectedValues.length) {
          feedback.textContent = 'Use each match only once.';
          feedback.classList.add('incorrect');
          feedback.hidden = false;
          return;
        }
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
      if (new Set(selectedValues).size !== selectedValues.length) {
        feedback.textContent = 'Use each step only once.';
        feedback.classList.add('incorrect');
        feedback.hidden = false;
        return;
      }
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
    feedback.replaceChildren();
    if (isCorrect) {
      feedback.textContent = question.dataset.feedbackCorrect || originalCorrectFeedback;
    } else {
      const lead = document.createElement('strong');
      lead.textContent = 'Not yet. ';
      feedback.append(lead, question.dataset.feedbackIncorrect || 'Review the idea above and try another answer.');
    }
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
      picker.hidden = false;
      start.disabled = !select.value;
    });
    start.addEventListener('click', () => {
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
      heading?.focus();
    });
    anotherButton.addEventListener('click', () => {
      resetComparison();
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
