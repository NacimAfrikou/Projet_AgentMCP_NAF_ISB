"""
Module d'analyse comparative pour les tests A/B de posts réseaux sociaux.

Fournit des fonctions Python pures (sans HTML/CSS) pour :
- Afficher chaque test (A, B, …) comme un post complet prêt-à-publier
- Comparer les deux propositions côte à côte
- Identifier les forces et faiblesses de chaque version
- Produire une recommandation argumentée
"""

from typing import Any, Dict, List
from collections import Counter


# ──────────────────────────────────────────────────────────────────────
# Constantes
# ──────────────────────────────────────────────────────────────────────

SCORE_TO_NUM = {
    "excellent": 95,
    "élevé": 90,
    "bon": 70,
    "moyen": 60,
    "faible": 30,
}

RELEVANCE_TO_NUM = {
    "haute": 3,
    "moyenne": 2,
    "basse": 1,
}


# ──────────────────────────────────────────────────────────────────────
# Extraction de métriques
# ──────────────────────────────────────────────────────────────────────

def extract_variation_metrics(variation) -> Dict[str, Any]:
    """
    Extrait un dictionnaire de métriques à partir d'une ABVariation.
    """
    post = variation.post
    hashtags = post.hashtags

    relevance_counts = Counter(h.relevance for h in hashtags)
    hashtag_score = sum(RELEVANCE_TO_NUM.get(h.relevance, 1) for h in hashtags)

    texte = post.texte
    nb_mots = len(texte.split())

    return {
        "version": variation.version,
        "strategie": variation.strategie,
        "score_estime": variation.score_estime,
        "score_numerique": SCORE_TO_NUM.get(
            variation.score_estime.lower().strip(), 50
        ),
        "longueur_caracteres": post.longueur_caracteres,
        "nb_mots": nb_mots,
        "nb_lignes": texte.count("\n") + 1,
        "nb_questions": texte.count("?"),
        "nb_exclamations": texte.count("!"),
        "nb_emojis": len(post.emojis_utilises),
        "emojis": post.emojis_utilises,
        "accroche": post.accroche,
        "call_to_action": post.call_to_action,
        "nb_hashtags": len(hashtags),
        "hashtags_haute": relevance_counts.get("haute", 0),
        "hashtags_moyenne": relevance_counts.get("moyenne", 0),
        "hashtags_basse": relevance_counts.get("basse", 0),
        "hashtag_score": hashtag_score,
        "hashtags_list": ["#" + h.tag for h in hashtags],
        "image_style": post.image_prompt.style,
        "image_couleurs": post.image_prompt.couleurs_dominantes,
        "image_prompt_en": post.image_prompt.prompt_en,
        "meilleur_creneau": (
            f"{post.timing[0].jour} à {post.timing[0].heure}"
            if post.timing
            else "N/A"
        ),
        "timing_raison": (
            post.timing[0].raison if post.timing else ""
        ),
    }


def extract_all_metrics(ab_output) -> List[Dict[str, Any]]:
    """Extrait les métriques de toutes les variations."""
    return [extract_variation_metrics(var) for var in ab_output.variations]


# ──────────────────────────────────────────────────────────────────────
# Analyse comparative
# ──────────────────────────────────────────────────────────────────────

def compare_variations(ab_output) -> Dict[str, Any]:
    """
    Compare les variations A/B et produit une analyse structurée.

    Returns:
        Dictionnaire contenant : metrics, classement, differences,
        hashtags_communs, hashtags_uniques, recommandation, etc.
    """
    metrics = extract_all_metrics(ab_output)
    classement = sorted(
        metrics, key=lambda m: m["score_numerique"], reverse=True
    )

    criteres_num = [
        ("score_numerique", "Score d'engagement", True),
        ("longueur_caracteres", "Longueur du texte", None),
        ("nb_mots", "Nombre de mots", None),
        ("nb_hashtags", "Nombre de hashtags", True),
        ("hashtag_score", "Qualité des hashtags", True),
        ("nb_emojis", "Emojis", None),
        ("nb_questions", "Questions posées", True),
    ]

    differences = []
    for key, label, higher_is_better in criteres_num:
        values = {m["version"]: m[key] for m in metrics}
        best_v = max(values, key=values.get)
        worst_v = min(values, key=values.get)
        if values[best_v] != values[worst_v]:
            differences.append({
                "critere": label,
                "valeurs": values,
                "ecart": values[best_v] - values[worst_v],
                "leader": best_v if higher_is_better else None,
            })

    hashtag_sets = {m["version"]: set(m["hashtags_list"]) for m in metrics}
    if len(hashtag_sets) >= 2:
        communs = set.intersection(*hashtag_sets.values())
        uniques = {v: tags - communs for v, tags in hashtag_sets.items()}
    else:
        communs = set()
        uniques = {}

    return {
        "metrics": metrics,
        "classement": classement,
        "differences": differences,
        "hashtags_communs": communs,
        "hashtags_uniques": uniques,
        "recommandation": ab_output.recommandation,
        "criteres_evaluation": ab_output.criteres_evaluation,
        "plateforme": ab_output.plateforme,
        "sujet": ab_output.sujet,
    }


# ──────────────────────────────────────────────────────────────────────
# Affichage — Test A / Test B (posts complets)
# ──────────────────────────────────────────────────────────────────────

def print_test(ab_output, version: str) -> None:
    """
    Affiche UN test (A ou B) comme un post complet prêt-à-publier.

    Args:
        ab_output: Instance ABTestOutput
        version: Lettre de la version à afficher ("A", "B", "C"…)
    """
    var = None
    for v in ab_output.variations:
        if v.version.upper() == version.upper():
            var = v
            break
    if var is None:
        versions = ", ".join(v.version for v in ab_output.variations)
        print(f"❌ Version '{version}' introuvable. Versions disponibles : {versions}")
        return

    post = var.post
    w = 65

    print(f"\n{'╔' + '═' * (w - 2) + '╗'}")
    print(f"║{'TEST ' + var.version:^{w - 2}}║")
    print(f"║{ab_output.plateforme.upper():^{w - 2}}║")
    print(f"{'╚' + '═' * (w - 2) + '╝'}")

    print(f"\n  Stratégie : {var.strategie}")
    print(f"  Score estimé : {var.score_estime}")

    # --- Le post tel qu'il serait publié ---
    print(f"\n{'┌' + '─' * (w - 2) + '┐'}")
    print(f"│{'POST TEL QU IL SERAIT PUBLIÉ':^{w - 2}}│")
    print(f"{'├' + '─' * (w - 2) + '┤'}")

    for line in post.texte.split("\n"):
        # Découper les lignes trop longues
        while len(line) > w - 4:
            print(f"│ {line[:w - 4]:<{w - 3}}│")
            line = line[w - 4:]
        print(f"│ {line:<{w - 3}}│")

    print(f"│{' ' * (w - 2)}│")
    hashtags_str = " ".join("#" + h.tag for h in post.hashtags)
    # Afficher les hashtags (peut être long)
    while len(hashtags_str) > w - 4:
        print(f"│ {hashtags_str[:w - 4]:<{w - 3}}│")
        hashtags_str = hashtags_str[w - 4:]
    print(f"│ {hashtags_str:<{w - 3}}│")
    print(f"{'└' + '─' * (w - 2) + '┘'}")

    # --- Détails ---
    print(f"\n  🎯 Accroche : \"{post.accroche}\"")
    print(f"  📢 CTA      : {post.call_to_action}")
    print(f"  📝 Longueur  : {post.longueur_caracteres} caractères, {len(post.texte.split())} mots")
    print(f"  😀 Emojis    : {' '.join(post.emojis_utilises[:8]) if post.emojis_utilises else '(aucun)'}")

    print(f"\n  🏷️  Hashtags ({len(post.hashtags)}) :")
    for h in post.hashtags:
        print(f"      #{h.tag:<25} pertinence: {h.relevance}")

    if post.timing:
        print(f"\n  ⏰ Créneaux recommandés :")
        for t in post.timing[:3]:
            print(f"      {t.jour} à {t.heure} — {t.raison} [{t.score_engagement}]")

    print(f"\n  🎨 Image DALL-E 3 :")
    print(f"      Style    : {post.image_prompt.style}")
    print(f"      Couleurs : {', '.join(post.image_prompt.couleurs_dominantes)}")
    print(f"      Prompt   : {post.image_prompt.prompt_en[:120]}...")
    print()


def print_test_a(ab_output) -> None:
    """Affiche le TEST A (première variation) comme post complet."""
    if ab_output.variations:
        print_test(ab_output, ab_output.variations[0].version)


def print_test_b(ab_output) -> None:
    """Affiche le TEST B (deuxième variation) comme post complet."""
    if len(ab_output.variations) >= 2:
        print_test(ab_output, ab_output.variations[1].version)


def print_all_tests(ab_output) -> None:
    """Affiche tous les tests (A, B, C…) l'un après l'autre."""
    print(f"\n{'═' * 65}")
    print(f"  🔬 TEST A/B — {ab_output.plateforme.upper()}")
    print(f"  📌 Sujet : {ab_output.sujet}")
    print(f"  📊 {len(ab_output.variations)} propositions générées par l'IA")
    print(f"{'═' * 65}")

    for var in ab_output.variations:
        print_test(ab_output, var.version)


# ──────────────────────────────────────────────────────────────────────
# Comparaison directe A vs B
# ──────────────────────────────────────────────────────────────────────

def print_comparaison(ab_output) -> None:
    """
    Compare les tests A et B (et C…) côte à côte.
    Montre un tableau de métriques puis les différences clés
    pour aider à choisir le meilleur post.
    """
    analysis = compare_variations(ab_output)
    metrics = analysis["metrics"]

    print(f"\n{'═' * 65}")
    print(f"  📊 COMPARAISON : ", end="")
    print(" vs ".join(f"TEST {m['version']}" for m in metrics))
    print(f"{'═' * 65}")

    # Tableau de métriques
    print(f"\n{'─' * 65}")
    header = f"  {'Critère':<28}"
    for m in metrics:
        header += f" │ {'Test ' + m['version']:>10}"
    print(header)
    print(f"{'─' * 65}")

    rows = [
        ("Score engagement", "score_numerique", "/100"),
        ("Caractères", "longueur_caracteres", ""),
        ("Mots", "nb_mots", ""),
        ("Questions (?)", "nb_questions", ""),
        ("Exclamations (!)", "nb_exclamations", ""),
        ("Emojis", "nb_emojis", ""),
        ("Hashtags", "nb_hashtags", ""),
        ("  dont haute pertinence", "hashtags_haute", ""),
        ("Qualité hashtags", "hashtag_score", "pts"),
    ]

    for label, key, unit in rows:
        line = f"  {label:<28}"
        values = [m[key] for m in metrics]
        best = max(values)
        for val in values:
            marker = " ★" if val == best and values.count(best) == 1 else ""
            line += f" │ {str(val) + unit:>10}{marker}"
        print(line)

    print(f"{'─' * 65}")
    print("  ★ = meilleure valeur\n")

    # Différences clés
    print(f"  🎯 ACCROCHES :")
    for m in metrics:
        print(f"    Test {m['version']} : \"{m['accroche']}\"")

    print(f"\n  📢 APPELS À L'ACTION :")
    for m in metrics:
        print(f"    Test {m['version']} : {m['call_to_action']}")

    print(f"\n  🎨 STYLES D'IMAGE :")
    for m in metrics:
        couleurs = ", ".join(m["image_couleurs"][:3])
        print(f"    Test {m['version']} : {m['image_style']} ({couleurs})")

    # Hashtags communs / uniques
    communs = analysis["hashtags_communs"]
    uniques = analysis["hashtags_uniques"]

    if communs:
        print(f"\n  🏷️  HASHTAGS EN COMMUN ({len(communs)}) :")
        print(f"    {' '.join(sorted(communs))}")

    if uniques:
        print(f"\n  🏷️  HASHTAGS UNIQUES :")
        for version, tags in uniques.items():
            if tags:
                print(f"    Test {version} uniquement : {' '.join(sorted(tags))}")
            else:
                print(f"    Test {version} : (tous en commun)")
    print()


# ──────────────────────────────────────────────────────────────────────
# Verdict final
# ──────────────────────────────────────────────────────────────────────

def print_verdict(ab_output) -> None:
    """
    Affiche le verdict final : classement des tests et
    recommandation de l'IA sur lequel choisir.
    """
    analysis = compare_variations(ab_output)
    classement = analysis["classement"]

    print(f"\n{'═' * 65}")
    print(f"  🏆 VERDICT : QUEL TEST CHOISIR ?")
    print(f"{'═' * 65}")

    medals = ["🥇", "🥈", "🥉", "4️⃣"]
    print(f"\n  Classement par score d'engagement :\n")
    for i, m in enumerate(classement):
        medal = medals[i] if i < len(medals) else f"#{i + 1}"
        bar_len = m["score_numerique"] // 5
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"   {medal} TEST {m['version']} │ {bar} │ {m['score_numerique']}/100 ({m['score_estime']})")
        print(f"          Stratégie : {m['strategie']}")

    print(f"\n{'─' * 65}")
    print(f"  ✅ Recommandation de l'IA :")
    print(f"  {analysis['recommandation']}")
    print(f"{'─' * 65}")
    print(f"  Critères d'évaluation utilisés :")
    for c in analysis["criteres_evaluation"]:
        print(f"    • {c}")
    print()


# ──────────────────────────────────────────────────────────────────────
# Analyse complète
# ──────────────────────────────────────────────────────────────────────

def print_ab_full_analysis(ab_output) -> None:
    """
    Lance l'analyse complète :
    1. Affiche chaque test (post complet)
    2. Comparaison côte à côte
    3. Verdict et recommandation
    """
    print_all_tests(ab_output)
    print_comparaison(ab_output)
    print_verdict(ab_output)


# ──────────────────────────────────────────────────────────────────────
# Anciens noms (rétro-compatibilité)
# ──────────────────────────────────────────────────────────────────────

def print_ab_summary(ab_output) -> None:
    """Alias → print_comparaison."""
    print_comparaison(ab_output)

def print_ab_texts(ab_output) -> None:
    """Alias → print_all_tests."""
    print_all_tests(ab_output)

def print_ab_differences(ab_output) -> None:
    """Alias → print_comparaison (inclut les différences)."""
    print_comparaison(ab_output)

def print_ab_recommendation(ab_output) -> None:
    """Alias → print_verdict."""
    print_verdict(ab_output)
