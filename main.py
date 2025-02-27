import logging
import sys
from pathlib import Path
import streamlit.web.bootstrap
from decouple import config
import signal
from contextlib import contextmanager
from typing import Generator

from moodreads.database.mongodb import MongoDBClient
from moodreads.database.init_db import init_database
from moodreads.analysis.claude import EmotionalAnalyzer
from moodreads.recommender.engine import RecommendationEngine

# Configure logging
logging.basicConfig(
    level=config('LOG_LEVEL', default='INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path('logs/moodreads.log'))
    ]
)
logger = logging.getLogger(__name__)

class MoodreadsApp:
    def __init__(self):
        self.db = None
        self.analyzer = None
        self.engine = None
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Set up graceful shutdown handlers."""
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        """Handle graceful shutdown."""
        logger.info("Shutting down Moodreads...")
        self.cleanup()
        sys.exit(0)

    @contextmanager
    def initialize(self) -> Generator[None, None, None]:
        """Initialize all application components."""
        try:
            logger.info("Initializing Moodreads application...")
            
            # Ensure logs directory exists
            Path('logs').mkdir(exist_ok=True)
            
            # Initialize database
            logger.info("Initializing database...")
            self.db = MongoDBClient()
            init_database()
            
            # Initialize components
            logger.info("Initializing components...")
            self.analyzer = EmotionalAnalyzer()
            self.engine = RecommendationEngine()
            
            # Verify environment variables
            self._verify_environment()
            
            logger.info("Moodreads initialization complete")
            yield
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {str(e)}")
            self.cleanup()
            sys.exit(1)

    def _verify_environment(self):
        """Verify all required environment variables are set."""
        required_vars = [
            'CLAUDE_API_KEY',
            'MONGODB_URI',
            'JWT_SECRET'
        ]
        
        missing_vars = [var for var in required_vars if not config(var, default=None)]
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    def cleanup(self):
        """Cleanup resources before shutdown."""
        logger.info("Cleaning up resources...")
        if self.db:
            try:
                self.db.client.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")

def main():
    """Main entry point for the application."""
    app = MoodreadsApp()
    
    with app.initialize():
        logger.info("Starting Streamlit application...")
        
        # Get the path to the Streamlit app
        app_path = Path(__file__).parent / "src" / "moodreads" / "app.py"
        
        try:
            # Start Streamlit
            streamlit.web.bootstrap.run(
                app_path,
                '',
                [],
                flag_options={
                    'server.port': config('PORT', default=8501, cast=int),
                    'server.address': config('HOST', default='0.0.0.0'),
                    'browser.serverAddress': config('PUBLIC_URL', default='localhost'),
                    'server.maxUploadSize': 5
                }
            )
        except Exception as e:
            logger.error(f"Error running Streamlit application: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main() 