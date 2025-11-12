import streamlit as st
import streamlit.components.v1 as components

def medical_header(title: str, subtitle: str = ""):
    """Custom medical header with gradient background"""
    html = f"""
    <div class="medical-header">
        <div class="header-content">
            <h1 class="header-title">{title}</h1>
            {f'<p class="header-subtitle">{subtitle}</p>' if subtitle else ''}
        </div>
        <div class="header-decoration">
            <div class="pulse-dot"></div>
            <div class="pulse-dot"></div>
            <div class="pulse-dot"></div>
        </div>
    </div>
    
    <style>
    .medical-header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        color: white;
    }}
    
    .header-content {{
        position: relative;
        z-index: 2;
    }}
    
    .header-title {{
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    
    .header-subtitle {{
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }}
    
    .header-decoration {{
        position: absolute;
        top: 1rem;
        right: 2rem;
        display: flex;
        gap: 0.5rem;
    }}
    
    .pulse-dot {{
        width: 12px;
        height: 12px;
        background: rgba(255,255,255,0.8);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }}
    
    .pulse-dot:nth-child(2) {{
        animation-delay: 0.5s;
    }}
    
    .pulse-dot:nth-child(3) {{
        animation-delay: 1s;
    }}
    
    @keyframes pulse {{
        0% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.5; transform: scale(1.2); }}
        100% {{ opacity: 1; transform: scale(1); }}
    }}
    </style>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def health_metric_card(title: str, value: str, unit: str = "", trend: str = "", status: str = "normal"):
    """Custom health metric card with status indicators"""
    status_colors = {
        "normal": "#10b981",
        "warning": "#f59e0b", 
        "critical": "#ef4444",
        "info": "#06b6d4"
    }
    
    status_icons = {
        "normal": "✅",
        "warning": "⚠️",
        "critical": "🚨",
        "info": "ℹ️"
    }
    
    color = status_colors.get(status, status_colors["normal"])
    icon = status_icons.get(status, status_icons["normal"])
    
    html = f"""
    <div class="health-metric-card">
        <div class="metric-header">
            <span class="metric-icon">{icon}</span>
            <h3 class="metric-title">{title}</h3>
        </div>
        <div class="metric-content">
            <div class="metric-value">
                <span class="value">{value}</span>
                <span class="unit">{unit}</span>
            </div>
            {f'<div class="metric-trend">{trend}</div>' if trend else ''}
        </div>
        <div class="metric-status" style="background: {color}"></div>
    </div>
    
    <style>
    .health-metric-card {{
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        position: relative;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        overflow: hidden;
    }}
    
    .health-metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }}
    
    .metric-header {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }}
    
    .metric-icon {{
        font-size: 1.2rem;
    }}
    
    .metric-title {{
        font-size: 0.9rem;
        font-weight: 600;
        color: #6b7280;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .metric-value {{
        display: flex;
        align-items: baseline;
        gap: 0.25rem;
        margin-bottom: 0.5rem;
    }}
    
    .value {{
        font-size: 2.5rem;
        font-weight: 700;
        color: #111827;
        line-height: 1;
    }}
    
    .unit {{
        font-size: 1rem;
        color: #6b7280;
        font-weight: 500;
    }}
    
    .metric-trend {{
        font-size: 0.875rem;
        color: #6b7280;
    }}
    
    .metric-status {{
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
    }}
    </style>
    """
    
    return html

def patient_status_badge(stage: int, gfr: float):
    """Dynamic patient status badge based on CKD stage"""
    if stage <= 2 and gfr >= 60:
        status = "normal"
        message = "Good Kidney Function"
        color = "#10b981"
    elif stage == 3:
        status = "warning"
        message = "Moderate CKD"
        color = "#f59e0b"
    else:
        status = "critical"
        message = "Advanced CKD"
        color = "#ef4444"
    
    html = f"""
    <div class="status-badge" style="border-left-color: {color}">
        <div class="status-icon">
            <div class="status-dot" style="background: {color}"></div>
        </div>
        <div class="status-content">
            <div class="status-title">CKD Stage {stage}</div>
            <div class="status-message">{message}</div>
        </div>
    </div>
    
    <style>
    .status-badge {{
        background: white;
        border: 1px solid #e5e7eb;
        border-left: 4px solid;
        border-radius: 8px;
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1rem 0;
    }}
    
    .status-icon {{
        flex-shrink: 0;
    }}
    
    .status-dot {{
        width: 16px;
        height: 16px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }}
    
    .status-title {{
        font-weight: 600;
        font-size: 1.1rem;
        color: #111827;
        margin: 0;
    }}
    
    .status-message {{
        font-size: 0.9rem;
        color: #6b7280;
        margin: 0;
    }}
    </style>
    """
    
    return html

def interactive_chart_container(title: str, chart_html: str):
    """Container for interactive charts with custom styling"""
    html = f"""
    <div class="chart-container">
        <div class="chart-header">
            <h3 class="chart-title">{title}</h3>
            <div class="chart-controls">
                <button class="chart-btn" onclick="toggleFullscreen(this)">
                    <span>⛶</span>
                </button>
            </div>
        </div>
        <div class="chart-content">
            {chart_html}
        </div>
    </div>
    
    <style>
    .chart-container {{
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        overflow: hidden;
        margin: 1rem 0;
    }}
    
    .chart-header {{
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f9fafb;
    }}
    
    .chart-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: #111827;
        margin: 0;
    }}
    
    .chart-controls {{
        display: flex;
        gap: 0.5rem;
    }}
    
    .chart-btn {{
        background: #f3f4f6;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }}
    
    .chart-btn:hover {{
        background: #e5e7eb;
        transform: scale(1.05);
    }}
    
    .chart-content {{
        padding: 1rem;
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    </style>
    
    <script>
    function toggleFullscreen(btn) {{
        const container = btn.closest('.chart-container');
        container.classList.toggle('fullscreen');
    }}
    </script>
    """
    
    return html

def loading_spinner(message: str = "Loading..."):
    """Custom loading spinner with message"""
    html = f"""
    <div class="loading-container">
        <div class="loading-spinner">
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
        </div>
        <p class="loading-message">{message}</p>
    </div>
    
    <style>
    .loading-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }}
    
    .loading-spinner {{
        position: relative;
        width: 60px;
        height: 60px;
        margin-bottom: 1rem;
    }}
    
    .spinner-ring {{
        position: absolute;
        width: 100%;
        height: 100%;
        border: 3px solid transparent;
        border-top: 3px solid #3b82f6;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }}
    
    .spinner-ring:nth-child(2) {{
        width: 80%;
        height: 80%;
        top: 10%;
        left: 10%;
        border-top-color: #60a5fa;
        animation-duration: 1.5s;
        animation-direction: reverse;
    }}
    
    .spinner-ring:nth-child(3) {{
        width: 60%;
        height: 60%;
        top: 20%;
        left: 20%;
        border-top-color: #93c5fd;
        animation-duration: 2s;
    }}
    
    .loading-message {{
        color: #6b7280;
        font-size: 1rem;
        margin: 0;
        font-weight: 500;
    }}
    
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """
    
    return html

def alert_banner(message: str, type: str = "info", dismissible: bool = True):
    """Custom alert banner with different types"""
    type_config = {
        "success": {"icon": "✅", "color": "#10b981", "bg": "#f0fdf4"},
        "warning": {"icon": "⚠️", "color": "#f59e0b", "bg": "#fffbeb"},
        "error": {"icon": "❌", "color": "#ef4444", "bg": "#fef2f2"},
        "info": {"icon": "ℹ️", "color": "#06b6d4", "bg": "#f0f9ff"}
    }
    
    config = type_config.get(type, type_config["info"])
    
    html = f"""
    <div class="alert-banner alert-{type}" style="background: {config['bg']}; border-left-color: {config['color']}">
        <div class="alert-icon">{config['icon']}</div>
        <div class="alert-content">
            <p class="alert-message">{message}</p>
        </div>
        {f'<button class="alert-dismiss" onclick="this.parentElement.remove()">×</button>' if dismissible else ''}
    </div>
    
    <style>
    .alert-banner {{
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        border-left: 4px solid;
        margin: 1rem 0;
    }}
    
    .alert-icon {{
        font-size: 1.2rem;
        flex-shrink: 0;
        margin-top: 0.1rem;
    }}
    
    .alert-content {{
        flex: 1;
    }}
    
    .alert-message {{
        margin: 0;
        color: #374151;
        font-size: 0.95rem;
        line-height: 1.5;
    }}
    
    .alert-dismiss {{
        background: none;
        border: none;
        font-size: 1.5rem;
        color: #6b7280;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        transition: background 0.2s ease;
    }}
    
    .alert-dismiss:hover {{
        background: rgba(0,0,0,0.1);
    }}
    </style>
    """
    
    return html

def render_html_component(html: str):
    """Render HTML component in Streamlit"""
    st.markdown(html, unsafe_allow_html=True)

def mobile_responsive_grid(items: list, columns: int = 3):
    """Create responsive grid layout for mobile devices"""
    html = f"""
    <div class="responsive-grid" style="grid-template-columns: repeat({columns}, 1fr);">
        {''.join(items)}
    </div>
    
    <style>
    .responsive-grid {{
        display: grid;
        gap: 1rem;
        margin: 1rem 0;
    }}
    
    @media (max-width: 768px) {{
        .responsive-grid {{
            grid-template-columns: 1fr !important;
        }}
    }}
    
    @media (min-width: 769px) and (max-width: 1024px) {{
        .responsive-grid {{
            grid-template-columns: repeat(2, 1fr) !important;
        }}
    }}
    </style>
    """
    
    return html
