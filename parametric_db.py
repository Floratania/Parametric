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
        if self.connection_string:
            return [self.connection_string]
        return [
            (
                "DRIVER={ODBC Driver 18 for SQL Server};"
                "SERVER=localhost;"
                "DATABASE=parametric_db;"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            ),
            (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=localhost;"
                "DATABASE=parametric_db;"
                "Trusted_Connection=yes;"
            ),
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
