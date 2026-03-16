# Plantilla de Email Cross-Client - Super Pack Agustín Laje

## Archivos generados

1. **agustin2.html** - Plantilla base con marcadores de posición `{VARIABLE}`
2. **agustin_ejemplo.html** - Ejemplo completo con contenido real

## Paleta de colores extraída de la imagen

- **Azul marino principal**: #1A3A5C (fondos, texto principal)
- **Naranja corporativo**: #E6653A (botones CTA, destacados)
- **Verde/amarillo acento**: #C4D843 (usado en "Globalismo", botón secundario)
- **Blanco**: #FFFFFF (textos sobre fondos oscuros)
- **Grises**: #f8f8f8, #cccccc, #666666 (fondos secundarios, textos)

## Características técnicas implementadas

### ✅ Compatibilidad Cross-Client
- **Layout basado en tablas** con `role="presentation"`
- **Estilos inline** en todos los elementos críticos
- **Media queries** solo para responsive básico
- **Soporte Outlook** con comentarios condicionales MSO
- **Dark mode friendly** con meta tags apropiados

### ✅ Botones "Bulletproof"
```html
<table role="presentation">
    <tr>
        <td style="background-color: #E6653A; padding: 15px 35px; border-radius: 30px;">
            <a href="#" style="color: #ffffff; text-decoration: none;">TEXTO</a>
        </td>
    </tr>
</table>
```

### ✅ Responsive Design
- **Ancho máximo**: 600px en desktop
- **Apilado automático** en móvil (<600px)
- **Padding ajustable** con clases móviles
- **Imágenes fluidas** con max-width: 100%

### ✅ Accesibilidad
- `lang="es"` declarado
- **Alt text** en todas las imágenes
- **Tamaños de fuente** mínimo 14px
- **Contraste adecuado** en todos los elementos

## Secciones incluidas

1. **Preheader** (85 caracteres máximo)
2. **Header** con logo corporativo
3. **Hero section** con título, precio y CTA principal
4. **Contenido principal** con lista de beneficios
5. **Productos** (dos columnas responsive)
6. **Información de contacto**
7. **Segundo CTA**
8. **Footer completo** con redes y legal

## Variables a reemplazar en agustin2.html

### Contenido principal
- `{TITULO_EMAIL}` - Título del email
- `{PREHEADER_TEXT}` - Texto preview (máx. 85 chars)
- `{TITULO_PRINCIPAL}` - H1 del hero
- `{SUBTITULO_DESTACADO}` - Caja naranja destacada
- `{DESCRIPCION_HERO}` - Párrafo explicativo
- `{PRECIO_ANTERIOR}` - Precio tachado
- `{PRECIO_ACTUAL}` - Precio en oferta
- `{TEXTO_BOTON_PRINCIPAL}` - CTA principal
- `{URL_CTA}` - Enlace del botón principal

### Imágenes
- `{LOGO_URL}` - Logo del header
- `{IMAGEN_PRODUCTO_1}` - Imagen primer libro
- `{IMAGEN_PRODUCTO_2}` - Imagen segundo libro
- `{LOGO_FOOTER_URL}` - Logo del footer

### Contacto y legal
- `{TELEFONO_CONTACTO}` - Número de teléfono
- `{URL_DESUSCRIBIR}` - Link de desuscripción
- `{DIRECCION_EMPRESA}` - Dirección física

## Limitaciones y consideraciones

### ⚠️ Outlook específico
- **No usar `background-image`** sin fallback VML
- **Evitar `border-radius`** en Outlook 2016/2019 (degradación aceptable)
- **Padding en `<td>`** en lugar de márgenes

### ⚠️ Imágenes
- **URLs absolutas obligatorias** para ESP
- **Dimensiones fijas** (width/height) requeridas
- **Alt text descriptivo** para accesibilidad
- **Formato recomendado**: PNG para logos, JPG para fotos

### ⚠️ Testing recomendado
- **Litmus** o **Email on Acid** para testing masivo
- **Clients principales**:
  - Outlook 2016/2019/365 (Windows)
  - Outlook para Mac
  - Gmail (web/móvil/app)
  - Apple Mail (iOS/macOS)
  - Yahoo Mail
  - Samsung Email

## Instrucciones de uso

### Para ESP (Email Service Provider)
1. Reemplazar todas las variables `{VARIABLE}` con contenido real
2. Subir imágenes a CDN con URLs absolutas
3. Configurar tracking de links si es necesario
4. Testear en múltiples clientes antes del envío

### Para personalización
- **Colores**: Cambiar los valores hexadecimales en línea
- **Fuentes**: Mantener Arial como fallback universal
- **Estructura**: Modificar content dentro de `<td>` existentes

## Optimizaciones adicionales

### Tamaño del archivo
- **HTML minificado**: ~15-20KB
- **Carga de imágenes**: Lazy loading automático en clientes
- **Peso total recomendado**: <100KB con imágenes

### Deliverability
- **Ratio texto/imagen**: 80/20 mantenido
- **Links trackeable**: Configurar en ESP
- **Autenticación**: SPF/DKIM/DMARC configurados en dominio

---

**Fecha de creación**: 2025-08-14
**Versión**: 1.0
**Compatibilidad**: Outlook 2016+, Gmail, Apple Mail, Yahoo Mail, clientes móviles
