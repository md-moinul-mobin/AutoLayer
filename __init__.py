def classFactory(iface):
    """Entry point for AutoLayer plugin."""
    from AutoLayer.autolayer import AutoLayer  # Explicit package reference
    return AutoLayer(iface)