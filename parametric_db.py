import hashlib
import json
import os

try:
    import pyodbc
except ImportError:
    pyodbc = None

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class LoginDialog(QDialog):
    def __init__(self, parent=None, message=""):
        super().__init__(parent)
        self.setWindowTitle("Авторизація")
        self.setModal(True)

        layout = QVBoxLayout(self)
        if message:
            label = QLabel(message)
            label.setWordWrap(True)
            layout.addWidget(label)

        form = QFormLayout()
        self.input_username = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Користувач:", self.input_username)
        form.addRow("Пароль:", self.input_password)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def credentials(self):
        return self.input_username.text().strip(), self.input_password.text()


class ParametricDb:
    def __init__(self, connection_string=None):
        self.connection_string = connection_string or os.environ.get("PARAMETRIC_DB_CONN")
        self.last_error = ""
        self.available = False
        self._check_connection()

    def candidate_connection_strings(self):
        # Якщо рядок було явно передано при ініціалізації, використовуємо тільки його
        if self.connection_string:
            return [self.connection_string]
            
        # Якщо ні — перебираємо всі доступні варіанти (локальні та серверні)
        return [
            # 1. Новий сервер srv2 (Авторизація за логіном/паролем)
            (
                "DRIVER={SQL Server};"
                "SERVER=prog-srv;"
                "DATABASE=parametric_db;"
                "UID=sa;"
                "PWD=*Htlbcrf2oo6;"
            ),
            # 2. Робочий сервер (ODBC 18, Trusted Connection)
            (
                "DRIVER={ODBC Driver 18 for SQL Server};"
                "SERVER=prog-srv;"
                "DATABASE=parametric_db;"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            ),
            # 3. Локальний сервер (ODBC 17)
            (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=localhost;"
                "DATABASE=parametric_db;"
                "Trusted_Connection=yes;"
            ),
            # 4. Локальний сервер (Старий базовий драйвер)
            (
                "DRIVER={SQL Server};"
                "SERVER=localhost;"
                "DATABASE=parametric_db;"
                "Trusted_Connection=yes;"
            ),
        ]

  


    def connect(self):
        if pyodbc is None:
            raise RuntimeError("pyodbc не встановлено")
        last_error = None
        for connection_string in self.candidate_connection_strings():
            try:
                return pyodbc.connect(connection_string, timeout=3, autocommit=False)
            except Exception as exc:
                last_error = exc
        raise last_error

    def _check_connection(self):
        try:
            with self.connect() as conn:
                conn.cursor().execute("SELECT 1")
            self.available = True
            self.last_error = ""
        except Exception as exc:
            self.available = False
            self.last_error = str(exc)

    def hash_password(self, password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(self, password, stored_hash):
        stored_hash = str(stored_hash or "")
        return stored_hash == password or stored_hash == self.hash_password(password)

    def authenticate(self, username, password):
        if not username or not password:
            return None
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM dbo.Users")
            users_count = int(cur.fetchone()[0])
            if users_count == 0:
                password_hash = self.hash_password(password)
                cur.execute(
                    """
                    INSERT INTO dbo.Users (Username, PasswordHash, FullName, IsActive, CreatedAt)
                    OUTPUT INSERTED.Id
                    VALUES (?, ?, ?, 1, sysdatetime())
                    """,
                    username,
                    password_hash,
                    username,
                )
                user_id = int(cur.fetchone()[0])
                self.ensure_role(cur, "Admin")
                self.ensure_user_role(cur, user_id, "Admin")
                conn.commit()
                return {"id": user_id, "username": username, "full_name": username}

            cur.execute(
                """
                SELECT Id, Username, PasswordHash, FullName
                FROM dbo.Users
                WHERE Username = ? AND IsActive = 1
                """,
                username,
            )
            row = cur.fetchone()
            if not row or not self.verify_password(password, row.PasswordHash):
                return None
            return {"id": int(row.Id), "username": row.Username, "full_name": row.FullName}

    def ensure_role(self, cur, role_name):
        cur.execute("SELECT Id FROM dbo.Roles WHERE Name = ?", role_name)
        row = cur.fetchone()
        if row:
            return int(row.Id)
        cur.execute(
            "INSERT INTO dbo.Roles (Name) OUTPUT INSERTED.Id VALUES (?)",
            role_name,
        )
        return int(cur.fetchone()[0])

    def ensure_user_role(self, cur, user_id, role_name):
        role_id = self.ensure_role(cur, role_name)
        cur.execute(
            "SELECT 1 FROM dbo.UserRoles WHERE UserId = ? AND RoleId = ?",
            user_id,
            role_id,
        )
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO dbo.UserRoles (UserId, RoleId) VALUES (?, ?)",
                user_id,
                role_id,
            )

    def save_project_snapshot(self, folder_path, file_path, config_path, meta, groups, user_id, status):
        if not self.available or not user_id:
            return False
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                folder_id = self.upsert_folder(cur, folder_path, meta, user_id)
                self.upsert_file(cur, folder_id, file_path, config_path, meta, user_id, status)
                self.save_group_templates(cur, groups, user_id)
                self.log_action(
                    cur,
                    user_id,
                    status,
                    "Project",
                    os.path.basename(file_path or folder_path or ""),
                    file_path,
                    folder_path,
                    {"config": config_path},
                )
                conn.commit()
            return True
        except Exception as exc:
            self.last_error = str(exc)
            return False

    def upsert_folder(self, cur, folder_path, meta, user_id):
        folder_name = os.path.basename(os.path.normpath(folder_path)) if folder_path else None
        cur.execute("SELECT TOP 1 Id FROM dbo.ProcessedFolders WHERE FolderPath = ?", folder_path)
        row = cur.fetchone()
        values = (
            folder_name,
            meta.get("source_width"),
            meta.get("source_height"),
            meta.get("target_width"),
            meta.get("target_height"),
            meta.get("source_door_opening"),
            meta.get("target_door_opening") or meta.get("door_opening"),
            user_id,
        )
        if row:
            folder_id = int(row.Id)
            cur.execute(
                """
                UPDATE dbo.ProcessedFolders
                SET FolderName = ?, SourceWidth = ?, SourceHeight = ?,
                    TargetWidth = ?, TargetHeight = ?,
                    SourceDoorOpening = ?, TargetDoorOpening = ?,
                    LastOpenedAt = sysdatetime(), UpdatedByUserId = ?, UpdatedAt = sysdatetime()
                WHERE Id = ?
                """,
                *values,
                folder_id,
            )
            return folder_id

        cur.execute(
            """
            INSERT INTO dbo.ProcessedFolders
                (FolderPath, FolderName, SourceWidth, SourceHeight, TargetWidth, TargetHeight,
                 SourceDoorOpening, TargetDoorOpening, CreatedByUserId, CreatedAt, LastOpenedAt, AccessScope)
            OUTPUT INSERTED.Id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, sysdatetime(), sysdatetime(), N'Shared')
            """,
            folder_path,
            *values,
        )
        return int(cur.fetchone()[0])

    def upsert_file(self, cur, folder_id, file_path, config_path, meta, user_id, status):
        file_name = os.path.basename(file_path) if file_path else None
        cur.execute("SELECT TOP 1 Id FROM dbo.ProcessedFiles WHERE FilePath = ?", file_path)
        row = cur.fetchone()
        values = (
            folder_id,
            file_name,
            config_path,
            meta.get("source_width"),
            meta.get("source_height"),
            meta.get("target_width"),
            meta.get("target_height"),
            meta.get("target_door_opening") or meta.get("door_opening"),
            status,
            user_id,
        )
        if row:
            cur.execute(
                """
                UPDATE dbo.ProcessedFiles
                SET FolderId = ?, FileName = ?, ConfigJsonPath = ?,
                    SourceWidth = ?, SourceHeight = ?, TargetWidth = ?, TargetHeight = ?,
                    DoorOpening = ?, Status = ?, ProcessedAt = sysdatetime(), CreatedByUserId = ?
                WHERE Id = ?
                """,
                *values,
                int(row.Id),
            )
            return
        cur.execute(
            """
            INSERT INTO dbo.ProcessedFiles
                (FolderId, FilePath, FileName, ConfigJsonPath, SourceWidth, SourceHeight,
                 TargetWidth, TargetHeight, DoorOpening, Status, ProcessedAt, CreatedByUserId, CreatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, sysdatetime(), ?, sysdatetime())
            """,
            folder_id,
            file_path,
            *values[1:],
        )

    def save_group_templates(self, cur, groups, user_id):
        for index, group in enumerate(groups or []):
            name = str(group.get("name") or "").strip()
            if not name:
                continue
            cur.execute("SELECT Id FROM dbo.GroupNameTemplates WHERE Name = ?", name)
            if not cur.fetchone():
                cur.execute(
                    """
                    INSERT INTO dbo.GroupNameTemplates
                        (Name, Description, SortOrder, IsActive, CreatedByUserId, CreatedAt)
                    VALUES (?, ?, ?, 1, ?, sysdatetime())
                    """,
                    name,
                    "Manual group name",
                    index,
                    user_id,
                )
            self.upsert_rule_template(cur, group, user_id)

    def upsert_rule_template(self, cur, group, user_id):
        name = str(group.get("name") or "").strip()
        if not name:
            return
        values = (
            "Saved from CAD group",
            float(group.get("k_w", 0.0) or 0.0),
            float(group.get("k_h", 0.0) or 0.0),
            float(group.get("growth_p_w", 0.0) or 0.0),
            float(group.get("growth_p_h", 0.0) or 0.0),
            str(group.get("growth_dir_x", "Центр")),
            str(group.get("growth_dir_y", "Центр")),
            str(group.get("shift_dir_x", "Вправо")),
            str(group.get("shift_dir_y", "Вгору")),
            str(group.get("link_x", "X = W")),
            str(group.get("link_y", "Y = H")),
            user_id,
        )
        cur.execute("SELECT Id FROM dbo.RuleTemplates WHERE Name = ?", name)
        row = cur.fetchone()
        if row:
            cur.execute(
                """
                UPDATE dbo.RuleTemplates
                SET Description = ?, K_W = ?, K_H = ?, Growth_P_W = ?, Growth_P_H = ?,
                    Growth_Dir_X = ?, Growth_Dir_Y = ?, Shift_Dir_X = ?, Shift_Dir_Y = ?,
                    Link_X = ?, Link_Y = ?, IsActive = 1, CreatedByUserId = ?
                WHERE Id = ?
                """,
                *values,
                int(row.Id),
            )
            return
        cur.execute(
            """
            INSERT INTO dbo.RuleTemplates
                (Name, Description, K_W, K_H, Growth_P_W, Growth_P_H,
                 Growth_Dir_X, Growth_Dir_Y, Shift_Dir_X, Shift_Dir_Y,
                 Link_X, Link_Y, IsSystem, IsActive, CreatedByUserId, CreatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 1, ?, sysdatetime())
            """,
            name,
            *values,
        )

    def table_exists(self, cur, table_name):
        row = cur.execute("SELECT OBJECT_ID(?, N'U')", f"dbo.{table_name}").fetchone()
        return bool(row and row[0])

    def list_project_files(self, limit=300):
        if not self.available:
            return []
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                if self.table_exists(cur, "ProjectFiles"):
                    rows = cur.execute(
                        f"""
                        SELECT TOP ({int(limit)})
                            Id, FileName, FileExtension, DoorModelId, Status, CreatedAt, UpdatedAt
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
                        }
                        for row in rows
                    ]

                if self.table_exists(cur, "ProcessedFiles"):
                    rows = cur.execute(
                        f"""
                        SELECT TOP ({int(limit)})
                            Id, FilePath, FileName, ConfigJsonPath, Status, ProcessedAt, CreatedAt
                        FROM dbo.ProcessedFiles
                        WHERE LOWER(ISNULL(FileName, N'')) LIKE N'%.dxf'
                           OR LOWER(ISNULL(FilePath, N'')) LIKE N'%.dxf'
                        ORDER BY COALESCE(ProcessedAt, CreatedAt) DESC, FileName
                        """
                    ).fetchall()
                    return [
                        {
                            "source": "ProcessedFiles",
                            "id": int(row.Id),
                            "file_name": row.FileName,
                            "file_path": row.FilePath,
                            "config_json_path": row.ConfigJsonPath,
                            "status": row.Status,
                            "created_at": row.CreatedAt,
                            "updated_at": row.ProcessedAt,
                        }
                        for row in rows
                    ]
        except Exception as exc:
            self.last_error = str(exc)
        return []

    def get_project_file_binary(self, project_file_id):
        if not self.available:
            return None
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                if not self.table_exists(cur, "ProjectFiles"):
                    return None
                row = cur.execute(
                    "SELECT FileData FROM dbo.ProjectFiles WHERE Id = ?",
                    project_file_id,
                ).fetchone()
                return bytes(row.FileData) if row and row.FileData is not None else None
        except Exception as exc:
            self.last_error = str(exc)
            return None

    def load_project_config_from_db(self, project_file_id):
        if not self.available:
            return None
        try:
            with self.connect() as conn:
                cur = conn.cursor()
                if not all(
                    self.table_exists(cur, table)
                    for table in ("ProjectFiles", "ProjectGroups", "ProjectGroupEntities")
                ):
                    return None

                file_row = cur.execute(
                    "SELECT * FROM dbo.ProjectFiles WHERE Id = ?",
                    project_file_id,
                ).fetchone()
                if not file_row:
                    return None

                model_row = None
                if getattr(file_row, "DoorModelId", None) and self.table_exists(cur, "DoorModels"):
                    model_row = cur.execute(
                        "SELECT * FROM dbo.DoorModels WHERE Id = ?",
                        file_row.DoorModelId,
                    ).fetchone()

                def as_float(value):
                    return None if value is None else float(value)

                source_width = as_float(getattr(model_row, "SourceWidth", None)) if model_row else as_float(getattr(file_row, "SourceWidth", None))
                source_height = as_float(getattr(model_row, "SourceHeight", None)) if model_row else as_float(getattr(file_row, "SourceHeight", None))
                source_opening = (
                    getattr(model_row, "SourceDoorOpening", None) if model_row else None
                ) or getattr(file_row, "SourceDoorOpening", None) or "left"
                current_opening = getattr(file_row, "CurrentDoorOpening", None) or source_opening

                meta = {
                    "source_width": source_width,
                    "source_height": source_height,
                    "target_width": source_width,
                    "target_height": source_height,
                    "door_opening": current_opening,
                    "source_door_opening": source_opening,
                    "target_door_opening": current_opening,
                    "growth_axis": getattr(file_row, "GrowthAxis", None) or "both",
                    "axis_link_mode": getattr(file_row, "AxisLinkMode", None) or "normal",
                    "door_text": {
                        "enabled": False,
                        "text": "",
                        "x": 0.0,
                        "y": 0.0,
                        "height": 30.0,
                        "width_factor": 120.0,
                        "rotation": 0.0,
                        "font": "STANDARD",
                        "handle": None,
                    },
                }

                if self.table_exists(cur, "ProjectTextSettings"):
                    text_row = cur.execute(
                        "SELECT * FROM dbo.ProjectTextSettings WHERE ProjectFileId = ?",
                        project_file_id,
                    ).fetchone()
                    if text_row:
                        meta["door_text"] = {
                            "enabled": bool(getattr(text_row, "Enabled", False)),
                            "text": getattr(text_row, "TextValue", None) or "",
                            "x": as_float(getattr(text_row, "X", None)) or 0.0,
                            "y": as_float(getattr(text_row, "Y", None)) or 0.0,
                            "height": as_float(getattr(text_row, "Height", None)) or 30.0,
                            "width_factor": as_float(getattr(text_row, "WidthFactor", None)) or 120.0,
                            "rotation": as_float(getattr(text_row, "Rotation", None)) or 0.0,
                            "font": getattr(text_row, "FontName", None) or "STANDARD",
                            "handle": getattr(text_row, "EntityHandle", None),
                        }

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
                for group_row in group_rows:
                    handles = {
                        row.EntityHandle
                        for row in cur.execute(
                            "SELECT EntityHandle FROM dbo.ProjectGroupEntities WHERE ProjectGroupId = ?",
                            group_row.Id,
                        ).fetchall()
                    }
                    uid = getattr(group_row, "Uid", None) or f"{group_row.Name}|{group_row.Id}"
                    group = {
                        "uid": uid,
                        "name": group_row.Name,
                        "handles": handles,
                        "k_w": float(getattr(group_row, "K_W", 0) or 0),
                        "k_h": float(getattr(group_row, "K_H", 0) or 0),
                        "growth_p_w": float(getattr(group_row, "Growth_P_W", 0) or 0),
                        "growth_p_h": float(getattr(group_row, "Growth_P_H", 0) or 0),
                        "growth_dir_x": getattr(group_row, "Growth_Dir_X", None) or "Р¦РµРЅС‚СЂ",
                        "growth_dir_y": getattr(group_row, "Growth_Dir_Y", None) or "Р¦РµРЅС‚СЂ",
                        "shift_dir_x": getattr(group_row, "Shift_Dir_X", None) or "Р’РїСЂР°РІРѕ",
                        "shift_dir_y": getattr(group_row, "Shift_Dir_Y", None) or "Р’РіРѕСЂСѓ",
                        "link_x": getattr(group_row, "Link_X", None) or "X = W",
                        "link_y": getattr(group_row, "Link_Y", None) or "Y = H",
                        "resizes": bool(getattr(group_row, "Resizes", True)),
                    }
                    groups.append(group)
                    block_keep_state[uid] = bool(getattr(group_row, "IsKeep", True))

                return {
                    "project_file_id": int(project_file_id),
                    "door_model_id": int(file_row.DoorModelId) if getattr(file_row, "DoorModelId", None) else None,
                    "meta": meta,
                    "groups": groups,
                    "block_keep_state": block_keep_state,
                }
        except Exception as exc:
            self.last_error = str(exc)
            return None

    def log_action(self, cur, user_id, action_type, entity_type, entity_id, file_path, folder_path, details):
        cur.execute(
            """
            INSERT INTO dbo.ActionLog
                (UserId, ActionType, EntityType, EntityId, FilePath, FolderPath, Details, CreatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, sysdatetime())
            """,
            user_id,
            action_type,
            entity_type,
            entity_id,
            file_path,
            folder_path,
            json.dumps(details or {}, ensure_ascii=False),
        )
