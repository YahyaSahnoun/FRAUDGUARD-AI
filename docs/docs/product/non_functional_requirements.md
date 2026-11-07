# S10 — Exigences non fonctionnelles et mesures

**Statut :** spécification préliminaire ; aucune mesure réalisée  
**Référence :** Cahier des charges v1.0, sections 8–10 et 12 ; README, sections 3 et 8.

| Dimension | Exigence | Mesure / preuve future |
|---|---|---|
| Confidentialité | Données exclusivement synthétiques ou publiques autorisées ; logs sans secrets/PII | Revue des jeux, scan secrets, tests logs |
| Sécurité | Secrets hors Git ; SQL agent read-only, paramétré et limité ; décision exclusivement humaine | Tests d'interdiction d'écriture et de décisions automatiques |
| Intégrité | Événements versionnés, déduplication, IDs stables, quarantaine | Tests de contrats, replay et déduplication |
| Résilience | Checkpoints, reprise, traitement des retards, erreurs LLM maîtrisées | Tests restart, timeout, indisponibilité LLM |
| ML | Split temporel, prévention des fuites, métriques classe minoritaire, calibration examinée | PR-AUC, précision/rappel fraude, F1, matrice, calibration |
| Agent | Rapport structuré, citations vérifiables, abstention sans preuve | Validité de schéma, fidélité citations, tests négatifs |
| Observabilité | Logs corrélables et métriques de bout en bout | `trace_id`, `transaction_id`, `model_version`, `investigation_id` ; compteurs et latence |
| Reproductibilité | Configurations, seed, versions et commandes documentées | Replay des échantillons, tests CI et guide opérateur |
| Ressources/coût | Cible Linux locale ~20 Go RAM ; profils Compose ; options sans API payante | Mesure de RAM, configuration profils, mock LLM |

## Objectifs de service — méthode

**Aucun SLO numérique n'est fixé au stade S10 :** le cahier des charges demande de mesurer une baseline locale d'abord. Lors du premier test E2E instrumenté, mesurer au minimum :

- Débit : événements émis, acceptés, validés, scorés et mis en quarantaine par intervalle.
- Latence : p50 et p95 pour ingestion → alerte, et démarrage → rapport d'investigation.
- Fiabilité : duplications, pertes constatées, reprises, événements tardifs et délais de récupération.
- Ressources : mémoire et CPU des profils actifs.
- Modèle : PR-AUC et précision/rappel de la classe fraude, calibration et seuil choisi sur validation.
- Agent : taux de rapport JSON conforme, fidélité des citations, taux d'abstention justifiée et erreurs.

### Convention de définition future des SLO

Pour chaque indicateur : définir population/denominateur, fenêtre de mesure, environnement, méthode, seuil fondé sur baseline, et responsable. Éviter de confondre une cible à atteindre et une mesure obtenue.

## Risques prioritaires

1. RAM : n'activer qu'un sous-ensemble de services ; Spark local si nécessaire.
2. Fraudes synthétiques simplistes : scénarios diversifiés et limites de généralisation documentées.
3. Déséquilibre : évaluer la classe minoritaire plutôt que la seule accuracy.
4. LLM absent/incorrect : provider abstrait, mock, preuves citées, revue humaine.
5. Complexité : MVP local et CI avant les déploiements avancés.
