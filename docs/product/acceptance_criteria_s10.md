# Story S10 — Critères de réception et revue

**Epic / sprint :** Sprint 1 — Fondations, architecture et Kafka  
**Jira import ID :** 10  
**Story :** Définir périmètre MVP, personas et parcours alerte  
**Statut :** documents produits, revue et approbation utilisateur en attente.

## Objectifs spécifiques de S10

- [x] Décrire le problème, le bénéfice et le périmètre des sprints 1–6.
- [x] Distinguer explicitement le MVP des extensions sprints 7–8 et des exclusions.
- [x] Documenter analyste fraude, développeur Data/AI et superviseur technique.
- [x] Décrire le parcours nominal de transaction à décision humaine.
- [x] Identifier les principaux chemins d'erreur et statuts d'alerte.
- [x] Définir les dimensions de qualité et un plan de mesure des SLO.
- [x] Faire une première revue de cohérence documentaire avec le cahier des charges et le README fournis.
- [ ] Obtenir la revue/validation du responsable du projet.

## Preuves produites

- `docs/product/mvp_scope.md`
- `docs/product/user_journeys.md`
- `docs/product/non_functional_requirements.md`
- `docs/architecture/overview.md`
- Ce document d'acceptation.

## Limitations et décisions différées

- Les objectifs p95, throughput, RAM et qualité ML/agent sont des **mesures à établir**, pas des résultats.
- Les contrats détaillés, la configuration Docker, le simulateur et les tests d'exécution ne font pas partie de cette Story.
- L'état `needs_more_info` et le retry `failed` devront recevoir des transitions détaillées en sprints 4–5.
- Le diagramme est logique et sera affiné en S11 ; le chemin réel des features temps réel reste à concevoir.

## Revue demandée

Valider le périmètre, les trois personas, le parcours humain et la priorité MVP local. Après validation, passage à **S11 : définir contrats de données et architecture**.
