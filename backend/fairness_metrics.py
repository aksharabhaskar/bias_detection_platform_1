import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.metrics import confusion_matrix

class FairnessMetrics:
    """Calculate all 13 fairness metrics for bias detection - matches Streamlit implementation"""
    
    def __init__(self, df: pd.DataFrame, protected_attr: str):
        self.df = df.copy()
        self.protected_attr = protected_attr
        self.groups = df[protected_attr].unique()
        
        # Create predicted_shortlist from screening_score using median threshold (like Streamlit)
        if 'screening_score' in self.df.columns:
            self.threshold = self.df['screening_score'].median()
            self.df['predicted_shortlist'] = (self.df['screening_score'] >= self.threshold).astype(int)
        else:
            self.threshold = None
            self.df['predicted_shortlist'] = self.df['shortlisted']
    
    def _get_group_data(self, group):
        """Get data for a specific group"""
        return self.df[self.df[self.protected_attr] == group]
    
    def _get_confusion_matrix(self, group):
        """Calculate confusion matrix for a specific group"""
        group_data = self._get_group_data(group)
        if len(group_data) == 0:
            return 0, 0, 0, 0
        
        tn, fp, fn, tp = confusion_matrix(
            group_data['shortlisted'],
            group_data['predicted_shortlist'],
            labels=[0, 1]
        ).ravel()
        return tn, fp, fn, tp
    
    def demographic_parity(self) -> Dict[str, Any]:
        """Calculate demographic parity - shortlisting rates by group"""
        results = {}
        for group in self.groups:
            group_data = self._get_group_data(group)
            rate = group_data['shortlisted'].mean()
            results[str(group)] = float(rate)
        
        # Calculate fairness assessment
        rates = list(results.values())
        max_diff = max(rates) - min(rates)
        assessment = "Fair" if max_diff < 0.1 else "Warning" if max_diff < 0.2 else "Violation"
        
        return {
            'values': results,
            'visualization_type': 'bar',
            'fairness_assessment': assessment,
            'max_difference': float(max_diff)
        }
    
    def disparate_impact(self) -> Dict[str, Any]:
        """Calculate disparate impact ratio (80% rule)"""
        rates = {}
        for group in self.groups:
            group_data = self._get_group_data(group)
            rates[str(group)] = float(group_data['shortlisted'].mean())
        
        if len(rates) < 2:
            return {'values': rates, 'fairness_assessment': 'Insufficient data'}
        
        # Calculate ratios relative to highest rate
        max_rate = max(rates.values())
        ratios = {group: float(rate / max_rate if max_rate > 0 else 0) for group, rate in rates.items()}
        
        # 80% rule: ratios should be >= 0.8
        min_ratio = min(ratios.values())
        assessment = "Fair" if min_ratio >= 0.8 else "Violation"
        
        return {
            'values': ratios,
            'rates': rates,
            'visualization_type': 'bar',
            'fairness_assessment': assessment,
            'min_ratio': float(min_ratio),
            'threshold': 0.8
        }
    
    def equal_opportunity(self) -> Dict[str, Any]:
        """Calculate True Positive Rate equality - ONLY for qualified candidates (screening_score >= threshold)"""
        results = {}
        
        if self.threshold is not None and 'screening_score' in self.df.columns:
            # Filter to qualified candidates only (like Streamlit)
            qualified = self.df[self.df['screening_score'] >= self.threshold]
            for group in self.groups:
                group_data = qualified[qualified[self.protected_attr] == group]
                if len(group_data) > 0:
                    rate = group_data['shortlisted'].mean()
                    results[str(group)] = float(rate)
                else:
                    results[str(group)] = 0.0
        else:
            # Fallback: use TPR from confusion matrix
            for group in self.groups:
                tn, fp, fn, tp = self._get_confusion_matrix(group)
                tpr = tp / (tp + fn + 1e-6)
                results[str(group)] = float(tpr)
        
        values = list(results.values())
        max_diff = max(values) - min(values) if values else 0
        assessment = "Fair" if max_diff < 0.1 else "Warning" if max_diff < 0.2 else "Violation"
        
        return {
            'values': results,
            'visualization_type': 'bar',
            'fairness_assessment': assessment,
            'max_difference': float(max_diff)
        }
    
    def predictive_equality(self) -> Dict[str, Any]:
        """Calculate False Positive Rate equality"""
        results = {}
        for group in self.groups:
            tn, fp, fn, tp = self._get_confusion_matrix(group)
            fpr = fp / (fp + tn + 1e-6)
            results[str(group)] = float(fpr)
        
        values = list(results.values())
        max_diff = max(values) - min(values) if values else 0
        assessment = "Fair" if max_diff < 0.1 else "Warning" if max_diff < 0.2 else "Violation"
        
        return {
            'values': results,
            'visualization_type': 'bar',
            'fairness_assessment': assessment,
            'max_difference': float(max_diff)
        }
    
    def calibration_by_group(self) -> Dict[str, Any]:
        """Calculate calibration across score bins using quantile binning"""
        if 'screening_score' not in self.df.columns:
            return {'values': {}, 'fairness_assessment': 'No screening_score column available'}
        
        try:
            # Use quantile binning (like Streamlit qcut)
            self.df['score_bin'] = pd.qcut(self.df['screening_score'], q=10, duplicates='drop')
            
            calibration_data = {}
            bin_labels = sorted(self.df['score_bin'].unique())
            
            for group in self.groups:
                group_data = self._get_group_data(group)
                group_calibration = []
                
                for bin_val in bin_labels:
                    bin_data = group_data[group_data['score_bin'] == bin_val]
                    if len(bin_data) > 0:
                        actual_rate = bin_data['shortlisted'].mean()
                        group_calibration.append(float(actual_rate))
                    else:
                        group_calibration.append(0.0)
                
                calibration_data[str(group)] = group_calibration
            
            return {
                'values': calibration_data,
                'bins': [str(b) for b in bin_labels],
                'visualization_type': 'heatmap',
                'fairness_assessment': 'See visualization'
            }
        except Exception as e:
            return {
                'values': {},
                'fairness_assessment': f'Error: {str(e)}'
            }
    
    def false_negative_rate_parity(self) -> Dict[str, Any]:
        """Calculate False Negative Rate parity"""
        results = {}
        for group in self.groups:
            tn, fp, fn, tp = self._get_confusion_matrix(group)
            fnr = fn / (fn + tp + 1e-6)
            results[str(group)] = float(fnr)
        
        values = list(results.values())
        max_diff = max(values) - min(values) if values else 0
        assessment = "Fair" if max_diff < 0.1 else "Warning" if max_diff < 0.2 else "Violation"
        
        return {
            'values': results,
            'visualization_type': 'bar',
            'fairness_assessment': assessment,
            'max_difference': float(max_diff)
        }
    
    def false_discovery_rate_parity(self) -> Dict[str, Any]:
        """Calculate False Discovery Rate parity"""
        results = {}
        for group in self.groups:
            tn, fp, fn, tp = self._get_confusion_matrix(group)
            fdr = fp / (fp + tp + 1e-6)
            results[str(group)] = float(fdr)
        
        values = list(results.values())
        max_diff = max(values) - min(values) if values else 0
        assessment = "Fair" if max_diff < 0.1 else "Warning" if max_diff < 0.2 else "Violation"
        
        return {
            'values': results,
            'visualization_type': 'bar',
            'fairness_assessment': assessment,
            'max_difference': float(max_diff)
        }
    
    def accuracy_equality(self) -> Dict[str, Any]:
        """Calculate accuracy equality across groups"""
        results = {}
        for group in self.groups:
            tn, fp, fn, tp = self._get_confusion_matrix(group)
            accuracy = (tp + tn) / (tp + tn + fp + fn + 1e-6)
            results[str(group)] = float(accuracy)
        
        values = list(results.values())
        max_diff = max(values) - min(values) if values else 0
        assessment = "Fair" if max_diff < 0.1 else "Warning" if max_diff < 0.2 else "Violation"
        
        return {
            'values': results,
            'visualization_type': 'bar',
            'fairness_assessment': assessment,
            'max_difference': float(max_diff)
        }
    
    def predictive_parity_ppv(self) -> Dict[str, Any]:
        """Calculate Positive Predictive Value parity"""
        results = {}
        for group in self.groups:
            tn, fp, fn, tp = self._get_confusion_matrix(group)
            ppv = tp / (tp + fp + 1e-6)
            results[str(group)] = float(ppv)
        
        values = list(results.values())
        max_diff = max(values) - min(values) if values else 0
        assessment = "Fair" if max_diff < 0.1 else "Warning" if max_diff < 0.2 else "Violation"
        
        return {
            'values': results,
            'visualization_type': 'bar',
            'fairness_assessment': assessment,
            'max_difference': float(max_diff)
        }
    
    def equalized_odds(self) -> Dict[str, Any]:
        """Calculate equalized odds (TPR and FPR together)"""
        results = {}
        for group in self.groups:
            tn, fp, fn, tp = self._get_confusion_matrix(group)
            tpr = tp / (tp + fn + 1e-6)
            fpr = fp / (fp + tn + 1e-6)
            results[str(group)] = {
                'tpr': float(tpr),
                'fpr': float(fpr)
            }
        
        # Check if both TPR and FPR are similar across groups
        tpr_values = [v['tpr'] for v in results.values()]
        fpr_values = [v['fpr'] for v in results.values()]
        
        tpr_diff = max(tpr_values) - min(tpr_values) if tpr_values else 0
        fpr_diff = max(fpr_values) - min(fpr_values) if fpr_values else 0
        
        max_diff = max(tpr_diff, fpr_diff)
        assessment = "Fair" if max_diff < 0.1 else "Warning" if max_diff < 0.2 else "Violation"
        
        return {
            'values': results,
            'visualization_type': 'scatter',
            'fairness_assessment': assessment,
            'tpr_difference': float(tpr_diff),
            'fpr_difference': float(fpr_diff)
        }
    
    def statistical_parity_difference(self) -> Dict[str, Any]:
        """Calculate statistical parity difference"""
        rates = []
        for group in self.groups:
            group_data = self._get_group_data(group)
            rate = group_data['shortlisted'].mean()
            rates.append(rate)
        
        if len(rates) >= 2:
            spd = rates[0] - rates[1]
        else:
            spd = 0
        
        assessment = "Fair" if abs(spd) < 0.1 else "Warning" if abs(spd) < 0.2 else "Violation"
        
        return {
            'value': float(spd),
            'visualization_type': 'metric',
            'fairness_assessment': assessment,
            'interpretation': 'Values close to 0 indicate fairness'
        }
    
    def average_odds_difference(self) -> Dict[str, Any]:
        """Calculate average odds difference"""
        if len(self.groups) < 2:
            return {
                'value': 0.0,
                'fairness_assessment': 'Insufficient groups',
                'visualization_type': 'metric'
            }
        
        # Get first two groups
        g1, g2 = list(self.groups)[:2]
        
        tn1, fp1, fn1, tp1 = self._get_confusion_matrix(g1)
        tn2, fp2, fn2, tp2 = self._get_confusion_matrix(g2)
        
        tpr1 = tp1 / (tp1 + fn1 + 1e-6)
        tpr2 = tp2 / (tp2 + fn2 + 1e-6)
        fpr1 = fp1 / (fp1 + tn1 + 1e-6)
        fpr2 = fp2 / (fp2 + tn2 + 1e-6)
        
        aod = ((tpr1 - tpr2) + (fpr1 - fpr2)) / 2
        
        assessment = "Fair" if abs(aod) < 0.1 else "Warning" if abs(aod) < 0.2 else "Violation"
        
        return {
            'value': float(aod),
            'tpr_diff': float(tpr1 - tpr2),
            'fpr_diff': float(fpr1 - fpr2),
            'visualization_type': 'metric',
            'fairness_assessment': assessment,
            'interpretation': 'Values close to 0 indicate fairness'
        }
    
    def theil_index(self) -> Dict[str, Any]:
        """Calculate Theil index - measures inequality (Streamlit formula)"""
        p = self.df['shortlisted']
        mean = p.mean()
        
        if mean == 0:
            theil = 0.0
        else:
            theil = np.mean((p / mean) * np.log((p + 1e-6) / mean))
        
        assessment = "Fair" if abs(theil) < 0.1 else "Warning" if abs(theil) < 0.2 else "Violation"
        
        return {
            'value': float(theil),
            'visualization_type': 'metric',
            'fairness_assessment': assessment,
            'interpretation': 'Values close to 0 indicate fairness'
        }
