#!/usr/bin/env python
"""
Generate self-signed SSL certificate for local development.
Run this once to create the certificate files.
"""
from OpenSSL import crypto
from pathlib import Path

def generate_self_signed_cert(cert_dir="ssl"):
    """Generate a self-signed certificate for localhost and local network."""
    
    # Create certificate directory if it doesn't exist
    cert_path = Path(__file__).parent / cert_dir
    cert_path.mkdir(exist_ok=True)
    
    # Create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    
    # Create a self-signed certificate
    cert = crypto.X509()
    cert.get_subject().C = "LT"
    cert.get_subject().ST = "Vilnius"
    cert.get_subject().L = "Vilnius"
    cert.get_subject().O = "ChorePoints Local Dev"
    cert.get_subject().OU = "Development"
    cert.get_subject().CN = "localhost"
    
    # Add Subject Alternative Names for different access methods
    cert.add_extensions([
        crypto.X509Extension(
            b"subjectAltName",
            False,
            b"DNS:localhost,DNS:*.local,IP:127.0.0.1,IP:192.168.0.35,IP:192.168.0.1"
        )
    ])
    
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for 1 year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')
    
    # Save certificate
    cert_file = cert_path / "cert.pem"
    key_file = cert_path / "key.pem"
    
    with open(cert_file, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open(key_file, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    
    print(f"✅ Certificate generated successfully!")
    print(f"📄 Certificate: {cert_file}")
    print(f"🔑 Private Key: {key_file}")
    print(f"\n⚠️  Note: This is a self-signed certificate for development only.")
    print(f"📱 On mobile devices, you may need to accept the security warning.")
    
    return cert_file, key_file

if __name__ == "__main__":
    generate_self_signed_cert()
