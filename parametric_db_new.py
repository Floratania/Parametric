# # # import os
# # # import json
# # # import hashlib
# # # import datetime as dt
# # # from typing import Any, Dict, List, Optional

# # # import pyodbc
# # # from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout


# # # class LoginDialog(QDialog):
# # #     def __init__(self, parent=None, message="Вхід"):
# # #         super().__init__(parent)
# # #         self.setWindowTitle("Авторизація")
# # #         layout = QVBoxLayout(self)
# # #         layout.addWidget(QLabel(message))
# # #         self.username_input = QLineEdit()
# # #         self.username_input.setPlaceholderText("Логін")
# # #         self.password_input = QLineEdit()
# # #         self.password_input.setPlaceholderText("Пароль")
# # #         self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
# # #         layout.addWidget(self.username_input)
# # #         layout.addWidget(self.password_input)
# # #         buttons = QHBoxLayout()
# # #         btn_ok = QPushButton("Увійти")
# # #         btn_cancel = QPushButton("Скасувати")
# # #         btn_ok.clicked.connect(self.accept)
# # #         btn_cancel.clicked.connect(self.reject)
# # #         buttons.addWidget(btn_ok)
# # #         buttons.addWidget(btn_cancel)
# # #         layout.addLayout(buttons)

# # #     def credentials(self):
# # #         return self.username_input.text().strip(), self.password_input.text()


# # # def get_sql_driver():
# # #     drivers = [d for d in pyodbc.drivers()]
# # #     for name in [
# # #         "SQL Server",
# # #         "ODBC Driver 18 for SQL Server",
# # #         "ODBC Driver 17 for SQL Server",
# # #         "SQL Server Native Client 11.0",
# # #     ]:
# # #         if name in drivers:
# # #             return name
# # #     raise RuntimeError(f"Не знайдено SQL Server ODBC driver. Є тільки: {drivers}")

# # # class ParametricDb:
# # #     """
# # #     MSSQL storage for MiniCAD.
# # #     Main source of truth: SQL Server.
# # #     JSON is only manual backup/export.
# # #     """

# # #     def __init__(self):
# # #         self.server = os.getenv("PARAMETRIC_DB_SERVER", "prog-srv")
# # #         self.database = os.getenv("PARAMETRIC_DB_NAME", "parametric_db")
# # #         self.username = os.getenv("PARAMETRIC_DB_USER", "sa")
# # #         self.password = os.getenv("PARAMETRIC_DB_PASSWORD", "*Htlbcrf2oo6")
# # #         self.trusted = os.getenv("PARAMETRIC_DB_TRUSTED", "0") == "1"
# # #         self.driver = os.getenv("PARAMETRIC_DB_DRIVER") or get_sql_driver()
# # #         self.available = False
# # #         self.last_error = ""
# # #         self._check_connection()



# # #     def connection_string(self) -> str:
# # #         base = f"DRIVER={{{self.driver}}};SERVER={self.server};DATABASE={self.database};TrustServerCertificate=yes;"
# # #         # if self.trusted:
# # #         #     return base + "Trusted_Connection=yes;"
# # #         return base + f"UID={self.username};PWD={self.password};"

# # #     def connect(self):
# # #         return pyodbc.connect(self.connection_string(), autocommit=False)

# # #     def _check_connection(self) -> bool:
# # #         try:
# # #             with self.connect() as conn:
# # #                 conn.cursor().execute("SELECT 1")
# # #             self.available = True
# # #             self.last_error = ""
# # #             return True
# # #         except Exception as exc:
# # #             self.available = False
# # #             self.last_error = str(exc)
# # #             return False

# # #     @staticmethod
# # #     def hash_password(password: str) -> str:
# # #         # For local desktop app. Later you can replace with bcrypt/argon2.
# # #         return hashlib.sha256(password.encode("utf-8")).hexdigest()

# # #     def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
# # #         sql = """
# # #         SELECT Id, Username, FullName, IsActive
# # #         FROM dbo.Users
# # #         WHERE Username = ? AND PasswordHash = ? AND IsActive = 1
# # #         """
# # #         with self.connect() as conn:
# # #             cur = conn.cursor()
# # #             row = cur.execute(sql, username, self.hash_password(password)).fetchone()
# # #             if not row:
              
# # #                 row = cur.execute(sql, username, password).fetchone()
# # #             if not row:
# # #                 return None
# # #             return {"id": int(row.Id), "username": row.Username, "full_name": row.FullName}

# # #     def _scalar(self, cur, sql: str, *params):
# # #         row = cur.execute(sql, *params).fetchone()
# # #         return row[0] if row else None

# # #     def _to_float(self, value):
# # #         return None if value is None else float(value)

# # #     def save_project_snapshot(
# # #         self,
# # #         project_dir: str,
# # #         dxf_path: str,
# # #         project_meta: Dict[str, Any],
# # #         parametric_groups: List[Dict[str, Any]],
# # #         block_keep_state: Dict[str, bool],
# # #         user_id: int,
# # #         status: str = "ConfigSaved",
# # #         project_file_id: Optional[int] = None,
# # #     ) -> Optional[int]:
# # #         """Upsert DXF binary + all parametric settings. Does NOT save target sizes."""
# # #         if not os.path.exists(dxf_path):
# # #             self.last_error = f"DXF не знайдено: {dxf_path}"
# # #             return None

# # #         try:
# # #             with open(dxf_path, "rb") as f:
# # #                 file_data = f.read()

# # #             file_name = os.path.basename(dxf_path)
# # #             local_path = os.path.abspath(dxf_path)
# # #             ext = os.path.splitext(file_name)[1] or ".dxf"
# # #             text = project_meta.get("door_text") or {}

# # #             with self.connect() as conn:
# # #                 cur = conn.cursor()

# # #                 if project_file_id is None:
# # #                     project_file_id = self._scalar(
# # #                         cur,
# # #                         "SELECT TOP 1 Id FROM dbo.ProjectFiles WHERE LocalPath = ? ORDER BY Id DESC",
# # #                         local_path,
# # #                     )

# # #                 if project_file_id is None:
# # #                     cur.execute(
# # #                         """
# # #                         INSERT INTO dbo.ProjectFiles
# # #                         (FileName, FileExtension, LocalPath, FileData,
# # #                          SourceWidth, SourceHeight, SourceDoorOpening, CurrentDoorOpening,
# # #                          GrowthAxis, AxisLinkMode, LinkX, LinkY,
# # #                          Status, CreatedByUserId, CreatedAt)
# # #                         OUTPUT INSERTED.Id
# # #                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
# # #                         """,
# # #                         file_name, ext, local_path, pyodbc.Binary(file_data),
# # #                         project_meta.get("source_width"),
# # #                         project_meta.get("source_height"),
# # #                         project_meta.get("source_door_opening") or project_meta.get("door_opening") or "left",
# # #                         project_meta.get("door_opening") or project_meta.get("source_door_opening") or "left",
# # #                         project_meta.get("growth_axis") or "both",
# # #                         project_meta.get("axis_link_mode") or "normal",
# # #                         project_meta.get("link_x") or "X = W",
# # #                         project_meta.get("link_y") or "Y = H",
# # #                         status,
# # #                         user_id,
# # #                     )
# # #                     project_file_id = int(cur.fetchone()[0])
# # #                 else:
# # #                     cur.execute(
# # #                         """
# # #                         UPDATE dbo.ProjectFiles
# # #                         SET FileName = ?, FileExtension = ?, LocalPath = ?, FileData = ?,
# # #                             SourceWidth = ?, SourceHeight = ?,
# # #                             SourceDoorOpening = ?, CurrentDoorOpening = ?,
# # #                             GrowthAxis = ?, AxisLinkMode = ?, LinkX = ?, LinkY = ?,
# # #                             Status = ?, UpdatedByUserId = ?, UpdatedAt = SYSDATETIME()
# # #                         WHERE Id = ?
# # #                         """,
# # #                         file_name, ext, local_path, pyodbc.Binary(file_data),
# # #                         project_meta.get("source_width"),
# # #                         project_meta.get("source_height"),
# # #                         project_meta.get("source_door_opening") or project_meta.get("door_opening") or "left",
# # #                         project_meta.get("door_opening") or project_meta.get("source_door_opening") or "left",
# # #                         project_meta.get("growth_axis") or "both",
# # #                         project_meta.get("axis_link_mode") or "normal",
# # #                         project_meta.get("link_x") or "X = W",
# # #                         project_meta.get("link_y") or "Y = H",
# # #                         status,
# # #                         user_id,
# # #                         project_file_id,
# # #                     )

# # #                 cur.execute("DELETE FROM dbo.ProjectTextSettings WHERE ProjectFileId = ?", project_file_id)
# # #                 cur.execute(
# # #                     """
# # #                     INSERT INTO dbo.ProjectTextSettings
# # #                     (ProjectFileId, Enabled, TextValue, X, Y, Height, WidthFactor, Rotation, FontName, EntityHandle)
# # #                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# # #                     """,
# # #                     project_file_id,
# # #                     1 if text.get("enabled") else 0,
# # #                     text.get("text") or "",
# # #                     text.get("x") or 0,
# # #                     text.get("y") or 0,
# # #                     text.get("height") or 30,
# # #                     text.get("width_factor") or 120,
# # #                     text.get("rotation") or 0,
# # #                     text.get("font") or "STANDARD",
# # #                     text.get("handle"),
# # #                 )

# # #                 cur.execute("DELETE FROM dbo.ProjectGroupEntities WHERE ProjectGroupId IN (SELECT Id FROM dbo.ProjectGroups WHERE ProjectFileId = ?)", project_file_id)
# # #                 cur.execute("DELETE FROM dbo.ProjectGroups WHERE ProjectFileId = ?", project_file_id)
# # #                 cur.execute("DELETE FROM dbo.ProjectBlockStates WHERE ProjectFileId = ?", project_file_id)

# # #                 for sort_order, group in enumerate(parametric_groups):
# # #                     handles = sorted(str(h) for h in group.get("handles", []))
# # #                     uid = group.get("uid") or f"{group.get('name', 'group')}|{','.join(handles)}"
# # #                     keep = 1 if block_keep_state.get(uid, True) else 0
# # #                     cur.execute(
# # #                         """
# # #                         INSERT INTO dbo.ProjectGroups
# # #                         (ProjectFileId, Name, Uid,
# # #                          K_W, K_H, Growth_P_W, Growth_P_H,
# # #                          Growth_Dir_X, Growth_Dir_Y, Shift_Dir_X, Shift_Dir_Y,
# # #                          Link_X, Link_Y, Resizes, IsKeep, SortOrder, CreatedAt)
# # #                         OUTPUT INSERTED.Id
# # #                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
# # #                         """,
# # #                         project_file_id,
# # #                         group.get("name") or "Група",
# # #                         uid,
# # #                         group.get("k_w") or 0,
# # #                         group.get("k_h") or 0,
# # #                         group.get("growth_p_w") or 0,
# # #                         group.get("growth_p_h") or 0,
# # #                         group.get("growth_dir_x") or "Центр",
# # #                         group.get("growth_dir_y") or "Центр",
# # #                         group.get("shift_dir_x") or "Вправо",
# # #                         group.get("shift_dir_y") or "Вгору",
# # #                         group.get("link_x") or "X = W",
# # #                         group.get("link_y") or "Y = H",
# # #                         1 if group.get("resizes") else 0,
# # #                         keep,
# # #                         sort_order,
# # #                     )
# # #                     group_id = int(cur.fetchone()[0])
# # #                     for handle in handles:
# # #                         cur.execute(
# # #                             "INSERT INTO dbo.ProjectGroupEntities (ProjectGroupId, EntityHandle) VALUES (?, ?)",
# # #                             group_id,
# # #                             handle,
# # #                         )
# # #                     cur.execute(
# # #                         "INSERT INTO dbo.ProjectBlockStates (ProjectFileId, BlockKey, BlockName, IsKeep) VALUES (?, ?, ?, ?)",
# # #                         project_file_id,
# # #                         uid,
# # #                         group.get("name") or "Група",
# # #                         keep,
# # #                     )

# # #                 cur.execute(
# # #                     "INSERT INTO dbo.ActionLog (UserId, ActionType, EntityType, EntityId, Details) VALUES (?, ?, ?, ?, ?)",
# # #                     user_id,
# # #                     status,
# # #                     "ProjectFile",
# # #                     str(project_file_id),
# # #                     f"Saved {file_name}",
# # #                 )
# # #                 conn.commit()
# # #                 return project_file_id
# # #         except Exception as exc:
# # #             self.last_error = str(exc)
# # #             return None

# # #     def load_project_config(self, dxf_path: str = None, project_file_id: int = None) -> Optional[Dict[str, Any]]:
# # #         """Load metadata/groups from DB. Target sizes are intentionally not loaded from ProjectFiles."""
# # #         try:
# # #             local_path = os.path.abspath(dxf_path) if dxf_path else None
# # #             with self.connect() as conn:
# # #                 cur = conn.cursor()
# # #                 if project_file_id is None and local_path:
# # #                     project_file_id = self._scalar(
# # #                         cur,
# # #                         "SELECT TOP 1 Id FROM dbo.ProjectFiles WHERE LocalPath = ? ORDER BY Id DESC",
# # #                         local_path,
# # #                     )
# # #                 if project_file_id is None:
# # #                     return None

# # #                 row = cur.execute("SELECT * FROM dbo.ProjectFiles WHERE Id = ?", project_file_id).fetchone()
# # #                 if not row:
# # #                     return None

# # #                 meta = {
# # #                     "source_width": self._to_float(row.SourceWidth),
# # #                     "source_height": self._to_float(row.SourceHeight),
# # #                     "target_width": self._to_float(row.SourceWidth),
# # #                     "target_height": self._to_float(row.SourceHeight),
# # #                     "door_opening": row.CurrentDoorOpening or row.SourceDoorOpening or "left",
# # #                     "source_door_opening": row.SourceDoorOpening or row.CurrentDoorOpening or "left",
# # #                     "target_door_opening": row.CurrentDoorOpening or row.SourceDoorOpening or "left",
# # #                     "growth_axis": row.GrowthAxis or "both",
# # #                     "axis_link_mode": row.AxisLinkMode or "normal",
# # #                     "link_x": row.LinkX or "X = W",
# # #                     "link_y": row.LinkY or "Y = H",
# # #                 }

# # #                 t = cur.execute("SELECT * FROM dbo.ProjectTextSettings WHERE ProjectFileId = ?", project_file_id).fetchone()
# # #                 meta["door_text"] = {
# # #                     "enabled": bool(t.Enabled) if t else False,
# # #                     "text": t.TextValue if t else "",
# # #                     "x": self._to_float(t.X) if t else 0.0,
# # #                     "y": self._to_float(t.Y) if t else 0.0,
# # #                     "height": self._to_float(t.Height) if t else 30.0,
# # #                     "width_factor": self._to_float(t.WidthFactor) if t else 120.0,
# # #                     "rotation": self._to_float(t.Rotation) if t else 0.0,
# # #                     "font": t.FontName if t else "STANDARD",
# # #                     "handle": t.EntityHandle if t else None,
# # #                 }

# # #                 groups = []
# # #                 group_rows = cur.execute(
# # #                     "SELECT * FROM dbo.ProjectGroups WHERE ProjectFileId = ? ORDER BY SortOrder, Id",
# # #                     project_file_id,
# # #                 ).fetchall()
# # #                 block_keep_state = {}
# # #                 for gr in group_rows:
# # #                     handles = {
# # #                         r.EntityHandle
# # #                         for r in cur.execute("SELECT EntityHandle FROM dbo.ProjectGroupEntities WHERE ProjectGroupId = ?", gr.Id).fetchall()
# # #                     }
# # #                     group = {
# # #                         "uid": gr.Uid,
# # #                         "name": gr.Name,
# # #                         "handles": handles,
# # #                         "k_w": float(gr.K_W or 0),
# # #                         "k_h": float(gr.K_H or 0),
# # #                         "growth_p_w": float(gr.Growth_P_W or 0),
# # #                         "growth_p_h": float(gr.Growth_P_H or 0),
# # #                         "growth_dir_x": gr.Growth_Dir_X or "Центр",
# # #                         "growth_dir_y": gr.Growth_Dir_Y or "Центр",
# # #                         "shift_dir_x": gr.Shift_Dir_X or "Вправо",
# # #                         "shift_dir_y": gr.Shift_Dir_Y or "Вгору",
# # #                         "link_x": gr.Link_X or "X = W",
# # #                         "link_y": gr.Link_Y or "Y = H",
# # #                         "resizes": bool(gr.Resizes),
# # #                     }
# # #                     groups.append(group)
# # #                     block_keep_state[gr.Uid] = bool(gr.IsKeep)

# # #                 return {"project_file_id": project_file_id, "meta": meta, "groups": groups, "block_keep_state": block_keep_state}
# # #         except Exception as exc:
# # #             self.last_error = str(exc)
# # #             return None

# # #     def export_project_json_backup(self, project_file_id: int, data: Dict[str, Any], user_id: int, backup_type="ManualExport") -> bool:
# # #         try:
# # #             safe = json.dumps(data, ensure_ascii=False, indent=4, default=list)
# # #             with self.connect() as conn:
# # #                 conn.cursor().execute(
# # #                     """
# # #                     INSERT INTO dbo.ProjectJsonBackups (ProjectFileId, JsonData, BackupType, CreatedByUserId, CreatedAt)
# # #                     VALUES (?, ?, ?, ?, SYSDATETIME())
# # #                     """,
# # #                     project_file_id,
# # #                     safe,
# # #                     backup_type,
# # #                     user_id,
# # #                 )
# # #                 conn.commit()
# # #             return True
# # #         except Exception as exc:
# # #             self.last_error = str(exc)
# # #             return False

# # #     def save_export_file(self, source_project_file_id: int, export_path: str, width: float, height: float, opening: str, user_id: int) -> bool:
# # #         try:
# # #             with open(export_path, "rb") as f:
# # #                 file_data = f.read()
# # #             with self.connect() as conn:
# # #                 conn.cursor().execute(
# # #                     """
# # #                     INSERT INTO dbo.ProjectExports
# # #                     (SourceProjectFileId, ExportFileName, ExportFileData, ExportWidth, ExportHeight, ExportDoorOpening, CreatedByUserId, CreatedAt)
# # #                     VALUES (?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
# # #                     """,
# # #                     source_project_file_id,
# # #                     os.path.basename(export_path),
# # #                     pyodbc.Binary(file_data),
# # #                     width,
# # #                     height,
# # #                     opening,
# # #                     user_id,
# # #                 )
# # #                 conn.commit()
# # #             return True
# # #         except Exception as exc:
# # #             self.last_error = str(exc)
# # #             return False
# # import os
# # import json
# # import hashlib
# # from typing import Any, Dict, List, Optional

# # import pyodbc
# # from PySide6.QtWidgets import (
# #     QDialog,
# #     QVBoxLayout,
# #     QLabel,
# #     QLineEdit,
# #     QPushButton,
# #     QHBoxLayout,
# # )


# # class LoginDialog(QDialog):
# #     def __init__(self, parent=None, message="Вхід"):
# #         super().__init__(parent)
# #         self.setWindowTitle("Авторизація")

# #         layout = QVBoxLayout(self)
# #         layout.addWidget(QLabel(message))

# #         self.username_input = QLineEdit()
# #         self.username_input.setPlaceholderText("Логін")

# #         self.password_input = QLineEdit()
# #         self.password_input.setPlaceholderText("Пароль")
# #         self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

# #         layout.addWidget(self.username_input)
# #         layout.addWidget(self.password_input)

# #         buttons = QHBoxLayout()
# #         btn_ok = QPushButton("Увійти")
# #         btn_cancel = QPushButton("Скасувати")

# #         btn_ok.clicked.connect(self.accept)
# #         btn_cancel.clicked.connect(self.reject)

# #         buttons.addWidget(btn_ok)
# #         buttons.addWidget(btn_cancel)
# #         layout.addLayout(buttons)

# #     def credentials(self):
# #         return self.username_input.text().strip(), self.password_input.text()


# # def get_sql_driver() -> str:
# #     drivers = [d for d in pyodbc.drivers()]
# #     preferred = [
# #         "ODBC Driver 18 for SQL Server",
# #         "ODBC Driver 17 for SQL Server",
# #         "SQL Server Native Client 11.0",
# #         "SQL Server",
# #     ]

# #     for name in preferred:
# #         if name in drivers:
# #             return name

# #     raise RuntimeError(f"Не знайдено SQL Server ODBC driver. Доступні драйвери: {drivers}")


# # class ParametricDb:
# #     """
# #     MSSQL storage for MiniCAD.

# #     Нова структура:
# #         DoorModels      = одна папка / одна модель дверей
# #         ProjectFiles    = DXF-файли цієї моделі
# #         ProjectGroups   = параметричні групи конкретного DXF
# #         ProjectExports  = історія експортованих DXF

# #     JSON не є основним сховищем. JSON використовується тільки для backup/export.
# #     """

# #     def __init__(self):
# #         self.server = os.getenv("PARAMETRIC_DB_SERVER", "prog-srv")
# #         self.database = os.getenv("PARAMETRIC_DB_NAME", "parametric_db")
# #         self.username = os.getenv("PARAMETRIC_DB_USER", "sa")
# #         self.password = os.getenv("PARAMETRIC_DB_PASSWORD", "*Htlbcrf2oo6")
# #         self.trusted = os.getenv("PARAMETRIC_DB_TRUSTED", "0") == "1"
# #         self.driver = os.getenv("PARAMETRIC_DB_DRIVER") or get_sql_driver()

# #         self.available = False
# #         self.last_error = ""
# #         self._check_connection()

# #     def connection_string(self) -> str:
# #         base = (
# #             f"DRIVER={{{self.driver}}};"
# #             f"SERVER={self.server};"
# #             f"DATABASE={self.database};"
# #             "TrustServerCertificate=yes;"
# #         )

# #         if self.trusted:
# #             return base + "Trusted_Connection=yes;"

# #         return base + f"UID={self.username};PWD={self.password};"

# #     def connect(self):
# #         return pyodbc.connect(self.connection_string(), autocommit=False)

# #     def _check_connection(self) -> bool:
# #         try:
# #             with self.connect() as conn:
# #                 conn.cursor().execute("SELECT 1")
# #             self.available = True
# #             self.last_error = ""
# #             return True
# #         except Exception as exc:
# #             self.available = False
# #             self.last_error = str(exc)
# #             return False
        
# #     def register_folder_dxf_files(
# #         self,
# #         folder_path,
# #         project_meta,
# #         user_id,
# #         door_model_id=None,
# #     ):
# #         """
# #         Реєструє папку як DoorModel та всі DXF файли всередині.
# #         """

# #         if door_model_id:
# #             model_id = door_model_id
# #         else:
# #             model_id = self.get_or_create_door_model(
# #                 folder_path=folder_path,
# #                 model_name=os.path.basename(folder_path),
# #                 source_width=project_meta.get("source_width"),
# #                 source_height=project_meta.get("source_height"),
# #                 source_door_opening=project_meta.get("door_opening", "left"),
# #                 user_id=user_id,
# #                 growth_axis=project_meta.get("growth_axis", "both"),
# #                 axis_link_mode=project_meta.get("axis_link_mode", "normal"),
# #                 link_x=project_meta.get("link_x", "X = W"),
# #                 link_y=project_meta.get("link_y", "Y = H"),
# #             )

# #         door_model_id = model_id

# #         if not door_model_id:
# #             return None

# #         with self.connect() as conn:
# #             cur = conn.cursor()

# #             for file_name in os.listdir(folder_path):

# #                 if not file_name.lower().endswith(".dxf"):
# #                     continue

# #                 full_path = os.path.join(folder_path, file_name)

# #                 with open(full_path, "rb") as f:
# #                     data = f.read()

# #                 existing = self._scalar(
# #                     cur,
# #                     """
# #                     SELECT TOP 1 Id
# #                     FROM ProjectFiles
# #                     WHERE DoorModelId = ?
# #                     AND FileName = ?
# #                     """,
# #                     door_model_id,
# #                     file_name,
# #                 )

# #                 if existing:
# #                     cur.execute(
# #                         """
# #                         UPDATE dbo.ProjectFiles
# #                         SET
# #                             SourceWidth = ?,
# #                             SourceHeight = ?,
# #                             SourceDoorOpening = ?,
# #                             CurrentDoorOpening = ?,
# #                             GrowthAxis = ?,
                     
         
# #                             UpdatedByUserId = ?,
# #                             UpdatedAt = SYSDATETIME()
# #                         WHERE Id = ?
# #                         """,
# #                         project_meta.get("source_width"),
# #                         project_meta.get("source_height"),
# #                         project_meta.get("source_door_opening") or project_meta.get("door_opening", "left"),
# #                         project_meta.get("door_opening", "left"),
# #                         project_meta.get("growth_axis", "both"),
# #                         # project_meta.get("axis_link_mode", "normal"),
# #                         # project_meta.get("link_x", "X = W"),
# #                         # project_meta.get("link_y", "Y = H"),
# #                         user_id,
# #                         existing,
# #                     )
# #                     continue

# #                 cur.execute(
# #                     """
# #                     INSERT INTO dbo.ProjectFiles
# #                     (
# #                         DoorModelId,
# #                         FileName,
# #                         FileExtension,
# #                         FileData,

# #                         SourceWidth,
# #                         SourceHeight,
# #                         SourceDoorOpening,
# #                         CurrentDoorOpening,
# #                         GrowthAxis,
                
  

# #                         Status,
# #                         CreatedByUserId,
# #                         CreatedAt
# #                     )
# #                     VALUES
# #                     (
# #                         ?, ?, '.dxf', ?,
# #                         ?, ?, ?, ?,
# #                         ?, 
# #                         'Registered',
# #                         ?, SYSDATETIME()
# #                     )
# #                     """,
# #                     door_model_id,
# #                     file_name,
# #                     pyodbc.Binary(data),

# #                     project_meta.get("source_width"),
# #                     project_meta.get("source_height"),
# #                     project_meta.get("source_door_opening") or project_meta.get("door_opening", "left"),
# #                     project_meta.get("door_opening", "left"),
# #                     project_meta.get("growth_axis", "both"),
# #                     project_meta.get("axis_link_mode", "normal"),
# #                     # project_meta.get("link_x", "X = W"),
# #                     # project_meta.get("link_y", "Y = H"),

# #                     user_id,
# #                 )

    

# #             conn.commit()

# #         return door_model_id

# #     @staticmethod
# #     def hash_password(password: str) -> str:
# #         return hashlib.sha256(password.encode("utf-8")).hexdigest()

# #     @staticmethod
# #     def _to_float(value):
# #         return None if value is None else float(value)

# #     @staticmethod
# #     def _row_to_dict(row) -> Dict[str, Any]:
# #         if row is None:
# #             return {}
# #         return {column[0]: getattr(row, column[0]) for column in row.cursor_description}

# #     def _scalar(self, cur, sql: str, *params):
# #         row = cur.execute(sql, *params).fetchone()
# #         return row[0] if row else None

# #     # ============================================================
# #     # AUTH
# #     # ============================================================

# #     def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
# #         sql = """
# #         SELECT Id, Username, FullName, IsActive
# #         FROM dbo.Users
# #         WHERE Username = ? AND PasswordHash = ? AND IsActive = 1
# #         """

# #         with self.connect() as conn:
# #             cur = conn.cursor()

# #             row = cur.execute(sql, username, self.hash_password(password)).fetchone()

# #             # Тимчасово дозволяє старий plain text пароль під час міграції.
# #             if not row:
# #                 row = cur.execute(sql, username, password).fetchone()

# #             if not row:
# #                 return None

# #             return {
# #                 "id": int(row.Id),
# #                 "username": row.Username,
# #                 "full_name": row.FullName,
# #             }

# #     # ============================================================
# #     # DOOR MODEL
# #     # ============================================================

# #     def get_or_create_door_model(
# #         self,
# #         folder_path: str,
# #         model_name: Optional[str],
# #         source_width: Optional[float],
# #         source_height: Optional[float],
# #         source_door_opening: str,
# #         user_id: int,
# #         growth_axis: str = "both",
# #         axis_link_mode: str = "normal",
# #         link_x: str = "X = W",
# #         link_y: str = "Y = H",
# #     ) -> Optional[int]:
# #         """
# #         Одна папка = одна DoorModel.

# #         Якщо модель для SourceFolderPath вже існує — оновлюємо базові параметри,
# #         але не створюємо дубль.
# #         """
# #         try:
# #             folder_path = os.path.abspath(folder_path)
# #             model_name = model_name or os.path.basename(folder_path) or "DoorModel"

# #             with self.connect() as conn:
# #                 cur = conn.cursor()

# #                 model_id = self._scalar(
# #                     cur,
# #                     """
# #                     SELECT TOP 1 Id
# #                     FROM dbo.DoorModels
# #                     WHERE SourceFolderPath = ?
# #                     ORDER BY Id DESC
# #                     """,
# #                     folder_path,
# #                 )

# #                 if model_id is None:
# #                     cur.execute(
# #                         """
# #                         INSERT INTO dbo.DoorModels
# #                         (
# #                             ModelName,
# #                             SourceFolderPath,
# #                             SourceWidth,
# #                             SourceHeight,
# #                             SourceDoorOpening,
# #                             GrowthAxis,
# #                             AxisLinkMode,
# #                             LinkX,
# #                             LinkY,
# #                             CreatedByUserId,
# #                             CreatedAt
# #                         )
# #                         OUTPUT INSERTED.Id
# #                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
# #                         """,
# #                         model_name,
# #                         folder_path,
# #                         source_width,
# #                         source_height,
# #                         source_door_opening or "left",
# #                         growth_axis or "both",
# #                         axis_link_mode or "normal",
# #                         link_x or "X = W",
# #                         link_y or "Y = H",
# #                         user_id,
# #                     )
# #                     model_id = int(cur.fetchone()[0])
# #                 else:
# #                     cur.execute(
# #                         """
# #                         UPDATE dbo.DoorModels
# #                         SET
# #                             ModelName = ?,
# #                             SourceWidth = COALESCE(?, SourceWidth),
# #                             SourceHeight = COALESCE(?, SourceHeight),
# #                             SourceDoorOpening = COALESCE(?, SourceDoorOpening),
# #                             GrowthAxis = COALESCE(?, GrowthAxis),
# #                             AxisLinkMode = COALESCE(?, AxisLinkMode),
# #                             LinkX = COALESCE(?, LinkX),
# #                             LinkY = COALESCE(?, LinkY),
# #                             UpdatedByUserId = ?,
# #                             UpdatedAt = SYSDATETIME()
# #                         WHERE Id = ?
# #                         """,
# #                         model_name,
# #                         source_width,
# #                         source_height,
# #                         source_door_opening or "left",
# #                         growth_axis or "both",
# #                         axis_link_mode or "normal",
# #                         link_x or "X = W",
# #                         link_y or "Y = H",
# #                         user_id,
# #                         model_id,
# #                     )

# #                 conn.commit()
# #                 return int(model_id)

# #         except Exception as exc:
# #             self.last_error = str(exc)
# #             return None

# #     def update_door_model_from_meta(
# #         self,
# #         door_model_id: int,
# #         project_meta: Dict[str, Any],
# #         user_id: int,
# #     ) -> bool:
# #         try:
# #             with self.connect() as conn:
# #                 conn.cursor().execute(
# #                     """
# #                     UPDATE dbo.DoorModels
# #                     SET
# #                         SourceWidth = ?,
# #                         SourceHeight = ?,
# #                         SourceDoorOpening = ?,
# #                         GrowthAxis = ?,
# #                         AxisLinkMode = ?,
# #                         LinkX = ?,
# #                         LinkY = ?,
# #                         UpdatedByUserId = ?,
# #                         UpdatedAt = SYSDATETIME()
# #                     WHERE Id = ?
# #                     """,
# #                     project_meta.get("source_width"),
# #                     project_meta.get("source_height"),
# #                     project_meta.get("source_door_opening") or project_meta.get("door_opening") or "left",
# #                     project_meta.get("growth_axis") or "both",
# #                     project_meta.get("axis_link_mode") or "normal",
# #                     project_meta.get("link_x") or "X = W",
# #                     project_meta.get("link_y") or "Y = H",
# #                     user_id,
# #                     door_model_id,
# #                 )
# #                 conn.commit()
# #             return True
# #         except Exception as exc:
# #             self.last_error = str(exc)
# #             return False

# #     def load_door_model(self, door_model_id: int) -> Optional[Dict[str, Any]]:
# #         try:
# #             with self.connect() as conn:
# #                 cur = conn.cursor()

# #                 model = cur.execute(
# #                     """
# #                     SELECT *
# #                     FROM dbo.DoorModels
# #                     WHERE Id = ?
# #                     """,
# #                     door_model_id,
# #                 ).fetchone()

# #                 if not model:
# #                     return None

# #                 files = cur.execute(
# #                     """
# #                     SELECT Id, FileName, FileExtension, DoorModelId, Status, CreatedAt, UpdatedAt
# #                     FROM dbo.ProjectFiles
# #                     WHERE DoorModelId = ?
# #                     ORDER BY FileName
# #                     """,
# #                     door_model_id,
# #                 ).fetchall()

# #                 model_meta = {
# #                     "source_width": self._to_float(model.SourceWidth),
# #                     "source_height": self._to_float(model.SourceHeight),
# #                     "target_width": self._to_float(model.SourceWidth),
# #                     "target_height": self._to_float(model.SourceHeight),
# #                     "door_opening": model.SourceDoorOpening or "left",
# #                     "source_door_opening": model.SourceDoorOpening or "left",
# #                     "target_door_opening": model.SourceDoorOpening or "left",
# #                     "growth_axis": model.GrowthAxis or "both",
# #                     "axis_link_mode": model.AxisLinkMode or "normal",
# #                     "link_x": model.LinkX or "X = W",
# #                     "link_y": model.LinkY or "Y = H",
# #                 }

# #                 return {
# #                     "id": int(model.Id),
# #                     "model_name": model.ModelName,
# #                     "folder_path": model.SourceFolderPath,
# #                     "meta": model_meta,
# #                     "files": [
# #                         {
# #                             "id": int(row.Id),
# #                             "file_name": row.FileName,
# #                             "extension": row.FileExtension,
# #                             "door_model_id": int(row.DoorModelId) if row.DoorModelId else None,
# #                             "status": row.Status,
# #                         }
# #                         for row in files
# #                     ],
# #                 }

# #         except Exception as exc:
# #             self.last_error = str(exc)
# #             return None

# #     def find_door_model_by_folder(self, folder_path: str) -> Optional[int]:
# #         try:
# #             folder_path = os.path.abspath(folder_path)
# #             with self.connect() as conn:
# #                 cur = conn.cursor()
# #                 value = self._scalar(
# #                     cur,
# #                     """
# #                     SELECT TOP 1 Id
# #                     FROM dbo.DoorModels
# #                     WHERE SourceFolderPath = ?
# #                     ORDER BY Id DESC
# #                     """,
# #                     folder_path,
# #                 )
# #                 return int(value) if value is not None else None
# #         except Exception as exc:
# #             self.last_error = str(exc)
# #             return None

# #     # ============================================================
# #     # PROJECT FILE
# #     # ============================================================

# #     def save_project_snapshot(
# #         self,
# #         project_dir: str,
# #         dxf_path: str,
# #         project_meta: Dict[str, Any],
# #         parametric_groups: List[Dict[str, Any]],
# #         block_keep_state: Dict[str, bool],
# #         user_id: int,
# #         status: str = "ConfigSaved",
# #         project_file_id: Optional[int] = None,
# #         door_model_id: Optional[int] = None,
# #     ) -> Optional[int]:
# #         """
# #         Upsert поточного DXF + його групи.

# #         Спільні параметри моделі пишуться в DoorModels.
# #         TargetWidth/TargetHeight не пишуться в ProjectFiles як постійний стан.
# #         """
# #         if not os.path.exists(dxf_path):
# #             self.last_error = f"DXF не знайдено: {dxf_path}"
# #             return None

# #         try:
# #             project_dir = os.path.abspath(project_dir)
# #             dxf_path = os.path.abspath(dxf_path)

# #             if door_model_id is None:
# #                 door_model_id = self.get_or_create_door_model(
# #                     folder_path=project_dir,
# #                     model_name=os.path.basename(project_dir),
# #                     source_width=project_meta.get("source_width"),
# #                     source_height=project_meta.get("source_height"),
# #                     source_door_opening=project_meta.get("source_door_opening")
# #                     or project_meta.get("door_opening")
# #                     or "left",
# #                     user_id=user_id,
# #                     growth_axis=project_meta.get("growth_axis") or "both",
# #                     axis_link_mode=project_meta.get("axis_link_mode") or "normal",
# #                     link_x=project_meta.get("link_x") or "X = W",
# #                     link_y=project_meta.get("link_y") or "Y = H",
# #                 )

# #             if door_model_id is None:
# #                 self.last_error = "Не вдалося створити/знайти DoorModel."
# #                 return None

# #             self.update_door_model_from_meta(door_model_id, project_meta, user_id)

# #             with open(dxf_path, "rb") as f:
# #                 file_data = f.read()

# #             file_name = os.path.basename(dxf_path)
# #             ext = os.path.splitext(file_name)[1] or ".dxf"
# #             text = project_meta.get("door_text") or {}

# #             with self.connect() as conn:
# #                 cur = conn.cursor()

# #                 if project_file_id is None:
# #                     project_file_id = self._scalar(
# #                         cur,
# #                         """
# #                         SELECT TOP 1 Id
# #                         FROM dbo.ProjectFiles
# #                         WHERE DoorModelId = ? AND FileName = ?
# #                         ORDER BY Id DESC
# #                         """,
# #                         door_model_id,
# #                         file_name,
# #                     )

# #                 if project_file_id is None:
# #                     cur.execute(
# #                         """
# #                         INSERT INTO dbo.ProjectFiles
# #                         (
# #                             DoorModelId,
# #                             FileName,
# #                             FileExtension,
# #                             FileData,
# #                             SourceWidth,
# #                             SourceHeight,
# #                             SourceDoorOpening,
# #                             CurrentDoorOpening,
# #                             GrowthAxis,
# #                             AxisLinkMode,
# #                             LinkX,
# #                             LinkY,
# #                             Status,
# #                             CreatedByUserId,
# #                             CreatedAt
# #                         )
# #                         OUTPUT INSERTED.Id
# #                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
# #                         """,
# #                         door_model_id,
# #                         file_name,
# #                         ext,
# #                         pyodbc.Binary(file_data),
# #                         project_meta.get("source_width"),
# #                         project_meta.get("source_height"),
# #                         project_meta.get("source_door_opening") or project_meta.get("door_opening") or "left",
# #                         project_meta.get("door_opening") or project_meta.get("source_door_opening") or "left",
# #                         project_meta.get("growth_axis") or "both",
# #                         project_meta.get("axis_link_mode") or "normal",
# #                         project_meta.get("link_x") or "X = W",
# #                         project_meta.get("link_y") or "Y = H",
# #                         status,
# #                         user_id,
# #                     )
# #                     project_file_id = int(cur.fetchone()[0])
# #                 else:
# #                     cur.execute(
# #                         """
# #                         UPDATE dbo.ProjectFiles
# #                         SET
# #                             DoorModelId = ?,
# #                             FileName = ?,
# #                             FileExtension = ?,
# #                             FileData = ?,
# #                             SourceWidth = ?,
# #                             SourceHeight = ?,
# #                             SourceDoorOpening = ?,
# #                             CurrentDoorOpening = ?,
# #                             GrowthAxis = ?,
# #                             AxisLinkMode = ?,
# #                             LinkX = ?,
# #                             LinkY = ?,
# #                             Status = ?,
# #                             UpdatedByUserId = ?,
# #                             UpdatedAt = SYSDATETIME()
# #                         WHERE Id = ?
# #                         """,
# #                         door_model_id,
# #                         file_name,
# #                         ext,
# #                         pyodbc.Binary(file_data),
# #                         project_meta.get("source_width"),
# #                         project_meta.get("source_height"),
# #                         project_meta.get("source_door_opening") or project_meta.get("door_opening") or "left",
# #                         project_meta.get("door_opening") or project_meta.get("source_door_opening") or "left",
# #                         project_meta.get("growth_axis") or "both",
# #                         project_meta.get("axis_link_mode") or "normal",
# #                         project_meta.get("link_x") or "X = W",
# #                         project_meta.get("link_y") or "Y = H",
# #                         status,
# #                         user_id,
# #                         project_file_id,
# #                     )

# #                 self._save_text_settings(cur, project_file_id, text)
# #                 self._save_groups(cur, project_file_id, parametric_groups, block_keep_state)

# #                 cur.execute(
# #                     """
# #                     INSERT INTO dbo.ActionLog
# #                     (UserId, ActionType, EntityType, EntityId, Details)
# #                     VALUES (?, ?, ?, ?, ?)
# #                     """,
# #                     user_id,
# #                     status,
# #                     "ProjectFile",
# #                     str(project_file_id),
# #                     f"Saved {file_name} in DoorModelId={door_model_id}",
# #                 )

# #                 conn.commit()
# #                 return int(project_file_id)

# #         except Exception as exc:
# #             self.last_error = str(exc)
# #             return None

# #     def _save_text_settings(self, cur, project_file_id: int, text: Dict[str, Any]) -> None:
# #         cur.execute(
# #             "DELETE FROM dbo.ProjectTextSettings WHERE ProjectFileId = ?",
# #             project_file_id,
# #         )

# #         cur.execute(
# #             """
# #             INSERT INTO dbo.ProjectTextSettings
# #             (
# #                 ProjectFileId,
# #                 Enabled,
# #                 TextValue,
# #                 X,
# #                 Y,
# #                 Height,
# #                 WidthFactor,
# #                 Rotation,
# #                 FontName,
# #                 EntityHandle
# #             )
# #             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# #             """,
# #             project_file_id,
# #             1 if text.get("enabled") else 0,
# #             text.get("text") or "",
# #             text.get("x") or 0,
# #             text.get("y") or 0,
# #             text.get("height") or 30,
# #             text.get("width_factor") or 120,
# #             text.get("rotation") or 0,
# #             text.get("font") or "STANDARD",
# #             text.get("handle"),
# #         )

# #     def _save_groups(
# #         self,
# #         cur,
# #         project_file_id: int,
# #         parametric_groups: List[Dict[str, Any]],
# #         block_keep_state: Dict[str, bool],
# #     ) -> None:
# #         cur.execute(
# #             """
# #             DELETE FROM dbo.ProjectGroupEntities
# #             WHERE ProjectGroupId IN (
# #                 SELECT Id
# #                 FROM dbo.ProjectGroups
# #                 WHERE ProjectFileId = ?
# #             )
# #             """,
# #             project_file_id,
# #         )
# #         cur.execute(
# #             "DELETE FROM dbo.ProjectGroups WHERE ProjectFileId = ?",
# #             project_file_id,
# #         )
# #         cur.execute(
# #             "DELETE FROM dbo.ProjectBlockStates WHERE ProjectFileId = ?",
# #             project_file_id,
# #         )

# #         for sort_order, group in enumerate(parametric_groups):
# #             handles = sorted(str(h) for h in group.get("handles", []))
# #             uid = group.get("uid") or f"{group.get('name', 'group')}|{','.join(handles)}"
# #             keep = 1 if block_keep_state.get(uid, True) else 0

# #             cur.execute(
# #                 """
# #                 INSERT INTO dbo.ProjectGroups
# #                 (
# #                     ProjectFileId,
# #                     Name,
# #                     Uid,
# #                     K_W,
# #                     K_H,
# #                     Growth_P_W,
# #                     Growth_P_H,
# #                     Growth_Dir_X,
# #                     Growth_Dir_Y,
# #                     Shift_Dir_X,
# #                     Shift_Dir_Y,
# #                     Link_X,
# #                     Link_Y,
# #                     Resizes,
# #                     IsKeep,
# #                     SortOrder,
# #                     CreatedAt
# #                 )
# #                 OUTPUT INSERTED.Id
# #                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
# #                 """,
# #                 project_file_id,
# #                 group.get("name") or "Група",
# #                 uid,
# #                 group.get("k_w") or 0,
# #                 group.get("k_h") or 0,
# #                 group.get("growth_p_w") or 0,
# #                 group.get("growth_p_h") or 0,
# #                 group.get("growth_dir_x") or "Центр",
# #                 group.get("growth_dir_y") or "Центр",
# #                 group.get("shift_dir_x") or "Вправо",
# #                 group.get("shift_dir_y") or "Вгору",
# #                 group.get("link_x") or "X = W",
# #                 group.get("link_y") or "Y = H",
# #                 1 if group.get("resizes") else 0,
# #                 keep,
# #                 sort_order,
# #             )

# #             group_id = int(cur.fetchone()[0])

# #             for handle in handles:
# #                 cur.execute(
# #                     """
# #                     INSERT INTO dbo.ProjectGroupEntities
# #                     (ProjectGroupId, EntityHandle)
# #                     VALUES (?, ?)
# #                     """,
# #                     group_id,
# #                     handle,
# #                 )

# #             cur.execute(
# #                 """
# #                 INSERT INTO dbo.ProjectBlockStates
# #                 (ProjectFileId, BlockKey, BlockName, IsKeep)
# #                 VALUES (?, ?, ?, ?)
# #                 """,
# #                 project_file_id,
# #                 uid,
# #                 group.get("name") or "Група",
# #                 keep,
# #             )

# #     def load_project_config(
# #         self,
# #         dxf_path: str = None,
# #         project_file_id: int = None,
# #         door_model_id: int = None,
# #         file_name: str = None,
# #     ) -> Optional[Dict[str, Any]]:
# #         """
# #         Завантаження конкретного DXF.

# #         Якщо передано DoorModelId + FileName — шукає файл в цій моделі.
# #         Якщо передано ProjectFileId — завантажує напряму.
# #         Старий пошук по LocalPath НЕ використовується, бо LocalPath вже немає в БД.
# #         """
# #         try:
# #             if file_name is None and dxf_path:
# #                 file_name = os.path.basename(dxf_path)

# #             with self.connect() as conn:
# #                 cur = conn.cursor()

# #                 if project_file_id is None and door_model_id is not None and file_name:
# #                     project_file_id = self._scalar(
# #                         cur,
# #                         """
# #                         SELECT TOP 1 Id
# #                         FROM dbo.ProjectFiles
# #                         WHERE DoorModelId = ? AND FileName = ?
# #                         ORDER BY Id DESC
# #                         """,
# #                         door_model_id,
# #                         file_name,
# #                     )

# #                 if project_file_id is None:
# #                     return None

# #                 file_row = cur.execute(
# #                     """
# #                     SELECT *
# #                     FROM dbo.ProjectFiles
# #                     WHERE Id = ?
# #                     """,
# #                     project_file_id,
# #                 ).fetchone()

# #                 if not file_row:
# #                     return None

# #                 model_row = None
# #                 if file_row.DoorModelId:
# #                     model_row = cur.execute(
# #                         """
# #                         SELECT *
# #                         FROM dbo.DoorModels
# #                         WHERE Id = ?
# #                         """,
# #                         file_row.DoorModelId,
# #                     ).fetchone()

# #                 meta = self._build_meta_from_rows(file_row, model_row)

# #                 text_row = cur.execute(
# #                     """
# #                     SELECT *
# #                     FROM dbo.ProjectTextSettings
# #                     WHERE ProjectFileId = ?
# #                     """,
# #                     project_file_id,
# #                 ).fetchone()

# #                 meta["door_text"] = self._build_text_settings(text_row)

# #                 groups, block_keep_state = self._load_groups(cur, project_file_id)

# #                 return {
# #                     "door_model_id": int(file_row.DoorModelId) if file_row.DoorModelId else None,
# #                     "project_file_id": int(project_file_id),
# #                     "meta": meta,
# #                     "groups": groups,
# #                     "block_keep_state": block_keep_state,
# #                 }

# #         except Exception as exc:
# #             self.last_error = str(exc)
# #             return None

# #     def _build_meta_from_rows(self, file_row, model_row) -> Dict[str, Any]:
# #         source_width = self._to_float(model_row.SourceWidth) if model_row else self._to_float(file_row.SourceWidth)
# #         source_height = self._to_float(model_row.SourceHeight) if model_row else self._to_float(file_row.SourceHeight)
# #         source_opening = (
# #             model_row.SourceDoorOpening
# #             if model_row and model_row.SourceDoorOpening
# #             else file_row.SourceDoorOpening
# #         ) or "left"

# #         return {
# #             "source_width": source_width,
# #             "source_height": source_height,

# #             # Цільові розміри тільки для UI. Вони не є постійним станом БД.
# #             "target_width": source_width,
# #             "target_height": source_height,

# #             "door_opening": file_row.CurrentDoorOpening or source_opening,
# #             "source_door_opening": source_opening,
# #             "target_door_opening": file_row.CurrentDoorOpening or source_opening,

# #             "growth_axis": (model_row.GrowthAxis if model_row else file_row.GrowthAxis) or "both",
# #             "axis_link_mode": (model_row.AxisLinkMode if model_row else file_row.AxisLinkMode) or "normal",
# #             "link_x": (model_row.LinkX if model_row else file_row.LinkX) or "X = W",
# #             "link_y": (model_row.LinkY if model_row else file_row.LinkY) or "Y = H",
# #         }

# #     def _build_text_settings(self, text_row) -> Dict[str, Any]:
# #         if not text_row:
# #             return {
# #                 "enabled": False,
# #                 "text": "",
# #                 "x": 0.0,
# #                 "y": 0.0,
# #                 "height": 30.0,
# #                 "width_factor": 120.0,
# #                 "rotation": 0.0,
# #                 "font": "STANDARD",
# #                 "handle": None,
# #             }

# #         return {
# #             "enabled": bool(text_row.Enabled),
# #             "text": text_row.TextValue or "",
# #             "x": self._to_float(text_row.X) or 0.0,
# #             "y": self._to_float(text_row.Y) or 0.0,
# #             "height": self._to_float(text_row.Height) or 30.0,
# #             "width_factor": self._to_float(text_row.WidthFactor) or 120.0,
# #             "rotation": self._to_float(text_row.Rotation) or 0.0,
# #             "font": text_row.FontName or "STANDARD",
# #             "handle": text_row.EntityHandle,
# #         }

# #     def _load_groups(self, cur, project_file_id: int):
# #         groups = []
# #         block_keep_state = {}

# #         group_rows = cur.execute(
# #             """
# #             SELECT *
# #             FROM dbo.ProjectGroups
# #             WHERE ProjectFileId = ?
# #             ORDER BY SortOrder, Id
# #             """,
# #             project_file_id,
# #         ).fetchall()

# #         for gr in group_rows:
# #             handles = {
# #                 r.EntityHandle
# #                 for r in cur.execute(
# #                     """
# #                     SELECT EntityHandle
# #                     FROM dbo.ProjectGroupEntities
# #                     WHERE ProjectGroupId = ?
# #                     """,
# #                     gr.Id,
# #                 ).fetchall()
# #             }

# #             group = {
# #                 "uid": gr.Uid,
# #                 "name": gr.Name,
# #                 "handles": handles,
# #                 "k_w": float(gr.K_W or 0),
# #                 "k_h": float(gr.K_H or 0),
# #                 "growth_p_w": float(gr.Growth_P_W or 0),
# #                 "growth_p_h": float(gr.Growth_P_H or 0),
# #                 "growth_dir_x": gr.Growth_Dir_X or "Центр",
# #                 "growth_dir_y": gr.Growth_Dir_Y or "Центр",
# #                 "shift_dir_x": gr.Shift_Dir_X or "Вправо",
# #                 "shift_dir_y": gr.Shift_Dir_Y or "Вгору",
# #                 "link_x": gr.Link_X or "X = W",
# #                 "link_y": gr.Link_Y or "Y = H",
# #                 "resizes": bool(gr.Resizes),
# #             }

# #             groups.append(group)
# #             block_keep_state[gr.Uid] = bool(gr.IsKeep)

# #         return groups, block_keep_state

# #     def get_model_files(self, door_model_id: int) -> List[Dict[str, Any]]:
# #         try:
# #             with self.connect() as conn:
# #                 rows = conn.cursor().execute(
# #                     """
# #                     SELECT Id, FileName, FileExtension, Status, CreatedAt, UpdatedAt
# #                     FROM dbo.ProjectFiles
# #                     WHERE DoorModelId = ?
# #                     ORDER BY FileName
# #                     """,
# #                     door_model_id,
# #                 ).fetchall()

# #                 return [
# #                     {
# #                         "id": int(r.Id),
# #                         "file_name": r.FileName,
# #                         "extension": r.FileExtension,
# #                         "status": r.Status,
# #                         "created_at": r.CreatedAt,
# #                         "updated_at": r.UpdatedAt,
# #                     }
# #                     for r in rows
# #                 ]
# #         except Exception as exc:
# #             self.last_error = str(exc)
# #             return []

# #     def get_project_file_binary(self, project_file_id: int) -> Optional[bytes]:
# #         try:
# #             with self.connect() as conn:
# #                 row = conn.cursor().execute(
# #                     """
# #                     SELECT FileData
# #                     FROM dbo.ProjectFiles
# #                     WHERE Id = ?
# #                     """,
# #                     project_file_id,
# #                 ).fetchone()

# #                 return bytes(row.FileData) if row and row.FileData is not None else None
# #         except Exception as exc:
# #             self.last_error = str(exc)
# #             return None

# #     # ============================================================
# #     # EXPORTS / JSON BACKUP
# #     # ============================================================

# #     def save_export_file(
# #         self,
# #         source_project_file_id: int,
# #         export_path: str,
# #         width: float,
# #         height: float,
# #         opening: str,
# #         user_id: int,
# #         door_model_id: Optional[int] = None,
# #     ) -> bool:
# #         try:
# #             if not os.path.exists(export_path):
# #                 self.last_error = f"Export DXF не знайдено: {export_path}"
# #                 return False

# #             with open(export_path, "rb") as f:
# #                 file_data = f.read()

# #             if door_model_id is None:
# #                 with self.connect() as conn:
# #                     cur = conn.cursor()
# #                     door_model_id = self._scalar(
# #                         cur,
# #                         """
# #                         SELECT DoorModelId
# #                         FROM dbo.ProjectFiles
# #                         WHERE Id = ?
# #                         """,
# #                         source_project_file_id,
# #                     )

# #             with self.connect() as conn:
# #                 conn.cursor().execute(
# #                     """
# #                     INSERT INTO dbo.ProjectExports
# #                     (
# #                         SourceProjectFileId,
# #                         DoorModelId,
# #                         ExportFileName,
# #                         ExportFileData,
# #                         ExportWidth,
# #                         ExportHeight,
# #                         ExportDoorOpening,
# #                         CreatedByUserId,
# #                         CreatedAt
# #                     )
# #                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
# #                     """,
# #                     source_project_file_id,
# #                     door_model_id,
# #                     os.path.basename(export_path),
# #                     pyodbc.Binary(file_data),
# #                     width,
# #                     height,
# #                     opening,
# #                     user_id,
# #                 )
# #                 conn.commit()

# #             return True

# #         except Exception as exc:
# #             self.last_error = str(exc)
# #             return False

# #     def export_project_json_backup(
# #         self,
# #         project_file_id: int,
# #         data: Dict[str, Any],
# #         user_id: int,
# #         backup_type: str = "ManualExport",
# #     ) -> bool:
# #         try:
# #             safe = json.dumps(data, ensure_ascii=False, indent=4, default=list)

# #             with self.connect() as conn:
# #                 conn.cursor().execute(
# #                     """
# #                     INSERT INTO dbo.ProjectJsonBackups
# #                     (
# #                         ProjectFileId,
# #                         JsonData,
# #                         BackupType,
# #                         CreatedByUserId,
# #                         CreatedAt
# #                     )
# #                     VALUES (?, ?, ?, ?, SYSDATETIME())
# #                     """,
# #                     project_file_id,
# #                     safe,
# #                     backup_type,
# #                     user_id,
# #                 )
# #                 conn.commit()

# #             return True

# #         except Exception as exc:
# #             self.last_error = str(exc)
# #             return False

# #     def create_admin_user_if_empty(
# #         self,
# #         username: str = "admin",
# #         password: str = "admin",
# #         full_name: str = "Administrator",
# #     ) -> bool:
# #         try:
# #             with self.connect() as conn:
# #                 cur = conn.cursor()

# #                 count_users = self._scalar(cur, "SELECT COUNT(*) FROM dbo.Users") or 0
# #                 if int(count_users) > 0:
# #                     return True

# #                 cur.execute(
# #                     """
# #                     INSERT INTO dbo.Users
# #                     (Username, PasswordHash, FullName, IsActive, CreatedAt)
# #                     VALUES (?, ?, ?, 1, SYSDATETIME())
# #                     """,
# #                     username,
# #                     self.hash_password(password),
# #                     full_name,
# #                 )

# #                 conn.commit()
# #                 return True

# #         except Exception as exc:
# #             self.last_error = str(exc)
# #             return False
# import os
# import json
# import hashlib
# from typing import Any, Dict, List, Optional

# import pyodbc
# from PySide6.QtWidgets import (
#     QDialog,
#     QVBoxLayout,
#     QLabel,
#     QLineEdit,
#     QPushButton,
#     QHBoxLayout,
# )


# class LoginDialog(QDialog):
#     def __init__(self, parent=None, message="Вхід"):
#         super().__init__(parent)
#         self.setWindowTitle("Авторизація")

#         layout = QVBoxLayout(self)
#         layout.addWidget(QLabel(message))

#         self.username_input = QLineEdit()
#         self.username_input.setPlaceholderText("Логін")

#         self.password_input = QLineEdit()
#         self.password_input.setPlaceholderText("Пароль")
#         self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

#         layout.addWidget(self.username_input)
#         layout.addWidget(self.password_input)

#         buttons = QHBoxLayout()
#         btn_ok = QPushButton("Увійти")
#         btn_cancel = QPushButton("Скасувати")

#         btn_ok.clicked.connect(self.accept)
#         btn_cancel.clicked.connect(self.reject)

#         buttons.addWidget(btn_ok)
#         buttons.addWidget(btn_cancel)
#         layout.addLayout(buttons)

#     def credentials(self):
#         return self.username_input.text().strip(), self.password_input.text()


# def get_sql_driver() -> str:
#     drivers = [d for d in pyodbc.drivers()]
#     preferred = [
#         "ODBC Driver 18 for SQL Server",
#         "ODBC Driver 17 for SQL Server",
#         "SQL Server Native Client 11.0",
#         "SQL Server",
#     ]

#     for name in preferred:
#         if name in drivers:
#             return name

#     raise RuntimeError(f"Не знайдено SQL Server ODBC driver. Доступні драйвери: {drivers}")


# class ParametricDb:
#     """
#     MSSQL storage for MiniCAD.

#     Нова структура:
#         DoorModels      = одна папка / одна модель дверей
#         ProjectFiles    = DXF-файли цієї моделі
#         ProjectGroups   = параметричні групи конкретного DXF
#         ProjectExports  = історія експортованих DXF

#     JSON не є основним сховищем. JSON використовується тільки для backup/export.
#     """

#     def __init__(self):
#         self.server = os.getenv("PARAMETRIC_DB_SERVER", "prog-srv")
#         self.database = os.getenv("PARAMETRIC_DB_NAME", "parametric_db")
#         self.username = os.getenv("PARAMETRIC_DB_USER", "sa")
#         self.password = os.getenv("PARAMETRIC_DB_PASSWORD", "*Htlbcrf2oo6")
#         self.trusted = os.getenv("PARAMETRIC_DB_TRUSTED", "0") == "1"
#         self.driver = os.getenv("PARAMETRIC_DB_DRIVER") or get_sql_driver()

#         self.available = False
#         self.last_error = ""
#         self._check_connection()

#     def connection_string(self) -> str:
#         base = (
#             f"DRIVER={{{self.driver}}};"
#             f"SERVER={self.server};"
#             f"DATABASE={self.database};"
#             "TrustServerCertificate=yes;"
#         )

#         if self.trusted:
#             return base + "Trusted_Connection=yes;"

#         return base + f"UID={self.username};PWD={self.password};"

#     def connect(self):
#         return pyodbc.connect(self.connection_string(), autocommit=False)

#     def _check_connection(self) -> bool:
#         try:
#             with self.connect() as conn:
#                 conn.cursor().execute("SELECT 1")
#             self.available = True
#             self.last_error = ""
#             return True
#         except Exception as exc:
#             self.available = False
#             self.last_error = str(exc)
#             return False


#     @staticmethod
#     def axis_pair_for_mode(mode: str):
#         mode = str(mode or "normal").strip().lower()
#         if mode == "rotated":
#             return "X = H", "Y = W"
#         return "X = W", "Y = H"

#     @staticmethod
#     def normalize_axis_link_mode(mode: str = None, link_x: str = None, link_y: str = None) -> str:
#         mode = str(mode or "").strip().lower()
#         if mode in ("normal", "rotated"):
#             return mode
#         link_x = str(link_x or "")
#         link_y = str(link_y or "")
#         if "H" in link_x or "W" in link_y:
#             return "rotated"
#         return "normal"

#     def register_folder_dxf_files(
#         self,
#         folder_path: str,
#         project_meta: Dict[str, Any],
#         user_id: int,
#         door_model_id: Optional[int] = None,
#     ) -> Optional[int]:
#         """
#         Реєструє папку як DoorModel та всі DXF-файли всередині.

#         Важливо:
#         - початкові розміри однакові для всієї папки;
#         - SourceWidth / SourceHeight / SourceDoorOpening дублюються в ProjectFiles
#           для зручності, але основне джерело правди — DoorModels;
#         - цільові розміри тут не зберігаються.
#         """
#         try:
#             folder_path = os.path.abspath(folder_path)

#             source_width = project_meta.get("source_width")
#             source_height = project_meta.get("source_height")
#             source_opening = (
#                 project_meta.get("source_door_opening")
#                 or project_meta.get("door_opening")
#                 or "left"
#             )
#             current_opening = project_meta.get("door_opening") or source_opening
#             axis_link_mode = self.normalize_axis_link_mode(
#                 project_meta.get("axis_link_mode"),
#                 project_meta.get("link_x"),
#                 project_meta.get("link_y"),
#             )
#             link_x, link_y = self.axis_pair_for_mode(axis_link_mode)
#             project_meta["axis_link_mode"] = axis_link_mode
#             project_meta["link_x"] = link_x
#             project_meta["link_y"] = link_y

#             if door_model_id is None:
#                 door_model_id = self.get_or_create_door_model(
#                     folder_path=folder_path,
#                     model_name=os.path.basename(folder_path),
#                     source_width=source_width,
#                     source_height=source_height,
#                     source_door_opening=source_opening,
#                     user_id=user_id,
#                     growth_axis=project_meta.get("growth_axis") or "both",
#                     axis_link_mode=axis_link_mode,
#                     link_x=link_x,
#                     link_y=link_y,
#                 )
#             else:
#                 self.update_door_model_from_meta(door_model_id, project_meta, user_id)

#             if not door_model_id:
#                 self.last_error = "Не вдалося створити або знайти DoorModel."
#                 return None

#             with self.connect() as conn:
#                 cur = conn.cursor()

#                 for file_name in sorted(os.listdir(folder_path)):
#                     if not file_name.lower().endswith(".dxf"):
#                         continue

#                     full_path = os.path.join(folder_path, file_name)
#                     if not os.path.isfile(full_path):
#                         continue

#                     with open(full_path, "rb") as f:
#                         data = f.read()

#                     ext = os.path.splitext(file_name)[1] or ".dxf"

#                     existing_id = self._scalar(
#                         cur,
#                         """
#                         SELECT TOP 1 Id
#                         FROM dbo.ProjectFiles
#                         WHERE DoorModelId = ? AND FileName = ?
#                         ORDER BY Id DESC
#                         """,
#                         door_model_id,
#                         file_name,
#                     )

#                     if existing_id:
#                         cur.execute(
#                             """
#                             UPDATE dbo.ProjectFiles
#                             SET
#                                 FileExtension = ?,
#                                 FileData = ?,
#                                 SourceWidth = ?,
#                                 SourceHeight = ?,
#                                 SourceDoorOpening = ?,
#                                 CurrentDoorOpening = ?,
#                                 GrowthAxis = ?,
#                                 AxisLinkMode = ?,
#                                 LinkX = ?,
#                                 LinkY = ?,
#                                 Status = CASE WHEN Status IS NULL OR Status = '' THEN N'Registered' ELSE Status END,
#                                 UpdatedByUserId = ?,
#                                 UpdatedAt = SYSDATETIME()
#                             WHERE Id = ?
#                             """,
#                             ext,
#                             pyodbc.Binary(data),
#                             source_width,
#                             source_height,
#                             source_opening,
#                             current_opening,
#                             project_meta.get("growth_axis") or "both",
#                             axis_link_mode,
#                             link_x,
#                             link_y,
#                             user_id,
#                             existing_id,
#                         )
#                     else:
#                         cur.execute(
#                             """
#                             INSERT INTO dbo.ProjectFiles
#                             (
#                                 DoorModelId,
#                                 FileName,
#                                 FileExtension,
#                                 FileData,
#                                 SourceWidth,
#                                 SourceHeight,
#                                 SourceDoorOpening,
#                                 CurrentDoorOpening,
#                                 GrowthAxis,
#                                 AxisLinkMode,
#                                 LinkX,
#                                 LinkY,
#                                 Status,
#                                 CreatedByUserId,
#                                 CreatedAt
#                             )
#                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, N'Registered', ?, SYSDATETIME())
#                             """,
#                             door_model_id,
#                             file_name,
#                             ext,
#                             pyodbc.Binary(data),
#                             source_width,
#                             source_height,
#                             source_opening,
#                             current_opening,
#                             project_meta.get("growth_axis") or "both",
#                             axis_link_mode,
#                             link_x,
#                             link_y,
#                             user_id,
#                         )

#                 conn.commit()

#             return int(door_model_id)

#         except Exception as exc:
#             self.last_error = str(exc)
#             return None

#     @staticmethod
#     def hash_password(password: str) -> str:
#         return hashlib.sha256(password.encode("utf-8")).hexdigest()

#     @staticmethod
#     def _to_float(value):
#         return None if value is None else float(value)

#     @staticmethod
#     def _row_to_dict(row) -> Dict[str, Any]:
#         if row is None:
#             return {}
#         return {column[0]: getattr(row, column[0]) for column in row.cursor_description}

#     def _scalar(self, cur, sql: str, *params):
#         row = cur.execute(sql, *params).fetchone()
#         return row[0] if row else None

#     # ============================================================
#     # AUTH
#     # ============================================================

#     def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
#         sql = """
#         SELECT Id, Username, FullName, IsActive
#         FROM dbo.Users
#         WHERE Username = ? AND PasswordHash = ? AND IsActive = 1
#         """

#         with self.connect() as conn:
#             cur = conn.cursor()

#             row = cur.execute(sql, username, self.hash_password(password)).fetchone()

#             # Тимчасово дозволяє старий plain text пароль під час міграції.
#             if not row:
#                 row = cur.execute(sql, username, password).fetchone()

#             if not row:
#                 return None

#             return {
#                 "id": int(row.Id),
#                 "username": row.Username,
#                 "full_name": row.FullName,
#             }

#     # ============================================================
#     # DOOR MODEL
#     # ============================================================

#     def get_or_create_door_model(
#         self,
#         folder_path: str,
#         model_name: Optional[str],
#         source_width: Optional[float],
#         source_height: Optional[float],
#         source_door_opening: str,
#         user_id: int,
#         growth_axis: str = "both",
#         axis_link_mode: str = "normal",
#         link_x: str = "X = W",
#         link_y: str = "Y = H",
#     ) -> Optional[int]:
#         """
#         Одна папка = одна DoorModel.

#         Якщо модель для SourceFolderPath вже існує — оновлюємо базові параметри,
#         але не створюємо дубль.
#         """
#         try:
#             folder_path = os.path.abspath(folder_path)
#             model_name = model_name or os.path.basename(folder_path) or "DoorModel"

#             with self.connect() as conn:
#                 cur = conn.cursor()

#                 model_id = self._scalar(
#                     cur,
#                     """
#                     SELECT TOP 1 Id
#                     FROM dbo.DoorModels
#                     WHERE SourceFolderPath = ?
#                     ORDER BY Id DESC
#                     """,
#                     folder_path,
#                 )

#                 if model_id is None:
#                     cur.execute(
#                         """
#                         INSERT INTO dbo.DoorModels
#                         (
#                             ModelName,
#                             SourceFolderPath,
#                             SourceWidth,
#                             SourceHeight,
#                             SourceDoorOpening,
#                             GrowthAxis,
#                             AxisLinkMode,
#                             LinkX,
#                             LinkY,
#                             CreatedByUserId,
#                             CreatedAt
#                         )
#                         OUTPUT INSERTED.Id
#                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
#                         """,
#                         model_name,
#                         folder_path,
#                         source_width,
#                         source_height,
#                         source_door_opening or "left",
#                         growth_axis or "both",
#                         axis_link_mode or "normal",
#                         link_x or "X = W",
#                         link_y or "Y = H",
#                         user_id,
#                     )
#                     model_id = int(cur.fetchone()[0])
#                 else:
#                     cur.execute(
#                         """
#                         UPDATE dbo.DoorModels
#                         SET
#                             ModelName = ?,
#                             SourceWidth = COALESCE(?, SourceWidth),
#                             SourceHeight = COALESCE(?, SourceHeight),
#                             SourceDoorOpening = COALESCE(?, SourceDoorOpening),
#                             GrowthAxis = COALESCE(?, GrowthAxis),
#                             AxisLinkMode = COALESCE(?, AxisLinkMode),
#                             LinkX = COALESCE(?, LinkX),
#                             LinkY = COALESCE(?, LinkY),
#                             UpdatedByUserId = ?,
#                             UpdatedAt = SYSDATETIME()
#                         WHERE Id = ?
#                         """,
#                         model_name,
#                         source_width,
#                         source_height,
#                         source_door_opening or "left",
#                         growth_axis or "both",
#                         axis_link_mode or "normal",
#                         link_x or "X = W",
#                         link_y or "Y = H",
#                         user_id,
#                         model_id,
#                     )

#                 conn.commit()
#                 return int(model_id)

#         except Exception as exc:
#             self.last_error = str(exc)
#             return None

#     def update_door_model_from_meta(
#         self,
#         door_model_id: int,
#         project_meta: Dict[str, Any],
#         user_id: int,
#     ) -> bool:
#         try:
#             axis_link_mode = self.normalize_axis_link_mode(
#                 project_meta.get("axis_link_mode"),
#                 project_meta.get("link_x"),
#                 project_meta.get("link_y"),
#             )
#             link_x, link_y = self.axis_pair_for_mode(axis_link_mode)
#             project_meta["axis_link_mode"] = axis_link_mode
#             project_meta["link_x"] = link_x
#             project_meta["link_y"] = link_y

#             with self.connect() as conn:
#                 conn.cursor().execute(
#                     """
#                     UPDATE dbo.DoorModels
#                     SET
#                         SourceWidth = ?,
#                         SourceHeight = ?,
#                         SourceDoorOpening = ?,
#                         GrowthAxis = ?,
#                         AxisLinkMode = ?,
#                         LinkX = ?,
#                         LinkY = ?,
#                         UpdatedByUserId = ?,
#                         UpdatedAt = SYSDATETIME()
#                     WHERE Id = ?
#                     """,
#                     project_meta.get("source_width"),
#                     project_meta.get("source_height"),
#                     project_meta.get("source_door_opening") or project_meta.get("door_opening") or "left",
#                     project_meta.get("growth_axis") or "both",
#                     axis_link_mode,
#                     link_x,
#                     link_y,
#                     user_id,
#                     door_model_id,
#                 )
#                 conn.commit()
#             return True
#         except Exception as exc:
#             self.last_error = str(exc)
#             return False

#     def load_door_model(self, door_model_id: int) -> Optional[Dict[str, Any]]:
#         try:
#             with self.connect() as conn:
#                 cur = conn.cursor()

#                 model = cur.execute(
#                     """
#                     SELECT *
#                     FROM dbo.DoorModels
#                     WHERE Id = ?
#                     """,
#                     door_model_id,
#                 ).fetchone()

#                 if not model:
#                     return None

#                 files = cur.execute(
#                     """
#                     SELECT Id, FileName, FileExtension, DoorModelId, Status, CreatedAt, UpdatedAt
#                     FROM dbo.ProjectFiles
#                     WHERE DoorModelId = ?
#                     ORDER BY FileName
#                     """,
#                     door_model_id,
#                 ).fetchall()

#                 model_meta = {
#                     "source_width": self._to_float(model.SourceWidth),
#                     "source_height": self._to_float(model.SourceHeight),
#                     "target_width": self._to_float(model.SourceWidth),
#                     "target_height": self._to_float(model.SourceHeight),
#                     "door_opening": model.SourceDoorOpening or "left",
#                     "source_door_opening": model.SourceDoorOpening or "left",
#                     "target_door_opening": model.SourceDoorOpening or "left",
#                     "growth_axis": model.GrowthAxis or "both",
#                     "axis_link_mode": model.AxisLinkMode or "normal",
#                     "link_x": model.LinkX or "X = W",
#                     "link_y": model.LinkY or "Y = H",
#                 }

#                 return {
#                     "id": int(model.Id),
#                     "model_name": model.ModelName,
#                     "folder_path": model.SourceFolderPath,
#                     "meta": model_meta,
#                     "files": [
#                         {
#                             "id": int(row.Id),
#                             "file_name": row.FileName,
#                             "extension": row.FileExtension,
#                             "door_model_id": int(row.DoorModelId) if row.DoorModelId else None,
#                             "status": row.Status,
#                         }
#                         for row in files
#                     ],
#                 }

#         except Exception as exc:
#             self.last_error = str(exc)
#             return None

#     def find_door_model_by_folder(self, folder_path: str) -> Optional[int]:
#         try:
#             folder_path = os.path.abspath(folder_path)
#             with self.connect() as conn:
#                 cur = conn.cursor()
#                 value = self._scalar(
#                     cur,
#                     """
#                     SELECT TOP 1 Id
#                     FROM dbo.DoorModels
#                     WHERE SourceFolderPath = ?
#                     ORDER BY Id DESC
#                     """,
#                     folder_path,
#                 )
#                 return int(value) if value is not None else None
#         except Exception as exc:
#             self.last_error = str(exc)
#             return None

#     # ============================================================
#     # PROJECT FILE
#     # ============================================================

#     def save_project_snapshot(
#         self,
#         project_dir: str,
#         dxf_path: str,
#         project_meta: Dict[str, Any],
#         parametric_groups: List[Dict[str, Any]],
#         block_keep_state: Dict[str, bool],
#         user_id: int,
#         status: str = "ConfigSaved",
#         project_file_id: Optional[int] = None,
#         door_model_id: Optional[int] = None,
#     ) -> Optional[int]:
#         """
#         Upsert поточного DXF + його групи.

#         Спільні параметри моделі пишуться в DoorModels.
#         TargetWidth/TargetHeight не пишуться в ProjectFiles як постійний стан.
#         """
#         if not os.path.exists(dxf_path):
#             self.last_error = f"DXF не знайдено: {dxf_path}"
#             return None

#         try:
#             project_dir = os.path.abspath(project_dir)
#             dxf_path = os.path.abspath(dxf_path)
#             axis_link_mode = self.normalize_axis_link_mode(
#                 project_meta.get("axis_link_mode"),
#                 project_meta.get("link_x"),
#                 project_meta.get("link_y"),
#             )
#             link_x, link_y = self.axis_pair_for_mode(axis_link_mode)
#             project_meta["axis_link_mode"] = axis_link_mode
#             project_meta["link_x"] = link_x
#             project_meta["link_y"] = link_y

#             if door_model_id is None:
#                 door_model_id = self.get_or_create_door_model(
#                     folder_path=project_dir,
#                     model_name=os.path.basename(project_dir),
#                     source_width=project_meta.get("source_width"),
#                     source_height=project_meta.get("source_height"),
#                     source_door_opening=project_meta.get("source_door_opening")
#                     or project_meta.get("door_opening")
#                     or "left",
#                     user_id=user_id,
#                     growth_axis=project_meta.get("growth_axis") or "both",
#                     axis_link_mode=axis_link_mode,
#                     link_x=link_x,
#                     link_y=link_y,
#                 )

#             if door_model_id is None:
#                 self.last_error = "Не вдалося створити/знайти DoorModel."
#                 return None

#             self.update_door_model_from_meta(door_model_id, project_meta, user_id)

#             with open(dxf_path, "rb") as f:
#                 file_data = f.read()

#             file_name = os.path.basename(dxf_path)
#             ext = os.path.splitext(file_name)[1] or ".dxf"
#             text = project_meta.get("door_text") or {}

#             with self.connect() as conn:
#                 cur = conn.cursor()

#                 if project_file_id is None:
#                     project_file_id = self._scalar(
#                         cur,
#                         """
#                         SELECT TOP 1 Id
#                         FROM dbo.ProjectFiles
#                         WHERE DoorModelId = ? AND FileName = ?
#                         ORDER BY Id DESC
#                         """,
#                         door_model_id,
#                         file_name,
#                     )

#                 if project_file_id is None:
#                     cur.execute(
#                         """
#                         INSERT INTO dbo.ProjectFiles
#                         (
#                             DoorModelId,
#                             FileName,
#                             FileExtension,
#                             FileData,
#                             SourceWidth,
#                             SourceHeight,
#                             SourceDoorOpening,
#                             CurrentDoorOpening,
#                             GrowthAxis,
#                             AxisLinkMode,
#                             LinkX,
#                             LinkY,
#                             Status,
#                             CreatedByUserId,
#                             CreatedAt
#                         )
#                         OUTPUT INSERTED.Id
#                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
#                         """,
#                         door_model_id,
#                         file_name,
#                         ext,
#                         pyodbc.Binary(file_data),
#                         project_meta.get("source_width"),
#                         project_meta.get("source_height"),
#                         project_meta.get("source_door_opening") or project_meta.get("door_opening") or "left",
#                         project_meta.get("door_opening") or project_meta.get("source_door_opening") or "left",
#                         project_meta.get("growth_axis") or "both",
#                         axis_link_mode,
#                         link_x,
#                         link_y,
#                         status,
#                         user_id,
#                     )
#                     project_file_id = int(cur.fetchone()[0])
#                 else:
#                     cur.execute(
#                         """
#                         UPDATE dbo.ProjectFiles
#                         SET
#                             DoorModelId = ?,
#                             FileName = ?,
#                             FileExtension = ?,
#                             FileData = ?,
#                             SourceWidth = ?,
#                             SourceHeight = ?,
#                             SourceDoorOpening = ?,
#                             CurrentDoorOpening = ?,
#                             GrowthAxis = ?,
#                             AxisLinkMode = ?,
#                             LinkX = ?,
#                             LinkY = ?,
#                             Status = ?,
#                             UpdatedByUserId = ?,
#                             UpdatedAt = SYSDATETIME()
#                         WHERE Id = ?
#                         """,
#                         door_model_id,
#                         file_name,
#                         ext,
#                         pyodbc.Binary(file_data),
#                         project_meta.get("source_width"),
#                         project_meta.get("source_height"),
#                         project_meta.get("source_door_opening") or project_meta.get("door_opening") or "left",
#                         project_meta.get("door_opening") or project_meta.get("source_door_opening") or "left",
#                         project_meta.get("growth_axis") or "both",
#                         axis_link_mode,
#                         link_x,
#                         link_y,
#                         status,
#                         user_id,
#                         project_file_id,
#                     )

#                 self._save_text_settings(cur, project_file_id, text)
#                 self._save_groups(cur, project_file_id, parametric_groups, block_keep_state)

#                 cur.execute(
#                     """
#                     INSERT INTO dbo.ActionLog
#                     (UserId, ActionType, EntityType, EntityId, Details)
#                     VALUES (?, ?, ?, ?, ?)
#                     """,
#                     user_id,
#                     status,
#                     "ProjectFile",
#                     str(project_file_id),
#                     f"Saved {file_name} in DoorModelId={door_model_id}",
#                 )

#                 conn.commit()
#                 return int(project_file_id)

#         except Exception as exc:
#             self.last_error = str(exc)
#             return None

#     def _save_text_settings(self, cur, project_file_id: int, text: Dict[str, Any]) -> None:
#         cur.execute(
#             "DELETE FROM dbo.ProjectTextSettings WHERE ProjectFileId = ?",
#             project_file_id,
#         )

#         cur.execute(
#             """
#             INSERT INTO dbo.ProjectTextSettings
#             (
#                 ProjectFileId,
#                 Enabled,
#                 TextValue,
#                 X,
#                 Y,
#                 Height,
#                 WidthFactor,
#                 Rotation,
#                 FontName,
#                 EntityHandle
#             )
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#             """,
#             project_file_id,
#             1 if text.get("enabled") else 0,
#             text.get("text") or "",
#             text.get("x") or 0,
#             text.get("y") or 0,
#             text.get("height") or 30,
#             text.get("width_factor") or 120,
#             text.get("rotation") or 0,
#             text.get("font") or "STANDARD",
#             text.get("handle"),
#         )

#     def _save_groups(
#         self,
#         cur,
#         project_file_id: int,
#         parametric_groups: List[Dict[str, Any]],
#         block_keep_state: Dict[str, bool],
#     ) -> None:
#         cur.execute(
#             """
#             DELETE FROM dbo.ProjectGroupEntities
#             WHERE ProjectGroupId IN (
#                 SELECT Id
#                 FROM dbo.ProjectGroups
#                 WHERE ProjectFileId = ?
#             )
#             """,
#             project_file_id,
#         )
#         cur.execute(
#             "DELETE FROM dbo.ProjectGroups WHERE ProjectFileId = ?",
#             project_file_id,
#         )
#         cur.execute(
#             "DELETE FROM dbo.ProjectBlockStates WHERE ProjectFileId = ?",
#             project_file_id,
#         )

#         for sort_order, group in enumerate(parametric_groups):
#             handles = sorted(str(h) for h in group.get("handles", []))
#             uid = group.get("uid") or f"{group.get('name', 'group')}|{','.join(handles)}"
#             keep = 1 if block_keep_state.get(uid, True) else 0

#             cur.execute(
#                 """
#                 INSERT INTO dbo.ProjectGroups
#                 (
#                     ProjectFileId,
#                     Name,
#                     Uid,
#                     K_W,
#                     K_H,
#                     Growth_P_W,
#                     Growth_P_H,
#                     Growth_Dir_X,
#                     Growth_Dir_Y,
#                     Shift_Dir_X,
#                     Shift_Dir_Y,
#                     Link_X,
#                     Link_Y,
#                     Resizes,
#                     IsKeep,
#                     SortOrder,
#                     CreatedAt
#                 )
#                 OUTPUT INSERTED.Id
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
#                 """,
#                 project_file_id,
#                 group.get("name") or "Група",
#                 uid,
#                 group.get("k_w") or 0,
#                 group.get("k_h") or 0,
#                 group.get("growth_p_w") or 0,
#                 group.get("growth_p_h") or 0,
#                 group.get("growth_dir_x") or "Центр",
#                 group.get("growth_dir_y") or "Центр",
#                 group.get("shift_dir_x") or "Вправо",
#                 group.get("shift_dir_y") or "Вгору",
#                 group.get("link_x") or "X = W",
#                 group.get("link_y") or "Y = H",
#                 1 if group.get("resizes") else 0,
#                 keep,
#                 sort_order,
#             )

#             group_id = int(cur.fetchone()[0])

#             for handle in handles:
#                 cur.execute(
#                     """
#                     INSERT INTO dbo.ProjectGroupEntities
#                     (ProjectGroupId, EntityHandle)
#                     VALUES (?, ?)
#                     """,
#                     group_id,
#                     handle,
#                 )

#             cur.execute(
#                 """
#                 INSERT INTO dbo.ProjectBlockStates
#                 (ProjectFileId, BlockKey, BlockName, IsKeep)
#                 VALUES (?, ?, ?, ?)
#                 """,
#                 project_file_id,
#                 uid,
#                 group.get("name") or "Група",
#                 keep,
#             )

#     def load_project_config(
#         self,
#         dxf_path: str = None,
#         project_file_id: int = None,
#         door_model_id: int = None,
#         file_name: str = None,
#     ) -> Optional[Dict[str, Any]]:
#         """
#         Завантаження конкретного DXF.

#         Якщо передано DoorModelId + FileName — шукає файл в цій моделі.
#         Якщо передано ProjectFileId — завантажує напряму.
#         Старий пошук по LocalPath НЕ використовується, бо LocalPath вже немає в БД.
#         """
#         try:
#             if file_name is None and dxf_path:
#                 file_name = os.path.basename(dxf_path)

#             with self.connect() as conn:
#                 cur = conn.cursor()

#                 if project_file_id is None and door_model_id is not None and file_name:
#                     project_file_id = self._scalar(
#                         cur,
#                         """
#                         SELECT TOP 1 Id
#                         FROM dbo.ProjectFiles
#                         WHERE DoorModelId = ? AND FileName = ?
#                         ORDER BY Id DESC
#                         """,
#                         door_model_id,
#                         file_name,
#                     )

#                 if project_file_id is None:
#                     return None

#                 file_row = cur.execute(
#                     """
#                     SELECT *
#                     FROM dbo.ProjectFiles
#                     WHERE Id = ?
#                     """,
#                     project_file_id,
#                 ).fetchone()

#                 if not file_row:
#                     return None

#                 model_row = None
#                 if file_row.DoorModelId:
#                     model_row = cur.execute(
#                         """
#                         SELECT *
#                         FROM dbo.DoorModels
#                         WHERE Id = ?
#                         """,
#                         file_row.DoorModelId,
#                     ).fetchone()

#                 meta = self._build_meta_from_rows(file_row, model_row)

#                 text_row = cur.execute(
#                     """
#                     SELECT *
#                     FROM dbo.ProjectTextSettings
#                     WHERE ProjectFileId = ?
#                     """,
#                     project_file_id,
#                 ).fetchone()

#                 meta["door_text"] = self._build_text_settings(text_row)

#                 groups, block_keep_state = self._load_groups(cur, project_file_id)

#                 return {
#                     "door_model_id": int(file_row.DoorModelId) if file_row.DoorModelId else None,
#                     "project_file_id": int(project_file_id),
#                     "meta": meta,
#                     "groups": groups,
#                     "block_keep_state": block_keep_state,
#                 }

#         except Exception as exc:
#             self.last_error = str(exc)
#             return None

#     def _build_meta_from_rows(self, file_row, model_row) -> Dict[str, Any]:
#         source_width = self._to_float(model_row.SourceWidth) if model_row else self._to_float(file_row.SourceWidth)
#         source_height = self._to_float(model_row.SourceHeight) if model_row else self._to_float(file_row.SourceHeight)
#         source_opening = (
#             model_row.SourceDoorOpening
#             if model_row and model_row.SourceDoorOpening
#             else file_row.SourceDoorOpening
#         ) or "left"

#         axis_link_mode = self.normalize_axis_link_mode(
#             (model_row.AxisLinkMode if model_row else file_row.AxisLinkMode) or "normal",
#             (model_row.LinkX if model_row else file_row.LinkX) if (model_row or file_row) else None,
#             (model_row.LinkY if model_row else file_row.LinkY) if (model_row or file_row) else None,
#         )
#         link_x, link_y = self.axis_pair_for_mode(axis_link_mode)

#         return {
#             "source_width": source_width,
#             "source_height": source_height,

#             # Цільові розміри тільки для UI. Вони не є постійним станом БД.
#             "target_width": source_width,
#             "target_height": source_height,

#             "door_opening": file_row.CurrentDoorOpening or source_opening,
#             "source_door_opening": source_opening,
#             "target_door_opening": file_row.CurrentDoorOpening or source_opening,

#             "growth_axis": (model_row.GrowthAxis if model_row else file_row.GrowthAxis) or "both",
#             "axis_link_mode": axis_link_mode,
#             "link_x": link_x,
#             "link_y": link_y,
#         }

#     def _build_text_settings(self, text_row) -> Dict[str, Any]:
#         if not text_row:
#             return {
#                 "enabled": False,
#                 "text": "",
#                 "x": 0.0,
#                 "y": 0.0,
#                 "height": 30.0,
#                 "width_factor": 120.0,
#                 "rotation": 0.0,
#                 "font": "STANDARD",
#                 "handle": None,
#             }

#         return {
#             "enabled": bool(text_row.Enabled),
#             "text": text_row.TextValue or "",
#             "x": self._to_float(text_row.X) or 0.0,
#             "y": self._to_float(text_row.Y) or 0.0,
#             "height": self._to_float(text_row.Height) or 30.0,
#             "width_factor": self._to_float(text_row.WidthFactor) or 120.0,
#             "rotation": self._to_float(text_row.Rotation) or 0.0,
#             "font": text_row.FontName or "STANDARD",
#             "handle": text_row.EntityHandle,
#         }

#     def _load_groups(self, cur, project_file_id: int):
#         groups = []
#         block_keep_state = {}

#         group_rows = cur.execute(
#             """
#             SELECT *
#             FROM dbo.ProjectGroups
#             WHERE ProjectFileId = ?
#             ORDER BY SortOrder, Id
#             """,
#             project_file_id,
#         ).fetchall()

#         for gr in group_rows:
#             handles = {
#                 r.EntityHandle
#                 for r in cur.execute(
#                     """
#                     SELECT EntityHandle
#                     FROM dbo.ProjectGroupEntities
#                     WHERE ProjectGroupId = ?
#                     """,
#                     gr.Id,
#                 ).fetchall()
#             }

#             group = {
#                 "uid": gr.Uid,
#                 "name": gr.Name,
#                 "handles": handles,
#                 "k_w": float(gr.K_W or 0),
#                 "k_h": float(gr.K_H or 0),
#                 "growth_p_w": float(gr.Growth_P_W or 0),
#                 "growth_p_h": float(gr.Growth_P_H or 0),
#                 "growth_dir_x": gr.Growth_Dir_X or "Центр",
#                 "growth_dir_y": gr.Growth_Dir_Y or "Центр",
#                 "shift_dir_x": gr.Shift_Dir_X or "Вправо",
#                 "shift_dir_y": gr.Shift_Dir_Y or "Вгору",
#                 "link_x": gr.Link_X or "X = W",
#                 "link_y": gr.Link_Y or "Y = H",
#                 "resizes": bool(gr.Resizes),
#             }

#             groups.append(group)
#             block_keep_state[gr.Uid] = bool(gr.IsKeep)

#         return groups, block_keep_state

#     def get_model_files(self, door_model_id: int) -> List[Dict[str, Any]]:
#         try:
#             with self.connect() as conn:
#                 rows = conn.cursor().execute(
#                     """
#                     SELECT Id, FileName, FileExtension, Status, CreatedAt, UpdatedAt
#                     FROM dbo.ProjectFiles
#                     WHERE DoorModelId = ?
#                     ORDER BY FileName
#                     """,
#                     door_model_id,
#                 ).fetchall()

#                 return [
#                     {
#                         "id": int(r.Id),
#                         "file_name": r.FileName,
#                         "extension": r.FileExtension,
#                         "status": r.Status,
#                         "created_at": r.CreatedAt,
#                         "updated_at": r.UpdatedAt,
#                     }
#                     for r in rows
#                 ]
#         except Exception as exc:
#             self.last_error = str(exc)
#             return []

#     def get_project_file_binary(self, project_file_id: int) -> Optional[bytes]:
#         try:
#             with self.connect() as conn:
#                 row = conn.cursor().execute(
#                     """
#                     SELECT FileData
#                     FROM dbo.ProjectFiles
#                     WHERE Id = ?
#                     """,
#                     project_file_id,
#                 ).fetchone()

#                 return bytes(row.FileData) if row and row.FileData is not None else None
#         except Exception as exc:
#             self.last_error = str(exc)
#             return None

#     # ============================================================
#     # EXPORTS / JSON BACKUP
#     # ============================================================

#     def save_export_file(
#         self,
#         source_project_file_id: int,
#         export_path: str,
#         width: float,
#         height: float,
#         opening: str,
#         user_id: int,
#         door_model_id: Optional[int] = None,
#     ) -> bool:
#         try:
#             if not os.path.exists(export_path):
#                 self.last_error = f"Export DXF не знайдено: {export_path}"
#                 return False

#             with open(export_path, "rb") as f:
#                 file_data = f.read()

#             if door_model_id is None:
#                 with self.connect() as conn:
#                     cur = conn.cursor()
#                     door_model_id = self._scalar(
#                         cur,
#                         """
#                         SELECT DoorModelId
#                         FROM dbo.ProjectFiles
#                         WHERE Id = ?
#                         """,
#                         source_project_file_id,
#                     )

#             with self.connect() as conn:
#                 conn.cursor().execute(
#                     """
#                     INSERT INTO dbo.ProjectExports
#                     (
#                         SourceProjectFileId,
#                         DoorModelId,
#                         ExportFileName,
#                         ExportFileData,
#                         ExportWidth,
#                         ExportHeight,
#                         ExportDoorOpening,
#                         CreatedByUserId,
#                         CreatedAt
#                     )
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
#                     """,
#                     source_project_file_id,
#                     door_model_id,
#                     os.path.basename(export_path),
#                     pyodbc.Binary(file_data),
#                     width,
#                     height,
#                     opening,
#                     user_id,
#                 )
#                 conn.commit()

#             return True

#         except Exception as exc:
#             self.last_error = str(exc)
#             return False

#     def export_project_json_backup(
#         self,
#         project_file_id: int,
#         data: Dict[str, Any],
#         user_id: int,
#         backup_type: str = "ManualExport",
#     ) -> bool:
#         try:
#             safe = json.dumps(data, ensure_ascii=False, indent=4, default=list)

#             with self.connect() as conn:
#                 conn.cursor().execute(
#                     """
#                     INSERT INTO dbo.ProjectJsonBackups
#                     (
#                         ProjectFileId,
#                         JsonData,
#                         BackupType,
#                         CreatedByUserId,
#                         CreatedAt
#                     )
#                     VALUES (?, ?, ?, ?, SYSDATETIME())
#                     """,
#                     project_file_id,
#                     safe,
#                     backup_type,
#                     user_id,
#                 )
#                 conn.commit()

#             return True

#         except Exception as exc:
#             self.last_error = str(exc)
#             return False

#     def create_admin_user_if_empty(
#         self,
#         username: str = "admin",
#         password: str = "admin",
#         full_name: str = "Administrator",
#     ) -> bool:
#         try:
#             with self.connect() as conn:
#                 cur = conn.cursor()

#                 count_users = self._scalar(cur, "SELECT COUNT(*) FROM dbo.Users") or 0
#                 if int(count_users) > 0:
#                     return True

#                 cur.execute(
#                     """
#                     INSERT INTO dbo.Users
#                     (Username, PasswordHash, FullName, IsActive, CreatedAt)
#                     VALUES (?, ?, ?, 1, SYSDATETIME())
#                     """,
#                     username,
#                     self.hash_password(password),
#                     full_name,
#                 )

#                 conn.commit()
#                 return True

#         except Exception as exc:
#             self.last_error = str(exc)
#             return False
import os
import json
import hashlib
from typing import Any, Dict, List, Optional

try:
    import pyodbc
except ImportError:
    pyodbc = None
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
)


class LoginDialog(QDialog):
    def __init__(self, parent=None, message="Вхід"):
        super().__init__(parent)
        self.setWindowTitle("Авторизація")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(message))

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логін")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)

        buttons = QHBoxLayout()
        btn_ok = QPushButton("Увійти")
        btn_cancel = QPushButton("Скасувати")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        buttons.addWidget(btn_ok)
        buttons.addWidget(btn_cancel)
        layout.addLayout(buttons)

    def credentials(self):
        return self.username_input.text().strip(), self.password_input.text()


def get_sql_driver() -> str:
    if pyodbc is None:
        return "SQL Server"
    drivers = [d for d in pyodbc.drivers()]
    preferred = [
        "SQL Server",
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "SQL Server Native Client 11.0",
    ]

    for name in preferred:
        if name in drivers:
            return name

    raise RuntimeError(f"Не знайдено SQL Server ODBC driver. Доступні драйвери: {drivers}")


class ParametricDb:
    """
    MSSQL storage for MiniCAD.

    Нова структура:
        DoorModels      = одна папка / одна модель дверей
        ProjectFiles    = DXF-файли цієї моделі
        ProjectGroups   = параметричні групи конкретного DXF
        ProjectExports  = історія експортованих DXF

    JSON не є основним сховищем. JSON використовується тільки для backup/export.
    """

    def __init__(self):
        self.server = os.getenv("PARAMETRIC_DB_SERVER", "prog-srv")
        self.database = os.getenv("PARAMETRIC_DB_NAME", "parametric_db")
        self.username = os.getenv("PARAMETRIC_DB_USER", "sa")
        self.password = os.getenv("PARAMETRIC_DB_PASSWORD", "*Htlbcrf2oo6")
        self.trusted = os.getenv("PARAMETRIC_DB_TRUSTED", "0") == "1"
        self.driver = os.getenv("PARAMETRIC_DB_DRIVER") or get_sql_driver()

        self.available = False
        self.last_error = ""
        self._check_connection()

    def connection_string(self) -> str:
        base = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            "TrustServerCertificate=yes;"
        )

        if self.trusted:
            return base + "Trusted_Connection=yes;"

        return base + f"UID={self.username};PWD={self.password};"

    def connect(self):
        if pyodbc is None:
            raise RuntimeError("pyodbc не встановлено")
        return pyodbc.connect(self.connection_string(), autocommit=False)

    def _check_connection(self) -> bool:
        try:
            with self.connect() as conn:
                conn.cursor().execute("SELECT 1")
            self.available = True
            self.last_error = ""
            return True
        except Exception as exc:
            self.available = False
            self.last_error = str(exc)
            return False


    @staticmethod
    def axis_pair_for_mode(mode: str):
        mode = str(mode or "normal").strip().lower()
        if mode == "rotated":
            return "X = H", "Y = W"
        return "X = W", "Y = H"

    @staticmethod
    def normalize_axis_link_mode(mode: str = None, link_x: str = None, link_y: str = None) -> str:
        mode = str(mode or "").strip().lower()
        if mode in ("normal", "rotated"):
            return mode
        link_x = str(link_x or "")
        link_y = str(link_y or "")
        if "H" in link_x or "W" in link_y:
            return "rotated"
        return "normal"

    def register_folder_dxf_files(
        self,
        folder_path: str,
        project_meta: Dict[str, Any],
        user_id: int,
        door_model_id: Optional[int] = None,
    ) -> Optional[int]:
        """
        Реєструє папку як DoorModel та всі DXF-файли всередині.

        Важливо:
        - початкові розміри однакові для всієї папки;
        - SourceWidth / SourceHeight / SourceDoorOpening дублюються в ProjectFiles
          для зручності, але основне джерело правди — DoorModels;
        - AxisLinkMode / LinkX / LinkY / GrowthAxis є параметрами конкретного DXF-файлу,
          тому при реєстрації папки НЕ перезаписуємо їх у вже існуючих ProjectFiles;
        - цільові розміри тут не зберігаються.
        """
        try:
            folder_path = os.path.abspath(folder_path)

            source_width = project_meta.get("source_width")
            source_height = project_meta.get("source_height")
            source_opening = (
                project_meta.get("source_door_opening")
                or project_meta.get("door_opening")
                or "left"
            )
            current_opening = project_meta.get("door_opening") or source_opening

            # Осі НЕ належать DoorModels. Це параметри конкретного DXF-файлу.
            # Тут беремо значення тільки як дефолт для нових файлів,
            # а існуючим файлам їх не перезаписуємо.
            file_axis_link_mode = self.normalize_axis_link_mode(
                project_meta.get("axis_link_mode"),
                project_meta.get("link_x"),
                project_meta.get("link_y"),
            )
            file_link_x, file_link_y = self.axis_pair_for_mode(file_axis_link_mode)

            if door_model_id is None:
                door_model_id = self.get_or_create_door_model(
                    folder_path=folder_path,
                    model_name=os.path.basename(folder_path),
                    source_width=source_width,
                    source_height=source_height,
                    source_door_opening=source_opening,
                    user_id=user_id,
                )
            else:
                self.update_door_model_from_meta(door_model_id, project_meta, user_id)

            if not door_model_id:
                self.last_error = "Не вдалося створити або знайти DoorModel."
                return None

            with self.connect() as conn:
                cur = conn.cursor()

                for file_name in sorted(os.listdir(folder_path)):
                    if not file_name.lower().endswith(".dxf"):
                        continue

                    full_path = os.path.join(folder_path, file_name)
                    if not os.path.isfile(full_path):
                        continue

                    with open(full_path, "rb") as f:
                        data = f.read()

                    ext = os.path.splitext(file_name)[1] or ".dxf"

                    existing_id = self._scalar(
                        cur,
                        """
                        SELECT TOP 1 Id
                        FROM dbo.ProjectFiles
                        WHERE DoorModelId = ? AND FileName = ?
                        ORDER BY Id DESC
                        """,
                        door_model_id,
                        file_name,
                    )

                    if existing_id:
                        cur.execute(
                            """
                            UPDATE dbo.ProjectFiles
                            SET
                                FileExtension = ?,
                                FileData = ?,
                                SourceWidth = ?,
                                SourceHeight = ?,
                                SourceDoorOpening = ?,
                                CurrentDoorOpening = ?,
                                Status = CASE WHEN Status IS NULL OR Status = '' THEN N'Registered' ELSE Status END,
                                UpdatedByUserId = ?,
                                UpdatedAt = SYSDATETIME()
                            WHERE Id = ?
                            """,
                            ext,
                            pyodbc.Binary(data),
                            source_width,
                            source_height,
                            source_opening,
                            current_opening,
                            user_id,
                            existing_id,
                        )
                    else:
                        cur.execute(
                            """
                            INSERT INTO dbo.ProjectFiles
                            (
                                DoorModelId,
                                FileName,
                                FileExtension,
                                FileData,
                                SourceWidth,
                                SourceHeight,
                                SourceDoorOpening,
                                CurrentDoorOpening,
                                GrowthAxis,
                                AxisLinkMode,
                                LinkX,
                                LinkY,
                                Status,
                                CreatedByUserId,
                                CreatedAt
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, N'Registered', ?, SYSDATETIME())
                            """,
                            door_model_id,
                            file_name,
                            ext,
                            pyodbc.Binary(data),
                            source_width,
                            source_height,
                            source_opening,
                            current_opening,
                            user_id,
                        )

                conn.commit()

            return int(door_model_id)

        except Exception as exc:
            self.last_error = str(exc)
            return None

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def _to_float(value):
        return None if value is None else float(value)

    @staticmethod
    def _row_to_dict(row) -> Dict[str, Any]:
        if row is None:
            return {}
        return {column[0]: getattr(row, column[0]) for column in row.cursor_description}

    def _scalar(self, cur, sql: str, *params):
        row = cur.execute(sql, *params).fetchone()
        return row[0] if row else None

    # ============================================================
    # AUTH
    # ============================================================

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        sql = """
        SELECT Id, Username, FullName, IsActive
        FROM dbo.Users
        WHERE Username = ? AND PasswordHash = ? AND IsActive = 1
        """

        with self.connect() as conn:
            cur = conn.cursor()

            row = cur.execute(sql, username, self.hash_password(password)).fetchone()

            # Тимчасово дозволяє старий plain text пароль під час міграції.
            if not row:
                row = cur.execute(sql, username, password).fetchone()

            if not row:
                return None

            return {
                "id": int(row.Id),
                "username": row.Username,
                "full_name": row.FullName,
            }

    # ============================================================
    # DOOR MODEL
    # ============================================================

    def get_or_create_door_model(
        self,
        folder_path: str,
        model_name: Optional[str],
        source_width: Optional[float],
        source_height: Optional[float],
        source_door_opening: str,
        user_id: int,
        growth_axis: str = "both",
        axis_link_mode: str = "normal",
        link_x: str = "X = W",
        link_y: str = "Y = H",
    ) -> Optional[int]:
        """
        Одна папка = одна DoorModel.

        Якщо модель для SourceFolderPath вже існує — оновлюємо базові параметри,
        але не створюємо дубль.
        """
        try:
            folder_path = os.path.abspath(folder_path)
            model_name = model_name or os.path.basename(folder_path) or "DoorModel"

            with self.connect() as conn:
                cur = conn.cursor()

                model_id = self._scalar(
                    cur,
                    """
                    SELECT TOP 1 Id
                    FROM dbo.DoorModels
                    WHERE SourceFolderPath = ?
                    ORDER BY Id DESC
                    """,
                    folder_path,
                )

                if model_id is None:
                    cur.execute(
                        """
                        INSERT INTO dbo.DoorModels
                        (
                            ModelName,
                            SourceFolderPath,
                            SourceWidth,
                            SourceHeight,
                            SourceDoorOpening,
                            GrowthAxis,
                            AxisLinkMode,
                            LinkX,
                            LinkY,
                            CreatedByUserId,
                            CreatedAt
                        )
                        OUTPUT INSERTED.Id
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
                        """,
                        model_name,
                        folder_path,
                        source_width,
                        source_height,
                        source_door_opening or "left",
                        "both",
                        "normal",
                        "X = W",
                        "Y = H",
                        user_id,
                    )
                    model_id = int(cur.fetchone()[0])
                else:
                    cur.execute(
                        """
                        UPDATE dbo.DoorModels
                        SET
                            ModelName = ?,
                            SourceWidth = COALESCE(?, SourceWidth),
                            SourceHeight = COALESCE(?, SourceHeight),
                            SourceDoorOpening = COALESCE(?, SourceDoorOpening),
                            UpdatedByUserId = ?,
                            UpdatedAt = SYSDATETIME()
                        WHERE Id = ?
                        """,
                        model_name,
                        source_width,
                        source_height,
                        source_door_opening or "left",
                        growth_axis or "both",
                        axis_link_mode or "normal",
                        link_x or "X = W",
                        link_y or "Y = H",
                        user_id,
                        model_id,
                    )

                conn.commit()
                return int(model_id)

        except Exception as exc:
            self.last_error = str(exc)
            return None

    def update_door_model_from_meta(
        self,
        door_model_id: int,
        project_meta: Dict[str, Any],
        user_id: int,
    ) -> bool:
        """
        Оновлює тільки спільні дані моделі дверей.

        ВАЖЛИВО: осі файлу НЕ оновлюються тут.
        AxisLinkMode / LinkX / LinkY / GrowthAxis належать ProjectFiles,
        бо для різних DXF у тій самій папці вони можуть бути різними.
        """
        try:
            with self.connect() as conn:
                conn.cursor().execute(
                    """
                    UPDATE dbo.DoorModels
                    SET
                        SourceWidth = ?,
                        SourceHeight = ?,
                        SourceDoorOpening = ?,
                        UpdatedByUserId = ?,
                        UpdatedAt = SYSDATETIME()
                    WHERE Id = ?
                    """,
                    project_meta.get("source_width"),
                    project_meta.get("source_height"),
                    project_meta.get("source_door_opening") or project_meta.get("door_opening") or "left",
                    user_id,
                    door_model_id,
                )
                conn.commit()
            return True
        except Exception as exc:
            self.last_error = str(exc)
            return False

    def load_door_model(self, door_model_id: int) -> Optional[Dict[str, Any]]:
        try:
            with self.connect() as conn:
                cur = conn.cursor()

                model = cur.execute(
                    """
                    SELECT *
                    FROM dbo.DoorModels
                    WHERE Id = ?
                    """,
                    door_model_id,
                ).fetchone()

                if not model:
                    return None

                files = cur.execute(
                    """
                    SELECT Id, FileName, FileExtension, DoorModelId, Status, CreatedAt, UpdatedAt
                    FROM dbo.ProjectFiles
                    WHERE DoorModelId = ?
                    ORDER BY FileName
                    """,
                    door_model_id,
                ).fetchall()

                model_meta = {
                    "source_width": self._to_float(model.SourceWidth),
                    "source_height": self._to_float(model.SourceHeight),
                    "target_width": self._to_float(model.SourceWidth),
                    "target_height": self._to_float(model.SourceHeight),
                    "door_opening": model.SourceDoorOpening or "left",
                    "source_door_opening": model.SourceDoorOpening or "left",
                    "target_door_opening": model.SourceDoorOpening or "left",
                    # Осі не беремо з DoorModels: вони зберігаються окремо в ProjectFiles.
                    "growth_axis": "both",
                    "axis_link_mode": "normal",
                    "link_x": "X = W",
                    "link_y": "Y = H",
                }

                return {
                    "id": int(model.Id),
                    "model_name": model.ModelName,
                    "folder_path": model.SourceFolderPath,
                    "meta": model_meta,
                    "files": [
                        {
                            "id": int(row.Id),
                            "file_name": row.FileName,
                            "extension": row.FileExtension,
                            "door_model_id": int(row.DoorModelId) if row.DoorModelId else None,
                            "status": row.Status,
                        }
                        for row in files
                    ],
                }

        except Exception as exc:
            self.last_error = str(exc)
            return None

    def find_door_model_by_folder(self, folder_path: str) -> Optional[int]:
        try:
            folder_path = os.path.abspath(folder_path)
            with self.connect() as conn:
                cur = conn.cursor()
                value = self._scalar(
                    cur,
                    """
                    SELECT TOP 1 Id
                    FROM dbo.DoorModels
                    WHERE SourceFolderPath = ?
                    ORDER BY Id DESC
                    """,
                    folder_path,
                )
                return int(value) if value is not None else None
        except Exception as exc:
            self.last_error = str(exc)
            return None

    # ============================================================
    # PROJECT FILE
    # ============================================================

    def save_project_snapshot(
        self,
        project_dir: str,
        dxf_path: str,
        project_meta: Dict[str, Any],
        parametric_groups: List[Dict[str, Any]],
        block_keep_state: Dict[str, bool],
        user_id: int,
        status: str = "ConfigSaved",
        project_file_id: Optional[int] = None,
        door_model_id: Optional[int] = None,
    ) -> Optional[int]:
        """
        Upsert поточного DXF + його групи.

        Спільні параметри моделі пишуться в DoorModels.
        TargetWidth/TargetHeight не пишуться в ProjectFiles як постійний стан.
        """
        if not os.path.exists(dxf_path):
            self.last_error = f"DXF не знайдено: {dxf_path}"
            return None

        try:
            project_dir = os.path.abspath(project_dir)
            dxf_path = os.path.abspath(dxf_path)
            axis_link_mode = self.normalize_axis_link_mode(
                project_meta.get("axis_link_mode"),
                project_meta.get("link_x"),
                project_meta.get("link_y"),
            )
            link_x, link_y = self.axis_pair_for_mode(axis_link_mode)
            project_meta["axis_link_mode"] = axis_link_mode
            project_meta["link_x"] = link_x
            project_meta["link_y"] = link_y

            if door_model_id is None:
                door_model_id = self.get_or_create_door_model(
                    folder_path=project_dir,
                    model_name=os.path.basename(project_dir),
                    source_width=project_meta.get("source_width"),
                    source_height=project_meta.get("source_height"),
                    source_door_opening=project_meta.get("source_door_opening")
                    or project_meta.get("door_opening")
                    or "left",
                    user_id=user_id,
                )

            if door_model_id is None:
                self.last_error = "Не вдалося створити/знайти DoorModel."
                return None

            self.update_door_model_from_meta(door_model_id, project_meta, user_id)

            with open(dxf_path, "rb") as f:
                file_data = f.read()

            file_name = os.path.basename(dxf_path)
            ext = os.path.splitext(file_name)[1] or ".dxf"
            text = project_meta.get("door_text") or {}

            with self.connect() as conn:
                cur = conn.cursor()

                if project_file_id is None:
                    project_file_id = self._scalar(
                        cur,
                        """
                        SELECT TOP 1 Id
                        FROM dbo.ProjectFiles
                        WHERE DoorModelId = ? AND FileName = ?
                        ORDER BY Id DESC
                        """,
                        door_model_id,
                        file_name,
                    )

                if project_file_id is None:
                    cur.execute(
                        """
                        INSERT INTO dbo.ProjectFiles
                        (
                            DoorModelId,
                            FileName,
                            FileExtension,
                            FileData,
                            SourceWidth,
                            SourceHeight,
                            SourceDoorOpening,
                            CurrentDoorOpening,
                            GrowthAxis,
                            AxisLinkMode,
                            LinkX,
                            LinkY,
                            Status,
                            CreatedByUserId,
                            CreatedAt
                        )
                        OUTPUT INSERTED.Id
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
                        """,
                        door_model_id,
                        file_name,
                        ext,
                        pyodbc.Binary(file_data),
                        project_meta.get("source_width"),
                        project_meta.get("source_height"),
                        project_meta.get("source_door_opening") or project_meta.get("door_opening") or "left",
                        project_meta.get("door_opening") or project_meta.get("source_door_opening") or "left",
                        project_meta.get("growth_axis") or "both",
                        axis_link_mode,
                        link_x,
                        link_y,
                        status,
                        user_id,
                    )
                    project_file_id = int(cur.fetchone()[0])
                else:
                    cur.execute(
                        """
                        UPDATE dbo.ProjectFiles
                        SET
                            DoorModelId = ?,
                            FileName = ?,
                            FileExtension = ?,
                            FileData = ?,
                            SourceWidth = ?,
                            SourceHeight = ?,
                            SourceDoorOpening = ?,
                            CurrentDoorOpening = ?,
                            GrowthAxis = ?,
                            AxisLinkMode = ?,
                            LinkX = ?,
                            LinkY = ?,
                            Status = ?,
                            UpdatedByUserId = ?,
                            UpdatedAt = SYSDATETIME()
                        WHERE Id = ?
                        """,
                        door_model_id,
                        file_name,
                        ext,
                        pyodbc.Binary(file_data),
                        project_meta.get("source_width"),
                        project_meta.get("source_height"),
                        project_meta.get("source_door_opening") or project_meta.get("door_opening") or "left",
                        project_meta.get("door_opening") or project_meta.get("source_door_opening") or "left",
                        project_meta.get("growth_axis") or "both",
                        axis_link_mode,
                        link_x,
                        link_y,
                        status,
                        user_id,
                        project_file_id,
                    )

                self._save_text_settings(cur, project_file_id, text)
                self._save_groups(cur, project_file_id, parametric_groups, block_keep_state)

                cur.execute(
                    """
                    INSERT INTO dbo.ActionLog
                    (UserId, ActionType, EntityType, EntityId, Details)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    user_id,
                    status,
                    "ProjectFile",
                    str(project_file_id),
                    f"Saved {file_name} in DoorModelId={door_model_id}",
                )

                conn.commit()
                return int(project_file_id)

        except Exception as exc:
            self.last_error = str(exc)
            return None

    def _save_text_settings(self, cur, project_file_id: int, text: Dict[str, Any]) -> None:
        cur.execute(
            "DELETE FROM dbo.ProjectTextSettings WHERE ProjectFileId = ?",
            project_file_id,
        )

        cur.execute(
            """
            INSERT INTO dbo.ProjectTextSettings
            (
                ProjectFileId,
                Enabled,
                TextValue,
                X,
                Y,
                Height,
                WidthFactor,
                Rotation,
                FontName,
                EntityHandle
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            project_file_id,
            1 if text.get("enabled") else 0,
            text.get("text") or "",
            text.get("x") or 0,
            text.get("y") or 0,
            text.get("height") or 30,
            text.get("width_factor") or 120,
            text.get("rotation") or 0,
            text.get("font") or "STANDARD",
            text.get("handle"),
        )

    def _save_groups(
        self,
        cur,
        project_file_id: int,
        parametric_groups: List[Dict[str, Any]],
        block_keep_state: Dict[str, bool],
    ) -> None:
        cur.execute(
            """
            DELETE FROM dbo.ProjectGroupEntities
            WHERE ProjectGroupId IN (
                SELECT Id
                FROM dbo.ProjectGroups
                WHERE ProjectFileId = ?
            )
            """,
            project_file_id,
        )
        cur.execute(
            "DELETE FROM dbo.ProjectGroups WHERE ProjectFileId = ?",
            project_file_id,
        )
        cur.execute(
            "DELETE FROM dbo.ProjectBlockStates WHERE ProjectFileId = ?",
            project_file_id,
        )

        for sort_order, group in enumerate(parametric_groups):
            handles = sorted(str(h) for h in group.get("handles", []))
            uid = group.get("uid") or f"{group.get('name', 'group')}|{','.join(handles)}"
            keep = 1 if block_keep_state.get(uid, True) else 0

            cur.execute(
                """
                INSERT INTO dbo.ProjectGroups
                (
                    ProjectFileId,
                    Name,
                    Uid,
                    K_W,
                    K_H,
                    Growth_P_W,
                    Growth_P_H,
                    Growth_Dir_X,
                    Growth_Dir_Y,
                    Shift_Dir_X,
                    Shift_Dir_Y,
                    Link_X,
                    Link_Y,
                    Resizes,
                    IsKeep,
                    SortOrder,
                    CreatedAt
                )
                OUTPUT INSERTED.Id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
                """,
                project_file_id,
                group.get("name") or "Група",
                uid,
                group.get("k_w") or 0,
                group.get("k_h") or 0,
                group.get("growth_p_w") or 0,
                group.get("growth_p_h") or 0,
                group.get("growth_dir_x") or "Центр",
                group.get("growth_dir_y") or "Центр",
                group.get("shift_dir_x") or "Вправо",
                group.get("shift_dir_y") or "Вгору",
                group.get("link_x") or "X = W",
                group.get("link_y") or "Y = H",
                1 if group.get("resizes") else 0,
                keep,
                sort_order,
            )

            group_id = int(cur.fetchone()[0])

            for handle in handles:
                cur.execute(
                    """
                    INSERT INTO dbo.ProjectGroupEntities
                    (ProjectGroupId, EntityHandle)
                    VALUES (?, ?)
                    """,
                    group_id,
                    handle,
                )

            cur.execute(
                """
                INSERT INTO dbo.ProjectBlockStates
                (ProjectFileId, BlockKey, BlockName, IsKeep)
                VALUES (?, ?, ?, ?)
                """,
                project_file_id,
                uid,
                group.get("name") or "Група",
                keep,
            )

    def load_project_config(
        self,
        dxf_path: str = None,
        project_file_id: int = None,
        door_model_id: int = None,
        file_name: str = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Завантаження конкретного DXF.

        Якщо передано DoorModelId + FileName — шукає файл в цій моделі.
        Якщо передано ProjectFileId — завантажує напряму.
        Старий пошук по LocalPath НЕ використовується, бо LocalPath вже немає в БД.
        """
        try:
            if file_name is None and dxf_path:
                file_name = os.path.basename(dxf_path)

            with self.connect() as conn:
                cur = conn.cursor()

                if project_file_id is None and door_model_id is not None and file_name:
                    project_file_id = self._scalar(
                        cur,
                        """
                        SELECT TOP 1 Id
                        FROM dbo.ProjectFiles
                        WHERE DoorModelId = ? AND FileName = ?
                        ORDER BY Id DESC
                        """,
                        door_model_id,
                        file_name,
                    )

                if project_file_id is None:
                    return None

                file_row = cur.execute(
                    """
                    SELECT *
                    FROM dbo.ProjectFiles
                    WHERE Id = ?
                    """,
                    project_file_id,
                ).fetchone()

                if not file_row:
                    return None

                model_row = None
                if file_row.DoorModelId:
                    model_row = cur.execute(
                        """
                        SELECT *
                        FROM dbo.DoorModels
                        WHERE Id = ?
                        """,
                        file_row.DoorModelId,
                    ).fetchone()

                meta = self._build_meta_from_rows(file_row, model_row)

                text_row = cur.execute(
                    """
                    SELECT *
                    FROM dbo.ProjectTextSettings
                    WHERE ProjectFileId = ?
                    """,
                    project_file_id,
                ).fetchone()

                meta["door_text"] = self._build_text_settings(text_row)

                groups, block_keep_state = self._load_groups(cur, project_file_id)

                return {
                    "door_model_id": int(file_row.DoorModelId) if file_row.DoorModelId else None,
                    "project_file_id": int(project_file_id),
                    "meta": meta,
                    "groups": groups,
                    "block_keep_state": block_keep_state,
                }

        except Exception as exc:
            self.last_error = str(exc)
            return None

    def _build_meta_from_rows(self, file_row, model_row) -> Dict[str, Any]:
        source_width = self._to_float(model_row.SourceWidth) if model_row else self._to_float(file_row.SourceWidth)
        source_height = self._to_float(model_row.SourceHeight) if model_row else self._to_float(file_row.SourceHeight)
        source_opening = (
            model_row.SourceDoorOpening
            if model_row and model_row.SourceDoorOpening
            else file_row.SourceDoorOpening
        ) or "left"

        # Осі файлу є параметрами конкретного DXF, тому беремо їх тільки з ProjectFiles.
        axis_link_mode = self.normalize_axis_link_mode(
            file_row.AxisLinkMode or "normal",
            file_row.LinkX,
            file_row.LinkY,
        )
        link_x, link_y = self.axis_pair_for_mode(axis_link_mode)

        return {
            "source_width": source_width,
            "source_height": source_height,

            # Цільові розміри тільки для UI. Вони не є постійним станом БД.
            "target_width": source_width,
            "target_height": source_height,

            "door_opening": file_row.CurrentDoorOpening or source_opening,
            "source_door_opening": source_opening,
            "target_door_opening": file_row.CurrentDoorOpening or source_opening,

            "growth_axis": file_row.GrowthAxis or "both",
            "axis_link_mode": axis_link_mode,
            "link_x": link_x,
            "link_y": link_y,
        }

    def _build_text_settings(self, text_row) -> Dict[str, Any]:
        if not text_row:
            return {
                "enabled": False,
                "text": "",
                "x": 0.0,
                "y": 0.0,
                "height": 30.0,
                "width_factor": 120.0,
                "rotation": 0.0,
                "font": "STANDARD",
                "handle": None,
            }

        return {
            "enabled": bool(text_row.Enabled),
            "text": text_row.TextValue or "",
            "x": self._to_float(text_row.X) or 0.0,
            "y": self._to_float(text_row.Y) or 0.0,
            "height": self._to_float(text_row.Height) or 30.0,
            "width_factor": self._to_float(text_row.WidthFactor) or 120.0,
            "rotation": self._to_float(text_row.Rotation) or 0.0,
            "font": text_row.FontName or "STANDARD",
            "handle": text_row.EntityHandle,
        }

    def _load_groups(self, cur, project_file_id: int):
        groups = []
        block_keep_state = {}

        group_rows = cur.execute(
            """
            SELECT *
            FROM dbo.ProjectGroups
            WHERE ProjectFileId = ?
            ORDER BY SortOrder, Id
            """,
            project_file_id,
        ).fetchall()

        for gr in group_rows:
            handles = {
                r.EntityHandle
                for r in cur.execute(
                    """
                    SELECT EntityHandle
                    FROM dbo.ProjectGroupEntities
                    WHERE ProjectGroupId = ?
                    """,
                    gr.Id,
                ).fetchall()
            }

            group = {
                "uid": gr.Uid,
                "name": gr.Name,
                "handles": handles,
                "k_w": float(gr.K_W or 0),
                "k_h": float(gr.K_H or 0),
                "growth_p_w": float(gr.Growth_P_W or 0),
                "growth_p_h": float(gr.Growth_P_H or 0),
                "growth_dir_x": gr.Growth_Dir_X or "Центр",
                "growth_dir_y": gr.Growth_Dir_Y or "Центр",
                "shift_dir_x": gr.Shift_Dir_X or "Вправо",
                "shift_dir_y": gr.Shift_Dir_Y or "Вгору",
                "link_x": gr.Link_X or "X = W",
                "link_y": gr.Link_Y or "Y = H",
                "resizes": bool(gr.Resizes),
            }

            groups.append(group)
            block_keep_state[gr.Uid] = bool(gr.IsKeep)

        return groups, block_keep_state

    def get_model_files(self, door_model_id: int) -> List[Dict[str, Any]]:
        try:
            with self.connect() as conn:
                rows = conn.cursor().execute(
                    """
                    SELECT Id, FileName, FileExtension, Status, CreatedAt, UpdatedAt
                    FROM dbo.ProjectFiles
                    WHERE DoorModelId = ?
                    ORDER BY FileName
                    """,
                    door_model_id,
                ).fetchall()

                return [
                    {
                        "id": int(r.Id),
                        "file_name": r.FileName,
                        "extension": r.FileExtension,
                        "status": r.Status,
                        "created_at": r.CreatedAt,
                        "updated_at": r.UpdatedAt,
                    }
                    for r in rows
                ]
        except Exception as exc:
            self.last_error = str(exc)
            return []

    def list_project_files(self, limit: int = 300) -> List[Dict[str, Any]]:
        try:
            with self.connect() as conn:
                rows = conn.cursor().execute(
                    f"""
                    SELECT TOP ({int(limit)})
                        Id,
                        FileName,
                        FileExtension,
                        DoorModelId,
                        Status,
                        CreatedAt,
                        UpdatedAt,
                        CASE WHEN FileData IS NULL THEN 0 ELSE 1 END AS HasFileData
                    FROM dbo.ProjectFiles
                    WHERE LOWER(ISNULL(FileExtension, N'.dxf')) LIKE N'%dxf%'
                       OR LOWER(ISNULL(FileName, N'')) LIKE N'%.dxf'
                    ORDER BY COALESCE(UpdatedAt, CreatedAt) DESC, FileName
                    """
                ).fetchall()

                return [
                    {
                        "source": "ProjectFiles",
                        "id": int(row.Id),
                        "file_name": row.FileName,
                        "extension": row.FileExtension,
                        "door_model_id": int(row.DoorModelId) if row.DoorModelId else None,
                        "status": row.Status,
                        "created_at": row.CreatedAt,
                        "updated_at": row.UpdatedAt,
                        "has_file_data": bool(row.HasFileData),
                    }
                    for row in rows
                ]
        except Exception as exc:
            self.last_error = str(exc)
            return []

    def get_project_file_binary(self, project_file_id: int) -> Optional[bytes]:
        try:
            with self.connect() as conn:
                row = conn.cursor().execute(
                    """
                    SELECT FileData
                    FROM dbo.ProjectFiles
                    WHERE Id = ?
                    """,
                    project_file_id,
                ).fetchone()

                return bytes(row.FileData) if row and row.FileData is not None else None
        except Exception as exc:
            self.last_error = str(exc)
            return None

    # ============================================================
    # EXPORTS / JSON BACKUP
    # ============================================================

    def save_export_file(
        self,
        source_project_file_id: int,
        export_path: str,
        width: float,
        height: float,
        opening: str,
        user_id: int,
        door_model_id: Optional[int] = None,
    ) -> bool:
        try:
            if not os.path.exists(export_path):
                self.last_error = f"Export DXF не знайдено: {export_path}"
                return False

            with open(export_path, "rb") as f:
                file_data = f.read()

            if door_model_id is None:
                with self.connect() as conn:
                    cur = conn.cursor()
                    door_model_id = self._scalar(
                        cur,
                        """
                        SELECT DoorModelId
                        FROM dbo.ProjectFiles
                        WHERE Id = ?
                        """,
                        source_project_file_id,
                    )

            with self.connect() as conn:
                conn.cursor().execute(
                    """
                    INSERT INTO dbo.ProjectExports
                    (
                        SourceProjectFileId,
                        DoorModelId,
                        ExportFileName,
                        ExportFileData,
                        ExportWidth,
                        ExportHeight,
                        ExportDoorOpening,
                        CreatedByUserId,
                        CreatedAt
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
                    """,
                    source_project_file_id,
                    door_model_id,
                    os.path.basename(export_path),
                    pyodbc.Binary(file_data),
                    width,
                    height,
                    opening,
                    user_id,
                )
                conn.commit()

            return True

        except Exception as exc:
            self.last_error = str(exc)
            return False

    def export_project_json_backup(
        self,
        project_file_id: int,
        data: Dict[str, Any],
        user_id: int,
        backup_type: str = "ManualExport",
    ) -> bool:
        try:
            safe = json.dumps(data, ensure_ascii=False, indent=4, default=list)

            with self.connect() as conn:
                conn.cursor().execute(
                    """
                    INSERT INTO dbo.ProjectJsonBackups
                    (
                        ProjectFileId,
                        JsonData,
                        BackupType,
                        CreatedByUserId,
                        CreatedAt
                    )
                    VALUES (?, ?, ?, ?, SYSDATETIME())
                    """,
                    project_file_id,
                    safe,
                    backup_type,
                    user_id,
                )
                conn.commit()

            return True

        except Exception as exc:
            self.last_error = str(exc)
            return False

    def create_admin_user_if_empty(
        self,
        username: str = "admin",
        password: str = "admin",
        full_name: str = "Administrator",
    ) -> bool:
        try:
            with self.connect() as conn:
                cur = conn.cursor()

                count_users = self._scalar(cur, "SELECT COUNT(*) FROM dbo.Users") or 0
                if int(count_users) > 0:
                    return True

                cur.execute(
                    """
                    INSERT INTO dbo.Users
                    (Username, PasswordHash, FullName, IsActive, CreatedAt)
                    VALUES (?, ?, ?, 1, SYSDATETIME())
                    """,
                    username,
                    self.hash_password(password),
                    full_name,
                )

                conn.commit()
                return True

        except Exception as exc:
            self.last_error = str(exc)
            return False
