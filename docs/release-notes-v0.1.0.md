# 📝 Notas de la versión v0.1.0

Primera versión pública de **TODOFERRETERO** 🚀.  
Esta build está orientada a pruebas iniciales en Android.

---

## 📦 Archivo descargable
- **APK**: [`todoferretero-0.1.0-arm64-v8a_armeabi-v7a-debug.apk`](../bin/todoferretero-0.1.0-arm64-v8a_armeabi-v7a-debug.apk)

---

## ✅ Funcionalidades incluidas
  
    - Pantalla de Login (validación contra base SQLite).
    - Busqueda de clientes dinámicas
    - Busqueda de clientes con varios tres criterios
    - Historial de pedidos
    - Generación de identificadores para numero de serie  
    - Toma de pedidos offline.  
    - criterio de precios por región obligatorio, el usuario no puede avanzar
    - si se escoge "retiro" precios de Santiago RM
    - si se esgoe "regiro" y la region es Santiago, precios de Santiago
    - si se escoge "retiro" y la región es distinta a STGO, precios de Santiago
    - si se escoge despacho y la regioń es <> SGTO, precios de región en tabla clientes
    - si el cliente no tiene "region" y escoge despacho, se se debe escoger region
    - Busqueda de productos dinámica por nombre o sku
    - Carrito de compras con totales.
    - Historial de pedidos.  
    - Generación de PDF de pedidos.
    - La persistencia de ordenes sin terminar funciona
    - La persistencia solo mantiene una sesión guardada
    - Cuando se completa la orden, la tabla para persistencias se limpia completamente
    - Se puede escribir en la BD
    - Compatibilidad probada en Android 14 (ZTE Blade A55).  

---

## ⚠️ Limitaciones conocidas
    - APK en modo **debug** (puede mostrar mensajes adicionales).  
    - Orientación fija en **portrait**, aún no optimizado para tablets grandes.  
    - La base de datos SQLite incluida está en estado inicial.
    - Esta versión no imprime PDF porque se deshabilitó para esta compilación (pendiente de revisión)
    - Nota: El cliente no estaba preocupado de generar PDF en la primera etapa
    - En las pruebas de escrito, funciona el metodo para crear PDF  

---

## 🔜 Próximos pasos
    - Preparar versión **release firmada**.  
    - Integrar mejoras en la UI y manejo de errores.  
    - Publicar roadmap en `docs/`.
    - Trabajar en la actualización on line, escribiendo los datos de "ordenes" en servicio online
    - Trabajar en la actualización in line, leyendo datos en servicio on line y actualizar datos locals
