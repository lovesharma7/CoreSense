import json
import os
from datetime import datetime

class TaskManager:
    def __init__(self, filename='tasks.json'):
        self.filename = filename
        self.tasks = []
        self.next_id = 1
        self.load_from_file()
    
    def add_task(self, description, priority='Medium', status='Pending'):
        task = {
            'id': self.next_id,
            'description': description,
            'priority': priority,
            'status': status,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }        
        self.tasks.append(task)
        self.next_id += 1
        return task['id']
    
    def get_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def get_all_tasks(self):
        return self.tasks
    
    def update_task(self, task_id, description=None, priority=None, status=None):
        task = self.get_task(task_id)
        if task:
            if description is not None:
                task['description'] = description
            if priority is not None:
                task['priority'] = priority
            if status is not None:
                task['status'] = status
            return True
        return False
    
    def update_task_status(self, task_id, status):
        return self.update_task(task_id, status=status)
    
    def delete_task(self, task_id):
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False
    
    def get_tasks_by_status(self, status):
        return [task for task in self.tasks if task['status'] == status]
    
    def save_to_file(self):
        try:
            data = {
                'tasks': self.tasks,
                'next_id': self.next_id
            }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving tasks: {e}")
            return False
    
    def load_from_file(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', [])
                    self.next_id = data.get('next_id', 1)
                return True
            return False
        except Exception as e:
            print(f"Error loading tasks: {e}")
            return False
    
    def get_statistics(self):
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t['status'] == 'Completed'])
        pending = len([t for t in self.tasks if t['status'] == 'Pending'])
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }
