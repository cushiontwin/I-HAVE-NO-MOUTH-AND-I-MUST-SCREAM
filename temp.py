def update(self):
        if not self.started:
            return

        elapsed_since_start = time.time() - self.start_time
        if elapsed_since_start < self.start_delay:
            return

        if self.current is None and self.queue:
            self.current = self.queue.pop(0)
            self.current_start_time = time.time()

            if not self.current.pause:
                if self.current.start_pos is None:
                    self.current.start_pos = (self.current.sprite.x,
                                              self.current.sprite.y)
        if self.current:
            step = self.current
            elapsed = time.time() - self.current_start_time
            if elapsed < step.delay:
                return

            if step.pause:
                if elapsed >= step.delay + step.duration:
                    self.current = None
            else:
                t = min((elapsed - step.delay) / step.duration, 1.0)
                sx, sy = step.start_pos
                ex, ey = step.end_pos
                step.sprite.x = sx + (ex - sx) * t
                step.sprite.y = sy + (ey - sy) * t

                if t >= 1.0:
                    step.sprite.x, step.sprite.y = ex, ey
                    self.current = None