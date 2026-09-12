import React from 'react';
import type {CharteTokens} from '../types';

type Props = {
  charte: CharteTokens;
  children: React.ReactNode;
  // Barre de fenetre a trois pastilles. Sur une capture de page web elle
  // dit « c'est un navigateur » sans qu'on ait a l'ecrire ; sur un terminal
  // ou une photo, elle ment, d'ou le choix par scene.
  barre?: boolean;
  largeur?: number | string;
  rayon?: number;
};

/**
 * Le cadre dans lequel vit tout asset rectangulaire (capture, image, video).
 *
 * Il existe pour une raison precise : sur fond sombre, une capture d'ecran
 * posee a nu se confond avec le fond quand elle est sombre, et cogne comme
 * un rectangle blanc quand elle est claire. Le liseré clair la detoure, et
 * l'ombre portee la decolle — c'est le seul generateur de profondeur du
 * systeme, celui qui manquait quand tout etait du trait plat sur aplat.
 */
export const Cadre: React.FC<Props> = ({charte, children, barre = false, largeur = '100%', rayon = 28}) => {
  const hauteurBarre = barre ? 56 : 0;

  return (
    <div
      style={{
        width: largeur,
        borderRadius: rayon,
        overflow: 'hidden',
        backgroundColor: charte.couleurs.fond,
        // Liseré clair tres faible + ombre profonde. Les deux sont
        // indispensables sur fond sombre : l'ombre seule ne se voit pas,
        // le liseré seul ne decolle pas.
        boxShadow: [
          `0 0 0 1px ${charte.couleurs.texte_principal}1f`,
          '0 30px 70px rgba(0,0,0,0.55)',
          '0 8px 20px rgba(0,0,0,0.35)',
        ].join(', '),
      }}
    >
      {barre ? (
        <div
          style={{
            height: hauteurBarre,
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            paddingLeft: 22,
            backgroundColor: `${charte.couleurs.texte_principal}14`,
          }}
        >
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              style={{
                width: 14,
                height: 14,
                borderRadius: 7,
                backgroundColor: `${charte.couleurs.texte_principal}3d`,
              }}
            />
          ))}
        </div>
      ) : null}
      {children}
    </div>
  );
};
