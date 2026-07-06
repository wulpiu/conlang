import json
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

from core.model import Language


class Storage(QObject):
    # Сигналы для динамического обновления интерфейса
    data_changed = pyqtSignal()          # Общее изменение данных
    morpheme_types_changed = pyqtSignal() # Изменение типов морфем
    strategies_changed = pyqtSignal()     # Изменение стратегий языка

    def __init__(self):
        super().__init__()
        self.path: Path | None = None
        self.lang = Language()
        self.dirty = False  # есть несохранённые изменения

    def new(self):
        self.path = None
        self.lang = Language()
        self.dirty = False

    def load(self, path: str | Path) -> bool:
        try:
            p = Path(path)
            with open(p, encoding="utf-8") as f:
                self.lang = Language.from_dict(json.load(f))
            self.path = p
            self.dirty = False
            self.data_changed.emit()
            return True
        except Exception as e:
            print(f"[Storage.load] {e}")
            return False

    def save(self, path: str | Path | None = None) -> bool:
        target = Path(path) if path else self.path
        if not target:
            return False
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                json.dump(self.lang.to_dict(), f, ensure_ascii=False, indent=2)
            self.path = target
            self.dirty = False
            return True
        except Exception as e:
            print(f"[Storage.save] {e}")
            return False

    def mark_dirty(self):
        self.dirty = True
        self.data_changed.emit()

    def mark_morpheme_types_changed(self):
        """Вызвать при изменении чекбоксов в «Типах морфем»."""
        self.mark_dirty()
        self.morpheme_types_changed.emit()

    def mark_strategies_changed(self):
        """Вызвать при изменении стратегий в «Типе языка»."""
        self.mark_dirty()
        self.strategies_changed.emit()
