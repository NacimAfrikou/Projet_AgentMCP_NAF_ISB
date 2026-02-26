"""
Fonctions utilitaires pour le générateur de posts réseaux sociaux.

Inclut les helpers JSON Schema, le formatage d'affichage,
et l'export des résultats.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


# ──────────────────────────────────────────────────────────────────────
# JSON Schema helpers (requis par OpenAI Structured Outputs)
# ──────────────────────────────────────────────────────────────────────

def resolve_schema_refs(schema: dict) -> dict:
    """
    Résout toutes les références $ref en inlinant les définitions depuis $defs.
    
    Nécessaire car OpenAI strict mode interdit les keywords siblings
    à côté de $ref (ex: description + $ref ensemble).
    Pydantic 2.x génère ce pattern pour les champs avec Field(description=...).
    """
    import copy
    defs = schema.get("$defs", {})

    def _resolve(node):
        if not isinstance(node, dict):
            return node

        if "$ref" in node:
            ref_name = node["$ref"].split("/")[-1]
            if ref_name in defs:
                # Inline la définition (copie profonde pour éviter la mutation)
                resolved = copy.deepcopy(defs[ref_name])
                return _resolve(resolved)
            return node

        result = {}
        for key, value in node.items():
            if key == "$defs":
                continue  # On supprime $defs car tout est inliné
            elif isinstance(value, dict):
                result[key] = _resolve(value)
            elif isinstance(value, list):
                result[key] = [
                    _resolve(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    return _resolve(schema)


def add_additional_properties_false(schema: dict) -> dict:
    """
    Prépare un schéma Pydantic pour OpenAI Structured Outputs :
    1. Résout les $ref en inlinant les définitions (évite l'erreur sibling keywords)
    2. Ajoute additionalProperties: False sur tous les objets
    3. Met tous les champs dans 'required'
    
    Référence : GenAI/Texte/3_Structured_Outputs.ipynb
    """
    # Étape 1 : Résoudre toutes les $ref
    schema = resolve_schema_refs(schema)

    # Étape 2 : Ajouter les contraintes OpenAI récursivement
    def _fix(node):
        if not isinstance(node, dict):
            return node

        # Si c'est un objet, ajouter additionalProperties: False
        if node.get("type") == "object":
            node["additionalProperties"] = False
            if "properties" in node:
                node["required"] = list(node["properties"].keys())
                for prop_schema in node["properties"].values():
                    _fix(prop_schema)

        # Traiter les items d'arrays
        if node.get("type") == "array" and "items" in node:
            _fix(node["items"])

        # Traiter anyOf, allOf, oneOf
        for key in ["anyOf", "allOf", "oneOf"]:
            if key in node:
                for item in node[key]:
                    _fix(item)

        return node

    return _fix(schema)


# ──────────────────────────────────────────────────────────────────────
# Formatage d'affichage
# ──────────────────────────────────────────────────────────────────────

def format_post_display(post, show_image_prompt: bool = False) -> str:
    """
    Formate un PostContent pour affichage lisible.
    
    Args:
        post: Instance PostContent
        show_image_prompt: Afficher le prompt d'image
        
    Returns:
        Texte formaté
    """
    separator = "─" * 60
    lines = [
        f"\n{'═' * 60}",
        f"  📱 {post.plateforme.upper()}",
        f"{'═' * 60}",
        "",
        f"📝 Texte du post ({post.longueur_caracteres} caractères) :",
        f"{separator}",
        post.texte,
        f"{separator}",
        "",
        f"🎯 Accroche : {post.accroche}",
        f"📢 CTA : {post.call_to_action}",
        "",
        f"# Hashtags ({len(post.hashtags)}) :",
    ]

    for h in post.hashtags:
        lines.append(f"  #{h.tag} [{h.relevance}]")

    lines.append(f"\n⏰ Meilleurs créneaux de publication :")
    for t in post.timing:
        lines.append(
            f"  • {t.jour} à {t.heure} — {t.raison} [{t.score_engagement}]"
        )

    if show_image_prompt:
        lines.extend([
            "",
            f"🎨 Prompt image DALL-E 3 :",
            f"  Style : {post.image_prompt.style}",
            f"  Couleurs : {', '.join(post.image_prompt.couleurs_dominantes)}",
            f"  Éléments : {', '.join(post.image_prompt.elements_cles)}",
            f"  Prompt : {post.image_prompt.prompt_en}",
        ])

    return "\n".join(lines)


def format_full_output(output, show_image_prompts: bool = False) -> str:
    """
    Formate un SocialMediaOutput complet.
    
    Args:
        output: Instance SocialMediaOutput
        show_image_prompts: Afficher les prompts d'image
        
    Returns:
        Texte formaté complet
    """
    lines = [
        "╔══════════════════════════════════════════════════════════════╗",
        "║         🚀 POSTS RÉSEAUX SOCIAUX GÉNÉRÉS                   ║",
        "╚══════════════════════════════════════════════════════════════╝",
        "",
        f"📌 Sujet : {output.sujet}",
        f"🎯 Objectif : {output.objectif}",
    ]

    for post in output.posts:
        lines.append(format_post_display(post, show_image_prompts))

    lines.extend([
        "",
        f"{'═' * 60}",
        f"💡 Conseil stratégique : {output.conseil_global}",
        f"{'═' * 60}",
    ])

    return "\n".join(lines)


def format_ab_output(ab_output) -> str:
    """
    Formate un ABTestOutput pour affichage.
    
    Args:
        ab_output: Instance ABTestOutput
        
    Returns:
        Texte formaté
    """
    lines = [
        "╔══════════════════════════════════════════════════════════════╗",
        "║         🔬 TEST A/B — VARIATIONS GÉNÉRÉES                  ║",
        "╚══════════════════════════════════════════════════════════════╝",
        "",
        f"📱 Plateforme : {ab_output.plateforme.upper()}",
        f"📌 Sujet : {ab_output.sujet}",
        f"📊 Critères d'évaluation : {', '.join(ab_output.criteres_evaluation)}",
    ]

    for var in ab_output.variations:
        lines.extend([
            "",
            f"{'─' * 60}",
            f"  🅰️ Variation {var.version} — Stratégie : {var.strategie}",
            f"  📈 Score estimé : {var.score_estime}",
            f"{'─' * 60}",
            "",
            var.post.texte,
            "",
            f"  # Hashtags : {' '.join('#' + h.tag for h in var.post.hashtags[:5])}",
            f"  📢 CTA : {var.post.call_to_action}",
        ])

    lines.extend([
        "",
        f"{'═' * 60}",
        f"✅ Recommandation : {ab_output.recommandation}",
        f"{'═' * 60}",
    ])

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────
# Export
# ──────────────────────────────────────────────────────────────────────

def export_to_json(
    data: BaseModel,
    filepath: str,
    indent: int = 2,
) -> str:
    """
    Exporte un résultat Pydantic vers un fichier JSON.
    
    Args:
        data: Instance Pydantic à exporter
        filepath: Chemin du fichier de sortie
        indent: Indentation JSON
        
    Returns:
        Chemin absolu du fichier sauvegardé
    """
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(data.model_dump_json(indent=indent))
    
    return os.path.abspath(filepath)


def export_posts_markdown(output, filepath: str) -> str:
    """
    Exporte les posts en format Markdown (prêt à copier-coller).
    
    Args:
        output: SocialMediaOutput
        filepath: Chemin du fichier .md
        
    Returns:
        Chemin absolu du fichier
    """
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    
    lines = [
        f"# Posts Réseaux Sociaux — {output.sujet}",
        f"",
        f"*Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*",
        f"",
        f"**Objectif** : {output.objectif}",
        f"",
    ]

    for post in output.posts:
        platform_emoji = {
            "linkedin": "🔵",
            "instagram": "📸",
            "twitter": "🐦",
        }
        emoji = platform_emoji.get(post.plateforme, "📱")
        
        lines.extend([
            f"---",
            f"",
            f"## {emoji} {post.plateforme.upper()}",
            f"",
            f"### Texte ({post.longueur_caracteres} caractères)",
            f"",
            f"```",
            post.texte,
            f"```",
            f"",
            f"### Hashtags",
            f"",
            " ".join(f"`#{h.tag}`" for h in post.hashtags),
            f"",
            f"### Meilleurs créneaux",
            f"",
        ])
        for t in post.timing:
            lines.append(f"- **{t.jour} {t.heure}** — {t.raison}")
        
        lines.extend([
            f"",
            f"### Prompt image DALL-E 3",
            f"",
            f"> {post.image_prompt.prompt_en}",
            f"",
            f"- Style : {post.image_prompt.style}",
            f"- Couleurs : {', '.join(post.image_prompt.couleurs_dominantes)}",
            f"",
        ])

    lines.extend([
        f"---",
        f"",
        f"**💡 Conseil** : {output.conseil_global}",
    ])

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    return os.path.abspath(filepath)
