import jwt
from jwt.algorithms import RSAAlgorithm
import json
import urllib.request
from fastapi import HTTPException, status
from app.core.config import settings

# Cache for JWKS
jwks_cache = {}

def get_jwks():
    if jwks_cache:
        return jwks_cache
    
    if not settings.CLERK_ISSUER_URL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clerk Issuer URL not configured"
        )
        
    jwks_url = f"{settings.CLERK_ISSUER_URL}/.well-known/jwks.json"
    try:
        with urllib.request.urlopen(jwks_url) as response:
            jwks = json.loads(response.read())
            jwks_cache.update(jwks)
            return jwks
    except Exception as e:
        print(f"Failed to fetch JWKS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch JWKS"
        )

def verify_token(token: str):
    try:
        # Get the Key ID (kid) from the token header
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token header"
            )
            
        jwks = get_jwks()
        public_key = None
        
        for key in jwks["keys"]:
            if key["kid"] == kid:
                public_key = RSAAlgorithm.from_jwk(json.dumps(key))
                break
                
        if not public_key:
            # Refresh cache and try once more
            jwks_cache.clear()
            jwks = get_jwks()
            for key in jwks["keys"]:
                if key["kid"] == kid:
                    public_key = RSAAlgorithm.from_jwk(json.dumps(key))
                    break
            
            if not public_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token key"
                )
        
        # Verify the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_aud": False} # Clerk tokens might not have audience set as expected for API
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
