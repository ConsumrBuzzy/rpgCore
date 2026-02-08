"""
Commander Dashboard - Rich CLI Interface for Real-Time Fleet Monitoring
ADR 160: Unified View Layer - Rich CLI Component
"""

import time
import threading
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from contextlib import contextmanager

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.align import Align

from loguru import logger


@dataclass
class ViewState:
    """Unified view state for dashboard rendering"""
    timestamp: float
    fleet_status: List[Dict[str, Any]]
    simulation_stats: Dict[str, Any]
    tactical_overview: Dict[str, Any]
    system_health: Dict[str, Any]


class CommanderDashboard:
    """Rich CLI interface for real-time fleet monitoring with thread-safe updates"""
    
    def __init__(self, refresh_rate: float = 1.0):
        self.console = Console()
        self.refresh_rate = refresh_rate
        self.current_view_state: Optional[ViewState] = None
        self._live_display: Optional[Live] = None
        self._update_lock = threading.Lock()
        self._running = False
        self._update_thread: Optional[threading.Thread] = None
        
        logger.debug("📊 CommanderDashboard initialized")
    
    def start_dashboard(self):
        """Start the live dashboard display"""
        if self._running:
            logger.warning("📊 Dashboard already running")
            return
        
        self._running = True
        self._update_thread = threading.Thread(target=self._dashboard_loop, daemon=True)
        self._update_thread.start()
        
        logger.info("📊 CommanderDashboard started")
    
    def stop_dashboard(self):
        """Stop the live dashboard display"""
        if not self._running:
            return
        
        self._running = False
        
        if self._live_display:
            self._live_display.stop()
            self._live_display = None
        
        if self._update_thread:
            self._update_thread.join(timeout=2.0)
        
        logger.info("📊 CommanderDashboard stopped")
    
    def update_view_state(self, view_state: ViewState):
        """Thread-safe view state update"""
        with self._update_lock:
            self.current_view_state = view_state
    
    def _dashboard_loop(self):
        """Main dashboard update loop"""
        while self._running:
            try:
                with self._update_lock:
                    if self.current_view_state:
                        layout = self._create_dashboard_layout(self.current_view_state)
                        
                        if not self._live_display:
                            self._live_display = Live(layout, console=self.console, refresh_per_second=self.refresh_rate)
                        else:
                            self._live_display.update(layout)
                
                time.sleep(self.refresh_rate)
                
            except Exception as e:
                logger.error(f"📊 Dashboard update failed: {e}")
                time.sleep(self.refresh_rate * 2)  # Back off on error
    
    def _create_dashboard_layout(self, view_state: ViewState) -> Layout:
        """Create the main dashboard layout"""
        layout = Layout()
        
        # Define layout structure
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="fleet", ratio=2),
            Layout(name="tactical", ratio=1)
        )
        
        # Populate sections
        layout["header"].update(self._create_header_panel(view_state))
        layout["fleet"].update(self._create_fleet_table(view_state.fleet_status))
        layout["tactical"].update(self._create_tactical_panel(view_state.tactical_overview))
        layout["footer"].update(self._create_system_panel(view_state.system_health))
        
        return layout
    
    def _create_header_panel(self, view_state: ViewState) -> Panel:
        """Create header panel with title and timestamp"""
        title = Text("DGT COMMANDER DASHBOARD", style="bold cyan")
        subtitle = Text(f"Universal Genetic Kernel - {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(view_state.timestamp))}", style="dim")
        
        header_content = Align.center(title) + "\n" + Align.center(subtitle)
        
        return Panel(
            header_content,
            border_style="cyan",
            padding=(1, 2)
        )
    
    def _create_fleet_table(self, fleet_status: List[Dict[str, Any]]) -> Panel:
        """Create fleet status table"""
        table = Table(title="Fleet Status", border_style="green", show_header=True)
        
        # Define columns
        table.add_column("Ship ID", style="bold white", width=12)
        table.add_column("Position", justify="center", style="cyan", width=12)
        table.add_column("Health", justify="center", width=8)
        table.add_column("Thrust", justify="center", width=8)
        table.add_column("Engine", justify="center", width=10)
        table.add_column("Role", justify="center", width=10)
        
        # Add fleet data
        for ship in fleet_status:
            # Health indicator
            health_pct = ship.get('health_percentage', 0)
            if health_pct > 0.7:
                health_style = "green"
            elif health_pct > 0.3:
                health_style = "yellow"
            else:
                health_style = "red"
            
            health_text = f"[{health_style}]{health_pct:.0%}[/{health_style}]"
            
            # Thrust status
            thrust_active = ship.get('thrust_active', False)
            thrust_text = "[green]ON[/green]" if thrust_active else "[red]OFF[/red]"
            
            # Position
            pos = ship.get('position', (0, 0))
            pos_text = f"({pos[0]:.0f},{pos[1]:.0f})"
            
            table.add_row(
                ship.get('ship_id', 'UNKNOWN'),
                pos_text,
                health_text,
                thrust_text,
                ship.get('engine_type', 'UNKNOWN'),
                ship.get('role', 'UNKNOWN')
            )
        
        return Panel(table, border_style="green", padding=(1, 1))
    
    def _create_tactical_panel(self, tactical_overview: Dict[str, Any]) -> Panel:
        """Create tactical overview panel"""
        # Create tactical stats table
        table = Table(title="Tactical Overview", border_style="yellow", show_header=False)
        table.add_column("Metric", style="bold white")
        table.add_column("Value", justify="right", style="cyan")
        
        # Add tactical data
        tactical_data = [
            ("Total Ships", str(tactical_overview.get('total_ships', 0))),
            ("Active Engagements", str(tactical_overview.get('active_engagements', 0))),
            ("Fleet DPS", f"{tactical_overview.get('fleet_dps', 0):.1f}"),
            ("Avg Accuracy", f"{tactical_overview.get('avg_accuracy', 0):.1%}"),
            ("Command Confidence", f"{tactical_overview.get('command_confidence', 0):.1%}"),
            ("Target Locks", str(tactical_overview.get('target_locks', 0))),
        ]
        
        for metric, value in tactical_data:
            table.add_row(metric, value)
        
        return Panel(table, border_style="yellow", padding=(1, 1))
    
    def _create_system_panel(self, system_health: Dict[str, Any]) -> Panel:
        """Create system health panel"""
        # Create system stats table
        table = Table(title="System Health", border_style="blue", show_header=False)
        table.add_column("Component", style="bold white")
        table.add_column("Status", justify="right")
        table.add_column("Load", justify="right", style="cyan")
        
        # Add system data
        system_data = [
            ("Physics Engine", system_health.get('physics_status', 'UNKNOWN'), f"{system_health.get('physics_load', 0):.1%}"),
            ("Evolution System", system_health.get('evolution_status', 'UNKNOWN'), f"{system_health.get('evolution_load', 0):.1%}"),
            ("Batch Processor", system_health.get('batch_status', 'UNKNOWN'), f"{system_health.get('batch_load', 0):.1%}"),
            ("Memory Usage", f"{system_health.get('memory_mb', 0):.1f} MB", f"{system_health.get('memory_load', 0):.1%}"),
            ("FPS", f"{system_health.get('fps', 0):.1f}", f"{system_health.get('frame_time_ms', 0):.1f}ms"),
        ]
        
        for component, status, load in system_data:
            # Color code status
            if status.upper() == "HEALTHY":
                status_style = "green"
            elif status.upper() == "WARNING":
                status_style = "yellow"
            else:
                status_style = "red"
            
            table.add_row(component, f"[{status_style}]{status}[/{status_style}]", load)
        
        return Panel(table, border_style="blue", padding=(1, 1))
    
    @contextmanager
    def temporary_display(self):
        """Context manager for temporary dashboard display"""
        original_running = self._running
        try:
            self.start_dashboard()
            yield self
        finally:
            self.stop_dashboard()
            if original_running:
                self.start_dashboard()
    
    def generate_static_report(self, view_state: ViewState) -> str:
        """Generate static text report for logging"""
        layout = self._create_dashboard_layout(view_state)
        return self.console.render(layout)


# Factory function for easy initialization
def create_commander_dashboard(refresh_rate: float = 1.0) -> CommanderDashboard:
    """Create a CommanderDashboard instance"""
    return CommanderDashboard(refresh_rate)


# Global instance
commander_dashboard = create_commander_dashboard()
