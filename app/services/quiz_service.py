from typing import List, Dict, Optional
from datetime import datetime
from app.models.models import Quiz, QuizQuestion, QuizAttempt
from app.storage.database import Database, QuizDB, QuizQuestionDB, QuizAttemptDB


class QuizService:
    def __init__(self, db: Database):
        self.db = db
    
    def create_quiz(self, quiz: Quiz) -> Quiz:
        session = self.db.get_session()
        try:
            db_quiz = QuizDB(
                topic_id=quiz.topic_id,
                title=quiz.title,
                created_at=quiz.created_at
            )
            session.add(db_quiz)
            session.flush()
            
            for question in quiz.questions:
                db_question = QuizQuestionDB(
                    quiz_id=db_quiz.id,
                    question_text=question.question_text,
                    option_a=question.option_a,
                    option_b=question.option_b,
                    option_c=question.option_c,
                    option_d=question.option_d,
                    correct_answer=question.correct_answer
                )
                session.add(db_question)
            
            session.commit()
            session.refresh(db_quiz)
            quiz.id = db_quiz.id
            return quiz
        finally:
            session.close()
    
    def get_quiz(self, quiz_id: int) -> Optional[Quiz]:
        session = self.db.get_session()
        try:
            db_quiz = session.query(QuizDB).filter(QuizDB.id == quiz_id).first()
            if not db_quiz:
                return None
            
            questions = []
            for db_q in db_quiz.questions:
                questions.append(QuizQuestion(
                    id=db_q.id,
                    quiz_id=db_q.quiz_id,
                    question_text=db_q.question_text,
                    option_a=db_q.option_a,
                    option_b=db_q.option_b,
                    option_c=db_q.option_c,
                    option_d=db_q.option_d,
                    correct_answer=db_q.correct_answer
                ))
            
            return Quiz(
                id=db_quiz.id,
                topic_id=db_quiz.topic_id,
                title=db_quiz.title,
                created_at=db_quiz.created_at,
                questions=questions
            )
        finally:
            session.close()
    
    def get_quizzes_by_topic(self, topic_id: int) -> List[Quiz]:
        session = self.db.get_session()
        try:
            db_quizzes = session.query(QuizDB).filter(QuizDB.topic_id == topic_id).all()
            quizzes = []
            for db_quiz in db_quizzes:
                questions = [
                    QuizQuestion(
                        id=db_q.id,
                        quiz_id=db_q.quiz_id,
                        question_text=db_q.question_text,
                        option_a=db_q.option_a,
                        option_b=db_q.option_b,
                        option_c=db_q.option_c,
                        option_d=db_q.option_d,
                        correct_answer=db_q.correct_answer
                    ) for db_q in db_quiz.questions
                ]
                quizzes.append(Quiz(
                    id=db_quiz.id,
                    topic_id=db_quiz.topic_id,
                    title=db_quiz.title,
                    created_at=db_quiz.created_at,
                    questions=questions
                ))
            return quizzes
        finally:
            session.close()
    
    def submit_quiz_attempt(self, quiz_id: int, answers: Dict[int, str]) -> QuizAttempt:
        session = self.db.get_session()
        try:
            db_quiz = session.query(QuizDB).filter(QuizDB.id == quiz_id).first()
            if not db_quiz:
                raise ValueError("Quiz not found")
            
            correct_count = 0
            total_questions = len(db_quiz.questions)
            
            for question in db_quiz.questions:
                user_answer = answers.get(question.id, "")
                if user_answer == question.correct_answer:
                    correct_count += 1
            
            score = (correct_count / total_questions * 100) if total_questions > 0 else 0
            
            db_attempt = QuizAttemptDB(
                quiz_id=quiz_id,
                attempted_at=datetime.now(),
                score=score,
                total_questions=total_questions
            )
            session.add(db_attempt)
            session.commit()
            session.refresh(db_attempt)
            
            return QuizAttempt(
                id=db_attempt.id,
                quiz_id=db_attempt.quiz_id,
                attempted_at=db_attempt.attempted_at,
                score=db_attempt.score,
                total_questions=db_attempt.total_questions
            )
        finally:
            session.close()
    
    def get_quiz_attempts(self, quiz_id: int) -> List[QuizAttempt]:
        session = self.db.get_session()
        try:
            db_attempts = session.query(QuizAttemptDB).filter(
                QuizAttemptDB.quiz_id == quiz_id
            ).order_by(QuizAttemptDB.attempted_at.desc()).all()
            
            return [
                QuizAttempt(
                    id=att.id,
                    quiz_id=att.quiz_id,
                    attempted_at=att.attempted_at,
                    score=att.score,
                    total_questions=att.total_questions
                ) for att in db_attempts
            ]
        finally:
            session.close()
