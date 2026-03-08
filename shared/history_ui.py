import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from shared.history_manager import HistoryManager

def display_history_sidebar():
    """Display history in the sidebar"""
    
    history_mgr = HistoryManager()
    
    with st.sidebar:
        st.title("📊 Scan History")
        
        # Get statistics
        stats = history_mgr.get_statistics()
        
        # Display stats in metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Scans", stats["total_scans"])
        with col2:
            st.metric("Avg Risk Score", stats["average_risk_score"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Violations", stats["total_violations"])
        with col2:
            st.metric("Most Common", stats["most_common_risk_level"])
        
        st.divider()
        
        # Get recent scans
        recent_scans = history_mgr.get_history(limit=5)
        
        if recent_scans:
            st.subheader("📋 Recent Scans")
            
            for scan in recent_scans:
                # Create an expander for each scan
                with st.expander(f"Scan #{scan['scan_id']} - {scan['filename']}"):
                    st.write(f"📅 {scan['timestamp'][:16]}")
                    st.write(f"⚠️ Violations: {scan['violations_count']}")
                    st.write(f"🎯 Risk Score: {scan['risk_score']}")
                    st.write(f"📊 Risk Level: **{scan['risk_level']}**")
                    
                    # Show preview of violations
                    if scan['violations']:
                        st.write("**Top violations:**")
                        for v in scan['violations'][:3]:
                            st.caption(f"• {v['description'][:50]}...")
        else:
            st.info("No scans yet. Upload a file to get started!")

def display_history_page():
    """Display full history page"""
    
    st.header("📜 Scan History Dashboard")
    
    history_mgr = HistoryManager()
    recent_scans = history_mgr.get_history(limit=20)
    
    if not recent_scans:
        st.info("No scan history available. Upload some Terraform files to get started!")
        return
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 History Table", "📈 Trends", "📊 Statistics"])
    
    with tab1:
        # Convert to DataFrame for display
        df = pd.DataFrame(recent_scans)
        
        # Format for display
        display_df = df[['scan_id', 'timestamp', 'filename', 'violations_count', 'risk_score', 'risk_level']].copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        display_df.columns = ['ID', 'Timestamp', 'File', 'Violations', 'Risk Score', 'Risk Level']
        
        st.dataframe(display_df, use_container_width=True)
        
        # View details of specific scan
        st.subheader("View Scan Details")
        scan_ids = [f"Scan #{s['scan_id']} - {s['filename']}" for s in recent_scans]
        selected = st.selectbox("Select a scan to view details:", scan_ids)
        
        if selected:
            scan_id = int(selected.split('#')[1].split(' ')[0])
            scan = history_mgr.get_scan_by_id(scan_id)
            
            if scan:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Risk Score", scan['risk_score'])
                with col2:
                    st.metric("Risk Level", scan['risk_level'])
                with col3:
                    st.metric("Violations", scan['violations_count'])
                
                if scan['violations']:
                    st.write("**Violations detected:**")
                    for v in scan['violations']:
                        st.error(f"⚠️ {v['description']} - {v['severity']}")
    
    with tab2:
        # Trend visualization
        trend_data = history_mgr.get_trend_data()
        
        if not trend_data.empty:
            # Risk score trend
            fig1 = px.line(trend_data, x='date', y='risk_score', 
                          title='Risk Score Trend Over Time',
                          markers=True)
            st.plotly_chart(fig1, use_container_width=True)
            
            # Violations trend
            fig2 = px.bar(trend_data, x='date', y='violations',
                         title='Violations Detected Over Time',
                         color='violations')
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        # Statistics
        stats = history_mgr.get_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Scans Performed", stats['total_scans'])
            st.metric("Average Risk Score", stats['average_risk_score'])
        
        with col2:
            st.metric("Total Violations Found", stats['total_violations'])
            st.metric("Most Common Risk Level", stats['most_common_risk_level'])
        
        # Risk level distribution pie chart
        if stats['risk_level_distribution']:
            dist_df = pd.DataFrame([
                {"Risk Level": level, "Count": count}
                for level, count in stats['risk_level_distribution'].items()
            ])
            
            fig = px.pie(dist_df, values='Count', names='Risk Level',
                        title='Risk Level Distribution',
                        color='Risk Level',
                        color_discrete_map={
                            'CRITICAL': 'red',
                            'HIGH': 'orange',
                            'MEDIUM': 'yellow',
                            'LOW': 'green'
                        })
            st.plotly_chart(fig, use_container_width=True)