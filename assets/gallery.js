/* Progressive enhancement only: all image and download links work without JS. */
(() => {
  const allLinks = [...document.querySelectorAll('[data-artwork]')];
  let links = allLinks;
  const search = document.querySelector('#card-search');
  if (search) {
    const count = document.querySelector('#search-count');
    const filter = () => {
      const words = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
      allLinks.forEach(link => {
        const text = `${link.dataset.title} ${link.dataset.detail} ${link.dataset.artwork}`.toLowerCase();
        link.closest('figure').hidden = !words.every(word => text.includes(word));
      });
      links = allLinks.filter(link => !link.closest('figure').hidden);
      document.querySelectorAll('.artwork-section').forEach(section => {
        section.hidden = !section.querySelector('figure:not([hidden])');
      });
      document.querySelectorAll('.collection').forEach(section => {
        section.hidden = !section.querySelector('figure:not([hidden])');
      });
      document.querySelectorAll('.section-links a').forEach(link => {
        link.hidden = document.getElementById(link.hash.slice(1))?.hidden ?? false;
      });
      count.textContent = links.length ? `${links.length} of ${allLinks.length} artworks` : 'No matching cards. Try a different name, suit, or color.';
    };
    search.closest('.gallery-search').hidden = false;
    search.addEventListener('input', filter);
    filter();
  }
  const viewer = document.querySelector('.viewer');
  if (!viewer || typeof viewer.showModal !== 'function') return;
  const image = document.querySelector('#viewer-image');
  const title = document.querySelector('#viewer-title');
  const detail = document.querySelector('#viewer-detail');
  const position = document.querySelector('#viewer-position');
  const download = document.querySelector('#viewer-download');
  const original = document.querySelector('#viewer-original');
  const turn = document.querySelector('#viewer-turn');
  const close = document.querySelector('#viewer-close');
  let index = 0;
  let opener = null;

  function show(next) {
    index = (next + links.length) % links.length;
    const link = links[index];
    const save = link.closest('figure').querySelector('[download]');
    image.src = link.href;
    image.alt = link.dataset.title;
    image.classList.remove('turned');
    turn.setAttribute('aria-pressed', 'false');
    turn.textContent = 'Turn 180°';
    title.textContent = link.dataset.title;
    detail.textContent = `${link.closest('figure').dataset.design === 'design1' ? 'Design 01' : 'Design 02'} · ${link.dataset.detail}`;
    position.textContent = `${index + 1} / ${links.length}`;
    download.href = link.href;
    download.download = save.download;
    original.href = link.href;
  }

  allLinks.forEach(link => link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    opener = link;
    show(links.indexOf(link));
    viewer.showModal();
    document.body.classList.add('viewer-open');
    close.focus();
  }));
  close.addEventListener('click', () => viewer.close());
  viewer.addEventListener('close', () => {
    document.body.classList.remove('viewer-open');
    image.removeAttribute('src');
    opener?.focus({preventScroll: true});
  });
  viewer.addEventListener('click', event => {
    if (event.target !== viewer) return;
    const rect = viewer.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) viewer.close();
  });
  document.querySelector('#viewer-prev').addEventListener('click', () => show(index - 1));
  document.querySelector('#viewer-next').addEventListener('click', () => show(index + 1));
  turn.addEventListener('click', () => {
    const turned = image.classList.toggle('turned');
    turn.setAttribute('aria-pressed', String(turned));
    turn.textContent = turned ? 'Return upright' : 'Turn 180°';
  });
  viewer.addEventListener('keydown', event => {
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      show(index + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
})();
