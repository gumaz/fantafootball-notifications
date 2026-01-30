import subprocess
import sys
import signal
import os
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
    
    try:
        logger.info("Starting bot and scheduler...")
        
        # Start bot
        bot_process = subprocess.Popen(
            [sys.executable, '-m', 'src.bot.run'],
            start_new_session=True
        )
        processes.append(bot_process)
        
        # Start scheduler
        scheduler_process = subprocess.Popen(
            [sys.executable, '-m', 'src.scheduler.run'],
            start_new_session=True
        )
        processes.append(scheduler_process)
        
        logger.info("Both services running. Press Ctrl+C to stop.")
        
        # Wait for processes
        for p in processes:
            p.wait()
            
    except KeyboardInterrupt:
        logger.info("Stopping services...")
        for p in processes:
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            except Exception:
                try:
                    p.terminate()
                except Exception:
                    pass
        for p in processes:
            try:
                p.wait()
            except Exception:
                pass
        logger.info("Stopped.")

if __name__ == '__main__':
    main()