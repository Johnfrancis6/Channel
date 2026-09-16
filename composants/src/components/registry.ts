import type {ComponentType} from 'react';
import {TitleCard} from './TitleCard';
import {StickmanTalk} from './StickmanTalk';
import {ConceptCutaway} from './ConceptCutaway';
import {PlanCapture} from './PlanCapture';
import {PlanBroll} from './PlanBroll';
import {PlanLogos} from './PlanLogos';
import {PlanNavigateurCurseur} from './PlanNavigateurCurseur';
import {PlanDeuxTerminaux} from './PlanDeuxTerminaux';
import {PlanTerminalFrappe} from './PlanTerminalFrappe';
import {PlanListeSequencee} from './PlanListeSequencee';
import type {CharteTokens} from '../types';

// Registre des composants (§8) : le Monteur (A7) doit d'abord reutiliser un
// composant d'ici, sinon en etendre un, sinon en creer un nouveau (qui
// entre au registre avec le statut "nouveau" dans composants/REGISTRE.md).
//
// Les **surcouches** ne sont pas ici : le registre associe un composant a une
// scene entiere, et ce qui se pose par-dessus une scene n'est pas un choix
// par scene. Il y en a deux :
//   - Subtitles, surimprime sur toute la video par Video.tsx ;
//   - InsertFootage, l'insert de video reelle, borne dans le temps par un
//     <Sequence> et declare sur la scene (`scene.inserts`). L'y mettre en
//     ferait un plan plein cadre pendant toute la scene, c'est-a-dire
//     exactement PlanBroll.

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
  // Composants « mis en scene » (2026-09-16) : ils dessinent un dispositif
  // dont le sujet est le GESTE ou la GRADATION, pas un asset. Une capture
  // fixe ne peut montrer ni un curseur qui cherche, ni une commande qui
  // s'ecrit, ni une echelle qui s'allume barreau par barreau.
  PlanNavigateurCurseur,
  PlanDeuxTerminaux,
  PlanTerminalFrappe,
  PlanListeSequencee,
};

export function composantExiste(nom: string): boolean {
  return nom in REGISTRE;
}
