"""
Technical evaluation framework for IdeasFactory agents.

This module provides tools for evaluating technologies using standardized criteria
without imposing specific evaluation patterns, allowing agents to develop their
own evaluation frameworks.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import json
from collections import defaultdict

from ideasfactory.utils.error_handler import handle_errors

# Configure logging
logger = logging.getLogger(__name__)

# Standard evaluation criteria - these are provided as EXAMPLES
# but agents are free to define their own criteria
STANDARD_CRITERIA = {
    "performance": {
        "description": "Speed, efficiency, and resource utilization",
        "scale": [
            {"score": 1, "description": "Poor performance, significant resource overhead"},
            {"score": 2, "description": "Below average performance, noticeable resource usage"},
            {"score": 3, "description": "Average performance, acceptable resource usage"},
            {"score": 4, "description": "Good performance, efficient resource usage"},
            {"score": 5, "description": "Excellent performance, highly optimized"}
        ]
    },
    "maintainability": {
        "description": "Ease of maintenance, code quality, documentation",
        "scale": [
            {"score": 1, "description": "Very difficult to maintain, poor documentation"},
            {"score": 2, "description": "Challenging to maintain, limited documentation"},
            {"score": 3, "description": "Moderately maintainable, adequate documentation"},
            {"score": 4, "description": "Easily maintainable, good documentation"},
            {"score": 5, "description": "Highly maintainable, excellent documentation"}
        ]
    },
    "scalability": {
        "description": "Ability to handle growth in users, data, or functionality",
        "scale": [
            {"score": 1, "description": "Poor scalability, significant limitations"},
            {"score": 2, "description": "Limited scalability, may encounter issues with growth"},
            {"score": 3, "description": "Moderate scalability, can handle typical growth patterns"},
            {"score": 4, "description": "Good scalability, can handle substantial growth"},
            {"score": 5, "description": "Excellent scalability, designed for massive scale"}
        ]
    },
    "community_support": {
        "description": "Strength of community, availability of resources and support",
        "scale": [
            {"score": 1, "description": "Minimal or no community, very limited resources"},
            {"score": 2, "description": "Small community, few resources available"},
            {"score": 3, "description": "Moderate community, sufficient resources"},
            {"score": 4, "description": "Strong community, abundant resources"},
            {"score": 5, "description": "Thriving community, extensive resources and support"}
        ]
    },
    "maturity": {
        "description": "Stage of development, stability, and production-readiness",
        "scale": [
            {"score": 1, "description": "Experimental, not ready for production"},
            {"score": 2, "description": "Early stage, limited production use"},
            {"score": 3, "description": "Established but evolving, some production use"},
            {"score": 4, "description": "Mature, widely used in production"},
            {"score": 5, "description": "Very mature, battle-tested in production"}
        ]
    },
    "learning_curve": {
        "description": "Ease of learning and adoption",
        "scale": [
            {"score": 1, "description": "Very steep learning curve, difficult to adopt"},
            {"score": 2, "description": "Significant learning curve, challenging adoption"},
            {"score": 3, "description": "Moderate learning curve, reasonable adoption effort"},
            {"score": 4, "description": "Gentle learning curve, easy to adopt"},
            {"score": 5, "description": "Minimal learning curve, very easy to adopt"}
        ]
    },
    "integration": {
        "description": "Ease of integration with other systems and technologies",
        "scale": [
            {"score": 1, "description": "Very difficult to integrate, limited compatibility"},
            {"score": 2, "description": "Challenging integration, requires significant effort"},
            {"score": 3, "description": "Moderate integration effort, standard interfaces"},
            {"score": 4, "description": "Easy integration, good compatibility"},
            {"score": 5, "description": "Seamless integration, designed for interoperability"}
        ]
    },
    "security": {
        "description": "Security features, vulnerability history, and best practices",
        "scale": [
            {"score": 1, "description": "Major security concerns, history of vulnerabilities"},
            {"score": 2, "description": "Some security issues, limited security features"},
            {"score": 3, "description": "Adequate security, standard security features"},
            {"score": 4, "description": "Good security practices, strong security features"},
            {"score": 5, "description": "Excellent security, comprehensive features and track record"}
        ]
    }
}


@handle_errors
def create_evaluation_framework(
    criteria: Dict[str, Dict[str, Any]] = None,
    custom_criteria: Dict[str, Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a custom evaluation framework with standardized and/or custom criteria.
    
    Args:
        criteria: Dictionary of pre-defined criteria to include
        custom_criteria: Dictionary of custom criteria to add
        
    Returns:
        Complete evaluation framework
    """
    # Start with empty framework
    framework = {"criteria": {}, "weights": {}}
    
    # Add pre-defined criteria if specified
    if criteria:
        for criterion_name, criterion_data in criteria.items():
            if criterion_name in STANDARD_CRITERIA:
                framework["criteria"][criterion_name] = STANDARD_CRITERIA[criterion_name]
                # Default weight of 1.0
                framework["weights"][criterion_name] = 1.0
    
    # Add all standard criteria if none specified
    if not criteria:
        framework["criteria"] = STANDARD_CRITERIA.copy()
        # Default weights of 1.0
        framework["weights"] = {criterion: 1.0 for criterion in STANDARD_CRITERIA}
    
    # Add custom criteria
    if custom_criteria:
        for criterion_name, criterion_data in custom_criteria.items():
            # Ensure proper format for custom criteria
            if "description" in criterion_data:
                framework["criteria"][criterion_name] = criterion_data
                # Default weight of 1.0
                framework["weights"][criterion_name] = 1.0
    
    return framework


@handle_errors
def create_scoring_template(
    framework: Dict[str, Any],
    technology_name: str = ""
) -> Dict[str, Any]:
    """
    Create a template for scoring a technology based on a framework.
    
    Args:
        framework: Evaluation framework with criteria
        technology_name: Name of the technology being evaluated
        
    Returns:
        Dictionary template for scoring
    """
    template = {
        "name": technology_name,
        "scores": {},
        "justifications": {},
        "strengths": [],
        "weaknesses": [],
        "notes": ""
    }
    
    # Create a score entry for each criterion in the framework
    criteria = framework.get("criteria", {})
    for criterion_name in criteria:
        template["scores"][criterion_name] = None
        template["justifications"][criterion_name] = ""
    
    return template


@handle_errors
def evaluate_technology(
    technology: Dict[str, Any],
    framework: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluate a technology using a predefined framework.
    
    Args:
        technology: Technology with scores and justifications
        framework: Evaluation framework with criteria and weights
        
    Returns:
        Evaluation results
    """
    results = {
        "name": technology.get("name", "Unknown Technology"),
        "criteria_scores": {},
        "overall_score": 0,
        "strengths": [],
        "weaknesses": [],
        "summary": {}
    }
    
    # Get scores and weights
    scores = technology.get("scores", {})
    justifications = technology.get("justifications", {})
    weights = framework.get("weights", {})
    criteria = framework.get("criteria", {})
    
    # Calculate weighted scores and find strengths/weaknesses
    total_weighted_score = 0
    total_weight = 0
    
    for criterion, score in scores.items():
        if score is None:
            continue
            
        # Validate score (ensure it's 1-5)
        score = max(1, min(5, score))
        
        # Get weight for this criterion
        weight = weights.get(criterion, 1.0)
        
        # Calculate weighted score
        weighted_score = score * weight
        total_weighted_score += weighted_score
        total_weight += weight
        
        # Store score and justification
        results["criteria_scores"][criterion] = score
        
        # Find criterion details
        criterion_info = criteria.get(criterion, {})
        description = criterion_info.get("description", "")
        scale = criterion_info.get("scale", [])
        
        # Find score description if available
        score_description = ""
        for scale_point in scale:
            if scale_point.get("score") == score:
                score_description = scale_point.get("description", "")
                break
        
        # Add to summary
        results["summary"][criterion] = {
            "score": score,
            "weight": weight,
            "weighted_score": weighted_score,
            "description": description,
            "score_description": score_description,
            "justification": justifications.get(criterion, "")
        }
        
        # Identify strengths and weaknesses
        if score >= 4:
            results["strengths"].append({
                "criterion": criterion,
                "score": score,
                "description": description,
                "justification": justifications.get(criterion, "")
            })
        elif score <= 2:
            results["weaknesses"].append({
                "criterion": criterion,
                "score": score,
                "description": description,
                "justification": justifications.get(criterion, "")
            })
    
    # Calculate overall score
    if total_weight > 0:
        results["overall_score"] = round(total_weighted_score / total_weight, 2)
    
    # Sort strengths and weaknesses by score (descending for strengths, ascending for weaknesses)
    results["strengths"].sort(key=lambda x: x["score"], reverse=True)
    results["weaknesses"].sort(key=lambda x: x["score"])
    
    return results


@handle_errors
def compare_technologies(
    evaluations: Dict[str, Dict[str, Any]],
    framework: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Compare multiple technology evaluations.
    
    Args:
        evaluations: Dictionary mapping technology names to their evaluations
        framework: Evaluation framework for reference (optional)
        
    Returns:
        Comparison results
    """
    comparison = {
        "technologies": list(evaluations.keys()),
        "criteria": [],
        "overall_ranking": [],
        "criteria_comparison": {},
        "strengths_comparison": {},
        "weaknesses_comparison": {},
        "best_per_criterion": {},
        "recommendations": []
    }
    
    # If no evaluations, return empty comparison
    if not evaluations:
        return comparison
    
    # Get all criteria from evaluations
    all_criteria = set()
    for eval_data in evaluations.values():
        all_criteria.update(eval_data.get("criteria_scores", {}).keys())
    
    comparison["criteria"] = sorted(list(all_criteria))
    
    # Generate overall ranking
    tech_scores = []
    for tech_name, eval_data in evaluations.items():
        overall_score = eval_data.get("overall_score", 0)
        tech_scores.append({
            "name": tech_name,
            "score": overall_score
        })
    
    comparison["overall_ranking"] = sorted(tech_scores, key=lambda x: x["score"], reverse=True)
    
    # Compare by criteria
    for criterion in all_criteria:
        comparison["criteria_comparison"][criterion] = []
        
        for tech_name, eval_data in evaluations.items():
            score = eval_data.get("criteria_scores", {}).get(criterion)
            if score is not None:
                comparison["criteria_comparison"][criterion].append({
                    "name": tech_name,
                    "score": score
                })
        
        # Sort by score
        comparison["criteria_comparison"][criterion].sort(key=lambda x: x["score"], reverse=True)
    
    # Find best technology per criterion
    for criterion in all_criteria:
        best_tech = None
        best_score = 0
        
        for tech_name, eval_data in evaluations.items():
            score = eval_data.get("criteria_scores", {}).get(criterion)
            if score is not None and score > best_score:
                best_score = score
                best_tech = tech_name
        
        if best_tech:
            comparison["best_per_criterion"][criterion] = {
                "name": best_tech,
                "score": best_score
            }
    
    # Compare strengths and weaknesses
    for tech_name, eval_data in evaluations.items():
        comparison["strengths_comparison"][tech_name] = eval_data.get("strengths", [])
        comparison["weaknesses_comparison"][tech_name] = eval_data.get("weaknesses", [])
    
    # Generate recommendations
    # Check if there's a clear overall winner
    if comparison["overall_ranking"]:
        best_tech = comparison["overall_ranking"][0]
        
        if len(comparison["overall_ranking"]) > 1:
            second_best = comparison["overall_ranking"][1]
            
            if best_tech["score"] - second_best["score"] >= 0.5:
                # Clear winner
                comparison["recommendations"].append({
                    "type": "clear_winner",
                    "technology": best_tech["name"],
                    "score": best_tech["score"],
                    "message": f"{best_tech['name']} is the recommended technology with a score of {best_tech['score']}"
                })
            else:
                # No clear winner based on overall score
                # Recommend based on specific strengths
                comparison["recommendations"].append({
                    "type": "situational",
                    "message": "Multiple technologies are viable depending on specific needs",
                    "options": []
                })
                
                # Add top 3 technologies with their specific strengths
                for tech in comparison["overall_ranking"][:3]:
                    tech_name = tech["name"]
                    strengths = evaluations[tech_name].get("strengths", [])
                    
                    # Find top strengths
                    top_strengths = []
                    for strength in strengths[:2]:  # Top 2 strengths
                        top_strengths.append(strength["criterion"])
                    
                    if top_strengths:
                        comparison["recommendations"][0]["options"].append({
                            "name": tech_name,
                            "score": tech["score"],
                            "best_for": top_strengths
                        })
        else:
            # Only one technology evaluated
            comparison["recommendations"].append({
                "type": "default",
                "technology": best_tech["name"],
                "message": f"Only {best_tech['name']} was evaluated, with a score of {best_tech['score']}"
            })
    
    return comparison


@handle_errors
def analyze_technology_tradeoffs(
    evaluations: Dict[str, Dict[str, Any]],
    priorities: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Analyze trade-offs between different technologies.
    
    Args:
        evaluations: Dictionary mapping technology names to their evaluations
        priorities: Optional dictionary mapping criteria to their relative importance
        
    Returns:
        Trade-off analysis
    """
    tradeoff_analysis = {
        "technologies": list(evaluations.keys()),
        "trade_offs": [],
        "complementary_pairs": [],
        "recommended_combinations": []
    }
    
    # If no evaluations or only one technology, no trade-offs to analyze
    if len(evaluations) <= 1:
        return tradeoff_analysis
    
    # Get all criteria from evaluations
    all_criteria = set()
    for eval_data in evaluations.values():
        all_criteria.update(eval_data.get("criteria_scores", {}).keys())
    
    # Use default equal priorities if none provided
    if not priorities:
        priorities = {criterion: 1.0 for criterion in all_criteria}
    
    # Find trade-offs between technologies
    tech_names = list(evaluations.keys())
    
    for i in range(len(tech_names)):
        for j in range(i + 1, len(tech_names)):
            tech1 = tech_names[i]
            tech2 = tech_names[j]
            
            tech1_scores = evaluations[tech1].get("criteria_scores", {})
            tech2_scores = evaluations[tech2].get("criteria_scores", {})
            
            # Find criteria where tech1 is better
            tech1_better = []
            for criterion in all_criteria:
                if criterion in tech1_scores and criterion in tech2_scores:
                    if tech1_scores[criterion] > tech2_scores[criterion] + 1:  # Significantly better
                        tech1_better.append({
                            "criterion": criterion,
                            "tech1_score": tech1_scores[criterion],
                            "tech2_score": tech2_scores[criterion],
                            "difference": tech1_scores[criterion] - tech2_scores[criterion],
                            "priority": priorities.get(criterion, 1.0)
                        })
            
            # Find criteria where tech2 is better
            tech2_better = []
            for criterion in all_criteria:
                if criterion in tech1_scores and criterion in tech2_scores:
                    if tech2_scores[criterion] > tech1_scores[criterion] + 1:  # Significantly better
                        tech2_better.append({
                            "criterion": criterion,
                            "tech1_score": tech1_scores[criterion],
                            "tech2_score": tech2_scores[criterion],
                            "difference": tech2_scores[criterion] - tech1_scores[criterion],
                            "priority": priorities.get(criterion, 1.0)
                        })
            
            # If there are significant differences both ways, we have a trade-off
            if tech1_better and tech2_better:
                # Sort by priority-weighted difference
                tech1_better.sort(key=lambda x: x["difference"] * x["priority"], reverse=True)
                tech2_better.sort(key=lambda x: x["difference"] * x["priority"], reverse=True)
                
                tradeoff_analysis["trade_offs"].append({
                    "technologies": [tech1, tech2],
                    "tech1_advantages": tech1_better,
                    "tech2_advantages": tech2_better
                })
                
                # Check if the technologies are complementary (different strengths)
                complementary = False
                for t1_adv in tech1_better:
                    for t2_adv in tech2_better:
                        # If the strengths don't overlap and are in high priority areas
                        if (t1_adv["criterion"] != t2_adv["criterion"] and 
                            t1_adv["priority"] >= 1.0 and t2_adv["priority"] >= 1.0):
                            complementary = True
                            break
                    if complementary:
                        break
                
                if complementary:
                    tradeoff_analysis["complementary_pairs"].append({
                        "technologies": [tech1, tech2],
                        "tech1_strengths": [adv["criterion"] for adv in tech1_better[:2]],
                        "tech2_strengths": [adv["criterion"] for adv in tech2_better[:2]]
                    })
    
    # Recommend combinations for hybrid approaches
    if tradeoff_analysis["complementary_pairs"]:
        # Sort by combined priority-weighted advantages
        def combined_advantage(pair):
            tech1, tech2 = pair["technologies"]
            tech1_eval = evaluations[tech1]
            tech2_eval = evaluations[tech2]
            
            tech1_score = tech1_eval.get("overall_score", 0)
            tech2_score = tech2_eval.get("overall_score", 0)
            
            return tech1_score + tech2_score
        
        sorted_pairs = sorted(tradeoff_analysis["complementary_pairs"], 
                              key=combined_advantage, reverse=True)
        
        # Recommend top 3 complementary pairs
        for pair in sorted_pairs[:3]:
            tech1, tech2 = pair["technologies"]
            tech1_strengths = pair["tech1_strengths"]
            tech2_strengths = pair["tech2_strengths"]
            
            tradeoff_analysis["recommended_combinations"].append({
                "technologies": [tech1, tech2],
                "recommendation": f"Use {tech1} for {', '.join(tech1_strengths)} and {tech2} for {', '.join(tech2_strengths)}",
                "integration_complexity": "Medium"  # Default assumption
            })
    
    return tradeoff_analysis


@handle_errors
def generate_evaluation_report(
    evaluation: Dict[str, Any],
    format_type: str = "markdown"
) -> str:
    """
    Generate a human-readable evaluation report.
    
    Args:
        evaluation: Technology evaluation results
        format_type: Type of formatting to use (markdown, text)
        
    Returns:
        Formatted evaluation report
    """
    if format_type == "markdown":
        return _generate_markdown_report(evaluation)
    else:
        return _generate_text_report(evaluation)


def _generate_markdown_report(evaluation: Dict[str, Any]) -> str:
    """Generate a markdown formatted evaluation report."""
    report = []
    
    # Add header and overall score
    tech_name = evaluation.get("name", "Unknown Technology")
    overall_score = evaluation.get("overall_score", 0)
    
    report.append(f"# Technology Evaluation: {tech_name}")
    report.append("")
    report.append(f"## Overall Score: {overall_score}/5")
    report.append("")
    
    # Add strengths
    strengths = evaluation.get("strengths", [])
    if strengths:
        report.append("## Strengths")
        report.append("")
        
        for strength in strengths:
            criterion = strength.get("criterion", "")
            score = strength.get("score", 0)
            description = strength.get("description", "")
            justification = strength.get("justification", "")
            
            report.append(f"### {criterion} ({score}/5)")
            if description:
                report.append(f"*{description}*")
            report.append("")
            if justification:
                report.append(justification)
                report.append("")
    
    # Add weaknesses
    weaknesses = evaluation.get("weaknesses", [])
    if weaknesses:
        report.append("## Weaknesses")
        report.append("")
        
        for weakness in weaknesses:
            criterion = weakness.get("criterion", "")
            score = weakness.get("score", 0)
            description = weakness.get("description", "")
            justification = weakness.get("justification", "")
            
            report.append(f"### {criterion} ({score}/5)")
            if description:
                report.append(f"*{description}*")
            report.append("")
            if justification:
                report.append(justification)
                report.append("")
    
    # Add all criteria
    report.append("## Detailed Scores")
    report.append("")
    
    # Add criteria scores table
    report.append("| Criterion | Score | Description |")
    report.append("| --- | --- | --- |")
    
    summary = evaluation.get("summary", {})
    for criterion, details in sorted(summary.items()):
        score = details.get("score", 0)
        description = details.get("score_description", "")
        
        report.append(f"| {criterion} | {score}/5 | {description} |")
    
    return "\n".join(report)


def _generate_text_report(evaluation: Dict[str, Any]) -> str:
    """Generate a plain text formatted evaluation report."""
    report = []
    
    # Add header and overall score
    tech_name = evaluation.get("name", "Unknown Technology")
    overall_score = evaluation.get("overall_score", 0)
    
    report.append(f"TECHNOLOGY EVALUATION: {tech_name}")
    report.append("=" * 50)
    report.append("")
    report.append(f"Overall Score: {overall_score}/5")
    report.append("")
    
    # Add strengths
    strengths = evaluation.get("strengths", [])
    if strengths:
        report.append("STRENGTHS")
        report.append("-" * 20)
        
        for strength in strengths:
            criterion = strength.get("criterion", "")
            score = strength.get("score", 0)
            description = strength.get("description", "")
            justification = strength.get("justification", "")
            
            report.append(f"{criterion} ({score}/5)")
            if description:
                report.append(f"  {description}")
            if justification:
                report.append(f"  {justification}")
            report.append("")
    
    # Add weaknesses
    weaknesses = evaluation.get("weaknesses", [])
    if weaknesses:
        report.append("WEAKNESSES")
        report.append("-" * 20)
        
        for weakness in weaknesses:
            criterion = weakness.get("criterion", "")
            score = weakness.get("score", 0)
            description = weakness.get("description", "")
            justification = weakness.get("justification", "")
            
            report.append(f"{criterion} ({score}/5)")
            if description:
                report.append(f"  {description}")
            if justification:
                report.append(f"  {justification}")
            report.append("")
    
    # Add all criteria
    report.append("DETAILED SCORES")
    report.append("-" * 20)
    
    summary = evaluation.get("summary", {})
    for criterion, details in sorted(summary.items()):
        score = details.get("score", 0)
        description = details.get("score_description", "")
        
        report.append(f"{criterion}: {score}/5")
        if description:
            report.append(f"  {description}")
        report.append("")
    
    return "\n".join(report)


@handle_errors
def generate_comparison_report(
    comparison: Dict[str, Any],
    format_type: str = "markdown"
) -> str:
    """
    Generate a human-readable technology comparison report.
    
    Args:
        comparison: Technology comparison results
        format_type: Type of formatting to use (markdown, text)
        
    Returns:
        Formatted comparison report
    """
    if format_type == "markdown":
        return _generate_markdown_comparison(comparison)
    else:
        return _generate_text_comparison(comparison)


def _generate_markdown_comparison(comparison: Dict[str, Any]) -> str:
    """Generate a markdown formatted comparison report."""
    report = []
    
    # Add header
    report.append("# Technology Comparison Report")
    report.append("")
    
    # Add technologies being compared
    technologies = comparison.get("technologies", [])
    report.append("## Technologies Evaluated")
    report.append("")
    
    for tech in technologies:
        report.append(f"- {tech}")
    report.append("")
    
    # Add overall ranking
    report.append("## Overall Ranking")
    report.append("")
    
    overall_ranking = comparison.get("overall_ranking", [])
    for i, tech in enumerate(overall_ranking, 1):
        report.append(f"{i}. **{tech.get('name', '')}** - Score: {tech.get('score', 0)}")
    report.append("")
    
    # Add recommendations
    recommendations = comparison.get("recommendations", [])
    if recommendations:
        report.append("## Recommendations")
        report.append("")
        
        for rec in recommendations:
            rec_type = rec.get("type", "")
            
            if rec_type == "clear_winner":
                tech = rec.get("technology", "")
                message = rec.get("message", "")
                report.append(f"**{tech}** is recommended.")
                if message:
                    report.append(message)
                report.append("")
            
            elif rec_type == "situational":
                message = rec.get("message", "")
                options = rec.get("options", [])
                
                report.append(message)
                report.append("")
                
                for option in options:
                    name = option.get("name", "")
                    best_for = option.get("best_for", [])
                    
                    if best_for:
                        report.append(f"- **{name}** is best for {', '.join(best_for)}")
                    else:
                        report.append(f"- **{name}**")
                
                report.append("")
            
            elif rec_type == "default":
                tech = rec.get("technology", "")
                message = rec.get("message", "")
                
                report.append(f"**{tech}** is the default recommendation.")
                if message:
                    report.append(message)
                report.append("")
    
    # Add best per criterion
    best_per_criterion = comparison.get("best_per_criterion", {})
    if best_per_criterion:
        report.append("## Best Technology Per Criterion")
        report.append("")
        
        for criterion, best in sorted(best_per_criterion.items()):
            name = best.get("name", "")
            score = best.get("score", 0)
            
            report.append(f"- **{criterion}**: {name} (Score: {score}/5)")
        
        report.append("")
    
    # Add detailed comparison by criteria
    criteria_comparison = comparison.get("criteria_comparison", {})
    if criteria_comparison:
        report.append("## Comparison by Criteria")
        report.append("")
        
        for criterion, scores in sorted(criteria_comparison.items()):
            report.append(f"### {criterion}")
            report.append("")
            
            for score_info in scores:
                name = score_info.get("name", "")
                score = score_info.get("score", 0)
                
                report.append(f"- **{name}**: {score}/5")
            
            report.append("")
    
    return "\n".join(report)


def _generate_text_comparison(comparison: Dict[str, Any]) -> str:
    """Generate a plain text formatted comparison report."""
    report = []
    
    # Add header
    report.append("TECHNOLOGY COMPARISON REPORT")
    report.append("=" * 50)
    report.append("")
    
    # Add technologies being compared
    technologies = comparison.get("technologies", [])
    report.append("TECHNOLOGIES EVALUATED")
    report.append("-" * 25)
    
    for tech in technologies:
        report.append(f"- {tech}")
    report.append("")
    
    # Add overall ranking
    report.append("OVERALL RANKING")
    report.append("-" * 25)
    
    overall_ranking = comparison.get("overall_ranking", [])
    for i, tech in enumerate(overall_ranking, 1):
        report.append(f"{i}. {tech.get('name', '')} - Score: {tech.get('score', 0)}")
    report.append("")
    
    # Add recommendations
    recommendations = comparison.get("recommendations", [])
    if recommendations:
        report.append("RECOMMENDATIONS")
        report.append("-" * 25)
        
        for rec in recommendations:
            rec_type = rec.get("type", "")
            
            if rec_type == "clear_winner":
                tech = rec.get("technology", "")
                message = rec.get("message", "")
                report.append(f"{tech} is recommended.")
                if message:
                    report.append(message)
                report.append("")
            
            elif rec_type == "situational":
                message = rec.get("message", "")
                options = rec.get("options", [])
                
                report.append(message)
                report.append("")
                
                for option in options:
                    name = option.get("name", "")
                    best_for = option.get("best_for", [])
                    
                    if best_for:
                        report.append(f"- {name} is best for {', '.join(best_for)}")
                    else:
                        report.append(f"- {name}")
                
                report.append("")
            
            elif rec_type == "default":
                tech = rec.get("technology", "")
                message = rec.get("message", "")
                
                report.append(f"{tech} is the default recommendation.")
                if message:
                    report.append(message)
                report.append("")
    
    # Add best per criterion
    best_per_criterion = comparison.get("best_per_criterion", {})
    if best_per_criterion:
        report.append("BEST TECHNOLOGY PER CRITERION")
        report.append("-" * 25)
        
        for criterion, best in sorted(best_per_criterion.items()):
            name = best.get("name", "")
            score = best.get("score", 0)
            
            report.append(f"{criterion}: {name} (Score: {score}/5)")
        
        report.append("")
    
    # Add detailed comparison by criteria
    criteria_comparison = comparison.get("criteria_comparison", {})
    if criteria_comparison:
        report.append("COMPARISON BY CRITERIA")
        report.append("-" * 25)
        
        for criterion, scores in sorted(criteria_comparison.items()):
            report.append(f"{criterion}:")
            
            for score_info in scores:
                name = score_info.get("name", "")
                score = score_info.get("score", 0)
                
                report.append(f"  {name}: {score}/5")
            
            report.append("")
    
    return "\n".join(report)