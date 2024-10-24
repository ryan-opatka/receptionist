# data_analyzer.py
import json
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import logging
import re

class LibraryDataAnalyzer:
    def __init__(self, base_dir: str):
        """Initialize the analyzer with library-specific settings"""
        self.base_dir = Path(base_dir)
        self.data = []
        self.metadata = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Categories we expect to find
        self.categories = [
            'contact', 
            'hours', 
            'events', 
            'services', 
            'general'
        ]
        
    def load_data(self) -> bool:
        """Load library data from the directory structure"""
        try:
            # Find the most recent data directory
            if not self.base_dir.exists():
                self.logger.error(f"Directory not found: {self.base_dir}")
                return False
            
            # Look for domain directories
            domain_dirs = [d for d in self.base_dir.iterdir() if d.is_dir()]
            if not domain_dirs:
                self.logger.error(f"No domain directories found in {self.base_dir}")
                return False
                
            # Use the first domain directory
            domain_dir = domain_dirs[0]
            
            # Find the most recent timestamp directory
            timestamp_dirs = [d for d in domain_dir.iterdir() if d.is_dir()]
            if not timestamp_dirs:
                self.logger.error(f"No timestamp directories found in {domain_dir}")
                return False
                
            latest_dir = max(timestamp_dirs, key=lambda x: x.stat().st_mtime)
            self.base_dir = latest_dir
            self.logger.info(f"Using data directory: {latest_dir}")
            
            # Load data from each category
            files_found = False
            for category in self.categories:
                category_dir = self.base_dir / 'raw' / category
                if category_dir.exists():
                    for file in category_dir.glob('*.json'):
                        files_found = True
                        try:
                            with open(file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                data['category'] = category
                                data['filename'] = file.name
                                self.data.append(data)
                        except Exception as e:
                            self.logger.error(f"Error loading {file}: {e}")
                            
            if not files_found:
                self.logger.error(f"No data files found in {self.base_dir}")
                return False
                
            self.logger.info(f"Successfully loaded {len(self.data)} documents")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during data loading: {e}")
            return False
            
    def analyze_library_data(self) -> Dict[str, Any]:
        """Analyze library-specific content"""
        analysis = {
            'total_documents': len(self.data),
            'categories': Counter(doc['category'] for doc in self.data),
            'contact_info': self.analyze_contacts(),
            'hours_info': self.analyze_hours(),
            'events_info': self.analyze_events(),
            'services_info': self.analyze_services(),
            'common_topics': self.analyze_topics()
        }
        return analysis
        
    def analyze_contacts(self) -> Dict[str, Any]:
        """Analyze contact information"""
        contacts = []
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
        
        for doc in self.data:
            content = doc.get('content', '')
            emails = re.findall(email_pattern, content)
            phones = re.findall(phone_pattern, content)
            
            if emails or phones:
                contacts.append({
                    'url': doc['url'],
                    'emails': emails,
                    'phones': phones
                })
                
        return {
            'total_contacts': len(contacts),
            'contacts': contacts[:10],  # Return first 10 contacts
            'total_emails': sum(len(c['emails']) for c in contacts),
            'total_phones': sum(len(c['phones']) for c in contacts)
        }
        
    def analyze_hours(self) -> Dict[str, Any]:
        """Analyze library hours information"""
        hours_info = []
        
        for doc in self.data:
            content = doc.get('content', '').lower()
            if any(term in content for term in ['hours', 'schedule', 'open', 'closed']):
                # Look for time patterns
                time_pattern = r'\b\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)\b'
                times = re.findall(time_pattern, content)
                
                if times:
                    hours_info.append({
                        'url': doc['url'],
                        'times_found': times
                    })
                    
        return {
            'total_hours_pages': len(hours_info),
            'hours_info': hours_info[:5]  # Return first 5 hours entries
        }
        
    def analyze_events(self) -> Dict[str, Any]:
        """Analyze event information"""
        events = []
        
        for doc in self.data:
            content = doc.get('content', '')
            if 'event' in content.lower():
                # Look for date patterns
                date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}(?:st|nd|rd|th)?,? \d{4}\b'
                dates = re.findall(date_pattern, content)
                
                if dates:
                    events.append({
                        'url': doc['url'],
                        'title': doc.get('title', ''),
                        'dates': dates
                    })
                    
        return {
            'total_events': len(events),
            'events': events[:10]  # Return first 10 events
        }
        
    def analyze_services(self) -> Dict[str, Any]:
        """Analyze service information"""
        services = []
        service_keywords = ['service', 'help', 'assistance', 'support', 'resource']
        
        for doc in self.data:
            content = doc.get('content', '').lower()
            if any(keyword in content for keyword in service_keywords):
                services.append({
                    'url': doc['url'],
                    'title': doc.get('title', ''),
                    'content_preview': content[:200] + '...'
                })
                
        return {
            'total_services': len(services),
            'services': services[:10]  # Return first 10 services
        }
        
    def analyze_topics(self) -> Dict[str, List[str]]:
        """Analyze common topics in the content"""
        # Combine all content
        all_content = ' '.join(doc.get('content', '') for doc in self.data)
        
        # Tokenize and clean
        tokens = word_tokenize(all_content.lower())
        # Remove stopwords and short words
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word.isalnum() and len(word) > 3 and word not in stop_words]
        
        # Get most common words
        return {
            'common_terms': [word for word, _ in Counter(tokens).most_common(20)]
        }
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        if not self.data:
            return {"error": "No data loaded"}
            
        return {
            "basic_stats": {
                "total_documents": len(self.data),
                "categories": Counter(doc['category'] for doc in self.data),
                "unique_urls": len(set(doc['url'] for doc in self.data))
            },
            "content_analysis": self.analyze_library_data()
        }
        
    def run_analysis(self) -> Dict[str, Any]:
        """Run complete analysis process"""
        results = {
            "success": False,
            "errors": [],
            "data_loaded": False,
            "analysis": None
        }
        
        # Load data
        if not self.load_data():
            results["errors"].append("Failed to load data")
            return results
            
        results["data_loaded"] = True
        
        try:
            results["analysis"] = self.generate_report()
            results["success"] = True
        except Exception as e:
            results["errors"].append(f"Error generating report: {str(e)}")
            
        return results

    def export_summary(self, output_file: str = 'library_analysis.html'):
        """Export analysis to HTML"""
        if not self.data:
            self.logger.error("No data to export")
            return
            
        analysis = self.generate_report()
        
        # Create HTML summary
        html_content = f"""
        <html>
        <head>
            <title>Library Website Analysis</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            </style>
        </head>
        <body>
            <h1>Library Website Analysis Summary</h1>
            
            <div class="section">
                <h2>Overview</h2>
                <p>Total Documents: {analysis['basic_stats']['total_documents']}</p>
                <p>Unique URLs: {analysis['basic_stats']['unique_urls']}</p>
            </div>
            
            <div class="section">
                <h2>Categories</h2>
                <table>
                    <tr><th>Category</th><th>Count</th></tr>
        """
        
        for category, count in analysis['basic_stats']['categories'].items():
            html_content += f"<tr><td>{category}</td><td>{count}</td></tr>"
            
        html_content += """
                </table>
            </div>
        </body>
        </html>
        """
        
        output_path = self.base_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)