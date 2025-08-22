from qgis.core import (
    QgsProject, QgsVectorLayer, QgsRasterLayer, QgsSymbol, QgsSingleSymbolRenderer,
    QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol, QgsPalLayerSettings,
    QgsTextFormat, QgsVectorLayerSimpleLabeling, QgsCoordinateReferenceSystem,
    QgsLayerTreeLayer, QgsLayerTreeGroup, QgsSimpleLineSymbolLayer
)
from qgis.gui import QgsProjectionSelectionDialog
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QPushButton, QAction
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtCore import QTimer
from qgis.utils import iface
import os
import logging
import re

# Set up logging
logging.basicConfig()
logger = logging.getLogger('AutoLayer')
logger.setLevel(logging.INFO)

class CRSSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Project CRS")
        self.setFixedSize(320, 220)  # Increased height for additional button
        self.layout = QVBoxLayout()
        
        crs_buttons = [
            ("EPSG:28992", "Amersfoort / RD New"),
            ("EPSG:2154", "RGF93 / Lambert-93"),
            ("EPSG:31370", "Belge 1972 / Belgian Lambert 72")
        ]
        
        for epsg, label in crs_buttons:
            btn = QPushButton(f"{epsg}\n{label}")
            btn.setStyleSheet("text-align: center; padding: 8px;")
            btn.clicked.connect(lambda _, e=epsg: self.select_crs(e))
            self.layout.addWidget(btn)
            
        # Add "Choose Other" button
        other_btn = QPushButton("Choose Other...")
        other_btn.setStyleSheet("text-align: center; padding: 8px; font-weight: bold;")
        other_btn.clicked.connect(self.open_native_crs_selector)
        self.layout.addWidget(other_btn)
        
        self.setLayout(self.layout)
        self.selected_crs = None
    
    def select_crs(self, crs):
        self.selected_crs = crs
        self.accept()
        
    def open_native_crs_selector(self):
        """Open QGIS's native CRS selection dialog"""
        dlg = QgsProjectionSelectionDialog(self)
        if dlg.exec_():
            crs = dlg.crs()
            if crs.isValid():
                self.selected_crs = crs.authid()
                self.accept()

class AutoLayer:
    def __init__(self, iface):
        self.iface = iface
        self.project = QgsProject.instance()
        self.plugin_dir = os.path.dirname(__file__)
        self.is_enabled = True
        
        # New 16-color palette
        self.color_palette = [
            '#e41a1c', '#3579b1', '#00e4f6', '#0000ff', 
            '#ff00ff', '#ff69b4', '#5e17eb', '#ffa500',
            '#00fa9a', '#e10052', '#9bbce7', '#c8ff6d',
            '#22c89e', '#ffd93d', '#008e9b', '#ff9671'
        ]
        self.current_color_index = 0
        
        # Custom symbology rules
        self.custom_rules = {
            'eo': {'type': 'point', 'color': '#fdbf6f', 'keep_default_symbol': True},
            'tile': {
                'type': 'polygon',
                'fill': 'no',
                'outline_width': '1.0',
                'outline_color': '#3579b1',
                'label': {'field': 'TileID', 'size': 11, 'color': '#ffc843'}
            },
            'grid': {
                'type': 'polygon',
                'fill': 'no',
                'outline_width': '1.0',
                'outline_color': '#74cee3',
                'label': {'field': 'id', 'size': 11, 'color': '#ffc843'}
            },
            'cutline': {
                'type': 'polygon',
                'fill': 'no',
                'outline_width': '0.5',
                'outline_color': '#4daf4a'
            }
        }

    def initGui(self):
        """Initialize plugin interface with toolbar and icon"""
        self.toolbar = self.iface.addToolBar("AutoLayer")
        self.toolbar.setObjectName("AutoLayerToolbar")
        
        icon_path = os.path.join(self.plugin_dir, 'autolayer.png')
        self.action = QAction(
            QIcon(icon_path),
            "AutoLayer",
            self.iface.mainWindow()
        )
        
        self.action.setCheckable(True)
        self.action.setChecked(self.is_enabled)
        self.action.triggered.connect(self.toggle_plugin)
        self.action.setWhatsThis("Click to enable/disable automatic layer processing")
        self.toolbar.addAction(self.action)
        
        # Connect signals
        self.iface.initializationCompleted.connect(self.on_init_complete)
        self.project.layersAdded.connect(self.process_new_layer)
        self.project.readProject.connect(self.on_project_read)

    def toggle_plugin(self):
        """Toggle plugin enabled/disabled state"""
        self.is_enabled = self.action.isChecked()
        
        if self.is_enabled:
            self.iface.messageBar().pushMessage(
                "AutoLayer", "Plugin ENABLED - Will process new layers", 
                level=0, duration=3
            )
        else:
            self.iface.messageBar().pushMessage(
                "AutoLayer", "Plugin DISABLED - Will ignore new layers", 
                level=1, duration=3
            )

    def on_project_read(self):
        """Handle opening of existing/saved projects"""
        self.iface.actionSelect().trigger()

    def on_init_complete(self):
        """Handle new project initialization"""
        if not self.project.fileName() and not self.project.mapLayers():
            dlg = CRSSelectionDialog(parent=self.iface.mainWindow())
            if dlg.exec_():
                if dlg.selected_crs:  # Check if a CRS was selected (including from native dialog)
                    crs = QgsCoordinateReferenceSystem(dlg.selected_crs)
                    if crs.isValid():
                        self.project.setCrs(crs)
                        logger.info(f"Project CRS set to: {crs.authid()}")
            self.iface.actionSelect().trigger()

    def extract_tile_numbers(self, name):
        """STRICT extraction of tile numbers from exact 'tile_A_B' pattern only"""
        match = re.match(r'^tile_(\d+)_(\d+)$', name)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        return None

    def sort_layers_naturally(self, group):
        """Sort layers with natural ordering for exact tile patterns only"""
        try:
            layers = group.findLayers()
            if not layers:
                return

            # Separate exact tile_A_B layers from others
            tile_layers = []
            other_layers = []
            
            for layer in layers:
                numbers = self.extract_tile_numbers(layer.name())
                if numbers is not None:  # Only process exact matches
                    tile_layers.append((numbers, layer))
                else:
                    other_layers.append(layer)

            # Create temporary group
            root = group.parent() or group
            temp_group = root.insertGroup(0, "temp_sort_group")
            
            # Add layers to temp group (tile layers sorted, others in original order)
            for layer in other_layers + [x[1] for x in sorted(tile_layers, key=lambda x: x[0])]:
                layer_clone = layer.clone()
                temp_group.addChildNode(layer_clone)
                group.removeChildNode(layer)

            # Move back to original group
            for layer in temp_group.findLayers():
                layer_clone = layer.clone()
                group.insertChildNode(-1, layer_clone)

            # Remove temporary group
            root.removeChildNode(temp_group)
            
        except Exception as e:
            logger.error(f"Error in natural sorting: {str(e)}")

    def process_new_layer(self, layers):
        """Process newly added layers with CRS handling"""
        if not self.is_enabled:
            return
            
        project_crs = self.project.crs()
        has_target_raster = False
        
        for layer in layers:
            try:
                if not layer or not isinstance(layer, (QgsVectorLayer, QgsRasterLayer)):
                    continue
                
                logger.info(f"Processing layer: {layer.name()} (Source: {layer.source()})")
                
                if not layer.crs().isValid() or layer.crs() != project_crs:
                    layer.setCrs(project_crs, False)
                    logger.info(f"Assigned project CRS: {project_crs.authid()}")
                
                if isinstance(layer, QgsVectorLayer):
                    self.apply_symbology(layer)
                elif isinstance(layer, QgsRasterLayer):
                    source_lower = layer.source().lower()
                    if any(source_lower.endswith(ext) for ext in ['.pix', '.tif', '.tiff']):
                        has_target_raster = True
                        logger.info(f"Found target raster: {layer.name()} ({layer.source()})")
                    
            except Exception as e:
                logger.error(f"Error processing layer {layer.name()}: {str(e)}")
        
        # Use QTimer to ensure layers are fully loaded before processing
        if has_target_raster:
            QTimer.singleShot(1000, self.process_raster_layers)

    def process_raster_layers(self):
        """Process raster layers with natural sorting and collapsing"""
        try:
            root = QgsProject.instance().layerTreeRoot()
            target_extensions = ['.pix', '.tif', '.tiff']
            
            def process_group(group):
                # First sort naturally (only affects exact tile_A_B patterns)
                self.sort_layers_naturally(group)
                
                # Then process matching layers
                for child in group.children():
                    if isinstance(child, QgsLayerTreeGroup):
                        process_group(child)
                    elif isinstance(child, QgsLayerTreeLayer):
                        layer = child.layer()
                        if isinstance(layer, QgsRasterLayer):
                            source_lower = layer.source().lower()
                            if any(source_lower.endswith(ext) for ext in target_extensions):
                                child.setExpanded(False)
            
            process_group(root)
            
        except Exception as e:
            logger.error(f"Error processing raster layers: {str(e)}")

    def apply_symbology(self, layer):
        """Apply custom or sequential symbology"""
        layer_name_lower = layer.name().lower()
        rule = None
        
        # Check custom rules
        for rule_name, rule_data in self.custom_rules.items():
            if rule_name in layer_name_lower:
                rule = rule_data
                break
        
        if rule:
            self.apply_custom_rule(layer, rule)
        else:
            self.apply_sequential_symbology(layer)
        layer.triggerRepaint()

    def apply_custom_rule(self, layer, rule):
        """Apply predefined symbology rules"""
        try:
            geom_type = layer.geometryType()
            
            if rule['type'] == 'point' and geom_type == 0:
                symbol = QgsMarkerSymbol.createSimple({
                    'name': 'circle',
                    'size': rule.get('size', '4.0')
                }) if not rule.get('keep_default_symbol', False) else QgsMarkerSymbol()
                symbol.setColor(QColor(rule['color']))
                
            elif rule['type'] == 'polygon' and geom_type == 2:
                # Create QgsFillSymbol with outline-only configuration (Symbol layer type = Outline: Simple Line)
                symbol = QgsFillSymbol()
                # Remove default fill layer and add simple line layer for outline
                symbol.deleteSymbolLayer(0)  # Remove default simple fill layer
                line_layer = QgsSimpleLineSymbolLayer(QColor(rule['outline_color']), float(rule['outline_width']))
                symbol.appendSymbolLayer(line_layer)
                
            layer.setRenderer(QgsSingleSymbolRenderer(symbol))
            
            # Apply labels if specified
            if 'label' in rule:
                label_settings = QgsPalLayerSettings()
                label_settings.fieldName = rule['label']['field']
                text_format = QgsTextFormat()
                text_format.setSize(rule['label']['size'])
                text_format.setColor(QColor(rule['label']['color']))
                label_settings.setFormat(text_format)
                layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
                layer.setLabelsEnabled(True)
                
        except Exception as e:
            logger.error(f"Error applying custom rule: {str(e)}")

    def apply_sequential_symbology(self, layer):
        """Apply default sequential coloring"""
        try:
            color = QColor(self.color_palette[self.current_color_index])
            self.current_color_index = (self.current_color_index + 1) % len(self.color_palette)
            
            geom_type = layer.geometryType()
            
            if geom_type == 0:  # Point
                symbol = QgsMarkerSymbol.createSimple({'name': 'diamond', 'size': '4.4'})
            elif geom_type == 1:  # Line
                symbol = QgsLineSymbol.createSimple({'width': '0.6'})
            else:  # Polygon
                # Create QgsFillSymbol with outline-only configuration (Symbol layer type = Outline: Simple Line)
                symbol = QgsFillSymbol()
                # Remove default fill layer and add simple line layer for outline
                symbol.deleteSymbolLayer(0)  # Remove default simple fill layer
                line_layer = QgsSimpleLineSymbolLayer(color, 1.0)
                symbol.appendSymbolLayer(line_layer)
            
            if geom_type != 2:  # Only set color for non-polygon types (polygon uses line layer color directly)
                symbol.setColor(color)
            layer.setRenderer(QgsSingleSymbolRenderer(symbol))
            
        except Exception as e:
            logger.error(f"Error applying sequential symbology: {str(e)}")

    def unload(self):
        """Cleanup on plugin unload"""
        self.iface.initializationCompleted.disconnect(self.on_init_complete)
        self.project.layersAdded.disconnect(self.process_new_layer)
        self.project.readProject.disconnect(self.on_project_read)
        del self.toolbar
