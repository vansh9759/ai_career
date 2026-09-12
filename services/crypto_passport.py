import hmac
import hashlib
import json
import base64
from datetime import datetime
from flask import current_app

class CryptoPassportEngine:
    """
    Cryptographic Skill Passport Service providing HMAC-SHA256 signed skill credentials
    and tamper-evident public verification tokens.
    """

    @staticmethod
    def get_secret_key():
        try:
            secret = current_app.config.get('SECRET_KEY', 'AIResumeAnalyzerSecretKey')
        except RuntimeError:
            secret = 'AIResumeAnalyzerSecretKey'
        return secret.encode('utf-8')

    @classmethod
    def generate_credential(cls, user_id, skill_name, score=85, issuer="CAREER_OS_AI"):
        timestamp = datetime.utcnow().isoformat()
        prefix = skill_name.replace(" ", "").upper()[:4]
        raw_msg = f"{user_id}:{skill_name}:{score}:{timestamp}:{issuer}"
        
        secret = cls.get_secret_key()
        signature = hmac.new(secret, raw_msg.encode('utf-8'), hashlib.sha256).hexdigest()
        credential_id = f"VERIFIED-{prefix}-{signature[:8].upper()}"

        payload = {
            "credential_id": credential_id,
            "user_id": user_id,
            "skill_name": skill_name,
            "score": score,
            "issuer": issuer,
            "timestamp": timestamp,
            "signature": signature
        }
        return payload

    @classmethod
    def verify_signature(cls, user_id, skill_name, score, timestamp, issuer, signature):
        raw_msg = f"{user_id}:{skill_name}:{score}:{timestamp}:{issuer}"
        secret = cls.get_secret_key()
        expected = hmac.new(secret, raw_msg.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def generate_qr_svg(verification_url):
        encoded_url = base64.b64encode(verification_url.encode('utf-8')).decode('utf-8')
        qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={verification_url}"
        svg_code = f'''
        <div class="qr-code-container text-center p-3 bg-dark rounded border border-cyan" style="display:inline-block;">
            <img src="{qr_api_url}" alt="Verification QR Code" width="160" height="160" class="img-fluid rounded border shadow" onerror="this.onerror=null; this.src='https://chart.googleapis.com/chart?chs=160x160&cht=qr&chl={encoded_url}&choe=UTF-8';" />
            <p class="mt-2 text-cyan font-monospace small mb-0"><i class="bi bi-shield-check me-1"></i> Scan to Verify Credential</p>
        </div>
        '''
        return svg_code
