# Scanner — mise en place (à faire une seule fois)

Le déploiement est automatique : chaque push sur `main` qui touche `scanner/`
lance le workflow **Scanner** (`.github/workflows/scanner.yml`), qui teste,
construit, crée la base D1 et le bucket R2 s'ils n'existent pas, applique les
migrations et déploie le Worker.

Ce qui reste à faire à la main, une fois, dans le tableau de bord Cloudflare
et sur GitHub :

## 1. Jeton d'API Cloudflare : vérifier ses permissions

Le secret GitHub `CLOUDFLARE_API_TOKEN` doit avoir, au niveau du compte :

| Permission | Niveau |
|---|---|
| Workers Scripts | Edit |
| D1 | Edit |
| Workers R2 Storage | Edit |
| Account Settings | Read |

Le modèle « Edit Cloudflare Workers » ne contient **pas** D1 : ajoute-la
(My Profile → API Tokens → ton jeton → Edit → + Add more → Account → D1 → Edit).

## 2. Activer R2 et le sous-domaine workers.dev

- **R2** : tableau de bord → R2 Object Storage → activer. Cloudflare demande un
  moyen de paiement même pour l'offre gratuite ; rien n'est facturé sous
  10 Go de stockage et 1 million d'écritures par mois.
- **workers.dev** : si tu n'as jamais déployé de Worker, choisis ton
  sous-domaine dans Workers & Pages (première visite). L'app sera servie sur
  `https://scanner.<ton-sous-domaine>.workers.dev`.

Si le workflow échoue à l'étape « Création de D1 et R2 » (jeton sans les
droits, par exemple), tu peux créer les deux ressources à la main depuis ton
ordinateur, puis relancer le workflow (Actions → Scanner → Re-run) :

```sh
cd scanner
npx wrangler login
npx wrangler d1 create scanner
npx wrangler r2 bucket create scanner-files
```

Pas besoin de recopier l'id de la base : le workflow la retrouve par son nom.

## 3. Protéger l'app avec Cloudflare Access

Après le premier déploiement réussi :

1. **Workers & Pages → scanner → Settings → Domains & Routes** : sur la ligne
   `workers.dev`, active **Cloudflare Access**. Cela crée une application
   Access pour `scanner.<sous-domaine>.workers.dev`.
   *(Sinon, à la main : Zero Trust → Access → Applications → Add an
   application → Self-hosted, domaine `scanner.<sous-domaine>.workers.dev`.)*
2. **Zero Trust → Access → Applications → l'application → Policies** : une
   seule règle *Allow* avec *Include → Emails →* ton adresse.
3. **Méthode de connexion** : garde **One-time PIN** (code reçu par e-mail).
   Elle reste dans la fenêtre de l'app installée sur l'iPhone, contrairement
   aux connexions Google/GitHub qui ouvrent parfois Safari à part.
4. Relève deux valeurs :
   - le **tag AUD** : Access → Applications → l'application → *Overview* →
     *Application Audience (AUD) Tag* ;
   - le **domaine d'équipe** : Zero Trust → Settings → Custom Pages →
     *Team domain* (`<equipe>.cloudflareaccess.com`).

## 4. Donner ces valeurs au Worker

GitHub → dépôt → Settings → Secrets and variables → Actions → onglet
**Variables** → New repository variable :

| Nom | Valeur |
|---|---|
| `ACCESS_TEAM_DOMAIN` | `<equipe>.cloudflareaccess.com` |
| `ACCESS_AUD` | le tag AUD |
| `ACCESS_ALLOWED_EMAILS` | *(facultatif)* ton e-mail — seconde barrière si la politique Access était un jour trop large |

Puis relance le workflow (Actions → Scanner → Run workflow sur `main`).

Tant que ces variables manquent, l'API répond `503` à tout : elle échoue
fermée, jamais ouverte. L'écran d'accueil affiche alors « Cloudflare Access
non configuré sur le Worker ».

## 5. Installer sur l'iPhone

Voir le [README](../README.md#installer-sur-liphone).

## Développement en local (facultatif)

```sh
cd scanner
npm ci                      # .npmrc active legacy-peer-deps (bug de npm)
echo 'ACCESS_DEV_BYPASS=1' > .dev.vars      # jamais commité
npx wrangler d1 migrations apply DB --local
npm run build && npx wrangler dev           # app + API sur http://localhost:8787
# ou, avec rechargement à chaud : `npx wrangler dev` dans un terminal,
# `npm run dev` dans un autre (Vite relaie /api vers 8787)
```

`ACCESS_DEV_BYPASS` ne désactive la vérification que pour les requêtes vers
`localhost` : en production, l'hôte n'est jamais `localhost`.
