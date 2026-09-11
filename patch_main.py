import re
with open('app/ui/main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the place where CompetitionDashboardView is created
target = '''            from app.ui.views.competition_dashboard_view import CompetitionDashboardView
            return CompetitionDashboardView()'''

replacement = '''            from app.ui.views.competition_dashboard_view import CompetitionDashboardView
            view = CompetitionDashboardView()
            view.case_activated.connect(self.set_active_case)
            return view'''

if target in content:
    content = content.replace(target, replacement)
    with open('app/ui/main_window.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched main_window.py successfully")
else:
    print("Could not find the target string in main_window.py")
