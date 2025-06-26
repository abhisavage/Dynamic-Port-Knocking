import pyotp
import qrcode
from io import BytesIO
import base64
import os
import json
from pathlib import Path

class TOTPManager:
    def __init__(self, secrets_file="/var/app/pks/totp_secrets.json"):
        self.secrets_file = Path(secrets_file)
        self.secrets = self._load_secrets()

    def _load_secrets(self):
        """Load existing secrets from file."""
        if self.secrets_file.exists():
            with open(self.secrets_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_secrets(self):
        """Save secrets to file."""
        with open(self.secrets_file, 'w') as f:
            json.dump(self.secrets, f, indent=4)

    def user_has_secret(self, user_id: str) -> bool:
        """Check if a user already has a TOTP secret."""
        return user_id in self.secrets

    def generate_secret_for_user(self, user_id: str) -> tuple:
        """Generate a new TOTP secret and QR code for a user."""
        secret = pyotp.random_base32()
        self.secrets[user_id] = secret
        self._save_secrets()

        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=f"PKS User: {user_id}",
            issuer_name="PKS-Server"
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        
        return buffered.getvalue()

    def verify_totp(self, user_id: str, token: str) -> bool:
        """Verify a TOTP token for a user."""
        if user_id not in self.secrets:
            return False
        
        totp = pyotp.TOTP(self.secrets[user_id])
        return totp.verify(token)

    def remove_secret(self, user_id: str):
        """Remove a TOTP secret for a user."""
        if user_id in self.secrets:
            del self.secrets[user_id]
            self._save_secrets() 