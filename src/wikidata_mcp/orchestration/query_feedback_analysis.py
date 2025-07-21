import json
import os
import datetime
from typing import Dict, Any, List
from .query_feedback import QueryFeedback

class QueryFeedbackAnalysis:
    def __init__(self, feedback_system: QueryFeedback = None):
        self.feedback_system = feedback_system or QueryFeedback()
        
    def generate_failure_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report of query failures and patterns.
        
        Returns:
            A dictionary containing failure statistics and patterns
        """
        feedback_data = self.feedback_system.feedback_data
        
        # Basic statistics
        total_failures = len(feedback_data["failed_queries"])
        if total_failures == 0:
            return {"status": "No failed queries recorded"}
        
        # Get patterns by query type
        patterns_by_type = {}
        for query_type, query_hashes in feedback_data["query_clusters"].items():
            if query_hashes:
                patterns_by_type[query_type] = {
                    "count": len(query_hashes),
                    "percentage": (len(query_hashes) / total_failures) * 100,
                    "examples": [feedback_data["failed_queries"][qh]["query"] 
                                for qh in query_hashes[:5] if qh in feedback_data["failed_queries"]],
                    "common_errors": self._get_common_errors(query_hashes)
                }
        
        # Get correction success rates
        correction_stats = self._analyze_corrections(feedback_data["correction_patterns"])
        
        # Compile the report
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_failed_queries": total_failures,
            "patterns_by_query_type": patterns_by_type,
            "correction_statistics": correction_stats,
            "recommendations": self._generate_recommendations(patterns_by_type, correction_stats)
        }
        
        return report
    
    def _get_common_errors(self, query_hashes: List[str]) -> List[Dict[str, Any]]:
        """
        Get common error messages for a set of query hashes.
        """
        error_counts = {}
        feedback_data = self.feedback_system.feedback_data
        
        for qh in query_hashes:
            if qh in feedback_data["failed_queries"]:
                for error in feedback_data["failed_queries"][qh]["error_messages"]:
                    if error not in error_counts:
                        error_counts[error] = 0
                    error_counts[error] += 1
        
        # Sort by frequency
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return [{
            "error": error,
            "count": count,
            "percentage": (count / len(query_hashes)) * 100
        } for error, count in sorted_errors[:5]]
    
    def _analyze_corrections(self, correction_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the success of query corrections.
        """
        if not correction_patterns:
            return {"status": "No corrections recorded"}
        
        total_corrections = 0
        successful_corrections = 0
        failed_corrections = 0
        correction_examples = []
        
        for query_hash, data in correction_patterns.items():
            for corr_hash, corr_data in data["corrections"].items():
                success = corr_data["success_count"]
                failure = corr_data["failure_count"]
                total = success + failure
                
                if total > 0:
                    total_corrections += total
                    successful_corrections += success
                    failed_corrections += failure
                    
                    # Add example if it has a good success rate
                    if success / total > 0.7 and len(correction_examples) < 5:
                        correction_examples.append({
                            "original": data["original_query"],
                            "correction": corr_data["corrected_query"],
                            "success_rate": (success / total) * 100
                        })
        
        if total_corrections == 0:
            return {"status": "No corrections applied yet"}
        
        return {
            "total_corrections_applied": total_corrections,
            "successful_corrections": successful_corrections,
            "failed_corrections": failed_corrections,
            "overall_success_rate": (successful_corrections / total_corrections) * 100 if total_corrections > 0 else 0,
            "successful_examples": correction_examples
        }
    
    def _generate_recommendations(self, patterns_by_type: Dict[str, Any], 
                                correction_stats: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations for improving the query handling system.
        """
        recommendations = []
        
        # Check if there are many temporal query failures
        if "temporal_query" in patterns_by_type and patterns_by_type["temporal_query"]["percentage"] > 30:
            recommendations.append("Consider improving the temporal query handling, as it represents a significant portion of failures.")
            
            # Check common errors in temporal queries
            common_errors = patterns_by_type["temporal_query"].get("common_errors", [])
            for error_data in common_errors:
                if "date" in error_data["error"].lower() or "time" in error_data["error"].lower():
                    recommendations.append("Improve date parsing and handling in temporal queries.")
                    break
        
        # Check correction success rate
        if isinstance(correction_stats, dict) and "overall_success_rate" in correction_stats:
            success_rate = correction_stats["overall_success_rate"]
            if success_rate < 50:
                recommendations.append("The query correction system has a low success rate. Consider refining the correction algorithms.")
            elif success_rate > 80:
                recommendations.append("The query correction system is performing well. Consider expanding it to handle more types of queries.")
        
        # If no specific recommendations, add a general one
        if not recommendations:
            recommendations.append("Continue monitoring query patterns for more specific recommendations.")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """
        Save the analysis report to a file.
        
        Args:
            report: The report to save
            filename: Optional filename (defaults to a timestamped file)
            
        Returns:
            The path to the saved report file
        """
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"query_failure_report_{timestamp}.json"
        
        report_dir = os.path.join(os.path.dirname(__file__), "reports")
        os.makedirs(report_dir, exist_ok=True)
        
        report_path = os.path.join(report_dir, filename)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return report_path
