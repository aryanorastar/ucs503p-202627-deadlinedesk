document$.subscribe(() => {
  if (typeof renderMathInElement === 'function') {
    renderMathInElement(document.body);
  }
});
