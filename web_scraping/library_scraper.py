import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import time
import json
from pathlib import Path
import logging
from typing import Set, Dict, List, Optional
from datetime import datetime

class LibraryScraper:
    def __init__(
        self,
        start_url: str,
        base_output_dir: str,
        delay: float = 1.0,
        max_pages: int = 500,
        user_agent: str = "LibraryInfoBot",
        email: str = "your@email.com"
    ):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.base_output_dir = Path(base_output_dir)
        self.delay = delay
        self.max_pages = max_pages
        self.user_agent = user_agent
        self.email = email
        
        # Use lists instead of sets for better URL management
        self.visited_urls: Set[str] = set()
        self.queue: List[str] = [start_url]  # Changed to list for FIFO behavior
        self.found_urls: Set[str] = set()  # Track all discovered URLs
        
        # Setup
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = self.base_output_dir / self.domain / self.timestamp
        self.setup_directories()
        self.setup_logging()
        
    def setup_directories(self):
        """Create directory structure"""
        categories = ['contact', 'hours', 'events', 'services', 'general']
        
        for category in categories:
            (self.output_dir / 'raw' / category).mkdir(parents=True, exist_ok=True)
            (self.output_dir / 'processed' / category).mkdir(parents=True, exist_ok=True)
            
        (self.output_dir / 'logs').mkdir(parents=True, exist_ok=True)
        
    def setup_logging(self):
        """Configure logging"""
        log_file = self.output_dir / 'logs' / 'scraping.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def get_page(self, url: str) -> Optional[requests.Response]:
        """Fetch a page"""
        try:
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
            
    def extract_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract page content"""
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style']):
            element.decompose()
            
        # Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        if not main_content:
            return None
            
        content = ' '.join(p.get_text().strip() for p in main_content.find_all('p'))
        
        return {
            'url': url,
            'title': soup.title.string if soup.title else '',
            'content': content,
            'timestamp': time.time()
        }
        
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract valid links more thoroughly"""
        new_links = []
        seen_on_page = set()  # Track unique links on this page
        
        # Find all <a> tags
        for link in soup.find_all(['a', 'area']):  # Include image map links
            href = link.get('href')
            if not href:
                continue
                
            try:
                url = urljoin(base_url, href)
                parsed = urlparse(url)
                
                # Skip invalid URLs and non-HTTP(S) schemes
                if not parsed.netloc or not parsed.scheme in {'http', 'https'}:
                    continue
                    
                # Only process URLs from the same domain
                if parsed.netloc != self.domain:
                    continue
                    
                # Skip common non-content URLs
                if any(pat in parsed.path.lower() for pat in ['.pdf', '.jpg', '.png', '.gif', '.css', '.js']):
                    continue
                    
                # Normalize URL
                normalized_url = url.split('#')[0].split('?')[0].rstrip('/')
                
                # Only add if we haven't seen this URL before
                if (normalized_url not in seen_on_page and 
                    normalized_url not in self.visited_urls and 
                    normalized_url not in self.found_urls):
                    seen_on_page.add(normalized_url)
                    new_links.append(normalized_url)
                    self.found_urls.add(normalized_url)
                    
            except Exception as e:
                self.logger.warning(f"Error processing link {href}: {e}")
                
        return new_links
        
    def save_content(self, content: Dict):
        """Save content to file"""
        if not content:
            return
            
        # Save to general category for now
        filename = f"{hash(content['url'])}.json"
        output_path = self.output_dir / 'raw' / 'general' / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
            
    def scrape(self):
        """Main scraping logic with exhaustive link processing"""
        self.start_time = time.time()
        
        while self.queue and len(self.visited_urls) < self.max_pages:
            # Get next URL from start of queue (FIFO)
            url = self.queue.pop(0)
            
            if url in self.visited_urls:
                continue
                
            self.logger.info(f"Scraping: {url} (Queue size: {len(self.queue)}, Visited: {len(self.visited_urls)})")
            
            response = self.get_page(url)
            if not response:
                continue
                
            self.visited_urls.add(url)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            content = self.extract_content(soup, url)
            
            if content:
                self.save_content(content)
                
            # Get new links and add them to the end of the queue
            new_links = self.extract_links(soup, url)
            self.queue.extend(new_links)
            
            # Log progress
            if len(self.visited_urls) % 10 == 0:
                self.logger.info(f"Progress: {len(self.visited_urls)} pages visited, {len(self.queue)} URLs in queue")
                
            time.sleep(self.delay)
            
        self.logger.info(f"Scraping completed. Processed {len(self.visited_urls)} pages.")
        self.logger.info(f"Total unique URLs found: {len(self.found_urls)}")
        
    def get_scraping_stats(self) -> Dict:
        """Get scraping statistics"""
        stats = {
            'total_pages_visited': len(self.visited_urls),
            'total_urls_found': len(self.found_urls),
            'urls_remaining': len(self.queue),
            'start_time': getattr(self, 'start_time', time.time()),
            'end_time': time.time(),
            'domain': self.domain,
            'categories': {}
        }
        
        for category in ['general', 'contact', 'hours', 'events', 'services']:
            raw_path = self.output_dir / 'raw' / category
            processed_path = self.output_dir / 'processed' / category
            
            stats['categories'][category] = {
                'raw': len(list(raw_path.glob('*.json'))),
                'processed': len(list(processed_path.glob('*.json')))
            }
            
        return stats