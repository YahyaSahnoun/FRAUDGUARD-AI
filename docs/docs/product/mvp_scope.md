# S10 — Périmètre MVP de FraudGuard AI

**Version :** 0.1 (proposition)  
**Statut :** spécification non implémentée  
**Référence :** Cahier des charges v1.0, sections 1–4, 8 et 12 ; README d'implémentation, sections 2–3 et 7.

## 1. Problème

Un score de fraude sans contexte, preuves ni historique de décision est insuffisant pour l'investigation. FraudGuard AI relie ingestion, contrôles qualité, scoring, investigations documentées et revue humaine, exclusivement sur des données synthétiques ou publiques autorisées.

## 2. Objectif produit

Démontrer localement un parcours reproductible : une transaction synthétique est ingérée et traitée, reçoit un score de risque, peut déclencher une alerte, est investiguée avec des preuves traçables, puis fait l'objet d'une décision humaine auditée.

## 3. Périmètre MVP (sprints 1–6)

| Capacité | Attente vérifiable | Sprint cible |
|---|---|---|
| Générateur | Transactions synthétiques reproductibles via seed, cadence et anomalies configurables | 1 |
| Kafka | Publication de messages versionnés, validation et quarantaine pour événements invalides | 1 |
| Lakehouse | Ingestion Spark, données Bronze/Silver/Gold, déduplication, reprise et backfill idempotents | 2 |
| Orchestration | Airflow pour traitements batch et backfills, pas pour chaque événement | 2 |
| ML | Baseline et XGBoost comparés ; split temporel, calibration évaluée, seuil justifié | 3 |
| Serving | API FastAPI validée, scores et alertes à identifiants stables | 3 |
| Agent | LangGraph, historique via outils read-only, RAG sur procédures fictives citées, rapport structuré | 4 |
| Revue humaine | Suspension/reprise du workflow, décision humaine obligatoire, traçabilité | 4–5 |
| Dashboard | Liste, filtres, détail des alertes, preuve, revue et export | 5 |
| Qualité/déploiement | Docker, tests, CI et démonstration E2E reproductible | 6 |

## 4. Hors périmètre

- Données bancaires privées réelles ; numéros de carte ou identifiants de personnes non autorisés.
- Blocage automatique de comptes, décisions réglementaires ou adjudication autonome par LLM.
- Haute disponibilité ou performances garanties de niveau bancaire.
- Kubernetes/Terraform obligatoires, surveillance avancée ou réentraînement automatique non approuvé au stade MVP.

## 5. Extensions (sprints 7–8)

DVC pour versionnement, Evidently pour dérive, réentraînement soumis à quality gate et approbation, évaluation de l'agent, Prometheus/Grafana, runbooks et démo documentée. Kubernetes/Terraform sont optionnels.

## 6. Hypothèses et contraintes

- Poste Linux local disposant d'environ 20 Go RAM ; Docker Compose par profils pour limiter les services simultanés.
- Préférence pour open source et interfaces LLM substituables (mock déterministe possible).
- Les labels de fraude ne sont jamais transmis comme features d'inférence ; pas de fuite temporelle.
- Aucune métrique de performance n'est présumée acquise ; les objectifs chiffrés seront fixés après mesures de référence.

## 7. Critère d'acceptation MVP global (cible de Sprint 6)

Depuis un environnement documenté, rejouer des transactions synthétiques et prouver : ingestion, transformation, scoring, création d'alerte, investigation sourcée, validation humaine, audit et tests automatisés. La démonstration doit couvrir duplication, erreur de schéma et reprise après incident. **Ce critère n'est pas validé à S10.**
