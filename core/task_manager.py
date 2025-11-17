import json
import os
from datetime import datetime

class TaskManager:
    
    def __init__(self, filename='tasks.json'):
        self.filename = filename
        self.tasks = []
        self.next_id = 1
        self.load_from_file()
    
    def add_task(self, description, priority='Medium', category='Personal', deadline=None, 
                 status='Pending', progress=0, tags=None, notes=''):
        if progress >= 100:
            status = 'Completed'
        elif progress > 0:
            status = 'In Progress'
        else:
            status = 'Pending'
        
        task = {
            'id': self.next_id,
            'description': description,
            'priority': priority,
            'category': category,
            'deadline': deadline,
            'status': status,
            'progress': progress,
            'tags': tags or [],
            'notes': notes,
            'subtasks': [],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        self.tasks.append(task)
        self.next_id += 1
        return task['id']
    
    def add_subtask(self, parent_id, description, progress=0):
        task = self.get_task(parent_id)
        if task:
            subtask = {
                'id': len(task['subtasks']) + 1,
                'description': description,
                'progress': progress,
                'completed': progress >= 100
            }
            task['subtasks'].append(subtask)
            
            self._update_task_progress_from_subtasks(task)
            
            task['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            return True
        return False
    
    def _update_task_progress_from_subtasks(self, task):
        subtasks = task.get('subtasks', [])
        
        if not subtasks:
            return
        
        total_progress = sum(st.get('progress', 0) for st in subtasks)
        avg_progress = round(total_progress / len(subtasks))
        
        task['progress'] = avg_progress
        
        if avg_progress >= 100:
            task['status'] = 'Completed'
        elif avg_progress > 0:
            task['status'] = 'In Progress'
        else:
            task['status'] = 'Pending'
    
    def get_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def get_all_tasks(self):
        return self.tasks
    
    def update_task(self, task_id, **kwargs):
        task = self.get_task(task_id)
        if not task:
            return False
        
        has_subtasks = len(task.get('subtasks', [])) > 0
        
        if has_subtasks and 'progress' in kwargs:
            del kwargs['progress']
        
        status_in_kwargs = 'status' in kwargs
        progress_in_kwargs = 'progress' in kwargs
        
        new_status = kwargs.get('status')
        new_progress = kwargs.get('progress')
        
        status_actually_changed = status_in_kwargs and new_status != task['status']
        progress_actually_changed = progress_in_kwargs and new_progress != task['progress']
        
        for key, value in kwargs.items():
            if key in task and key not in ['status', 'progress']:
                task[key] = value
        
        if has_subtasks:
            if status_actually_changed and new_status == 'Completed':
                task['progress'] = 100
                task['status'] = 'Completed'
                for subtask in task['subtasks']:
                    subtask['progress'] = 100
                    subtask['completed'] = True
            else:
                if status_actually_changed:
                    task['status'] = new_status
                self._update_task_progress_from_subtasks(task)
        else:
            if progress_actually_changed:
                task['progress'] = new_progress
                
                if new_progress >= 100:
                    task['status'] = 'Completed'
                elif new_progress > 0:
                    task['status'] = 'In Progress'
                else:
                    task['status'] = 'Pending'
            
            elif status_actually_changed:
                task['status'] = new_status
                
                if new_status == 'Completed':
                    task['progress'] = 100
                elif new_status == 'Pending' and task['progress'] >= 100:
                    task['progress'] = 0
        
        task['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        return True
    
    def update_subtasks(self, task_id):
        task = self.get_task(task_id)
        if task:
            self._update_task_progress_from_subtasks(task)
            task['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    def delete_task(self, task_id):
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False
    
    def get_task_weighted_progress(self, task):
        subtasks = task.get('subtasks', [])
        
        if not subtasks:
            return task.get('progress', 0)
        
        subtask_total = sum(st.get('progress', 0) for st in subtasks)
        return round(subtask_total / len(subtasks))
    
    def get_overall_progress(self):
        if not self.tasks:
            return 0.0
        
        total_progress = 0
        for task in self.tasks:
            task_progress = self.get_task_weighted_progress(task)
            total_progress += task_progress
        
        return round(total_progress / len(self.tasks), 1)
    
    def get_statistics(self):
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t['status'] == 'Completed'])
        pending = len([t for t in self.tasks if t['status'] == 'Pending'])
        
        overdue = 0
        for task in self.tasks:
            if task['status'] != 'Completed' and task.get('deadline'):
                try:
                    deadline = datetime.strptime(task['deadline'], '%Y-%m-%d')
                    if deadline.date() < datetime.now().date():
                        overdue += 1
                except:
                    pass
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'overdue': overdue,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }
    
    def save_to_file(self):
        try:
            data = {'tasks': self.tasks, 'next_id': self.next_id}
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Save error: {e}")
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
            print(f"Load error: {e}")
            return False
