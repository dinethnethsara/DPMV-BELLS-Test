from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QTabWidget, QSplitter, QGroupBox, QGridLayout,
    QComboBox, QDateEdit, QSpinBox, QListWidget, QProgressBar,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QDateTime, QDate, QTimer
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette
import os
import matplotlib.pyplot as plt
import numpy as np
import datetime

class StatCard(QFrame):
    """A card displaying a single statistic with a title and value"""
    
    def __init__(self, title, value, color="#00a0ff", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            background-color: #1e1e2e;
            border-radius: 10px;
            border: 1px solid {color}40;
        """)
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Add title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"""
            font-size: 14px;
            color: {color};
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # Add value
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
        """)
        self.value_label.setAlignment(Qt.AlignCenter)
        
        # Add to layout
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.value_label)
        
    def update_value(self, value):
        """Update the displayed value"""
        self.value_label.setText(str(value))


class ChartWidget(QFrame):
    """Widget to display a chart image"""
    
    def __init__(self, title, image_path=None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 10px;
            border: 1px solid #353550;
        """)
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Add title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #00a0ff;
        """)
        
        # Add image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(200)
        
        # Add refresh button
        self.refresh_button = QPushButton("↻ Refresh")
        self.refresh_button.setStyleSheet("""
            background-color: #2d2d40;
            color: white;
            border-radius: 5px;
            padding: 5px 10px;
            max-width: 100px;
        """)
        
        # Add to layout
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.refresh_button, 0, Qt.AlignRight)
        
        # Set image if provided
        if image_path and os.path.exists(image_path):
            self.update_image(image_path)
        
    def update_image(self, image_path):
        """Update the chart image"""
        if not os.path.exists(image_path):
            self.image_label.setText("Image not found")
            return
            
        pixmap = QPixmap(image_path)
        
        # Scale to fit while maintaining aspect ratio
        pixmap = pixmap.scaled(
            self.image_label.width(), self.image_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(pixmap)
        
    def resizeEvent(self, event):
        """Handle resize to scale the image"""
        super().resizeEvent(event)
        
        # Re-scale the image if there is one
        if not self.image_label.pixmap().isNull():
            pixmap = self.image_label.pixmap()
            scaled_pixmap = pixmap.scaled(
                self.image_label.width(), self.image_label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)


class AnalyticsDashboard(QWidget):
    """Advanced analytics dashboard widget"""
    
    def __init__(self, bell_scheduler=None, analytics_engine=None, parent=None):
        super().__init__(parent)
        self.bell_scheduler = bell_scheduler
        self.analytics_engine = analytics_engine
        
        # Set up the UI
        self.setup_ui()
        
        # Update charts
        self.update_analytics()
        
    def setup_ui(self):
        """Set up the dashboard UI"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # Add title
        self.title_label = QLabel("Bell Analytics Dashboard")
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
        """)
        
        # Add date range selector
        self.date_range_layout = QHBoxLayout()
        
        self.date_label = QLabel("Date Range:")
        self.date_label.setStyleSheet("color: white;")
        
        self.range_combo = QComboBox()
        self.range_combo.addItems([
            "Today", "Yesterday", "Last 7 Days", "Last 30 Days", "This Month", "Custom"
        ])
        self.range_combo.setStyleSheet("""
            background-color: #2d2d40;
            color: white;
            padding: 5px;
            border-radius: 5px;
        """)
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("""
            background-color: #2d2d40;
            color: white;
            padding: 5px;
            border-radius: 5px;
        """)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("""
            background-color: #2d2d40;
            color: white;
            padding: 5px;
            border-radius: 5px;
        """)
        
        self.update_button = QPushButton("Update")
        self.update_button.setStyleSheet("""
            background-color: #00a0ff;
            color: white;
            border-radius: 5px;
            padding: 5px 10px;
        """)
        self.update_button.clicked.connect(self.update_analytics)
        
        self.export_button = QPushButton("Export Report")
        self.export_button.setStyleSheet("""
            background-color: #00ff99;
            color: black;
            border-radius: 5px;
            padding: 5px 10px;
        """)
        self.export_button.clicked.connect(self.export_report)
        
        # Add to date range layout
        self.date_range_layout.addWidget(self.date_label)
        self.date_range_layout.addWidget(self.range_combo)
        self.date_range_layout.addWidget(self.start_date)
        self.date_range_layout.addWidget(self.end_date)
        self.date_range_layout.addWidget(self.update_button)
        self.date_range_layout.addWidget(self.export_button)
        self.date_range_layout.addStretch()
        
        # Create stats row
        self.stats_layout = QHBoxLayout()
        
        # Add stat cards
        self.total_bells_card = StatCard("Total Bells", "0")
        self.today_bells_card = StatCard("Today's Bells", "0", "#00ff99")
        self.week_bells_card = StatCard("This Week", "0", "#ffaa00")
        self.most_used_card = StatCard("Most Frequent", "None", "#ff5500")
        
        # Add to stats layout
        self.stats_layout.addWidget(self.total_bells_card)
        self.stats_layout.addWidget(self.today_bells_card)
        self.stats_layout.addWidget(self.week_bells_card)
        self.stats_layout.addWidget(self.most_used_card)
        
        # Create tabs for different charts
        self.charts_tabs = QTabWidget()
        self.charts_tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: #1a1a2a;
                border: 1px solid #353550;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #252535;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #353550;
            }
        """)
        
        # Add chart tabs
        self.add_heatmap_tab()
        self.add_category_tab()
        self.add_hourly_tab()
        
        # Add all components to main layout
        self.layout.addWidget(self.title_label)
        self.layout.addLayout(self.date_range_layout)
        self.layout.addLayout(self.stats_layout)
        self.layout.addWidget(self.charts_tabs)
        
    def add_heatmap_tab(self):
        """Add the heatmap tab"""
        self.heatmap_tab = QWidget()
        self.heatmap_layout = QVBoxLayout(self.heatmap_tab)
        
        # Create heatmap widget
        self.heatmap_widget = ChartWidget("Bell Activity Heatmap")
        self.heatmap_widget.refresh_button.clicked.connect(self.update_heatmap)
        
        # Add to layout
        self.heatmap_layout.addWidget(self.heatmap_widget)
        
        # Add to tabs
        self.charts_tabs.addTab(self.heatmap_tab, "Activity Heatmap")
        
    def add_category_tab(self):
        """Add the category distribution tab"""
        self.category_tab = QWidget()
        self.category_layout = QVBoxLayout(self.category_tab)
        
        # Create category widget
        self.category_widget = ChartWidget("Category Distribution")
        self.category_widget.refresh_button.clicked.connect(self.update_category_chart)
        
        # Add to layout
        self.category_layout.addWidget(self.category_widget)
        
        # Add to tabs
        self.charts_tabs.addTab(self.category_tab, "Categories")
        
    def add_hourly_tab(self):
        """Add the hourly distribution tab"""
        self.hourly_tab = QWidget()
        self.hourly_layout = QVBoxLayout(self.hourly_tab)
        
        # Create hourly widget
        self.hourly_widget = ChartWidget("Hourly Bell Distribution")
        self.hourly_widget.refresh_button.clicked.connect(self.update_hourly_chart)
        
        # Add to layout
        self.hourly_layout.addWidget(self.hourly_widget)
        
        # Add to tabs
        self.charts_tabs.addTab(self.hourly_tab, "Hourly Distribution")
        
    def update_analytics(self):
        """Update all analytics charts and stats"""
        if not self.analytics_engine:
            return
            
        # Update the analytics engine
        self.analytics_engine.update_stats()
        
        # Get the stats
        stats = self.analytics_engine.stats
        
        # Update stat cards
        self.total_bells_card.update_value(stats["total_events"])
        self.today_bells_card.update_value(stats["events_today"])
        self.week_bells_card.update_value(stats["events_this_week"])
        
        # Update most frequent bell
        if stats["most_frequent_bell"]["name"]:
            self.most_used_card.update_value(stats["most_frequent_bell"]["name"])
        else:
            self.most_used_card.update_value("None")
            
        # Update charts
        self.update_heatmap()
        self.update_category_chart()
        self.update_hourly_chart()
        
    def update_heatmap(self):
        """Update the heatmap chart"""
        if not self.analytics_engine:
            return
            
        # Generate heatmap
        heatmap_path = self.analytics_engine.generate_daily_heatmap()
        
        # Update widget
        if heatmap_path and os.path.exists(heatmap_path):
            self.heatmap_widget.update_image(heatmap_path)
            
    def update_category_chart(self):
        """Update the category distribution chart"""
        if not self.analytics_engine:
            return
            
        # Generate chart
        chart_path = self.analytics_engine.generate_category_pie_chart()
        
        # Update widget
        if chart_path and os.path.exists(chart_path):
            self.category_widget.update_image(chart_path)
            
    def update_hourly_chart(self):
        """Update the hourly distribution chart"""
        if not self.analytics_engine:
            return
            
        # Generate chart
        chart_path = self.analytics_engine.generate_hourly_bar_chart()
        
        # Update widget
        if chart_path and os.path.exists(chart_path):
            self.hourly_widget.update_image(chart_path)
            
    def export_report(self):
        """Export analytics report"""
        if not self.analytics_engine:
            return
            
        try:
            # Generate report
            report_path = self.analytics_engine.export_analytics_report()
            
            if not report_path or not os.path.exists(report_path):
                QMessageBox.warning(self, "Export Error", "Failed to generate analytics report")
                return
                
            # Ask user where to save the report
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Analytics Report", "", "HTML Files (*.html)"
            )
            
            if not save_path:
                return
                
            # Copy report to save location
            import shutil
            shutil.copy2(report_path, save_path)
            
            # Ask if user wants to open the report
            if QMessageBox.question(
                self, "Report Exported", 
                f"Report saved to {save_path}. Would you like to open it?",
                QMessageBox.Yes | QMessageBox.No
            ) == QMessageBox.Yes:
                # Open report in default browser
                import webbrowser
                webbrowser.open(save_path)
                
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export report: {str(e)}")