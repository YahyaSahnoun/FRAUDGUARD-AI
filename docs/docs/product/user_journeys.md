# S10 — Personas et parcours utilisateur

**Statut :** parcours proposés, non implémentés  
**Référence :** Cahier des charges v1.0, sections 3–4, 7 et 9 ; README, sections 5–6.

## Personas

### Analyste fraude — utilisateur principal

**Mission :** consulter les alertes, évaluer les éléments de preuve et consigner une décision.  
**Besoins :** historique transactionnel contextualisé, rapport explicable et sources consultables, statut fiable, trace de ses actions.  
**Limite :** l'agent recommande mais ne décide jamais à sa place.

### Data / AI Engineer — opérateur technique

**Mission :** gérer simulateur, ingestion, qualité, transformation, pipelines ML et services d'inférence.  
**Besoins :** données reproductibles, schémas versionnés, mesures, logs, idempotence, tests, procédures de reprise.

### Superviseur technique — responsable qualité opérationnelle

**Mission :** inspecter la santé du pipeline, la qualité des modèles et des agents, valider les promotions de modèle.  
**Besoins :** métriques, résultats d'évaluation, traçabilité et procédure de rollback.

## Parcours nominal — de la transaction à la revue humaine

1. Le simulateur génère un événement synthétique identifiable de façon stable.
2. Kafka reçoit `transactions.raw` ; validation, déduplication et transformations produisent Bronze/Silver/Gold.
3. Le service de scoring consomme les features disponibles au temps de l'événement et calcule un `risk_score` associé à une version de modèle.
4. Si le score franchit le seuil configuré, une alerte identifiée de façon stable est produite sur `fraud.alerts` et persistée.
5. L'analyste ouvre l'alerte et lance une investigation : `new → investigating`.
6. LangGraph recueille l'historique via des outils read-only, recherche des procédures fictives et construit un rapport structuré, avec références explicites et limites.
7. Le workflow attend l'analyste : `investigating → pending_review`.
8. L'analyste décide `confirmed_fraud`, `false_positive` ou `needs_more_info`. L'application consigne auteur, horodatage et action.
9. Le rapport et l'audit sont consultables/exportables. Aucune décision n'est prise automatiquement par le LLM.

## Scénarios alternatifs et cas limites

| Situation | Comportement attendu |
|---|---|
| Message invalide ou schéma incompatible | Quarantaine (`transactions.dlq`), raison diagnostic, pas de score aveugle |
| Relecture ou duplication d'événement | Absence de nouvelle alerte identique pour le même événement et la même version de score |
| Événement tardif | Traitement selon règle temporelle documentée, sans utilisation d'information future |
| Historique ou preuve absent(e) | Rapport déclarant l'information indisponible ; aucune preuve inventée |
| LLM indisponible | Erreur contrôlée/retry borné ou mode dégradé, sans blocage du flux de scoring |
| Échec de l'investigation | État `failed` et reprise contrôlée ; pas de décision automatique |
| Analyste demande des informations supplémentaires | État `needs_more_info`, suivi explicite avant toute reprise/revue ultérieure |

## États proposés

`new → investigating → pending_review → {confirmed_fraud, false_positive, needs_more_info}`.

Un état `failed` et un mécanisme de retry contrôlé sont prévus. Les règles exactes de reprise depuis `needs_more_info` ou `failed` et la gestion des tentatives simultanées seront précisées dans les stories des sprints 4–5.

## Exemple fictif

Une transaction de montant atypique déclenche une alerte après scoring. Le graphe obtient les transactions précédentes et cite une procédure fictive de revue des montants anormaux. Le rapport signale qu'une anomalie statistique ne prouve pas une fraude ; l'analyste choisit `needs_more_info`. Ce scénario est illustratif, **pas** une performance ou un résultat système observé.
