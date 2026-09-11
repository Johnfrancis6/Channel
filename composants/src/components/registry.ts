import type {ComponentType} from 'react';
import {TitleCard} from './TitleCard';
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
};

export function composantExiste(nom: string): boolean {
  return nom in REGISTRE;
}
