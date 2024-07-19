import io
import json
import uuid
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from .models import Document, DocumentCode


@csrf_exempt
def generate_document(request):
    if request.method == "POST":
        # Obtener datos del cuerpo JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos JSON inválidos."}, status=400)

        # Verificar que los datos necesarios estén presentes
        required_fields = [
            "arrendador_nombre",
            "arrendador_cedula",
            "arrendatario_nombre",
            "arrendatario_cedula",
            "arrendatario_celular",
            "deudor_solidario_nombre",
            "deudor_solidario_celular",
            "deudor_solidario_cedula",
            "inmueble_destino",
            "local_identificacion",
            "local_uso",
            "inmueble_direccion",
            "precio_arrendamiento",
            "fecha_inicio",
            "fecha_inicio_mes",
            "fecha_inicio_dia",
            "fecha_inicio_año",
            "deposito",
            "duracion_contrato",
            "fecha_fin",
        ]
        if not all(key in data for key in required_fields):
            return JsonResponse({"error": "Faltan campos obligatorios."}, status=400)

        # Preparar el documento PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        # Definir un estilo para texto justificado
        justified_style = ParagraphStyle(
            "Justified",
            parent=styles["Normal"],
            alignment=4,  # Justificado
            fontName="Helvetica",
            fontSize=14,
            leading=12,
        )

        content = []

        # Añadir el título
        content.append(Paragraph("CONTRATO SIMPLIFICADO", styles["Title"]))
        content.append(Spacer(1, 12))

        # Añadir el párrafo prefabricado con datos del JSON
        paragraphs = [
            f"""
                En el Municipio de LA VIRGINIA, Departamento de 
                RISARALDA, República de COLOMBIA, entre los suscritos
                a saber de una parte, la señora {data["arrendador_nombre"]},
                Mujer de nacionalidad colombiana y mayor de edad,
                identificada con la cédula de ciudadanía N°{data["arrendador_cedula"]},
                domiciliada y residente en esta localidad, actuando en
                su propio nombre y quién para efectos del presente acto
                se denominará LA ARRENDADORA, de una parte, y de la otra
                parte, el señor {data["arrendatario_nombre"]}, varón de
                nacionalidad colombiana y mayor de edad, identificado
                con la cédula de ciudadanía N°{data["arrendatario_cedula"]},
                Celular #{data["arrendatario_celular"]}, actuando igualmente
                en su propio nombre, quién para efectos del presente
                contrato se denominará EL ARRENDATARIO. Quienes de común
                acuerdo han decidido entre las partes celebrar un
                CONTRATO DE ARRENDAMIENTO de bien inmueble destinado a
                LOCAL COMERCIAL que se regirá por la siguientes cláusulas:
                ======================================
                PRIMERA: OBJETO DEL NEGOCIO: LA ARRENDADORA, se obliga
                a favor de EL ARRENDATARIO a realizar la entrega del uso
                y goce que tiene y ejerce sobre un bien inmueble, y
                está a su vez se obliga con EL ARRENDATARIO a recibirlo
                a título de arrendamiento. ====================================
                LOCAL COMERCIAL construido en material de adobe y cemento,
                pisos en cerámica, uno (1) unidad sanitaria completa, con
                servicios públicos domiciliarios de AGUA, ALCANTARILLADO,
                ENERGÍA ELÉCTRICA. Identificado como LOCAL N°1 para
                {data["local_uso"]} del bien inmueble ubicado en la
                {data["inmueble_direccion"]}, área urbana del Municipio de
                LA VIRGINIA, Departamento de RISARALDA el cual será destinado
                para LOCAL COMERCIAL. =========================================
                PARÁGRAFO PRIMERO: Igualmente pactan las partes que se
                prohíbe el cambio de destinación del inmueble que no sea
                comercial diferente a la establecida para este contrato,
                y en el evento en que esto suceda dará causal para
                terminación unilateral del contrato de arrendamiento por
                parte del ARRENDADOR. =========================================
                PARÁGRAFO SEGUNDO: Pactan las partes que EL ARRENDATARIO
                exonera al ARRENDADOR del pago de Industria y comercio y
                demás que se deban de pagar con ocasión a la actividad
                comercial del establecimiento, para lo cual manifiesta
                que estos impuestos serán pagados única y exclusivamente
                por EL ARRENDATARIO. ============================================
                PARÁGRAFO TERCERO: EL ARRENDATARIO no destinará el inmueble
                a fines ilícitos, y en consecuencia se obliga a no utilizarlo
                para ocultar o 
                """,
            f"""
                depositar armas, explosivos, actividades de secuestro o
                depósito de dineros de procedencia ilícita, artículos de
                contrabando o para que en él se elaboren, almacenen o
                vendan drogas estupefacientes o sustancias alucinógenas
                y afines. ==================
                PARÁGRAFO CUARTO – EL ARRENDATARIO se obliga a no guardar
                o permitir que se guarden en el inmueble arrendado
                sustancias inflamables o explosivas que pongan en peligro
                la seguridad del mismo, y en caso que ocurriera dentro
                del inmueble enfermedad infecto-contagiosa, serán de EL
                ARRENDATARIO los gastos de desinfección que ordenen las
                autoridades sanitarias. =================================
                PARÁGRAFO QUINTO: Pactan las partes de común acuerdo que
                EL ARRENDATARIO le queda expresamente prohibido realizar
                algún tipo de contratación de servicios o adquirir bienes
                muebles y/o electrodomésticos en los cuales tenga relación
                con las facturas de los servicios públicos domiciliarios
                del bien inmueble. ================================
                PARÁGRAFO SEXTO: Pactan las partes de común acuerdo que
                los problemas como cierres por volumen, riñas, alto volumen
                y demás serán responsabilidad de EL ARRENDATARIO y serán
                los responsables en el pago que se requiera. ============
                SEGUNDA - DEL PRECIO, OPORTUNIDAD Y SITIO DE PAGO: El
                precio del arrendamiento es de {data["precio_arrendamiento"]},
                que se pagará a LA ARRENDADORA ó a su orden en LA VIRGINIA
                RISARALDA, a partir del día {data["fecha_inicio_dia"]} de
                {data["fecha_inicio_mes"]} del año {data["fecha_inicio_año"]},
                y de ahí en adelante cada día {data["fecha_inicio_dia"]} de
                cada mes. ============================
                PARÁGRAFO PRIMERO: La mera tolerancia de LA ARRENDADORA
                en aceptar el pago del precio con posterioridad a los
                tres días citados, no se entenderá como ánimo de modificar
                la cláusula anterior. =============
                PARÁGRAFO SEGUNDO: El precio del arrendamiento será
                reajustado anualmente, teniendo en cuenta el incremento
                del índice de precios al consumidor, en el año calendario
                inmediatamente anterior al del vencimiento del contrato o
                en el de la prórroga vigente, o de acuerdo con normas
                legales dictadas por el Gobierno Nacional en este aspecto.
                =====
                DEPÓSITO: Pactan las partes de común acuerdo un depósito de
                {data["deposito"]}, dinero que va a ser pagado por EL
                ARRENDATARIO en efectivo a LA ARRENDADORA y que será
                destinado para el pago de los servicios públicos en el
                evento en que EL ARRENDATARIO al momento de la restitución
                del bien inmueble arrendado, deje facturas de los servicios
                pendientes por pagar, y/o en su
                """,
            f"""
                defecto de lugar a realizar alguna reparación locativa,
                y LA ARRENDADORA se obliga para con EL ARRENDATARIO
                a devolver dicha suma de dinero en el evento en que no
                existam facturas de servicios públicos pendientes por
                pagar o reparaciones locativas para realizar. ===========

                TERCERA - DURACIÓN: El término del contrato es:
                {data["duracion_contrato"]}, y tanto LA ARRENDADORA
                como EL ARRENDATARIO se notificarán con TRES (03)
                MESES de antelación si desean terminar con el presente
                contrato. ==============================================

                Lo anterior sin perjuicio del derecho a la renovación
                consagrada en la ley, y la renta aumentará de acuerdo
                a lo que estipula la ley. En caso de no prorrogarse
                deberá ser entregado a LA ARRENDADORA a paz y salvo
                por concepto de servicios públicos y en el mismo buen
                estado en que se encuentra lo que ha recibido. ========

                CUARTA - INCUMPLIMIENTO A LAS OBLIGACIONES CONTRAÍDAS:
                Así como la mora en el pago del canon de arrendamiento
                en la forma y términos estipulados ó la violación de
                cualquiera de las obligaciones por parte de EL
                ARRENDATARIO, dará lugar a LA ARRENDADORA, a poder dar
                por terminado el contrato antes del tiempo previsto
                y exigir la entrega del bien sin necesidad del desahucio,
                ni de los requerimientos previstos en la ley a favor
                de EL ARRENDATARIO a los cuales renuncia desde ahora,
                y de poder cobrar ejecutivamente el valor de los cánones
                adeudados, los servicios e impuestos dejados de pagar
                por EL ARRENDATARIO, la indemnización por perjuicios,
                bastando la sola afirmación y la presentación de este
                contrato, que PRESTA MÉRITO EJECUTIVO para cualquier
                acción por la vía judicial. =============================

                PARÁGRAFO: Así mismo se compromete a restituir el
                inmueble con todos los servicios conexos totalmente al
                día y paz y salvo con las empresas prestadoras del
                servicio y se obliga a cancelar las facturas que lleguen
                posteriormente, pero causadas ó consumidas en la vigencia
                del contrato, en ningún caso LA ARRENDADORA será
                responsable por el pago de servicios, conexiones ó
                acometidas que fueren directamente contratadas por EL
                ARRENDATARIO, salvo pacto expreso y escrito. ===========

                QUINTA - DE LA DESTINACIÓN: El bien inmueble se
                destina para LOCAL COMERCIAL, para el funcionamiento
                de {data["local_uso"]} y EL ARRENDATARIO no podrá darle
                otra destinación que no sea COMERCIAL ni permitir un
                uso que sea contrario a la ley, el orden público y las
                buenas costumbres.
                """,
            f"""
                costumbres, ni subarrendar ni ceder a terceros sin
                la previa autorización de LA ARRENDADORA. =========

                SEXTA - MEJORAS: EL ARRENDATARIO, se obliga a efectuar
                las reparaciones locativas y aquellas que se causen
                por hechos de él ó de sus dependientes. ==============

                NO PODRÁ HACERLE MEJORAS AL BIEN INMUEBLE QUE NO SEAN
                AUTORIZADAS, EN TODO CASO LAS QUE HICIERE SIN ESTE
                REQUISITO, QUEDARÁN A FAVOR DEL LOCAL COMERCIAL Y
                POR ENDE DE LA ARRENDADORA - PROPIETARIA, Y A LA
                FINALIZACIÓN DEL CONTRATO, NO LE SERÁN RECONOCIDAS
                AL ARRENDATARIO. =====================================

                SEPTIMA – ENTREGA DEL BIEN INMUEBLE: LA ARRENDADORA
                manifiesta que realiza la entrega del BIEN INMUEBLE
                se entrega pintado, sin fallas ni daños en puertas
                o piso, con servicios de energía, agua, acueducto
                y alcantarillado. ===================================

                OCTAVA – RESTITUCIÓN BIEN INMUEBLE: EL ARRENDATARIO
                se compromete y obliga a devolver el inmueble en
                las mismas buenas condiciones en que lo ha recibido,
                ya que este se entrega en perfecto estado, limpio,
                pisos en perfecto estado, con todas las redes eléctricas
                en excelentes condiciones; servicios públicos a paz
                y salvo; servicios sanitarios en perfecto estado;
                y demás mejoras y anexidades adecuadas para prestar
                el servicio que ofrecen. Todo en excelente estado
                de conservación. =====================================

                PARÁGRAFO: Y a la terminación del contrato debe
                entregarse en las mismas condiciones y a paz y salvo
                por dicho concepto y son por cuenta de EL ARRENDATARIO,
                el incumplimiento y la obligación de pagar dichos
                servicios, se cumplirán de acuerdo a lo establecido
                en el Artículo 15 de la ley 820 de 2003, cumpliendo
                las reglamentaciones que haga el gobierno al respecto.
                ====================================================

                NOVENA- OBLIGACIONES DEL ARRENDATARIO: ================

                1. Cancelar el canon o precio de arrendamiento por
                el valor y la puntualidad establecida en este contrato.

                2. Restituir el inmueble a LA ARRENDADORA al terminar
                este contrato, o sus prórrogas, en el mismo estado
                en el que lo recibe.

                3. Efectuar las reparaciones locativas.

                4. Efectuar las mejoras necesarias cuando sea por
                causa de hechos culposos o dolosos realizados por EL
                ARRENDATARIO o sus dependientes.
                """,
            f"""
                5. Cancelar los servicios públicos de energía eléctrica,
                acueducto y alcantarillado y demás que sean utilizados
                en el inmueble.
                6. Y las demás que se encuentran debidamente establecidas
                en la ley 820 de 2003.

                DÉCIMA – CLÁUSULA PENAL: En el evento de incumplimiento
                cualquiera de las Partes a las obligaciones a su cargo
                contenidas en la ley o en este Contrato, la parte
                incumplida deberá pagar a la otra parte una suma equivalente
                a DOS (02) CANONES DE ARRENDAMIENTO vigentes en la fecha
                del incumplimiento, a título de pena. =====================

                PARÁGRAFO PRIMERO: En el evento que alguna de las partes
                decida dar por terminado el contrato de manera unilateral
                antes de cumplirse el tiempo pactado, está se constituye
                en deudora de la otra parte, por la suma equivalente a los
                cánones de arrendamientos pendientes por cumplirse. ========

                PARÁGRAFO SEGUNDO: En el evento en que los perjuicios
                ocasionados por la parte incumplida, excedan el valor de
                la suma aquí prevista como pena, la parte incumplida
                deberá pagar a la otra parte la diferencia entre el valor
                total de los perjuicios y el valor de la pena prevista
                en esta Cláusula. ==========================================

                UNDÉCIMA - OBLIGACIONES DE LA ARRENDADORA:
                1. Conceder el uso y goce del inmueble y los elementos
                que lo integran a LA ARRENDATARIA en la fecha y condiciones
                establecidas en este contrato.
                2. Y las demás que se encuentran debidamente establecidas
                en la ley 820 de 2003. =====================================

                DÉCIMA SEGUNDA – DOMICILIO: Para todos los fines
                judiciales o extrajudiciales que se generan del presente
                contrato, las partes dejan constituidos como sus domicilios,
                LA ARRENDADORA y EL ARRENDATARIO en la dirección Local
                Comercial dado en dicho arrendamiento. =====================

                DÉCIMA TERCERA – DEUDOR SOLIDARIO: El señor
                {data["deudor_solidario_nombre"]}, Varón de nacionalidad
                colombiana y mayor de edad, identificado con la cédula
                de ciudadanía N°{data["deudor_solidario_cedula"]},
                domiciliado y residente en esta localidad, Celular
                #{data["deudor_solidario_celular"]}, quien LIBRE Y DE
                FORMA VOLUNTARIA se declara ser CODEUDOR O DEUDOR
                de EL ARRENDATARIO en forma SOLIDARIA E INDIVISIBLE
                de todas las CARGAS Y OBLIGACIONES contenidas en el
                presente contrato, tanto durante el término inicialmente
                pactado, como durante todas sus prórrogas expresas o
                tácitas y solo hasta que se produzca la entrega material
                del inmueble a LA ARRENDADORA, por concepto de
                """,
            f"""
                arrendamiento, servicios públicos, indemnizaciones, daños
                en el inmueble, intereses moratorios, honorarios causados
                en caso de mora en el pago del arriendo por las gestiones
                de cobranza extrajudicial o judicial y las costas procesales
                a que sea condenado EL ARRENDATARIO en la cuantía señalada
                por el respectivo juzgado en el caso del proceso de
                restitución, ejecutivo, cláusulas penales, etc. ============

                DÉCIMA CUARTA – LESIÓN DE LOS DERECHOS DEL ARRENDADOR:
                Para efectos del cambio de destinación del inmueble y del
                subarriendo, son lesivos de los derechos del ARRENDADOR:
                Subarrendar para Usar el bien arrendado destinándolo a otra
                actividad diferente. =====================================

                DÉCIMA QUINTA - INSPECCIÓN: EL ARRENDATARIO permitirá en
                cualquier tiempo las visitas que EL ARRENDADOR o sus
                representantes tengan bien realizar para constatar el
                estado y conservación del inmueble u otras circunstancias
                que sean de su interés. ===================================

                DÉCIMA SEXTA - GOOD WILL: Las partes acuerdan que el
                presente contrato de arrendamiento no genera ningún tipo
                de prima o Good Will a favor de EL ARRENDATARIO. =========

                DÉCIMA SEPTIMA – HORARIO: El funcionamiento del
                establecimiento de comercio estará sujeto a los horarios
                que estén establecidos por la administración municipal. ===

                DÉCIMA OCTAVA - DOMICILIO: Para todos los fines judiciales
                o extrajudiciales que se generan del presente contrato,
                las partes dejan constituidos como sus domicilios,
                LA ARRENDADORA, EL ARRENDATARIO Y EL CODEUDOR en la
                dirección del APARTAMENTO dado en dicho arrendamiento. =====

                DÉCIMA NOVENA - MÉRITO EJECUTIVO: Las partes establecen
                que el presente contrato presta mérito ejecutivo para la
                exigencia de las obligaciones aquí acordadas, por contener
                obligaciones expresas, claras y exigibles. =================

                ESPACIO ÚNICA Y EXCLUSIVAMENTE PARA DESCRIBIR LINDERO,
                ÁREA, FICHA CATASTRAL Y MATRÍCULA INMOBILIARIA DEL BIEN
                INMUEBLE.
                """,
            f"""
                En constancia se firman dos ejemplares para su fiel cumplimiento
                y cada parte recibe su ejemplar en ese acto de conformidad, hoy
                {data["fecha_inicio"]}.
                 """,
            f"""
                {data["arrendador_nombre"]}
                ARRENDADORA
                 """,
            f"""
                {data["arrendatario_nombre"]}
                ARRENDATARIO
                 """,
            f"""
                {data["deudor_solidario_nombre"]}
                DEUDOR SOLIDARIO
                """,
        ]

        for para in paragraphs:
            content.append(Paragraph(para, justified_style))
            content.append(Spacer(1, 13))

        # Crear y guardar el documento PDF
        doc.build(content)

        pdf = buffer.getvalue()
        buffer.close()

        # Guardar el documento en la base de datos
        document = Document(document_type="Contrato de Arrendamiento", content=pdf)
        document.save()

        # Generar y guardar el código único
        document_code = DocumentCode(document=document)
        document_code.save()

        # Preparar la respuesta HTTP con el PDF
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="contract.pdf"'
        response.write(pdf)

        return response

    else:
        return JsonResponse({"error": "Método no permitido. Use POST."}, status=405)


def retrieve_document(request, unique_code):
    document_code = get_object_or_404(DocumentCode, unique_code=unique_code)
    document = document_code.document

    # Crear el documento PDF usando ReportLab
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="document_{unique_code}.pdf"'
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    # Añadir el título y el contenido del documento almacenado
    content.append(Paragraph("CONTRATO DE ARRENDAMIENTO", styles["Title"]))
    content.append(Spacer(1, 12))
    content.append(Paragraph(document.content, styles["Normal"]))

    # Guardar el documento
    doc.build(content)

    pdf = buffer.getvalue()
    buffer.close()

    response.write(pdf)
    return response
