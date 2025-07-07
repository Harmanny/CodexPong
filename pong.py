# Pong game with colorful gradient using Tkinter
import tkinter as tk

class GradientCanvas(tk.Canvas):
    def __init__(self, master, width, height, start_color, end_color, **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=0, **kwargs)
        self.start_color = start_color
        self.end_color = end_color
        self.width = width
        self.height = height
        self.draw_gradient()

    def _hex_color(self, r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_gradient(self):
        r1, g1, b1 = self.winfo_rgb(self.start_color)
        r2, g2, b2 = self.winfo_rgb(self.end_color)
        r_ratio = (r2 - r1) / self.height
        g_ratio = (g2 - g1) / self.height
        b_ratio = (b2 - b1) / self.height
        for i in range(self.height):
            nr = int(r1 + (r_ratio * i)) >> 8
            ng = int(g1 + (g_ratio * i)) >> 8
            nb = int(b1 + (b_ratio * i)) >> 8
            color = self._hex_color(nr, ng, nb)
            self.create_line(0, i, self.width, i, fill=color)

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

class Pong:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Codex Pong")
        self.width = 600
        self.height = 400
        self.canvas = GradientCanvas(
            self.root,
            self.width,
            self.height,
            start_color="#004e92",
            end_color="#000428",
        )
        self.canvas.pack()

        self.paddle_width = 10
        self.paddle_height = 80
        self.ball_radius = 8
        self.paddle_speed = 6
        self.ball_speed_x = 4
        self.ball_speed_y = 4

        self.score = 0
        self.highscore = self.load_highscore()
        self.state = "title"

        self.root.bind("<Up>", self.on_key_up)
        self.root.bind("<Down>", self.on_key_down)
        self.root.bind("<space>", self.start_game)

        self.show_title()
        self.root.mainloop()

    def load_highscore(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def save_highscore(self):
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.highscore))
        except Exception:
            pass

    def on_key_up(self, _event):
        if self.state == "play":
            self.move_paddle(self.right_paddle, -self.paddle_speed)

    def on_key_down(self, _event):
        if self.state == "play":
            self.move_paddle(self.right_paddle, self.paddle_speed)

    def start_game(self, _event=None):
        if self.state != "title":
            return
        self.state = "play"
        self.score = 0
        self.canvas.delete("title")
        self.create_objects()
        self.update_score_text()
        self.animate()

    def show_title(self):
        self.canvas.delete("game")
        text = (
            "Codex Pong\n"
            "Press SPACE to start\n"
            f"Highscore: {self.highscore}"
        )
        self.canvas.create_text(
            self.width // 2,
            self.height // 2,
            text=text,
            fill="white",
            font=("Helvetica", 24),
            justify="center",
            tags="title",
        )

    def create_objects(self):
        mid_y = self.height // 2
        self.left_paddle = self.canvas.create_rectangle(
            20,
            mid_y - self.paddle_height // 2,
            20 + self.paddle_width,
            mid_y + self.paddle_height // 2,
            fill="#f953c6",
            outline="",
            tags="game",
        )
        self.right_paddle = self.canvas.create_rectangle(
            self.width - 20 - self.paddle_width,
            mid_y - self.paddle_height // 2,
            self.width - 20,
            mid_y + self.paddle_height // 2,
            fill="#b91d73",
            outline="",
            tags="game",
        )
        self.ball = self.canvas.create_oval(
            self.width // 2 - self.ball_radius,
            mid_y - self.ball_radius,
            self.width // 2 + self.ball_radius,
            mid_y + self.ball_radius,
            fill="#ffdd00",
            outline="",
            tags="game",
        )
        self.score_text = self.canvas.create_text(
            self.width // 2,
            20,
            text="",
            fill="white",
            font=("Helvetica", 14),
            tags="game",
        )

    def update_score_text(self):
        self.canvas.itemconfigure(
            self.score_text,
            text=f"Score: {self.score}  Highscore: {self.highscore}",
        )

    def move_paddle(self, paddle, dy):
        x0, y0, x1, y1 = self.canvas.coords(paddle)
        new_y0 = clamp(y0 + dy, 0, self.height - self.paddle_height)
        new_y1 = new_y0 + self.paddle_height
        self.canvas.coords(paddle, x0, new_y0, x1, new_y1)

    def move_cpu(self):
        bx0, by0, bx1, by1 = self.canvas.coords(self.ball)
        ball_cy = (by0 + by1) / 2
        px0, py0, px1, py1 = self.canvas.coords(self.left_paddle)
        paddle_cy = (py0 + py1) / 2
        if paddle_cy < ball_cy - self.paddle_speed:
            self.move_paddle(self.left_paddle, self.paddle_speed)
        elif paddle_cy > ball_cy + self.paddle_speed:
            self.move_paddle(self.left_paddle, -self.paddle_speed)

    def animate(self):
        if self.state != "play":
            return

        self.move_cpu()

        bx0, by0, bx1, by1 = self.canvas.coords(self.ball)
        dx, dy = self.ball_speed_x, self.ball_speed_y
        next_bx0, next_by0 = bx0 + dx, by0 + dy
        next_bx1, next_by1 = bx1 + dx, by1 + dy

        # Collision with top/bottom
        if next_by0 <= 0 or next_by1 >= self.height:
            self.ball_speed_y *= -1

        # Collision with paddles
        if self.check_collision(self.left_paddle, next_bx0, next_by0, next_bx1, next_by1):
            self.ball_speed_x = abs(self.ball_speed_x)
        elif self.check_collision(self.right_paddle, next_bx0, next_by0, next_bx1, next_by1):
            self.ball_speed_x = -abs(self.ball_speed_x)

        self.canvas.move(self.ball, self.ball_speed_x, self.ball_speed_y)
        bx0, by0, bx1, by1 = self.canvas.coords(self.ball)

        if bx0 <= 0:
            self.score += 1
            self.update_score_text()
            self.reset_ball(direction=1)
        elif bx1 >= self.width:
            self.end_game()
            return

        self.root.after(16, self.animate)

    def reset_ball(self, direction):
        mid_y = self.height // 2
        self.canvas.coords(
            self.ball,
            self.width // 2 - self.ball_radius,
            mid_y - self.ball_radius,
            self.width // 2 + self.ball_radius,
            mid_y + self.ball_radius,
        )
        self.ball_speed_x = 4 * direction
        self.ball_speed_y = 4

    def end_game(self):
        self.state = "title"
        if self.score > self.highscore:
            self.highscore = self.score
            self.save_highscore()
        self.show_title()

    def check_collision(self, paddle, bx0, by0, bx1, by1):
        px0, py0, px1, py1 = self.canvas.coords(paddle)
        if bx1 >= px0 and bx0 <= px1 and by1 >= py0 and by0 <= py1:
            return True
        return False

if __name__ == "__main__":
    Pong()
