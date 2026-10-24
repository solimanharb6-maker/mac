"""
mobile.py - Touch controls for Supermarket Simulator 2D
Floating joystick (left half of the screen) + action buttons.
Works with FINGER events (Android / iPhone-Safari / touch screens).
Menus keep using the synthesized mouse events, so they need no change.
"""
import math
import pygame


def _inside(rect, x, y):
    rx, ry, rw, rh = rect
    return rx <= x <= rx + rw and ry <= y <= ry + rh


def _in_circle(cx, cy, r, x, y):
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def map_finger(fx, fy, win_w, win_h, sw, sh):
    """Normalized finger coords (0..1 of the window) -> logical game coords.
    Handles the letterbox bars that pygame.SCALED adds."""
    s = min(win_w / float(sw), win_h / float(sh))
    ox = (win_w - sw * s) / 2.0
    oy = (win_h - sh * s) / 2.0
    return (fx * win_w - ox) / s, (fy * win_h - oy) / s


class TouchControls:
    DEAD = 0.18

    def __init__(self, sw, sh, scale, hud_h, enabled=False, font_path=None):
        self.sw, self.sh, self.hud_h, self.k = sw, sh, hud_h, scale
        self.enabled = enabled          # becomes True on the first finger touch
        self.vx = 0.0
        self.vy = 0.0
        self.joy_id = None
        self.joy_r = int(95 * scale)
        self.rest_center = (int(150 * scale), sh - int(140 * scale))
        self.joy_center = self.rest_center
        self.knob = self.rest_center
        self._held = {}                 # finger_id -> button name
        k = scale
        # name: (cx, cy, radius, label, key)
        self.btns = {
            "E": (sw - int(140 * k), sh - int(150 * k), int(76 * k), "E", pygame.K_e),
            "H": (sw - int(290 * k), sh - int(95 * k), int(46 * k), "H", pygame.K_h),
            "P": (sw - int(52 * k), hud_h + int(46 * k), int(32 * k), "II", pygame.K_p),
        }
        self._build_surfaces(font_path)

    # ---------------- geometry shared with the Renderer ----------------
    def _tut_box(self):
        k = self.k
        return (self.sw // 2 - int(360 * k), self.sh - int(170 * k), int(720 * k), int(120 * k))

    def _sup_box(self):
        k = self.k
        return (self.sw // 2 - int(400 * k), self.sh // 2 - int(310 * k), int(800 * k), int(620 * k))

    def _hire_box(self):
        k = self.k
        return (self.sw // 2 - int(420 * k), self.sh // 2 - int(270 * k), int(840 * k), int(540 * k))

    def _close_btn(self, box):
        bx, by, bw, _ = box
        return (bx + bw - int(30 * self.k), by + int(30 * self.k), int(24 * self.k))

    # ---------------- input ----------------
    def _pos(self, ev):
        try:
            ww, wh = pygame.display.get_window_size()
        except Exception:
            ww, wh = self.sw, self.sh
        return map_finger(ev.x, ev.y, ww, wh, self.sw, self.sh)

    def process(self, ev, gs):
        """Handle a FINGER* event. Returns a pygame key to feed into the game, or None."""
        t = ev.type
        if t == pygame.FINGERDOWN:
            self.enabled = True
            x, y = self._pos(ev)
            return self._down(ev.finger_id, x, y, gs)
        if t == pygame.FINGERMOTION:
            if ev.finger_id == self.joy_id:
                x, y = self._pos(ev)
                self._joy_move(x, y)
            return None
        if t == pygame.FINGERUP:
            if ev.finger_id == self.joy_id:
                self._joy_release()
            self._held.pop(ev.finger_id, None)
        return None

    def _down(self, fid, x, y, gs):
        st = gs.state
        if st == "INTRO":
            return pygame.K_SPACE
        if st == "PLAY":
            if gs.tutorial < 6 and _inside(self._tut_box(), x, y):
                return pygame.K_SPACE
            pad = int(10 * self.k)
            for name, (cx, cy, r, _lbl, key) in self.btns.items():
                if _in_circle(cx, cy, r + pad, x, y):
                    self._held[fid] = name
                    return key
            if x < self.sw * 0.5 and y > self.hud_h and self.joy_id is None:
                self._joy_start(fid, x, y)
            return None
        if st == "SUPPLIER":
            box = self._sup_box()
            cx, cy, cr = self._close_btn(box)
            if _in_circle(cx, cy, cr + 8, x, y) or not _inside(box, x, y):
                return pygame.K_ESCAPE
            bx, by, bw, _ = box
            for i in range(len(gs.player.unlocked())):
                if _inside((bx + 34, by + 110 + i * 56, bw - 68, 48), x, y):
                    return pygame.K_1 + i
            return None
        if st == "HIRE":
            box = self._hire_box()
            cx, cy, cr = self._close_btn(box)
            if _in_circle(cx, cy, cr + 8, x, y) or not _inside(box, x, y):
                return pygame.K_ESCAPE
            bx, by, bw, _ = box
            for i in range(4):
                if _inside((bx + 34, by + 110 + i * 90, bw - 68, 78), x, y):
                    return pygame.K_1 + i
            return None
        return None

    # ---------------- joystick ----------------
    def _joy_start(self, fid, x, y):
        r = self.joy_r
        cx = min(max(x, r + 10), self.sw * 0.5)
        cy = min(max(y, self.hud_h + r), self.sh - r - 10)
        self.joy_id = fid
        self.joy_center = (cx, cy)
        self._joy_move(x, y)

    def _joy_move(self, x, y):
        cx, cy = self.joy_center
        dx, dy = x - cx, y - cy
        d = math.hypot(dx, dy)
        if d > self.joy_r:
            dx *= self.joy_r / d
            dy *= self.joy_r / d
            d = float(self.joy_r)
        self.knob = (cx + dx, cy + dy)
        mag = d / float(self.joy_r)
        if mag < self.DEAD or d == 0:
            self.vx = self.vy = 0.0
        else:
            m = min(1.0, mag * 1.25)
            self.vx = dx / d * m
            self.vy = dy / d * m

    def _joy_release(self):
        self.joy_id = None
        self.vx = self.vy = 0.0
        self.joy_center = self.rest_center
        self.knob = self.rest_center

    # ---------------- drawing ----------------
    def _build_surfaces(self, font_path):
        try:
            self.font = pygame.font.Font(font_path, max(14, int(26 * self.k))) if font_path \
                else pygame.font.Font(None, max(18, int(34 * self.k)))
        except Exception:
            self.font = pygame.font.Font(None, max(18, int(34 * self.k)))
        r = self.joy_r
        self.s_base = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(self.s_base, (255, 255, 255, 36), (r + 2, r + 2), r)
        pygame.draw.circle(self.s_base, (255, 255, 255, 110), (r + 2, r + 2), r, 3)
        kr = int(r * 0.42)
        self.s_knob = pygame.Surface((kr * 2 + 4, kr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(self.s_knob, (255, 255, 255, 130), (kr + 2, kr + 2), kr)
        pygame.draw.circle(self.s_knob, (255, 255, 255, 200), (kr + 2, kr + 2), kr, 3)
        colors = {"E": (60, 170, 100), "H": (230, 150, 60), "P": (90, 100, 130)}
        self.s_btn = {}
        for name, (_cx, _cy, br, label, _key) in self.btns.items():
            s = pygame.Surface((br * 2 + 4, br * 2 + 4), pygame.SRCALPHA)
            c = colors[name]
            pygame.draw.circle(s, (c[0], c[1], c[2], 150), (br + 2, br + 2), br)
            pygame.draw.circle(s, (255, 255, 255, 190), (br + 2, br + 2), br, 3)
            t = self.font.render(label, True, (255, 255, 255))
            s.blit(t, (br + 2 - t.get_width() // 2, br + 2 - t.get_height() // 2))
            self.s_btn[name] = s
        cr = int(24 * self.k)
        self.s_close = pygame.Surface((cr * 2 + 4, cr * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(self.s_close, (200, 60, 60, 230), (cr + 2, cr + 2), cr)
        pygame.draw.circle(self.s_close, (255, 255, 255, 220), (cr + 2, cr + 2), cr, 3)
        t = self.font.render("X", True, (255, 255, 255))
        self.s_close.blit(t, (cr + 2 - t.get_width() // 2, cr + 2 - t.get_height() // 2))

    def update(self, gs):
        # Drop the joystick if the game left PLAY while a finger was held
        if gs.state != "PLAY" and self.joy_id is not None:
            self._joy_release()
        if gs.state != "PLAY":
            self._held.clear()

    def draw(self, scr, gs):
        if not self.enabled:
            return
        self.update(gs)
        st = gs.state
        if st == "PLAY":
            bw = self.s_base.get_width() // 2
            scr.blit(self.s_base, (self.joy_center[0] - bw, self.joy_center[1] - bw))
            kw = self.s_knob.get_width() // 2
            scr.blit(self.s_knob, (self.knob[0] - kw, self.knob[1] - kw))
            held = set(self._held.values())
            for name, (cx, cy, r, _l, _k) in self.btns.items():
                s = self.s_btn[name]
                scr.blit(s, (cx - r - 2, cy - r - 2))
                if name in held:
                    pygame.draw.circle(scr, (255, 255, 255), (cx, cy), r + 4, 4)
        elif st == "SUPPLIER" or st == "HIRE":
            box = self._sup_box() if st == "SUPPLIER" else self._hire_box()
            cx, cy, cr = self._close_btn(box)
            scr.blit(self.s_close, (cx - cr - 2, cy - cr - 2))
        elif st == "INTRO":
            t = self.font.render("TAP TO CONTINUE >>", True, (255, 220, 120))
            scr.blit(t, (self.sw // 2 - t.get_width() // 2, self.sh - int(60 * self.k)))
