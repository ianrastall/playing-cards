/* One shared stage preserves each card's complete canvas and aspect ratio. */
(() => {
  const data = JSON.parse(document.querySelector('#card-data').textContent);
  const $ = id => document.getElementById(id);
  const design = $('design-select'), format = $('format-select'), set = $('set-select');
  const search = $('card-search'), card = $('card-select'), range = $('card-range');
  const image = $('viewer-image'), turn = $('viewer-turn'), download = $('viewer-download');
  let available = [], cards = [], index = 0;
  let turned = false;
  const isFace = a => a.kind === 'face' || a.kind === 'study';
  const sets = [
    ['pips', 'Large suit pips', a => a.kind === 'pip'],
    ...['queen', 'jack', 'joker'].map(rank =>
      [`review-${rank}s`, `${rank[0].toUpperCase() + rank.slice(1)}s for review`, a => a.kind === 'study' && a.rank === rank]),
    ['studies', 'Court artwork for review', a => a.kind === 'study'],
    ['faces', 'All faces', isFace],
    ['a10', 'Aces & number cards', a => a.kind === 'face' && a.system === 'french-suited' && /^(?:ace|[2-9]|10)$/.test(a.rank)],
    ['french', 'French-suited deck', a => isFace(a) && a.system === 'french-suited'],
    ['tarot', 'Tarot deck', a => a.kind === 'face' && a.system === 'tarot'],
    ['first-proofs', 'First Tarot proofs', a => a.kind === 'face' && a.proof_group === 'tarot-first-proofs'],
    ...['spades', 'hearts', 'diamonds', 'clubs', 'batons', 'cups', 'swords', 'coins'].map(suit =>
      [suit, suit[0].toUpperCase() + suit.slice(1), a => isFace(a) && a.suit === suit]),
    ['trumps', 'Trumps & Fool', a => a.kind === 'face' && a.arcana === 'major'],
    ['jokers', 'Jokers', a => isFace(a) && a.rank === 'joker'],
    ['numbers', 'Number cards', a => a.kind === 'face' && a.arcana !== 'major' && /^(?:[2-9]|10)$/.test(a.rank)],
    ['backs', 'Card backs', a => a.kind === 'back'],
    ['frames', 'Blank face frames', a => a.kind === 'frame'],
    ['masters', 'Original artwork masters', a => a.kind === 'masters']
  ];
  const option = (value, name) => new Option(name, value);
  const title = a => a.chinese_title ? `${a.title} · ${a.chinese_title}` : a.title;
  function remember(a) {
    const params = new URLSearchParams({design: design.value, size: format.value, set: set.value});
    if (a) params.set('card', a.id);
    if (search.value) params.set('q', search.value);
    if (turned) params.set('turn', '1');
    history.replaceState(null, '', '#' + params);
  }
  function show(next, save = true) {
    index = cards.length ? (next + cards.length) % cards.length : 0;
    const a = cards[index];
    card.disabled = range.disabled = !a;
    $('viewer-prev').disabled = $('viewer-next').disabled = cards.length < 2;
    turn.disabled = !a;
    image.hidden = download.hidden = !a;
    $('empty-state').hidden = !!a;
    $('image-status').textContent = '';
    $('viewer-position').textContent = a ? `${index + 1} / ${cards.length}` : '0 cards';
    $('viewer-context').textContent = `${design.selectedOptions[0].text} / ${format.selectedOptions[0].text} / ${set.selectedOptions[0].text}`;
    $('viewer-title').textContent = a ? title(a) : 'No matching cards';
    $('viewer-detail').textContent = a ? `${a.pixels.join(' × ')} px${a.trim_inches ? ` · ${a.trim_inches.join(' × ')} in` : ' · Original dimensions'}${a.kind === 'masters' ? ' · Source master' : a.kind === 'study' || a.status === 'review' && a.kind === 'face' ? ' · Artwork under review' : a.kind === 'pip' ? ' · Transparent pip master' : ''}` : '';
    range.max = Math.max(1, cards.length);
    range.value = index + 1;
    range.setAttribute('aria-valuetext', a ? `${a.title}, ${index + 1} of ${cards.length}` : 'No matching cards');
    if (a) {
      card.value = a.id;
      image.src = a.src;
      image.alt = title(a);
      image.width = a.pixels[0]; image.height = a.pixels[1];
      download.href = a.src; download.download = a.id.replaceAll('.', '-') + '.png';
    }
    image.classList.toggle('turned', turned);
    turn.setAttribute('aria-pressed', String(turned));
    turn.textContent = turned ? 'Return upright' : 'Turn 180°';
    if (save) remember(a);
  }
  function filter(id) {
    const predicate = sets.find(s => s[0] === set.value)[2];
    const words = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    cards = available.filter(a => predicate(a) && words.every(word => `${title(a)} ${a.detail} ${a.id}`.toLowerCase().includes(word)));
    card.replaceChildren(...cards.map(a => option(a.id, title(a))));
    show(Math.max(0, cards.findIndex(a => a.id === id)));
  }
  function loadSet(preferred = set.value, id) {
    const sizes = new Set(data.assets.filter(a => a.design === design.value).map(a => a.format));
    for (const entry of format.options) entry.disabled = !sizes.has(entry.value);
    if (!sizes.has(format.value)) format.value = sizes.has('poker') ? 'poker' : [...sizes][0];
    available = data.assets.filter(a => a.design === design.value && a.format === format.value);
    const choices = sets.filter(s => available.some(s[2]));
    set.replaceChildren(...choices.map(s => option(s[0], `${s[1]} (${available.filter(s[2]).length})`)));
    set.value = choices.some(s => s[0] === preferred) ? preferred : choices[0][0];
    const faces = available.filter(isFace).length;
    const studies = available.filter(a => a.kind === 'study').length;
    $('availability').textContent = faces ? `${faces} faces · ${available.filter(a => a.kind === 'back').length} backs in this size.${studies ? ` Includes ${studies} court artworks under review.` : ''}${design.value === 'design2' && format.value === 'tarot' && available.some(a => a.kind === 'face' && a.status === 'review') ? ' Layout, names and costumes under review.' : ''}` : 'Faces are not yet available in this size. Browse backs and blank frames.';
    filter(id);
  }
  function restore() {
    const params = new URLSearchParams(location.hash.slice(1));
    design.value = [...design.options].some(o => o.value === params.get('design')) ? params.get('design') : data.design;
    format.value = [...format.options].some(o => o.value === params.get('size')) ? params.get('size') : data.format;
    search.value = params.get('q') || '';
    turned = params.get('turn') === '1';
    const remembered = params.get('set') || data.set;
    loadSet(remembered === 'minchiate' ? 'tarot' : remembered, params.get('card'));
  }
  [design, format].forEach(control => control.addEventListener('change', () => { search.value = ''; loadSet(); }));
  set.addEventListener('change', () => { search.value = ''; filter(); });
  search.addEventListener('input', () => filter(card.value));
  card.addEventListener('change', () => show(cards.findIndex(a => a.id === card.value)));
  range.addEventListener('input', () => show(Number(range.value) - 1));
  $('viewer-prev').addEventListener('click', () => show(index - 1));
  $('viewer-next').addEventListener('click', () => show(index + 1));
  function stepSet(step) { set.selectedIndex = (set.selectedIndex + step + set.length) % set.length; search.value = ''; filter(); }
  $('set-prev').addEventListener('click', () => stepSet(-1));
  $('set-next').addEventListener('click', () => stepSet(1));
  turn.addEventListener('click', () => { turned = !turned; show(index); });
  document.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || /INPUT|SELECT|TEXTAREA/.test(event.target.tagName) || event.target.isContentEditable) return;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') { event.preventDefault(); show(index + (event.key === 'ArrowRight' ? 1 : -1)); }
  });
  image.addEventListener('error', () => { $('image-status').textContent = 'The PNG could not load. Try another card or reload the page.'; });
  image.addEventListener('load', () => { $('image-status').textContent = ''; });
  window.addEventListener('hashchange', () => {
    if (new URLSearchParams(location.hash.slice(1)).has('design')) restore();
  });
  $('browser-controls').hidden = $('card-navigation').hidden = turn.hidden = false;
  restore();
})();
