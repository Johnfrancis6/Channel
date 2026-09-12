"""
Teste la chaine d'assets (E5b) : le jugement des captures
(outils/capturer_web.py) et la resolution des ressources
(agents/short-monteur/scripts/construire_props.py).

Les trois premiers tests de `TestJugerCapture` figent trois echecs REELS,
survenus dans cet ordre le 12/09/2026. Chacun avait produit un PNG
parfaitement valide, et chacun serait entre dans une video comme un plan
normal. Ils sont ici parce qu'un controle qui a deja menti trois fois ne se
relit pas a l'oeil : il se teste.
"""
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "outils"))
sys.path.insert(0, str(REPO_ROOT / "agents" / "short-monteur" / "scripts"))

import capturer_web  # noqa: E402
import construire_props  # noqa: E402


class TestJugerCapture(unittest.TestCase):
    def test_interstitielle_tls_refusee(self):
        """Echec 1 : le proxy reforge les certificats, Chromium affiche son
        interstitielle, le PNG est valide."""
        dom = "<html><head><title>Privacy error</title></head><body>" \
              "<h1>Your connection is not private</h1></body></html>"
        _, suspect, motif = capturer_web.juger(dom)
        self.assertTrue(suspect)
        self.assertIn("your connection is not private", motif)

    def test_corps_json_refuse(self):
        """Echec 2 : un proxy renvoie un JSON d'erreur. Ni page d'erreur
        Chrome, ni marqueur connu — seule la forme du corps trahit."""
        dom = '<html><head><title>x</title></head><body><pre>' \
              '{"message":"access is not enabled","documentation_url":"http://x"}' \
              '</pre></body></html>'
        _, suspect, motif = capturer_web.juger(dom)
        self.assertTrue(suspect)
        self.assertIn("JSON", motif)

    def test_marqueur_tardif_dans_un_gros_dom(self):
        """Echec 3, le plus instructif : la page d'erreur reseau de Chromium
        embarque une grosse ressource inline AVANT son texte visible. Une
        premiere version ne scannait que les 40 000 premiers caracteres — le
        controle etait ecrit, correct, et desactive en silence."""
        bourrage = "<script>/*" + ("x" * 150000) + "*/</script>"
        dom = (f"<html><head><title>example.com</title></head><body>{bourrage}"
               "<span>This site can’t be reached</span></body></html>")
        self.assertGreater(dom.index("reached"), 140000)
        _, suspect, _ = capturer_web.juger(dom)
        self.assertTrue(suspect)

    def test_apostrophe_courbe_reconnue(self):
        """Chromium ecrit « can’t » avec une apostrophe typographique. La
        comparer a « can't » sans normaliser ne matche jamais."""
        droite = capturer_web.normaliser("This site can't be reached")
        courbe = capturer_web.normaliser("This site can’t be reached")
        self.assertEqual(droite, courbe)

    def test_code_erreur_reseau_reconnu_generiquement(self):
        dom = "<html><head><title>x</title></head><body>ERR_TUNNEL_CONNECTION_FAILED</body></html>"
        _, suspect, motif = capturer_web.juger(dom)
        self.assertTrue(suspect)
        self.assertIn("ERR_TUNNEL_CONNECTION_FAILED", motif)

    def test_page_sans_titre_refusee(self):
        _, suspect, motif = capturer_web.juger("<html><body><p>du contenu</p></body></html>")
        self.assertTrue(suspect)
        self.assertIn("<title>", motif)

    def test_page_vide_refusee(self):
        _, suspect, motif = capturer_web.juger("   ")
        self.assertTrue(suspect)
        self.assertEqual(motif, "page vide")

    def test_vraie_page_acceptee(self):
        """Le pendant indispensable : un controle qui refuse tout ne vaut pas
        mieux qu'un controle qui accepte tout."""
        dom = ("<html><head><title>exemple / depot</title></head><body>"
               "<h1>exemple / depot</h1><p>Contenu normal d'une page.</p></body></html>")
        titre, suspect, motif = capturer_web.juger(dom)
        self.assertFalse(suspect, motif)
        self.assertEqual(titre, "exemple / depot")


class TestPreparerRessources(unittest.TestCase):
    def _ecrire(self, dossier, table):
        chemin = Path(dossier) / "05b_ressources.json"
        chemin.write_text(json.dumps({"video_id": "2026-01-01_v01", "ressources": table}),
                          encoding="utf-8")
        return chemin

    def test_fichier_absent_nempeche_pas_le_montage(self):
        """Une video d'avant E5b n'a pas de fichier de ressources : le montage
        doit continuer, avec un avertissement."""
        ressources, avertissements = construire_props.preparer_ressources("/inexistant/x.json")
        self.assertEqual(ressources, {})
        self.assertTrue(avertissements)

    def test_ressource_introuvable_est_omise_et_signalee(self):
        """Omise plutot que fausse : le composant affichera « Ressource
        manquante » en clair, ce qui se voit au CP3. Une URL qui pointe dans
        le vide produirait un cadre noir que personne ne remarque."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            chemin = self._ecrire(d, {"page": {"chemin": "assets/absent.png", "type": "capture"}})
            ressources, avertissements = construire_props.preparer_ressources(chemin)
        self.assertNotIn("page", ressources)
        self.assertTrue(any("page" in a for a in avertissements))

    def test_ressource_sans_chemin_est_signalee(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            chemin = self._ecrire(d, {"page": {"type": "capture"}})
            ressources, avertissements = construire_props.preparer_ressources(chemin)
        self.assertEqual(ressources, {})
        self.assertTrue(any("chemin" in a for a in avertissements))

    def test_ressource_presente_est_copiee_et_servie_sous_public(self):
        """Le serveur de rendu de Remotion ne sert que public/ : un chemin
        absolu ou une URI file:// echouent tous les deux."""
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "assets").mkdir()
            (Path(d) / "assets" / "page.png").write_bytes(b"\x89PNG fictif")
            chemin = self._ecrire(d, {"page": {"chemin": "assets/page.png", "type": "capture",
                                               "largeur_px": 1200, "licence": "capture-ecran",
                                               "cout_interne": "a ne pas propager"}})
            cwd = os.getcwd()
            with tempfile.TemporaryDirectory() as faux_composants:
                os.chdir(faux_composants)
                try:
                    ressources, avertissements = construire_props.preparer_ressources(chemin)
                    self.assertEqual(avertissements, [])
                    self.assertEqual(ressources["page"]["src"],
                                     "/public/assets/2026-01-01_v01/page.png")
                    self.assertTrue((Path(faux_composants) / "public" / "assets" /
                                     "2026-01-01_v01" / "page.png").is_file())
                    self.assertEqual(ressources["page"]["largeur_px"], 1200)
                    # Les cles internes a A8 n'ont rien a faire dans le bundle.
                    self.assertNotIn("cout_interne", ressources["page"])
                finally:
                    os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
