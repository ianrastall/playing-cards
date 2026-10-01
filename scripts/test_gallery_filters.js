/* Exercise the viewer's actual predicates against its generated inventory. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'assets/gallery.js'), 'utf8');
const declarations = source.slice(source.indexOf('  const isFace ='), source.indexOf('  const option ='));
const {sets} = vm.runInNewContext(`(() => {${declarations}; return {sets};})()`);
const html = fs.readFileSync(path.join(root, 'designs/design3/poker.html'), 'utf8');
const {assets} = JSON.parse(html.match(/<script id="card-data" type="application\/json">(.*?)<\/script>/s)[1]);
const choose = (design, view) => assets.filter(a => a.design === design && a.format === 'poker' && sets.find(s => s[0] === view)[2](a));
for (const design of ['design1', 'design2', 'design3']) {
  assert.equal(choose(design, 'faces').length, 54, `${design}: all faces`);
  assert.equal(choose(design, 'french').length, 54, `${design}: French deck`);
  assert.equal(choose(design, 'jokers').length, 2, `${design}: Jokers`);
  for (const suit of ['spades', 'hearts', 'diamonds', 'clubs']) {
    const cards = choose(design, suit);
    assert.equal(cards.length, 13, `${design}: ${suit}`);
    assert.deepEqual(cards.map(a => a.rank), ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']);
  }
}
assert.equal(choose('design3', 'a10').length, 40);
assert.equal(choose('design3', 'numbers').length, 36);
for (const rank of ['queen', 'jack', 'joker']) {
  const review = choose('design3', `review-${rank}s`);
  assert.equal(review.length, rank === 'joker' ? 2 : 4);
  assert.ok(review.every(a => a.status === 'review'));
}
assert.ok(choose('design3', 'faces').every(a => !['masters','pip','frame'].includes(a.kind)));
console.log('PASS viewer filters: all 54 Poker faces, 13 per suit, both Jokers; review sets and components remain distinct');
