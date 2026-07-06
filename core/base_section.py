from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.i18n import tr
from core.storage import Storage


class BaseSection(QWidget):
    """
    Базовый класс для каждого раздела дерева навигации.
    Подклассы переопределяют:
      - build_ui()  — строит виджеты
      - load()      — заполняет из storage.lang
      - save()      — пишет в storage.lang (вызывается перед сменой раздела и сохранением)
      - retranslate() — обновляет все тексты при смене языка
    """

    def __init__(self, storage: Storage):
        super().__init__()
        self._s = storage
        self.build_ui()
        self.load()

    def build_ui(self):
        pass

    def load(self):
        pass

    def save(self):
        pass

    def retranslate(self):
        pass


class PlaceholderSection(BaseSection):
    """Заглушка для разделов, которые ещё не реализованы."""

    def build_ui(self):
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl = QLabel()
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl.setStyleSheet("color: gray; font-size: 14px;")
        lay.addWidget(self._lbl)

    def load(self):
        self._lbl.setText(tr("not_implemented"))

    def retranslate(self):
        self._lbl.setText(tr("not_implemented"))
