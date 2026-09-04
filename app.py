import os

from flask import Flask, render_template, redirect, url_for, session
from google import genai
from sqlalchemy import inspect

from config import Config
from models import db


def _repair_sqlite_schema(app):

    if not str(
        app.config.get("SQLALCHEMY_DATABASE_URI", "")
    ).startswith("sqlite"):
        return

    try:

        inspector = inspect(db.engine)

        expected = {

            "personality_profiles": {
                "communication_style",
                "emotional_openness",
                "conflict_style",
                "trust_level",
                "social_preference",
                "relationship_expectation",
                "compatibility_score",
                "compatibility_data"
            },

            "chat_analyses": {
                "participants",
                "total_messages",
                "participant_statistics",
                "positive_percentage",
                "neutral_percentage",
                "negative_percentage",
                "communication_score",
                "engagement_score",
                "emotional_score",
                "trust_score",
                "compatibility_score",
                "emotional_tone",
                "ai_summary",
                "ai_analysis_json",
                "chat_text"
            },

            "astrology_readings": {
                "user_id",
                "profile_id",
                "mode",
                "person1_name",
                "person2_name",
                "person1_data",
                "person2_data",
                "combined_data"
            }
        }

        for table, required_columns in expected.items():

            if table in inspector.get_table_names():

                existing_columns = {
                    column["name"]
                    for column in inspector.get_columns(table)
                }

                if not required_columns.issubset(
                    existing_columns
                ):

                    print(
                        f"Repairing legacy SQLite table: {table}"
                    )

                    db.session.execute(
                        db.text(
                            f"DROP TABLE IF EXISTS {table}"
                        )
                    )

                    db.session.commit()

        db.create_all()

    except Exception as exc:

        db.session.rollback()

        print(
            "Schema check warning:",
            type(exc).__name__,
            str(exc)
        )

        db.create_all()


def create_app():

    app = Flask(__name__)

    # -----------------------------------------
    # CONFIGURATION
    # -----------------------------------------

    app.config.from_object(Config)

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    os.makedirs(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            "chat_screenshots"
        ),
        exist_ok=True
    )

    # -----------------------------------------
    # DATABASE
    # -----------------------------------------

    db.init_app(app)

    # SQLite works much better for a Flask development app when WAL mode
    # and a busy timeout are enabled. WAL allows readers while a writer is
    # active, and busy_timeout gives SQLite time to wait for short locks.
    if str(app.config.get("SQLALCHEMY_DATABASE_URI", "")).startswith("sqlite"):
        from sqlalchemy import event

        def _configure_sqlite(connection, _record):
            cursor = connection.cursor()
            try:
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA busy_timeout=30000")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA foreign_keys=ON")
            finally:
                cursor.close()

        # db.engine requires an active Flask application context.
        # Register the listener after entering the app context so startup
        # itself does not fail with "Working outside of application context".
        with app.app_context():
            event.listen(db.engine, "connect", _configure_sqlite)

    # -----------------------------------------
    # GEMINI AI
    # -----------------------------------------

    api_key = (
        app.config.get("GEMINI_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if api_key:

        app.client = genai.Client(
            api_key=api_key
        )

        print("Gemini API key detected.")

        print(
            "Gemini model:",
            app.config.get(
                "GEMINI_MODEL",
                "gemini-3.6-flash"
            )
        )

    else:

        app.client = None

        print(
            "WARNING: GEMINI_API_KEY is not configured."
        )

    # -----------------------------------------
    # IMPORT MODELS
    # -----------------------------------------

    from models.user import User
    from models.personality import PersonalityProfile
    from models.astrology import (
        AstrologyProfile,
        AstrologyReading
    )
    from models.relationship import Relationship
    from models.compatibility import CompatibilityResult
    from models.chat_analysis import ChatAnalysis
    from models.progress import ProgressTracking
    from models.relationship_plan import (
        RelationshipPlan,
        DailyTask
    )
    from models.report import AIReport
    from models.assessment import AssessmentSnapshot
    from models.coach import CoachConversation

    # -----------------------------------------
    # IMPORT BLUEPRINTS
    # -----------------------------------------

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.personality import personality_bp
    from routes.compatibility import compatibility_bp
    from routes.astrology import astrology_bp
    from routes.chat import chat_bp
    from routes.coach import coach_bp
    from routes.report import report_bp
    from routes.progress import progress_bp
    from routes.assessment import assessment_bp

    # -----------------------------------------
    # REGISTER BLUEPRINTS
    # -----------------------------------------

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(personality_bp)
    app.register_blueprint(compatibility_bp)
    app.register_blueprint(astrology_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(coach_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(assessment_bp)

    # -----------------------------------------
    # HOME PAGE
    # -----------------------------------------

    @app.route("/")
    def home():

        # If already logged in,
        # directly open dashboard.
        if session.get("user_id"):

            return redirect(
                url_for("dashboard.index")
            )

        # Otherwise open login page.
        return redirect(
            url_for("auth.login")
        )

    # -----------------------------------------
    # HEALTH CHECK
    # -----------------------------------------

    @app.route("/health")
    def health():

        return {
            "status": "ok",
            "application": "HeartAI",
            "gemini": bool(app.client),
            "model": app.config.get(
                "GEMINI_MODEL",
                "gemini-3.6-flash"
            )
        }

    # -----------------------------------------
    # 404 ERROR
    # -----------------------------------------

    @app.errorhandler(404)
    def not_found(error):

        return render_template(
            "base.html",
            error_title="404 Not Found",
            error_msg=(
                "The page you requested "
                "could not be found."
            )
        ), 404

    # -----------------------------------------
    # 500 ERROR
    # -----------------------------------------

    @app.errorhandler(500)
    def server_error(error):

        return render_template(
            "base.html",
            error_title="500 Internal Error",
            error_msg=(
                "An unexpected server error "
                "occurred. Check the Flask "
                "terminal for the exact error."
            )
        ), 500

    # -----------------------------------------
    # DATABASE CREATE / REPAIR
    # -----------------------------------------

    with app.app_context():

        db.create_all()

        _repair_sqlite_schema(app)

        print(
            "HeartAI database is ready."
        )

    return app


# ---------------------------------------------
# CREATE APPLICATION
# ---------------------------------------------

app = create_app()


# ---------------------------------------------
# RUN SERVER
# ---------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )