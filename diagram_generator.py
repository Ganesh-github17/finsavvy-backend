import os
import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass
import graphviz

@dataclass
class ClassDefinition:
    name: str
    attributes: List[str]
    methods: List[str]
    relationships: List[Dict[str, str]]

class DiagramGenerator:
    def __init__(self):
        self.output_dir = 'generated_diagrams'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_class_diagram(self, classes: List[ClassDefinition], filename: str) -> str:
        dot = graphviz.Digraph(comment='Class Diagram')
        dot.attr(rankdir='TB')
        
        # Add classes
        for cls in classes:
            # Create class node
            label = f"{cls.name}|{self._format_attributes(cls.attributes)}|{self._format_methods(cls.methods)}"
            dot.node(cls.name, label, shape='record')
            
            # Add relationships
            for rel in cls.relationships:
                dot.edge(cls.name, rel['target'], rel['type'])
        
        # Save the diagram
        output_path = os.path.join(self.output_dir, f"{filename}.png")
        dot.render(output_path, format='png', cleanup=True)
        return output_path
    
    def generate_sequence_diagram(self, sequence_data: Dict, filename: str) -> str:
        # Create PlantUML content
        puml_content = "@startuml\n"
        puml_content += "skinparam sequence {\n"
        puml_content += "    ParticipantBackgroundColor #FEFECE\n"
        puml_content += "    ParticipantBorderColor #666666\n"
        puml_content += "}\n\n"
        
        # Add participants
        for participant in sequence_data['participants']:
            puml_content += f"participant {participant}\n"
        
        # Add interactions
        for interaction in sequence_data['interactions']:
            puml_content += f"{interaction['from']} -> {interaction['to']}: {interaction['message']}\n"
            if interaction.get('response'):
                puml_content += f"{interaction['to']} --> {interaction['from']}: {interaction['response']}\n"
        
        puml_content += "@enduml"
        
        # Save and generate diagram
        output_path = os.path.join(self.output_dir, f"{filename}")
        with open(f"{output_path}.puml", 'w') as f:
            f.write(puml_content)
        
        # Convert to PNG using PlantUML
        try:
            subprocess.run(['plantuml', f"{output_path}.puml"])
            return f"{output_path}.png"
        except Exception as e:
            raise Exception(f"Error generating sequence diagram: {str(e)}")
    
    def generate_architecture_diagram(self, components: Dict, filename: str) -> str:
        dot = graphviz.Digraph(comment='Architecture Diagram')
        dot.attr(rankdir='TB')
        
        # Add components
        for comp_name, comp_data in components['components'].items():
            dot.node(comp_name, comp_name, shape='box', style='rounded')
        
        # Add connections
        for conn in components['connections']:
            dot.edge(
                conn['from'],
                conn['to'],
                label=conn.get('label', ''),
                style=conn.get('style', 'solid')
            )
        
        # Save the diagram
        output_path = os.path.join(self.output_dir, f"{filename}.png")
        dot.render(output_path, format='png', cleanup=True)
        return output_path
    
    def _format_attributes(self, attributes: List[str]) -> str:
        return '\n'.join(attributes) if attributes else ''
    
    def _format_methods(self, methods: List[str]) -> str:
        return '\n'.join(methods) if methods else ''

# Example usage
def example_usage():
    generator = DiagramGenerator()
    
    # Class diagram example
    classes = [
        ClassDefinition(
            name='User',
            attributes=['+id: int', '-name: string', '#email: string'],
            methods=['+ login()', '+ logout()', '- validate()'],
            relationships=[{'target': 'Profile', 'type': 'has-a'}]
        ),
        ClassDefinition(
            name='Profile',
            attributes=['+user_id: int', '-bio: string'],
            methods=['+ update_bio(text: string)'],
            relationships=[]
        )
    ]
    generator.generate_class_diagram(classes, 'class_diagram')
    
    # Sequence diagram example
    sequence_data = {
        'participants': ['User', 'Frontend', 'Backend', 'Database'],
        'interactions': [
            {
                'from': 'User',
                'to': 'Frontend',
                'message': 'Login Request',
                'response': 'Display Form'
            },
            {
                'from': 'Frontend',
                'to': 'Backend',
                'message': 'Validate Credentials',
                'response': 'Token'
            }
        ]
    }
    generator.generate_sequence_diagram(sequence_data, 'sequence_diagram')
    
    # Architecture diagram example
    architecture = {
        'components': {
            'Web Client': {},
            'API Gateway': {},
            'Auth Service': {},
            'User Service': {},
            'Database': {}
        },
        'connections': [
            {'from': 'Web Client', 'to': 'API Gateway', 'label': 'HTTPS'},
            {'from': 'API Gateway', 'to': 'Auth Service', 'label': 'REST'},
            {'from': 'API Gateway', 'to': 'User Service', 'label': 'REST'},
            {'from': 'Auth Service', 'to': 'Database', 'style': 'dashed'},
            {'from': 'User Service', 'to': 'Database', 'style': 'dashed'}
        ]
    }
    generator.generate_architecture_diagram(architecture, 'architecture_diagram')

if __name__ == '__main__':
    example_usage()