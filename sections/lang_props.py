from PyQt6.QtWidgets import QFormLayout, QLabel, QLineEdit, QTextEdit

from core.base_section import BaseSection
from core.i18n import tr


class LangPropsSection(BaseSection):

    def build_ui(self):
        form = QFormLayout(self)
        form.setContentsMargins(16, 16, 16, 16)
        form.setSpacing(10)

        self._name  = QLineEdit()
        self._local = QLineEdit()
        self._auth  = QLineEdit()
        self._ver   = QLineEdit()
        self._desc  = QTextEdit(); self._desc.setFixedHeight(100)

        self._l_name  = QLabel(); self._l_local = QLabel()
        self._l_auth  = QLabel(); self._l_ver   = QLabel()
        self._l_desc  = QLabel()

        form.addRow(self._l_name,  self._name)
        form.addRow(self._l_local, self._local)
        form.addRow(self._l_auth,  self._auth)
        form.addRow(self._l_ver,   self._ver)
        form.addRow(self._l_desc,  self._desc)

        for w in (self._name, self._local, self._auth, self._ver):
            w.textChanged.connect(self._write)
        self._desc.textChanged.connect(self._write)
        self._retranslate_labels()

    def load(self):
        lg = self._s.lang
        self._name.setText(lg.name)
        self._local.setText(lg.local_language)
        self._auth.setText(lg.author)
        self._ver.setText(lg.version)
        self._desc.setPlainText(lg.description)

    def save(self):
        lg = self._s.lang
        lg.name          = self._name.text().strip() or tr("unnamed")
        lg.local_language= self._local.text().strip()
        lg.author        = self._auth.text().strip()
        lg.version       = self._ver.text().strip()
        lg.description   = self._desc.toPlainText().strip()

    def retranslate(self):
        self._retranslate_labels()

    def _retranslate_labels(self):
        self._l_name.setText(tr("lp_lang_name"))
        self._l_local.setText(tr("lp_local_lang"))
        self._l_auth.setText(tr("lp_author"))
        self._l_ver.setText(tr("lp_version"))
        self._l_desc.setText(tr("lp_description"))

    def _write(self):
        self._s.mark_dirty()
