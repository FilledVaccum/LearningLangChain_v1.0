"""
Checkpoint Tree Visualizer for LangGraph
Usage:
    from checkpoint_visualizer import visualize_checkpoints
    visualize_checkpoints(workflow, thread_id="1")
"""

from IPython.display import display
import graphviz


def visualize_checkpoints(workflow, thread_id, display_graph=True):
    """
    Create a detailed visual tree of checkpoint branches
    
    Args:
        workflow: Compiled LangGraph workflow with checkpointer
        thread_id: Thread ID to visualize (str)
        display_graph: If True, displays the graph. If False, returns the dot object
    
    Returns:
        graphviz.Digraph object
    """
    config = {"configurable": {"thread_id": thread_id}}
    history = list(workflow.get_state_history(config))
    
    dot = graphviz.Digraph(comment='Checkpoint Tree')
    dot.attr(rankdir='TB')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
    
    for snapshot in history:
        checkpoint_id = snapshot.config['configurable']['checkpoint_id']
        parent_config = snapshot.parent_config
        
        # Extract details
        step = snapshot.metadata.get('step', 0)
        source = snapshot.metadata.get('source', 'loop')
        next_nodes = ', '.join(snapshot.next) if snapshot.next else 'END'
        
        # State values (truncate if too long)
        state_str = '\n'.join([
            f"{k}: {str(v)[:30]}..." if len(str(v)) > 30 else f"{k}: {v}"
            for k, v in snapshot.values.items()
        ])
        
        # Timestamp
        created = snapshot.created_at.split('T')[1][:8] if snapshot.created_at else 'N/A'
        
        # Build label with HTML-like formatting
        label = f"""<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
        <TR><TD BGCOLOR="lightblue"><B>Checkpoint {checkpoint_id[:8]}</B></TD></TR>
        <TR><TD ALIGN="LEFT">Step: {step} | Source: {source}</TD></TR>
        <TR><TD ALIGN="LEFT">Time: {created}</TD></TR>
        <TR><TD ALIGN="LEFT">Next: {next_nodes}</TD></TR>
        <TR><TD BGCOLOR="lightyellow" ALIGN="LEFT"><B>State:</B><BR/>{state_str.replace('\n', '<BR/>')}</TD></TR>
        </TABLE>>"""
        
        # Color based on source
        color = {
            'loop': 'lightgreen',
            'update': 'lightyellow', 
            'input': 'lightblue'
        }.get(source, 'white')
        
        dot.node(checkpoint_id, label, fillcolor=color)
        
        # Add edge from parent
        if parent_config:
            parent_id = parent_config['configurable']['checkpoint_id']
            edge_label = 'update' if source == 'update' else 'next'
            dot.edge(parent_id, checkpoint_id, label=edge_label)
    
    if display_graph:
        display(dot)
        return None  # Don't return to avoid double display
    
    return dot


def visualize_checkpoints_compact(workflow, thread_id, display_graph=True):
    """
    Create a compact visual tree of checkpoint branches
    
    Args:
        workflow: Compiled LangGraph workflow with checkpointer
        thread_id: Thread ID to visualize (str)
        display_graph: If True, displays the graph. If False, returns the dot object
    
    Returns:
        graphviz.Digraph object
    """
    config = {"configurable": {"thread_id": thread_id}}
    history = list(workflow.get_state_history(config))
    
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR', size='10,8')
    
    for snapshot in history:
        cid = snapshot.config['configurable']['checkpoint_id'][:8]
        step = snapshot.metadata.get('step', 0)
        source = snapshot.metadata.get('source', 'loop')
        
        label = f"{cid}\nStep:{step}\n{source}\n{list(snapshot.values.keys())}"
        color = 'yellow' if source == 'update' else 'lightblue'
        
        dot.node(cid, label, style='filled', fillcolor=color)
        
        if snapshot.parent_config:
            pid = snapshot.parent_config['configurable']['checkpoint_id'][:8]
            dot.edge(pid, cid)
    
    if display_graph:
        display(dot)
    
    return dot
