from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QListWidget, QListWidgetItem, QDialog, QLineEdit,
    QFormLayout, QSpinBox, QCheckBox, QTextEdit, QColorDialog, QComboBox,
    QMessageBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QToolButton, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QFont

from core.multi_zone_controller import Zone, ZoneScheduleRule

class ZoneListItem(QListWidgetItem):
    """Custom list item for displaying zones"""
    
    def __init__(self, zone, parent=None):
        super().__init__(parent)
        self.zone = zone
        self.update_display()
        
    def update_display(self):
        """Update item display based on zone properties"""
        # Set text and tooltip
        self.setText(self.zone.name)
        self.setToolTip(self.zone.description)
        
        # Set background color based on zone color
        color = QColor(self.zone.color)
        color.setAlpha(50)  # Make it semi-transparent
        self.setBackground(color)
        
        # Use white or black text based on color brightness
        if color.lightnessF() > 0.5:
            self.setForeground(Qt.black)
        else:
            self.setForeground(Qt.white)
            
        # Set disabled state
        if not self.zone.enabled:
            font = self.font()
            font.setItalic(True)
            self.setFont(font)
            self.setForeground(Qt.gray)


class ZoneEditorDialog(QDialog):
    """Dialog for editing zone properties"""
    
    def __init__(self, zone=None, parent=None):
        super().__init__(parent)
        self.zone = zone
        self.setWindowTitle("Zone Editor")
        self.setMinimumSize(450, 500)
        
        # Set up the UI
        self.setup_ui()
        
        # Fill fields if editing existing zone
        if zone:
            self.populate_form()
            
    def setup_ui(self):
        """Set up the dialog UI"""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Form layout for zone properties
        self.form_layout = QFormLayout()
        
        # Zone name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter zone name")
        self.form_layout.addRow("Zone Name:", self.name_edit)
        
        # Zone description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter zone description")
        self.description_edit.setMaximumHeight(80)
        self.form_layout.addRow("Description:", self.description_edit)
        
        # Zone enabled
        self.enabled_checkbox = QCheckBox("Zone Enabled")
        self.enabled_checkbox.setChecked(True)
        self.form_layout.addRow("", self.enabled_checkbox)
        
        # Volume modifier
        self.volume_spinner = QSpinBox()
        self.volume_spinner.setRange(0, 200)
        self.volume_spinner.setValue(100)
        self.volume_spinner.setSuffix("%")
        self.form_layout.addRow("Volume Modifier:", self.volume_spinner)
        
        # Zone color
        self.color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.setFixedSize(40, 25)
        self.color = QColor("#00a0ff")  # Default color
        self.color_button.setStyleSheet(f"background-color: {self.color.name()}")
        self.color_button.clicked.connect(self.choose_color)
        
        self.color_layout.addWidget(self.color_button)
        self.color_layout.addWidget(QLabel("Click to change color"))
        self.color_layout.addStretch()
        
        self.form_layout.addRow("Zone Color:", self.color_layout)
        
        # Add the form layout to the main layout
        self.layout.addLayout(self.form_layout)
        
        # Bells allowed section
        self.bells_group = QGroupBox("Bells Allowed in Zone")
        self.bells_layout = QVBoxLayout(self.bells_group)
        
        self.all_bells_checkbox = QCheckBox("Allow All Bells")
        self.all_bells_checkbox.setChecked(True)
        self.all_bells_checkbox.stateChanged.connect(self.toggle_bells_list)
        
        self.bells_list = QListWidget()
        self.bells_list.setSelectionMode(QListWidget.MultiSelection)
        self.bells_list.setEnabled(False)
        
        # Add some dummy bells for now
        self.bells_list.addItems([
            "School Start", "Period 1", "Break", "Period 2",
            "Lunch", "Period 3", "End of Day"
        ])
        
        self.bells_layout.addWidget(self.all_bells_checkbox)
        self.bells_layout.addWidget(self.bells_list)
        
        self.layout.addWidget(self.bells_group)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Save Zone")
        self.save_button.clicked.connect(self.save_zone)
        self.save_button.setStyleSheet("""
            background-color: #00a0ff;
            color: white;
            font-weight: bold;
            padding: 8px 16px;
        """)
        
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.save_button)
        
        self.layout.addLayout(self.button_layout)
        
    def toggle_bells_list(self, state):
        """Enable or disable bells list based on checkbox state"""
        self.bells_list.setEnabled(not state)
        
    def choose_color(self):
        """Open color dialog and set zone color"""
        color = QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()}")
            
    def populate_form(self):
        """Fill form with zone data if editing existing zone"""
        if not self.zone:
            return
            
        self.name_edit.setText(self.zone.name)
        self.description_edit.setText(self.zone.description)
        self.enabled_checkbox.setChecked(self.zone.enabled)
        self.volume_spinner.setValue(self.zone.volume_modifier)
        
        # Set color
        self.color = QColor(self.zone.color)
        self.color_button.setStyleSheet(f"background-color: {self.color.name()}")
        
        # Set bells allowed
        if not self.zone.bells_allowed:
            self.all_bells_checkbox.setChecked(True)
            self.bells_list.setEnabled(False)
        else:
            self.all_bells_checkbox.setChecked(False)
            self.bells_list.setEnabled(True)
            
            # Select matching bells
            for i in range(self.bells_list.count()):
                item = self.bells_list.item(i)
                if item.text() in self.zone.bells_allowed:
                    item.setSelected(True)
                    
    def save_zone(self):
        """Save zone data and close dialog"""
        # Validate zone name
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Zone name cannot be empty")
            return
            
        # Get bells allowed
        bells_allowed = []
        if not self.all_bells_checkbox.isChecked():
            for item in self.bells_list.selectedItems():
                bells_allowed.append(item.text())
                
        # Create zone data
        zone_id = self.zone.id if self.zone else None
        
        self.zone_data = Zone(
            name=name,
            id=zone_id,
            description=self.description_edit.toPlainText(),
            enabled=self.enabled_checkbox.isChecked(),
            volume_modifier=self.volume_spinner.value(),
            bells_allowed=bells_allowed,
            color=self.color.name()
        )
        
        # Accept dialog
        self.accept()


class ZoneManager(QWidget):
    """Widget for managing bell zones"""
    
    zone_changed = pyqtSignal()
    
    def __init__(self, zone_controller=None, bell_scheduler=None, parent=None):
        super().__init__(parent)
        self.zone_controller = zone_controller
        self.bell_scheduler = bell_scheduler
        
        # Set up the UI
        self.setup_ui()
        
        # Load zones
        self.load_zones()
        
    def setup_ui(self):
        """Set up the widget UI"""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Add header with title and controls
        self.header_layout = QHBoxLayout()
        
        self.title = QLabel("Bell Zones")
        self.title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)
        
        self.add_button = QPushButton("+ Add Zone")
        self.add_button.setStyleSheet("""
            background-color: #00a0ff;
            color: white;
            border-radius: 5px;
            padding: 5px 10px;
        """)
        self.add_button.clicked.connect(self.add_zone)
        
        self.header_layout.addWidget(self.title)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.add_button)
        
        # Add zone list
        self.zone_list = QListWidget()
        self.zone_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                border-radius: 10px;
                border: 1px solid #353550;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                margin: 2px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #404060;
            }
            QListWidget::item:hover {
                background-color: #353550;
            }
        """)
        self.zone_list.itemDoubleClicked.connect(self.edit_zone)
        
        # Add context menu to zone list
        self.zone_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.zone_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Add zone details panel
        self.details_panel = QFrame()
        self.details_panel.setFrameShape(QFrame.StyledPanel)
        self.details_panel.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 10px;
            border: 1px solid #353550;
            padding: 10px;
        """)
        
        self.details_layout = QVBoxLayout(self.details_panel)
        
        self.details_title = QLabel("Zone Details")
        self.details_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #00a0ff;
        """)
        
        self.details_content = QLabel("Select a zone to view details")
        self.details_content.setWordWrap(True)
        self.details_content.setStyleSheet("color: white;")
        
        self.details_layout.addWidget(self.details_title)
        self.details_layout.addWidget(self.details_content)
        
        # Add button panel
        self.button_panel = QFrame()
        self.button_layout = QHBoxLayout(self.button_panel)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_selected_zone)
        self.edit_button.setEnabled(False)
        
        self.toggle_button = QPushButton("Enable/Disable")
        self.toggle_button.clicked.connect(self.toggle_selected_zone)
        self.toggle_button.setEnabled(False)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_selected_zone)
        self.remove_button.setEnabled(False)
        
        self.button_layout.addWidget(self.edit_button)
        self.button_layout.addWidget(self.toggle_button)
        self.button_layout.addWidget(self.remove_button)
        
        # Create a splitter for zone list and details
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.zone_list)
        
        # Create right panel with details and buttons
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.addWidget(self.details_panel)
        self.right_layout.addWidget(self.button_panel)
        
        self.splitter.addWidget(self.right_panel)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        
        # Add all components to main layout
        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.splitter)
        
        # Connect signals
        self.zone_list.itemSelectionChanged.connect(self.update_zone_details)
        
    def load_zones(self):
        """Load zones from controller"""
        self.zone_list.clear()
        
        if not self.zone_controller:
            return
            
        for zone in self.zone_controller.get_all_zones():
            item = ZoneListItem(zone)
            self.zone_list.addItem(item)
            
    def add_zone(self):
        """Add a new zone"""
        dialog = ZoneEditorDialog(parent=self)
        
        if dialog.exec_():
            # Get zone data
            zone = dialog.zone_data
            
            # Add to controller
            if self.zone_controller:
                self.zone_controller.add_zone(zone)
                
            # Add to list
            item = ZoneListItem(zone)
            self.zone_list.addItem(item)
            
            # Emit signal
            self.zone_changed.emit()
            
    def edit_zone(self, item):
        """Edit a zone from list item"""
        if not isinstance(item, ZoneListItem):
            return
            
        dialog = ZoneEditorDialog(item.zone, self)
        
        if dialog.exec_():
            # Get updated zone data
            updated_zone = dialog.zone_data
            
            # Update in controller
            if self.zone_controller:
                self.zone_controller.update_zone(item.zone.id, updated_zone)
                
            # Update item
            item.zone = updated_zone
            item.update_display()
            
            # Update details if this is the selected zone
            if item.isSelected():
                self.update_zone_details()
                
            # Emit signal
            self.zone_changed.emit()
            
    def edit_selected_zone(self):
        """Edit the currently selected zone"""
        items = self.zone_list.selectedItems()
        if items:
            self.edit_zone(items[0])
            
    def toggle_selected_zone(self):
        """Toggle enabled state of selected zone"""
        items = self.zone_list.selectedItems()
        if not items or not self.zone_controller:
            return
            
        item = items[0]
        
        # Toggle enabled state
        enabled = not item.zone.enabled
        
        # Update in controller
        self.zone_controller.enable_zone(item.zone.id, enabled)
        
        # Update zone object
        item.zone.enabled = enabled
        
        # Update display
        item.update_display()
        
        # Update details
        self.update_zone_details()
        
        # Emit signal
        self.zone_changed.emit()
        
    def remove_selected_zone(self):
        """Remove the selected zone"""
        items = self.zone_list.selectedItems()
        if not items or not self.zone_controller:
            return
            
        item = items[0]
        
        # Confirm deletion
        if QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete zone '{item.zone.name}'?",
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
            
        # Remove from controller
        self.zone_controller.remove_zone(item.zone.id)
        
        # Remove from list
        row = self.zone_list.row(item)
        self.zone_list.takeItem(row)
        
        # Clear details
        self.details_content.setText("Select a zone to view details")
        
        # Disable buttons
        self.edit_button.setEnabled(False)
        self.toggle_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        
        # Emit signal
        self.zone_changed.emit()
        
    def update_zone_details(self):
        """Update the details panel with selected zone info"""
        items = self.zone_list.selectedItems()
        
        if not items:
            self.details_content.setText("Select a zone to view details")
            self.edit_button.setEnabled(False)
            self.toggle_button.setEnabled(False)
            self.remove_button.setEnabled(False)
            return
            
        item = items[0]
        zone = item.zone
        
        # Format details
        details = f"""
        <h2 style='color: {zone.color}'>{zone.name}</h2>
        <p><b>Status:</b> {'Enabled' if zone.enabled else 'Disabled'}</p>
        <p><b>Description:</b> {zone.description}</p>
        <p><b>Volume Modifier:</b> {zone.volume_modifier}%</p>
        """
        
        if zone.bells_allowed:
            details += "<p><b>Restricted to Bells:</b></p><ul>"
            for bell in zone.bells_allowed:
                details += f"<li>{bell}</li>"
            details += "</ul>"
        else:
            details += "<p><b>Bell Restrictions:</b> None (all bells allowed)</p>"
            
        self.details_content.setText(details)
        
        # Enable buttons
        self.edit_button.setEnabled(True)
        self.toggle_button.setEnabled(True)
        self.remove_button.setEnabled(True)
        
        # Update toggle button text
        self.toggle_button.setText("Disable" if zone.enabled else "Enable")
        
    def show_context_menu(self, position):
        """Show context menu for zone list"""
        items = self.zone_list.selectedItems()
        if not items:
            return
            
        item = items[0]
        zone = item.zone
        
        menu = QMenu()
        
        edit_action = menu.addAction("Edit Zone")
        toggle_action = menu.addAction("Disable" if zone.enabled else "Enable")
        remove_action = menu.addAction("Remove Zone")
        
        action = menu.exec_(self.zone_list.mapToGlobal(position))
        
        if action == edit_action:
            self.edit_zone(item)
        elif action == toggle_action:
            self.toggle_selected_zone()
        elif action == remove_action:
            self.remove_selected_zone()