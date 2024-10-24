# run_analyzer.py
from analyzer import LibraryDataAnalyzer
import logging
from pathlib import Path

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize analyzer
    analyzer = LibraryDataAnalyzer(base_dir="library_data")
    
    # Run analysis
    logger.info("Starting library content analysis...")
    results = analyzer.run_analysis()
    
    # Print results
    print("\n=== Library Content Analysis Results ===")
    
    if results["success"]:
        analysis = results["analysis"]
        print("\nBasic Statistics:")
        print(f"Total Documents: {analysis['basic_stats']['total_documents']}")
        print("\nDocuments by Category:")
        for category, count in analysis['basic_stats']['categories'].items():
            print(f"  - {category}: {count}")
            
        content_analysis = analysis['content_analysis']
        
        if content_analysis.get('contact_info'):
            print(f"\nContact Information Found:")
            print(f"  Total contacts: {content_analysis['contact_info']['total_contacts']}")
            print(f"  Total emails: {content_analysis['contact_info']['total_emails']}")
            print(f"  Total phone numbers: {content_analysis['contact_info']['total_phones']}")
            
        if content_analysis.get('events_info'):
            print(f"\nEvents Information:")
            print(f"  Total events: {content_analysis['events_info']['total_events']}")
            
        if content_analysis.get('services_info'):
            print(f"\nServices Information:")
            print(f"  Total services: {content_analysis['services_info']['total_services']}")
            
    if results["errors"]:
        print("\nWarnings/Errors encountered:")
        for error in results["errors"]:
            print(f"  - {error}")
            
    print("\nOutput files:")
    if results["success"]:
        print("  - library_analysis.html")

if __name__ == "__main__":
    main()