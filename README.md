# AutoLayer QGIS Plugin

A smart QGIS plugin that automatically processes newly added layers, applying custom symbology rules and handling project Coordinate Reference System (CRS) setup.

![QGIS Plugin](autolayer.png)

## Features

- **Automatic CRS Setup**: Prompts user to select a project CRS on startup (RD New, Lambert-93, Belgian Lambert 72, or custom).
- **Smart Symbology Rules**: Applies predefined styling based on layer naming patterns:
  - `tile_*` layers: Blue outlines with TileID labels
  - `grid` layers: Light blue outlines with ID labels  
  - `cutline` layers: Green outlines
  - `eo` points: Orange points (keeps default symbol)
- **Sequential Coloring**: Applies a consistent 16-color palette to other vector layers.
- **Automatic Layer Management**: Collapses and naturally sorts raster tile layers (.pix, .tif, .tiff).

## Installation

1. **Download the plugin**: Clone this repository or download as ZIP
2. **Install in QGIS**:
   - Go to `Plugins > Manage and Install Plugins... > Install from ZIP`
   - Select the downloaded ZIP file
   - Click `Install Plugin`

## Usage

1. Enable the plugin using the toolbar icon (![icon](autolayer.png))
2. Start adding layers to your project - they will be processed automatically
3. The plugin handles:
   - CRS assignment and validation
   - Automatic symbology application
   - Layer sorting and organization

## Supported CRS Systems

- EPSG:28992 (Amersfoort / RD New) - Netherlands
- EPSG:2154 (RGF93 / Lambert-93) - France  
- EPSG:31370 (Belge 1972 / Belgian Lambert 72) - Belgium
- Custom CRS selection via native QGIS dialog

## File Structure

```
AutoLayer/
├── __init__.py          # Plugin loader
├── metadata.txt         # Plugin metadata
├── autolayer.py         # Main plugin code
├── autolayer.png        # Plugin icon
├── LICENSE             # MIT License
└── README.md           # This file
```

## Author

**md-moinul-mobin**  
- Email: mdmoinulmobin@gmail.com  
- GitHub: [@md-moinul-mobin](https://github.com/md-moinul-mobin)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please create an issue in this repository or contact the author directly.