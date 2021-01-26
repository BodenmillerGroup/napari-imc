from abc import abstractmethod
from typing import Any, List, Optional


class IMCFileTreeItem:
    imc_file_tree_is_checkable = False

    def __init__(self):
        self._deleted = False

    @property
    @abstractmethod
    def _imc_file_tree_data(self) -> List[Any]:
        pass

    @property
    @abstractmethod
    def _imc_file_tree_parent(self) -> Optional['IMCFileTreeItem']:
        pass

    @property
    @abstractmethod
    def _imc_file_tree_children(self) -> List['IMCFileTreeItem']:
        pass

    @property
    def imc_file_tree_data(self) -> List[Any]:
        if self._deleted:
            return []
        return self._imc_file_tree_data

    @property
    def imc_file_tree_parent(self) -> Optional['IMCFileTreeItem']:
        if self._deleted:
            return None
        return self._imc_file_tree_parent

    @property
    def imc_file_tree_children(self) -> List['IMCFileTreeItem']:
        if self._deleted:
            return []
        return self._imc_file_tree_children

    @property
    def imc_file_tree_is_checked(self) -> bool:
        return False

    @imc_file_tree_is_checked.setter
    def imc_file_tree_is_checked(self, imc_file_tree_is_checked: bool):
        pass

    def mark_deleted(self):
        self._deleted = True
        for child in self._imc_file_tree_children:
            child.mark_deleted()


class ModelBase:
    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass
