import os
import json
import datetime
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QDateTime, QDate, QTime

class BellAnalytics(QObject):
    """Advanced analytics engine for bell system data visualization and insights"""
    
    # Signals
    analytics_updated = pyqtSignal(dict)
    
    def __init__(self, log_file="data/bell_logs.json", config_file="data/user_config.json"):
        super().__init__()
        self.log_file = log_file
        self.config_file = config_file
        self.logs = []
        self.stats = {}
        
        # Ensure log file exists
        self.initialize_log_file()
        
        # Load logs
        self.load_logs()
        
    def initialize_log_file(self):
        """Create log file if it doesn't exist"""
        if not os.path.exists(self.log_file):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'w') as f:
                json.dump([], f)
                
    def load_logs(self):
        """Load bell logs from file"""
        try:
            with open(self.log_file, 'r') as f:
                self.logs = json.load(f)
        except Exception as e:
            print(f"Error loading logs: {e}")
            self.logs = []
            
    def save_logs(self):
        """Save bell logs to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.logs, f, indent=4)
        except Exception as e:
            print(f"Error saving logs: {e}")
            
    def log_bell_event(self, bell, event_type="played", details=None):
        """Log a bell event with timestamp and details
        
        Args:
            bell: The bell object that triggered the event
            event_type: Type of event (played, missed, stopped, etc.)
            details: Additional details about the event
        """
        now = datetime.datetime.now()
        
        # Create log entry
        log_entry = {
            "timestamp": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "bell_name": bell.name,
            "bell_id": bell.id,
            "event_type": event_type,
            "category": bell.category,
            "details": details or {}
        }
        
        # Add to logs
        self.logs.append(log_entry)
        
        # Save logs
        self.save_logs()
        
        # Update statistics
        self.update_stats()
        
    def update_stats(self):
        """Update analytics statistics based on logs"""
        self.stats = {
            "total_events": len(self.logs),
            "events_today": 0,
            "events_this_week": 0,
            "events_this_month": 0,
            "most_frequent_bell": {"name": "", "count": 0},
            "category_distribution": {},
            "hourly_distribution": {f"{i:02d}": 0 for i in range(24)},
            "daily_distribution": {i: 0 for i in range(7)},  # 0 = Monday, 6 = Sunday
            "event_types": {}
        }
        
        # Get current date for comparisons
        now = datetime.datetime.now()
        today = now.date()
        
        # Calculate start of week (Monday)
        start_of_week = today - datetime.timedelta(days=today.weekday())
        
        # Calculate start of month
        start_of_month = today.replace(day=1)
        
        # Temporary counters
        bell_counts = {}
        category_counts = {}
        event_type_counts = {}
        
        # Process logs
        for log in self.logs:
            # Parse log date
            log_date = datetime.datetime.fromisoformat(log["timestamp"]).date()
            log_time = datetime.datetime.fromisoformat(log["timestamp"]).time()
            log_datetime = datetime.datetime.fromisoformat(log["timestamp"])
            
            # Count total events by period
            if log_date == today:
                self.stats["events_today"] += 1
                
            if log_date >= start_of_week:
                self.stats["events_this_week"] += 1
                
            if log_date >= start_of_month:
                self.stats["events_this_month"] += 1
                
            # Count by bell name
            bell_name = log["bell_name"]
            bell_counts[bell_name] = bell_counts.get(bell_name, 0) + 1
            
            # Count by category
            category = log["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count by hour
            hour = log_time.hour
            self.stats["hourly_distribution"][f"{hour:02d}"] += 1
            
            # Count by day of week
            day_of_week = log_datetime.weekday()  # 0 = Monday, 6 = Sunday
            self.stats["daily_distribution"][day_of_week] += 1
            
            # Count by event type
            event_type = log["event_type"]
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
            
        # Find most frequent bell
        most_frequent_bell = {"name": "", "count": 0}
        for bell_name, count in bell_counts.items():
            if count > most_frequent_bell["count"]:
                most_frequent_bell = {"name": bell_name, "count": count}
                
        self.stats["most_frequent_bell"] = most_frequent_bell
        
        # Set category distribution
        self.stats["category_distribution"] = category_counts
        
        # Set event types
        self.stats["event_types"] = event_type_counts
        
        # Emit signal with updated stats
        self.analytics_updated.emit(self.stats)
        
    def generate_daily_heatmap(self, output_path="data/heatmap.png"):
        """Generate a heatmap of bell activity by day and hour
        
        Returns:
            str: Path to the saved image
        """
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            
            # Create a 7x24 matrix for days vs hours
            heatmap_data = np.zeros((7, 24))
            
            # Fill with log data
            for log in self.logs:
                log_datetime = datetime.datetime.fromisoformat(log["timestamp"])
                day = log_datetime.weekday()  # 0 = Monday, 6 = Sunday
                hour = log_datetime.hour
                heatmap_data[day, hour] += 1
                
            # Create plot
            plt.figure(figsize=(12, 6))
            plt.imshow(heatmap_data, cmap='viridis', aspect='auto')
            plt.colorbar(label='Number of Bells')
            
            # Set labels
            plt.yticks(range(7), ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
            plt.xticks(range(0, 24, 2), [f"{i:02d}:00" for i in range(0, 24, 2)])
            plt.xlabel('Hour of Day')
            plt.ylabel('Day of Week')
            plt.title('Bell Activity Heatmap')
            
            # Save figure
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()
            
            return output_path
        except Exception as e:
            print(f"Error generating heatmap: {e}")
            return None
            
    def generate_category_pie_chart(self, output_path="data/categories_pie.png"):
        """Generate a pie chart of bell categories
        
        Returns:
            str: Path to the saved image
        """
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            
            # Get category data
            categories = list(self.stats["category_distribution"].keys())
            values = list(self.stats["category_distribution"].values())
            
            # Create plot
            plt.figure(figsize=(8, 8))
            plt.pie(values, labels=categories, autopct='%1.1f%%', startangle=90, 
                   shadow=True, explode=[0.05] * len(categories),
                   colors=plt.cm.Paired(np.linspace(0, 1, len(categories))))
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            plt.title('Bell Distribution by Category')
            
            # Save figure
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()
            
            return output_path
        except Exception as e:
            print(f"Error generating pie chart: {e}")
            return None
            
    def generate_hourly_bar_chart(self, output_path="data/hourly_bar.png"):
        """Generate a bar chart of hourly bell distribution
        
        Returns:
            str: Path to the saved image
        """
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            
            # Get hourly data
            hours = list(self.stats["hourly_distribution"].keys())
            counts = list(self.stats["hourly_distribution"].values())
            
            # Create plot
            plt.figure(figsize=(12, 6))
            plt.bar(hours, counts, color='skyblue')
            plt.xlabel('Hour of Day')
            plt.ylabel('Number of Bells')
            plt.title('Bell Distribution by Hour')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save figure
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()
            
            return output_path
        except Exception as e:
            print(f"Error generating bar chart: {e}")
            return None
            
    def export_analytics_report(self, output_path="data/analytics_report.html"):
        """Generate a complete analytics report as HTML
        
        Returns:
            str: Path to the HTML report
        """
        try:
            # Generate charts
            heatmap_path = self.generate_daily_heatmap()
            pie_chart_path = self.generate_category_pie_chart()
            bar_chart_path = self.generate_hourly_bar_chart()
            
            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>DPMMV Bells System Analytics Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                    h1, h2, h3 {{ color: #2c3e50; }}
                    .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                    .stats-card {{ background-color: #ecf0f1; border-radius: 5px; padding: 15px; margin-bottom: 20px; }}
                    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); grid-gap: 15px; }}
                    .stat-item {{ background-color: #3498db; color: white; padding: 15px; border-radius: 5px; text-align: center; }}
                    .stat-value {{ font-size: 24px; font-weight: bold; }}
                    .stat-label {{ font-size: 14px; }}
                    .chart-container {{ margin: 30px 0; }}
                    img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>DPMMV Bells System Analytics Report</h1>
                    <p>Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    
                    <div class="stats-card">
                        <h2>Summary Statistics</h2>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-value">{self.stats["total_events"]}</div>
                                <div class="stat-label">Total Bell Events</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{self.stats["events_today"]}</div>
                                <div class="stat-label">Bells Today</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{self.stats["events_this_week"]}</div>
                                <div class="stat-label">Bells This Week</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{self.stats["events_this_month"]}</div>
                                <div class="stat-label">Bells This Month</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="stats-card">
                        <h2>Most Frequent Bell</h2>
                        <p><strong>{self.stats["most_frequent_bell"]["name"]}</strong> 
                        with {self.stats["most_frequent_bell"]["count"]} activations</p>
                    </div>
                    
                    <div class="chart-container">
                        <h2>Bell Activity Heatmap</h2>
                        <p>Shows bell distribution across days and hours</p>
                        <img src="{os.path.basename(heatmap_path)}" alt="Bell Activity Heatmap">
                    </div>
                    
                    <div class="chart-container">
                        <h2>Category Distribution</h2>
                        <p>Breakdown of bells by category</p>
                        <img src="{os.path.basename(pie_chart_path)}" alt="Category Distribution">
                    </div>
                    
                    <div class="chart-container">
                        <h2>Hourly Distribution</h2>
                        <p>Bells per hour throughout the day</p>
                        <img src="{os.path.basename(bar_chart_path)}" alt="Hourly Distribution">
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Save HTML report
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(html_content)
                
            return output_path
        except Exception as e:
            print(f"Error generating analytics report: {e}")
            return None