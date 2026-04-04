# socios/dni_utils.py
import re

def check_dni(dni: str) -> dict:
    """
    Valida el formato de un DNI español (8 dígitos + letra).
    
    Args:
        dni: Cadena con el documento a validar
        
    Returns:
        dict con el resultado de la validación
    """
    dni = dni.upper().strip()
    
    # Patrón: 8 dígitos seguidos de letra válida
    if not re.match(r'^\d{8}[A-HJ-NP-TV-Z]$', dni):
        return {
            "valido": False,
            "documento": dni,
            "error": "Formato inválido. Use: 12345678A"
        }
    
    # Validar letra (algoritmo módulo 23)
    numero = int(dni[:-1])
    letra = dni[-1]
    letras_validas = 'TRWAGMYFPDXBNJZSQVHLCKE'
    
    if letras_validas[numero % 23] != letra:
        return {
            "valido": False,
            "documento": dni,
            "error": "Letra incorrecta"
        }
    
    return {
        "valido": True,
        "documento": dni,
        "tipo": "DNI"
    }