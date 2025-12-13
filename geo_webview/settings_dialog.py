from qgis.PyQt import QtWidgets, QtCore
import os
import tempfile

from qgis.PyQt.QtGui import QIcon


class SettingsDialog(QtWidgets.QDialog):
    """Settings dialog for MapLibre and OpenLayers HTML output directory configuration"""

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'icon', 'setting.png')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass

        # Initialize QSettings for persistent storage
        self.settings = QtCore.QSettings('GeoWebView', 'geo_webview')
        
        # Main layout
        layout = QtWidgets.QVBoxLayout()

        # Title
        title = QtWidgets.QLabel("Web Map Output Directories")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)

        # OpenLayers output path settings (first)
        openlayers_group = QtWidgets.QGroupBox("OpenLayers HTML Save Location")
        openlayers_layout = QtWidgets.QVBoxLayout()

        # Path display
        ol_path_layout = QtWidgets.QHBoxLayout()
        ol_path_label = QtWidgets.QLabel("Output Path:")
        self.ol_path_input = QtWidgets.QLineEdit()
        self.ol_path_input.setReadOnly(True)
        ol_path_layout.addWidget(ol_path_label)
        ol_path_layout.addWidget(self.ol_path_input)
        openlayers_layout.addLayout(ol_path_layout)

        # Buttons layout
        ol_button_layout = QtWidgets.QHBoxLayout()
        
        # Browse button
        ol_btn_browse = QtWidgets.QPushButton("Browse...")
        ol_btn_browse.clicked.connect(self._browse_openlayers_folder)
        ol_button_layout.addWidget(ol_btn_browse)

        # Default (temp) button
        ol_btn_default = QtWidgets.QPushButton("Default (Temp)")
        ol_btn_default.setToolTip("Reset to system temporary directory")
        ol_btn_default.clicked.connect(self._set_default_openlayers_temp)
        ol_button_layout.addWidget(ol_btn_default)

        # Open folder button
        ol_btn_open = QtWidgets.QPushButton("Open Folder")
        ol_btn_open.clicked.connect(self._open_openlayers_folder)
        ol_button_layout.addWidget(ol_btn_open)

        ol_button_layout.addStretch()
        openlayers_layout.addLayout(ol_button_layout)

        openlayers_group.setLayout(openlayers_layout)
        layout.addWidget(openlayers_group)

        # MapLibre output path settings (second)
        maplibre_group = QtWidgets.QGroupBox("MapLibre HTML Save Location")
        maplibre_layout = QtWidgets.QVBoxLayout()

        # Path display
        path_layout = QtWidgets.QHBoxLayout()
        path_label = QtWidgets.QLabel("Output Path:")
        self.path_input = QtWidgets.QLineEdit()
        self.path_input.setReadOnly(True)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        maplibre_layout.addLayout(path_layout)

        # Buttons layout
        button_layout = QtWidgets.QHBoxLayout()
        
        # Browse button
        btn_browse = QtWidgets.QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse_folder)
        button_layout.addWidget(btn_browse)

        # Default (temp) button
        btn_default = QtWidgets.QPushButton("Default (Temp)")
        btn_default.setToolTip("Reset to system temporary directory (current behavior)")
        btn_default.clicked.connect(self._set_default_temp)
        button_layout.addWidget(btn_default)

        # Open folder button
        btn_open = QtWidgets.QPushButton("Open Folder")
        btn_open.clicked.connect(self._open_folder)
        button_layout.addWidget(btn_open)

        button_layout.addStretch()
        maplibre_layout.addLayout(button_layout)

        maplibre_group.setLayout(maplibre_layout)
        layout.addWidget(maplibre_group)

        # Info label
        info = QtWidgets.QLabel(
            "When MapLibre/OpenLayers HTML is generated, it will be saved to the selected directory. "
            "If Default (Temp) is selected, the system temporary directory will be used."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666;")
        layout.addWidget(info)

        layout.addStretch()

        # Close button
        btn_close = QtWidgets.QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self.setLayout(layout)

        # Load saved settings
        self._load_settings()

    def showEvent(self, event):
        """Refresh settings when dialog is shown to reflect latest values"""
        super().showEvent(event)
        self._load_settings()

    def _load_settings(self):
        """Load saved output paths from QSettings and display them dynamically"""
        # MapLibre settings
        saved_path = self.settings.value('maplibre_output_path', None)
        if saved_path is None or saved_path == '__default__':
            # Dynamically get the default folder: tempdir/qmap_maplibre
            temp_dir = tempfile.gettempdir()
            default_folder = os.path.join(temp_dir, 'qmap_maplibre')
            self.path_input.setText(f"[Default] {default_folder}")
            self._current_path = '__default__'
        else:
            # Verify the saved path still exists
            if os.path.exists(saved_path):
                self.path_input.setText(saved_path)
                self._current_path = saved_path
            else:
                # Path no longer exists, reset to default
                temp_dir = tempfile.gettempdir()
                default_folder = os.path.join(temp_dir, 'qmap_maplibre')
                self.path_input.setText(f"[Default] {default_folder}")
                self._current_path = '__default__'
                self.settings.setValue('maplibre_output_path', '__default__')

        # OpenLayers settings
        ol_saved_path = self.settings.value('openlayers_output_path', None)
        if ol_saved_path is None or ol_saved_path == '__default__':
            # Dynamically get the default folder: tempdir/qmap_openlayers
            temp_dir = tempfile.gettempdir()
            ol_default_folder = os.path.join(temp_dir, 'qmap_openlayers')
            self.ol_path_input.setText(f"[Default] {ol_default_folder}")
            self._ol_current_path = '__default__'
        else:
            # Verify the saved path still exists
            if os.path.exists(ol_saved_path):
                self.ol_path_input.setText(ol_saved_path)
                self._ol_current_path = ol_saved_path
            else:
                # Path no longer exists, reset to default
                temp_dir = tempfile.gettempdir()
                ol_default_folder = os.path.join(temp_dir, 'qmap_openlayers')
                self.ol_path_input.setText(f"[Default] {ol_default_folder}")
                self._ol_current_path = '__default__'
                self.settings.setValue('openlayers_output_path', '__default__')

    def _browse_folder(self):
        """Open a folder browser dialog to select output directory"""
        # Note: getExistingDirectory by default only shows directories,
        # so options parameter is not strictly necessary
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select MapLibre HTML Output Directory",
            self._current_path if self._current_path != '__default__' else tempfile.gettempdir()
        )
        if folder:
            self.path_input.setText(folder)
            self._current_path = folder
            # Save to QSettings
            self.settings.setValue('maplibre_output_path', folder)

    def _set_default_temp(self):
        """Reset to default temporary directory"""
        temp_dir = tempfile.gettempdir()
        default_folder = os.path.join(temp_dir, 'qmap_maplibre')
        self.path_input.setText(f"[Default] {default_folder}")
        self._current_path = '__default__'
        # Save to QSettings
        self.settings.setValue('maplibre_output_path', '__default__')

    def _open_folder(self):
        """Open the current MapLibre output directory in file explorer"""
        # Always get the latest setting value
        saved_path = self.settings.value('maplibre_output_path', None)
        if saved_path is None or saved_path == '__default__':
            # Default: tempdir/qmap_maplibre
            temp_dir = tempfile.gettempdir()
            path_to_open = os.path.join(temp_dir, 'qmap_maplibre')
        else:
            path_to_open = saved_path
        
        # Normalize path (convert forward slashes to backslashes on Windows)
        path_to_open = os.path.normpath(path_to_open)
        
        # Create folder if it doesn't exist
        if not os.path.exists(path_to_open):
            try:
                os.makedirs(path_to_open, exist_ok=True)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to create folder: {e}")
                return
        
        try:
            import platform
            if platform.system() == 'Windows':
                # Use os.startfile for Windows (more reliable)
                os.startfile(path_to_open)
            elif platform.system() == 'Darwin':
                # macOS
                import subprocess
                subprocess.Popen(['open', path_to_open])
            else:
                # Linux
                import subprocess
                subprocess.Popen(['xdg-open', path_to_open])
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to open folder: {e}")

    def _browse_openlayers_folder(self):
        """Open a folder browser dialog to select OpenLayers output directory"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select OpenLayers HTML Output Directory",
            self._ol_current_path if self._ol_current_path != '__default__' else tempfile.gettempdir()
        )
        if folder:
            self.ol_path_input.setText(folder)
            self._ol_current_path = folder
            # Save to QSettings
            self.settings.setValue('openlayers_output_path', folder)

    def _set_default_openlayers_temp(self):
        """Reset OpenLayers to default temporary directory"""
        temp_dir = tempfile.gettempdir()
        ol_default_folder = os.path.join(temp_dir, 'qmap_openlayers')
        self.ol_path_input.setText(f"[Default] {ol_default_folder}")
        self._ol_current_path = '__default__'
        # Save to QSettings
        self.settings.setValue('openlayers_output_path', '__default__')

    def _open_openlayers_folder(self):
        """Open the current OpenLayers output directory in file explorer"""
        # Always get the latest setting value
        ol_saved_path = self.settings.value('openlayers_output_path', None)
        if ol_saved_path is None or ol_saved_path == '__default__':
            # Default: tempdir/qmap_openlayers
            temp_dir = tempfile.gettempdir()
            ol_path_to_open = os.path.join(temp_dir, 'qmap_openlayers')
        else:
            ol_path_to_open = ol_saved_path
        
        # Normalize path (convert forward slashes to backslashes on Windows)
        ol_path_to_open = os.path.normpath(ol_path_to_open)
        
        # Create folder if it doesn't exist
        if not os.path.exists(ol_path_to_open):
            try:
                os.makedirs(ol_path_to_open, exist_ok=True)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to create folder: {e}")
                return
        
        try:
            import platform
            if platform.system() == 'Windows':
                # Use os.startfile for Windows (more reliable)
                os.startfile(ol_path_to_open)
            elif platform.system() == 'Darwin':
                # macOS
                import subprocess
                subprocess.Popen(['open', ol_path_to_open])
            else:
                # Linux
                import subprocess
                subprocess.Popen(['xdg-open', ol_path_to_open])
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to open folder: {e}")
