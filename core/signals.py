"""Signal autentikasi → Catatan Audit (login / logout / login gagal)."""
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

from .audit import log_action


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    log_action(request, "Login", f"{user} berhasil masuk.")


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    pelaku = str(user) if user else "Pengguna"
    log_action(request, "Logout", f"{pelaku} keluar.")


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request=None, **kwargs):
    username = credentials.get("username") or "?"
    log_action(request, "Login gagal", f"Percobaan login gagal untuk '{username}'.")
