#!/usr/bin/env python3
"""
Dashboard Generator - Creates an HTML dashboard showing migration status.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state_manager import StateManager, PHASE_WEIGHTS
from core.deliverables import DeliverableChecker
from core.congruence import CongruenceValidator
from core.logger import FrameworkLogger


def generate_dashboard(base_path: str = ".") -> str:
    """Generate HTML dashboard content."""
    state_manager = StateManager(base_path)
    deliverable_checker = DeliverableChecker(base_path)
    validator = CongruenceValidator(base_path)
    logger = FrameworkLogger(base_path)

    # Get project info
    project_id = state_manager.get_active_project_id()
    state = state_manager.get_project_state() if project_id else None

    # Get MCP usage summary
    mcp_summary = logger.get_mcp_usage_summary()
    agent_summary = logger.get_agent_summary()

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Migration Framework Dashboard</title>
    <style>
        :root {{
            --primary: #8B5CF6;
            --primary-dark: #7C3AED;
            --success: #10B981;
            --warning: #F59E0B;
            --error: #EF4444;
            --bg: #1E1E2D;
            --card-bg: #2D2D3F;
            --text: #E5E7EB;
            --text-muted: #9CA3AF;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }}
        h1 {{
            font-size: 1.5rem;
            color: var(--primary);
        }}
        .timestamp {{
            color: var(--text-muted);
            font-size: 0.875rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }}
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
        }}
        .card h2 {{
            font-size: 1rem;
            color: var(--text-muted);
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .progress-bar {{
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin: 1rem 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--primary-dark));
            border-radius: 4px;
            transition: width 0.3s;
        }}
        .big-number {{
            font-size: 3rem;
            font-weight: bold;
            color: var(--primary);
        }}
        .phase-list {{
            list-style: none;
        }}
        .phase-item {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .phase-item:last-child {{
            border-bottom: none;
        }}
        .phase-status {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        .phase-status.completed {{
            background: var(--success);
        }}
        .phase-status.in_progress {{
            background: var(--warning);
            animation: pulse 2s infinite;
        }}
        .phase-status.pending {{
            background: var(--text-muted);
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
        }}
        .metric-label {{
            color: var(--text-muted);
        }}
        .metric-value {{
            font-weight: 600;
        }}
        .tag {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        .tag.success {{
            background: rgba(16, 185, 129, 0.2);
            color: var(--success);
        }}
        .tag.warning {{
            background: rgba(245, 158, 11, 0.2);
            color: var(--warning);
        }}
        .tag.error {{
            background: rgba(239, 68, 68, 0.2);
            color: var(--error);
        }}
        .deliverable-list {{
            list-style: none;
        }}
        .deliverable-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 0;
            font-size: 0.875rem;
        }}
        .check {{
            color: var(--success);
        }}
        .cross {{
            color: var(--error);
        }}
        .mcp-bar {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin: 0.5rem 0;
        }}
        .mcp-name {{
            min-width: 100px;
            font-size: 0.875rem;
        }}
        .mcp-count {{
            flex: 1;
            height: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            position: relative;
            overflow: hidden;
        }}
        .mcp-fill {{
            height: 100%;
            background: var(--primary);
            border-radius: 4px;
        }}
        .mcp-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
        }}
        .no-data {{
            color: var(--text-muted);
            font-style: italic;
            padding: 1rem 0;
        }}
        .full-width {{
            grid-column: 1 / -1;
        }}
        .recent-actions {{
            max-height: 200px;
            overflow-y: auto;
        }}
        .action-item {{
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 0.875rem;
        }}
        .action-time {{
            color: var(--text-muted);
            font-size: 0.75rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Migration Framework Dashboard</h1>
            <span class="timestamp">Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
        </header>

        <div class="grid">
"""

    if not state:
        html += """
            <div class="card full-width">
                <h2>No Active Migration</h2>
                <p class="no-data">No hay ninguna migración activa. Usa <code>/migration start</code> para comenzar.</p>
            </div>
        """
    else:
        # Project Overview Card
        progress = state.get('progress', 0)
        current_phase = state.get('current_phase', 'IDLE')
        project_name = state.get('project_name', 'Unknown')

        html += f"""
            <!-- Project Overview -->
            <div class="card">
                <h2>Project Overview</h2>
                <div style="font-size: 1.25rem; margin-bottom: 0.5rem;">{project_name}</div>
                <div class="tag {'success' if current_phase == 'COMPLETED' else 'warning'}">{current_phase}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress}%"></div>
                </div>
                <div class="metric">
                    <span class="metric-label">Overall Progress</span>
                    <span class="metric-value">{progress}%</span>
                </div>
            </div>

            <!-- Phase Status -->
            <div class="card">
                <h2>Phase Status</h2>
                <ul class="phase-list">
        """

        phases = ['ANALYSIS', 'FEEDBACK', 'DESIGN', 'CONSTRUCTION', 'TESTING']
        phases_status = state.get('phases_status', {})

        for phase in phases:
            status = phases_status.get(phase, 'pending')
            html += f"""
                    <li class="phase-item">
                        <div class="phase-status {status}"></div>
                        <span>{phase}</span>
                        <span class="tag {'success' if status == 'completed' else 'warning' if status == 'in_progress' else ''}" style="margin-left: auto;">
                            {status.upper() if status != 'pending' else ''}
                        </span>
                    </li>
            """

        html += """
                </ul>
            </div>
        """

        # Deliverables Status
        all_complete, missing_required, missing_optional = deliverable_checker.check_phase_deliverables(current_phase)

        html += f"""
            <!-- Deliverables -->
            <div class="card">
                <h2>Current Phase Deliverables</h2>
                <div class="metric">
                    <span class="metric-label">Status</span>
                    <span class="tag {'success' if all_complete else 'error'}">
                        {'Complete' if all_complete else f'{len(missing_required)} Missing'}
                    </span>
                </div>
        """

        if missing_required:
            html += """<ul class="deliverable-list">"""
            for item in missing_required[:5]:
                html += f"""
                <li class="deliverable-item">
                    <span class="cross">✗</span>
                    <span>{item.split('/')[-1]}</span>
                </li>
                """
            html += """</ul>"""
        else:
            html += """<p style="color: var(--success); margin-top: 1rem;">✓ All deliverables complete</p>"""

        html += """</div>"""

        # MCP Usage
        html += """
            <!-- MCP Usage -->
            <div class="card">
                <h2>MCP Usage</h2>
        """

        if mcp_summary.get('by_mcp'):
            max_count = max(mcp_summary['by_mcp'].values()) if mcp_summary['by_mcp'] else 1
            for mcp, count in mcp_summary['by_mcp'].items():
                width = (count / max_count) * 100
                html += f"""
                <div class="mcp-bar">
                    <span class="mcp-name">{mcp}</span>
                    <div class="mcp-count">
                        <div class="mcp-fill" style="width: {width}%"></div>
                    </div>
                    <span class="mcp-label">{count}</span>
                </div>
                """
        else:
            html += """<p class="no-data">No MCP usage recorded yet</p>"""

        html += """</div>"""

        # Agent Invocations
        html += f"""
            <!-- Agent Summary -->
            <div class="card">
                <h2>Agent Invocations</h2>
                <div class="big-number">{agent_summary.get('total_invocations', 0)}</div>
                <div class="metric">
                    <span class="metric-label">Completed</span>
                    <span class="metric-value" style="color: var(--success);">
                        {agent_summary.get('by_status', {}).get('completed', 0)}
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">Failed</span>
                    <span class="metric-value" style="color: var(--error);">
                        {agent_summary.get('by_status', {}).get('failed', 0)}
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">Deliverables Created</span>
                    <span class="metric-value">{agent_summary.get('total_deliverables', 0)}</span>
                </div>
            </div>
        """

        # Congruence Status
        blocking_issues = validator.get_blocking_issues()
        has_issues = len(blocking_issues) > 0 and "Validation not run" not in blocking_issues[0]

        html += f"""
            <!-- Congruence -->
            <div class="card">
                <h2>Congruence Validation</h2>
                <div class="tag {'error' if has_issues else 'success'}" style="font-size: 1rem; padding: 0.5rem 1rem;">
                    {len(blocking_issues) if has_issues else '0'} Issues
                </div>
        """

        if has_issues:
            html += """<ul class="deliverable-list" style="margin-top: 1rem;">"""
            for issue in blocking_issues[:3]:
                html += f"""
                <li class="deliverable-item">
                    <span class="cross">✗</span>
                    <span style="font-size: 0.8rem;">{issue[:50]}...</span>
                </li>
                """
            html += """</ul>"""

        html += """</div>"""

        # Recent Actions
        last_action = state.get('last_action', 'N/A')
        next_action = state.get('next_action', 'N/A')
        last_checkpoint = state.get('last_checkpoint', 'N/A')

        html += f"""
            <!-- Recent Activity -->
            <div class="card full-width">
                <h2>Activity</h2>
                <div class="grid" style="grid-template-columns: repeat(3, 1fr);">
                    <div>
                        <div class="metric-label">Last Action</div>
                        <div style="margin-top: 0.5rem;">{last_action}</div>
                    </div>
                    <div>
                        <div class="metric-label">Next Action</div>
                        <div style="margin-top: 0.5rem;">{next_action}</div>
                    </div>
                    <div>
                        <div class="metric-label">Last Checkpoint</div>
                        <div style="margin-top: 0.5rem;">{last_checkpoint[:19] if last_checkpoint != 'N/A' else 'N/A'}</div>
                    </div>
                </div>
            </div>
        """

    html += """
        </div>
    </div>
</body>
</html>
"""

    return html


def main():
    """Generate and save dashboard."""
    base_path = os.getcwd()
    dashboard_path = Path(base_path) / "docs" / "state" / "dashboard.html"
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)

    html = generate_dashboard(base_path)

    with open(dashboard_path, 'w') as f:
        f.write(html)

    print(json.dumps({
        "result": "success",
        "message": f"Dashboard generated at {dashboard_path}",
        "path": str(dashboard_path)
    }))


if __name__ == "__main__":
    main()
