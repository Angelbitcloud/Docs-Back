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
            "inmueble_destino",
            "local_identificacion",
            "local_uso",
            "inmueble_direccion",
            "precio_arrendamiento",
            "fecha_inicio",
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
            'Justified',
            parent=styles['Normal'],
            alignment=4,  # Justificado
            fontName='Helvetica',
            fontSize=14,
            leading=12
        )

        content = []

        # Añadir el título
        content.append(Paragraph("CONTRATO SIMPLIFICADO", styles["Title"]))
        content.append(Spacer(1, 12))

        # Añadir el párrafo prefabricado con datos del JSON
        paragraphs = [
            f"""
            En el Municipio de LA VIRGINIA, Departamento de
            RISARALDA, República de COLOMBIA, entre los suscritos a
            saber de una parte, la señora {data["arrendador_nombre"]},
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
            LOCAL COMERCIAL que se regirá por la siguientes clausulas:
            """,
            f"""
            PRIMERA: OBJETO DEL NEGOCIO: LA ARRENDADORA, se obliga
            a favor de EL ARRENDATARIO a realizar la entrega del uso
            y goce que tiene y ejerce sobre un bien inmueble, y
            está a su vez se obliga con EL ARRENDATARIO a recibirlo
            a título de arrendamiento.
            """,
            f"""
            LOCAL COMERCIAL construido en material de adobe y cemento,
            pisos en cerámica, uno (1) unidades sanitarias completas,
            con servicios públicos domiciliarios de AGUA,
            ALCANTARILLADO, ENERGIA ELECTRICA. Identificado como LOCAL
            N°1 para VENTA REPUESTOS PARA BICICLETAS del bien inmueble
            ubicado en la CARRERA 6ª #9-60 BARRIO RESTREPO, área urbana
            del Municipio de LA VIRGINIA, Departamento de RISARALDA
            el cual será destinado para LOCAL COMERCIAL.
            """,
            f"""
            PARAGRAFO PRIMERO: Igualmente pactan las partes que se
            prohíbe el cambio de destinación del inmueble que no sea
            comercial diferente a la establecida para este contrato,
            y en el evento en que esto suceda dará causal para
            terminación unilateral del contrato de arrendamiento por
            parte del ARRENDADOR.
            """,
            f"""
            PARÁGRAFO SEGUNDO: Pactan las partes que EL ARRENDATARIO
            exonera al ARRENDADOR del pago de Industria y comercio y
            demás que se deban de pagar con ocasión a la actividad
            comercial del establecimiento, para lo cual manifiesta
            que estos impuestos serán pagados única y exclusivamente
            por EL ARRENDATARIO.
            """,
            f"""
            PARAGRAFO TERCERO: EL ARRENDATARIO no destinará el inmueble
            a fines ilícitos, y en consecuencia se obliga a no
            utilizarlo para ocultar o depositar armas, explosivos,
            actividades de secuestro o depósito de dineros de
            procedencia ilícita, artículos de contrabando o para que
            en él se elaboren, almacenen o vendan drogas estupefacientes
            o sustancias alucinógenas y afines.
            """,
            f"""
            PARAGRAFO CUARTO: EL ARRENDATARIO se obliga a no guardar
            o permitir que se guarden en el inmueble arrendado
            sustancias inflamables o explosivas que pongan en peligro
            la seguridad del mismo, y en caso que ocurriera dentro
            del inmueble enfermedad infecto-contagiosa, serán de EL
            ARRENDATARIO los gastos de desinfección que ordenen las
            autoridades sanitarias.
            """,
            f"""
            PARAGRAFO QUINTO: Pactan las partes de común acuerdo que
            EL ARRENDATARIO le queda expresamente prohibido realizar
            algún tipo de contratación de servicios o adquirir bienes
            muebles y/o electrodomésticos en los cuales tenga relación
            con las facturas de los servicios públicos domiciliarios
            del bien inmueble.
            """,
            f"""
            PARAGRAFO SEXTO: Pactan las partes de común que los problemas
            como cierres por volumen, riñas, alto volumen y demás
            serán responsables EL ARRENDATARIO y serán los responsables
            en el pago que se requieran.
            """,
            f"""
            SEGUNDA - DEL PRECIO, OPORTUNIDAD Y SITIO DE PAGO: El
            ARRENDATARIO se obliga a pagar a LA ARRENDADORA como valor
            del arrendamiento la suma de {data["precio_arrendamiento"]} pesos
            colombianos ($) mensuales, los cuales se cancelarán por meses
            anticipados, en la forma y lugar que se estipule en el presente
            contrato.
            """,
            f"""
            TERCERA - DEL PLAZO: El presente contrato tendrá una duración
            de {data["duracion_contrato"]} y comenzará a regir a partir del
            {data["fecha_inicio"]} y se dará por terminado automáticamente
            sin necesidad de requerimiento alguno en el caso en que el
            contrato termine el {data["fecha_fin"]}.
            """,
            f"""
            CUARTA - DEL DEPÓSITO: EL ARRENDATARIO se obliga a entregar a LA
            ARRENDADORA la suma de {data["deposito"]} pesos colombianos ($)
            como depósito de garantía. La ARRENDADORA, al vencimiento
            del contrato, devolverá al ARRENDATARIO el depósito menos
            los valores que correspondan a reparaciones de daños o
            incumplimientos.
            """,
            f"""
            QUINTA - DEL MANTENIMIENTO: EL ARRENDATARIO se obliga a mantener
            el inmueble en buen estado, cubriendo los gastos de mantenimiento
            ordinario y correctivo.
            """,
            f"""
            SEXTA - DE LA TERMINACIÓN ANTICIPADA: El contrato podrá ser
            terminado anticipadamente por cualquiera de las partes con
            un aviso previo de al menos {data["duracion_contrato"]}, sin
            que se genere penalidad alguna.
            """,
            f"""
            SÉPTIMA - DEL INCUMPLIMIENTO: En caso de incumplimiento de
            alguna de las cláusulas, la parte afectada podrá dar por
            terminado el contrato de manera unilateral.
            """,
            f"""
            OCTAVA - DE LA LEGISLACIÓN APLICABLE: El presente contrato
            se regirá por las disposiciones del Código Civil y Comercial
            colombiano y demás normas concordantes.
            """,
            f"""
            NOVENA - DE LAS CLÁUSULAS ADICIONALES: Las partes podrán
            acordar cláusulas adicionales siempre que no contravengan
            las disposiciones legales.
            """,
            f"""
            EN FE DE LO CUAL, las partes firman el presente contrato
            en dos ejemplares del mismo tenor y a un solo efecto,
            en la ciudad de LA VIRGINIA, a los {data["fecha_inicio"]}.
            """
        ]

        for para in paragraphs:
            content.append(Paragraph(para, justified_style))
            content.append(Spacer(1, 12))

     # Crear y guardar el documento PDF
        doc.build(content)

        pdf = buffer.getvalue()
        buffer.close()

        # Guardar el documento en la base de datos
        document = Document(
            document_type="Contrato de Arrendamiento",
            content=pdf
        )
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
    response["Content-Disposition"] = f'attachment; filename="document_{unique_code}.pdf"'

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