# run_scraper.py
from library_scraper import LibraryScraper
import logging

def main():
    # Configure scraper
    scraper = LibraryScraper(
        start_url="https://www.library.northwestern.edu/",
        base_output_dir="library_data",
        delay=2.0,
        max_pages=1000,  # Start with a smaller number for testing
        user_agent="NULibraryInfoBot",
        email="opatka.ryan@email.com"
    )
    
    # Run scraper
    print("Starting library website scraping...")
    scraper.scrape()
    
    # Print statistics
    stats = scraper.get_scraping_stats()
    print("\nScraping completed!")
    print(f"Total pages scraped: {stats['total_pages']}")
    print("\nFiles by category:")
    for category, counts in stats['categories'].items():
        print(f"{category}:")
        print(f"  Raw files: {counts['raw']}")
        print(f"  Processed files: {counts['processed']}")

if __name__ == "__main__":
    main()