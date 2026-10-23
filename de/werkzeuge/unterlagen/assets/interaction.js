(() => {
  'use strict';
  const slides = [...document.querySelectorAll('[data-slide]')];
  const position = document.querySelector('#position');
  const previous = document.querySelector('#previous');
  const next = document.querySelector('#next');
  const overview = document.querySelector('#overview');
  const noteButton = document.querySelector('#show-notes');
  let current = 0;
  let shiftAlone = false;

  function showSlide(index) {
    current = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach((slide, i) => { slide.hidden = i !== current; });
    if (position) position.textContent = `${current + 1} / ${slides.length}`;
    if (previous) previous.disabled = current === 0;
    if (next) next.disabled = current === slides.length - 1;
  }
  function toggleNotes() {
    const visible = document.body.classList.toggle('notes-visible');
    noteButton?.setAttribute('aria-pressed', String(visible));
  }
  const isInput = target => target instanceof Element && Boolean(target.closest('input, textarea, select, [contenteditable="true"]'));
  if (slides.length) {
    showSlide(0);
    previous.addEventListener('click', () => showSlide(current - 1));
    next.addEventListener('click', () => showSlide(current + 1));
    noteButton.addEventListener('click', toggleNotes);
    document.querySelector('#show-overview').addEventListener('click', () => overview.showModal());
    document.querySelector('#close-overview').addEventListener('click', () => overview.close());
    document.querySelectorAll('[data-goto]').forEach(button => button.addEventListener('click', () => {
      showSlide(Number(button.dataset.goto));
      overview.close();
    }));
    document.addEventListener('keydown', event => {
      if (isInput(event.target) || overview.open || event.ctrlKey || event.metaKey || event.altKey) return;
      if (event.key === 'Shift') { if (!event.repeat) shiftAlone = true; return; }
      shiftAlone = false;
      if (event.shiftKey) return;
      if (['ArrowRight', 'PageDown', 'ArrowLeft', 'PageUp', 'Home', 'End'].includes(event.key)) {
        event.preventDefault();
        if (event.key === 'Home') showSlide(0);
        else if (event.key === 'End') showSlide(slides.length - 1);
        else showSlide(current + (['ArrowRight', 'PageDown'].includes(event.key) ? 1 : -1));
      } else if (event.key.toLowerCase() === 'n') toggleNotes();
    });
    document.addEventListener('keyup', event => {
      if (event.key === 'Shift') {
        if (shiftAlone && !isInput(event.target) && !overview.open) toggleNotes();
        shiftAlone = false;
      }
    });
    window.addEventListener('blur', () => { shiftAlone = false; });
  }

  const status = document.querySelector('#copy-status');
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const value = document.getElementById(button.dataset.copy).textContent;
    let success = false;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(value);
        success = true;
      }
    } catch (_) { /* A denied clipboard falls back to a local selection. */ }
    if (!success) {
      const field = document.createElement('textarea');
      field.value = value;
      field.className = 'clipboard-helper';
      document.body.append(field);
      field.select();
      try { success = document.execCommand('copy'); } catch (_) { success = false; }
      field.remove();
      button.focus();
    }
    status.textContent = success ? 'Prompt kopiert.' : 'Kopieren nicht möglich. Bitte den Prompt markieren und manuell kopieren.';
  }));

  const filter = document.querySelector('#role-filter');
  if (filter) {
    const examples = [...document.querySelectorAll('[data-role]')];
    const update = () => {
      let visible = 0;
      examples.forEach(example => {
        example.hidden = Boolean(filter.value && example.dataset.role !== filter.value);
        if (!example.hidden) visible += 1;
      });
      document.querySelector('#example-count').textContent = `${visible} von ${examples.length} Beispielen`;
    };
    filter.addEventListener('change', update);
    update();
  }

  let closedDetails = [];
  window.addEventListener('beforeprint', () => {
    closedDetails.push(...document.querySelectorAll('details:not([open])'));
    closedDetails.forEach(item => { item.open = true; });
    document.querySelectorAll('textarea').forEach(field => {
      let mirror = field.nextElementSibling;
      if (!mirror?.classList.contains('print-answer')) {
        mirror = document.createElement('div');
        mirror.className = 'print-answer';
        mirror.setAttribute('aria-hidden', 'true');
        field.after(mirror);
      }
      mirror.textContent = field.value;
    });
  });
  window.addEventListener('afterprint', () => {
    closedDetails.forEach(item => { item.open = false; });
    closedDetails = [];
    document.querySelectorAll('.print-answer').forEach(mirror => mirror.remove());
  });
  document.querySelector('#print').addEventListener('click', () => window.print());
})();
