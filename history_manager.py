class HistoryManager:
    def __init__(self, dxf_path):
        self.dxf_path = dxf_path
        self.undo_stack = []
        self.redo_stack = []

    def save_state(self):
        with open(self.dxf_path, "rb") as f:
            self.undo_stack.append(f.read())

        if len(self.undo_stack) > 30:
            self.undo_stack.pop(0)

    def undo(self):
        if len(self.undo_stack) <= 1:
            return None

        current_state = self.undo_stack.pop()
        self.redo_stack.append(current_state)

        previous_state = self.undo_stack[-1]

        with open(self.dxf_path, "wb") as f:
            f.write(previous_state)

        return previous_state

    def redo(self):
        if not self.redo_stack:
            return None

        next_state = self.redo_stack.pop()
        self.undo_stack.append(next_state)

        with open(self.dxf_path, "wb") as f:
            f.write(next_state)

        return next_state

    def clear_redo(self):
        self.redo_stack.clear()