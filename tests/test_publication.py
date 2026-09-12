"""
Teste skills/short-publier/scripts/publier.py : fermeture du cycle de vie
d'une video (E7, §11) et passage du registre a publiee/programmee (§5.3).

Avant ce skill, aucun code n'ecrivait jamais `publiee`, `programmee` ni
`publication.date_effective` — le pipeline ne pouvait pas terminer une
video autrement qu'en editant state.json a la main.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, "skills", "short-publier", "scripts", "publier.py")
GABARIT = os.path.join(REPO_ROOT, "skills", "new-short", "assets", "state_template.json")


class TestPublier(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="chaine_yt_publier_")
        os.makedirs(os.path.join(self.root, "00_Profil"))
        self.video_id = "2026-09-11_v01"
        self.dossier = os.path.join(self.root, "videos", self.video_id)
        os.makedirs(self.dossier)
        with open(GABARIT, encoding="utf-8-sig") as f:
            state = json.load(f)
        state["video_id"] = self.video_id
        state["statut_global"] = "prete"
        state["etapes"]["CP3"]["statut"] = "valide"
        state["etapes"]["E6_montage"]["statut"] = "termine"
        self.ecrire(state)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def ecrire(self, state):
        with open(os.path.join(self.dossier, "state.json"), "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def lire(self):
        with open(os.path.join(self.dossier, "state.json"), encoding="utf-8-sig") as f:
            return json.load(f)

    def run_script(self, *args):
        proc = subprocess.run(
            [sys.executable, SCRIPT, "--root", self.root, "--video", self.video_id, *args],
            capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout)

    def test_publication_ferme_le_cycle_de_vie(self):
        code, out = self.run_script("--url", "https://www.youtube.com/shorts/abc", "--date", "2026-09-14")
        self.assertEqual(code, 0, out)
        state = self.lire()
        self.assertEqual(state["statut_global"], "publiee")
        self.assertEqual(state["publication"]["url"], "https://www.youtube.com/shorts/abc")
        self.assertEqual(state["publication"]["date_effective"], "2026-09-14T00:00:00Z")
        self.assertEqual(state["etapes"]["E7_publication"]["statut"], "termine")
        self.assertEqual(state["etape_actuelle"], "termine")
        self.assertEqual(state["historique"][-1]["evenement"], "publiee")

    def test_cp3_non_valide_bloque_la_publication(self):
        state = self.lire()
        state["etapes"]["CP3"]["statut"] = "attente_validation"
        self.ecrire(state)
        code, out = self.run_script("--url", "https://youtu.be/x")
        self.assertEqual(code, 7)
        self.assertEqual(self.lire()["statut_global"], "prete")

    def test_programmee_laisse_l_etape_ouverte(self):
        # Sinon la video disparait du tableau de bord avant d'etre en ligne.
        code, out = self.run_script("--statut", "programmee", "--date", "2026-09-20")
        self.assertEqual(code, 0, out)
        state = self.lire()
        self.assertEqual(state["statut_global"], "programmee")
        self.assertEqual(state["etapes"]["E7_publication"]["statut"], "attente_franco")
        self.assertEqual(state["publication"]["date_prevue"], "2026-09-20T00:00:00Z")
        self.assertIsNone(state["publication"]["date_effective"])

    def test_url_obligatoire_pour_publiee(self):
        code, out = self.run_script()
        self.assertEqual(code, 4)
        self.assertIn("--url", out["message"])

    def test_deuxieme_passage_refuse_sans_force(self):
        self.run_script("--url", "https://youtu.be/x")
        code, out = self.run_script("--url", "https://youtu.be/y")
        self.assertEqual(code, 8)
        self.assertEqual(self.lire()["publication"]["url"], "https://youtu.be/x")

    def test_force_corrige_une_url(self):
        self.run_script("--url", "https://youtu.be/x")
        code, out = self.run_script("--url", "https://youtu.be/y", "--force")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.lire()["publication"]["url"], "https://youtu.be/y")

    def test_video_inconnue(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT, "--root", self.root, "--video", "2026-01-01_v09",
             "--url", "https://youtu.be/x"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 6)

    def test_date_illisible(self):
        code, out = self.run_script("--url", "https://youtu.be/x", "--date", "14/09/2026")
        self.assertEqual(code, 4)

    def test_programmer_puis_publier_sans_force(self):
        # C'est le trajet nominal decrit par le skill. Il exigeait `--force`,
        # le drapeau reserve aux corrections : la protection contre
        # l'ecrasement bloquait l'etape suivante du cycle normal.
        self.run_script("--statut", "programmee", "--date", "2026-09-20")
        code, out = self.run_script("--url", "https://youtu.be/x", "--date", "2026-09-20")

        self.assertEqual(code, 0, out)
        state = self.lire()
        self.assertEqual(state["statut_global"], "publiee")
        self.assertEqual(state["etapes"]["E7_publication"]["statut"], "termine")

    def test_url_fantaisiste_refusee(self):
        # H1 s'en sert pour rapprocher les performances YouTube des videos
        # produites : une valeur qui n'est pas une adresse se voit tard.
        code, out = self.run_script("--url", "youtube/abc")
        self.assertEqual(code, 4)
        self.assertEqual(self.lire()["statut_global"], "prete")

    def test_abandon_ferme_le_cycle_sans_cp3(self):
        # `abandonnee` etait lu par quatre endroits (tampon de short-state,
        # liberation du sujet_id, compteur du tableau de bord) et ecrit par
        # personne : une idee laissee tomber restait a vie dans le tampon.
        state = self.lire()
        state["etapes"]["CP3"]["statut"] = "a_venir"
        state["statut_global"] = "en_production"
        self.ecrire(state)

        code, out = self.run_script("--statut", "abandonnee", "--motif", "sujet deja traite ailleurs")

        self.assertEqual(code, 0, out)
        state = self.lire()
        self.assertEqual(state["statut_global"], "abandonnee")
        self.assertEqual(state["etape_actuelle"], "termine")
        self.assertEqual(state["historique"][-1]["evenement"], "abandonnee")
        self.assertEqual(state["historique"][-1]["message"], "sujet deja traite ailleurs")
        # Rien n'a ete publie : pas de date inventee.
        self.assertIsNone(state["publication"]["date_effective"])
        self.assertIsNone(state["publication"]["date_prevue"])

    def test_abandon_sans_motif_refuse(self):
        code, out = self.run_script("--statut", "abandonnee")
        self.assertEqual(code, 4)
        self.assertIn("motif", out["message"])
        self.assertEqual(self.lire()["statut_global"], "prete")

    def test_un_cycle_clos_est_protege(self):
        self.run_script("--statut", "abandonnee", "--motif", "trop proche du sujet precedent")
        code, out = self.run_script("--url", "https://youtu.be/x")
        self.assertEqual(code, 8)
        self.assertEqual(self.lire()["statut_global"], "abandonnee")

    def test_etat_reste_valide_au_regard_du_schema(self):
        self.run_script("--url", "https://www.youtube.com/shorts/abc")
        state = self.lire()
        with open(os.path.join(REPO_ROOT, "schemas", "state_schema.json"), encoding="utf-8-sig") as f:
            schema = json.load(f)
        self.assertIn(state["statut_global"], schema["properties"]["statut_global"]["enum"])
        etape = schema["definitions"]["etape_agent"]["properties"]["statut"]["enum"]
        self.assertIn(state["etapes"]["E7_publication"]["statut"], etape)


if __name__ == "__main__":
    unittest.main()
