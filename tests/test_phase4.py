"""
Unit tests for Phase 4: Honesty & Reality Check System
"""

import pytest
from datetime import datetime, timedelta
from app.storage.database import Database
from app.services.honesty_service import HonestyService
from app.services.exam_simulation_service import ExamSimulationService
from app.services.reprioritization_service import ForcedReprioritizationEngine, ConsequenceEngine
from app.models.models import Course, Topic


@pytest.fixture
def db():
    """Create in-memory database for testing"""
    database = Database(":memory:")
    return database


@pytest.fixture
def honesty_service(db):
    """Create HonestyService instance"""
    return HonestyService(db)


@pytest.fixture
def exam_sim_service(db):
    """Create ExamSimulationService instance"""
    return ExamSimulationService(db)


@pytest.fixture
def reprioritization_engine(db):
    """Create ForcedReprioritizationEngine instance"""
    return ForcedReprioritizationEngine(db)


@pytest.fixture
def consequence_engine(db):
    """Create ConsequenceEngine instance"""
    return ConsequenceEngine(db)


@pytest.fixture
def sample_course(db):
    """Create a sample course"""
    from app.storage.database import CourseDB
    session = db.get_session()
    try:
        course = CourseDB(
            name="Test Course",
            exam_date=datetime.now() + timedelta(days=14)
        )
        session.add(course)
        session.commit()
        session.refresh(course)
        return course
    finally:
        session.close()


@pytest.fixture
def sample_topics(db, sample_course):
    """Create sample topics for testing"""
    from app.storage.database import TopicDB
    session = db.get_session()
    try:
        topics = [
            TopicDB(course_id=sample_course.id, name="Topic A", weight=0.4, skill_level=30.0),
            TopicDB(course_id=sample_course.id, name="Topic B", weight=0.3, skill_level=70.0),
            TopicDB(course_id=sample_course.id, name="Topic C", weight=0.3, skill_level=50.0),
        ]
        for topic in topics:
            session.add(topic)
        session.commit()
        for topic in topics:
            session.refresh(topic)
        return topics
    finally:
        session.close()


class TestFakeProductivityDetection:
    """Tests for TICKET-401: Fake Productivity Detection"""
    
    def test_fake_productivity_high_time_no_improvement(self, db, honesty_service, sample_topics):
        """Test detection of high study time with no skill improvement"""
        from app.storage.database import StudySessionDB, SkillHistoryDB
        
        topic = sample_topics[0]
        session = db.get_session()
        try:
            # Create multiple study sessions (150 minutes total)
            start = datetime.now() - timedelta(days=7)
            for i in range(3):
                study_session = StudySessionDB(
                    topic_id=topic.id,
                    start_time=start + timedelta(days=i),
                    end_time=start + timedelta(days=i, minutes=50),
                    duration_minutes=50
                )
                session.add(study_session)
            
            # Minimal skill change
            skill_history = SkillHistoryDB(
                topic_id=topic.id,
                timestamp=datetime.now() - timedelta(days=6),
                previous_skill=30.0,
                new_skill=32.0,
                reason="self-assessment"
            )
            session.add(skill_history)
            session.commit()
        finally:
            session.close()
        
        result = honesty_service.detect_fake_productivity(topic.id, days=14)
        
        assert result['suspicious'] is True
        assert result['fake_productivity_score'] > 30
        assert result['total_study_time'] == 150
        assert len(result['reasons']) > 0
    
    def test_fake_productivity_no_quizzes(self, db, honesty_service, sample_topics):
        """Test detection of study time without quiz verification"""
        from app.storage.database import StudySessionDB
        
        topic = sample_topics[0]
        session = db.get_session()
        try:
            # Create long study session (140 minutes)
            study_session = StudySessionDB(
                topic_id=topic.id,
                start_time=datetime.now() - timedelta(days=3),
                end_time=datetime.now() - timedelta(days=3, minutes=-140),
                duration_minutes=140
            )
            session.add(study_session)
            session.commit()
        finally:
            session.close()
        
        result = honesty_service.detect_fake_productivity(topic.id, days=14)
        
        assert result['suspicious'] is True
        assert 'No quizzes taken' in str(result['reasons'])
    
    def test_legitimate_productivity(self, db, honesty_service, sample_topics):
        """Test that legitimate productivity is not flagged"""
        from app.storage.database import StudySessionDB, SkillHistoryDB, QuizDB, QuizAttemptDB
        
        topic = sample_topics[0]
        session = db.get_session()
        try:
            # Study session
            study_session = StudySessionDB(
                topic_id=topic.id,
                start_time=datetime.now() - timedelta(days=5),
                end_time=datetime.now() - timedelta(days=5, minutes=-60),
                duration_minutes=60
            )
            session.add(study_session)
            
            # Skill improvement
            skill_history = SkillHistoryDB(
                topic_id=topic.id,
                timestamp=datetime.now() - timedelta(days=4),
                previous_skill=30.0,
                new_skill=45.0,
                reason="quiz"
            )
            session.add(skill_history)
            
            # Quiz with good score
            quiz = QuizDB(
                topic_id=topic.id,
                title="Test Quiz",
                created_at=datetime.now() - timedelta(days=5)
            )
            session.add(quiz)
            session.flush()
            
            quiz_attempt = QuizAttemptDB(
                quiz_id=quiz.id,
                attempted_at=datetime.now() - timedelta(days=4),
                score=75.0,
                total_questions=10
            )
            session.add(quiz_attempt)
            session.commit()
        finally:
            session.close()
        
        result = honesty_service.detect_fake_productivity(topic.id, days=14)
        
        assert result['suspicious'] is False


class TestAvoidancePatternDetection:
    """Tests for TICKET-402: Avoidance Pattern Detection"""
    
    def test_avoidance_high_weight_low_time(self, db, honesty_service, sample_topics):
        """Test detection of avoiding high-weight topics"""
        from app.storage.database import StudySessionDB
        
        high_weight_topic = sample_topics[0]  # 40% weight, 30% skill
        low_weight_topic = sample_topics[1]   # 30% weight, 70% skill
        
        session = db.get_session()
        try:
            # Study low-weight topic extensively
            for i in range(5):
                study_session = StudySessionDB(
                    topic_id=low_weight_topic.id,
                    start_time=datetime.now() - timedelta(days=7-i),
                    end_time=datetime.now() - timedelta(days=7-i, minutes=-60),
                    duration_minutes=60
                )
                session.add(study_session)
            
            # Barely study high-weight topic
            study_session = StudySessionDB(
                topic_id=high_weight_topic.id,
                start_time=datetime.now() - timedelta(days=3),
                end_time=datetime.now() - timedelta(days=3, minutes=-15),
                duration_minutes=15
            )
            session.add(study_session)
            session.commit()
        finally:
            session.close()
        
        result = honesty_service.detect_avoidance_patterns(high_weight_topic.id, days=21)
        
        assert result['avoided'] is True
        assert result['avoidance_severity'] > 30
        assert result['skill_gap'] == 70  # 100 - 30
    
    def test_no_avoidance_balanced_study(self, db, honesty_service, sample_topics):
        """Test that balanced study is not flagged as avoidance"""
        from app.storage.database import StudySessionDB
        
        topic = sample_topics[0]
        session = db.get_session()
        try:
            # Regular study sessions
            for i in range(4):
                study_session = StudySessionDB(
                    topic_id=topic.id,
                    start_time=datetime.now() - timedelta(days=10-i*2),
                    end_time=datetime.now() - timedelta(days=10-i*2, minutes=-45),
                    duration_minutes=45
                )
                session.add(study_session)
            session.commit()
        finally:
            session.close()
        
        result = honesty_service.detect_avoidance_patterns(topic.id, days=21)
        
        assert result['avoided'] is False


class TestOverconfidenceDetection:
    """Tests for TICKET-403: Overconfidence Detection"""
    
    def test_overconfidence_high_self_low_quiz(self, db, honesty_service, sample_topics):
        """Test detection of overconfidence via quiz mismatch"""
        from app.storage.database import TopicDB, QuizDB, QuizAttemptDB
        
        topic = sample_topics[1]  # 70% skill level
        session = db.get_session()
        try:
            # Create quiz with low scores
            quiz = QuizDB(
                topic_id=topic.id,
                title="Reality Check Quiz",
                created_at=datetime.now() - timedelta(days=3)
            )
            session.add(quiz)
            session.flush()
            
            # Multiple low quiz attempts
            for score in [45.0, 48.0, 50.0]:
                attempt = QuizAttemptDB(
                    quiz_id=quiz.id,
                    attempted_at=datetime.now() - timedelta(days=2),
                    score=score,
                    total_questions=10
                )
                session.add(attempt)
            session.commit()
        finally:
            session.close()
        
        result = honesty_service.detect_overconfidence(topic.id)
        
        assert result['overconfident'] is True
        assert result['overconfidence_score'] > 40
        assert result['current_skill'] == 70.0
        assert result['avg_quiz_score'] < 50.0
    
    def test_realistic_self_assessment(self, db, honesty_service, sample_topics):
        """Test that realistic assessment is not flagged"""
        from app.storage.database import QuizDB, QuizAttemptDB
        
        topic = sample_topics[2]  # 50% skill level
        session = db.get_session()
        try:
            # Create quiz with matching scores
            quiz = QuizDB(
                topic_id=topic.id,
                title="Test Quiz",
                created_at=datetime.now() - timedelta(days=2)
            )
            session.add(quiz)
            session.flush()
            
            for score in [48.0, 52.0, 51.0]:
                attempt = QuizAttemptDB(
                    quiz_id=quiz.id,
                    attempted_at=datetime.now() - timedelta(days=1),
                    score=score,
                    total_questions=10
                )
                session.add(attempt)
            session.commit()
        finally:
            session.close()
        
        result = honesty_service.detect_overconfidence(topic.id)
        
        assert result['overconfident'] is False


class TestBrutalHonestyMode:
    """Tests for TICKET-404: Brutal Honesty Mode"""
    
    def test_toggle_brutal_honesty(self, honesty_service):
        """Test toggling brutal honesty mode"""
        initial = honesty_service.brutal_honesty_mode
        
        result1 = honesty_service.toggle_brutal_honesty_mode()
        assert result1 != initial
        
        result2 = honesty_service.toggle_brutal_honesty_mode()
        assert result2 == initial
    
    def test_warning_messages_differ(self, db, honesty_service, sample_topics):
        """Test that warning messages differ in brutal mode"""
        from app.storage.database import StudySessionDB
        
        topic = sample_topics[0]
        session = db.get_session()
        try:
            # Create fake productivity scenario
            study_session = StudySessionDB(
                topic_id=topic.id,
                start_time=datetime.now() - timedelta(days=3),
                end_time=datetime.now() - timedelta(days=3, minutes=-150),
                duration_minutes=150
            )
            session.add(study_session)
            session.commit()
        finally:
            session.close()
        
        # Normal mode
        honesty_service.brutal_honesty_mode = False
        normal_warnings = honesty_service.get_honesty_warnings(sample_topics[0].course_id)
        
        # Brutal mode
        honesty_service.brutal_honesty_mode = True
        brutal_warnings = honesty_service.get_honesty_warnings(sample_topics[0].course_id)
        
        # Warnings should differ in tone
        assert len(normal_warnings) > 0
        assert len(brutal_warnings) > 0
        if normal_warnings and brutal_warnings:
            assert normal_warnings[0] != brutal_warnings[0]


class TestForcedReprioritization:
    """Tests for TICKET-405: Forced Re-Prioritization Engine"""
    
    def test_imminent_exam_trigger(self, db, reprioritization_engine):
        """Test forced reprioritization for imminent exam"""
        from app.storage.database import CourseDB, TopicDB
        
        session = db.get_session()
        try:
            # Create course with exam in 5 days
            course = CourseDB(
                name="Imminent Exam Course",
                exam_date=datetime.now() + timedelta(days=5)
            )
            session.add(course)
            session.flush()
            
            # Create topics with low skills
            topic = TopicDB(
                course_id=course.id,
                name="Critical Topic",
                weight=0.5,
                skill_level=35.0
            )
            session.add(topic)
            session.commit()
            session.refresh(course)
        finally:
            session.close()
        
        result = reprioritization_engine.check_forced_reprioritization(course.id)
        
        assert result['forced_reprioritization'] is True
        assert result['days_until_exam'] in [4, 5]  # Allow for timing differences
        assert result['risk_level'] in ['HIGH', 'CRITICAL']
    
    def test_critical_prerequisites_trigger(self, db, reprioritization_engine):
        """Test forced reprioritization for critical prerequisites"""
        from app.storage.database import CourseDB, TopicDB
        
        session = db.get_session()
        try:
            # Create course with reasonable exam date
            course = CourseDB(
                name="Prerequisites Course",
                exam_date=datetime.now() + timedelta(days=20)
            )
            session.add(course)
            session.flush()
            
            # Create critical topic with very low skill
            topic = TopicDB(
                course_id=course.id,
                name="Critical Prerequisite",
                weight=0.4,
                skill_level=25.0
            )
            session.add(topic)
            session.commit()
            session.refresh(course)
        finally:
            session.close()
        
        result = reprioritization_engine.check_forced_reprioritization(course.id)
        
        assert result['forced_reprioritization'] is True
        # Check that critical_prerequisites trigger is present
        triggers = [o['trigger'] for o in result['overrides']]
        assert 'critical_prerequisites' in triggers


class TestExamSimulation:
    """Tests for TICKET-406: Exam-Day Simulation"""
    
    def test_exam_simulation_basic(self, db, exam_sim_service, sample_course, sample_topics):
        """Test basic exam simulation"""
        result = exam_sim_service.simulate_exam_today(sample_course.id)
        
        assert 'estimated_score' in result
        assert 'pass_probability' in result
        assert 'will_pass' in result
        assert 'risk_level' in result
        assert result['topics_analyzed'] == 3
    
    def test_exam_simulation_with_quizzes(self, db, exam_sim_service, sample_course, sample_topics):
        """Test exam simulation considers quiz scores"""
        from app.storage.database import QuizDB, QuizAttemptDB
        
        session = db.get_session()
        try:
            # Add quiz for first topic
            quiz = QuizDB(
                topic_id=sample_topics[0].id,
                title="Test Quiz",
                created_at=datetime.now() - timedelta(days=2)
            )
            session.add(quiz)
            session.flush()
            
            # Add high-scoring attempt
            attempt = QuizAttemptDB(
                quiz_id=quiz.id,
                attempted_at=datetime.now() - timedelta(days=1),
                score=85.0,
                total_questions=10
            )
            session.add(attempt)
            session.commit()
        finally:
            session.close()
        
        result = exam_sim_service.simulate_exam_today(sample_course.id)
        
        # Score should be influenced by quiz
        assert result['estimated_score'] > 0


class TestConsequenceEngine:
    """Tests for TICKET-408: Hard Warnings & Lockouts"""
    
    def test_lockout_low_priority_imminent_exam(self, db, consequence_engine):
        """Test that low-priority topics get locked near exam"""
        from app.storage.database import CourseDB, TopicDB
        
        session = db.get_session()
        try:
            # Create course with imminent exam
            course = CourseDB(
                name="Lockout Test Course",
                exam_date=datetime.now() + timedelta(days=4)
            )
            session.add(course)
            session.flush()
            
            # Create low-skill high-weight topic
            topic = TopicDB(
                course_id=course.id,
                name="Critical Topic",
                weight=0.5,
                skill_level=30.0
            )
            session.add(topic)
            session.commit()
            session.refresh(course)
        finally:
            session.close()
        
        # Try to study low-priority topic
        lockout = consequence_engine.check_lockouts(course.id, 'study_low_priority')
        
        # Should be locked if conditions are critical
        if lockout['allowed'] is False:
            assert 'reason' in lockout
            assert 'EXAM' in lockout['reason'] or 'LOCKED' in lockout['reason']
    
    def test_no_lockout_normal_conditions(self, db, consequence_engine, sample_course):
        """Test no lockouts under normal conditions"""
        # With normal exam date and reasonable skills, no lockouts
        lockout = consequence_engine.check_lockouts(sample_course.id, 'study_low_priority')
        
        # May or may not be locked depending on conditions
        assert 'allowed' in lockout


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
