"""
resoudre_ressources.py — le maillon qui manquait au tuyau d'assets (E5b,
file #18).

Les deux bouts existaient depuis la seance du 15/09 : A6 declare des
`besoins`, `construire_props.preparer_ressources` sait lire
`05b_ressources.json`, et `PlanBroll` / `PlanCapture` / `PlanLogos` savent
afficher le resultat. Rien n'ecrivait le fichier du milieu, donc aucune
image reelle n'est jamais arrivee a l'ecran.

Le test qui compte le plus est `TestRoundTrip` : il verifie que ce qui sort
d'ici entre vraiment de l'autre cote. Un contrat de fichier verifie
seulement sur ses propres assertions est exactement ce qui a produit trois
composants alimentes par rien.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTIL = REPO_ROOT / "outils" / "resoudre_ressources.py"

sys.path.insert(0, str(REPO_ROOT / "agents" / "short-monteur" / "scripts"))
import construire_props  # noqa: E402


def lancer(dossier_video, *args):
    p = subprocess.run(
        [sys.executable, str(OUTIL), "--storyboard",
         str(Path(dossier_video) / "05_storyboard.json"), "--hors-ligne", *args],
        capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout)


class BaseRessources(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="resoudre_")
        self.racine = Path(self.tmp)
        self.video = self.racine / "videos" / "2026-09-16_v01"
        self.assets = self.video / "assets"
        self.assets.mkdir(parents=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def storyboard(self, *besoins_par_scene):
        scenes = [{"id": f"s{i + 1}", "composant": "PlanBroll", "duree_s": 3,
                   "params": {}, "besoins": list(besoins)}
                  for i, besoins in enumerate(besoins_par_scene)]
        (self.video / "05_storyboard.json").write_text(
            json.dumps({"scenes": scenes}), encoding="utf-8")

    def deposer(self, nom, contenu=b"\x00rush"):
        chemin = self.assets / nom
        chemin.write_bytes(contenu)
        return chemin

    def rushes(self, entrees):
        (self.assets / "rushes.json").write_text(
            json.dumps({"rushes": entrees}), encoding="utf-8")

    def table(self):
        return json.loads((self.video / "05b_ressources.json").read_text(encoding="utf-8"))["ressources"]


class TestResolutionLocale(BaseRessources):
    def test_le_nom_du_fichier_suffit(self):
        """Le chemin sans configuration : nommer le rush d'apres la cle."""
        self.storyboard([{"cle": "demo_mcp", "type": "broll"}])
        self.deposer("demo_mcp.mp4")
        code, res = lancer(self.video)
        self.assertEqual(code, 0, res)
        self.assertEqual(self.table()["demo_mcp"]["chemin"], "assets/demo_mcp.mp4")
        self.assertEqual(self.table()["demo_mcp"]["type"], "broll")

    def test_rushes_json_lie_un_fichier_a_une_cle(self):
        self.storyboard([{"cle": "demo", "type": "broll", "requete": "l'agent edite un fichier"}])
        self.deposer("capture_ecran_2026_09_16.mp4")
        self.rushes([{"cle": "demo", "fichier": "capture_ecran_2026_09_16.mp4",
                      "decrit": "VS Code, Claude modifie un fichier", "duree_s": 12.4}])
        code, res = lancer(self.video)
        self.assertEqual(code, 0, res)
        entree = self.table()["demo"]
        self.assertEqual(entree["chemin"], "assets/capture_ecran_2026_09_16.mp4")
        self.assertEqual(entree["duree_s"], 12.4)

    def test_associer_prime_sur_la_convention_de_nom(self):
        self.storyboard([{"cle": "demo", "type": "broll"}])
        self.deposer("demo.mp4")
        self.deposer("le_bon.mp4")
        code, res = lancer(self.video, "--associer", "demo=le_bon.mp4")
        self.assertEqual(code, 0, res)
        self.assertEqual(self.table()["demo"]["chemin"], "assets/le_bon.mp4")

    def test_un_fichier_designe_mais_absent_est_une_erreur_explicite(self):
        self.storyboard([{"cle": "demo", "type": "broll", "obligatoire": True}])
        code, res = lancer(self.video, "--associer", "demo=jamais_depose.mp4")
        self.assertEqual(code, 3)
        self.assertIn("introuvable", res["non_resolus"][0]["motif"])


class TestTypeSuitLeFichier(BaseRessources):
    """`PlanBroll` choisit <OffthreadVideo> ou <Img> sur `type === 'broll'`.
    Un besoin de b-roll honore par une photo doit sortir en `image`, sinon le
    composant tente de lire un PNG comme une video et n'affiche rien."""

    def test_un_broll_rendu_par_une_image_devient_image(self):
        self.storyboard([{"cle": "plan", "type": "broll"}])
        self.deposer("plan.png")
        code, res = lancer(self.video)
        self.assertEqual(code, 0, res)
        self.assertEqual(self.table()["plan"]["type"], "image")
        self.assertTrue(any("plan fixe" in a for a in res["avertissements"]))

    def test_une_capture_garde_son_type(self):
        # PlanCapture n'affiche sa barre de navigateur que sur `capture`.
        self.storyboard([{"cle": "page", "type": "capture", "url": "https://exemple.test"}])
        self.deposer("page.png")
        code, res = lancer(self.video)
        self.assertEqual(code, 0, res)
        self.assertEqual(self.table()["page"]["type"], "capture")

    def test_duree_inconnue_est_signalee_pas_inventee(self):
        # Sans duree, PlanBroll ne reboucle pas : la fin du plan serait noire.
        self.storyboard([{"cle": "clip", "type": "broll"}])
        self.deposer("clip.mp4")
        _, res = lancer(self.video)
        if "duree_s" not in self.table()["clip"]:       # ffprobe absent
            self.assertTrue(any("Duree inconnue" in a for a in res["avertissements"]))


class TestNonResolus(BaseRessources):
    def test_un_besoin_sans_fichier_sort_avec_le_menu_des_rushes(self):
        """Associer « l'agent edite un fichier » a `demo.mp4` est un jugement.
        L'outil ne le rend pas : il presente ce qui est disponible."""
        self.storyboard([{"cle": "abstrait", "type": "broll",
                          "requete": "une metaphore de la memoire"}])
        self.deposer("autre_chose.mp4")
        code, res = lancer(self.video)
        self.assertEqual(code, 0)          # non bloquant : le besoin est facultatif
        self.assertEqual(res["non_resolus"][0]["cle"], "abstrait")
        self.assertIn("autre_chose.mp4", [r["fichier"] for r in res["rushes_disponibles"]])

    def test_un_besoin_obligatoire_non_resolu_bloque(self):
        self.storyboard([{"cle": "preuve", "type": "broll", "obligatoire": True}])
        code, res = lancer(self.video)
        self.assertEqual(code, 3)
        self.assertIn("obligatoire", res["message"])

    def test_le_fichier_est_ecrit_meme_quand_il_manque_des_besoins(self):
        """Une ressource manquante ne doit pas empecher les autres d'arriver a
        l'ecran : le composant orphelin affiche « Ressource manquante » en
        clair, ce qui se voit au CP3."""
        self.storyboard([{"cle": "ok", "type": "broll"}, {"cle": "absent", "type": "broll"}])
        self.deposer("ok.mp4")
        lancer(self.video)
        self.assertIn("ok", self.table())
        self.assertNotIn("absent", self.table())


class TestLogos(BaseRessources):
    def test_un_logo_deja_en_banque_ne_se_retelecharge_pas(self):
        banque = self.racine / "00_Profil" / "banque_assets" / "logos"
        banque.mkdir(parents=True)
        (banque / "github.svg").write_text("<svg/>", encoding="utf-8")
        self.storyboard([{"cle": "gh", "type": "logo", "requete": "GitHub"}])
        code, res = lancer(self.video)
        self.assertEqual(code, 0, res)
        self.assertEqual(self.table()["gh"]["licence"], "CC0-1.0")

    def test_un_logo_absent_hors_ligne_dit_quoi_lancer(self):
        self.storyboard([{"cle": "gh", "type": "logo", "requete": "GitHub"}])
        _, res = lancer(self.video)
        self.assertIn("recuperer_logo.py", res["non_resolus"][0]["motif"])


class TestBesoinsDupliques(BaseRessources):
    def test_une_meme_cle_dans_deux_scenes_est_normale(self):
        besoin = {"cle": "logo", "type": "broll"}
        self.storyboard([besoin], [besoin])
        self.deposer("logo.mp4")
        _, res = lancer(self.video)
        self.assertFalse([a for a in res["avertissements"] if "deux fois" in a])
        self.assertEqual(len(self.table()), 1)

    def test_deux_besoins_differents_sous_la_meme_cle_sont_signales(self):
        """Le second ecraserait le premier dans la table, et la scene
        afficherait autre chose que ce qu'elle a demande."""
        self.storyboard([{"cle": "x", "type": "broll", "requete": "A"}],
                        [{"cle": "x", "type": "broll", "requete": "B"}])
        self.deposer("x.mp4")
        _, res = lancer(self.video)
        self.assertTrue(any("deux fois" in a for a in res["avertissements"]))


class TestRoundTrip(BaseRessources):
    """Le seul test qui prouve que le tuyau est branche de bout en bout."""

    def test_la_sortie_est_lue_par_construire_props(self):
        self.storyboard([{"cle": "demo", "type": "broll"},
                         {"cle": "page", "type": "capture", "url": "https://exemple.test"}])
        self.deposer("demo.mp4")
        self.deposer("page.png")
        code, _ = lancer(self.video)
        self.assertEqual(code, 0)

        cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as faux_composants:
            os.chdir(faux_composants)
            try:
                ressources, avertissements = construire_props.preparer_ressources(
                    self.video / "05b_ressources.json")
            finally:
                os.chdir(cwd)

        self.assertEqual(avertissements, [])
        self.assertEqual(set(ressources), {"demo", "page"})
        # Le rendu ne sert que public/ : un chemin disque n'y arriverait pas.
        for entree in ressources.values():
            self.assertTrue(entree["src"].startswith("/public/assets/2026-09-16_v01/"))
        self.assertEqual(ressources["page"]["type"], "capture")


if __name__ == "__main__":
    unittest.main()
