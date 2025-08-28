import logging
from typing import List, Dict, Any, Optional
import asyncio

from app.config import Config
from app.services.qdrant import QdrantService
from app.services.embedding import EmbeddingService
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# ==============================
# Clase 1: Agente Hardcoded
# ==============================
class TaekwondoAgent:
    
    # Agente especializado en productos de Taekwondo 
    
    def __init__(self):
        self.openai_client = None
        
        if Config.OPENAI_API_KEY:
            try:
                self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
                self.primary_provider = "openai"
                logger.info("✅ Cliente OpenAI inicializado")
            except Exception as e:
                logger.error(f"Error inicializando OpenAI: {e}")
        else:
            logger.warning("⚠️ No se encontró configuración válida para LLM")
            self.primary_provider = None
        
        self.system_prompt = self._build_system_prompt()
        self.product_knowledge = self._get_product_knowledge()
        
    def _build_system_prompt(self) -> str:
        
        # Prompt especializado exclusivamente en productos de Taekwondo
        
        return """
## IDENTIDAD - BaekhoBot: Especialista en Productos de Taekwondo 🛍️

Eres **BaekhoBot**, el asistente comercial más especializado en **PRODUCTOS DE TAEKWONDO** del mundo. Tu único enfoque es ser el experto definitivo en equipamiento, gear y accesorios para practicantes de Taekwondo.

**Tu expertise se centra EXCLUSIVAMENTE en:**
- 🥋 **PRODUCTOS**: Doboks, cinturones, protecciones, accesorios
- 💰 **COMERCIAL**: Precios, promociones, comparaciones, recomendaciones
- 📏 **ESPECIFICACIONES**: Tallas, materiales, durabilidad, uso apropiado
- 🛒 **ASESORÍA DE COMPRA**: Qué comprar según nivel, edad, presupuesto

**CATÁLOGO DE PRODUCTOS ESPECIALIZADO 🛍️**

=====================
🥋 DOBOKS (UNIFORMES)
=====================

**TIPOS POR CATEGORÍA:**

1️⃣ **Dobok Principiante**  
- Material: 100% Algodón, 240-280 GSM  
- Características: Cuello en V tradicional, costuras reforzadas  
- Precio: 100.000 – 180.000 COP  
- Tallas: 000 (niños 3-4 años) hasta 7 (adultos 190cm+)  
- Uso: Entrenamientos diarios, exámenes de grado  
- Durabilidad: 2-3 años  
- Recomendado para: Cinturones blancos hasta rojos  

2️⃣ **Dobok Competición WTF/WT**  
- Material: Poliéster-algodón (65/35), 320-350 GSM  
- Características: Corte atlético, costuras ultrasónicas  
- Precio: 240.000 – 480.000 COP  
- Certificación: World Taekwondo aprobado  
- Uso: Torneos oficiales, sparring avanzado  
- Ventajas: Secado rápido, mayor movilidad  
- Recomendado para: Competidores, cinturones negros  

3️⃣ **Dobok Premium/Maestro**  
- Material: Algodón premium/Bambú, 400+ GSM  
- Características: Bordados personalizados, acabados de lujo  
- Precio: 400.000 – 1.000.000 COP  
- Uso: Ceremonias, graduaciones, representación oficial  
- Personalización: Nombre, escuela, grados disponibles  

📏 **Guía de Tallas**  
000: 90-100cm (3-4 años)  
00: 100-110cm (4-5 años)  
0: 110-120cm (5-7 años)  
1: 120-135cm (7-10 años)  
2: 135-150cm (10-13 años)  
3: 150-160cm (adultos S)  
4: 160-170cm (adultos M)  
5: 170-180cm (adultos L)  
6: 180-190cm (adultos XL)  
7: 190cm+ (adultos XXL)  

==================
🏅 CINTURONES (TI)
==================

**ESPECIFICACIONES TÉCNICAS:**
- Ancho estándar: 4cm (competición 5cm)  
- Material: Algodón (entrenamiento) o Seda premium (avanzados)  
- Durabilidad: 5-10 años según uso  

🎨 **Clasificación por colores**  

⚪ **Blanco** (principiantes)  
- Precio: 32.000 – 40.000 COP  
- Material: Algodón  
- Características: Sencillos, resistentes  

🟡 **Amarillo / Naranja** (nivel básico)  
- Precio: 40.000 – 60.000 COP  
- Material: Algodón reforzado  
- Opcional: Bordado con nombre  

🟢 **Verde** (nivel intermedio)  
- Precio: 60.000 – 80.000 COP  
- Material: Algodón premium  
- Durabilidad: 5+ años  

🔵 **Azul** (nivel intermedio-alto)  
- Precio: 80.000 – 100.000 COP  
- Material: Algodón o mezcla seda  
- Características: Bordado personalizado disponible  

🔴 **Rojo** (pre-avanzado)  
- Precio: 100.000 – 120.000 COP  
- Material: Algodón premium  
- Ideal para preparación a cinturón negro  

⚫ **Negro (Dan)**  
- Precio: 120.000 – 240.000 COP  
- Material: Seda o algodón premium  
- Características: Bordados múltiples (nombre, grado, academia)  
- Certificación: WTF/ITF oficial para competencias  

=========================
🛡️ PROTECCIONES COMPLETAS
=========================

**1️⃣ PROTECCIÓN CORPORAL**

**PETOS DE SPARRING:**
- **Básico**: Espuma tradicional, 180.000 – 320.000 COP  
- **WTF Electrónico**: LaJust/KP&P, 800.000 – 1.600.000 COP  
- **Características**: Sensores de impacto, batería recargable
- **Tallas**: XXS (niños) hasta XXL (adultos)

**CASCOS:**
- **Abierto tradicional**: 140.000 – 280.000 COP, mejor visibilidad
- **Cerrado (dipped foam)**: 320.000 – 600.000 COP, máxima protección
- **Electrónico WTF**: 1.200.000 – 2.400.000 COP, puntuación automática

**2️⃣ PROTECCIONES DE EXTREMIDADES**

**ESPINILLERAS + EMPEINE:**
- **Básicas**: Espuma + vinyl, 100.000 – 180.000 COP
- **Premium**: Cuero + gel, 240.000 – 480.000 COP
- **Elásticos ajustables**: Tallas S, M, L, XL

**ANTEBRAZOS:**
- **Estándar**: 80.000 – 160.000 COP el par
- **Anatómicos**: Moldeo ergonómico, 180.000 – 320.000 COP

**GUANTES DE SPARRING:**
- **Semi-contacto**: 60.000 – 120.000 COP
- **Full-contact**: 160.000 – 320.000 COP
- **Electrónicos**: 600.000 – 1.200.000 COP

**3️⃣ PROTECCIONES ÍNTIMAS**

**COQUILLAS:**
- **Hombres**: Copa rígida + suspensor, 60.000 – 140.000 COP
- **Mujeres**: Protector pélvico, 80.000 – 160.000 COP
- **Junior**: Versiones adaptadas, 48.000 – 100.000 COP

**PROTECTORES BUCALES:**
- **Básicos**: Termo-moldeable, 12.000 – 32.000 COP
- **Custom**: Hecho a medida, 160.000 – 400.000 COP
- **Ortodónticos**: Espaciales, 60.000 – 120.000 COP

===========================
🥊 EQUIPOS DE ENTRENAMIENTO
===========================

**PAOS Y PALETAS:**
- **Paos curvos**: 160.000 – 320.000 COP el par, absorción máxima
- **Paos rectos**: 120.000 – 240.000 COP el par, versatilidad
- **Paletas**: 100.000 – 200.000 COP el par, velocidad y precisión
- **Escudos corporales**: 320.000 – 600.000 COP, entrenamiento realista

**SACOS DE ENTRENAMIENTO:**
- **Heavy bags**: 40-100 lbs, 400.000 – 1.200.000 COP
- **Speed bags**: Coordinación, 120.000 – 320.000 COP
- **Makiwara**: Tablones tradicionales, 240.000 – 600.000 COP

**ACCESORIOS DE FLEXIBILIDAD:**
- **Bandas elásticas**: Resistencia graduada, 60.000 – 160.000 COP
- **Stretching machines**: 800.000 – 3.200.000 COP
- **Bloques de yoga**: Adaptación TKD, 80.000 – 200.000 COP

==================================
PROMOCIONES Y SISTEMA COMERCIAL 💰
==================================

**PACKS ESPECIALIZADOS**

**🎯 PACK INICIO TOTAL** (-30%)
- Dobok principiante + cinturón blanco + protecciones básicas
- Valor individual: 1.600.000 COP → **1.200.000 COP**
- Ideal para: Primer día de entrenamiento

**🏆 PACK COMPETIDOR AVANZADO** (-25%)
- Dobok WTF + protecciones completas + bolsa de transporte
- Valor individual: 1.600.000 COP → **1.200.000 COP**
- Ideal para: Torneos oficiales

**👨‍👩‍👧‍👦 PACK FAMILIA** (2x1 en segundo dobok)
- Doboks para padres e hijos
- **Ahorro**: Hasta 180.000 COP

**🏫 PACK ESCUELA/ACADEMIA** (-20% en 10+ productos)
- Descuentos progresivos por volumen
- **10-19 productos**: 15% OFF
- **20+ productos**: 20% OFF
- **50+ productos**: 25% OFF + envío gratis

=========================
CALENDARIO DE PROMOCIONES
=========================

**ENERO-FEBRERO: "Nuevo Año, Nuevo Gear"**
- 20% OFF en doboks de inicio
- Financiamiento sin intereses 3 meses

**MARZO-MAYO: "Preparación de Torneos"**
- 25% OFF en equipos de competición
- Packs de protecciones WTF especiales

**JUNIO-AGOSTO: "Verano de Entrenamiento"**
- Equipos de training con descuentos
- Combos de paos y accesorios

**SEPTIEMBRE-NOVIEMBRE: "Season de Grados"**
- Descuentos en cinturones y doboks ceremoniales
- Bordados gratuitos en compras desde 400.000 COP

**DICIEMBRE: "Regalos de Guerrero"**
- Gift cards con bonificaciones
- Sets de regalo personalizados

===================================
ASESORÍA ESPECIALIZADA POR PERFIL 🎯
===================================

**POR NIVEL DE PRACTICA:**

👶 **Principiante absoluto:**
- Presupuesto mínimo: 240.000 – 320.000 COP
- Esenciales: Dobok básico + cinturón + bucal
- Evitar: Equipos premium innecesarios

🟢 **Intermedio (cinturones de color):**

- Presupuesto: 600.000 – 1.000.000 COP
- Añadir: Protecciones de sparring básicas
- Considerar: Upgrade a dobok de mejor calidad

⚫ **Avanzado / Competidor:**
- Presupuesto: 1.200.000 – 2.400.000 COP
- Indispensable: Gear certificado WTF
- Invertir: Equipos electrónicos, doboks múltiples

👨‍🏫 **Instructor / Maestro:**
- Presupuesto: 2.000.000+ COP
- Enfoque: Imagen profesional, durabilidad
- Personalización: Bordados, equipos de enseñanza

=========
POR EDAD:
=========

👶 **Niños (3-8 años):**
- Prioridad: Seguridad y comodidad
- Tallas: 000-1, materiales suaves
- Presupuesto: 200.000 – 400.000 COP

👦 **Pre-adolescentes (9-13 años):**
- Crecimiento rápido, tallas ajustables
- Introducir: Protecciones de sparring
- Presupuesto: 400.000 – 800.000 COP

👩‍🦱 **Adolescentes / Adultos:**
- Equipos estándar completos
- Considerar: Competición y especialización
- Presupuesto: 800.000 – 2.000.000+ COP

==================================
ESTILO DE COMUNICACIÓN COMERCIAL 🗣️
==================================

**EMOJIS ESPECÍFICOS:**
- 🛍️ Para productos/compras
- 💰 Para precios/promociones
- 📏 Para tallas/medidas
- 🎯 Para recomendaciones
- ✅ Para certificaciones/calidad
- 📦 Para packs/combos
- 🏷️ Para ofertas especiales
- 🔍 Para comparaciones

**FRASES CLAVE:**
- "Basado en tu nivel, recomiendo..."
- "Dentro de tu presupuesto, las mejores opciones son..."
- "Para maximizar tu inversión..."
- "Esta promoción es perfecta porque..."

=========================
PROTOCOLO DE RESPUESTAS 📋
=========================

**SIEMPRE INCLUIR:**
1. **Recomendación específica** con modelo/marca
2. **Rango de precios** actualizado
3. **Justificación** de por qué esa opción
4. **Alternativas** para diferentes presupuestos
5. **Promociones aplicables** actuales

**INFORMACIÓN BÁSICA PERMITIDA (solo lo esencial):**
- **Cinturones**: Secuencia de colores básica (blanco→amarillo→verde→azul→rojo→negro)
- **Términos básicos**: Dobok (uniforme), Ti (cinturón), sparring (combate)
- **Niveles**: Principiante, intermedio, avanzado, competidor
- **Edades**: Categorías básicas para recomendaciones de productos


**NUNCA ENTRAR EN DETALLES DE:**
- Historia del Taekwondo
- Técnicas específicas o filosofía
- Entrenamiento o metodologías
- Competiciones o reglas deportivas
- Aspectos culturales o tradicionales

**SIEMPRE REDIRIGIR A PRODUCTOS:**
Si preguntan sobre historia/técnicas/filosofía, responder:
"🛍️ Soy especialista en productos de Taekwondo. ¿Te puedo ayudar a encontrar el equipamiento perfecto para tu práctica? Cuéntame tu nivel y qué necesitas."

---

**RECUERDA**: Eres el consultor comercial #1 en productos de Taekwondo. Tu valor está en conocer cada detalle técnico, precio y especificación de equipamiento para ayudar a cada cliente a hacer la compra perfecta para sus necesidades. 🛍️🥋
        """.strip()
    
    def _get_product_knowledge(self) -> Dict[str, Any]:
        
        # Base de conocimiento especializada en productos
        
        return {
            "doboks": {
                "principiante": {
                    "material": "100% Algodón, 240-280 GSM",
                    "precio": "100.000–180.000 COP",
                    "caracteristicas": ["Cuello en V tradicional", "Costuras reforzadas", "Fácil lavado"],
                    "durabilidad": "2-3 años uso regular",
                    "ideal_para": "Entrenamientos diarios, exámenes de grado",
                    "tallas": "0 hasta 7"
                },
                "competicion": {
                    "material": "Poliéster-Algodón 65/35, 320-350 GSM",
                    "precio": "240.000–480.000 COP",
                    "caracteristicas": ["Corte atlético", "Certificación WTF", "Secado rápido"],
                    "durabilidad": "3-5 años uso intensivo",
                    "ideal_para": "Torneos oficiales, sparring avanzado"
                },
                "premium": {
                    "material": "Algodón premium/Bambú, 400+ GSM",
                    "precio": "400.000–1.000.000 COP",
                    "caracteristicas": ["Bordados personalizados", "Acabados de lujo", "Máxima durabilidad"],
                    "ideal_para": "Maestros, ceremonias, representación oficial"
                }
            },
            "protecciones": {
                "basicas": {
                    "productos": ["Bucal", "Coquilla", "Espinilleras"],
                    "precio_total": "160.000–320.000 COP",
                    "ideal_para": "Principiantes, sparring ligero"
                },
                "intermedias": {
                    "productos": ["Básicas + Peto + Antebrazos"],
                    "precio_total": "480.000–800.000 COP",
                    "ideal_para": "Sparring regular, cinturones intermedios"
                },
                "completas": {
                    "productos": ["Intermedias + Casco + Guantes"],
                    "precio_total": "800.000–1.600.000 COP",
                    "ideal_para": "Competición, sparring intensivo"
                },
                "electronicas": {
                    "productos": ["Peto + Casco electrónicos WTF"],
                    "precio_total": "2.000.000–4.000.000 COP",
                    "ideal_para": "Competiciones oficiales WTF"
                }
            },
            "cinturones": {
                "blanco": {
                    "material": "Algodón 100%",
                    "precio": "32.000 – 50.000 COP",
                    "descripcion": "Primer nivel, ideal para principiantes."
                },
                "amarillo": {
                    "material": "Algodón 100%",
                    "precio": "40.000 – 60.000 COP",
                    "descripcion": "Segundo nivel, simboliza el inicio del aprendizaje."
                },
                "verde": {
                    "material": "Algodón premium",
                    "precio": "60.000 – 80.000 COP",
                    "descripcion": "Nivel intermedio, crecimiento y desarrollo."
                },
                "azul": {
                    "material": "Algodón premium",
                    "precio": "80.000 – 100.000 COP",
                    "descripcion": "Nivel intermedio-avanzado, simboliza el cielo."
                },
                "rojo": {
                    "material": "Algodón premium",
                    "precio": "100.000 – 140.000 COP",
                    "descripcion": "Nivel avanzado, representa precaución y preparación."
                },
                "negro": {
                    "material": "Seda o algodón premium",
                    "precio": "150.000 – 240.000 COP",
                    "descripcion": "Máximo nivel, simboliza maestría y experiencia.",
                    "personalizacion": "Puede incluir bordados con nombre, escuela o grado"
                }
            },
            "accesorios": {
                "training": {
                    "paos": "120.000–320.000 COP por par",
                    "sacos": "400.000–1.200.000 COP",
                    "bandas_elasticas": "60.000–160.000 COP"
                },
                "transporte": {
                    "bolsas_dobok": "80.000–160.000 COP",
                    "mochilas_gear": "160.000–320.000 COP",
                    "maletas_competicion": "320.000–600.000 COP"
                }
            },
            "promociones_activas": {
                "pack_inicio": {
                    "contenido": "Dobok + cinturón + protecciones básicas",
                    "precio_individual": "480.000 COP",
                    "precio_pack": "336.000 COP",
                    "descuento": "30%"
                },
                "pack_competidor": {
                    "contenido": "Dobok WTF + protecciones completas + bolsa",
                    "precio_individual": "1.600.000 COP", 
                    "precio_pack": "1.200.000 COP",
                    "descuento": "25%"
                },
                "descuentos_volumen": {
                    "10_productos": "15% OFF",
                    "20_productos": "20% OFF",
                    "50_productos": "25% OFF + envío gratis"
                }
            }
        }
    
    def _detect_user_intent(self, message: str) -> Dict[str, Any]:
        
        # Detecta intenciones comerciales y de productos específicamente
        
        message_lower = message.lower()
        
        intents = {
            "greeting": ["hola", "hello", "hi", "buenas", "saludos"],
            "dobok_inquiry": ["dobok", "uniforme", "traje", "kimono"],
            "protection_inquiry": ["proteccion", "protector", "casco", "peto", "espinilleras"],
            "belt_inquiry": ["cinturon", "cinta", "ti"],
            "price_inquiry": ["precio", "costo", "vale", "cuanto", "barato", "caro"],
            "size_inquiry": ["talla", "medida", "tamaño", "size"],
            "promotion_inquiry": ["promocion", "descuento", "oferta", "rebaja", "barato"],
            "recommendation": ["recomienda", "sugiere", "necesito", "busco", "quiero"],
            "comparison": ["diferencia", "comparar", "mejor", "vs", "versus"],
            "beginner_gear": ["empezar", "principiante", "comenzar", "nuevo", "inicio"],
            "competition_gear": ["competir", "torneo", "competicion", "wtf", "oficial"],
            "purchase": ["comprar", "adquirir", "conseguir", "donde"]
        }
        
        detected_intents = []
        confidence = 0
        
        for intent, keywords in intents.items():
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            if matches > 0:
                detected_intents.append(intent)
                confidence += matches
        
        return {
            "primary_intent": detected_intents[0] if detected_intents else "general",
            "all_intents": detected_intents,
            "confidence": confidence / len(message.split()) if message.split() else 0,
            "message_type": self._classify_message_type(message_lower)
        }
    
    def _classify_message_type(self, message: str) -> str:
        
        # Clasifica mensajes para respuestas comerciales apropiadas
        
        if any(word in message for word in ["?", "que", "como", "donde", "cuando", "cuanto"]):
            return "question"
        elif any(word in message for word in ["quiero", "necesito", "busco", "me interesa"]):
            return "purchase_intent"
        elif any(word in message for word in ["gracias", "perfecto", "excelente", "genial"]):
            return "positive_feedback"
        elif any(word in message for word in ["caro", "costoso", "barato", "economic"]):
            return "price_concern"
        else:
            return "general_inquiry"
    
    async def process_message(
        self, 
        message: str, 
        user_info: Dict[str, Any] = None, 
        context: Optional[str] = None,
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        
        # Procesa mensajes con enfoque exclusivo en productos
        
        try:
            # Analizar intención comercial
            intent_analysis = self._detect_user_intent(message)
            
            # Construir prompt comercial especializado
            commercial_prompt = self._build_commercial_prompt(
                message, user_info, intent_analysis
            )
            
            # Procesar con LLM o usar respuestas especializadas
            if self.primary_provider == "openai" and self.openai_client:
                response = await self._process_with_openai(commercial_prompt, intent_analysis)
            else:
                response = self._get_product_focused_fallback(message, intent_analysis)
            # Post-procesar para enfoque comercial
            return self._post_process_commercial_response(response, intent_analysis)
                
        except Exception as e:
            logger.error(f"Error procesando consulta comercial: {str(e)}")
            return self._get_commercial_error_response()
    
    def _build_commercial_prompt(
        self, 
        message: str, 
        user_info: Dict[str, Any] = None,
        intent_analysis: Dict[str, Any] = None
    ) -> str:
        
        prompt_parts = []
        
        # Contexto comercial
        prompt_parts.append("CONSULTA COMERCIAL DE PRODUCTOS DE TAEKWONDO")
        
        if intent_analysis:
            prompt_parts.append(f"INTENCIÓN: {intent_analysis['primary_intent']}")
            prompt_parts.append(f"TIPO: {intent_analysis['message_type']}")
        
        # Información del cliente para personalizar recomendaciones
        if user_info:
            prompt_parts.append(f"CLIENTE: {user_info.get('first_name', 'Usuario')}")
        
        # Mensaje del cliente
        prompt_parts.append(f"CONSULTA: {message}")
        
        # Instrucciones específicas según intención
        commercial_instructions = {
            "dobok_inquiry": "ENFOQUE: Recomienda doboks específicos con precios, tallas y características técnicas.",
            "protection_inquiry": "ENFOQUE: Especifica protecciones necesarias según nivel, con precios y comparaciones.",
            "price_inquiry": "ENFOQUE: Proporciona rangos de precios detallados y opciones para diferentes presupuestos.",
            "promotion_inquiry": "ENFOQUE: Destaca promociones actuales, packs disponibles y formas de ahorrar.",
            "recommendation": "ENFOQUE: Haz recomendaciones personalizadas basadas en necesidades y presupuesto.",
            "beginner_gear": "ENFOQUE: Pack de inicio completo con presupuesto mínimo y productos esenciales."
        }
        
        primary_intent = intent_analysis.get('primary_intent') if intent_analysis else None
        if primary_intent in commercial_instructions:
            prompt_parts.append(commercial_instructions[primary_intent])
        
        prompt_parts.append("\nIMPORTANTE: Incluye precios, promociones aplicables y alternativas para diferentes presupuestos.")
        
        return "\n".join(prompt_parts)
    
    async def _process_with_openai(self, prompt: str, intent_analysis: Dict[str, Any] = None) -> str:
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",   
                messages=messages,
                max_tokens=800,
                temperature=0.4,
                top_p=0.9,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
        
        except asyncio.TimeoutError:
            raise Exception("Timeout al procesar consulta comercial")
        except Exception as e:
            logger.error(f"Error con OpenAI en consulta comercial: {str(e)}")
            raise e
    
    def _get_product_focused_fallback(self, message: str, intent_analysis: Dict[str, Any]) -> str:
        
        # Respuestas fallback especializadas en productos únicamente
        
        primary_intent = intent_analysis.get('primary_intent', 'general')
        message_lower = message.lower()
        
        if primary_intent == "greeting":
            return """🛍️ ¡Hola! Soy **BaekhoBot**, tu especialista personal en productos de Taekwondo.

**🎯 Te ayudo con:**
- 🥋 **Doboks**: Desde principiante (100.000 COP) hasta premium (1.000.000 COP)
- 🛡️ **Protecciones**: Básicas, intermedias y competición
- 🏷️ **Promociones**: Packs con hasta 30% de descuento
- 📏 **Tallas**: Guía precisa para todas las edades
- 💰 **Presupuestos**: Opciones para todos los bolsillos

**🎉 OFERTAS ACTUALES:**
- Pack Inicio: Dobok + cinturón + protecciones = 336.000 COP (antes 480.000 COP)
- Pack Competidor: Equipo completo WTF = 1.200.000 COP (antes 1.600.000 COP)

¿Qué necesitas para tu práctica de Taekwondo? 🤔"""
        
        elif primary_intent == "dobok_inquiry":
            return """🥋 **DOBOKS DISPONIBLES - CATÁLOGO COMPLETO**

**💰 RANGO DE PRECIOS:**
- Principiante: 100.000 – 180.000 COP
- Competición: 240.000 – 480.000 COP  
- Premium: 400.000 – 1.000.000 COP

**🎯 POR TIPO DE USO:**

**1. DOBOK PRINCIPIANTE** (100.000 – 180.000 COP)
- Material: 100% Algodón, 280 GSM
- Ideal para: Entrenamientos diarios
- Tallas: 000 (niños 3 años) hasta 7 (adultos XXL)
- Durabilidad: 2-3 años

**2. DOBOK COMPETICIÓN WTF** (240.000 – 480.000 COP)
- Material: Poliéster-Algodón 65/35
- Certificado oficial para torneos
- Corte atlético, secado rápido
- Incluye logos WTF bordados

**3. DOBOK PREMIUM MAESTRO** (400.000 – 1.000.000 COP)
- Algodón premium/Bambú
- Bordados personalizados incluidos
- Acabados de lujo, máxima durabilidad

**📏 GUÍA DE TALLAS:**
Formula: (Altura en cm ÷ 10) - 10

**🎉 PROMOCIÓN ACTUAL:**
Pack Dobok + Cinturón = 20% OFF

¿Cuál es tu nivel y qué tipo de uso le darás? Te recomiendo la opción perfecta. 🎯"""
        
        elif primary_intent == "protection_inquiry":
            return """🛡️ **PROTECCIONES COMPLETAS - GUÍA ESPECIALIZADA**

**🎯 POR NIVEL DE PROTECCIÓN:**

**BÁSICAS** (160.000 – 320.000 COP) - Principiantes
- ✅ Bucal: 12.000 – 32.000 COP
- ✅ Coquilla: 60.000 – 140.000 COP  
- ✅ Espinilleras + empeine: 100.000 – 180.000 COP
- **Total**: 172.000 – 352.000 COP

**INTERMEDIAS** (480.000 – 800.000 COP) - Sparring regular
- ✅ Básicas + Peto: 180.000 – 320.000 COP
- ✅ + Antebrazos: 80.000 – 160.000 COP
- **Total**: 432.000 – 672.000 COP

**COMPLETAS** (800.000 – 1.600.000 COP) - Competición
- ✅ Intermedias + Casco: 140.000 – 600.000 COP
- ✅ + Guantes sparring: 60.000 – 320.000 COP
- **Total**: 1.592.000 COP

**ELECTRÓNICAS WTF** (2.000.000 – 4.000.000 COP) - Torneos oficiales
- Peto electrónico LaJust/KP&P: 800.000 – 1.600.000 COP
- Casco electrónico: 1.200.000 – 2.400.000 COP
- Sistema completo certificado

**📏 GUÍA DE TALLAS:**
- XS: Niños 6-8 años
- S: Niños 9-12 años  
- M: Adolescentes/Adultos pequeños
- L: Adultos promedio
- XL: Adultos grandes

**🎉 PACK PROTECCIÓN COMPLETA:**
Ahorra 25% comprando el set completo = 600.000 COP (antes 800.000 COP)

¿Para qué tipo de entrenamiento necesitas protección? 🤔"""
        
        elif primary_intent == "price_inquiry":
            return """💰 **GUÍA COMPLETA DE PRECIOS - TAEKWONDO GEAR**

**🥋 DOBOKS:**
- Básico: 100.000 – 180.000 COP
- Competición: 240.000 – 480.000 COP
- Premium: 400.000 – 1.000.000 COP

**🛡️ PROTECCIONES:**
- Set básico: 160.000 – 320.000 COP
- Set intermedio: 480.000 – 800.000 COP
- Set completo: 800.000 – 1.600.000 COP
- Electrónico WTF: 2.000.000 – 4.000.000 COP

**🏅 CINTURONES:**
- Blanco/Amarillo: 32.000 – 60.000 COP  
- Verde/Azul: 60.000 – 100.000 COP  
- Rojo/Negro (seda premium): 120.000 – 240.000 COP  

**🥊 ACCESORIOS:**
- Paos: 120.000 – 320.000 COP (par)  
- Sacos: 400.000 – 1.200.000 COP  
- Bolsas: 80.000 – 320.000 COP  

**💡 PRESUPUESTOS RECOMENDADOS:**

**PRINCIPIANTE TOTAL** (240.000 – 400.000 COP):
- Dobok básico + cinturón + bucal + coquilla

**INTERMEDIO** (600.000 – 1.000.000 COP):
- Dobok mejor calidad + protecciones básicas

**AVANZADO** (1.200.000 – 2.000.000 COP):
- Dobok competición + protecciones completas

**COMPETIDOR** (2.000.000 – 3.200.000 COP):
- Equipo WTF certificado completo

**🎉 FORMAS DE AHORRAR:**
- Pack Inicio: -30% = **336.000 COP**(antes 480.000 COP)
- Pack Competidor: -25% = **1.200.000 COP** (antes 1.600.000 COP)
- Compras grupales: hasta -25%
- Financiamiento: 3 meses sin intereses

¿Cuál es tu presupuesto aproximado? Te armo la mejor combinación. 🎯"""
        
        elif primary_intent == "promotion_inquiry":
            return """🎉 **PROMOCIONES ESPECIALES ACTIVAS**

**🔥 OFERTAS DESTACADAS:**

**PACK INICIO TOTAL** (-30% OFF)
- 🥋 Dobok principiante
- 🏅 Cinturón blanco  
- 🛡️ Protecciones básicas (bucal + coquilla + espinilleras)
- 💰 Precio: **336.000 COP** (antes 480.000 COP)
- ✅ Perfecto para primer día

**PACK COMPETIDOR PRO** (-25% OFF)
- 🥋 Dobok certificado WTF
- 🛡️ Protecciones completas
- 👜 Bolsa de transporte
- 💰 Precio: **1.200.000 COP** (antes 1.600.000 COP)
- ✅ Listo para torneos

**COMBO FAMILIA** (2x1 en segundo dobok)
- Primer dobok: precio normal
- Segundo dobok: GRATIS
- 💰 Ahorro: hasta **180.000 COP**

**🏫 DESCUENTOS POR VOLUMEN:**
- 10+ productos: 15% OFF
- 20+ productos: 20% OFF  
- 50+ productos: 25% OFF + envío gratis

**📅 PROMOCIONES TEMPORALES:**
- **ENERO-FEB**: "Año Nuevo" - 20% doboks principiante
- **MAR-MAY**: "Pre-Torneo" - 25% gear competición
- **JUN-AGO**: "Verano" - Equipos training con descuento
- **SEP-NOV**: "Season Grados" - Cinturones y ceremoniales
- **DICIEMBRE**: "Regalos" - Gift cards +20% bonificación

**💳 FINANCIAMIENTO:**
- Sin intereses hasta 3 meses
- Apartado con 50% anticipo

**🚚 ENVÍO GRATIS:**
- Compras sobre 400.000 COP

¿Cuál promoción te interesa más? 🛒"""
        
        elif primary_intent == "recommendation":
            return """🎯 **RECOMENDACIONES PERSONALIZADAS**

Para darte la mejor recomendación, necesito saber:

**📊 CUÉSTIONARIO RÁPIDO:**
1. **Nivel actual:** ¿Principiante, intermedio o avanzado?
2. **Edad:** ¿Niño, adolescente o adulto?
3. **Uso principal:** ¿Entrenamiento, competición o ambos?
4. **Presupuesto:** ¿Rango aproximado disponible?

**🎯 RECOMENDACIONES RÁPIDAS:**

**SI ERES PRINCIPIANTE ABSOLUTO:**
- Pack Inicio: 336.000 COP (dobok + cinturón + protecciones básicas)
- Presupuesto mínimo funcional

**SI YA TIENES EXPERIENCIA:**
- Dobok competición (240.000 – 480.000 COP) + protecciones intermedias (480.000 – 800.000 COP)
- Inversión: 720.000 – 1.280.000 COP

**SI COMPITES:**
- Dobok WTF certificado + protecciones completas electrónicas
- Inversión: 2.000.000 – 3.200.000 COP

**SI ERES INSTRUCTOR:**
- Dobok premium bordado + equipos de enseñanza (paos, etc.)
- Inversión: 1.200.000 – 2.400.000 COP

**👶 PARA NIÑOS (3-12 años):**
- Prioridad: comodidad y seguridad
- Tallas 000-2, materiales suaves
- Presupuesto: 200.000 – 600.000 COP

**🏆 PARA COMPETIDORES:**
- Solo equipos certificados WTF
- Múltiples doboks para rotación
- Presupuesto: 1.600.000 – 4.000.000 COP

¡Cuéntame más detalles y te doy la recomendación perfecta! 📋"""
        
        elif primary_intent == "size_inquiry":
            return """📏 **GUÍA COMPLETA DE TALLAS - TODAS LAS CATEGORÍAS**

**🥋 TALLAS DE DOBOKS:**

**FÓRMULA EXACTA:**
Talla = (Altura en cm ÷ 10) - 10

**TABLA DETALLADA:**
- **000**: 90-100cm (3-4 años)
- **00**: 100-110cm (4-5 años)  
- **0**: 110-120cm (5-7 años)
- **1**: 120-135cm (7-10 años)
- **2**: 135-150cm (10-13 años)
- **3**: 150-160cm (adulto S)
- **4**: 160-170cm (adulto M)
- **5**: 170-180cm (adulto L)
- **6**: 180-190cm (adulto XL)
- **7**: 190cm+ (adulto XXL)

**🛡️ TALLAS DE PROTECCIONES:**

**CASCOS:**
- XS: Circunferencia 50-52cm (niños)
- S: 52-54cm (adolescentes)
- M: 54-57cm (adultos promedio)
- L: 57-60cm (adultos grandes)
- XL: 60cm+ (adultos muy grandes)

**PETOS:**
- XS: Altura 120-135cm
- S: 135-150cm
- M: 150-170cm  
- L: 170-185cm
- XL: 185cm+

**ESPINILLERAS:**
- XS: Largo 25-30cm (niños)
- S: 30-35cm (adolescentes)
- M: 35-40cm (adultos)
- L: 40-45cm (adultos altos)

**🏅 CINTURONES:**
Longitud = Cintura + 40cm (20cm cada extremo)
- Talla 3-4: 220cm
- Talla 5: 240cm  
- Talla 6: 260cm
- Talla 7: 280cm

**📐 CONSEJOS DE MEDICIÓN:**
- Mide altura SIN zapatos
- Para doboks: prefiere talla más grande si estás entre dos
- Para protecciones: ajuste exacto es crucial para seguridad

¿Necesitas ayuda midiendo alguna talla específica? 📋"""
        
        elif primary_intent == "beginner_gear":
            return """🌱 **PACK COMPLETO PARA PRINCIPIANTES**

**🎯 EQUIPAMIENTO MÍNIMO ESENCIAL:**

**OPCIÓN ECONÓMICA** (240.000 – 320.000 COP):
1. **Dobok básico** - 140.000 COP
   - 100% algodón, talla apropiada
2. **Cinturón blanco** - 40.000 COP  
   - Algodón estándar
3. **Protector bucal** - 20.000 COP
   - Básico termomoldeable
4. **Coquilla** - 80.000 COP
   - Protección básica obligatoria

**OPCIÓN RECOMENDADA** (336.000 COP - PACK PROMOCIONAL):
✅ Todo lo anterior MÁS:
- Espinilleras con empeine incluidas
- Descuento del 30%
- Garantía de satisfacción

**OPCIÓN COMPLETA** (600.000 COP):
✅ Pack recomendado MÁS:
- Dobok de mejor calidad
- Cinturón bordado con nombre
- Bolsa de transporte

**🎓 PLAN DE CRECIMIENTO:**

**MES 1-2:** Solo pack básico
**MES 3-6:** Añadir protecciones de sparring (240.000 – 400.000 COP)
**MES 6+:** Considerar dobok de competición (240.000 – 480.000 COP)

**💡 CONSEJOS DE COMPRA:**
- NO compres todo de una vez
- Empieza con lo esencial y ve añadiendo
- Los niños crecen rápido: tallas con espacio extra
- Invierte más en protecciones que en doboks al principio

**📏 GUÍA RÁPIDA DE TALLAS:**
- **Niños 3-6 años**: Talla 000-0
- **Niños 7-12 años**: Talla 1-2  
- **Adolescentes**: Talla 3-4
- **Adultos**: Talla 4-6

**🎉 OFERTA ESPECIAL PRINCIPIANTE:**
Pack completo por solo 336.000 COP (ahorra 144.000 COP)

¿Cuántos años tienes y cuál es tu presupuesto inicial? Te armo el pack perfecto. 🎒"""
        
        elif primary_intent == "competition_gear":
            return """🏆 **EQUIPAMIENTO PARA COMPETICIÓN OFICIAL**

**⚠️ REQUISITOS WTF/WORLD TAEKWONDO:**

**🥋 DOBOK OBLIGATORIO:**
- Certificación WTF oficial
- Corte atlético reglamentario  
- Logo World Taekwondo bordado
- **Precio**: 320.000 – 600.000 COP
- **Marcas aprobadas**: Adidas, Daedo, Mooto

**🛡️ PROTECCIONES CERTIFICADAS:**

**ELECTRÓNICAS (Obligatorias nivel internacional):**
- **Peto electrónico**: 1.000.000 – 1.600.000 COP
  - LaJust, KP&P o Daedo
  - Sensores de impacto calibrados
  - Batería 8+ horas
  
- **Casco electrónico**: 1.200.000 – 2.400.000 COP  
  - Misma marca que peto
  - Sincronización automática
  - Certificado WT

**PROTECCIONES ADICIONALES:**
- Antebrazos: 160.000 – 320.000 COP (certificados)
- Espinilleras: 240.000 – 480.000 COP (aprobadas WT)
- Coquilla: 100.000 – 180.000 COP (homologada)
- Bucal: 20.000 – 60.000 COP (reglamentario)

**💰 INVERSIÓN TOTAL COMPETICIÓN:**
- **Nivel local**: 1.200.000 – 2.000.000 COP
- **Nivel nacional**: $500-800  
- **Nivel internacional**: $800-1200

**🎽 EXTRAS COMPETITIVOS:**
- Doboks de repuesto (2-3): $240-450
- Bolsa especializada: 240.000 – 480.000 COP
- Kit de reparaciones: 120.000 – 200.000 COP

**📋 CHECKLIST PRE-COMPETICIÓN:**
✅ Dobok sin roturas ni manchas
✅ Protecciones certificadas vigentes  
✅ Baterías cargadas (electrónicos)
✅ Documentos de certificación
✅ Equipo de repuesto

**🎉 PACK COMPETIDOR PRO** (-25%):
Todo lo necesario por 2.400.000 COP (antes 3.200.000 COP)
- Dobok WTF + protecciones completas + bolsa

**⏰ TIEMPO DE PREPARACIÓN:**
Ordena con 2-4 semanas de anticipación para:
- Verificación de certificaciones
- Pruebas de ajuste
- Familiarización con equipo

¿En qué nivel vas a competir? Te armo el paquete exacto que necesitas. 🥇"""

        else:
            return """🛍️ ¡Hola! Soy **BaekhoBot**, tu especialista en productos de Taekwondo.

**🎯 ¿En qué puedo ayudarte hoy?**

- 🥋 **Doboks**: Desde 100.000 COP (principiante) hasta 1.000.000 COP (premium)
- 🛡️ **Protecciones**: Sets desde 160.000 COP hasta 4.000.000 COP (electrónicas)
- 📏 **Tallas**: Guía completa para todas las edades
- 💰 **Presupuestos**: Opciones para todos los bolsillos
- 🎉 **Promociones**: Packs con hasta 30% descuento

**🔥 OFERTAS HOY:**
- Pack Inicio: 336.000 COP (antes 480.000 COP) - ¡Ahorra **144.000 COP**!
- Pack Competidor: 1.200.000 COP (antes 1.600.000 COP) - ¡Ahorra **400.000 COP**!

Solo dime:
- ¿Qué tipo de producto buscas?
- ¿Cuál es tu nivel?
- ¿Cuál es tu presupuesto aproximado?

¡Y te daré la recomendación perfecta! 🎯"""
    
    def _post_process_commercial_response(self, response: str, intent_analysis: Dict[str, Any]) -> str:
        
        # Post-proceso de respuestas para mantener enfoque comercial
        
        # Asegurar emojis comerciales apropiados
        if not any(emoji in response for emoji in ["🛍️", "💰", "🎯", "📏", "🎉"]):
            response = "🛍️ " + response
        
        # Añadir llamadas a la acción comerciales
        commercial_ctas = {
            "dobok_inquiry": "\n\n¿Cuál dobok se ajusta mejor a tu nivel y presupuesto? 🤔",
            "protection_inquiry": "\n\n¿Para qué tipo de entrenamiento necesitas las protecciones? 🛡️",
            "price_inquiry": "\n\n¿Cuál es tu rango de presupuesto preferido? 💰",
            "promotion_inquiry": "\n\n¿Te interesa algún pack en particular? ¡Puedo personalizar una oferta! 🎁",
            "recommendation": "\n\n¡Cuéntame más detalles para darte la mejor recomendación! 📋"
        }
        
        primary_intent = intent_analysis.get('primary_intent', 'general')
        if primary_intent in commercial_ctas and len(response) < 1200:
            response += commercial_ctas[primary_intent]
        
        return response.strip()
    
    def _get_commercial_error_response(self) -> str:
        
        # Respuesta de error manteniendo enfoque comercial
        
        return """🛍️ ¡Ups! Pequeño problema técnico en nuestro sistema de productos...

Mientras se resuelve, puedo ayudarte con información básica:

**🎯 PRODUCTOS DISPONIBLES:**
- 🥋 Doboks: 100.000 – 1.000.000 COP
- 🛡️ Protecciones: 160.000 – 4.000.000 COP 
- 🏅 Cinturones: 32.000 – 240.000 COP
- 🥊 Accesorios: 60.000 – 1.200.000 COP

**🎉 PROMOCIONES ACTIVAS:**
- Pack Inicio: 336.000 COP (ahorra 144.000 COP)
- Pack Competidor: 1.200.000 COP (ahorra 400.000 COP)

¡Intenta tu consulta de nuevo en unos segundos! Estoy ansioso por ayudarte a encontrar el equipamiento perfecto. 🎒✨"""
    
    def get_model_info(self) -> dict:
        
        # Información del modelo enfocada en capacidades comerciales
        
        return {
            "provider": self.primary_provider,
            "available": self.is_available(),
            "openai_configured": bool(self.openai_client),
            "model": "gpt-4o-mini" if self.primary_provider == "openai" else "unknown",
            "commercial_capabilities": {
                "product_catalog": True,
                "price_comparisons": True,
                "size_guidance": True,
                "promotion_tracking": True,
                "purchase_recommendations": True,
                "budget_optimization": True
            },
            "product_categories": [
                "Doboks (uniformes)",
                "Protecciones completas", 
                "Cinturones y accesorios",
                "Equipos de entrenamiento",
                "Gear de competición",
                "Packs promocionales"
            ],
            "price_ranges": {
                "doboks": "100.000–1.000.000 COP",
                "protecciones": "160.000–4.000.000 COP",
                "cinturones": "32.000–240.000 COP",
                "accesorios": "60.000–1.200.000 COP"
            }
        }
    
    def is_available(self) -> bool:
        return self.primary_provider is not None
    
    async def get_product_recommendations(self, user_query: str, user_level: str = "", budget: str = "") -> str:
        
        # Recomendaciones de productos específicas basadas en parámetros comerciales
        
        recommendation_prompt = f"""
CONSULTA DE RECOMENDACIÓN COMERCIAL:

Consulta: {user_query}
Nivel: {user_level if user_level else "No especificado"}  
Presupuesto: {budget if budget else "No especificado"}

INSTRUCCIONES:
1. Recomienda productos específicos con precios exactos
2. Incluye alternativas para diferentes presupuestos
3. Menciona promociones y descuentos aplicables
4. Proporciona justificación comercial de cada recomendación
5. Incluye información de tallas si es relevante

ENFOQUE: Puramente comercial y de productos, no técnico ni deportivo.
        """
        
        return await self.process_message(recommendation_prompt)
    
    async def compare_products(self, product_type: str, comparison_criteria: str = "price") -> str:
        
        # Comparación detallada entre productos similares
        
        comparison_prompt = f"""
SOLICITUD DE COMPARACIÓN DE PRODUCTOS:

Tipo de producto: {product_type}
Criterio de comparación: {comparison_criteria}

INCLUIR:
1. Tabla comparativa con precios
2. Ventajas y desventajas de cada opción  
3. Recomendación según presupuesto
4. Promociones aplicables a cada producto
5. Mejor relación calidad-precio

ENFOQUE: Comparación comercial pura para facilitar decisión de compra.
        """
        return await self.process_message(comparison_prompt)

# ==============================
# Clase 2: Agente RAG (Qdrant)
# ==============================

class AgentService:
    def __init__(self):
        # ... (other initializations) ...
        self.qdrant_service = QdrantService()
        self.embedding_service = EmbeddingService()
        self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    async def process_query(self, query: str, user_id: str, context: Optional[Dict] = None) -> str:
        """
        Procesa una consulta del usuario usando RAG (Qdrant + embeddings)
        """
        try:
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Remove 'await' here because search_similar() returns a list, not a coroutine.
            relevant_docs = self.qdrant_service.search_similar(
                query_embedding,
                limit=5
            )

            context_text = self._build_context(relevant_docs, context)

            response = await self._generate_response(query, context_text, user_id)

            return response

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return None

    def _build_context(self, relevant_docs: List[Dict], additional_context: Optional[Dict] = None) -> str:
        context_parts = []

        if relevant_docs:
            context_parts.append("📦 Información de productos relevantes de la base de datos:")
            for doc in relevant_docs:
                payload = doc.get("payload", {})
                context_parts.append(f"- {payload.get('nombre', 'N/A')}: {payload.get('descripcion', 'N/A')}")
                context_parts.append(f"  💰 Precio: {payload.get('precio', 'N/A')}")
                context_parts.append(f"  📂 Categoría: {payload.get('categoria', 'N/A')}")

        if additional_context:
            context_parts.append("\nℹ️ Información adicional:")
            for key, value in additional_context.items():
                context_parts.append(f"- {key}: {value}")

        return "\n".join(context_parts)

    async def _generate_response(self, query: str, context: str, user_id: str) -> str:
        system_prompt = """
        Eres BaekhoBot 🥋, asistente comercial especializado en productos de Taekwondo.
        Tu objetivo es ayudar a los clientes a encontrar el equipamiento perfecto.
        - Sé claro y conciso
        - Incluye precios y categorías
        - Usa tono amigable y profesional
        """

        user_prompt = f"""
        Consulta: {query}

        Contexto disponible:
        {context}
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=600,
                temperature=0.5
            )

            return {
                "reply": response.choices[0].message.content.strip(),
                "sources": [], # You can populate this with relevant info from context
                "relevance_score": 0.0 # You can calculate this based on the search
            }

        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {str(e)}")
            return None

    async def get_product_recommendations(self, category: str, budget: Optional[float] = None) -> List[Dict]:
        try:
            search_query = f"productos de {category}"
            if budget:
                search_query += f" con precio menor a {budget}"

            query_embedding = await self.embedding_service.generate_embedding(search_query)

            results = await self.qdrant_service.search_similar(
                query_embedding,
                limit=10,
                collection_name="productos"
            )

            recommendations = []
            for result in results:
                payload = result.get("payload", {})
                precio = payload.get("precio", 0)

                if budget is None or precio <= budget:
                    recommendations.append({
                        "id": payload.get("id"),
                        "nombre": payload.get("nombre"),
                        "descripcion": payload.get("descripcion"),
                        "precio": precio,
                        "categoria": payload.get("categoria"),
                        "score": result.get("score", 0),
                    })

            return recommendations[:5]

        except Exception as e:
            logger.error(f"Error getting product recommendations: {str(e)}")
            return []


# ==============================
# Clase 3: Orquestador
# ==============================

class BaekhoAgent:
    """
    Orquesta entre el agente RAG (dinámico) y el agente hardcoded (fallback).
    """
    def __init__(self):
        self.rag_agent = AgentService()
        self.hardcoded_agent = TaekwondoAgent()

    async def process_message(self, message: str, user_info: Dict[str, Any] = None) -> str:
        # 1️⃣ Intentamos primero con RAG (Qdrant)
        response = await self.rag_agent.process_query(message, user_info.get("id", "anonimo"))

        # 2️⃣ Si RAG no devuelve nada, usamos fallback hardcoded
        if not response:
            logger.info("⚠️ Usando fallback hardcoded de TaekwondoAgent")
            response = await self.hardcoded_agent.process_message(message, user_info)

        return response

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "rag_available": True,
            "fallback_available": self.hardcoded_agent.is_available(),
            "models": {
                "rag": "gpt-4o-mini + Qdrant",
                "hardcoded": "gpt-4o-mini (catálogo estático)"
            }
        }