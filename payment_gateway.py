# Simulación de una pasarela de pago
def procesar_pago(usuario_id, monto):
    """Simula el procesamiento de un pago."""
    print(f"Procesando pago de ${monto} para usuario {usuario_id}...")
    return {"estado": "exitoso", "monto": monto, "usuario_id": usuario_id}
