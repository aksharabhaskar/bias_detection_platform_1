from typing import Dict, List

METRIC_DEFINITIONS = {
    "demographic_parity": {
        "name": "demographic_parity",
        "display_name": "Demographic Parity",
        "definition": "Ensures that the proportion of individuals receiving a positive outcome (e.g., being shortlisted) is equal across all groups defined by protected attributes.",
        "interpretation": "The shortlisting rates should be similar across all groups. Differences less than 10% are generally considered fair.",
        "context": "Use this metric when you want to ensure equal representation in positive outcomes regardless of group membership. Most appropriate for screening decisions.",
        "what_this_means": "One group is being shortlisted more often regardless of qualification.",
        "what_is_wrong": "The screening system is over-selecting one group. Hiring is outcome-biased, not merit-based.",
        "root_causes": [
            "Use of biased historical data",
            "Proxy features (education, experience) correlated with gender/age",
            "Single hard threshold applied uniformly"
        ],
        "recruiter_actions": [
            "Review screening score distribution by group",
            "Introduce group-aware threshold audits",
            "Remove or re-weight proxy features",
            "Add post-screening fairness checks"
        ],
        "dashboard_recommendation": "Selection rates differ significantly across groups. Review screening thresholds and feature weights to ensure equal access to shortlisting.",
        "value_segments": [
            {"max": 0.05, "interpretation": "Practically equal selection", "severity": "Fair"},
            {"max": 0.15, "interpretation": "Noticeable imbalance", "severity": "Warning"},
            {"max": 1.0, "interpretation": "Strong imbalance", "severity": "Violation"}
        ]
    },
    "disparate_impact": {
        "name": "disparate_impact",
        "display_name": "Disparate Impact (80% Rule)",
        "definition": "Measures the ratio of selection rates between groups. The 80% rule (also called four-fifths rule) is a legal standard in employment.",
        "interpretation": "The ratio should be at least 0.8 (80%). Values below 0.8 may indicate adverse impact.",
        "context": "This is a legal standard used by EEOC and courts to detect discrimination. Particularly important for hiring and promotion decisions.",
        "what_this_means": "A protected group receives less than 80% of the opportunities compared to the reference group.",
        "what_is_wrong": "The system violates regulatory fairness standards. Potential legal and compliance risk.",
        "root_causes": [
            "Screening score penalizes certain demographics",
            "Hard filters disproportionately remove one group"
        ],
        "recruiter_actions": [
            "Immediately audit AI screening rules",
            "Run counterfactual tests (same candidate, different group)",
            "Adjust thresholds or scoring weights",
            "Introduce fairness-aware post-processing"
        ],
        "dashboard_recommendation": "Fails the 80% rule. This indicates adverse impact and potential regulatory risk. Immediate model and threshold review required.",
        "value_segments": [
            {"min": 0.80, "interpretation": "Passes 80% rule", "severity": "Fair"},
            {"min": 0.60, "max": 0.79, "interpretation": "Potential adverse impact", "severity": "Warning"},
            {"max": 0.60, "interpretation": "Strong adverse impact", "severity": "Violation"}
        ]
    },
    "equal_opportunity": {
        "name": "equal_opportunity",
        "display_name": "Equal Opportunity (TPR Equality)",
        "definition": "Ensures that the True Positive Rate (correctly identifying qualified candidates) is equal across groups.",
        "interpretation": "All qualified candidates should have an equal chance of being identified as qualified, regardless of group. Values should be similar across groups.",
        "context": "Use when the cost of false negatives (missing qualified candidates) is high and should be distributed fairly.",
        "what_this_means": "Qualified candidates from one group are being missed.",
        "what_is_wrong": "Merit is not rewarded equally. High-quality candidates are lost unfairly.",
        "root_causes": [
            "Screening score underestimates capability of one group",
            "Resume features are unevenly interpreted"
        ],
        "recruiter_actions": [
            "Re-evaluate what 'qualified' means",
            "Improve feature engineering (skills over proxies)",
            "Introduce manual review for borderline cases"
        ],
        "dashboard_recommendation": "Qualified candidates from one group are less likely to be shortlisted. Review feature relevance and qualification definitions.",
        "value_segments": [
            {"max": 0.05, "interpretation": "Qualified treated equally", "severity": "Fair"},
            {"max": 0.15, "interpretation": "Unequal access", "severity": "Warning"},
            {"max": 1.0, "interpretation": "Qualified candidates missed", "severity": "Violation"}
        ]
    },
    "predictive_equality": {
        "name": "predictive_equality",
        "display_name": "Predictive Equality (FPR Equality)",
        "definition": "Ensures that the False Positive Rate (incorrectly identifying unqualified candidates) is equal across groups.",
        "interpretation": "Unqualified candidates from all groups should have an equal chance of being incorrectly selected. Rates should be similar.",
        "context": "Use when the cost of false positives (selecting unqualified candidates) should be distributed fairly across groups.",
        "what_this_means": "One group is being shortlisted incorrectly more often.",
        "what_is_wrong": "Hiring quality is inconsistent. One group benefits from leniency.",
        "root_causes": [
            "Threshold too low for certain groups",
            "Noise or bias in score calibration"
        ],
        "recruiter_actions": [
            "Tighten screening thresholds",
            "Improve validation of shortlisting decisions",
            "Apply consistent evaluation criteria"
        ],
        "dashboard_recommendation": "False positive rates differ across groups, indicating inconsistent shortlisting quality.",
        "value_segments": [
            {"max": 0.05, "interpretation": "Balanced errors", "severity": "Fair"},
            {"max": 0.15, "interpretation": "Inconsistent leniency", "severity": "Warning"},
            {"max": 1.0, "interpretation": "One group favored", "severity": "Violation"}
        ]
    },
    "calibration_by_group": {
        "name": "calibration_by_group",
        "display_name": "Calibration by Group",
        "definition": "Ensures that predicted probabilities or scores reflect actual outcomes equally well across groups.",
        "interpretation": "For each score range, the actual success rate should be similar across groups. Good calibration means scores are trustworthy.",
        "context": "Important when using risk scores or probability estimates that inform human decision-making.",
        "what_this_means": "Same score means different outcomes across groups.",
        "what_is_wrong": "AI score is unreliable. Trust in ATS is compromised.",
        "root_causes": [
            "Score trained on biased labels",
            "Unequal representation in training data"
        ],
        "recruiter_actions": [
            "Retrain scoring model with balanced data",
            "Calibrate scores separately by group",
            "Avoid strict score cutoffs"
        ],
        "dashboard_recommendation": "Screening scores are not equally predictive across groups. Model recalibration is recommended.",
        "value_segments": [
            {"max": 0.05, "interpretation": "Well-calibrated", "severity": "Fair"},
            {"max": 0.10, "interpretation": "Mild calibration drift", "severity": "Warning"},
            {"max": 1.0, "interpretation": "Score unreliable", "severity": "Violation"}
        ]
    },
    "false_negative_rate_parity": {
        "name": "false_negative_rate_parity",
        "display_name": "False Negative Rate Parity",
        "definition": "Ensures that the rate of missing qualified candidates (false negatives) is equal across groups.",
        "interpretation": "The proportion of qualified candidates who are incorrectly rejected should be similar across groups.",
        "context": "Critical when missing qualified candidates has significant negative consequences (e.g., talent loss, diversity goals).",
        "what_this_means": "One group has higher rate of qualified candidates being wrongly rejected.",
        "what_is_wrong": "Talent loss. Unfair exclusion.",
        "root_causes": [
            "Conservative thresholds",
            "Poor skill extraction for certain groups"
        ],
        "recruiter_actions": [
            "Lower rejection thresholds for borderline cases",
            "Add second-stage review",
            "Improve resume parsing logic"
        ],
        "dashboard_recommendation": "Higher rejection errors for a group indicate potential talent loss. Review rejection thresholds.",
        "value_segments": [
            {"max": 0.05, "interpretation": "Equal rejection errors", "severity": "Fair"},
            {"max": 0.15, "interpretation": "Talent loss risk", "severity": "Warning"},
            {"max": 1.0, "interpretation": "Systematic rejection", "severity": "Violation"}
        ]
    },
    "false_discovery_rate_parity": {
        "name": "false_discovery_rate_parity",
        "display_name": "False Discovery Rate Parity",
        "definition": "Ensures that among those selected, the proportion who are unqualified is equal across groups.",
        "interpretation": "The 'error rate' among selected candidates should be consistent across groups. Similar FDR values indicate fairness.",
        "context": "Important when you want to ensure equal quality among selected candidates from different groups.",
        "what_this_means": "Shortlisted candidates from one group are less reliable.",
        "what_is_wrong": "Shortlisting quality varies. Hiring inefficiency.",
        "root_causes": [
            "Bias in resume keyword matching",
            "Uneven scoring noise"
        ],
        "recruiter_actions": [
            "Strengthen validation of shortlisted candidates",
            "Use skill-based assessments",
            "Reduce over-reliance on AI scores"
        ],
        "dashboard_recommendation": "Shortlisting reliability differs across groups. Review validation mechanisms.",
        "value_segments": [
            {"max": 0.05, "interpretation": "Consistent shortlist quality", "severity": "Fair"},
            {"max": 0.15, "interpretation": "Uneven reliability", "severity": "Warning"},
            {"max": 1.0, "interpretation": "Poor hiring quality", "severity": "Violation"}
        ]
    },
    "accuracy_equality": {
        "name": "accuracy_equality",
        "display_name": "Accuracy Equality",
        "definition": "Ensures that the overall prediction accuracy is equal across all groups.",
        "interpretation": "The model should perform equally well for all groups. Differences in accuracy indicate potential bias.",
        "context": "Use as a general fairness check. However, equal accuracy doesn't guarantee fairness in all error types.",
        "what_this_means": "The AI system performs better for one group.",
        "what_is_wrong": "Unequal system performance. Model favors dominant group.",
        "root_causes": [
            "Data imbalance",
            "Overfitting to majority group patterns"
        ],
        "recruiter_actions": [
            "Balance training data",
            "Perform group-wise performance testing",
            "Avoid deploying model without fairness validation"
        ],
        "dashboard_recommendation": "Prediction accuracy differs across groups. Indicates unequal system performance.",
        "value_segments": [
            {"max": 0.05, "interpretation": "Equal system performance", "severity": "Fair"},
            {"max": 0.10, "interpretation": "Uneven performance", "severity": "Warning"},
            {"max": 1.0, "interpretation": "System favors one group", "severity": "Violation"}
        ]
    },
    "predictive_parity_ppv": {
        "name": "predictive_parity_ppv",
        "display_name": "Predictive Parity (PPV)",
        "definition": "Ensures that the Positive Predictive Value (precision) is equal across groups - i.e., among those selected, the success rate is equal.",
        "interpretation": "Among shortlisted candidates, the actual qualification rate should be similar across groups.",
        "context": "Important when you want to ensure that selection decisions have equal predictive validity across groups.",
        "what_this_means": "Shortlisted candidates from one group are more likely to be truly qualified.",
        "what_is_wrong": "Hiring confidence differs by group. Biased talent perception.",
        "root_causes": [
            "Score calibration issues",
            "Threshold inconsistencies"
        ],
        "recruiter_actions": [
            "Align confidence thresholds",
            "Improve model calibration",
            "Standardize evaluation criteria"
        ],
        "dashboard_recommendation": "Shortlisting precision differs across groups. Indicates unequal confidence in selections.",
        "value_segments": [
            {"max": 0.05, "interpretation": "Equal confidence", "severity": "Fair"},
            {"max": 0.15, "interpretation": "Uneven confidence", "severity": "Warning"},
            {"max": 1.0, "interpretation": "Biased confidence", "severity": "Violation"}
        ]
    },
    "equalized_odds": {
        "name": "equalized_odds",
        "display_name": "Equalized Odds",
        "definition": "Ensures that both True Positive Rate and False Positive Rate are equal across groups. This is a combination of equal opportunity and predictive equality.",
        "interpretation": "Both qualified and unqualified candidates should have equal error rates across groups. This is a strong fairness criterion.",
        "context": "Use when you want comprehensive fairness that accounts for both types of errors. Often considered one of the most rigorous fairness metrics.",
        "what_this_means": "Overall error behavior is biased.",
        "what_is_wrong": "One group is both favored and protected from errors.",
        "root_causes": [
            "Structural bias in scoring pipeline"
        ],
        "recruiter_actions": [
            "Re-design scoring pipeline",
            "Use fairness-aware optimization",
            "Apply post-processing corrections"
        ],
        "dashboard_recommendation": "Error rates differ across groups. Comprehensive fairness correction required.",
        "value_segments": [
            {"max": 0.05, "interpretation": "Balanced errors", "severity": "Fair"},
            {"max": 0.15, "interpretation": "Partial imbalance", "severity": "Warning"},
            {"max": 1.0, "interpretation": "Structural bias", "severity": "Violation"}
        ]
    },
    "statistical_parity_difference": {
        "name": "statistical_parity_difference",
        "display_name": "Statistical Parity Difference",
        "definition": "Measures the absolute difference in selection rates between the most and least favored groups.",
        "interpretation": "Values close to 0 indicate fairness. Typically, |SPD| < 0.1 is considered fair.",
        "context": "A simple, interpretable metric for measuring outcome differences. Good for initial bias screening.",
        "what_this_means": "Clear imbalance in outcomes.",
        "what_is_wrong": "Systematic bias.",
        "root_causes": [
            "Biased selection process",
            "Unfair thresholds"
        ],
        "recruiter_actions": [
            "Review entire screening workflow",
            "Introduce fairness constraints"
        ],
        "dashboard_recommendation": "Statistical parity difference is significant. Review entire screening workflow and introduce fairness constraints.",
        "value_segments": [
            {"max": 0.05, "interpretation": "Minimal disparity", "severity": "Fair"},
            {"max": 0.15, "interpretation": "Moderate disparity", "severity": "Warning"},
            {"max": 1.0, "interpretation": "Strong disparity", "severity": "Violation"}
        ]
    },
    "average_odds_difference": {
        "name": "average_odds_difference",
        "display_name": "Average Odds Difference",
        "definition": "Measures the average of the absolute differences in False Positive Rate and True Positive Rate between groups.",
        "interpretation": "Values close to 0 indicate fairness. This metric balances both types of errors.",
        "context": "Use when you want a single metric that captures both opportunity and predictive equality.",
        "what_this_means": "Combined error imbalance.",
        "what_is_wrong": "Both acceptance and rejection errors are biased.",
        "root_causes": [
            "Systematic scoring bias",
            "Poorly calibrated thresholds"
        ],
        "recruiter_actions": [
            "Address both acceptance and rejection bias",
            "Adjust thresholds + retraining"
        ],
        "dashboard_recommendation": "Average odds difference indicates combined error imbalance. Address both acceptance and rejection bias through threshold adjustment and retraining.",
        "value_segments": [
            {"max": 0.05, "interpretation": "Minimal error difference", "severity": "Fair"},
            {"max": 0.15, "interpretation": "Unequal errors", "severity": "Warning"},
            {"max": 1.0, "interpretation": "Serious bias", "severity": "Violation"}
        ]
    },
    "theil_index": {
        "name": "theil_index",
        "display_name": "Theil Index",
        "definition": "Measures inequality in the distribution of positive outcomes relative to group representation. Based on information theory.",
        "interpretation": "Values close to 0 indicate fairness. Higher values indicate greater inequality in outcome distribution.",
        "context": "Useful for understanding overall distributional fairness across multiple groups simultaneously.",
        "what_this_means": "Outcomes are highly unequal.",
        "what_is_wrong": "Structural inequality amplified by AI.",
        "root_causes": [
            "Biased historical data",
            "Over-filtering certain groups"
        ],
        "recruiter_actions": [
            "Review hiring volume & thresholds",
            "Reduce over-filtering",
            "Improve inclusivity measures"
        ],
        "dashboard_recommendation": "Theil Index indicates high inequality. Review hiring volume, reduce over-filtering, and improve inclusivity measures.",
        "value_segments": [
            {"max": 0.5, "interpretation": "Low inequality", "severity": "Fair"},
            {"max": 1.0, "interpretation": "Moderate inequality", "severity": "Warning"},
            {"max": 10.0, "interpretation": "High inequality", "severity": "Violation"}
        ]
    }
}

def get_metric_definition(metric_name: str) -> Dict[str, str]:
    """Get the definition and explanation for a specific metric"""
    return METRIC_DEFINITIONS.get(metric_name, {
        "name": metric_name,
        "display_name": metric_name.replace("_", " ").title(),
        "definition": "Definition not available",
        "formula": "Formula not available",
        "interpretation": "Interpretation not available",
        "context": "Context not available",
        "fairness_implications": "Fairness implications not available",
        "recommendations": "Recommendations not available"
    })

def get_all_metrics() -> Dict[str, Dict[str, str]]:
    """Get all metric definitions"""
    return METRIC_DEFINITIONS
