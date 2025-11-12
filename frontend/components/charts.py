import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any
import numpy as np

def create_vitals_chart(patient_data: Dict[str, Any]) -> go.Figure:
    """Create a vitals overview chart"""
    fig = go.Figure()
    
    # Add GFR gauge
    fig.add_trace(go.Indicator(
        mode = "gauge+number+delta",
        value = patient_data.get('gfr', 0),
        domain = {'x': [0, 0.5], 'y': [0, 1]},
        title = {'text': "GFR (ml/min/1.73m²)"},
        gauge = {
            'axis': {'range': [None, 120]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgray"},
                {'range': [30, 60], 'color': "yellow"},
                {'range': [60, 90], 'color': "lightgreen"},
                {'range': [90, 120], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 60
            }
        }
    ))
    
    # Add Creatinine gauge
    fig.add_trace(go.Indicator(
        mode = "gauge+number+delta",
        value = patient_data.get('creatinine', 0),
        domain = {'x': [0.5, 1], 'y': [0, 1]},
        title = {'text': "Creatinine (mg/dL)"},
        gauge = {
            'axis': {'range': [None, 5]},
            'bar': {'color': "darkred"},
            'steps': [
                {'range': [0, 1.2], 'color': "green"},
                {'range': [1.2, 2.0], 'color': "yellow"},
                {'range': [2.0, 5], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 1.2
            }
        }
    ))
    
    fig.update_layout(
        title="Patient Vitals Overview",
        height=400,
        showlegend=False
    )
    
    return fig

def create_lab_trends_chart(lab_results: List[Dict[str, Any]]) -> go.Figure:
    """Create lab results trends over time"""
    if not lab_results:
        return go.Figure().add_annotation(
            text="No lab results available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    df = pd.DataFrame(lab_results)
    df['date_taken'] = pd.to_datetime(df['date_taken'], errors='coerce')
    
    # Group by test name and create trend lines
    fig = go.Figure()
    
    for test_name in df['test_name'].unique():
        test_data = df[df['test_name'] == test_name].sort_values('date_taken')
        fig.add_trace(go.Scatter(
            x=test_data['date_taken'],
            y=test_data['result_value'],
            mode='lines+markers',
            name=test_name,
            line=dict(width=3)
        ))
    
    fig.update_layout(
        title="Lab Results Trends",
        xaxis_title="Date",
        yaxis_title="Value",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_medication_adherence_chart(adherence_data: Dict[str, Any]) -> go.Figure:
    """Create medication adherence visualization"""
    if 'medications' not in adherence_data:
        return go.Figure().add_annotation(
            text="No adherence data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    medications = adherence_data['medications']
    names = [med['name'] for med in medications]
    rates = [med['adherence_rate'] * 100 for med in medications]
    
    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=rates,
            marker_color=['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in rates]
        )
    ])
    
    fig.update_layout(
        title=f"Medication Adherence (Overall: {adherence_data.get('overall_adherence', 0)*100:.1f}%)",
        xaxis_title="Medication",
        yaxis_title="Adherence Rate (%)",
        height=400,
        yaxis=dict(range=[0, 100])
    )
    
    return fig

def create_ckd_stage_distribution(patients_data: List[Dict[str, Any]]) -> go.Figure:
    """Create CKD stage distribution pie chart"""
    if not patients_data:
        return go.Figure().add_annotation(
            text="No patient data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    stages = [patient.get('ckd_stage', 0) for patient in patients_data]
    stage_counts = pd.Series(stages).value_counts().sort_index()
    
    fig = go.Figure(data=[go.Pie(
        labels=[f"Stage {stage}" for stage in stage_counts.index],
        values=stage_counts.values,
        hole=0.3
    )])
    
    fig.update_layout(
        title="CKD Stage Distribution",
        height=400
    )
    
    return fig

def create_prediction_confidence_chart(prediction_data: Dict[str, Any]) -> go.Figure:
    """Create prediction confidence visualization"""
    probability = prediction_data.get('probability', 0) * 100
    confidence = prediction_data.get('confidence', 'unknown')
    
    # Color based on confidence level
    color_map = {
        'high': 'green',
        'medium': 'orange', 
        'low': 'red'
    }
    color = color_map.get(confidence, 'gray')
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = probability,
        title = {'text': f"Risk Probability ({confidence.title()} Confidence)"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 60], 'color': "yellow"},
                {'range': [60, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_nutrition_goals_chart(nutrition_data: Dict[str, Any]) -> go.Figure:
    """Create daily nutritional goals chart"""
    if 'daily_nutritional_goals' not in nutrition_data:
        return go.Figure().add_annotation(
            text="No nutritional goals available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    goals = nutrition_data['daily_nutritional_goals']
    nutrients = list(goals.keys())
    values = list(goals.values())
    
    fig = go.Figure(data=[
        go.Bar(
            x=nutrients,
            y=values,
            marker_color='lightblue',
            text=[f"{v:.1f}" for v in values],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Daily Nutritional Goals",
        xaxis_title="Nutrient",
        yaxis_title="Amount",
        height=400
    )
    
    return fig
