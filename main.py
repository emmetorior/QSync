# main.py
import asyncio
import uvicorn
import sys
import logging
from typing import Any
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceRunner:
    def __init__(self):
        self.should_exit = False
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Set up handlers for graceful shutdown"""
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._handle_signal)

    def _handle_signal(self, signum: int, frame: Any):
        """Handle termination signals"""
        logger.info(f"Received signal {signum}. Starting graceful shutdown...")
        self.should_exit = True

    async def run_service(self, name: str, port: int) -> None:
        """Run a uvicorn service with the specified configuration"""
        config = uvicorn.Config(
            f"{name}:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            loop="asyncio"
        )
        server = uvicorn.Server(config)
        server.install_signal_handlers = lambda: None
        await server.serve()

    async def run_all_services(self):
        """Run all services concurrently"""
        try:
            # Create tasks for both services
            services = await asyncio.gather(
                self.run_service("MQueue8004", 8004),
                self.run_service("MPublisher"),
                return_exceptions=True
            )

            # Check for exceptions
            for service in services:
                if isinstance(service, Exception):
                    logger.error(f"Service error: {service}")
                    raise service

        except Exception as e:
            logger.error(f"Error running services: {e}")
            raise
        finally:
            logger.info("Shutting down services...")


async def main():
    """Async main entry point"""
    try:
        # Check if Python version is compatible
        if sys.version_info < (3, 7):
            raise RuntimeError("Python 3.7 or higher is required")

        logger.info("Starting message queue system...")

        # Create and run the service runner
        runner = ServiceRunner()
        await runner.run_all_services()

    except Exception as e:
        logger.error(f"Failed to start services: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")