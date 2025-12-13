from qgis.PyQt import QtWidgets, QtCore
import os
import tempfile

from qgis.PyQt.QtGui import QIcon


class SettingsDialog(QtWidgets.QDialog):
    """Settings dialog for MapLibre HTML output directory configuration"""

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
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
        title = QtWidgets.QLabel("MapLibre HTML Output Directory")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)

        # MapLibre output path settings
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
            "When MapLibre HTML is generated, it will be saved to the selected directory. "
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

    def _load_settings(self):
        """Load saved MapLibre output path from QSettings"""
        saved_path = self.settings.value('maplibre_output_path', None)
        if saved_path is None or saved_path == '__default__':
            self.path_input.setText(f"[Default] {tempfile.gettempdir()}")
            self._current_path = '__default__'
        else:
            self.path_input.setText(saved_path)
            self._current_path = saved_path

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
        self.path_input.setText(f"[Default] {tempfile.gettempdir()}")
        self._current_path = '__default__'
        # Save to QSettings
        self.settings.setValue('maplibre_output_path', '__default__')

    def _open_folder(self):
        """Open the current output directory in file explorer"""
        if self._current_path == '__default__':
            path_to_open = tempfile.gettempdir()
        else:
            path_to_open = self._current_path
        
        if os.path.exists(path_to_open):
            try:
                import subprocess
                import platform
                if platform.system() == 'Windows':
                    subprocess.Popen(f'explorer /select,"{path_to_open}"')
                elif platform.system() == 'Darwin':
                    subprocess.Popen(['open', '-R', path_to_open])
                else:
                    subprocess.Popen(['xdg-open', path_to_open])
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to open folder: {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", f"Path does not exist: {path_to_open}")
