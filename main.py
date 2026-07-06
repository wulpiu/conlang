import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction

# ── Импорты PyQt6 ───────────────────────────────────────────────────────────
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QToolBar,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

import core.i18n as i18n
from core.base_section import BaseSection
from core.dna_language import PRESETS, decode_language, encode_language, encode_language_readable
from core.i18n import tr
from core.storage import Storage
from sections.lang_props import LangPropsSection
from sections.leipzig import LeipzigSection
from sections.lexicon import LexiconSection, WordFormationSection
from sections.morph_extra import AgreementSection
from sections.morphology import LangTypeSection, MorphemeTypesSection
from sections.phonology import ConsonantsSection, PhonotacticsSection, ProsodySection, VowelsSection
from sections.pragmatics_writing import PragmaticsSection, WritingSection
from sections.sentence_builder import SentenceBuilderSection
from sections.syntax import AlignmentSection, WordOrderSection
from sections.unified_paradigm import UnifiedParadigmSection


# ── Проверка зависимостей для анализатора текста ─────────────────────────────
def _check_dependencies():
    """Проверяет наличие библиотек для анализа текста."""
    import importlib.util
    missing = []

    if importlib.util.find_spec("pymorphy3") is None:
        missing.append("pymorphy3 (для анализа русского языка)")

    try:
        import spacy
        if not spacy.util.is_package("en_core_web_sm"):
            missing.append("spaCy модель 'en_core_web_sm' (python -m spacy download en_core_web_sm)")
    except ImportError:
        missing.append("spaCy (для анализа английского языка)")

    return missing

_MISSING_DEPS = _check_dependencies()


# ── Структура дерева: (ключ_i18n, section_class | None, [дочерние]) ─────────
_NAV = [
    ("nav_lang_props", LangPropsSection, []),

    ("nav_phonetics", None, [
        ("nav_vowels",       VowelsSection,       []),
        ("nav_consonants",   ConsonantsSection,   []),
        ("nav_prosody",      ProsodySection,      []),
        ("nav_phonotactics", PhonotacticsSection, []),
    ]),

    ("nav_morphology", None, [
        ("nav_lang_type",   LangTypeSection,      []),
        ("nav_morphemes",   MorphemeTypesSection, []),
        ("nav_paradigms",   UnifiedParadigmSection, []),
    ]),

    ("nav_lexicon", None, [
        ("nav_wordlist",       LexiconSection,       []),
        ("nav_word_formation", WordFormationSection, []),
        ("nav_leipzig",        LeipzigSection,       []),
    ]),

    ("nav_syntax", None, [
        ("nav_word_order", WordOrderSection,   []),
        ("nav_alignment",  AlignmentSection,   []),
        ("nav_agreement",  AgreementSection,   []),
    ]),

    ("nav_pragmatics", PragmaticsSection,      []),
    ("nav_writing",    WritingSection,         []),
    ("nav_sentence",   SentenceBuilderSection, []),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._storage = Storage()
        self._items: dict[str, tuple[QTreeWidgetItem, int]] = {}
        self._sections: list[BaseSection] = []
        self._current_section = None

        self.setMinimumSize(1050, 680)
        self._build_toolbar()
        self._build_body()
        self._retranslate()
        self._select_first()

        if _MISSING_DEPS:
            QMessageBox.warning(
                self,
                tr("app_title"),
                tr("missing_deps_warning") + "\n\n• " + "\n• ".join(_MISSING_DEPS) + "\n\n" +
                tr("missing_deps_hint")
            )

    def _build_toolbar(self):
        tb = QToolBar()
        tb.setMovable(False)
        tb.setIconSize(QSize(18, 18))
        self.addToolBar(tb)

        self._act_new     = QAction(tr("file_new"), self)
        self._act_open    = QAction(tr("file_open"), self)
        self._act_save    = QAction(tr("file_save"), self)
        self._act_save_as = QAction(tr("file_save_as"), self)
        self._act_refresh = QAction(tr("refresh"), self)
        self._act_lang    = QAction(tr("switch_lang"), self)

        self._act_new.triggered.connect(self._new)
        self._act_open.triggered.connect(self._open)
        self._act_save.triggered.connect(self._save)
        self._act_save_as.triggered.connect(self._save_as)
        self._act_refresh.triggered.connect(self._refresh_all)
        self._act_lang.triggered.connect(self._toggle_lang)

        self._act_new.setShortcut("Ctrl+N")
        self._act_open.setShortcut("Ctrl+O")
        self._act_save.setShortcut("Ctrl+S")
        self._act_refresh.setShortcut("F5")

        for a in (self._act_new, self._act_open, self._act_save,
                  self._act_save_as, self._act_refresh, self._act_lang):
            tb.addAction(a)

        tb.addSeparator()

        # Кнопка DNA
        self._act_dna_export = QAction(tr("dna_export"), self)
        self._act_dna_import = QAction(tr("dna_import"), self)
        self._act_dna_export.triggered.connect(self._export_dna)
        self._act_dna_import.triggered.connect(self._import_dna)

        dna_menu = QMenu()
        dna_menu.addAction(self._act_dna_export)
        dna_menu.addAction(self._act_dna_import)
        dna_menu.addSeparator()

        # Подменю с пресетами
        preset_menu = QMenu(tr("dna_preset"), self)
        for preset_id, preset_info in PRESETS.items():
            action = QAction(preset_info["name"], self)
            action.setData(preset_id)
            action.triggered.connect(lambda checked, pid=preset_id: self._load_preset(pid))
            preset_menu.addAction(action)
        dna_menu.addMenu(preset_menu)

        dna_btn = QToolButton()
        dna_btn.setText("🧬")
        dna_btn.setToolTip(tr("dna_tooltip"))
        dna_btn.setMenu(dna_menu)
        dna_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        tb.addWidget(dna_btn)

    def _build_body(self):
        central = QWidget()
        self.setCentralWidget(central)
        h = QHBoxLayout(central)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setFixedWidth(240)
        self._tree.setIndentation(16)
        self._tree.itemClicked.connect(self._on_tree_click)

        self._stack = QStackedWidget()

        self._build_tree(_NAV, self._tree.invisibleRootItem())

        h.addWidget(self._tree)
        h.addWidget(self._stack, 1)

        self._tree.setStyleSheet("""
            QTreeWidget { border-right: 1px solid #cccccc; font-size: 13px; }
            QTreeWidget::item { padding: 4px 6px; }
            QTreeWidget::item:selected { background: #4a90d9; color: white; }
        """)

    def _build_tree(self, nodes, parent_item):
        for key, cls, children in nodes:
            item = QTreeWidgetItem(parent_item, [tr(key)])
            item.setData(0, Qt.ItemDataRole.UserRole, key)

            if cls is not None:
                section = cls(self._storage)
                idx = self._stack.addWidget(section)
                self._items[key] = (item, idx)
                self._sections.append(section)
            else:
                f = item.font(0)
                f.setBold(True)
                item.setFont(0, f)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

            if children:
                self._build_tree(children, item)
                item.setExpanded(True)

    def _on_tree_click(self, item: QTreeWidgetItem, _col: int):
        key = item.data(0, Qt.ItemDataRole.UserRole)
        if key not in self._items:
            return
        if self._current_section:
            self._current_section.save()
        _, idx = self._items[key]
        self._stack.setCurrentIndex(idx)
        self._current_section = self._stack.currentWidget()

    def _select_first(self):
        if self._items:
            key = next(iter(self._items))
            item, idx = self._items[key]
            self._tree.setCurrentItem(item)
            self._stack.setCurrentIndex(idx)
            self._current_section = self._stack.widget(idx)

    def _new(self):
        if not self._check_unsaved():
            return
        self._storage.new()
        self._reload_all()
        self._update_title()

    def _open(self):
        if not self._check_unsaved():
            return
        path, _ = QFileDialog.getOpenFileName(
            self, tr("file_open"), "", "ConLang JSON (*.clng *.json)"
        )
        if path:
            if self._storage.load(path):
                self._reload_all()
                self._update_title()
            else:
                QMessageBox.warning(self, tr("app_title"), tr("load_err"))

    def _save(self):
        if self._current_section:
            self._current_section.save()
        if not self._storage.path:
            self._save_as()
            return
        ok = self._storage.save()
        self.statusBar().showMessage(tr("saved_ok") if ok else tr("save_err"), 3000)
        self._update_title()

    def _save_as(self):
        if self._current_section:
            self._current_section.save()
        path, _ = QFileDialog.getSaveFileName(
            self, tr("file_save_as"), "", "ConLang JSON (*.clng *.json)"
        )
        if path:
            ok = self._storage.save(path)
            self.statusBar().showMessage(tr("saved_ok") if ok else tr("save_err"), 3000)
            self._update_title()

    def _check_unsaved(self) -> bool:
        if not self._storage.dirty:
            return True
        ans = QMessageBox.question(
            self, tr("app_title"), tr("unsaved"),
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No |
            QMessageBox.StandardButton.Cancel,
        )
        if ans == QMessageBox.StandardButton.Cancel:
            return False
        if ans == QMessageBox.StandardButton.Yes:
            self._save()
        return True

    def closeEvent(self, event):
        if self._check_unsaved():
            event.accept()
        else:
            event.ignore()

    def _toggle_lang(self):
        i18n.set_lang("en" if i18n.get_lang() == "ru" else "ru")
        self._retranslate()

    def _retranslate(self):
        self._update_title()
        self._act_new.setText(tr("file_new"))
        self._act_open.setText(tr("file_open"))
        self._act_save.setText(tr("file_save"))
        self._act_save_as.setText(tr("file_save_as"))
        self._act_refresh.setText(tr("refresh"))
        self._act_lang.setText(tr("switch_lang"))
        self._act_dna_export.setText(tr("dna_export"))
        self._act_dna_import.setText(tr("dna_import"))
        self._retranslate_tree(_NAV, self._tree.invisibleRootItem())
        for s in self._sections:
            s.retranslate()

    def _retranslate_tree(self, nodes, parent_item):
        child_idx = 0
        for key, cls, children in nodes:
            item = parent_item.child(child_idx)
            if item:
                item.setText(0, tr(key))
            if children and item:
                self._retranslate_tree(children, item)
            child_idx += 1

    def _update_title(self):
        lang_name = self._storage.lang.name or tr("unnamed")
        dirty = " *" if self._storage.dirty else ""
        fname = f" — {self._storage.path.name}" if self._storage.path else ""
        self.setWindowTitle(f"{tr('app_title')} | {lang_name}{fname}{dirty}")

    def _reload_all(self):
        for s in self._sections:
            s.load()
        self._update_title()

    def _refresh_all(self):
        """Полностью обновляет текущий раздел и все связанные данные."""
        if self._current_section:
            self._current_section.save()
        self._reload_all()
        if hasattr(self._current_section, 'refresh_strategies'):
            self._current_section.refresh_strategies()
        self.statusBar().showMessage(tr("refreshed"), 2000)

    def _export_dna(self):
        """Экспортирует текущий язык в DNA-строку."""
        dna = encode_language(self._storage.lang)

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("dna_export_title"))
        dialog.setMinimumWidth(600)
        layout = QVBoxLayout(dialog)

        lbl = QLabel(tr("dna_export_hint"))
        layout.addWidget(lbl)

        dna_edit = QTextEdit()
        dna_edit.setText(dna)
        dna_edit.setReadOnly(True)
        dna_edit.setFixedHeight(80)
        layout.addWidget(dna_edit)

        copy_btn = QPushButton(tr("copy_to_clipboard"))
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(dna))
        layout.addWidget(copy_btn)

        show_json = QCheckBox(tr("dna_show_readable"))
        layout.addWidget(show_json)

        json_edit = QTextEdit()
        json_edit.setVisible(False)
        json_edit.setReadOnly(True)
        layout.addWidget(json_edit)

        def toggle_json(checked):
            if checked:
                json_edit.setText(encode_language_readable(self._storage.lang))
            json_edit.setVisible(checked)

        show_json.toggled.connect(toggle_json)

        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        bb.accepted.connect(dialog.accept)
        layout.addWidget(bb)

        dialog.exec()

    def _import_dna(self):
        """Импортирует язык из DNA-строки."""
        clipboard = QApplication.clipboard().text().strip()

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("dna_import_title"))
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)

        lbl = QLabel(tr("dna_import_hint"))
        layout.addWidget(lbl)

        dna_edit = QTextEdit()
        dna_edit.setPlaceholderText(tr("dna_import_ph"))
        if clipboard:
            dna_edit.setText(clipboard)
        layout.addWidget(dna_edit)

        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(dialog.accept)
        bb.rejected.connect(dialog.reject)
        layout.addWidget(bb)

        if dialog.exec():
            dna = dna_edit.toPlainText().strip()
            if dna:
                lang = decode_language(dna)
                if lang:
                    self._storage.lang = lang
                    self._storage.path = None
                    self._storage.dirty = False
                    self._reload_all()
                    self._update_title()
                    QMessageBox.information(self, tr("dna_import_title"), tr("dna_import_ok"))
                else:
                    QMessageBox.warning(self, tr("dna_import_title"), tr("dna_import_error"))

    def _load_preset(self, preset_id: str):
        """Загружает пресет языка."""
        preset = PRESETS.get(preset_id)
        if not preset:
            return

        dna = preset.get("dna")
        if not dna:
            return

        lang = decode_language(dna)
        if lang:
            self._storage.lang = lang
            self._storage.path = None
            self._storage.dirty = False
            self._reload_all()
            self._update_title()
            QMessageBox.information(self, tr("dna_import_title"),
                                   tr("dna_preset_loaded").format(preset["name"]))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    if _MISSING_DEPS:
        from PyQt6.QtWidgets import QMessageBox as QMessageBoxPre
        msg = QMessageBoxPre()
        msg.setWindowTitle("ConLang Studio")
        msg.setIcon(QMessageBoxPre.Icon.Warning)
        msg.setText("Некоторые функции будут недоступны:\n\n• " + "\n• ".join(_MISSING_DEPS))
        msg.setInformativeText("Рекомендуется установить недостающие библиотеки.\nПродолжить без них?")
        msg.setStandardButtons(QMessageBoxPre.StandardButton.Yes | QMessageBoxPre.StandardButton.No)
        msg.setDefaultButton(QMessageBoxPre.StandardButton.Yes)

        if msg.exec() == QMessageBoxPre.StandardButton.No:
            sys.exit(1)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())
