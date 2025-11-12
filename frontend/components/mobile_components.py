import streamlit as st
import streamlit.components.v1 as components

def mobile_navigation():
    """Mobile-responsive navigation component"""
    html = """
    <div class="mobile-nav">
        <div class="nav-brand">
            <span class="nav-icon">🩺</span>
            <span class="nav-title">CKD Care</span>
        </div>
        <div class="nav-toggle" onclick="toggleMobileNav()">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>
    
    <div class="mobile-nav-menu" id="mobileNavMenu">
        <a href="#" class="nav-item">Dashboard</a>
        <a href="#" class="nav-item">Predictions</a>
        <a href="#" class="nav-item">Medications</a>
        <a href="#" class="nav-item">Lab Results</a>
        <a href="#" class="nav-item">Nutrition</a>
        <a href="#" class="nav-item">Logout</a>
    </div>
    
    <style>
    .mobile-nav {
        display: none;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .nav-icon {
        font-size: 1.5rem;
    }
    
    .nav-title {
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .nav-toggle {
        display: flex;
        flex-direction: column;
        gap: 4px;
        cursor: pointer;
        padding: 0.5rem;
    }
    
    .nav-toggle span {
        width: 25px;
        height: 3px;
        background: white;
        border-radius: 2px;
        transition: all 0.3s ease;
    }
    
    .mobile-nav-menu {
        position: fixed;
        top: 70px;
        left: -100%;
        width: 100%;
        height: calc(100vh - 70px);
        background: white;
        transition: left 0.3s ease;
        z-index: 999;
        padding: 2rem;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }
    
    .mobile-nav-menu.active {
        left: 0;
    }
    
    .nav-item {
        display: block;
        padding: 1rem 0;
        color: #374151;
        text-decoration: none;
        font-weight: 500;
        border-bottom: 1px solid #e5e7eb;
        transition: color 0.2s ease;
    }
    
    .nav-item:hover {
        color: #3b82f6;
    }
    
    .nav-toggle.active span:nth-child(1) {
        transform: rotate(45deg) translate(6px, 6px);
    }
    
    .nav-toggle.active span:nth-child(2) {
        opacity: 0;
    }
    
    .nav-toggle.active span:nth-child(3) {
        transform: rotate(-45deg) translate(6px, -6px);
    }
    
    @media (max-width: 768px) {
        .mobile-nav {
            display: flex;
        }
        
        .main .block-container {
            padding-top: 90px;
        }
    }
    
    @media (min-width: 769px) {
        .mobile-nav {
            display: none !important;
        }
    }
    </style>
    
    <script>
    function toggleMobileNav() {
        const menu = document.getElementById('mobileNavMenu');
        const toggle = document.querySelector('.nav-toggle');
        
        menu.classList.toggle('active');
        toggle.classList.toggle('active');
    }
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        const menu = document.getElementById('mobileNavMenu');
        const toggle = document.querySelector('.nav-toggle');
        
        if (!menu.contains(e.target) && !toggle.contains(e.target)) {
            menu.classList.remove('active');
            toggle.classList.remove('active');
        }
    });
    </script>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def responsive_data_table(data, title="Data Table"):
    """Responsive data table that works on mobile"""
    html = f"""
    <div class="responsive-table-container">
        <h3 class="table-title">{title}</h3>
        <div class="table-wrapper">
            <table class="responsive-table">
                <thead>
                    <tr>
                        {''.join([f'<th>{col}</th>' for col in data.columns])}
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'<tr>{''.join([f'<td>{row[col]}</td>' for col in data.columns])}</tr>' for _, row in data.iterrows()])}
                </tbody>
            </table>
        </div>
    </div>
    
    <style>
    .responsive-table-container {{
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        overflow: hidden;
        margin: 1rem 0;
    }}
    
    .table-title {{
        padding: 1rem 1.5rem;
        margin: 0;
        background: #f9fafb;
        border-bottom: 1px solid #e5e7eb;
        font-size: 1.1rem;
        font-weight: 600;
        color: #111827;
    }}
    
    .table-wrapper {{
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }}
    
    .responsive-table {{
        width: 100%;
        border-collapse: collapse;
        min-width: 600px;
    }}
    
    .responsive-table th,
    .responsive-table td {{
        padding: 1rem;
        text-align: left;
        border-bottom: 1px solid #e5e7eb;
    }}
    
    .responsive-table th {{
        background: #f9fafb;
        font-weight: 600;
        color: #374151;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .responsive-table td {{
        color: #111827;
        font-size: 0.875rem;
    }}
    
    .responsive-table tbody tr:hover {{
        background: #f9fafb;
    }}
    
    @media (max-width: 768px) {{
        .responsive-table {{
            font-size: 0.8rem;
        }}
        
        .responsive-table th,
        .responsive-table td {{
            padding: 0.75rem 0.5rem;
        }}
    }}
    </style>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def mobile_friendly_form(form_html, title="Form"):
    """Mobile-friendly form wrapper"""
    html = f"""
    <div class="mobile-form-container">
        <h3 class="form-title">{title}</h3>
        <div class="form-content">
            {form_html}
        </div>
    </div>
    
    <style>
    .mobile-form-container {{
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
    }}
    
    .form-title {{
        padding: 1rem 1.5rem;
        margin: 0;
        background: #f9fafb;
        border-bottom: 1px solid #e5e7eb;
        font-size: 1.1rem;
        font-weight: 600;
        color: #111827;
        border-radius: 12px 12px 0 0;
    }}
    
    .form-content {{
        padding: 1.5rem;
    }}
    
    @media (max-width: 768px) {{
        .form-content {{
            padding: 1rem;
        }}
        
        .form-title {{
            padding: 0.75rem 1rem;
            font-size: 1rem;
        }}
    }}
    </style>
    """
    
    return html

def touch_friendly_button(text, onclick="", variant="primary", size="medium"):
    """Touch-friendly button for mobile devices"""
    variants = {
        "primary": "background: #3b82f6; color: white;",
        "secondary": "background: #f3f4f6; color: #374151; border: 1px solid #d1d5db;",
        "success": "background: #10b981; color: white;",
        "warning": "background: #f59e0b; color: white;",
        "error": "background: #ef4444; color: white;"
    }
    
    sizes = {
        "small": "padding: 0.5rem 1rem; font-size: 0.875rem;",
        "medium": "padding: 0.75rem 1.5rem; font-size: 1rem;",
        "large": "padding: 1rem 2rem; font-size: 1.125rem;"
    }
    
    style = f"""
    {variants.get(variant, variants['primary'])}
    {sizes.get(size, sizes['medium'])}
    border: none;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    min-height: 44px; /* Touch target size */
    min-width: 44px;
    """
    
    html = f"""
    <button class="touch-button" style="{style}" onclick="{onclick}">
        {text}
    </button>
    
    <style>
    .touch-button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    .touch-button:active {{
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    @media (max-width: 768px) {{
        .touch-button {{
            width: 100%;
            margin: 0.5rem 0;
        }}
    }}
    </style>
    """
    
    return html

def mobile_health_widget(title, value, unit, status="normal", trend=""):
    """Mobile-optimized health widget"""
    status_colors = {
        "normal": "#10b981",
        "warning": "#f59e0b",
        "critical": "#ef4444",
        "info": "#06b6d4"
    }
    
    html = f"""
    <div class="mobile-health-widget">
        <div class="widget-header">
            <h4 class="widget-title">{title}</h4>
            <div class="widget-status" style="background: {status_colors.get(status, '#6b7280')}"></div>
        </div>
        <div class="widget-content">
            <div class="widget-value">
                <span class="value">{value}</span>
                <span class="unit">{unit}</span>
            </div>
            {f'<div class="widget-trend">{trend}</div>' if trend else ''}
        </div>
    </div>
    
    <style>
    .mobile-health-widget {{
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        margin: 0.5rem;
        flex: 1;
        min-width: 150px;
    }}
    
    .widget-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }}
    
    .widget-title {{
        font-size: 0.875rem;
        font-weight: 600;
        color: #6b7280;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .widget-status {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }}
    
    .widget-content {{
        text-align: center;
    }}
    
    .widget-value {{
        display: flex;
        align-items: baseline;
        justify-content: center;
        gap: 0.25rem;
        margin-bottom: 0.25rem;
    }}
    
    .value {{
        font-size: 1.5rem;
        font-weight: 700;
        color: #111827;
    }}
    
    .unit {{
        font-size: 0.75rem;
        color: #6b7280;
    }}
    
    .widget-trend {{
        font-size: 0.75rem;
        color: #6b7280;
    }}
    
    @media (max-width: 768px) {{
        .mobile-health-widget {{
            margin: 0.25rem;
            padding: 0.75rem;
        }}
        
        .value {{
            font-size: 1.25rem;
        }}
    }}
    </style>
    """
    
    return html
