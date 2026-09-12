import type {ComponentType} from 'react';
import {TitleCard} from './TitleCard';
import {StickmanTalk} from './StickmanTalk';
import {ConceptCutaway} from './ConceptCutaway';
import {PlanCapture} from './PlanCapture';
import {PlanBroll} from './PlanBroll';
import {PlanLogos} from './PlanLogos';
import type {CharteTokens} from '../types';

// Registre des composants (§8) : le Monteur (A7) doit d'abord reutiliser un
// composant d'ici, sinon en etendre un, sinon en creer un nouveau (qui
// entre au registre avec le statut "nouveau" dans composants/REGISTRE.md).
//
// Le composant Subtitles n'est pas ici : il est surimprime sur toutes les
// scenes par Video.tsx, ce n'est pas un choix par scene.

export type ComposantParams = Record<string, unknown> & {charte?: CharteTokens};

export const REGISTRE: Record<string, ComponentType<any>> = {
  TitleCard,
  StickmanTalk,
  ConceptCutaway,
  // Composants « contenants » (E5b) : ils ne dessinent rien, ils mettent en
  // scene un asset resolu par A8. Leur variete ne coute pas de code — c'est
  // ce qui inverse le barème qui poussait A7 a toujours reutiliser le meme
  // schema plutot qu'a en creer un nouveau.
  PlanCapture,
  PlanBroll,
  PlanLogos,
};

export function composantExiste(nom: string): boolean {
  return nom in REGISTRE;
}
