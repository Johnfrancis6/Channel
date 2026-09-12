# Catalogue visuel des composants

*Genere par `outils/generer_apercus.py` — ne pas editer a la main.*

A quoi ressemble chaque composant, variante par variante. Le Designer
(A6) choisit ici **en regardant**, pas en devinant a partir d'un nom.
Les images passent par la composition de rendu reelle : c'est ce que la
video montrera, tokens de charte compris.

Images prises a la frame 30 (~1.0 s), donc apres
l'animation d'entree.

Pour regenerer apres avoir cree ou modifie un composant :

```bash
python3 outils/generer_apercus.py
```

## ConceptCutaway

### llm-single-turn

![ConceptCutaway — llm-single-turn](ConceptCutaway-llm-single-turn.png)

- Parametres : `scene` = `llm_single_turn`, `label` = `STEP 1 — LLM`

### workflow-tools

![ConceptCutaway — workflow-tools](ConceptCutaway-workflow-tools.png)

- Parametres : `scene` = `workflow_tools`, `label` = `STEP 2 — AI WORKFLOW`

### workflow-fixed-path

![ConceptCutaway — workflow-fixed-path](ConceptCutaway-workflow-fixed-path.png)

- Parametres : `scene` = `workflow_fixed_path`, `label` = `FIXED PATH`

### agent-loop

![ConceptCutaway — agent-loop](ConceptCutaway-agent-loop.png)

- Parametres : `scene` = `agent_loop`, `label` = `STEP 3 — AI AGENT`

### github-demo

![ConceptCutaway — github-demo](ConceptCutaway-github-demo.png)

- Parametres : `scene` = `github_demo`, `label` = `CLAUDE + GITHUB`

### context7-demo

![ConceptCutaway — context7-demo](ConceptCutaway-context7-demo.png)

- Parametres : `scene` = `context7_demo`, `label` = `CONTEXT7 MCP`, `compteur` = `1/5`

### playwright-demo

![ConceptCutaway — playwright-demo](ConceptCutaway-playwright-demo.png)

- Parametres : `scene` = `playwright_demo`, `label` = `PLAYWRIGHT MCP`, `compteur` = `2/5`

### firecrawl-demo

![ConceptCutaway — firecrawl-demo](ConceptCutaway-firecrawl-demo.png)

- Parametres : `scene` = `firecrawl_demo`, `label` = `FIRECRAWL MCP`, `compteur` = `3/5`

### higgsfield-demo

![ConceptCutaway — higgsfield-demo](ConceptCutaway-higgsfield-demo.png)

- Parametres : `scene` = `higgsfield_demo`, `label` = `HIGGSFIELD MCP`, `compteur` = `4/5`

### github-mcp-demo

![ConceptCutaway — github-mcp-demo](ConceptCutaway-github-mcp-demo.png)

- Parametres : `scene` = `github_mcp_demo`, `label` = `GITHUB MCP`, `compteur` = `5/5`

## PlanBroll

### photo-accroche

![PlanBroll — photo-accroche](PlanBroll-photo-accroche.png)

- Parametres : `broll` = `fond`, `accroche` = `3 minutes`

## PlanCapture

### capture-seule

![PlanCapture — capture-seule](PlanCapture-capture-seule.png)

- Parametres : `capture` = `page`, `label` = `LA VRAIE PAGE`

### capture-logo-compteur

![PlanCapture — capture-logo-compteur](PlanCapture-capture-logo-compteur.png)

- Parametres : `capture` = `page`, `logo` = `marque`, `label` = `CONTEXT7 MCP`, `compteur` = `1/5`

### ressource-manquante

![PlanCapture — ressource-manquante](PlanCapture-ressource-manquante.png)

- Parametres : `capture` = `page_absente`, `label` = `REPLI VISIBLE`

## PlanLogos

### trois-logos-relies

![PlanLogos — trois-logos-relies](PlanLogos-trois-logos-relies.png)

- Parametres : `label` = `CE QUI SE BRANCHE`, `logos` = `[{'cle': 'a', 'libelle': 'CLAUDE'}, {'cle': 'b', 'libelle': 'MCP'}, {'cle': 'c', 'libelle': 'GITHUB'}]`

## StickmanTalk

### intro

![StickmanTalk — intro](StickmanTalk-intro.png)

- Parametres : `pose` = `intro`

### lean-in

![StickmanTalk — lean-in](StickmanTalk-lean-in.png)

- Parametres : `pose` = `lean_in`, `label` = `REAL EXAMPLE`

### outro

![StickmanTalk — outro](StickmanTalk-outro.png)

- Parametres : `pose` = `outro`

## TitleCard

### titre-seul

![TitleCard — titre-seul](TitleCard-titre-seul.png)

- Parametres : `texte` = `Most of them are not agents.`

### titre-et-sous-titre

![TitleCard — titre-et-sous-titre](TitleCard-titre-et-sous-titre.png)

- Parametres : `texte` = `What changed this week`, `sousTitre` = `AI news, decoded`
