from django.core.management.base import BaseCommand
import subprocess
import os
import signal
import sys

class Command(BaseCommand):
    help = 'Start Celery worker and beat scheduler'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--concurrency',
            type=int,
            default=4,
            help='Number of worker processes (default: 4)',
        )
        parser.add_argument(
            '--loglevel',
            default='info',
            help='Log level (default: info)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write("Starting Celery worker and beat scheduler...")
        
        # Start Celery worker
        worker_cmd = [
            'celery', '-A', 'JMCDonations', 'worker',
            '--loglevel', options['loglevel'],
            '--concurrency', str(options['concurrency']),
            '--hostname', 'worker1@%h'
        ]
        
        # Start Celery beat
        beat_cmd = [
            'celery', '-A', 'JMCDonations', 'beat',
            '--loglevel', options['loglevel'],
            '--scheduler', 'django_celery_beat.schedulers:DatabaseScheduler'
        ]
        
        self.stdout.write(f"Worker command: {' '.join(worker_cmd)}")
        self.stdout.write(f"Beat command: {' '.join(beat_cmd)}")
        
        try:
            # In production, you'd use systemd or supervisor
            # For development, we can start both
            import multiprocessing
            
            def start_worker():
                subprocess.run(worker_cmd)
            
            def start_beat():
                subprocess.run(beat_cmd)
            
            worker_process = multiprocessing.Process(target=start_worker)
            beat_process = multiprocessing.Process(target=start_beat)
            
            worker_process.start()
            beat_process.start()
            
            self.stdout.write(self.style.SUCCESS(
                "Celery processes started. Press Ctrl+C to stop."
            ))
            
            # Keep running
            worker_process.join()
            beat_process.join()
            
        except KeyboardInterrupt:
            self.stdout.write("\nShutting down Celery...")
            worker_process.terminate()
            beat_process.terminate()
            sys.exit(0)