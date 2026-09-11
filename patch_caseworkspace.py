import re
with open('app/ui/views/case_workspace_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '''
        self.tabs.addTab(self.tab_iocs, "IOCs")
        
        # 4a. Flags
        self.tab_flags = QWidget()
        flag_layout = QVBoxLayout(self.tab_flags)
        
        self.table_flags = QTableWidget()
        self.table_flags.setColumnCount(4)
        self.table_flags.setHorizontalHeaderLabels(["ID", "Flag", "Status", "Actions"])
        
        btn_add_flag = QPushButton("Add Flag")
        btn_add_flag.clicked.connect(self.prompt_add_flag)
        
        flag_layout.addWidget(self.table_flags)
        flag_layout.addWidget(btn_add_flag)
        self.tabs.addTab(self.tab_flags, "Flags")
        
        # 4b. Tasks
        self.tab_tasks = QWidget()
        task_layout = QVBoxLayout(self.tab_tasks)
        
        self.table_tasks = QTableWidget()
        self.table_tasks.setColumnCount(4)
        self.table_tasks.setHorizontalHeaderLabels(["Title", "Status", "Priority", "Actions"])
        
        btn_add_task = QPushButton("Add Task")
        btn_add_task.clicked.connect(self.prompt_add_task)
        
        task_layout.addWidget(self.table_tasks)
        task_layout.addWidget(btn_add_task)
        self.tabs.addTab(self.tab_tasks, "Tasks")
        
        # 5. Reports
'''

if 'self.tabs.addTab(self.tab_iocs, "IOCs")' in content and '# 4a. Flags' not in content:
    content = content.replace('        self.tabs.addTab(self.tab_iocs, "IOCs")', patch)
    
    # Add methods to CaseWorkspaceView
    methods = '''
    def prompt_add_flag(self):
        if not self.current_case_id:
            return
        from PySide6.QtWidgets import QInputDialog
        flag, ok = QInputDialog.getText(self, "Add Flag", "Enter Flag:")
        if ok and flag:
            from app.database.database import db
            import uuid, time
            with db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO flags (id, case_id, flag_value, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (f"flag_{uuid.uuid4().hex[:8]}", self.current_case_id, flag, "CANDIDATE", time.time(), time.time())
                )
            self.refresh_case_data()
            
    def prompt_add_task(self):
        if not self.current_case_id:
            return
        from PySide6.QtWidgets import QInputDialog
        title, ok = QInputDialog.getText(self, "Add Task", "Task Title:")
        if ok and title:
            from app.database.database import db
            import uuid, time
            with db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO case_tasks (id, case_id, title, status, priority, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (f"task_{uuid.uuid4().hex[:8]}", self.current_case_id, title, "TODO", "MEDIUM", time.time(), time.time())
                )
            self.refresh_case_data()
            
    def update_flag_status(self, flag_id, status):
        from app.database.database import db
        with db.get_connection() as conn:
            conn.execute("UPDATE flags SET status = ? WHERE id = ?", (status, flag_id))
        self.refresh_case_data()

    def update_task_status(self, task_id, status):
        from app.database.database import db
        with db.get_connection() as conn:
            conn.execute("UPDATE case_tasks SET status = ? WHERE id = ?", (status, task_id))
        self.refresh_case_data()
'''
    
    refresh_patch = '''
        # Refresh Flags
        from app.database.database import db
        from PySide6.QtWidgets import QTableWidgetItem, QWidget, QHBoxLayout
        with db.get_connection() as conn:
            flags = conn.execute("SELECT id, flag_value, status FROM flags WHERE case_id = ?", (self.current_case_id,)).fetchall()
            self.table_flags.setRowCount(len(flags))
            for i, row in enumerate(flags):
                self.table_flags.setItem(i, 0, QTableWidgetItem(row['id']))
                self.table_flags.setItem(i, 1, QTableWidgetItem(row['flag_value']))
                self.table_flags.setItem(i, 2, QTableWidgetItem(row['status']))
                
                actions = QWidget()
                l = QHBoxLayout(actions)
                l.setContentsMargins(0,0,0,0)
                
                btn_c = QPushButton("Confirm")
                btn_c.clicked.connect(lambda _, fid=row['id']: self.update_flag_status(fid, "CONFIRMED"))
                btn_r = QPushButton("Reject")
                btn_r.clicked.connect(lambda _, fid=row['id']: self.update_flag_status(fid, "REJECTED"))
                
                l.addWidget(btn_c)
                l.addWidget(btn_r)
                self.table_flags.setCellWidget(i, 3, actions)
                
        # Refresh Tasks
        with db.get_connection() as conn:
            tasks = conn.execute("SELECT id, title, status, priority FROM case_tasks WHERE case_id = ?", (self.current_case_id,)).fetchall()
            self.table_tasks.setRowCount(len(tasks))
            for i, row in enumerate(tasks):
                self.table_tasks.setItem(i, 0, QTableWidgetItem(row['title']))
                self.table_tasks.setItem(i, 1, QTableWidgetItem(row['status']))
                self.table_tasks.setItem(i, 2, QTableWidgetItem(row['priority']))
                
                actions = QWidget()
                l = QHBoxLayout(actions)
                l.setContentsMargins(0,0,0,0)
                
                btn_d = QPushButton("Done")
                btn_d.clicked.connect(lambda _, tid=row['id']: self.update_task_status(tid, "DONE"))
                btn_r = QPushButton("Reopen")
                btn_r.clicked.connect(lambda _, tid=row['id']: self.update_task_status(tid, "TODO"))
                
                l.addWidget(btn_d)
                l.addWidget(btn_r)
                self.table_tasks.setCellWidget(i, 3, actions)
'''
    content += methods
    content = content.replace('self.tree_evidence.addTopLevelItem(item)', 'self.tree_evidence.addTopLevelItem(item)' + refresh_patch)
    with open('app/ui/views/case_workspace_view.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched case_workspace_view.py successfully")
else:
    print("Patch not applied. Maybe already applied.")
