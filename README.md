# AutoLayer QGIS Plugin

A smart QGIS plugin that automatically processes newly added layers, applying custom symbology rules and handling project Coordinate Reference System (CRS) setup.

![QGIS Plugin](autolayer.png)

AutoLayer Plugin - Key Features
-CRS selection dialog for new projects with 4 specific options : EPSG:28992, EPSG:2154, EPSG:31370 & Choose Other.

-Auto enable "Selection" mode after opening a project.

-Automatically change/assign CRS of new layers with invalid or unknown CRS to match project CRS.

-Auto symbology for all new vector layers. Point layers get diamond symbols, line layers get colored lines, polygon layers get colored outlines.

-Apply different colors sequentially to newly added vector layers using 16-unique & more visible color palette.

-Special styling for "Cutline" layers (green outline polygons with 0.5mm stroke width).

-Special styling for "Tiles" layers (blue outline polygons with TileID labels).

-Special styling for "Grid" layers (cyan outline polygons with id labels).

-Special styling for "EO" layers (Default symbols with orange color).

-Automatic sort(by name), collapse & move to the bottom for newly added raster layers with specific name(tile_A_B) & file format(pix, tif, tiff).

-Toggle plugin on/off using toolbar icon (enabled by default) & show status messages when turning plugin on or off.

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




