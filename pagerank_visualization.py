from manim import *
import numpy as np
import networkx as nx

class PageRankVisualization(Scene):
    def construct(self):
        # Title
        title = Text("PageRank Algorithm", font_size=48)
        subtitle = Text("How Google Ranks Web Pages", font_size=28, color=GRAY)
        subtitle.next_to(title, DOWN)
        title_group = VGroup(title, subtitle)
        
        self.play(Write(title_group))
        self.wait(1.5)
        self.play(FadeOut(title_group))
        
        # Create a purely directed graph (no bidirectional edges)
        # This represents web pages linking to each other
        edges = [(0, 1), (0, 2), (1, 3), (2, 1), (2, 4), (3, 2), (4, 0), (4, 1)]
        
        # Position nodes in a nice layout
        pos = {
            0: np.array([-2, 1.5, 0]),
            1: np.array([0, 2, 0]),
            2: np.array([2, 1, 0]),
            3: np.array([1, -1.5, 0]),
            4: np.array([-1.5, -1, 0])
        }
        
        # Create node objects
        nodes = []
        node_labels = []
        
        for i in range(5):
            node = Circle(radius=0.4, color=BLUE, fill_opacity=0.8)
            node.move_to(pos[i])
            
            label = Text(str(i), font_size=28, color=WHITE)
            label.move_to(node.get_center())
            
            nodes.append(node)
            node_labels.append(label)
        
        # Create edges
        edge_objects = []
        for start, end in edges:
            edge = Arrow(
                start=pos[start] + 0.4 * (pos[end] - pos[start]) / np.linalg.norm(pos[end] - pos[start]),
                end=pos[end] - 0.4 * (pos[end] - pos[start]) / np.linalg.norm(pos[end] - pos[start]),
                buff=0,
                stroke_width=3,
                color=WHITE,
                max_stroke_width_to_length_ratio=3,
                max_tip_length_to_length_ratio=0.15
            )
            edge_objects.append(edge)
        
        # Show graph
        graph_title = Text("Web Pages as a Directed Graph", font_size=32)
        graph_title.to_edge(UP)
        
        self.play(Write(graph_title))
        self.play(*[Create(node) for node in nodes])
        self.play(*[Write(label) for label in node_labels])
        self.wait(0.5)
        self.play(*[Create(edge) for edge in edge_objects])
        self.wait(1)
        
        # PART 1: Random Surfer Model
        surfer_title = Text("Random Surfer Model", font_size=28, color=YELLOW)
        surfer_title.to_edge(UP)
        self.play(Transform(graph_title, surfer_title))
        
        # Create random surfers
        surfers = []
        for _ in range(3):
            surfer = Dot(radius=0.15, color=YELLOW, fill_opacity=0.9)
            surfer.move_to(nodes[np.random.randint(5)].get_center())
            surfers.append(surfer)
        
        self.play(*[Create(surfer) for surfer in surfers])
        
        # Animate surfers moving along edges
        for _ in range(4):
            animations = []
            for surfer in surfers:
                # Find current node
                current_pos = surfer.get_center()
                current_node = min(range(5), key=lambda i: np.linalg.norm(pos[i] - current_pos))
                
                # Find outgoing edges
                outgoing = [end for start, end in edges if start == current_node]
                if outgoing:
                    next_node = np.random.choice(outgoing)
                    animations.append(surfer.animate.move_to(nodes[next_node].get_center()))
            
            self.play(*animations, run_time=1)
            self.wait(0.3)
        
        self.play(*[FadeOut(surfer) for surfer in surfers])
        
        # Explain the idea
        idea_text = Text("Pages are important if many surfers visit them!", font_size=22, color=GREEN)
        idea_text.to_edge(DOWN)
        self.play(Write(idea_text))
        self.wait(1.5)
        self.play(FadeOut(idea_text))
        
        # PART 2: Build Adjacency Matrix Step by Step
        matrix_title = Text("Building the Adjacency Matrix", font_size=28)
        matrix_title.to_edge(UP)
        self.play(Transform(graph_title, matrix_title))
        
        # Shift graph to the left
        graph_group = VGroup(*nodes, *node_labels, *edge_objects)
        self.play(graph_group.animate.shift(LEFT * 3))
        
        # Create empty matrix on the right
        matrix_size = 0.5
        matrix_start = RIGHT * 2 + UP * 1
        
        # Create matrix grid
        matrix_lines = VGroup()
        for i in range(6):
            h_line = Line(
                matrix_start + LEFT * 0.5 + DOWN * i * matrix_size,
                matrix_start + RIGHT * 2.5 + DOWN * i * matrix_size,
                stroke_width=1
            )
            v_line = Line(
                matrix_start + RIGHT * (i - 0.5) * matrix_size,
                matrix_start + RIGHT * (i - 0.5) * matrix_size + DOWN * 2.5,
                stroke_width=1
            )
            matrix_lines.add(h_line, v_line)
        
        # Add row/column labels
        matrix_labels = VGroup()
        for i in range(5):
            row_label = Text(str(i), font_size=20, color=BLUE)
            row_label.move_to(matrix_start + LEFT * 0.8 + DOWN * (i + 0.5) * matrix_size)
            col_label = Text(str(i), font_size=20, color=BLUE)
            col_label.move_to(matrix_start + RIGHT * i * matrix_size + UP * 0.3)
            matrix_labels.add(row_label, col_label)
        
        self.play(Create(matrix_lines), Write(matrix_labels))
        
        # Create matrix entries (initially all zeros)
        matrix_entries = [[None for _ in range(5)] for _ in range(5)]
        for i in range(5):
            for j in range(5):
                entry = Text("0", font_size=20, color=GRAY)
                entry.move_to(matrix_start + RIGHT * j * matrix_size + DOWN * (i + 0.5) * matrix_size)
                matrix_entries[i][j] = entry
                self.add(entry)
        
        self.wait(0.5)
        
        # Animate building the adjacency matrix
        adj_text = Text("A[i,j] = 1 if page j links to page i", font_size=20)
        adj_text.to_edge(DOWN)
        self.play(Write(adj_text))
        
        for idx, (start, end) in enumerate(edges):
            # Highlight the edge
            edge_objects[idx].set_color(YELLOW)
            self.play(edge_objects[idx].animate.set_stroke_width(5))
            
            # Update matrix entry
            old_entry = matrix_entries[end][start]
            new_entry = Text("1", font_size=20, color=YELLOW)
            new_entry.move_to(old_entry.get_center())
            
            # Animate the connection
            arrow = Arrow(
                edge_objects[idx].get_center(),
                old_entry.get_center(),
                color=YELLOW,
                stroke_width=2
            )
            self.play(Create(arrow))
            self.play(Transform(old_entry, new_entry))
            self.play(FadeOut(arrow))
            
            # Reset edge color
            self.play(
                edge_objects[idx].animate.set_color(WHITE).set_stroke_width(3),
                old_entry.animate.set_color(WHITE)
            )
        
        self.wait(1)
        self.play(FadeOut(adj_text))
        
        # PART 3: Convert to Transition Matrix
        trans_title = Text("From Adjacency to Transition Matrix", font_size=28)
        trans_title.to_edge(UP)
        self.play(Transform(graph_title, trans_title))
        
        # Explain column normalization
        norm_text = Text("Divide each column by its sum (outgoing links)", font_size=20)
        norm_text.to_edge(DOWN)
        self.play(Write(norm_text))
        
        # Calculate column sums and normalize
        adj_matrix = np.zeros((5, 5))
        for start, end in edges:
            adj_matrix[end, start] = 1
        
        col_sums = adj_matrix.sum(axis=0)
        col_sums[col_sums == 0] = 1  # Avoid division by zero
        
        # Animate normalization column by column
        for j in range(5):
            if col_sums[j] > 1:
                # Highlight column
                col_rect = Rectangle(
                    width=matrix_size * 0.8,
                    height=matrix_size * 5,
                    color=YELLOW,
                    fill_opacity=0.2
                )
                col_rect.move_to(matrix_start + RIGHT * j * matrix_size + DOWN * 2 * matrix_size)
                self.play(Create(col_rect))
                
                # Update entries in this column
                for i in range(5):
                    if adj_matrix[i, j] == 1:
                        old_entry = matrix_entries[i][j]
                        new_value = f"{1/col_sums[j]:.2f}"
                        new_entry = Text(new_value, font_size=18, color=GREEN)
                        new_entry.move_to(old_entry.get_center())
                        self.play(Transform(old_entry, new_entry))
                
                self.play(FadeOut(col_rect))
        
        self.wait(1)
        self.play(FadeOut(norm_text))
        
        # PART 4: Iterative Process
        iter_title = Text("PageRank: The Iterative Process", font_size=28)
        iter_title.to_edge(UP)
        self.play(Transform(graph_title, iter_title))
        
        # Initialize PageRank values
        pr_values = np.ones(5) / 5  # Start with uniform distribution
        pr_labels = []
        
        for i in range(5):
            pr_label = Text(f"{pr_values[i]:.3f}", font_size=18, color=YELLOW)
            pr_label.next_to(nodes[i], RIGHT, buff=0.2)
            pr_labels.append(pr_label)
            self.play(Write(pr_label))
        
        # Create transition matrix with damping factor
        d = 0.85
        n = 5
        transition_matrix = adj_matrix / col_sums
        M = d * transition_matrix + (1 - d) / n * np.ones((n, n))
        
        # Show iteration formula
        formula = MathTex(r"PR^{(t+1)} = M \cdot PR^{(t)}", font_size=32)
        formula.to_edge(DOWN)
        self.play(Write(formula))
        
        # Perform iterations
        for iteration in range(4):
            iter_text = Text(f"Iteration {iteration + 1}", font_size=20, color=GRAY)
            iter_text.next_to(formula, UP)
            self.play(Write(iter_text))
            
            # Calculate new values
            new_pr_values = M @ pr_values
            
            # Animate the update
            for i in range(5):
                new_label = Text(f"{new_pr_values[i]:.3f}", font_size=18, color=YELLOW)
                new_label.move_to(pr_labels[i].get_center())
                self.play(Transform(pr_labels[i], new_label))
            
            pr_values = new_pr_values
            self.play(FadeOut(iter_text))
            self.wait(0.5)
        
        # PART 5: Reveal Eigenvector Solution
        self.play(FadeOut(formula))
        
        eigen_title = Text("The Analytical Solution: Eigenvectors!", font_size=28, color=GREEN)
        eigen_title.to_edge(UP)
        self.play(Transform(graph_title, eigen_title))
        
        # Show eigenvalue equation
        eigen_eq = MathTex(r"M \vec{v} = \lambda \vec{v}", font_size=36)
        eigen_eq.shift(DOWN * 2.5)
        self.play(Write(eigen_eq))
        
        eigen_text = Text("PageRank = dominant eigenvector (λ = 1)", font_size=22)
        eigen_text.next_to(eigen_eq, DOWN)
        self.play(Write(eigen_text))
        
        # Calculate and show convergence
        eigenvalues, eigenvectors = np.linalg.eig(M)
        idx = np.argmax(np.abs(eigenvalues))
        pagerank_vector = np.abs(eigenvectors[:, idx])
        pagerank_vector = pagerank_vector / pagerank_vector.sum()
        
        # Update to final values with emphasis
        for i in range(5):
            final_label = Text(f"{pagerank_vector[i]:.3f}", font_size=20, color=GREEN)
            final_label.move_to(pr_labels[i].get_center())
            self.play(
                Transform(pr_labels[i], final_label),
                nodes[i].animate.set_fill(GREEN, opacity=0.3 + 0.7 * pagerank_vector[i] / max(pagerank_vector))
            )
        
        # Final message
        final_text = Text("Iterations converge to the eigenvector solution!", font_size=24, color=GREEN)
        final_text.to_edge(DOWN)
        self.play(Transform(eigen_text, final_text))
        
        self.wait(2)

# To render this animation, use:
# manim -pql pagerank_visualization.py PageRankVisualization
