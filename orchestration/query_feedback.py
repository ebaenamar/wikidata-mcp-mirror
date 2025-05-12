import json
import os
import time
import datetime
from typing import Dict, Any, List, Optional

class QueryFeedback:
    def __init__(self, feedback_file: str = None):
        self.feedback_file = feedback_file or os.path.join(
            os.path.dirname(__file__), "query_feedback.json"
        )
        self.feedback_data = self._load_feedback()
        
    def _load_feedback(self) -> Dict[str, Any]:
        """
        Load feedback data from file or initialize if it doesn't exist.
        """
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, "r") as f:
                    return json.load(f)
            except:
                return self._initialize_feedback()
        return self._initialize_feedback()
    
    def _initialize_feedback(self) -> Dict[str, Any]:
        """
        Initialize the feedback data structure.
        """
        return {
            "failed_queries": {},  # Store patterns of failed queries
            "correction_patterns": {},  # Store successful corrections
            "query_clusters": {},  # Group similar queries
            "last_update": time.time()
        }
    
    def _save_feedback(self) -> None:
        """
        Save feedback data to file.
        """
        with open(self.feedback_file, "w") as f:
            json.dump(self.feedback_data, f)
    
    def register_failed_query(self, query_text: str, error_message: str, query_type: str = "unknown") -> None:
        """
        Register a failed query to learn from it.
        
        Args:
            query_text: The natural language query that failed
            error_message: The error message returned
            query_type: The detected query type if available
        """
        query_hash = str(hash(query_text))
        
        # Initialize if this query hasn't failed before
        if query_hash not in self.feedback_data["failed_queries"]:
            self.feedback_data["failed_queries"][query_hash] = {
                "query": query_text,
                "failures": 0,
                "last_failure": time.time(),
                "error_messages": [],
                "query_types": [],
                "similar_patterns": []
            }
        
        # Update the failure data
        entry = self.feedback_data["failed_queries"][query_hash]
        entry["failures"] += 1
        entry["last_failure"] = time.time()
        
        if error_message not in entry["error_messages"]:
            entry["error_messages"].append(error_message)
        
        # Use list instead of set for JSON serialization
        if query_type not in entry["query_types"]:
            entry["query_types"].append(query_type)
        
        # Analyze the query for patterns
        self._analyze_query_patterns(query_text, query_hash)
        
        # Save the updated feedback data
        self._save_feedback()
    
    def register_correction(self, failed_query: str, corrected_query: str, success: bool) -> None:
        """
        Register a correction for a previously failed query.
        
        Args:
            failed_query: The original query that failed
            corrected_query: The corrected query
            success: Whether the correction was successful
        """
        failed_hash = str(hash(failed_query))
        corrected_hash = str(hash(corrected_query))
        
        if failed_hash not in self.feedback_data["correction_patterns"]:
            self.feedback_data["correction_patterns"][failed_hash] = {
                "original_query": failed_query,
                "corrections": {}
            }
        
        if corrected_hash not in self.feedback_data["correction_patterns"][failed_hash]["corrections"]:
            self.feedback_data["correction_patterns"][failed_hash]["corrections"][corrected_hash] = {
                "corrected_query": corrected_query,
                "success_count": 0,
                "failure_count": 0,
                "last_used": time.time()
            }
        
        # Update the correction statistics
        correction = self.feedback_data["correction_patterns"][failed_hash]["corrections"][corrected_hash]
        if success:
            correction["success_count"] += 1
        else:
            correction["failure_count"] += 1
        
        correction["last_used"] = time.time()
        
        # Save the updated feedback data
        self._save_feedback()
    
    def get_suggested_correction(self, query_text: str) -> Optional[str]:
        """
        Get a suggested correction for a query based on past corrections.
        
        Args:
            query_text: The query to find corrections for
            
        Returns:
            A suggested correction if available, None otherwise
        """
        query_hash = str(hash(query_text))
        
        # Check if we have corrections for this query
        if query_hash in self.feedback_data["correction_patterns"]:
            corrections = self.feedback_data["correction_patterns"][query_hash]["corrections"]
            
            # Find the most successful correction
            best_correction = None
            best_score = -1
            
            for corr_hash, corr_data in corrections.items():
                # Calculate a score based on success rate and recency
                total = corr_data["success_count"] + corr_data["failure_count"]
                if total == 0:
                    continue
                    
                success_rate = corr_data["success_count"] / total
                recency_factor = 1.0 / (1.0 + (time.time() - corr_data["last_used"]) / 86400)  # Days
                score = success_rate * 0.7 + recency_factor * 0.3
                
                if score > best_score:
                    best_score = score
                    best_correction = corr_data["corrected_query"]
            
            return best_correction
        
        # Check if there are similar patterns
        similar_queries = self._find_similar_queries(query_text)
        for similar in similar_queries:
            similar_hash = str(hash(similar))
            if similar_hash in self.feedback_data["correction_patterns"]:
                # Use the same logic as above to find the best correction
                corrections = self.feedback_data["correction_patterns"][similar_hash]["corrections"]
                best_correction = None
                best_score = -1
                
                for corr_hash, corr_data in corrections.items():
                    total = corr_data["success_count"] + corr_data["failure_count"]
                    if total == 0:
                        continue
                        
                    success_rate = corr_data["success_count"] / total
                    recency_factor = 1.0 / (1.0 + (time.time() - corr_data["last_used"]) / 86400)
                    score = success_rate * 0.7 + recency_factor * 0.3
                    
                    if score > best_score:
                        best_score = score
                        best_correction = corr_data["corrected_query"]
                
                if best_correction:
                    # Adapt the correction to the current query
                    return self._adapt_correction(query_text, similar, best_correction)
        
        return None
    
    def _analyze_query_patterns(self, query_text: str, query_hash: str) -> None:
        """
        Analyze patterns in a failed query to identify common issues.
        """
        # Simple pattern extraction - in a real system, this would use more advanced NLP
        words = query_text.lower().split()
        
        # Check for common temporal patterns
        temporal_patterns = ["last", "current", "recent", "today", "now", "latest"]
        has_temporal = any(word in temporal_patterns for word in words)
        
        # Check for entity patterns (simplified)
        if has_temporal:
            pattern_type = "temporal_query"
        else:
            pattern_type = "generic_query"
        
        # Add to query clusters
        if pattern_type not in self.feedback_data["query_clusters"]:
            self.feedback_data["query_clusters"][pattern_type] = []
            
        if query_hash not in self.feedback_data["query_clusters"][pattern_type]:
            self.feedback_data["query_clusters"][pattern_type].append(query_hash)
    
    def _find_similar_queries(self, query_text: str) -> List[str]:
        """
        Find queries similar to the given query based on patterns.
        """
        # This is a simplified implementation - in a real system, use more advanced similarity metrics
        similar_queries = []
        words = set(query_text.lower().split())
        
        # Check all failed queries for similarity
        for query_hash, query_data in self.feedback_data["failed_queries"].items():
            other_query = query_data["query"]
            other_words = set(other_query.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(words.intersection(other_words))
            union = len(words.union(other_words))
            
            if union > 0 and intersection / union > 0.5:  # Threshold for similarity
                similar_queries.append(other_query)
        
        return similar_queries
    
    def _adapt_correction(self, original_query: str, similar_query: str, correction: str) -> str:
        """
        Adapt a correction from a similar query to the current query.
        """
        # This is a simplified implementation - in a real system, use more advanced adaptation
        # For now, just replace the similar query terms with the original query terms
        orig_words = original_query.split()
        similar_words = similar_query.split()
        corr_words = correction.split()
        
        # Find unique words in the original query
        unique_orig = [w for w in orig_words if w not in similar_words]
        
        # Find unique words in the similar query that were replaced in the correction
        unique_similar = [w for w in similar_words if w not in orig_words]
        
        # Create a mapping from similar query words to original query words
        mapping = {}
        for i, word in enumerate(unique_similar):
            if i < len(unique_orig):
                mapping[word] = unique_orig[i]
        
        # Apply the mapping to the correction
        adapted_correction = correction
        for old_word, new_word in mapping.items():
            adapted_correction = adapted_correction.replace(old_word, new_word)
        
        return adapted_correction
    
    def get_common_failure_patterns(self) -> Dict[str, Any]:
        """
        Analyze and return common patterns in failed queries.
        """
        patterns = {}
        
        # Analyze temporal queries
        if "temporal_query" in self.feedback_data["query_clusters"]:
            temporal_failures = self.feedback_data["query_clusters"]["temporal_query"]
            if temporal_failures:
                patterns["temporal_queries"] = {
                    "count": len(temporal_failures),
                    "examples": [self.feedback_data["failed_queries"][hash_id]["query"] 
                                for hash_id in temporal_failures[:5]],
                    "common_errors": self._extract_common_errors(temporal_failures)
                }
        
        # Similar analysis for other query types
        # ...
        
        return patterns
    
    def _extract_common_errors(self, query_hashes: List[str]) -> List[str]:
        """
        Extract common error messages from a list of query hashes.
        """
        error_counts = {}
        
        for query_hash in query_hashes:
            if query_hash in self.feedback_data["failed_queries"]:
                for error in self.feedback_data["failed_queries"][query_hash]["error_messages"]:
                    if error not in error_counts:
                        error_counts[error] = 0
                    error_counts[error] += 1
        
        # Sort by frequency
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return [error for error, count in sorted_errors[:5]]  # Return top 5 errors
