from manim import *
import numpy as np
import random

class PageRankRandomSurfer(Scene):
    def construct(self):
        # Configuration
        DAMPING = 0.8
        NUM_NODES = 5
        NUM_ITERATIONS = 8
        
        # Create graph structure
        graph_edges = [
            (0, 1), (0, 2),
            (1, 2), (1, 3),
            (2, 1), (2, 3), (2, 4),
            (3, 4),
            (4, 0), (4, 1)
        ]
        
        # Node positions in a nice layout (shifted down to avoid overlap)
        graph_offset = DOWN * 0.8
        positions = {
            0: UP * 2 + graph_offset,
            1: RIGHT * 2.5 + UP * 0.5 + graph_offset,
            2: RIGHT * 1.5 + DOWN * 2 + graph_offset,
            3: LEFT * 1.5 + DOWN * 2 + graph_offset,
            4: LEFT * 2.5 + UP * 0.5 + graph_offset
        }
        
        # Create nodes
        nodes = {}
        node_labels = {}
        
        for i in range(NUM_NODES):
            nodes[i] = Circle(radius=0.4, color=BLUE, fill_opacity=0.7)
            nodes[i].move_to(positions[i])
            node_labels[i] = Text(str(i), font_size=24).next_to(nodes[i], UP, buff=0.2)
        
        # Create edges
        edges = []
        for start, end in graph_edges:
            edge = Arrow(
                nodes[start].get_center(),
                nodes[end].get_center(),
                buff=0.4,
                color=GRAY,
                stroke_width=2,
                max_tip_length_to_length_ratio=0.15
            )
            edges.append(edge)
        
        # Add title
        title = Text("PageRank: Random Surfer Model", font_size=36)
        title.to_edge(UP)
        subtitle = Text(f"Damping Factor = {DAMPING}", font_size=24, color=GRAY)
        subtitle.next_to(title, DOWN)
        
        # Create surfer (small dot that moves between nodes)
        surfer = Dot(radius=0.15, color=RED)
        surfer.move_to(nodes[0].get_center())
        current_node = 0
        
        # Add all elements to scene at once
        self.add(title, subtitle)
        self.add(*edges)
        self.add(*[nodes[i] for i in range(NUM_NODES)])
        self.add(*[node_labels[i] for i in range(NUM_NODES)])
        self.add(surfer)
        self.wait(2)
        
        # Create iteration counter
        iteration_text = Text("Iteration: 0", font_size=20).to_corner(UL)
        self.play(Write(iteration_text))
        
        # Simulate random surfer
        for iteration in range(NUM_ITERATIONS):
            # Update iteration counter
            new_iteration_text = Text(f"Iteration: {iteration + 1}", font_size=20).to_corner(UL)
            self.play(Transform(iteration_text, new_iteration_text), run_time=0.2)
            
            # Determine next node
            if random.random() < DAMPING:
                # Follow a link
                outgoing = [end for start, end in graph_edges if start == current_node]
                if outgoing:
                    next_node = random.choice(outgoing)
                    # Highlight the edge being followed
                    edge_to_highlight = None
                    for i, (start, end) in enumerate(graph_edges):
                        if start == current_node and end == next_node:
                            edge_to_highlight = edges[i]
                            break
                    
                    if edge_to_highlight:
                        self.play(
                            edge_to_highlight.animate.set_color(RED).set_stroke_width(4),
                            run_time=0.2
                        )
                else:
                    # Dead end, random jump
                    next_node = random.choice(list(range(NUM_NODES)))
            else:
                # Random jump (teleport)
                next_node = random.choice(list(range(NUM_NODES)))
                # Show teleportation with a dashed arc
                arc = DashedLine(
                    surfer.get_center(),
                    nodes[next_node].get_center(),
                    color=YELLOW,
                    stroke_width=2,
                    dash_length=0.2
                )
                self.play(Create(arc), run_time=0.2)
                self.play(FadeOut(arc), run_time=0.15)
            
            # Move surfer
            self.play(
                surfer.animate.move_to(nodes[next_node].get_center()),
                nodes[next_node].animate.set_fill(RED, opacity=0.8),
                run_time=0.4
            )
            
            
            # Reset colors
            self.play(
                nodes[next_node].animate.set_fill(BLUE, opacity=0.7),
                *[edges[i].animate.set_color(GRAY).set_stroke_width(2) 
                  for i in range(len(edges))],
                run_time=0.2
            )
            
            current_node = next_node
            self.wait(0.15)
        
        # Final pause to show results
        self.wait(3)
