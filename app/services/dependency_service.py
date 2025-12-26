from typing import List, Dict, Set, Optional
from datetime import datetime
from app.storage.database import TopicDependencyDB, TopicDB
from app.models.models import Topic


class DependencyService:
    def __init__(self, db):
        self.db = db
    
    def add_dependency(self, prerequisite_topic_id: int, dependent_topic_id: int, 
                      min_skill_threshold: float = 70.0) -> TopicDependencyDB:
        """Add a dependency between two topics."""
        if prerequisite_topic_id == dependent_topic_id:
            raise ValueError("A topic cannot be its own prerequisite")
        
        if self._would_create_cycle(prerequisite_topic_id, dependent_topic_id):
            raise ValueError("This dependency would create a circular dependency")
        
        session = self.db.get_session()
        try:
            existing = session.query(TopicDependencyDB).filter(
                TopicDependencyDB.prerequisite_topic_id == prerequisite_topic_id,
                TopicDependencyDB.dependent_topic_id == dependent_topic_id
            ).first()
            
            if existing:
                raise ValueError("This dependency already exists")
            
            dependency = TopicDependencyDB(
                prerequisite_topic_id=prerequisite_topic_id,
                dependent_topic_id=dependent_topic_id,
                min_skill_threshold=min_skill_threshold
            )
            session.add(dependency)
            session.commit()
            session.refresh(dependency)
            return dependency
        finally:
            session.close()
    
    def get_prerequisites(self, topic_id: int) -> List[Dict]:
        """Get all prerequisites for a topic."""
        session = self.db.get_session()
        try:
            deps = session.query(TopicDependencyDB).filter(
                TopicDependencyDB.dependent_topic_id == topic_id
            ).all()
            
            result = []
            for dep in deps:
                prereq_topic = session.query(TopicDB).filter(
                    TopicDB.id == dep.prerequisite_topic_id
                ).first()
                
                result.append({
                    'dependency_id': dep.id,
                    'prerequisite_id': dep.prerequisite_topic_id,
                    'prerequisite_name': prereq_topic.name,
                    'current_skill': prereq_topic.skill_level,
                    'required_skill': dep.min_skill_threshold,
                    'is_satisfied': prereq_topic.skill_level >= dep.min_skill_threshold
                })
            
            return result
        finally:
            session.close()
    
    def get_dependents(self, topic_id: int) -> List[Dict]:
        """Get all topics that depend on this topic."""
        session = self.db.get_session()
        try:
            deps = session.query(TopicDependencyDB).filter(
                TopicDependencyDB.prerequisite_topic_id == topic_id
            ).all()
            
            result = []
            for dep in deps:
                dependent_topic = session.query(TopicDB).filter(
                    TopicDB.id == dep.dependent_topic_id
                ).first()
                
                result.append({
                    'dependency_id': dep.id,
                    'dependent_id': dep.dependent_topic_id,
                    'dependent_name': dependent_topic.name,
                    'required_skill': dep.min_skill_threshold
                })
            
            return result
        finally:
            session.close()
    
    def check_dependencies_satisfied(self, topic_id: int) -> Dict:
        """Check if all dependencies for a topic are satisfied."""
        prerequisites = self.get_prerequisites(topic_id)
        
        if not prerequisites:
            return {
                'all_satisfied': True,
                'blocking_prerequisites': [],
                'total_prerequisites': 0
            }
        
        blocking = [p for p in prerequisites if not p['is_satisfied']]
        
        return {
            'all_satisfied': len(blocking) == 0,
            'blocking_prerequisites': blocking,
            'total_prerequisites': len(prerequisites)
        }
    
    def _would_create_cycle(self, prerequisite_id: int, dependent_id: int) -> bool:
        """Check if adding this dependency would create a cycle."""
        visited = set()
        
        def has_path(start: int, end: int) -> bool:
            if start == end:
                return True
            
            if start in visited:
                return False
            
            visited.add(start)
            
            session = self.db.get_session()
            try:
                deps = session.query(TopicDependencyDB).filter(
                    TopicDependencyDB.prerequisite_topic_id == start
                ).all()
                
                for dep in deps:
                    if has_path(dep.dependent_topic_id, end):
                        return True
                
                return False
            finally:
                session.close()
        
        return has_path(dependent_id, prerequisite_id)
    
    def get_dependency_graph(self) -> Dict:
        """Get the full dependency graph."""
        session = self.db.get_session()
        try:
            all_deps = session.query(TopicDependencyDB).all()
            all_topics = session.query(TopicDB).all()
            
            nodes = []
            for topic in all_topics:
                nodes.append({
                    'id': topic.id,
                    'name': topic.name,
                    'skill_level': topic.skill_level
                })
            
            edges = []
            for dep in all_deps:
                edges.append({
                    'from': dep.prerequisite_topic_id,
                    'to': dep.dependent_topic_id,
                    'threshold': dep.min_skill_threshold
                })
            
            return {
                'nodes': nodes,
                'edges': edges
            }
        finally:
            session.close()
    
    def get_learning_path(self, target_topic_id: int) -> List[int]:
        """Get the recommended learning path to reach a target topic."""
        visited = set()
        path = []
        
        def dfs(topic_id: int):
            if topic_id in visited:
                return
            
            visited.add(topic_id)
            
            prerequisites = self.get_prerequisites(topic_id)
            for prereq in prerequisites:
                dfs(prereq['prerequisite_id'])
            
            path.append(topic_id)
        
        dfs(target_topic_id)
        return path
    
    def remove_dependency(self, dependency_id: int):
        """Remove a dependency."""
        session = self.db.get_session()
        try:
            dep = session.query(TopicDependencyDB).filter(
                TopicDependencyDB.id == dependency_id
            ).first()
            
            if dep:
                session.delete(dep)
                session.commit()
        finally:
            session.close()
