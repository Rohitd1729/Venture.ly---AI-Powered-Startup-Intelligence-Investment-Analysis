"""
Venture.ly - Comprehensive Visualization Dashboard
Merged version with enhanced UI and complete functionality
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def apply_plotly_theme(fig):
    """Apply consistent Venture.ly theme to Plotly figures"""
    fig.update_layout(
        plot_bgcolor='rgba(30, 41, 59, 0.5)',
        paper_bgcolor='rgba(30, 41, 59, 0.3)',
        font=dict(
            family='Inter, sans-serif',
            size=12,
            color='#f1f5f9'
        ),
        title_font=dict(
            size=18,
            color='#f1f5f9',
            family='Inter, sans-serif'
        ),
        legend=dict(
            bgcolor='rgba(30, 41, 59, 0.8)',
            bordercolor='#334155',
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor='#1e293b',
            font_size=12,
            font_family='Inter, sans-serif'
        ),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Update axes
    fig.update_xaxes(
        gridcolor='#334155',
        zerolinecolor='#334155',
        color='#94a3b8'
    )
    
    fig.update_yaxes(
        gridcolor='#334155',
        zerolinecolor='#334155',
        color='#94a3b8'
    )
    
    return fig


def create_metric_card(label: str, value: str, delta: Optional[str] = None, 
                       icon: str = "📊", color: str = "#6366f1"):
    """Create a styled metric card"""
    delta_html = ""
    if delta:
        delta_html = f"""
        <div style='font-size: 0.875rem; color: #10b981; margin-top: 0.25rem;'>
            ↑ {delta}
        </div>
        """
    
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        text-align: center;
    '>
        <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{icon}</div>
        <div style='
            color: #94a3b8;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        '>{label}</div>
        <div style='
            color: {color};
            font-size: 1.75rem;
            font-weight: 700;
        '>{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def display_data_sources(data: Dict):
    """Display information about data sources with enhanced styling"""
    st.markdown("#### 📡 Data Collection Status")
    
    # Check metadata
    metadata = data.get('metadata', {})
    successful_sources = metadata.get('successful_sources', 0)
    total_sources = metadata.get('total_sources', 0)
    
    # If no metadata, infer from data
    if not successful_sources and not total_sources:
        source_names = ['crunchbase', 'linkedin', 'web_search', 'simple_web']
        successful_count = 0
        
        for source in source_names:
            if source in data and 'error' not in str(data.get(source, '')):
                successful_count += 1
        
        successful_sources = successful_count
        total_sources = len(source_names)
    
    # Progress indicator
    progress = successful_sources / total_sources if total_sources > 0 else 0
    progress_color = "#10b981" if progress >= 0.75 else "#f59e0b" if progress >= 0.5 else "#ef4444"
    
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 1.5rem;
    '>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
            <span style='color: #f1f5f9; font-weight: 600;'>Data Quality Score</span>
            <span style='color: {progress_color}; font-weight: 700; font-size: 1.25rem;'>
                {successful_sources}/{total_sources}
            </span>
        </div>
        <div style='
            background: #0f172a;
            border-radius: 10px;
            height: 12px;
            overflow: hidden;
        '>
            <div style='
                background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
                height: 100%;
                width: {progress * 100}%;
                transition: width 0.3s ease;
            '></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Source breakdown
    col1, col2, col3, col4 = st.columns(4)
    source_configs = [
        ('crunchbase', 'Crunchbase', '💼', col1),
        ('linkedin', 'LinkedIn', '👔', col2),
        ('web_search', 'Web Search', '🔍', col3),
        ('simple_web', 'Company Site', '🌐', col4)
    ]
    
    for source_key, source_name, icon, col in source_configs:
        with col:
            if source_key in data:
                source_data = data[source_key]
                if isinstance(source_data, dict) and 'error' not in source_data:
                    status = "✅"
                    color = "#10b981"
                else:
                    status = "❌"
                    color = "#ef4444"
            else:
                status = "❌"
                color = "#ef4444"
            
            st.markdown(f"""
            <div style='
                background: rgba(30, 41, 59, 0.5);
                padding: 0.75rem;
                border-radius: 8px;
                border: 1px solid #334155;
                text-align: center;
            '>
                <div style='font-size: 1.5rem; margin-bottom: 0.25rem;'>{icon}</div>
                <div style='color: {color}; font-weight: 600; font-size: 0.875rem;'>
                    {status} {source_name}
                </div>
            </div>
            """, unsafe_allow_html=True)


def display_company_overview(data: Dict):
    """Display enhanced company overview section"""
    st.markdown("#### 🏢 Company Overview")
    
    # Company description
    if data.get('description'):
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #334155;
            margin-bottom: 1.5rem;
        '>
            <p style='color: #f1f5f9; line-height: 1.6; margin: 0;'>
                {data['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        funding = data.get('funding_raised', 0)
        if funding >= 1e9:
            funding_str = f"${funding/1e9:.2f}B"
        elif funding >= 1e6:
            funding_str = f"${funding/1e6:.1f}M"
        else:
            funding_str = f"${funding:,.0f}" if funding else "N/A"
        create_metric_card("Total Funding", funding_str, icon="💰", color="#10b981")
    
    with col2:
        employees = data.get('employees', 0)
        emp_str = f"{employees:,}" if employees else "N/A"
        create_metric_card("Team Size", emp_str, icon="👥", color="#6366f1")
    
    with col3:
        valuation = data.get('valuation', 0)
        if valuation >= 1e9:
            val_str = f"${valuation/1e9:.2f}B"
        elif valuation >= 1e6:
            val_str = f"${valuation/1e6:.1f}M"
        else:
            val_str = "N/A"
        create_metric_card("Valuation", val_str, icon="💎", color="#8b5cf6")
    
    with col4:
        stage = data.get('funding_stage', 'Unknown')
        create_metric_card("Stage", stage, icon="🚀", color="#ec4899")
    
    # Additional company info
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        info_items = []
        if data.get('website'):
            info_items.append(f"🌐 **Website:** [{data['website']}]({data['website']})")
        if data.get('location'):
            info_items.append(f"📍 **Location:** {data['location']}")
        if data.get('founded_year'):
            info_items.append(f"📅 **Founded:** {data['founded_year']}")
        
        if info_items:
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #334155;
            '>
            """, unsafe_allow_html=True)
            for item in info_items:
                st.markdown(item)
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        info_items = []
        if data.get('ceo'):
            info_items.append(f"👔 **CEO:** {data['ceo']}")
        if data.get('industry'):
            info_items.append(f"🏭 **Industry:** {data['industry']}")
        if data.get('company_age'):
            info_items.append(f"⏱️ **Age:** {data['company_age']} years")
        
        if info_items:
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #334155;
            '>
            """, unsafe_allow_html=True)
            for item in info_items:
                st.markdown(item)
            st.markdown("</div>", unsafe_allow_html=True)


def display_funding_analysis(data: Dict):
    """Display comprehensive funding analysis"""
    st.markdown("#### 💰 Funding Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Funding gauge
        funding = data.get('funding_raised', 0)
        if funding:
            max_range = max(funding * 2, 100000000)
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = funding,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Total Funding Raised", 'font': {'color': '#f1f5f9', 'size': 16}},
                number = {'prefix': "$", 'font': {'color': '#10b981', 'size': 32}},
                gauge = {
                    'axis': {'range': [None, max_range], 'tickcolor': '#94a3b8'},
                    'bar': {'color': "#10b981"},
                    'bgcolor': "rgba(30, 41, 59, 0.5)",
                    'borderwidth': 2,
                    'bordercolor': "#334155",
                    'steps': [
                        {'range': [0, 1000000], 'color': "rgba(99, 102, 241, 0.2)"},
                        {'range': [1000000, 10000000], 'color': "rgba(139, 92, 246, 0.3)"},
                        {'range': [10000000, 50000000], 'color': "rgba(236, 72, 153, 0.4)"},
                        {'range': [50000000, max_range], 'color': "rgba(16, 185, 129, 0.5)"}
                    ],
                    'threshold': {
                        'line': {'color': "#ec4899", 'width': 4},
                        'thickness': 0.75,
                        'value': 100000000
                    }
                }
            ))
            fig.update_layout(height=350)
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💰 Funding data not available")
    
    with col2:
        # Funding rounds distribution
        funding_rounds = data.get('funding_rounds', [])
        if funding_rounds and len(funding_rounds) > 0:
            round_types = [round_data.get('type', 'Unknown') for round_data in funding_rounds]
            round_counts = pd.Series(round_types).value_counts()
            
            colors = ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b']
            
            fig = go.Figure(data=[go.Pie(
                labels=round_counts.index,
                values=round_counts.values,
                hole=0.4,
                marker=dict(colors=colors, line=dict(color='#334155', width=2))
            )])
            
            fig.update_layout(
                title='Funding Rounds Distribution',
                showlegend=True,
                height=350
            )
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Funding rounds data not available")
    
    # Funding timeline
    if funding_rounds and len(funding_rounds) > 0:
        st.markdown("##### 📈 Funding Timeline")
        
        timeline_data = []
        for round_data in funding_rounds:
            if round_data.get('date') and round_data.get('amount'):
                timeline_data.append({
                    'Date': round_data['date'],
                    'Amount': round_data['amount'],
                    'Round': round_data.get('type', 'Unknown')
                })
        
        if timeline_data:
            df = pd.DataFrame(timeline_data)
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna()
            
            if not df.empty:
                fig = px.scatter(
                    df, x='Date', y='Amount', 
                    color='Round', size='Amount',
                    title="Funding Timeline",
                    hover_data=['Round', 'Amount'],
                    color_discrete_sequence=['#6366f1', '#8b5cf6', '#ec4899', '#10b981']
                )
                fig.update_traces(marker=dict(line=dict(width=2, color='#334155')))
                fig.update_layout(yaxis_title="Funding Amount ($)", height=400)
                fig = apply_plotly_theme(fig)
                st.plotly_chart(fig, use_container_width=True)


def display_financial_dashboard(data: Dict):
    """Display financial metrics dashboard"""
    st.markdown("#### 📊 Financial Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue vs Funding
        revenue = data.get('revenue', 0)
        funding = data.get('funding_raised', 0)
        
        if revenue or funding:
            categories = []
            values = []
            colors = []
            
            if funding:
                categories.append('Funding Raised')
                values.append(funding)
                colors.append('#6366f1')
            
            if revenue:
                categories.append('Revenue')
                values.append(revenue)
                colors.append('#10b981')
            
            fig = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=values,
                    marker=dict(
                        color=colors,
                        line=dict(color='#334155', width=2)
                    ),
                    text=[f"${v/1e6:.1f}M" if v >= 1e6 else f"${v:,.0f}" for v in values],
                    textposition='outside'
                )
            ])
            
            fig.update_layout(
                title="Revenue vs Funding",
                yaxis_title="Amount ($)",
                showlegend=False,
                height=350
            )
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💵 Revenue data not available")
    
    with col2:
        # Market cap vs Valuation
        market_cap = data.get('market_cap', 0)
        valuation = data.get('valuation', 0)
        
        if market_cap or valuation:
            categories = []
            values = []
            colors = []
            
            if market_cap:
                categories.append('Market Cap')
                values.append(market_cap)
                colors.append('#ec4899')
            
            if valuation:
                categories.append('Valuation')
                values.append(valuation)
                colors.append('#8b5cf6')
            
            fig = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=values,
                    marker=dict(
                        color=colors,
                        line=dict(color='#334155', width=2)
                    ),
                    text=[f"${v/1e9:.2f}B" if v >= 1e9 else f"${v/1e6:.1f}M" for v in values],
                    textposition='outside'
                )
            ])
            
            fig.update_layout(
                title="Market Cap vs Valuation",
                yaxis_title="Value ($)",
                showlegend=False,
                height=350
            )
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💎 Valuation data not available")
    
    # Financial metrics table
    st.markdown("##### 📋 Financial Summary")
    
    metrics_data = {
        'Metric': [],
        'Value': []
    }
    
    if data.get('funding_raised'):
        metrics_data['Metric'].append('Total Funding')
        metrics_data['Value'].append(f"${data['funding_raised']:,.0f}")
    
    if data.get('revenue'):
        metrics_data['Metric'].append('Revenue')
        metrics_data['Value'].append(f"${data['revenue']:,.0f}")
    
    if data.get('market_cap'):
        metrics_data['Metric'].append('Market Cap')
        metrics_data['Value'].append(f"${data['market_cap']:,.0f}")
    
    if data.get('valuation'):
        metrics_data['Metric'].append('Valuation')
        metrics_data['Value'].append(f"${data['valuation']:,.0f}")
    
    if data.get('employees'):
        metrics_data['Metric'].append('Employees')
        metrics_data['Value'].append(f"{data['employees']:,}")
    
    if metrics_data['Metric']:
        df = pd.DataFrame(metrics_data)
        st.dataframe(df, width='stretch', hide_index=True)
    else:
        st.info("📊 Detailed financial metrics not available")


def display_team_analysis(data: Dict):
    """Display team and leadership analysis"""
    st.markdown("#### 👥 Team & Leadership")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Leadership team
        st.markdown("##### 🏛️ Leadership")
        
        leadership = data.get('leadership', [])
        founders = data.get('founders', [])
        ceo = data.get('ceo')
        
        if leadership or founders or ceo:
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #334155;
            '>
            """, unsafe_allow_html=True)
            
            if ceo:
                st.markdown(f"**👔 CEO:** {ceo}")
            
            if founders:
                st.markdown("**🚀 Founders:**")
                for founder in founders[:5]:
                    st.markdown(f"• {founder}")
            
            if leadership:
                st.markdown("**👥 Leadership Team:**")
                for leader in leadership[:5]:
                    if isinstance(leader, dict):
                        name = leader.get('name', 'Unknown')
                        title = leader.get('title', '')
                        st.markdown(f"• {name} - {title}" if title else f"• {name}")
                    else:
                        st.markdown(f"• {leader}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("👥 Leadership information not available")
    
    with col2:
        # Team size gauge
        employees = data.get('employees', 0)
        if employees:
            size_category = data.get('employee_size', 'Unknown')
            if size_category == 'Unknown':
                if employees < 10:
                    size_category = 'Startup'
                elif employees < 50:
                    size_category = 'Small'
                elif employees < 200:
                    size_category = 'Medium'
                elif employees < 1000:
                    size_category = 'Large'
                else:
                    size_category = 'Enterprise'
            
            max_range = max(employees * 2, 1000)
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = employees,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"Team Size ({size_category})", 'font': {'color': '#f1f5f9', 'size': 16}},
                number = {'font': {'color': '#6366f1', 'size': 32}},
                gauge = {
                    'axis': {'range': [None, max_range], 'tickcolor': '#94a3b8'},
                    'bar': {'color': "#6366f1"},
                    'bgcolor': "rgba(30, 41, 59, 0.5)",
                    'borderwidth': 2,
                    'bordercolor': "#334155",
                    'steps': [
                        {'range': [0, 10], 'color': "rgba(99, 102, 241, 0.2)"},
                        {'range': [10, 50], 'color': "rgba(139, 92, 246, 0.3)"},
                        {'range': [50, 200], 'color': "rgba(236, 72, 153, 0.4)"},
                        {'range': [200, max_range], 'color': "rgba(16, 185, 129, 0.5)"}
                    ],
                    'threshold': {
                        'line': {'color': "#ec4899", 'width': 4},
                        'thickness': 0.75,
                        'value': 500
                    }
                }
            ))
            fig.update_layout(height=300)
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("👥 Team size data not available")
    
    # Investors section
    investors = data.get('investors', [])
    if investors and len(investors) > 0:
        st.markdown("##### 💼 Key Investors")
        
        cols = st.columns(min(len(investors), 4))
        for i, investor in enumerate(investors[:8]):
            with cols[i % 4]:
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                    padding: 1rem;
                    border-radius: 8px;
                    border: 1px solid #334155;
                    text-align: center;
                    margin-bottom: 0.5rem;
                '>
                    <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>💼</div>
                    <p style='color: #f1f5f9; font-size: 0.875rem; font-weight: 600; margin: 0;'>
                        {investor}
                    </p>
                </div>
                """, unsafe_allow_html=True)


def calculate_investment_score(data: Dict) -> Dict:
    """Calculate investment score based on available data"""
    scores = {}
    
    # Funding score (0-25 points)
    funding = data.get('funding_raised', 0)
    if funding > 100_000_000:
        scores['funding'] = 25
    elif funding > 50_000_000:
        scores['funding'] = 20
    elif funding > 10_000_000:
        scores['funding'] = 15
    elif funding > 1_000_000:
        scores['funding'] = 10
    else:
        scores['funding'] = 5
    
    # Team score (0-25 points)
    team_score = 0
    if data.get('ceo'):
        team_score += 5
    if data.get('founders'):
        team_score += min(len(data.get('founders', [])) * 3, 10)
    if data.get('employees', 0) > 50:
        team_score += 10
    elif data.get('employees', 0) > 10:
        team_score += 5
    scores['team'] = min(team_score, 25)
    
    # Market score (0-25 points)
    market_score = 0
    if data.get('revenue', 0) > 10_000_000:
        market_score += 15
    elif data.get('revenue', 0) > 1_000_000:
        market_score += 10
    elif data.get('revenue', 0) > 0:
        market_score += 5
    
    if data.get('employees', 0) > 100:
        market_score += 10
    elif data.get('employees', 0) > 50:
        market_score += 5
    
    scores['market'] = min(market_score, 25)
    
    # Growth score (0-25 points)
    growth_score = 0
    age = data.get('company_age', 0)
    if age > 0:
        funding_per_year = data.get('funding_raised', 0) / age
        if funding_per_year > 10_000_000:
            growth_score += 25
        elif funding_per_year > 5_000_000:
            growth_score += 20
        elif funding_per_year > 1_000_000:
            growth_score += 15
        else:
            growth_score += 10
    else:
        growth_score = 10
    
    scores['growth'] = min(growth_score, 25)
    
    # Calculate overall score
    overall_score = sum(scores.values())
    
    # Determine recommendation
    if overall_score >= 80:
        recommendation = "STRONG BUY"
        risk_level = "Low"
        color = "#10b981"
    elif overall_score >= 65:
        recommendation = "BUY"
        risk_level = "Medium-Low"
        color = "#6366f1"
    elif overall_score >= 50:
        recommendation = "HOLD"
        risk_level = "Medium"
        color = "#f59e0b"
    elif overall_score >= 35:
        recommendation = "CAUTIOUS"
        risk_level = "Medium-High"
        color = "#ec4899"
    else:
        recommendation = "PASS"
        risk_level = "High"
        color = "#ef4444"
    
    return {
        'overall': overall_score,
        'scores': scores,
        'recommendation': recommendation,
        'risk_level': risk_level,
        'color': color
    }


def display_market_analysis(data: Dict):
    """Display market position and investment analysis"""
    st.markdown("#### 🎯 Market Position & Investment Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Company maturity
        age = data.get('company_age', 0)
        if age:
            if age < 3:
                maturity = "Early Stage"
                color = "#ec4899"
            elif age < 7:
                maturity = "Growth Stage"
                color = "#f59e0b"
            else:
                maturity = "Mature"
                color = "#10b981"
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = age,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"Company Maturity ({maturity})", 'font': {'color': '#f1f5f9', 'size': 16}},
                number = {'suffix': " yrs", 'font': {'color': color, 'size': 32}},
                gauge = {
                    'axis': {'range': [None, 20], 'tickcolor': '#94a3b8'},
                    'bar': {'color': color},
                    'bgcolor': "rgba(30, 41, 59, 0.5)",
                    'borderwidth': 2,
                    'bordercolor': "#334155",
                    'steps': [
                        {'range': [0, 3], 'color': "rgba(236, 72, 153, 0.3)"},
                        {'range': [3, 7], 'color': "rgba(245, 158, 11, 0.4)"},
                        {'range': [7, 15], 'color': "rgba(16, 185, 129, 0.5)"},
                        {'range': [15, 20], 'color': "rgba(99, 102, 241, 0.6)"}
                    ]
                }
            ))
            fig.update_layout(height=300)
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📅 Company age data not available")
    
    with col2:
        # Funding stage
        stage = data.get('funding_stage', 'Unknown')
        
        stage_colors = {
            'Pre-Seed': '#ec4899',
            'Seed': '#f59e0b',
            'Series A': '#6366f1',
            'Series B': '#8b5cf6',
            'Series C': '#10b981',
            'Series C+': '#10b981',
            'Late Stage': '#0ea5e9',
            'IPO': '#22c55e',
            'Unknown': '#94a3b8'
        }
        
        color = stage_colors.get(stage, '#94a3b8')
        
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {color}20 0%, {color}40 100%);
            padding: 3rem 2rem;
            border-radius: 12px;
            border: 2px solid {color};
            text-align: center;
            height: 300px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        '>
            <div style='
                font-size: 0.875rem;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-bottom: 1rem;
            '>Funding Stage</div>
            <div style='
                color: {color};
                font-size: 2rem;
                font-weight: 700;
            '>{stage}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Investment scoring and recommendation
    st.markdown("##### 💡 Investment Recommendation")
    
    score_data = calculate_investment_score(data)
    overall_score = score_data['overall']
    scores = score_data['scores']
    recommendation = score_data['recommendation']
    risk_level = score_data['risk_level']
    rec_color = score_data['color']
    
    # Display overall metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid #334155;
            text-align: center;
        '>
            <div style='
                color: #94a3b8;
                font-size: 0.875rem;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
            '>Overall Score</div>
            <div style='
                color: #6366f1;
                font-size: 3rem;
                font-weight: 700;
            '>{overall_score}</div>
            <div style='color: #94a3b8; font-size: 0.875rem;'>out of 100</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {rec_color}20 0%, {rec_color}40 100%);
            padding: 2rem;
            border-radius: 12px;
            border: 2px solid {rec_color};
            text-align: center;
        '>
            <div style='
                color: #94a3b8;
                font-size: 0.875rem;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
            '>Recommendation</div>
            <div style='
                color: {rec_color};
                font-size: 1.75rem;
                font-weight: 700;
            '>{recommendation}</div>
            <div style='color: #94a3b8; font-size: 0.875rem; margin-top: 0.5rem;'>Investment Signal</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        risk_color = "#10b981" if risk_level in ["Low", "Medium-Low"] else "#f59e0b" if risk_level == "Medium" else "#ef4444"
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid #334155;
            text-align: center;
        '>
            <div style='
                color: #94a3b8;
                font-size: 0.875rem;
                text-transform: uppercase;
                margin-bottom: 0.5rem;
            '>Risk Level</div>
            <div style='
                color: {risk_color};
                font-size: 1.75rem;
                font-weight: 700;
            '>{risk_level}</div>
            <div style='color: #94a3b8; font-size: 0.875rem; margin-top: 0.5rem;'>Investment Risk</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Score breakdown
    st.markdown("##### 📊 Score Breakdown")
    
    score_categories = {
        'Funding': scores['funding'],
        'Team': scores['team'],
        'Market': scores['market'],
        'Growth': scores['growth']
    }
    
    colors_list = ['#6366f1', '#8b5cf6', '#ec4899', '#10b981']
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(score_categories.keys()),
            y=list(score_categories.values()),
            marker=dict(
                color=colors_list,
                line=dict(color='#334155', width=2)
            ),
            text=list(score_categories.values()),
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Investment Score Components (max 25 each)",
        yaxis_title="Score",
        yaxis=dict(range=[0, 30]),
        showlegend=False,
        height=350
    )
    fig = apply_plotly_theme(fig)
    st.plotly_chart(fig, use_container_width=True)
    
    # Competitive landscape
    competitors = data.get('competitors', [])
    if competitors and len(competitors) > 0:
        st.markdown("##### ⚔️ Competitive Landscape")
        
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #334155;
        '>
        """, unsafe_allow_html=True)
        
        cols = st.columns(min(len(competitors), 3))
        for i, comp in enumerate(competitors[:6]):
            with cols[i % 3]:
                st.markdown(f"""
                <div style='
                    background: rgba(236, 72, 153, 0.1);
                    padding: 0.75rem 1rem;
                    border-radius: 8px;
                    border-left: 3px solid #ec4899;
                    margin-bottom: 0.5rem;
                '>
                    <p style='color: #fce7f3; margin: 0; font-weight: 500;'>
                        • {comp}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)


def display_technology_stack(data: Dict):
    """Display technology and product information"""
    st.markdown("#### 💻 Technology & Products")
    
    col1, col2 = st.columns(2)
    
    with col1:
        technologies = data.get('technologies', [])
        if technologies and len(technologies) > 0:
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #334155;
            '>
                <h4 style='color: #6366f1; margin-bottom: 1rem;'>🔧 Tech Stack</h4>
            """, unsafe_allow_html=True)
            
            for tech in technologies[:10]:
                st.markdown(f"""
                <span style='
                    display: inline-block;
                    background: rgba(99, 102, 241, 0.2);
                    color: #a5b4fc;
                    padding: 0.5rem 1rem;
                    border-radius: 6px;
                    font-size: 0.875rem;
                    margin: 0.25rem;
                    border: 1px solid rgba(99, 102, 241, 0.3);
                    font-weight: 500;
                '>{tech}</span>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("🔧 Technology stack information not available")
    
    with col2:
        products = data.get('products', [])
        if products and len(products) > 0:
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #334155;
            '>
                <h4 style='color: #8b5cf6; margin-bottom: 1rem;'>📦 Products</h4>
            """, unsafe_allow_html=True)
            
            for product in products[:10]:
                st.markdown(f"""
                <span style='
                    display: inline-block;
                    background: rgba(139, 92, 246, 0.2);
                    color: #c4b5fd;
                    padding: 0.5rem 1rem;
                    border-radius: 6px;
                    font-size: 0.875rem;
                    margin: 0.25rem;
                    border: 1px solid rgba(139, 92, 246, 0.3);
                    font-weight: 500;
                '>{product}</span>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("📦 Product information not available")


def calculate_data_completeness(data: Dict) -> int:
    """Calculate data completeness percentage"""
    fields = [
        'description', 'funding_raised', 'employees', 'valuation',
        'funding_stage', 'leadership', 'investors', 'website',
        'founded_year', 'technologies', 'products', 'competitors',
        'ceo', 'location', 'industry'
    ]
    
    completed = sum(1 for field in fields if data.get(field))
    return int((completed / len(fields)) * 100)


def display_complete_dashboard(data: Dict):
    """Display the complete analysis dashboard with all components"""
    
    # Data sources status at the top
    display_data_sources(data)
    
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    # Create organized tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "💰 Funding & Financials",
        "👥 Team & Leadership",
        "🎯 Market & Investment"
    ])
    
    with tab1:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        display_company_overview(data)
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        display_technology_stack(data)
    
    with tab2:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        display_funding_analysis(data)
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        display_financial_dashboard(data)
    
    with tab3:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        display_team_analysis(data)
    
    with tab4:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        display_market_analysis(data)
    
    # Data completeness footer
    st.markdown("<div style='margin-top: 3rem;'></div>", unsafe_allow_html=True)
    
    data_completeness = calculate_data_completeness(data)
    completeness_color = "#10b981" if data_completeness >= 75 else "#f59e0b" if data_completeness >= 50 else "#ef4444"
    
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        border: 1px solid #334155;
        display: flex;
        justify-content: space-between;
        align-items: center;
    '>
        <div>
            <span style='color: #94a3b8; font-size: 0.875rem;'>
                📈 Data Completeness Score
            </span>
        </div>
        <div>
            <span style='color: {completeness_color}; font-weight: 700; font-size: 1.5rem;'>
                {data_completeness}%
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Timestamp
    st.markdown(f"""
    <div style='text-align: center; color: #64748b; font-size: 0.75rem; margin-top: 2rem;'>
        Analysis generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
    </div>
    """, unsafe_allow_html=True)