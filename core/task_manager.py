"""
Task Manager Core Module
Handles CRUD operations for user tasks and file persistence
"""

import json
import os
from datetime import datetime

class TaskManager:
    """
    Manages user tasks with CRUD operations and file persistence
    """
    
    def __init__(self, filename='tasks.json'):
        """
        Initialize task manager
        
        Args:
            filename: Name of file to store tasks (default: tasks.json)
        """
        self.filename = filename
        self.tasks = []
        self.next_id = 1
        
        # Try to load existing tasks
        self.load_from_file()
    
    def add_task(self, description, priority='Medium', status='Pending'):
        """
        Add a new task
        
        Args:
            description: Task description text
            priority: Task priority (Low, Medium, High)
            status: Task status (Pending, Completed)
        
        Returns:
            int: ID of the newly created task
        """
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
        """
        Get a specific task by ID
        
        Args:
            task_id: ID of the task to retrieve
        
        Returns:
            dict: Task data or None if not found
        """
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def get_all_tasks(self):
        """
        Get all tasks
        
        Returns:
            list: List of all task dictionaries
        """
        return self.tasks
    
    def update_task(self, task_id, description=None, priority=None, status=None):
        """
        Update an existing task
        
        Args:
            task_id: ID of the task to update
            description: New description (optional)
            priority: New priority (optional)
            status: New status (optional)
        
        Returns:
            bool: True if task was updated, False if not found
        """
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
        """
        Update only the status of a task
        
        Args:
            task_id: ID of the task
            status: New status (Pending, Completed)
        
        Returns:
            bool: True if updated, False if not found
        """
        return self.update_task(task_id, status=status)
    
    def delete_task(self, task_id):
        """
        Delete a task
        
        Args:
            task_id: ID of the task to delete
        
        Returns:
            bool: True if task was deleted, False if not found
        """
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False
    
    def get_tasks_by_status(self, status):
        """
        Get all tasks with a specific status
        
        Args:
            status: Status to filter by (Pending, Completed)
        
        Returns:
            list: List of matching tasks
        """
        return [task for task in self.tasks if task['status'] == status]
    
    def save_to_file(self):
        """
        Save all tasks to JSON file
        
        Returns:
            bool: True if save was successful, False otherwise
        """
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
        """
        Load tasks from JSON file
        
        Returns:
            bool: True if load was successful, False otherwise
        """
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
        """
        Get task statistics
        
        Returns:
            dict: Statistics including total, pending, and completed counts
        """
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t['status'] == 'Completed'])
        pending = len([t for t in self.tasks if t['status'] == 'Pending'])
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }
