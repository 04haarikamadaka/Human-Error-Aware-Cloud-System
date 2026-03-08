import json
import os
from datetime import datetime
import pandas as pd

class HistoryManager:
    def __init__(self):
        self.history_file = "data/scan_history.json"
        self.ensure_history_file()
    
    def ensure_history_file(self):
        """Create history file if it doesn't exist"""
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)
    
    def save_scan(self, filename, violations, risk_score, risk_level):
        """Save a scan result to history"""
        
        # Load existing history
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        # Create new scan entry
        scan_entry = {
            "scan_id": len(history) + 1,
            "timestamp": datetime.now().isoformat(),
            "filename": filename,
            "violations_count": len(violations),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "violations": violations[:5]  # Store only first 5 violations for preview
        }
        
        # Add to history
        history.append(scan_entry)
        
        # Keep only last 50 scans to prevent file from getting too large
        if len(history) > 50:
            history = history[-50:]
        
        # Save back to file
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return scan_entry
    
    def get_history(self, limit=10):
        """Get recent scan history"""
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        # Return most recent first, limited to specified number
        return list(reversed(history))[:limit]
    
    def get_scan_by_id(self, scan_id):
        """Get a specific scan by ID"""
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        for scan in history:
            if scan["scan_id"] == scan_id:
                return scan
        return None
    
    def get_statistics(self):
        """Get statistics from scan history"""
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        if not history:
            return {
                "total_scans": 0,
                "average_risk_score": 0,
                "most_common_risk_level": "N/A",
                "total_violations": 0
            }
        
        # Calculate statistics
        total_scans = len(history)
        avg_risk = sum(s["risk_score"] for s in history) / total_scans
        
        # Count risk levels
        risk_levels = {}
        for s in history:
            level = s["risk_level"]
            risk_levels[level] = risk_levels.get(level, 0) + 1
        
        most_common = max(risk_levels, key=risk_levels.get) if risk_levels else "N/A"
        
        total_violations = sum(s["violations_count"] for s in history)
        
        return {
            "total_scans": total_scans,
            "average_risk_score": round(avg_risk, 1),
            "most_common_risk_level": most_common,
            "total_violations": total_violations,
            "risk_level_distribution": risk_levels
        }
    
    def get_trend_data(self):
        """Get data for trend visualization"""
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        if not history:
            return pd.DataFrame()
        
        # Create DataFrame for easy plotting
        data = []
        for scan in history[-20:]:  # Last 20 scans
            data.append({
                "date": scan["timestamp"][:10],  # Just the date part
                "risk_score": scan["risk_score"],
                "violations": scan["violations_count"],
                "filename": scan["filename"]
            })
        
        return pd.DataFrame(data)