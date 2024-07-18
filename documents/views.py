import io
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, BaseDocTemplate, PageTemplate, Frame
from .models import Document, DocumentCode


def generate_document(request):
    if request.method == 'POST':
        # Datos dinámicos que vendrán del formulario del frontend
        data = {
            "arrendador_nombre": request.POST.get('arrendador_nombre'),
            "arrendador_cedula": request.POST.get('arrendador_cedula'),
            "arrendatario_nombre": request.POST.get('arrendatario_nombre'),
            "arrendatario_cedula": request.POST.get('arrendatario_cedula'),
            "arrendatario_celular": request.POST.get('arrendatario_celular'),
            "inmueble_destino": request.POST.get('inmueble_destino'),
            "local_identificacion": request.POST.get('local_identificacion'),
            "local_uso": request.POST.get('local_uso'),
            "inmueble_direccion": request.POST.get('inmueble_direccion'),
            "precio_arrendamiento": request.POST.get('precio_arrendamiento'),
            "fecha_inicio": request.POST.get('fecha_inicio'),
            "deposito": request.POST.get('deposito'),
            "duracion_contrato": request.POST.get('duracion_contrato'),
            "fecha_fin": request.POST.get('fecha_fin'),
        }

        # Verificar si algún campo está vacío
        if any(value is None for value in data.values()):
            return JsonResponse({"error": "Todos los campos son obligatorios."}, status=400)

        # Preparar el documento PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="contract.pdf"'
        
        doc = BaseDocTemplate(response, pagesize=letter)
        story = []
        
        # Define the header and footer
        styles = getSampleStyleSheet()
        header_style = styles['Title']
        footer_style = styles['Normal']

        # Custom Page Template
        class MyPageTemplate(PageTemplate):
            def __init__(self, *args, **kwargs):
                self.header = kwargs.pop('header', '')
                self.footer = kwargs.pop('footer', '')
                super().__init__(*args, **kwargs)

            def afterPage(self, canvas, doc):
                canvas.saveState()
                # Header
                canvas.setFont("Helvetica", 10)
                canvas.drawString(inch, 10.5 * inch, f"CONTRATO DE ARRENDAMIENTO DE BIEN INMUEBLE DESTINADO A LOCAL COMERCIAL 1")
                # Footer
                canvas.setFont("Helvetica", 8)
                canvas.drawString(inch, 0.75 * inch, "Carrera 6 #6-35, Barrio Bavaria, Enseguida de la Notaría Única Del Círculo de La Virginia, Risaralda / 3127682601 / johan.mazueraduran@gmail.com")
                canvas.restoreState()

        # Add PageTemplate to the Document
        doc.addPageTemplates([MyPageTemplate(header='', footer='')])

        # Prepare content
        html_content = f"""
                    <para>
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
                    </para>

                    <para>
                    PRIMERA: OBJETO DEL NEGOCIO: LA ARRENDADORA, se obliga
                    a favor de EL ARRENDATARIO a realizar la entrega del uso
                    y goce que tiene y ejerce sobre un bien inmueble, y
                    está a su vez se obliga con EL ARRENDATARIO a recibirlo
                    a título de arrendamiento.
                    </para>

                    <para>
                    LOCAL COMERCIAL construido en material de adobe y cemento,
                    pisos en cerámica, uno (1) unidades sanitarias completas,
                    con servicios públicos domiciliarios de AGUA,
                    ALCANTARILLADO, ENERGIA ELECTRICA. Identificado como LOCAL
                    N°1 para VENTA REPUESTOS PARA BICICLETAS del bien inmueble
                    ubicado en la CARRERA 6ª #9-60 BARRIO RESTREPO, área urbana
                    del Municipio de LA VIRGINIA, Departamento de RISARALDA
                    el cual será destinado para LOCAL COMERCIAL.
                    </para>

                    <para>
                    PARAGRAFO PRIMERO: Igualmente pactan las partes que se
                    prohíbe el cambio de destinación del inmueble que no sea
                    comercial diferente a la establecida para este contrato,
                    y en el evento en que esto suceda dará causal para
                    terminación unilateral del contrato de arrendamiento por
                    parte del ARRENDADOR.
                    </para>

                    <para>
                    PARÁGRAFO SEGUNDO: Pactan las partes que EL ARRENDATARIO
                    exonera al ARRENDADOR del pago de Industria y comercio y
                    demás que se deban de pagar con ocasión a la actividad
                    comercial del establecimiento, para lo cual manifiesta
                    que estos impuestos serán pagados única y exclusivamente
                    por EL ARRENDATARIO.
                    </para>

                    <para>
                    PARAGRAFO TERCERO: EL ARRENDATARIO no destinará el inmueble
                    a fines ilícitos, y en consecuencia se obliga a no
                    utilizarlo para ocultar o depositar armas, explosivos,
                    actividades de secuestro o depósito de dineros de
                    procedencia ilícita, artículos de contrabando o para que
                    en él se elaboren, almacenen o vendan drogas estupefacientes
                    o sustancias alucinógenas y afines.
                    </para>

                    <para>
                    PARAGRAFO CUARTO: EL ARRENDATARIO se obliga a no guardar
                    o permitir que se guarden en el inmueble arrendado
                    sustancias inflamables o explosivas que pongan en peligro
                    la seguridad del mismo, y en caso que ocurriera dentro
                    del inmueble enfermedad infecto-contagiosa, serán de EL
                    ARRENDATARIO los gastos de desinfección que ordenen las
                    autoridades sanitarias.
                    </para>

                    <para>
                    PARAGRAFO QUINTO: Pactan las partes de común acuerdo que
                    EL ARRENDATARIO le queda expresamente prohibido realizar
                    algún tipo de contratación de servicios o adquirir bienes
                    muebles y/o electrodomésticos en los cuales tenga relación
                    con las facturas de los servicios públicos domiciliarios
                    del bien inmueble.
                    </para>

                    <para>
                    PARAGRAFO SEXTO: Pactan las partes de común que los problemas
                    como cierres por volumen, riñas, alto volumen y demás
                    serán responsables EL ARRENDATARIO y serán los responsables
                    en el pago que se requieran.
                    </para>

                    <para>
                    SEGUNDA - DEL PRECIO, OPORTUNIDAD Y SITIO DE PAGO: El
                    precio del arrendamiento es de OCHOCIENTOS MIL PESOS M/CTE
                    ($800.000) MENSUALES, que se pagarán a LA ARRENDADORA ó
                    a su orden en LA VIRGINIA RISARALDA, a partir del día
                    VEINTIOCHO (28) de MAYO del año DOS MIL VEINTICUATRO
                    (2024), y de ahí en adelante cada día VEINTIOCHO (28) de
                    cada mes.
                    </para>

                    <para>
                    PARAGRAFO PRIMERO: La mera tolerancia LA ARRENDADORA
                    en aceptar el pago del precio con posterioridad a los
                    tres días citados, no se entenderá como animo de modificar
                    la cláusula anterior.
                    </para>

                    <para>
                    PARAGRAFO SEGUNDO: El precio del arrendamiento será
                    reajustado anualmente, teniendo en cuenta el incremento
                    del índice de precios al consumidor, en el año calendario
                    inmediatamente anterior al del vencimiento del contrato o
                    en el de la prórroga vigente, o de acuerdo con normas
                    legales dictadas por el Gobierno Nacional en este aspecto.
                    </para>

                    <para>
                    DEPOSITO: Pactan las partes de común acuerdo un depósito
                    de DOSCIENTOS MIL PESOS MCTE ($200.000), dinero que va
                    a ser pagado por EL ARRENDATARIO en efectivo a LA
                    ARRENDADORA y que será destinados para el pago de los
                    servicios públicos en el evento en que EL ARRENDATARIO al
                    momento de la restitución del bien inmueble arrendado, deje
                    facturas de los servicios pendientes por pagar, y/o en su
                    defecto de lugar a realizar alguna reparación locativa, y
                    LA ARRENDADORA se obliga para con EL ARRENDATARIO a devolver
                    dicha suma de dinero en el evento en que no existan facturas
                    de servicios públicos pendientes por pagar o reparaciones
                    locativas para realizar.
                    </para>

                    <para>
                    TERCERA - DURACION: El término del contrato es: SEIS (06)
                    MESES A PARTIR DEL DÍA VEINTIOCHO (28) de MAYO DEL AÑO
                    DOS MIL VEINTICUATRO (2024), HASTA EL DIA VEINTIOCHO (28)
                    DE MAYO DEL AÑO DOS MIL VEINTICUATRO (2024), y tanto LA
                    ARRENDADORA como EL ARRENDATARIO se notificarán con TRES
                    (03) MESES de antelación si desean terminar con el
                    presente contrato.
                    </para>

                    <para>
                    Lo anterior sin perjuicio del derecho a la renovación
                    consagrada en la ley, y la renta aumentará de acuerdo a lo
                    que estipula la ley, en caso de no prorrogarse deberá ser
                    entregado a LA ARRENDADORA a paz y salvo por concepto
                    de servicios públicos y en el mismo buen estado en que se
                    encuentra lo que ha recibido.
                    </para>

                    <para>
                    CUARTA - EL INCUMPLIMIENTO A LAS OBLIGACIONES CONTRAIDAS:
                    Así como la mora en el pago del canon de arrendamiento en
                    la forma y términos estipulados ó la violación de
                    cualquiera de las obligaciones por parte de EL ARRENDATARIO,
                    dará lugar a LA ARRENDADORA, de poder dar por terminado
                    el contrato antes del tiempo previsto y exigir la entrega
                    del bien sin necesidad del desahucio, ni de los requerimientos
                    previstos en la ley a favor de EL ARRENDATARIO a los cuales
                    renuncia desde ahora, y de poder cobrar ejecutivamente
                    el valor de los cánones adeudados, los servicios e impuestos
                    dejados de pagar por EL ARRENDATARIO, la indemnización por
                    perjuicios, bastando la sola afirmación y la presentación
                    de éste contrato, que PRESTA MÉRITO EJECUTIVO para cualquier
                    acción por la vía judicial.
                    </para>

                    <para>
                    PARAGRAFO: Así mismo se compromete a restituir el inmueble
                    con todos los servicios conexos totalmente al día y paz y
                    salvo con las empresas prestadoras del servicio y se obliga
                    a cancelar las facturas que lleguen posteriormente, pero
                    causadas ó consumidas en la vigencia del contrato, en ningún
                    caso LA ARRENDADORA será responsable por el pago de servicios,
                    conexiones ó acometidas que fueren directamente contratadas
                    por EL ARRENDATARIO, salvo pacto expreso y escrito.
                    </para>

                    <para>
                    QUINTA - DE LA DESTINACION: El bien inmueble se destina
                    para LOCAL COMERCIAL, para venta de repuestos de bicicletas,
                    quedando expresamente prohibida la destinación a actividades
                    diferentes o en general a cualquier actividad de carácter
                    ilícito. Cualquier modificación en el destino de la propiedad
                    deberá ser comunicada a LA ARRENDADORA, previamente y
                    por escrito.
                    </para>

                    <para>
                    SEXTA - DE LA RESTITUCIÓN: En caso de terminado el contrato,
                    EL ARRENDATARIO deberá restituir a LA ARRENDADORA el bien
                    inmueble objeto de arrendamiento, en el mismo estado en que
                    lo recibió, salvo el deterioro natural que se derive del uso
                    normal del bien y en el evento que existan reparaciones
                    locativas por daños ocasionados a la propiedad será EL
                    ARRENDATARIO quien asumirá los costos de las mismas.
                    </para>

                    <para>
                    SEPTIMA - DE LAS OBLIGACIONES ADICIONALES: EL ARRENDATARIO
                    se obliga a pagar los impuestos que graven el uso del bien
                    inmueble y cualquier otro gasto adicional relacionado con
                    la destinación del inmueble. LA ARRENDADORA no será
                    responsable por los costos derivados de actividades
                    comerciales realizadas por EL ARRENDATARIO.
                    </para>

                    <para>
                    OCTAVA - DE LA PROHIBICIÓN DE CESIÓN Y SUBARRIENDO: EL
                    ARRENDATARIO no podrá ceder ni subarrendar total o
                    parcialmente el bien inmueble objeto de arrendamiento sin
                    la autorización previa y escrita de LA ARRENDADORA.
                    </para>

                    <para>
                    NOVENA - DEL DOMICILIO CONTRACTUAL: Para todos los efectos
                    derivados del presente contrato, las partes fijan como
                    domicilio el ubicado en el MUNICIPIO DE LA VIRGINIA,
                    DEPARTAMENTO DE RISARALDA, y en caso de litigio o
                    conflicto serán competentes los jueces de este lugar.
                    </para>

                    <para>
                    DÉCIMA - DE LOS ANEXOS: Para el cumplimiento de lo
                    establecido en este contrato, se anexan los documentos
                    pertinentes como los certificados de existencia y
                    representación legal, y demás documentos que se consideren
                    necesarios para su correcta ejecución.
                    </para>

                    <para>
                    Firmado en LA VIRGINIA, RISARALDA a los ____ días del
                    mes de ___________ del año ____________.
                    </para>

                    <para>
                    _______________________________
                    LA ARRENDADORA
                    </para>

                    <para>
                    _______________________________
                    EL ARRENDATARIO
                    </para>
                    """

        
        story.append(Paragraph(html_content, styles['Normal']))
        
        # Build the PDF
        doc.build(story)

        return response
    else:
        return JsonResponse({"error": "Método no permitido. Use POST."}, status=405)

def retrieve_document(request, unique_code):
    document_code = get_object_or_404(DocumentCode, unique_code=unique_code)
    document = document_code.document

    # Crear el documento PDF usando ReportLab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="document_{unique_code}.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    # Añadir el título y el contenido del documento almacenado
    content.append(Paragraph('CONTRATO DE ARRENDAMIENTO', styles['Title']))
    content.append(Spacer(1, 12))
    content.append(Paragraph(document.content, styles['Normal']))

    # Guardar el documento
    doc.build(content)

    pdf = buffer.getvalue()
    buffer.close()

    response.write(pdf)
    return response