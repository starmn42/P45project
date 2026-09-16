# P45 CROWD TOPOLOGY / JOHNSON-SPACE LOCAL AUTOCORRELATION

## Registration boundary

- Research domain: `CROWD / PRIZE_SHARE`, completely separate from the DRAW engine
- Direction status: `REGISTERED_IDEA / NEEDS_EVIDENCE`
- Novelty status: `PROMISING_NOVEL_DIRECTION / NOVELTY_NOT_CONFIRMED`
- Experiment created: `NO`
- Protocol created or locked: `NO`
- Outcome calculation executed: `NO`
- Official-engine effect: `NONE`

This note records a research direction only. It does not assert novelty, support, predictive value, or promotion eligibility.

## Prior research boundary

1. Turner (2010), *Lottery Ticket Preferences as Indicated by the Variation in the Number of Winners*, Journal of Gambling Studies, DOI `10.1007/s10899-009-9171-7`.
   - Uses sales and prize-winner counts to study ticket preferences.
2. Baker & McHale (2011), *Investigating the Behavioural Characteristics of Lottery Players by Using a Combination Preference Model for Conscious Selection*, JRSS Series A, DOI `10.1111/j.1467-985X.2011.00693.x`.
   - Models clusters of similar consciously selected combinations and prize-tier winner correlations.
   - Therefore the generic claim that similar lottery combinations cluster is not novel.
3. Jeong & Jang (2025), *What is the secret behind lotto numbers? - Reflections on the fairness of the lotto and winning numbers*, Korean Journal of Applied Statistics 38(1), 89–101, DOI `10.5351/KJAS.2025.38.1.089`.
   - Studies non-random player number choice and unusually many first-prize winners in Korean Lotto 6/45.
4. Choi (2013), *Exploratory Analysis of Korea Lotto Lottery Using Social Network Analysis*.
   - Applies network analysis to Korean winning numbers; this differs from latent buyer-choice topology.

The three DOI records above were cross-checked against Crossref metadata on 2026-08-23. The Choi citation is retained as a literature-audit lead and requires broader bibliographic/full-text confirmation before any novelty conclusion.

## Generic claims rejected

The following are not accepted as novel claims:

- people choose clusters of similar combinations;
- winner counts can be used to infer number preferences;
- network methods can be applied to lottery data.

## Refined direction

### Combination space

- Vertices: all `C(45,6) = 8,145,060` exact tickets.
- Geometry: Johnson graph `J(45,6)`.
- Adjacency: two tickets are adjacent when they share exactly five numbers.
- Latent ticket-choice probability at vertex `v`: `q(v)`.

### Prize-tier radial-shell interpretation

- First prize `K1`: winning combination itself, Johnson distance 0.
- Second plus third prizes `K2 + K3`: the complete Johnson distance-1 shell.
  - 2nd prize: 6 neighbors containing the bonus.
  - 3rd prize: the other 228 neighbors.
  - Full shell: 234 neighbors.
- Fourth prize: four main matches, Johnson distance 2 shell.
- Fifth prize: three main matches, Johnson distance 3 shell.

Prize-tier winner counts are treated only as candidate radial-shell measurements of latent crowd-choice density. They are not DRAW occurrence predictors.

## First low-DF candidate hypothesis — not a protocol

- H1 candidate: `q(v)` has positive local autocorrelation at Johnson distance 1.
- Plain-language question: Are the true combination-space neighbors of a popular ticket—tickets sharing five numbers—also more popular on average?
- Opposite hypothesis: distance-1 local autocorrelation is less than or equal to zero.
- Tentative center proxy: sales-normalized `K1`.
- Tentative distance-1 shell proxy: sales-normalized `(K2 + K3)`.
- Required correction topics: multinomial sampling covariance and sales-size effects.

No proxy, coefficient, p-value, direction, graph, or outcome was calculated in this work.

## Novelty assessment

The direction overlaps Baker & McHale's combination clustering. In the sources reviewed so far, the exact combination of true `J(45,6)` geometry, prize-tier shell operators, local graph-autocorrelation inference, and locked/prospective validation was not confirmed. This absence is not proof of novelty. “World first” and equivalent claims are forbidden until a broader full-text literature audit is complete.

## Roadmap

1. Continue Prospective-001 unchanged.
2. Keep this as an independent CROWD/PRIZE_SHARE research axis.
3. Before creating an experiment, review identifiability, exact multinomial null, sales normalization, K1 versus K2+K3 covariance correction, minimum sample and power, multiple-testing policy, future-data blocking, and historical train/holdout/walkforward versus prospective validation.
4. Create and lock a separate experiment only after that design passes and explicit approval is given.
5. Never combine its results or scores with Prospective-001 or the DRAW engine.
