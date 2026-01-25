import subprocess
import sys
import signal

def main():
    """Run bot and scheduler as separate processes in background. Only for local development."""
    processes = []
    
    try:
        print("🚀 Starting bot and scheduler...")
        
        # Start bot
        bot_process = subprocess.Popen(
            [sys.executable, '-m', 'src.run_bot'],
            start_new_session=True
        )
        processes.append(bot_process)
        
        # Start scheduler
        scheduler_process = subprocess.Popen(
            [sys.executable, '-m', 'src.run_scheduler'],
            start_new_session=True
        )
        processes.append(scheduler_process)
        
        print("✅ Both services running. Press Ctrl+C to stop.")
        
        # Wait for processes
        for p in processes:
            p.wait()
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()
        print("✅ Stopped.")

if __name__ == '__main__':
    main()