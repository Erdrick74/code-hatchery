#!/usr/bin/env python3
import os
import shutil
import subprocess
import threading
from datetime import datetime
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gdk, GLib, Gtk, GtkLayerShell

TEMPLATES = [
    "python",
    "python-github-ready",
    "node-ts",
    "go",
    "rust",
    "java",
    "cpp",
    "csharp",
    "php",
    "lua",
]
DEFAULT_BASE = os.path.expanduser("~/Chronos/projects")
SCRIPT_DIR = Path(__file__).resolve().parent
CREATE_SCRIPT = SCRIPT_DIR / "create-project.sh"
GUI_LOGFILE = Path("/tmp/code-hatchery-gui.log")
APP_NAME = "Code Hatchery"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Erdrick74"


class DevCreateGtkApp:
    def __init__(self, open_after: bool, include_meta: bool):
        self.open_after = open_after
        self.include_meta = include_meta
        self.worker = None
        self._browse_dialog = None

        self.window = Gtk.Window(title=f"{APP_NAME} v{APP_VERSION}")
        self.window.set_name("devcreate-overlay")
        self.window.set_decorated(False)
        self.window.set_keep_above(True)
        self.window.connect("delete-event", self._on_close)
        self.window.connect("key-press-event", self._on_key_press)
        self.window.connect("focus-out-event", self._on_focus_out)
        self.window.connect("map-event", self._on_map)

        GtkLayerShell.init_for_window(self.window)
        GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.ON_DEMAND)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.RIGHT, True)

        self._apply_css()
        self._build_ui()
        self._set_busy(False)

        self.window.show_all()
        self._focus_project_initial()
        self._log("GUI started")

    def _focus_project_initial(self) -> None:
        # Initial focus should not select text, otherwise future keypresses can replace content.
        if hasattr(self.project_entry, "grab_focus_without_selecting"):
            self.project_entry.grab_focus_without_selecting()
        else:
            self.project_entry.grab_focus()

    def _log(self, msg: str) -> None:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with GUI_LOGFILE.open("a", encoding="utf-8") as f:
            f.write(f"[{stamp}] {msg}\n")

    def _set_error(self, msg: str, focus: str | None = None) -> None:
        self._set_status(msg)
        self._log(f"validation_error: {msg}")
        if focus == "project":
            self.project_entry.grab_focus()
        elif focus == "base":
            self.base_entry.grab_focus()

    def _apply_css(self) -> None:
        css = b"""
        #devcreate-overlay {
          background-color: rgba(16, 18, 20, 0.28);
        }

        #devcreate-card {
          background-color: @theme_base_color;
          border-radius: 12px;
          border: 2px solid #00ffff;
        }

        #devcreate-card > box {
          padding: 12px;
        }

        #devcreate-header-title {
          font-weight: 700;
          font-size: 1.05em;
        }

        #devcreate-header-user {
          opacity: 0.85;
        }

        #dev-template-combo,
        #dev-template-combo button,
        #dev-template-combo box,
        #dev-template-combo cellview {
          background-color: #ffffff;
          color: #000000;
        }

        #dev-create-button,
        #dev-confirm-yes {
          background-color: #2b5fb3;
          background-image: none;
          color: #ffffff;
          border-color: #8fb3ff;
        }

        #dev-create-button:focus,
        #dev-create-button:active,
        #dev-confirm-yes:focus,
        #dev-confirm-yes:active {
          background-color: #3b74d1;
          background-image: none;
          color: #ffffff;
          border-color: #b8d2ff;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _build_ui(self) -> None:
        # EventBox gives us an input surface for the entire overlay so clicks
        # outside the card are consumed instead of reaching other windows.
        self.capture = Gtk.EventBox()
        self.capture.set_visible_window(False)
        # Let child widgets handle input normally; background clicks are still captured.
        self.capture.set_above_child(False)
        self.window.add(self.capture)

        overlay = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.capture.add(overlay)

        top_spacer = Gtk.Box()
        top_spacer.set_vexpand(True)
        overlay.pack_start(top_spacer, True, True, 0)

        center_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        center_row.set_halign(Gtk.Align.CENTER)
        overlay.pack_start(center_row, False, False, 0)

        card = Gtk.Frame()
        card.set_name("devcreate-card")
        card.set_shadow_type(Gtk.ShadowType.NONE)
        card.set_size_request(640, -1)
        center_row.pack_start(card, False, False, 0)

        card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.add(card_box)

        header_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        card_box.pack_start(header_row, False, False, 0)

        header_icon = Gtk.Image.new_from_icon_name("code-hatchery", Gtk.IconSize.DIALOG)
        header_icon.set_pixel_size(40)
        if header_icon.get_storage_type() == Gtk.ImageType.EMPTY:
            icon_fallback = Path.home() / ".local/share/icons/hicolor/128x128/apps/code-hatchery.png"
            if icon_fallback.is_file():
                header_icon.set_from_file(str(icon_fallback))
        header_row.pack_start(header_icon, False, False, 0)

        header_line = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header_row.pack_start(header_line, True, True, 0)

        header_title = Gtk.Label(label=f"{APP_NAME} v{APP_VERSION}")
        header_title.set_name("devcreate-header-title")
        header_title.set_xalign(0.0)
        header_title.set_hexpand(True)
        header_line.pack_start(header_title, True, True, 0)

        header_user = Gtk.Label(label=APP_AUTHOR)
        header_user.set_name("devcreate-header-user")
        header_user.set_xalign(1.0)
        header_line.pack_end(header_user, False, False, 0)

        grid = Gtk.Grid(column_spacing=8, row_spacing=6)
        card_box.pack_start(grid, False, False, 0)

        template_label = Gtk.Label(label="Template")
        template_label.set_xalign(0.0)
        grid.attach(template_label, 0, 0, 1, 1)

        self.template_combo = Gtk.ComboBoxText()
        self.template_combo.set_name("dev-template-combo")
        for t in TEMPLATES:
            self.template_combo.append_text(t)
        self.template_combo.set_active(0)
        self.template_combo.connect("changed", self._on_template_changed)
        self.template_combo.connect("notify::popup-shown", self._on_template_popup_shown)
        self.template_combo.connect("notify::active", self._on_template_active_notify)
        grid.attach(self.template_combo, 1, 0, 1, 1)
        self._log("template_dropdown_ready")

        project_label = Gtk.Label(label="Project name")
        project_label.set_xalign(0.0)
        grid.attach(project_label, 0, 1, 1, 1)

        self.project_entry = Gtk.Entry()
        self.project_entry.set_hexpand(True)
        self.project_entry.connect("activate", lambda _e: self._start())
        grid.attach(self.project_entry, 1, 1, 1, 1)

        base_label = Gtk.Label(label="Base directory")
        base_label.set_xalign(0.0)
        grid.attach(base_label, 0, 2, 1, 1)

        base_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.base_entry = Gtk.Entry()
        self.base_entry.set_text(DEFAULT_BASE)
        self.base_entry.set_hexpand(True)
        self.base_entry.connect("activate", lambda _e: self._start())
        base_row.pack_start(self.base_entry, True, True, 0)

        self.browse_btn = Gtk.Button(label="Browse")
        self.browse_btn.connect("clicked", self._browse_dir)
        base_row.pack_start(self.browse_btn, False, False, 0)
        grid.attach(base_row, 1, 2, 1, 1)

        self.open_check = Gtk.CheckButton(label="Open in VS Code when done")
        self.open_check.set_active(True)
        grid.attach(self.open_check, 1, 3, 1, 1)

        self.meta_check = Gtk.CheckButton(label="Include open-source metadata files")
        self.meta_check.set_active(self.include_meta)
        grid.attach(self.meta_check, 1, 4, 1, 1)

        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_xalign(0.0)
        card_box.pack_start(self.status_label, False, False, 0)

        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        card_box.pack_start(btn_row, False, False, 0)

        self.create_btn = Gtk.Button(label="Create Project")
        self.create_btn.set_name("dev-create-button")
        self.create_btn.connect("clicked", lambda _b: self._start())
        btn_row.pack_end(self.create_btn, False, False, 0)

        bottom_spacer = Gtk.Box()
        bottom_spacer.set_vexpand(True)
        overlay.pack_start(bottom_spacer, True, True, 0)

    def _enforce_focus(self) -> bool:
        self.window.present()
        # Keep the layer-shell surface focused, but do not force focus back to
        # the project entry on every cycle (that can cause text replacement while typing).
        self.window.grab_focus()
        return False

    def _on_map(self, *_args) -> bool:
        GLib.idle_add(self._enforce_focus)
        return False

    def _on_focus_out(self, *_args) -> bool:
        # Do not force-focus on focus-out: combobox popups use separate surfaces
        # and this can cancel selection changes before they commit.
        return False

    def _on_background_input(self, *_args) -> bool:
        # Do not swallow pointer events; swallowing can interfere with combobox popup selection.
        return False

    def _on_key_press(self, _widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        if event.keyval == Gdk.KEY_Escape:
            self._log("key:escape -> close")
            Gtk.main_quit()
            return True
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self._log("key:enter -> start")
            self._start()
            return True
        return False

    def _on_close(self, *_args) -> bool:
        self._log("window close")
        Gtk.main_quit()
        return False

    def _browse_dir(self, _button: Gtk.Button) -> None:
        if self._browse_dialog is not None:
            self._log("browse toggle -> close chooser")
            self._browse_dialog.destroy()
            return

        dialog = Gtk.FileChooserDialog(
            title="Select base directory",
            parent=self.window,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK)
        dialog.set_modal(False)

        current = os.path.expanduser(self.base_entry.get_text().strip() or DEFAULT_BASE)
        if os.path.isdir(current):
            dialog.set_filename(current)

        def on_response(dlg: Gtk.FileChooserDialog, response: int) -> None:
            if response == Gtk.ResponseType.OK:
                chosen = dlg.get_filename()
                if chosen:
                    self.base_entry.set_text(chosen)
            dlg.destroy()

        def on_destroy(_dlg: Gtk.FileChooserDialog) -> None:
            self._browse_dialog = None

        dialog.connect("response", on_response)
        dialog.connect("destroy", on_destroy)

        self._browse_dialog = dialog
        dialog.show_all()

    def _set_busy(self, busy: bool) -> None:
        enabled = not busy
        self.template_combo.set_sensitive(enabled)
        self.project_entry.set_sensitive(enabled)
        self.base_entry.set_sensitive(enabled)
        self.browse_btn.set_sensitive(enabled)
        self.open_check.set_sensitive(enabled)
        self.meta_check.set_sensitive(enabled)
        self.create_btn.set_sensitive(enabled)

    def _on_template_changed(self, combo: Gtk.ComboBoxText) -> None:
        template = combo.get_active_text() or ""
        self._log(f"template_changed value={template}")

    def _on_template_popup_shown(self, combo: Gtk.ComboBoxText, _pspec) -> None:
        shown = combo.get_property("popup-shown")
        self._log(
            f"template_popup_shown={shown} active={combo.get_active()} text={combo.get_active_text() or ''}"
        )

    def _on_template_active_notify(self, combo: Gtk.ComboBoxText, _pspec) -> None:
        self._log(f"template_active_notify active={combo.get_active()} text={combo.get_active_text() or ''}")

    def _set_status(self, text: str) -> bool:
        self.status_label.set_text(text)
        return False

    def _show_message(self, message_type: Gtk.MessageType, title: str, body: str) -> None:
        self._log(f"message {title}: {body}")
        # Avoid modal dialogs in layer-shell mode: they can trap input and look frozen.
        self._set_status(f"{title}: {body}")
        if command_exists("notify-send"):
            subprocess.Popen(["notify-send", title, body], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _confirm_create(self, template: str, project_path: str, include_meta: bool) -> bool:
        self._log(f"confirm shown template={template} path={project_path}")
        result = {"confirmed": False}
        loop = GLib.MainLoop()

        self.window.set_sensitive(False)

        confirm = Gtk.Window(title="Code Hatchery")
        confirm.set_name("devcreate-overlay")
        confirm.set_decorated(False)
        confirm.set_keep_above(True)

        GtkLayerShell.init_for_window(confirm)
        GtkLayerShell.set_layer(confirm, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(confirm, GtkLayerShell.KeyboardMode.ON_DEMAND)
        GtkLayerShell.set_anchor(confirm, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(confirm, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(confirm, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(confirm, GtkLayerShell.Edge.RIGHT, True)

        capture = Gtk.EventBox()
        capture.set_visible_window(False)
        capture.set_above_child(False)
        capture.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
        capture.connect("button-press-event", lambda *_: True)
        capture.connect("button-release-event", lambda *_: True)
        confirm.add(capture)

        overlay = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        capture.add(overlay)

        top_spacer = Gtk.Box()
        top_spacer.set_vexpand(True)
        overlay.pack_start(top_spacer, True, True, 0)

        center_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        center_row.set_halign(Gtk.Align.CENTER)
        overlay.pack_start(center_row, False, False, 0)

        card = Gtk.Frame()
        card.set_name("devcreate-card")
        card.set_shadow_type(Gtk.ShadowType.NONE)
        card.set_size_request(560, -1)
        center_row.pack_start(card, False, False, 0)

        card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.add(card_box)

        title = Gtk.Label(label="Create project?")
        title.set_xalign(0.0)
        card_box.pack_start(title, False, False, 0)

        meta_text = "Yes" if include_meta else "No"
        detail = Gtk.Label(
            label=f"Template: {template}\nPath: {project_path}\nInclude metadata: {meta_text}"
        )
        detail.set_xalign(0.0)
        card_box.pack_start(detail, False, False, 0)

        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        card_box.pack_start(btn_row, False, False, 0)

        no_btn = Gtk.Button(label="No")
        yes_btn = Gtk.Button(label="Yes")
        yes_btn.set_name("dev-confirm-yes")

        def finish(confirmed: bool) -> None:
            result["confirmed"] = confirmed
            if loop.is_running():
                loop.quit()
            confirm.destroy()

        no_btn.connect("clicked", lambda *_: finish(False))
        yes_btn.connect("clicked", lambda *_: finish(True))
        btn_row.pack_end(yes_btn, False, False, 0)
        btn_row.pack_end(no_btn, False, False, 0)

        def on_key_press(_w: Gtk.Widget, event: Gdk.EventKey) -> bool:
            if event.keyval == Gdk.KEY_Escape:
                finish(False)
                return True
            if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                finish(True)
                return True
            return False

        confirm.connect("key-press-event", on_key_press)
        confirm.connect("delete-event", lambda *_: (finish(False), True)[1])

        bottom_spacer = Gtk.Box()
        bottom_spacer.set_vexpand(True)
        overlay.pack_start(bottom_spacer, True, True, 0)

        confirm.show_all()
        yes_btn.grab_focus()
        loop.run()
        self.window.set_sensitive(True)
        self._focus_project_initial()

        confirmed = result["confirmed"]
        self._log(f"confirm response confirmed={confirmed}")
        return confirmed

    def _run_command(self, cmd: list[str], cwd: str | None = None) -> int:
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        assert process.stdout is not None
        for _ in process.stdout:
            pass

        return process.wait()

    def _start(self) -> None:
        self._log("start requested")
        if self.worker and self.worker.is_alive():
            self._log("ignored: worker already running")
            return

        template = self.template_combo.get_active_text() or ""
        self._log(
            f"start_template_state active={self.template_combo.get_active()} value={template}"
        )
        if template not in TEMPLATES:
            self._set_error("Please select a valid template.")
            return

        project_name = self.project_entry.get_text().strip()
        if not project_name:
            self._set_error("Project name cannot be empty.", focus="project")
            return

        base_dir = os.path.expanduser(self.base_entry.get_text().strip() or DEFAULT_BASE)
        project_path = os.path.join(base_dir.rstrip("/"), project_name)
        self._log(f"template={template} path={project_path}")

        if os.path.exists(project_path):
            self._set_error(f"Path already exists: {project_path}", focus="project")
            return

        include_meta = self.meta_check.get_active()
        if not self._confirm_create(template, project_path, include_meta):
            self._set_status("Cancelled.")
            self._log("creation cancelled")
            return

        self._set_busy(True)
        self._set_status("Creating project...")
        self._log("creation started")

        def worker() -> None:
            try:
                os.makedirs(base_dir, exist_ok=True)
                create_cmd = [str(CREATE_SCRIPT), template, project_path]
                if include_meta:
                    create_cmd.append("--oss-meta")
                rc = self._run_command(create_cmd)
                if rc != 0:
                    self._log(f"create-project failed rc={rc}")
                    GLib.idle_add(self._finish, False, "Create step failed.")
                    return

                rc = self._run_command(["./bootstrap.sh"], cwd=project_path)
                if rc != 0:
                    self._log(f"bootstrap failed rc={rc}")
                    GLib.idle_add(self._finish, False, "Bootstrap failed.")
                    return

                if self.open_check.get_active() and shutil.which("code"):
                    candidate_tabs = [
                        os.path.join(project_path, "README.md"),
                        os.path.join(project_path, "src", "main.py"),
                        os.path.join(project_path, "src", "main.rs"),
                        os.path.join(project_path, "src", "main.go"),
                        os.path.join(project_path, "main.go"),
                        os.path.join(project_path, "main.py"),
                    ]
                    first_file = next((p for p in candidate_tabs if os.path.isfile(p)), "")
                    subprocess.Popen(
                        ["code", "--reuse-window", "--add", project_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    if first_file:
                        subprocess.Popen(
                            ["code", "--reuse-window", "--goto", f"{first_file}:1"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    self._log(f"opened in vscode add={project_path} tab={first_file or 'none'}")
                else:
                    self._log("skipped vscode open (unchecked or code not found)")
                    self._log("creation finished successfully")
                    GLib.idle_add(self._finish, True, f"Done: {project_path}")
                    return

                self._log("creation finished successfully")
                GLib.idle_add(self._finish, True, f"Done: {project_path}")
            except Exception as exc:
                self._log(f"unexpected exception: {exc}")
                GLib.idle_add(self._finish, False, "Unexpected error.")

        self.worker = threading.Thread(target=worker, daemon=True)
        self.worker.start()

    def _finish(self, ok: bool, status: str) -> bool:
        self._set_status(status)
        self._set_busy(False)
        if ok:
            self._log("success -> closing gui")
            Gtk.main_quit()
        else:
            self._show_message(Gtk.MessageType.ERROR, "Code Hatchery", status)
        return False


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def main() -> int:
    open_after = "--no-open" not in os.sys.argv[1:]
    include_meta = "--no-oss-meta" not in os.sys.argv[1:]
    app = DevCreateGtkApp(open_after=open_after, include_meta=include_meta)
    Gtk.main()
    del app
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
