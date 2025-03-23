import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene, 
                             QGraphicsPixmapItem, QFileDialog, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QSlider, QScrollArea, QAction,
                             QToolBar, QComboBox, QShortcut, QMessageBox, QDockWidget,
                             QTextBrowser, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QTransform, QKeySequence, QPainter
from PyQt5.QtCore import Qt, QRectF
import fitz  # PyMuPDF
import xml.etree.ElementTree as ET  # For parsing MusicXML

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_page = 0
        self.zoom_factor = 1.0
        self.pdf_document = None
        self.rotation = 0  # Rotation in degrees
        self.musicxml_file = None  # Path to associated MusicXML file
        self.musicxml_data = None  # Parsed MusicXML data
        
        self.init_ui()
        self.setup_shortcuts()
        self.create_musicxml_dock()
        
    def init_ui(self):
        self.setWindowTitle('Music Score PDF Viewer')
        self.setGeometry(100, 100, 1000, 800)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Open file action
        open_action = QAction("Open PDF", self)
        open_action.triggered.connect(self.open_pdf)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # Page navigation actions
        prev_action = QAction("Previous", self)
        prev_action.triggered.connect(self.previous_page)
        toolbar.addAction(prev_action)
        
        self.page_label = QLabel('Page: 0 / 0')
        toolbar.addWidget(self.page_label)
        
        next_action = QAction("Next", self)
        next_action.triggered.connect(self.next_page)
        toolbar.addAction(next_action)
        
        toolbar.addSeparator()
        
        # Zoom actions
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        self.zoom_label = QLabel('Zoom: 100%')
        toolbar.addWidget(self.zoom_label)
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        fit_width_action = QAction("Fit to Width", self)
        fit_width_action.triggered.connect(self.fit_to_width)
        toolbar.addAction(fit_width_action)
        
        toolbar.addSeparator()
        
        # Rotation actions
        rotate_left_action = QAction("Rotate Left", self)
        rotate_left_action.triggered.connect(self.rotate_left)
        toolbar.addAction(rotate_left_action)
        
        rotate_right_action = QAction("Rotate Right", self)
        rotate_right_action.triggered.connect(self.rotate_right)
        toolbar.addAction(rotate_right_action)
        
        toolbar.addSeparator()
        
        # MusicXML toggle action
        toggle_musicxml_action = QAction("MusicXML Info", self)
        toggle_musicxml_action.setCheckable(True)
        toggle_musicxml_action.triggered.connect(lambda checked: self.musicxml_dock.setVisible(checked))
        toolbar.addAction(toggle_musicxml_action)
        self.musicxml_toolbar_action = toggle_musicxml_action
        
        # Controls for additional features
        controls_layout = QHBoxLayout()
        
        # View mode selector for music scores
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["Single Page", "Two Pages", "Continuous"])
        self.view_mode_combo.currentIndexChanged.connect(self.change_view_mode)
        controls_layout.addWidget(QLabel("View Mode:"))
        controls_layout.addWidget(self.view_mode_combo)
        
        controls_layout.addStretch()
        
        # Add controls to main layout
        main_layout.addLayout(controls_layout)
        
        # PDF view
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Graphics view for displaying the PDF pages
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.scroll_area.setWidget(self.view)
        
        main_layout.addWidget(self.scroll_area)
        
        # Disable actions initially
        prev_action.setEnabled(False)
        next_action.setEnabled(False)
        zoom_in_action.setEnabled(False)
        zoom_out_action.setEnabled(False)
        fit_width_action.setEnabled(False)
        rotate_left_action.setEnabled(False)
        rotate_right_action.setEnabled(False)
        toggle_musicxml_action.setEnabled(False)
        
        self.prev_action = prev_action
        self.next_action = next_action
        self.zoom_in_action = zoom_in_action
        self.zoom_out_action = zoom_out_action
        self.fit_width_action = fit_width_action
        self.rotate_left_action = rotate_left_action
        self.rotate_right_action = rotate_right_action
        
    def setup_shortcuts(self):
        # Page navigation shortcuts
        QShortcut(QKeySequence(Qt.Key_Left), self, self.previous_page)
        QShortcut(QKeySequence(Qt.Key_Right), self, self.next_page)
        QShortcut(QKeySequence(Qt.Key_PageUp), self, self.previous_page)
        QShortcut(QKeySequence(Qt.Key_PageDown), self, self.next_page)
        
        # Zoom shortcuts
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Plus), self, self.zoom_in)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Minus), self, self.zoom_out)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_0), self, self.reset_zoom)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_W), self, self.fit_to_width)
        
        # Rotation shortcuts
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_R), self, self.rotate_right)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_L), self, self.rotate_left)
        
        # Open file shortcut
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_O), self, self.open_pdf)
        
        # First and last page shortcuts
        QShortcut(QKeySequence(Qt.Key_Home), self, self.first_page)
        QShortcut(QKeySequence(Qt.Key_End), self, self.last_page)
        
    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open PDF File', '', 'PDF Files (*.pdf)')
        
        if file_path:
            if self.pdf_document:
                self.pdf_document.close()
            
            try:
                self.pdf_document = fitz.open(file_path)
                self.current_page = 0
                self.update_page_label()
                
                # Enable navigation if document has pages
                has_pages = len(self.pdf_document) > 0
                self.prev_action.setEnabled(has_pages)
                self.next_action.setEnabled(has_pages and len(self.pdf_document) > 1)
                self.zoom_in_action.setEnabled(has_pages)
                self.zoom_out_action.setEnabled(has_pages)
                self.fit_width_action.setEnabled(has_pages)
                self.rotate_left_action.setEnabled(has_pages)
                self.rotate_right_action.setEnabled(has_pages)
                
                # Reset rotation and zoom
                self.rotation = 0
                self.zoom_factor = 1.0
                self.update_zoom_label()
                
                # Look for associated MusicXML file
                self.load_musicxml_file(file_path)
                
                # Enable MusicXML toggle if XML file was found
                self.musicxml_toolbar_action.setEnabled(self.musicxml_file is not None)
                
                if has_pages:
                    self.render_page()
            except Exception as e:
                print(f"Error opening PDF: {e}")
    
    def create_musicxml_dock(self):
        """Create a dock widget to display MusicXML information."""
        self.musicxml_dock = QDockWidget("MusicXML Information", self)
        self.musicxml_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Create widget for dock contents
        musicxml_widget = QWidget()
        musicxml_layout = QVBoxLayout(musicxml_widget)
        
        # Tree widget for structured display
        self.musicxml_tree = QTreeWidget()
        self.musicxml_tree.setHeaderLabels(["Property", "Value"])
        self.musicxml_tree.setColumnWidth(0, 150)
        musicxml_layout.addWidget(self.musicxml_tree)
        
        # Add a button to view/hide more detailed MusicXML information
        self.detail_button = QPushButton("View MusicXML Details")
        self.detail_button.clicked.connect(self.toggle_musicxml_details)
        musicxml_layout.addWidget(self.detail_button)
        
        # Text browser for raw XML display
        self.musicxml_text = QTextBrowser()
        self.musicxml_text.setVisible(False)
        musicxml_layout.addWidget(self.musicxml_text)
        
        self.musicxml_dock.setWidget(musicxml_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.musicxml_dock)
        self.musicxml_dock.setVisible(False)
        
        # Add action to toggle dock visibility
        toggle_musicxml_action = QAction("Toggle MusicXML Panel", self)
        toggle_musicxml_action.setCheckable(True)
        toggle_musicxml_action.triggered.connect(lambda checked: self.musicxml_dock.setVisible(checked))
        
        # Add to toolbar
        self.musicxml_toolbar_action = toggle_musicxml_action
        
    def load_musicxml_file(self, pdf_path):
        """
        Load MusicXML file with the same basename as the PDF file.
        Look for both .xml and .musicxml extensions.
        """
        self.musicxml_file = None
        self.musicxml_data = None
        self.musicxml_tree.clear()
        self.musicxml_text.setText("")
        self.musicxml_dock.setVisible(False)
        self.musicxml_toolbar_action.setChecked(False)
        
        # Get the base name of the PDF file without extension
        base_path = os.path.splitext(pdf_path)[0]
        
        # Check for .xml extension
        xml_path = f"{base_path}.xml"
        if os.path.exists(xml_path):
            self.musicxml_file = xml_path
        else:
            # Check for .musicxml extension
            musicxml_path = f"{base_path}.musicxml"
            if os.path.exists(musicxml_path):
                self.musicxml_file = musicxml_path
        
        # If MusicXML file was found, try to parse it
        if self.musicxml_file:
            try:
                self.parse_musicxml()
                self.update_musicxml_display()
                self.musicxml_dock.setVisible(True)
                self.musicxml_toolbar_action.setChecked(True)
                self.setWindowTitle(f'Music Score PDF Viewer - {os.path.basename(pdf_path)} (MusicXML loaded)')
                print(f"Loaded associated MusicXML file: {self.musicxml_file}")
                QMessageBox.information(self, "MusicXML Loaded", 
                                      f"Loaded associated MusicXML file:\n{os.path.basename(self.musicxml_file)}")
            except Exception as e:
                print(f"Error parsing MusicXML file: {e}")
                self.musicxml_file = None
        else:
            print(f"No associated MusicXML file found for {pdf_path}")
            self.setWindowTitle(f'Music Score PDF Viewer - {os.path.basename(pdf_path)}')
    
    def parse_musicxml(self):
        """
        Parse the MusicXML file to extract music notation information.
        """
        if not self.musicxml_file or not os.path.exists(self.musicxml_file):
            return
            
        try:
            tree = ET.parse(self.musicxml_file)
            root = tree.getroot()
            
            # Store the parsed data
            self.musicxml_data = {
                'title': self.get_musicxml_title(root),
                'composer': self.get_musicxml_composer(root),
                'parts': self.get_musicxml_parts(root),
                'measures': self.count_musicxml_measures(root),
            }
            
            print(f"MusicXML data loaded: {self.musicxml_data}")
        except Exception as e:
            print(f"Error parsing MusicXML file: {e}")
            self.musicxml_data = None
    
    def get_musicxml_title(self, root):
        """Extract the title from MusicXML file."""
        # Handle both compressed and uncompressed MusicXML formats
        if root.tag == 'score-partwise':
            # Uncompressed MusicXML
            work_title = root.find('.//work-title')
            if work_title is not None and work_title.text:
                return work_title.text
                
            movement_title = root.find('.//movement-title')
            if movement_title is not None and movement_title.text:
                return movement_title.text
        
        return "Unknown Title"
    
    def get_musicxml_composer(self, root):
        """Extract the composer from MusicXML file."""
        if root.tag == 'score-partwise':
            composer = root.find('.//creator[@type="composer"]')
            if composer is not None and composer.text:
                return composer.text
        
        return "Unknown Composer"
    
    def get_musicxml_parts(self, root):
        """Extract parts information from MusicXML file."""
        parts = []
        
        if root.tag == 'score-partwise':
            part_list = root.find('.//part-list')
            if part_list is not None:
                for part in part_list.findall('.//score-part'):
                    part_id = part.get('id')
                    part_name = part.find('.//part-name')
                    name = part_name.text if part_name is not None and part_name.text else "Unknown"
                    parts.append({'id': part_id, 'name': name})
        
        return parts
    
    def count_musicxml_measures(self, root):
        """Count measures in the MusicXML file."""
        if root.tag == 'score-partwise':
            # Get first part
            first_part = root.find('.//part')
            if first_part is not None:
                return len(first_part.findall('.//measure'))
        
        return 0
    
    def render_page(self):
        if not self.pdf_document or self.current_page >= len(self.pdf_document):
            return
        
        # Clear the previous rendering
        self.scene.clear()
        
        # Get the current page
        page = self.pdf_document[self.current_page]
        
        # Render the page to a pixmap with zoom
        zoom_matrix = fitz.Matrix(self.zoom_factor, self.zoom_factor)
        
        # Apply rotation if needed
        if self.rotation != 0:
            # PyMuPDF rotation is in 90-degree increments (0, 90, 180, 270)
            # Map our rotation to the nearest valid rotation
            mupdf_rotation = int(self.rotation / 90) % 4 * 90
            zoom_matrix = zoom_matrix * fitz.Matrix(mupdf_rotation)
        
        pixmap = page.get_pixmap(matrix=zoom_matrix)
        
        # Convert pixmap to QImage
        img = QImage(pixmap.samples, pixmap.width, pixmap.height,
                    pixmap.stride, QImage.Format_RGB888)
        
        # Create QPixmap from QImage
        pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(img))
        
        # For rotations that aren't multiples of 90, we need to apply additional rotation
        if self.rotation % 90 != 0:
            transform = QTransform().rotate(self.rotation % 90)
            pixmap_item.setTransform(transform)
        
        self.scene.addItem(pixmap_item)
        
        # Set the scene rectangle to the size of the pixmap
        self.scene.setSceneRect(QRectF(0, 0, pixmap.width, pixmap.height))
        
        # Update the view
        self.view.setSceneRect(self.scene.sceneRect())
        
    def update_page_label(self):
        total_pages = len(self.pdf_document) if self.pdf_document else 0
        self.page_label.setText(f'Page: {self.current_page + 1} / {total_pages}')
        
    def previous_page(self):
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.render_page()
            self.update_page_label()
        
    def next_page(self):
        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.render_page()
            self.update_page_label()
    
    def zoom_in(self):
        self.zoom_factor *= 1.25
        self.update_zoom_label()
        self.render_page()
    
    def zoom_out(self):
        self.zoom_factor /= 1.25
        self.update_zoom_label()
        self.render_page()
    
    def update_zoom_label(self):
        zoom_percentage = int(self.zoom_factor * 100)
        self.zoom_label.setText(f'Zoom: {zoom_percentage}%')
    
    def fit_to_width(self):
        if not self.pdf_document:
            return
        
        # Get the current page
        page = self.pdf_document[self.current_page]
        
        # Calculate the zoom factor to fit the width
        # Get page dimensions
        rect = page.rect
        page_width = rect.width
        
        # Get view width
        view_width = self.view.viewport().width() - 20  # Subtract some padding
        
        # Calculate zoom factor
        self.zoom_factor = view_width / page_width
        
        self.update_zoom_label()
        self.render_page()
    
    def rotate_left(self):
        self.rotation = (self.rotation - 90) % 360
        self.render_page()
    
    def rotate_right(self):
        self.rotation = (self.rotation + 90) % 360
        self.render_page()
    
    def change_view_mode(self, index):
        # This would be implemented to handle different view modes for music scores
        # For now, we'll just re-render the current page
        self.render_page()

    def resizeEvent(self, event):
        # When the window is resized, adjust the view if in fit-to-width mode
        super().resizeEvent(event)
        # In a real implementation, we might check if we're in fit-to-width mode
        # and recalculate the zoom factor

    def reset_zoom(self):
        if self.pdf_document:
            self.zoom_factor = 1.0
            self.update_zoom_label()
            self.render_page()
    
    def first_page(self):
        if self.pdf_document and self.current_page != 0:
            self.current_page = 0
            self.render_page()
            self.update_page_label()
    
    def last_page(self):
        if self.pdf_document and len(self.pdf_document) > 0:
            self.current_page = len(self.pdf_document) - 1
            self.render_page()
            self.update_page_label()

    def update_musicxml_display(self):
        """Update the MusicXML information display in the dock widget."""
        if not self.musicxml_data:
            return
            
        self.musicxml_tree.clear()
        
        # Add basic info
        title_item = QTreeWidgetItem(["Title", self.musicxml_data['title']])
        self.musicxml_tree.addTopLevelItem(title_item)
        
        composer_item = QTreeWidgetItem(["Composer", self.musicxml_data['composer']])
        self.musicxml_tree.addTopLevelItem(composer_item)
        
        measures_item = QTreeWidgetItem(["Measures", str(self.musicxml_data['measures'])])
        self.musicxml_tree.addTopLevelItem(measures_item)
        
        # Add parts information
        parts_item = QTreeWidgetItem(["Parts", f"{len(self.musicxml_data['parts'])} part(s)"])
        self.musicxml_tree.addTopLevelItem(parts_item)
        
        for part in self.musicxml_data['parts']:
            part_item = QTreeWidgetItem([part['id'], part['name']])
            parts_item.addChild(part_item)
            
        # Expand all items
        self.musicxml_tree.expandAll()
        
        # Load raw XML into text browser
        if self.musicxml_file:
            try:
                with open(self.musicxml_file, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                    self.musicxml_text.setText(xml_content)
            except Exception as e:
                self.musicxml_text.setText(f"Error loading XML content: {e}")

    def toggle_musicxml_details(self):
        """Toggle visibility of detailed MusicXML content."""
        if self.musicxml_text.isVisible():
            self.musicxml_text.setVisible(False)
            self.detail_button.setText("View MusicXML Details")
        else:
            self.musicxml_text.setVisible(True)
            self.detail_button.setText("Hide MusicXML Details")

def main():
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 