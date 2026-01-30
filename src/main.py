import subprocess
import sys
import signal
import logging

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
# Enable our package logs at INFO; keep all third-party libs at WARNING by default
logging.getLogger('src').setLevel(logging.INFO)

def main():
    """Run bot and scheduler as separate processes in background. Only for local development."""
    processes = []

    def cleanup(signum, frame):
        logger.info("Stopping services...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()
        logger.info("Stopped.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        logger.info("Starting bot and scheduler...")
        
        # Start bot and scheduler
        processes.append(subprocess.Popen([sys.executable, '-m', 'src.bot.run']))
        processes.append(subprocess.Popen([sys.executable, '-m', 'src.scheduler.run']))
        
        logger.info("Both services running. Press Ctrl+C to stop.")
        
        # Wait for processes
        for p in processes:
            p.wait()
            
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        logger.info("Stopping services...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()
        logger.info("Stopped.")

if __name__ == '__main__':
    main()