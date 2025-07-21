#!/usr/bin/env python

import sys
import os
import json
import argparse
import datetime
from pathlib import Path

# Add the parent directory to the path so we can import the orchestration modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.query_feedback import QueryFeedback
from orchestration.query_feedback_analysis import QueryFeedbackAnalysis

def main():
    parser = argparse.ArgumentParser(description='Analyze failed queries and generate recommendations')
    parser.add_argument('--output', '-o', help='Output file for the report (default: stdout)')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='text',
                        help='Output format (default: text)')
    parser.add_argument('--feedback-file', help='Path to the feedback file (default: use the default path)')
    args = parser.parse_args()
    
    # Initialize the feedback system
    feedback_system = QueryFeedback(args.feedback_file) if args.feedback_file else QueryFeedback()
    
    # Create the analyzer
    analyzer = QueryFeedbackAnalysis(feedback_system)
    
    # Generate the report
    report = analyzer.generate_failure_report()
    
    if args.format == 'json':
        # Output as JSON
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to {args.output}")
        else:
            print(json.dumps(report, indent=2))
    else:
        # Output as formatted text
        text_report = format_report_as_text(report)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(text_report)
            print(f"Report saved to {args.output}")
        else:
            print(text_report)

def format_report_as_text(report):
    """Format the report as human-readable text."""
    lines = []
    lines.append("===== QUERY FAILURE ANALYSIS REPORT =====")
    lines.append(f"Generated on: {report.get('timestamp', datetime.datetime.now().isoformat())}")
    lines.append("")
    
    if 'status' in report:
        lines.append(f"Status: {report['status']}")
        return '\n'.join(lines)
    
    lines.append(f"Total Failed Queries: {report.get('total_failed_queries', 0)}")
    lines.append("")
    
    # Query patterns by type
    lines.append("=== QUERY PATTERNS BY TYPE ===")
    patterns = report.get('patterns_by_query_type', {})
    if not patterns:
        lines.append("No patterns identified.")
    else:
        for query_type, data in patterns.items():
            lines.append(f"\n== {query_type.upper()} ==")
            lines.append(f"Count: {data.get('count', 0)} ({data.get('percentage', 0):.1f}%)")
            
            lines.append("\nExamples:")
            for example in data.get('examples', []):
                lines.append(f"  - \"{example}\"")
            
            lines.append("\nCommon Errors:")
            for error in data.get('common_errors', []):
                lines.append(f"  - {error.get('error', '')} ({error.get('count', 0)} occurrences, {error.get('percentage', 0):.1f}%)")
    
    # Correction statistics
    lines.append("\n\n=== CORRECTION STATISTICS ===")
    corr_stats = report.get('correction_statistics', {})
    if 'status' in corr_stats:
        lines.append(f"Status: {corr_stats['status']}")
    else:
        lines.append(f"Total Corrections Applied: {corr_stats.get('total_corrections_applied', 0)}")
        lines.append(f"Successful Corrections: {corr_stats.get('successful_corrections', 0)}")
        lines.append(f"Failed Corrections: {corr_stats.get('failed_corrections', 0)}")
        lines.append(f"Overall Success Rate: {corr_stats.get('overall_success_rate', 0):.1f}%")
        
        lines.append("\nSuccessful Correction Examples:")
        for example in corr_stats.get('successful_examples', []):
            lines.append(f"  - Original: \"{example.get('original', '')}\"")
            lines.append(f"    Correction: \"{example.get('correction', '')}\"")
            lines.append(f"    Success Rate: {example.get('success_rate', 0):.1f}%")
    
    # Recommendations
    lines.append("\n\n=== RECOMMENDATIONS ===")
    for rec in report.get('recommendations', []):
        lines.append(f"  - {rec}")
    
    return '\n'.join(lines)

if __name__ == '__main__':
    main()
