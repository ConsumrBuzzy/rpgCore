"""
View Coordinator - Thread-Safe View Management
ADR 164: Parallel View Rendering without Blocking
"""

import threading
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from loguru import logger

from .cli.dashboard import CommanderDashboard, ViewState
from .terminal.inspector import TerminalInspector, InspectorReport


@dataclass
class ViewUpdate:
    """View update packet"""
    timestamp: float
    view_type: str
    data: Dict[str, Any]
    priority: int = 0  # Higher = more important


class ViewCoordinator:
    """Thread-safe coordinator for multiple view components"""
    
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self.dashboard: Optional[CommanderDashboard] = None
        self.inspector: Optional[TerminalInspector] = None
        self._update_queue: list[ViewUpdate] = []
        self._queue_lock = threading.Lock()
        self._running = False
        self._coordinator_thread: Optional[threading.Thread] = None
        self._executor: Optional[ThreadPoolExecutor] = None
        
        logger.debug("👁️ ViewCoordinator initialized")
    
    def initialize_views(self, enable_dashboard: bool = True, enable_inspector: bool = True):
        """Initialize view components"""
        if enable_dashboard:
            self.dashboard = CommanderDashboard(refresh_rate=1.0)
            self.dashboard.start_dashboard()
        
        if enable_inspector:
            self.inspector = TerminalInspector()
        
        logger.info(f"👁️ Views initialized: dashboard={enable_dashboard}, inspector={enable_inspector}")
    
    def start_coordination(self):
        """Start the view coordination loop"""
        if self._running:
            logger.warning("👁️ View coordination already running")
            return
        
        self._running = True
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="view")
        self._coordinator_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        self._coordinator_thread.start()
        
        logger.info("👁️ View coordination started")
    
    def stop_coordination(self):
        """Stop the view coordination loop"""
        if not self._running:
            return
        
        self._running = False
        
        if self.dashboard:
            self.dashboard.stop_dashboard()
        
        if self._executor:
            self._executor.shutdown(wait=True)
        
        if self._coordinator_thread:
            self._coordinator_thread.join(timeout=2.0)
        
        logger.info("👁️ View coordination stopped")
    
    def submit_update(self, view_update: ViewUpdate):
        """Submit a view update for processing"""
        with self._queue_lock:
            self._update_queue.append(view_update)
            # Sort by priority (highest first)
            self._update_queue.sort(key=lambda x: x.priority, reverse=True)
    
    def update_fleet_view(self, fleet_state: list[Dict[str, Any]], 
                         tactical_state: Dict[str, Any],
                         system_health: Dict[str, Any]):
        """Update fleet view with current state"""
        view_state = ViewState(
            timestamp=time.time(),
            fleet_status=fleet_state,
            simulation_stats={},  # Would be populated with actual stats
            tactical_overview=tactical_state,
            system_health=system_health
        )
        
        if self.dashboard:
            self.dashboard.update_view_state(view_state)
        
        # Also submit to queue for processing
        update = ViewUpdate(
            timestamp=time.time(),
            view_type="fleet",
            data={
                "fleet_state": fleet_state,
                "tactical_state": tactical_state,
                "system_health": system_health
            },
            priority=1
        )
        
        self.submit_update(update)
    
    def update_system_view(self, system_state: Dict[str, Any],
                          evolution_state: Dict[str, Any],
                          performance_metrics: Dict[str, Any]):
        """Update system view with current state"""
        if self.inspector:
            # Create inspection report
            report = self.inspector.inspect_system(
                system_state=system_state,
                fleet_state=[],  # Would be populated with actual fleet state
                tactical_state={},  # Would be populated with actual tactical state
                evolution_state=evolution_state,
                performance_metrics=performance_metrics
            )
            
            # Submit to queue for processing
            update = ViewUpdate(
                timestamp=time.time(),
                view_type="system",
                data={
                    "system_state": system_state,
                    "evolution_state": evolution_state,
                    "performance_metrics": performance_metrics,
                    "report": report
                },
                priority=2  # System updates are high priority
            )
            
            self.submit_update(update)
    
    def _coordination_loop(self):
        """Main coordination loop"""
        while self._running:
            try:
                # Process queued updates
                updates_to_process = []
                
                with self._queue_lock:
                    if self._update_queue:
                        updates_to_process = self._update_queue.copy()
                        self._update_queue.clear()
                
                # Process updates in parallel
                if updates_to_process and self._executor:
                    futures = []
                    
                    for update in updates_to_process:
                        future = self._executor.submit(self._process_update, update)
                        futures.append(future)
                    
                    # Wait for completion (with timeout)
                    for future in as_completed(futures, timeout=0.1):
                        try:
                            future.result()
                        except Exception as e:
                            logger.error(f"👁️ View update failed: {e}")
                
                time.sleep(0.016)  # ~60 FPS coordination rate
                
            except Exception as e:
                logger.error(f"👁️ Coordination loop error: {e}")
                time.sleep(0.1)  # Back off on error
    
    def _process_update(self, update: ViewUpdate):
        """Process a single view update"""
        try:
            if update.view_type == "fleet":
                self._process_fleet_update(update.data)
            elif update.view_type == "system":
                self._process_system_update(update.data)
            else:
                logger.warning(f"👁️ Unknown view type: {update.view_type}")
                
        except Exception as e:
            logger.error(f"👁️ Failed to process update: {e}")
    
    def _process_fleet_update(self, data: Dict[str, Any]):
        """Process fleet-specific update"""
        # Dashboard is already updated via direct call
        # Additional processing could go here
        pass
    
    def _process_system_update(self, data: Dict[str, Any]):
        """Process system-specific update"""
        report = data.get("report")
        if report and self.inspector:
            # Save report to file periodically
            if int(time.time()) % 60 == 0:  # Every minute
                filename = f"inspection_report_{int(report.timestamp)}.txt"
                self.inspector.save_report_to_file(report, filename)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        with self._queue_lock:
            queue_size = len(self._update_queue)
            queue_priority = self._update_queue[0].priority if self._update_queue else 0
        
        return {
            "running": self._running,
            "queue_size": queue_size,
            "highest_priority": queue_priority,
            "dashboard_active": self.dashboard is not None and self.dashboard._running,
            "inspector_active": self.inspector is not None
        }


# Factory function for easy initialization
def create_view_coordinator(max_workers: int = 2) -> ViewCoordinator:
    """Create a ViewCoordinator instance"""
    return ViewCoordinator(max_workers)


# Global instance
view_coordinator = create_view_coordinator()
