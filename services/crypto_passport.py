import hmac
import hashlib
import json
import base64
from datetime import datetime, timezone
from flask import current_app
from database import db
from models import VerifiedSkill, UserCredential, AuditLog

class CryptoPassportEngine:
    """
    Cryptographic Skill Passport Service providing HMAC-SHA256 signed skill credentials
    with Key ID embedding, HMAC Key Rotation Registry, and Credential Revocation capabilities.
    """

    CURRENT_KEY_ID = "K1"

    KEY_REGISTRY = {
        "K1": "AIResumeAnalyzerSecretKey_V1_2026",
        "K2": "AIResumeAnalyzerSecretKey_V2_Rotation_2026"
    }

    @classmethod
    def get_secret_key(cls, key_id=None):
        target_kid = key_id or cls.CURRENT_KEY_ID
        if target_kid in cls.KEY_REGISTRY:
            return cls.KEY_REGISTRY[target_kid].encode('utf-8')
        
        try:
            secret = current_app.config.get('SECRET_KEY', 'AIResumeAnalyzerSecretKey')
        except RuntimeError:
            secret = 'AIResumeAnalyzerSecretKey'
        
        return f"{secret}:{target_kid}".encode('utf-8')

    @classmethod
    def generate_credential(cls, user_id, skill_name, score=85, issuer="CAREER_OS_AI", key_id=None):
        kid = key_id or cls.CURRENT_KEY_ID
        timestamp = datetime.now(timezone.utc).isoformat()
        prefix = skill_name.replace(" ", "").upper()[:4]
        raw_msg = f"{user_id}:{skill_name}:{score}:{timestamp}:{issuer}:{kid}"
        
        secret = cls.get_secret_key(kid)
        signature = hmac.new(secret, raw_msg.encode('utf-8'), hashlib.sha256).hexdigest()
        credential_id = f"VERIFIED-{prefix}-{kid}-{signature[:8].upper()}"

        payload = {
            "credential_id": credential_id,
            "key_id": kid,
            "user_id": user_id,
            "skill_name": skill_name,
            "score": score,
            "issuer": issuer,
            "timestamp": timestamp,
            "signature": signature,
            "is_revoked": False
        }
        return payload

    @classmethod
    def verify_signature(cls, user_id, skill_name, score, timestamp, issuer, signature, key_id=None):
        kid = key_id or cls.CURRENT_KEY_ID
        raw_msg = f"{user_id}:{skill_name}:{score}:{timestamp}:{issuer}:{kid}"
        secret = cls.get_secret_key(kid)
        expected = hmac.new(secret, raw_msg.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    @classmethod
    def extract_key_id(cls, badge_code):
        """Extracts Key ID (e.g. K1, K2) embedded within credential badge code string."""
        if not badge_code:
            return cls.CURRENT_KEY_ID
        parts = badge_code.split('-')
        if len(parts) >= 4 and parts[2].startswith('K'):
            return parts[2]
        elif len(parts) >= 3 and parts[1].startswith('K'):
            return parts[1]
        return cls.CURRENT_KEY_ID

    @classmethod
    def revoke_credential(cls, badge_code, admin_id=None, reason="Security Policy Revocation"):
        """Revokes a skill credential, marking it invalid across public verification checks."""
        skill = VerifiedSkill.query.filter_by(badge_code=badge_code).first()
        cred = UserCredential.query.filter_by(credential_id=badge_code).first()

        now = datetime.utcnow()
        revoked = False

        if skill:
            skill.is_revoked = True
            skill.revoked_at = now
            revoked = True
        
        if cred:
            cred.is_revoked = True
            cred.revoked_at = now
            revoked = True

        if revoked:
            audit = AuditLog(
                admin_id=admin_id,
                admin_name="Security Admin" if admin_id else "System Security Engine",
                action="Revoke Credential",
                target_type="VerifiedSkill",
                target_id=badge_code,
                details=f"Badge '{badge_code}' revoked. Reason: {reason}"
            )
            db.session.add(audit)
            db.session.commit()
            return True, f"Credential '{badge_code}' has been successfully revoked."
        
        return False, f"Credential badge '{badge_code}' not found in system records."

    @staticmethod
    def generate_qr_svg(verification_url):
        encoded_url = base64.b64encode(verification_url.encode('utf-8')).decode('utf-8')
        qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={verification_url}"
        svg_code = f'''
        <div class="qr-code-container text-center p-3 bg-dark rounded border border-cyan" style="display:inline-block;">
            <img src="{qr_api_url}" alt="Verification QR Code" width="160" height="160" class="img-fluid rounded border shadow" onerror="this.onerror=null; this.src='https://chart.googleapis.com/chart?chs=160x160&cht=qr&chl={encoded_url}&choe=UTF-8';" />
            <p class="mt-2 text-cyan font-monospace small mb-0"><i class="bi bi-shield-check me-1"></i> Scan to Verify Cryptographic Passport</p>
        </div>
        '''
        return svg_code
