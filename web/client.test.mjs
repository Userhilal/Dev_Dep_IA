// Contrôles RECONSTITUÉS à partir du manuel TP2 ; ne sont pas les 12 tests du kit absent.
import test from 'node:test';
import assert from 'node:assert/strict';
import { classer, messageErreur } from './client.js';

for (const [code, attendu] of [
  ['ENTREE_INVALIDE', 'refusé'],
  ['NON_AUTHENTIFIE', 'Clé'],
  ['ACCES_REFUSE', 'rôle'],
  ['MODELE_INDISPONIBLE', 'Modèle'],
  ['ERREUR_INTERNE', 'interne'],
]) {
  test(`erreur ${code}`, () => assert.ok(messageErreur(code, 400).includes(attendu)));
}
test('erreur inconnue', () => assert.match(messageErreur('X', 418), /418/));
test('positif', async () => {
  const r = await classer({ adresse: 'http://localhost:8000', cle: 'abc', texte: 'bien',
    fetcher: async () => ({ ok: true, json: async () => ({label:'POSITIVE',score:0.777}) }) });
  assert.equal(r.ok, true); assert.match(r.message, /78 %/);
});
test('indéterminé', async () => {
  const r = await classer({ adresse: 'http://localhost:8000', cle:'abc', texte:'x',
    fetcher: async () => ({ ok: true, json: async () => ({label:'INDETERMINE',score:0.5162}) }) });
  assert.match(r.message, /humain/);
});
test('clé invalide', async () => {
  const r = await classer({ adresse: 'http://localhost:8000', cle:'abc', texte:'x',
    fetcher: async () => ({ ok: false, status:401, json: async () => ({erreur:{code:'NON_AUTHENTIFIE'}}) }) });
  assert.equal(r.ok, false); assert.match(r.message, /Clé/);
});
test('CORS ou réseau', async () => {
  const r = await classer({ adresse:'x', cle:'abc', texte:'x', fetcher:async () => {throw Error('CORS')} });
  assert.equal(r.ok, false); assert.match(r.message, /CORS/);
});
test('JSON illisible', async () => {
  const r = await classer({ adresse:'x',cle:'abc',texte:'x',
    fetcher: async () => ({ok:false,status:500,json:async () => {throw Error('not json')} }) });
  assert.match(r.message,/500/);
});
test('en-tête X-API-Key', async () => {
  let options;
  await classer({adresse:'http://localhost:8000/',cle:'cle-test',texte:'bon',
    fetcher:async (url,o) => { assert.match(url,/\/v1\/predict$/); options=o; return {ok:true,json:async()=>({label:'POSITIVE',score:0.8})} }});
  assert.equal(options.headers['X-API-Key'],'cle-test');
  assert.equal(JSON.parse(options.body).text,'bon');
});
