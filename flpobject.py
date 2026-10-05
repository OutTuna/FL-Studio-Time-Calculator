# ---------------------------------------------------
#   Version: 2.0.0
#   Creators: Elliott Chimienti, Zane Little
#   Support us!: https://ko-fi.com/flhourcounterguys
# ---------------------------------------------------
#   Python 3.10
#   PyFLP 2.2.1
#   PySide6

import datetime, os
from project_sources import ProjectSource
from project_metadata import read_metadata
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem



# Custom object to hold information about parsed song
class FLP_Object():
    def __init__(self, file_path = None, relative_file_path = None):
        self.source = file_path if isinstance(file_path, ProjectSource) else None
        self.file_path = self.source.path if self.source else file_path
        self.error = None
        self.relative_path = relative_file_path
        self.file_name = self.path_to_array(relative_file_path)[-1]
        self.creation_date = None           # datetime
        self.project_hours = None           # float
        # self.total_num_notes              # int
        self.tree_item = None
        self.check_state = Qt.CheckState.Checked

    # Convert filepath from string to file array
    # Ex: "folder1/folder2/file1" == ["folder1","folder2","file1"]
    def path_to_array(self, path) -> list:
        # path_array = os.path.normpath(path)   # Normalize path
        return path.split(os.sep)
        
    # Parse song
    def parse(self):
        if self.file_path:  # If file path exists
            try:    # attempt to parse file
                if self.source:
                    with self.source.open() as stream:
                        temp = read_metadata(stream)
                else:
                    with open(self.file_path, "rb") as stream:
                        temp = read_metadata(stream)
                if temp.time_spent is None or temp.created_on is None:
                    raise ValueError("Project has no time metadata")
                self.project_hours = temp.time_spent/datetime.timedelta(hours=1) # Float
                self.creation_date = temp.created_on
                # total notes
                # other metrics                
            except Exception as exc:
                print("Error: Could not parse file ", self.file_name)
                self.error = str(exc)
                self.check_state = Qt.CheckState.Unchecked
                self.project_hours = 0

    # Create standard item for different trees
    def create_standard_item(self):
        if self.creation_date:  # If file could be parsed
            self.tree_item = QTreeWidgetItem([self.file_name,str("{:.2f}".format(self.project_hours)),str(self.creation_date.date())])
            self.tree_item.setCheckState(0,self.check_state)
        else:
            self.tree_item = QTreeWidgetItem([self.file_name,"",""])
            self.tree_item.setBackground(0,Qt.GlobalColor.red)
            self.tree_item.setToolTip(0, self.error or "Could not read project")

    # Update personal class state based on tree_items checkstate
    def update_state(self):
        if Qt.ItemFlag.ItemIsUserCheckable in self.tree_item.flags():
            self.check_state = self.tree_item.checkState(0)


