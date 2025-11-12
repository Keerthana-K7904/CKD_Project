import pandas as pd
import networkx as nx
from typing import List, Dict, Tuple
import json

class DrugInteractionAnalyzer:
    def __init__(self):
        self.interaction_graph = nx.Graph()
        self.rules = self._load_interaction_rules()
        self.name_to_class = self._load_name_to_class_map()

    def _load_name_to_class_map(self) -> Dict[str, str]:
        """Map common medication names to therapeutic classes used in rules."""
        mapping = {
            # ACE inhibitors
            "lisinopril": "ACE_INHIBITORS",
            "enalapril": "ACE_INHIBITORS",
            "ramipril": "ACE_INHIBITORS",
            # Potassium-sparing diuretics
            "spironolactone": "POTASSIUM_SPARING_DIURETICS",
            "eplerenone": "POTASSIUM_SPARING_DIURETICS",
            "amiloride": "POTASSIUM_SPARING_DIURETICS",
            "triamterene": "POTASSIUM_SPARING_DIURETICS",
            # Loop/thiazide diuretics
            "furosemide": "DIURETICS",
            "torsemide": "DIURETICS",
            "bumetanide": "DIURETICS",
            "hydrochlorothiazide": "DIURETICS",
            # NSAIDs
            "ibuprofen": "NSAIDS",
            "naproxen": "NSAIDS",
            "diclofenac": "NSAIDS",
            "indomethacin": "NSAIDS",
            # Others
            "lithium": "LITHIUM",
            "digoxin": "DIGOXIN",
            # Supplements
            "potassium": "POTASSIUM",
            "potassium chloride": "POTASSIUM",
        }
        # Normalize keys
        return {k.lower(): v for k, v in mapping.items()}
        
    def _load_interaction_rules(self) -> Dict:
        """Load predefined drug interaction rules"""
        # This would typically be loaded from a database or file
        return {
            'ACE_INHIBITORS': {
                'contraindications': ['POTASSIUM_SPARING_DIURETICS'],
                'warnings': ['NSAIDS', 'LITHIUM', 'POTASSIUM'],
                'precautions': ['DIURETICS']
            },
            'DIURETICS': {
                'contraindications': ['POTASSIUM_SPARING_DIURETICS'],
                'warnings': ['DIGOXIN'],
                'precautions': ['ACE_INHIBITORS']
            }
        }
    
    def analyze_interactions(self, medications: List[str]) -> Dict:
        """
        Analyze potential drug interactions for a list of medications
        """
        interactions = {
            'contraindications': [],
            'warnings': [],
            'precautions': []
        }
        
        # Normalize and map names to classes
        normalized = [self.name_to_class.get(m.strip().lower(), m.strip().upper()) for m in medications]

        # Check each medication against others
        for i, med1 in enumerate(normalized):
            for med2 in normalized[i+1:]:
                # Check rule-based interactions
                rule_interactions = self._check_rule_based_interactions(med1, med2)
                for category, interaction in rule_interactions.items():
                    if interaction:
                        interactions[category].append({
                            'medication1': medications[i],
                            'medication2': medications[i+1:][0] if medications[i+1:] else med2,
                            'interaction_type': interaction
                        })
                
                # Check knowledge graph interactions
                graph_interactions = self._check_graph_based_interactions(med1, med2)
                if graph_interactions:
                    interactions['warnings'].append({
                        'medication1': medications[i],
                        'medication2': medications[i+1:][0] if medications[i+1:] else med2,
                        'interaction_type': graph_interactions
                    })
        
        return interactions
    
    def _check_rule_based_interactions(self, med1: str, med2: str) -> Dict:
        """Check interactions based on predefined rules"""
        interactions = {
            'contraindications': None,
            'warnings': None,
            'precautions': None
        }
        
        # Check if med1 exists in rules and med2 is in its interaction lists
        if med1 in self.rules:
            rules = self.rules[med1]
            if med2 in rules.get('contraindications', []):
                interactions['contraindications'] = f"Contraindication: {med1} with {med2}"
            elif med2 in rules.get('warnings', []):
                interactions['warnings'] = f"Warning: {med1} may interact with {med2}"
            elif med2 in rules.get('precautions', []):
                interactions['precautions'] = f"Precaution: Monitor {med1} with {med2}"
        
        # Check if med2 exists in rules and med1 is in its interaction lists
        if med2 in self.rules:
            rules = self.rules[med2]
            if med1 in rules.get('contraindications', []):
                interactions['contraindications'] = f"Contraindication: {med2} with {med1}"
            elif med1 in rules.get('warnings', []):
                interactions['warnings'] = f"Warning: {med2} may interact with {med1}"
            elif med1 in rules.get('precautions', []):
                interactions['precautions'] = f"Precaution: Monitor {med2} with {med1}"
        
        return interactions
    
    def _check_graph_based_interactions(self, med1: str, med2: str) -> str:
        """Check interactions using knowledge graph"""
        if self.interaction_graph.has_edge(med1, med2):
            return self.interaction_graph[med1][med2]['interaction_type']
        return None
    
    def add_interaction(self, med1: str, med2: str, interaction_type: str):
        """Add a new interaction to the knowledge graph"""
        self.interaction_graph.add_edge(med1, med2, interaction_type=interaction_type)
    
    def get_interaction_summary(self, interactions: Dict) -> str:
        """Generate a human-readable summary of interactions"""
        total = (len(interactions.get('contraindications', [])) + 
                len(interactions.get('warnings', [])) + 
                len(interactions.get('precautions', [])))
        
        if total == 0:
            return "✅ No significant drug interactions detected. All medication combinations appear safe."
        
        summary_parts = []
        
        # Overall summary
        summary_parts.append(f"⚠️ Found {total} potential drug interaction(s):")
        
        # Contraindications
        contras = interactions.get('contraindications', [])
        if contras:
            summary_parts.append(f"\n🚨 CONTRAINDICATIONS ({len(contras)}):")
            for interaction in contras:
                med1 = interaction.get('medication1', 'Unknown')
                med2 = interaction.get('medication2', 'Unknown')
                interaction_type = interaction.get('interaction_type', 'Interaction detected')
                summary_parts.append(f"   • {med1} + {med2}: {interaction_type}")
        
        # Warnings
        warns = interactions.get('warnings', [])
        if warns:
            summary_parts.append(f"\n⚠️ WARNINGS ({len(warns)}):")
            for interaction in warns:
                med1 = interaction.get('medication1', 'Unknown')
                med2 = interaction.get('medication2', 'Unknown')
                interaction_type = interaction.get('interaction_type', 'Interaction detected')
                summary_parts.append(f"   • {med1} + {med2}: {interaction_type}")
        
        # Precautions
        precauts = interactions.get('precautions', [])
        if precauts:
            summary_parts.append(f"\n💡 PRECAUTIONS ({len(precauts)}):")
            for interaction in precauts:
                med1 = interaction.get('medication1', 'Unknown')
                med2 = interaction.get('medication2', 'Unknown')
                interaction_type = interaction.get('interaction_type', 'Interaction detected')
                summary_parts.append(f"   • {med1} + {med2}: {interaction_type}")
        
        # Add recommendation
        if contras:
            summary_parts.append("\n🔴 RECOMMENDATION: Avoid contraindicated combinations or consult physician immediately.")
        elif warns:
            summary_parts.append("\n🟡 RECOMMENDATION: Monitor patient closely for adverse effects.")
        else:
            summary_parts.append("\n🟢 RECOMMENDATION: Exercise normal clinical monitoring.")
        
        return "\n".join(summary_parts)


